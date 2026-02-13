"""Celery tasks for evaluation processing."""

import asyncio
import json
import statistics
import tempfile
import traceback
from dataclasses import asdict

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.endpoints.openai_model import (
    OpenAICompatibleClient,
    OpenAICompatibleModelConfig,
)
from lighteval.models.model_input import GenerationParameters
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.tasks.registry import Registry

from api.core.celery_app import celery_app
from api.core.logging import get_logger
from api.core.redis_client import clear_eval_progress, set_eval_progress
from api.evaluations.eval_pipeline.dataset_task import DatasetTask
from api.evaluations.eval_pipeline.eval_pipeline import (
    CustomTaskEvaluationPipeline,
    CustomTaskEvaluationPipelineParameters,
)
from api.evaluations.eval_pipeline.flexible_dataset_task import FlexibleDatasetTask
from api.evaluations.eval_pipeline.guideline_judge import GuidelineJudgeMetric
from api.evaluations.eval_pipeline.metric_doc_generator import MetricDocGenerator
from api.evaluations.schemas import JudgeType

logger = get_logger(__name__)

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


# ==================== A. Model Config Helper ====================


def _create_model_config(
    model_config_data: dict,
) -> OpenAICompatibleModelConfig:
    """Create OpenAI compatible model config from serialized data."""
    if model_config_data.get("extra_body"):
        return OpenAICompatibleModelConfig(
            model_name=model_config_data["model_name"],
            base_url=model_config_data["base_url"],
            api_key=model_config_data["api_key"],
            generation_parameters=GenerationParameters(
                extra_body=model_config_data["extra_body"]
            ),
        )
    return OpenAICompatibleModelConfig(
        model_name=model_config_data["model_name"],
        base_url=model_config_data["base_url"],
        api_key=model_config_data["api_key"],
    )


# ==================== B. Pipeline Runners ====================


def _run_task_pipeline(
    task_name: str,
    n_samples: int | None,
    n_fewshots: int | None,
    model_config_data: dict,
    progress_callback=None,
) -> dict:
    """Run a task evaluation pipeline. Raises on failure."""
    temp_dir = tempfile.mkdtemp()
    evaluation_tracker = EvaluationTracker(
        output_dir=temp_dir,
        save_details=True,
    )

    pipeline_params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        max_samples=n_samples,
    )

    model_config = _create_model_config(model_config_data)

    if "|" not in task_name:
        full_task_name = f"{task_name}|{n_fewshots}"
    else:
        full_task_name = task_name

    # Wrap the raw lighteval callback (completed, total) into our standard
    # (stage, percent, detail) format so _run_task_pipeline callers get a
    # consistent interface.
    def _lighteval_cb(progress_tuple):
        completed, total = progress_tuple
        pct = int(completed / max(total, 1) * 80)
        progress_callback("model_inference", pct, f"Sample {completed}/{total}")

    pipeline = Pipeline(
        tasks=full_task_name,
        pipeline_parameters=pipeline_params,
        evaluation_tracker=evaluation_tracker,
        model_config=model_config,
        progress_callback=_lighteval_cb if progress_callback else None,
    )

    pipeline.evaluate()

    if progress_callback:
        progress_callback("post_processing", 85, "Processing results...")

    pipeline.save_and_push_results()

    results = pipeline.get_results()

    task_results = results["results"]["all"]

    scores_by_metric = {}
    for metric_name, value in task_results.items():
        if not metric_name.endswith("_stderr"):
            scores_by_metric[metric_name] = value

    actual_sample_count = results.get("config_general", {}).get(
        "max_samples", n_samples
    )

    registry = Registry(tasks=full_task_name)
    configs = [
        config
        for configs in registry.task_to_configs.values()
        for config in configs
    ]
    metrics = [metric for config in configs for metric in config.metrics]
    metric_docs = MetricDocGenerator.generate_metric_docs(metrics)
    metric_docs_serialized = {
        name: [asdict(desc) for desc in descriptions]
        for name, descriptions in metric_docs.items()
    }

    return {
        "summary": task_results,
        "scores": scores_by_metric,
        "sample_count": actual_sample_count,
        "temp_dir": temp_dir,
        "metric_docs": metric_docs_serialized,
    }


def _run_flexible_pipeline(
    dataset_name: str,
    dataset_content: str,
    input_field: str,
    output_type: str,
    judge_type: str,
    text_config: dict | None,
    mc_config: dict | None,
    guidelines_data: list[dict],
    model_config_data: dict,
    judge_config_data: dict | None,
    progress_callback=None,
) -> dict:
    """Run a flexible evaluation pipeline. Raises on failure."""
    from api.evaluations.schemas import (
        MultipleChoiceConfig,
        OutputType,
        TextOutputConfig,
    )

    output_type_enum = OutputType(output_type)
    judge_type_enum = JudgeType(judge_type)

    guideline_metrics = []
    if judge_type_enum == JudgeType.LLM_AS_JUDGE and judge_config_data:
        for guideline in guidelines_data:
            metric = GuidelineJudgeMetric(
                guideline=guideline,
                model=judge_config_data["model_name"],
                url=judge_config_data["base_url"],
                api_key=judge_config_data["api_key"],
                extra_body=judge_config_data.get("extra_body", {}),
            )
            guideline_metrics.append(metric)

    text_config_obj = TextOutputConfig(**text_config) if text_config else None
    mc_config_obj = MultipleChoiceConfig(**mc_config) if mc_config else None

    dataset_task = FlexibleDatasetTask(
        dataset_name=dataset_name,
        dataset_content=dataset_content,
        input_field=input_field,
        output_type=output_type_enum,
        judge_type=judge_type_enum,
        text_config=text_config_obj,
        mc_config=mc_config_obj,
        guideline_metrics=guideline_metrics,
    )
    task = dataset_task.build_lighteval_task()

    registry = Registry(tasks=None)
    registry._task_registry[dataset_name] = task.config
    registry.task_to_configs = {dataset_name: [task.config]}

    model_config = _create_model_config(model_config_data)
    model = OpenAICompatibleClient(model_config)

    if hasattr(model, "_cache") and model._cache is not None:
        model._cache._init_registry(registry)

    temp_dir = tempfile.mkdtemp()
    evaluation_tracker = EvaluationTracker(
        output_dir=temp_dir,
        save_details=True,
        push_to_hub=False,
    )

    pipeline = CustomTaskEvaluationPipeline(
        task=task,
        evaluation_tracker=evaluation_tracker,
        model=model,
        params=CustomTaskEvaluationPipelineParameters(
            max_samples=None, save_details=True, use_cache=True
        ),
        progress_callback=progress_callback,
    )

    results = pipeline.evaluate()
    pipeline.save_and_push_results()

    dataset_task.cleanup()

    return {
        "summary": results["summary"],
        "scores": results["scores"],
        "sample_count": results["sample_count"],
        "temp_dir": temp_dir,
    }


# ==================== C. Async DB Helpers ====================


def _create_celery_session():
    """Create a fresh async engine and session for Celery task context.

    Each call creates a new engine to avoid event loop binding issues
    when asyncio.run() creates a new loop per invocation.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from api.core.config import settings

    database_url = settings.DATABASE_URL
    connect_args = {
        "ssl": "require",
        "statement_cache_size": 0,
    }
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, session_factory


def _run_async(coro):
    """Run an async coroutine from sync Celery context."""
    return asyncio.run(coro)


async def _mark_trace_failed_async(trace_id: int, error: str, tb: str):
    """Mark a trace as failed in the database."""
    from api.evaluations.repository import EvaluationRepository

    engine, session_factory = _create_celery_session()
    try:
        async with session_factory() as session:
            repo = EvaluationRepository(session)
            await repo.update_trace_status(
                trace_id, "failed", {"error": error, "traceback": tb}
            )
    finally:
        await engine.dispose()


def _mark_trace_failed(trace_id: int, error: str, tb: str):
    """Mark a trace as failed (sync wrapper)."""
    _run_async(_mark_trace_failed_async(trace_id, error, tb))


async def _update_trace_guidelines_async(trace_id: int, guideline_names: list[str]):
    """Update trace guideline names in the database."""
    from api.evaluations.repository import EvaluationRepository

    engine, session_factory = _create_celery_session()
    try:
        async with session_factory() as session:
            repo = EvaluationRepository(session)
            trace = await repo.get_trace_by_id(trace_id)
            if guideline_names:
                trace.guideline_names = guideline_names
                await session.commit()
                await session.refresh(trace)
    finally:
        await engine.dispose()


def _update_trace_guidelines(trace_id: int, guideline_names: list[str]):
    """Update trace guideline names (sync wrapper)."""
    _run_async(_update_trace_guidelines_async(trace_id, guideline_names))


async def _write_events_and_complete_trace_async(
    trace_id: int,
    spec_data: dict,
    results_s3_path: str,
    report_scores: dict,
    summary: dict,
    summary_extra: dict | None = None,
):
    """Create spec/sampling/report events, update trace to completed, return trace+events for JSONL."""
    from api.evaluations.repository import EvaluationRepository

    engine, session_factory = _create_celery_session()
    try:
        async with session_factory() as session:
            repo = EvaluationRepository(session)

            # Create spec event
            await repo.create_event(
                trace_id=trace_id,
                event_type="spec",
                data=spec_data,
            )

            # Create sampling event with S3 path
            await repo.create_event(
                trace_id=trace_id,
                event_type="sampling",
                data={"s3_path": results_s3_path},
            )

            # Create report event
            await repo.create_event(
                trace_id=trace_id,
                event_type="report",
                data={"scores": report_scores},
            )

            # Update trace to completed
            trace_summary = {"scores": summary}
            if summary_extra:
                trace_summary.update(summary_extra)
            await repo.update_trace_status(trace_id, "completed", trace_summary)

            # Fetch trace + events for JSONL upload
            trace = await repo.get_trace_by_id(trace_id)
            events = await repo.get_events_by_trace(trace_id)

            return {
                "completion_model": trace.completion_model,
                "dataset_name": trace.dataset_name,
                "trace_id": trace.id,
                "events": [
                    {
                        k: v
                        for k, v in {
                            "event_type": e.event_type,
                            "trace_id": e.trace_id,
                            "sample_id": e.sample_id,
                            "guideline_name": e.guideline_name,
                            "data": e.data,
                            "created_at": (
                                e.created_at.isoformat() if e.created_at else None
                            ),
                        }.items()
                        if v is not None
                    }
                    for e in events
                ],
            }
    finally:
        await engine.dispose()


def _write_events_and_complete_trace(
    trace_id: int,
    spec_data: dict,
    results_s3_path: str,
    report_scores: dict,
    summary: dict,
    summary_extra: dict | None = None,
) -> dict:
    """Write events and complete trace (sync wrapper). Returns trace data for JSONL upload."""
    return _run_async(
        _write_events_and_complete_trace_async(
            trace_id, spec_data, results_s3_path, report_scores, summary, summary_extra
        )
    )


# ==================== D. Summary Extraction ====================


def _extract_task_summary(pipeline_output: dict) -> dict:
    """Extract summary statistics from task pipeline output."""
    summary = {}
    task_results = pipeline_output["summary"]

    for metric_name, value in task_results.items():
        if metric_name.endswith("_stderr"):
            continue

        summary[metric_name] = {
            "mean": round(value, 2),
            "std": round(task_results.get(metric_name + "_stderr", 0), 2),
            "failed": 0,
        }

    return summary


def _extract_llm_judge_summary(
    pipeline_output: dict, guidelines_data: list[dict]
) -> dict:
    """Extract summary statistics for LLM-as-judge evaluations."""
    from api.guidelines.schemas import GuidelineScoringScale

    summary = {}

    for guideline in guidelines_data:
        metric_name = guideline["name"]
        scores = pipeline_output["scores"].get(metric_name, [])
        failed_count = pipeline_output["sample_count"] - len(scores)

        if guideline["scoring_scale"] in [
            GuidelineScoringScale.BOOLEAN,
            GuidelineScoringScale.CUSTOM_CATEGORY,
        ]:
            distribution = {}
            for score in scores:
                key = str(score)
                distribution[key] = distribution.get(key, 0) + 1

            mode = None
            if distribution:
                mode = max(distribution, key=distribution.get)

            summary[metric_name] = {
                "type": "categorical",
                "distribution": distribution,
                "mode": mode,
                "failed": failed_count,
            }
        else:
            if scores:
                mean = statistics.mean(scores)
                std = statistics.stdev(scores) if len(scores) > 1 else 0.0

                summary[metric_name] = {
                    "type": "numeric",
                    "mean": round(mean, 2),
                    "std": round(std, 2),
                    "failed": failed_count,
                }
            else:
                summary[metric_name] = {
                    "type": "numeric",
                    "mean": 0.0,
                    "std": 0.0,
                    "failed": failed_count,
                }

    return summary


def _extract_flexible_summary(
    pipeline_output: dict, judge_type: str, guidelines_data: list[dict]
) -> dict:
    """Extract summary statistics from flexible evaluation output."""
    if judge_type == JudgeType.LLM_AS_JUDGE.value:
        return _extract_llm_judge_summary(pipeline_output, guidelines_data)

    summary = {}
    for metric_name, scores in pipeline_output["scores"].items():
        if isinstance(scores, (int, float)):
            summary[metric_name] = {
                "type": "numeric",
                "mean": round(scores, 4),
                "std": 0.0,
                "failed": 0,
            }
        elif isinstance(scores, list):
            if scores:
                mean = statistics.mean(scores)
                std = statistics.stdev(scores) if len(scores) > 1 else 0.0
                summary[metric_name] = {
                    "type": "numeric",
                    "mean": round(mean, 4),
                    "std": round(std, 4),
                    "failed": pipeline_output["sample_count"] - len(scores),
                }
            else:
                summary[metric_name] = {
                    "type": "numeric",
                    "mean": 0.0,
                    "std": 0.0,
                    "failed": pipeline_output["sample_count"],
                }

    return summary


# ==================== E. S3 Upload Helper ====================


def _upload_trace_jsonl(trace_data: dict) -> None:
    """Upload trace events as JSONL to S3."""
    from api.core.s3 import S3Storage

    s3 = S3Storage()
    lines = []
    for event in trace_data["events"]:
        lines.append(json.dumps(event))

    content = "\n".join(lines)
    safe_model_name = trace_data["completion_model"].replace("/", "-")
    filename = f"{trace_data['trace_id']}_{safe_model_name}-{trace_data['dataset_name']}"
    s3.upload_trace(filename, content)


# ==================== F. Celery Tasks ====================


@celery_app.task(
    bind=True,
    name="evaluations.run_task_evaluation",
    max_retries=0,
    acks_late=True,
    reject_on_worker_lost=True,
)
def run_task_evaluation_task(
    self,
    trace_id: int,
    user_id: str,
    task_name: str,
    n_samples: int | None,
    n_fewshots: int | None,
    model_config_data: dict,
    request_data: dict,
) -> None:
    """Celery task: run a task evaluation pipeline, post-process results, handle errors."""
    try:
        logger.info(f"Starting task evaluation for trace {trace_id}")
        set_eval_progress(trace_id, "starting", 0, "Initializing...")

        def _progress_cb(stage: str, percent: int | None, detail: str = "") -> None:
            set_eval_progress(trace_id, stage, percent, detail)

        pipeline_output = _run_task_pipeline(
            task_name=task_name,
            n_samples=n_samples,
            n_fewshots=n_fewshots,
            model_config_data=model_config_data,
            progress_callback=_progress_cb,
        )

        # Post-process
        metric_docs = pipeline_output.get("metric_docs", {})
        metric_names = list(pipeline_output["scores"].keys())

        # Update trace guidelines with metric names
        _update_trace_guidelines(trace_id, metric_names)

        # Upload eval results to S3
        set_eval_progress(trace_id, "uploading", 90, "Uploading results...")
        from api.core.s3 import S3Storage

        s3 = S3Storage()
        results_s3_path = s3.upload_eval_results(trace_id, pipeline_output["temp_dir"])

        # Extract summary
        summary = _extract_task_summary(pipeline_output)

        # Build spec data from request_data
        spec_data = {
            "task_name": request_data["task_name"],
            "completion_model": request_data["completion_model"],
            "model_provider": request_data["model_provider"],
            "guideline_names": metric_names,
            "sample_count": request_data.get("n_samples"),
            "n_fewshots": request_data.get("n_fewshots"),
        }

        # Write events, complete trace, get trace data for JSONL
        set_eval_progress(trace_id, "finalizing", 95, "Saving to database...")
        trace_data = _write_events_and_complete_trace(
            trace_id=trace_id,
            spec_data=spec_data,
            results_s3_path=results_s3_path,
            report_scores=pipeline_output["summary"],
            summary=summary,
            summary_extra={"metric_docs": metric_docs},
        )

        # Upload JSONL
        _upload_trace_jsonl(trace_data)

        logger.info(f"Task evaluation completed for trace {trace_id}")

    except Exception as e:
        logger.error(f"Task evaluation failed for trace {trace_id}: {e}")
        _mark_trace_failed(trace_id, str(e), traceback.format_exc())
    finally:
        clear_eval_progress(trace_id)


@celery_app.task(
    bind=True,
    name="evaluations.run_flexible_evaluation",
    max_retries=0,
    acks_late=True,
    reject_on_worker_lost=True,
)
def run_flexible_evaluation_task(
    self,
    trace_id: int,
    user_id: str,
    dataset_name: str,
    dataset_content: str,
    input_field: str,
    output_type: str,
    judge_type: str,
    text_config: dict | None,
    mc_config: dict | None,
    guidelines_data: list[dict],
    model_config_data: dict,
    judge_config_data: dict | None,
    request_data: dict,
) -> None:
    """Celery task: run a flexible evaluation pipeline, post-process results, handle errors."""
    try:
        logger.info(f"Starting flexible evaluation for trace {trace_id}")
        set_eval_progress(trace_id, "starting", 0, "Initializing...")

        def _progress_cb(stage: str, percent: int | None, detail: str = "") -> None:
            set_eval_progress(trace_id, stage, percent, detail)

        # Run the pipeline
        pipeline_output = _run_flexible_pipeline(
            dataset_name=dataset_name,
            dataset_content=dataset_content,
            input_field=input_field,
            output_type=output_type,
            judge_type=judge_type,
            text_config=text_config,
            mc_config=mc_config,
            guidelines_data=guidelines_data,
            model_config_data=model_config_data,
            judge_config_data=judge_config_data,
            progress_callback=_progress_cb,
        )

        # Post-process
        metric_names = list(pipeline_output["scores"].keys())

        # Upload eval results to S3
        set_eval_progress(trace_id, "uploading", 90, "Uploading results...")
        from api.core.s3 import S3Storage

        s3 = S3Storage()
        results_s3_path = s3.upload_eval_results(trace_id, pipeline_output["temp_dir"])

        # Extract summary
        summary = _extract_flexible_summary(pipeline_output, judge_type, guidelines_data)

        # Build spec data from request_data
        spec_data = {
            "dataset_name": request_data["dataset_name"],
            "input_field": request_data["input_field"],
            "output_type": request_data["output_type"],
            "judge_type": request_data["judge_type"],
            "completion_model": request_data["completion_model"],
            "model_provider": request_data["model_provider"],
            "judge_model": request_data.get("judge_model", ""),
            "guideline_names": metric_names,
            "sample_count": pipeline_output["sample_count"],
        }

        # Write events, complete trace, get trace data for JSONL
        set_eval_progress(trace_id, "finalizing", 95, "Saving to database...")
        trace_data = _write_events_and_complete_trace(
            trace_id=trace_id,
            spec_data=spec_data,
            results_s3_path=results_s3_path,
            report_scores=pipeline_output["summary"],
            summary=summary,
        )

        # Upload JSONL
        _upload_trace_jsonl(trace_data)

        logger.info(f"Flexible evaluation completed for trace {trace_id}")

    except Exception as e:
        logger.error(f"Flexible evaluation failed for trace {trace_id}: {e}")
        _mark_trace_failed(trace_id, str(e), traceback.format_exc())
    finally:
        clear_eval_progress(trace_id)
