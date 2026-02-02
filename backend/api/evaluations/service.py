import json
import statistics
import asyncio
import traceback
from concurrent.futures import ProcessPoolExecutor
import functools

from api.models_and_providers.service import ModelsAndProvidersService
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.core.database import get_session
from api.evaluations.models import Trace
from api.evaluations.repository import EvaluationRepository
from api.evaluations.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    TaskEvaluationRequest,
    TaskEvaluationResponse,
    FlexibleEvaluationRequest,
    JudgeType,
    ModelConfig,
    TraceSamplesRequest,
    TraceSamplesResponse,
    TraceSample,
)
from api.guidelines.models import Guideline
from api.guidelines.service import GuidelineService
from api.guidelines.schemas import GuidelineScoringScale
from api.evaluations.eval_worker import (
    run_lighteval_pipeline_worker,
    run_lighteval_task_pipeline_worker,
    run_flexible_lighteval_pipeline_worker,
)

logger = get_logger(__name__)

# Process pool for running evaluations in separate processes
# This allows evaluations to run on their own main thread, fixing thread-affinity issues
# and preventing blocking of the FastAPI event loop
_process_pool: ProcessPoolExecutor | None = None


def get_process_pool() -> ProcessPoolExecutor:
    """Get or create the process pool for evaluation workers."""
    global _process_pool
    if _process_pool is None:
        # Use a small number of workers since evaluations are I/O bound (API calls)
        # and each process consumes memory
        _process_pool = ProcessPoolExecutor(max_workers=4)
    return _process_pool


def shutdown_process_pool():
    """Shutdown the process pool gracefully."""
    global _process_pool
    if _process_pool is not None:
        _process_pool.shutdown(wait=True)
        _process_pool = None


OPENROUTER_PROVIDER_SLUG = "openrouter"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


class EvaluationService:
    """Service for running evaluations."""

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.repository = EvaluationRepository(session)
        self.guideline_service = GuidelineService(session)
        self.s3 = S3Storage()
        self.model_providers_service = ModelsAndProvidersService(session)

    # ==================== Main Entry Point ====================

    async def run_evaluation(self, request: EvaluationRequest) -> EvaluationResponse:
        """Run an evaluation on a dataset with given guidelines using lighteval."""
        # Initialize trace in database
        trace = await self._create_trace(request)

        # Start background evaluation
        asyncio.create_task(
            EvaluationService._run_evaluation_background(trace.id, request)
        )

        # Return immediately with running status
        return EvaluationResponse(
            trace_id=trace.id,
            status="running",
            dataset_name=request.dataset_name,
            sample_count=0,
            guideline_names=request.guideline_names,
            completion_model=request.model_completion_config.model_name,
            model_provider=request.model_completion_config.model_provider,
            judge_model=request.judge_config.model_name,
            scores={},
            created_at=trace.created_at,
        )

    @staticmethod
    async def _run_evaluation_background(trace_id: int, request: EvaluationRequest):
        """Run evaluation in background using a separate process.

        The evaluation pipeline runs in a separate process to:
        1. Prevent blocking the FastAPI event loop
        2. Allow metrics that require main-thread execution to work correctly
        """
        async for session in get_session():
            repository = EvaluationRepository(session)
            try:
                # Get trace to get user_id
                trace = await repository.get_trace_by_id(trace_id)
                service = EvaluationService(session, trace.user_id)

                # Setup phase
                dataset_content = service._load_dataset_content(request.dataset_name)
                guidelines = await service._load_guidelines(request.guideline_names)

                # Convert guidelines to serializable dicts for the worker
                guidelines_data = [
                    service._convert_guideline_to_dict(g) for g in guidelines
                ]

                # Get model and judge configs as serializable dicts
                model_config_data = await service._get_serializable_model_config(
                    request.model_completion_config
                )
                judge_config_data = await service._get_serializable_judge_config(
                    request.judge_config
                )

                # Run pipeline in a separate process
                loop = asyncio.get_event_loop()
                pool = get_process_pool()
                pipeline_output = await loop.run_in_executor(
                    pool,
                    functools.partial(
                        run_lighteval_pipeline_worker,
                        dataset_name=request.dataset_name,
                        dataset_content=dataset_content,
                        guidelines_data=guidelines_data,
                        model_config_data=model_config_data,
                        judge_config_data=judge_config_data,
                    ),
                )

                # Check for worker errors
                if not pipeline_output.get("success", False):
                    raise Exception(
                        f"Worker failed: {pipeline_output.get('error', 'Unknown error')}\n"
                        f"{pipeline_output.get('traceback', '')}"
                    )

                # Write results to database and upload to S3
                trace = await repository.get_trace_by_id(trace_id)
                await service._write_results(trace, request, pipeline_output)

                # Finalize
                summary = service._extract_summary(pipeline_output, guidelines)
                await repository.update_trace_status(
                    trace_id, "completed", {"scores": summary}
                )

                # Upload trace to S3
                trace = await repository.get_trace_by_id(trace_id)
                await service._upload_trace_jsonl_simple(trace)

            except Exception as e:
                logger.error("Evaluation failed: %s", e)
                await repository.update_trace_status(
                    trace_id,
                    "failed",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            finally:
                await session.close()
            break

    async def run_task_evaluation(
        self, request: TaskEvaluationRequest
    ) -> TaskEvaluationResponse:
        """Run an evaluation on a task using lighteval."""

        # Initialize trace in database
        trace = await self._create_task_trace(request)

        # Start background evaluation
        asyncio.create_task(
            EvaluationService._run_task_evaluation_background(trace.id, request)
        )

        # Return immediately with running status
        judge_model = request.judge_config.model_name if request.judge_config else ""
        return TaskEvaluationResponse(
            trace_id=trace.id,
            status="running",
            task_name=request.task_name,
            sample_count=0,
            guideline_names=[],
            completion_model=request.model_completion_config.model_name,
            model_provider=request.model_completion_config.model_provider,
            judge_model=judge_model,
            created_at=trace.created_at,
        )

    @staticmethod
    async def _run_task_evaluation_background(
        trace_id: int, request: TaskEvaluationRequest
    ):
        """Run task evaluation in background using a separate process."""
        async for session in get_session():
            repository = EvaluationRepository(session)
            try:
                # Get trace to get user_id
                trace = await repository.get_trace_by_id(trace_id)
                service = EvaluationService(session, trace.user_id)

                # Get model config as serializable dict
                model_config_data = await service._get_serializable_model_config(
                    request.model_completion_config
                )

                task_name = service._build_task_name(request)

                # Run pipeline in a separate process
                loop = asyncio.get_event_loop()
                pool = get_process_pool()
                pipeline_output = await loop.run_in_executor(
                    pool,
                    functools.partial(
                        run_lighteval_task_pipeline_worker,
                        task_name=task_name,
                        n_samples=request.dataset_config.n_samples,
                        n_fewshots=request.dataset_config.n_fewshots,
                        model_config_data=model_config_data,
                    ),
                )

                # Check for worker errors
                if not pipeline_output.get("success", False):
                    raise Exception(
                        f"Worker failed: {pipeline_output.get('error', 'Unknown error')}\n"
                        f"{pipeline_output.get('traceback', '')}"
                    )

                metric_docs = pipeline_output.get("metric_docs", {})

                # Extract metric names to use as guidelines
                metric_names = list(pipeline_output["scores"].keys())

                # Update trace with metric names as guidelines
                trace = await service._update_trace_guidelines(trace, metric_names)

                # Write results to database and upload to S3
                await service._write_task_results(
                    trace, request, pipeline_output, metric_names
                )

                # Finalize
                summary = service._extract_task_summary(pipeline_output)
                await repository.update_trace_status(
                    trace_id,
                    "completed",
                    {"scores": summary, "metric_docs": metric_docs},
                )

                # Upload trace to S3
                trace = await repository.get_trace_by_id(trace_id)
                await service._upload_trace_jsonl_simple(trace)

            except Exception as e:
                logger.error("Evaluation failed: %s", e)
                await repository.update_trace_status(
                    trace_id,
                    "failed",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            finally:
                await session.close()
            break

    async def run_flexible_evaluation(
        self, request: FlexibleEvaluationRequest
    ) -> TaskEvaluationResponse:
        """Run a flexible evaluation on a dataset with configurable parsing and judging."""
        trace = await self._create_flexible_trace(request)

        asyncio.create_task(
            EvaluationService._run_flexible_evaluation_background(trace.id, request)
        )

        judge_model = request.judge_config.model_name if request.judge_config else ""
        guideline_names = request.guideline_names or []
        if request.judge_type != JudgeType.LLM_AS_JUDGE:
            guideline_names = [request.judge_type.value]

        return TaskEvaluationResponse(
            trace_id=trace.id,
            status="running",
            task_name=request.dataset_name,
            sample_count=0,
            guideline_names=guideline_names,
            completion_model=request.model_completion_config.model_name,
            model_provider=request.model_completion_config.model_provider,
            judge_model=judge_model,
            created_at=trace.created_at,
        )

    @staticmethod
    async def _run_flexible_evaluation_background(
        trace_id: int, request: FlexibleEvaluationRequest
    ):
        """Run flexible evaluation in background using a separate process."""
        async for session in get_session():
            repository = EvaluationRepository(session)
            try:
                trace = await repository.get_trace_by_id(trace_id)
                service = EvaluationService(session, trace.user_id)

                dataset_content = service._load_dataset_content(request.dataset_name)

                guidelines = []
                guidelines_data = []
                if (
                    request.judge_type == JudgeType.LLM_AS_JUDGE
                    and request.guideline_names
                ):
                    guidelines = await service._load_guidelines(request.guideline_names)
                    guidelines_data = [
                        service._convert_guideline_to_dict(g) for g in guidelines
                    ]

                # Get model and judge configs as serializable dicts
                model_config_data = await service._get_serializable_model_config(
                    request.model_completion_config
                )
                judge_config_data = None
                if request.judge_config:
                    judge_config_data = await service._get_serializable_judge_config(
                        request.judge_config
                    )

                # Convert configs to serializable dicts
                text_config_data = (
                    request.text_config.model_dump() if request.text_config else None
                )
                mc_config_data = (
                    request.mc_config.model_dump() if request.mc_config else None
                )

                # Run pipeline in a separate process
                loop = asyncio.get_event_loop()
                pool = get_process_pool()
                pipeline_output = await loop.run_in_executor(
                    pool,
                    functools.partial(
                        run_flexible_lighteval_pipeline_worker,
                        dataset_name=request.dataset_name,
                        dataset_content=dataset_content,
                        input_field=request.input_field,
                        output_type=request.output_type.value,
                        judge_type=request.judge_type.value,
                        text_config=text_config_data,
                        mc_config=mc_config_data,
                        guidelines_data=guidelines_data,
                        model_config_data=model_config_data,
                        judge_config_data=judge_config_data,
                    ),
                )

                # Check for worker errors
                if not pipeline_output.get("success", False):
                    raise Exception(
                        f"Worker failed: {pipeline_output.get('error', 'Unknown error')}\n"
                        f"{pipeline_output.get('traceback', '')}"
                    )

                trace = await repository.get_trace_by_id(trace_id)
                metric_names = list(pipeline_output["scores"].keys())

                await service._write_flexible_results(
                    trace, request, pipeline_output, metric_names
                )

                summary = service._extract_flexible_summary(
                    pipeline_output, request, guidelines
                )
                await repository.update_trace_status(
                    trace_id, "completed", {"scores": summary}
                )

                trace = await repository.get_trace_by_id(trace_id)
                await service._upload_trace_jsonl_simple(trace)

            except Exception as e:
                logger.error("Flexible evaluation failed: %s", e)
                await repository.update_trace_status(
                    trace_id,
                    "failed",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            finally:
                await session.close()
            break

    # ==================== Lighteval Integration ====================

    def _load_dataset_content(self, dataset_name: str) -> str:
        """Load dataset content from S3."""
        return self.s3.download_dataset(dataset_name)

    def _to_stored_config(self, config: ModelConfig) -> dict:
        return {
            "api_source": config.api_source,
            "api_name": config.api_name,
            "provider_slug": config.model_provider_slug,
        }

    async def _create_trace(self, request: EvaluationRequest) -> Trace:
        """Create initial trace in database."""
        completion_config = self._to_stored_config(request.model_completion_config)
        judge_config = self._to_stored_config(request.judge_config)
        return await self.repository.create_trace(
            user_id=self.user_id,
            dataset_name=request.dataset_name,
            guideline_names=request.guideline_names,
            completion_model_config=completion_config,
            judge_model_config=judge_config,
        )

    async def _create_task_trace(self, request: TaskEvaluationRequest) -> Trace:
        """Create initial trace in database."""
        completion_config = self._to_stored_config(request.model_completion_config)
        judge_config = (
            self._to_stored_config(request.judge_config)
            if request.judge_config
            else {
                "api_source": "standard",
                "api_name": "",
                "provider_slug": request.model_completion_config.model_provider_slug,
            }
        )
        return await self.repository.create_trace(
            user_id=self.user_id,
            dataset_name=request.task_name,
            guideline_names=[],
            completion_model_config=completion_config,
            judge_model_config=judge_config,
        )

    async def _create_flexible_trace(self, request: FlexibleEvaluationRequest) -> Trace:
        """Create initial trace for flexible evaluation."""
        completion_config = self._to_stored_config(request.model_completion_config)
        judge_config = (
            self._to_stored_config(request.judge_config)
            if request.judge_config
            else {
                "api_source": "standard",
                "api_name": "",
                "provider_slug": request.model_completion_config.model_provider_slug,
            }
        )
        guideline_names = request.guideline_names or []
        if request.judge_type != JudgeType.LLM_AS_JUDGE:
            guideline_names = [request.judge_type.value]

        return await self.repository.create_trace(
            user_id=self.user_id,
            dataset_name=request.dataset_name,
            guideline_names=guideline_names,
            completion_model_config=completion_config,
            judge_model_config=judge_config,
        )

    async def _update_trace_guidelines(
        self, trace: Trace, guideline_names: list[str]
    ) -> Trace:
        """Update trace with guideline names."""
        if guideline_names:
            trace.guideline_names = guideline_names
            await self.session.commit()
            await self.session.refresh(trace)
        return trace

    def _convert_guideline_to_dict(self, guideline: Guideline) -> dict:
        """Convert Guideline model to dict format for GuidelineJudgeMetric."""
        config_dict = {}
        if guideline.scoring_scale == GuidelineScoringScale.NUMERIC:
            config_dict = {
                "min_value": guideline.scoring_scale_config.get("min_value", 0),
                "max_value": guideline.scoring_scale_config.get("max_value", 10),
            }
        elif guideline.scoring_scale == GuidelineScoringScale.CUSTOM_CATEGORY:
            config_dict = {
                "categories": guideline.scoring_scale_config.get("categories", []),
            }

        return {
            "name": guideline.name,
            "prompt": guideline.prompt,
            "scoring_scale": guideline.scoring_scale,
            "scoring_scale_config": config_dict,
        }

    async def _get_model_api_name_and_base_url(
        self, model_provider_id: int, model_id: int
    ) -> tuple[str, str]:
        provider = await self.model_providers_service.get_provider(model_provider_id)
        if not provider:
            raise ValueError(f"Provider with id {model_provider_id} not found")

        model = await self.model_providers_service.get_model(model_id)
        if not model:
            raise ValueError(f"Model with id {model_id} not found")

        return model.api_name, provider.base_url

    async def _create_judge_client_parameters(self, judge_config: ModelConfig) -> dict:
        if judge_config.api_source == "standard":
            model_api_key = self.s3.download_api_key(
                self.user_id, judge_config.model_provider_slug
            )
            model_name, model_url = await self._get_model_api_name_and_base_url(
                judge_config.model_provider_id,
                judge_config.model_id,
            )
            return {
                "model_name": model_name,
                "base_url": model_url,
                "api_key": model_api_key,
            }
        else:
            model_api_key = self.s3.download_api_key(
                self.user_id, OPENROUTER_PROVIDER_SLUG
            )
            return {
                "model_name": judge_config.api_name,
                "base_url": OPENROUTER_API_BASE,
                "api_key": model_api_key,
                "extra_body": {
                    "provider": {
                        "order": [judge_config.model_provider_slug],
                        "allow_fallbacks": False,
                    }
                },
            }

    async def _get_serializable_model_config(
        self, model_completion_config: ModelConfig
    ) -> dict:
        """Get model config as a serializable dict for worker processes."""
        if model_completion_config.api_source == "standard":
            model_api_key = self.s3.download_api_key(
                self.user_id, model_completion_config.model_provider_slug
            )
            model_name, model_url = await self._get_model_api_name_and_base_url(
                model_completion_config.model_provider_id,
                model_completion_config.model_id,
            )
            return {
                "model_name": model_name,
                "base_url": model_url,
                "api_key": model_api_key,
            }
        else:
            model_api_key = self.s3.download_api_key(
                self.user_id, OPENROUTER_PROVIDER_SLUG
            )
            return {
                "model_name": model_completion_config.api_name,
                "base_url": OPENROUTER_API_BASE,
                "api_key": model_api_key,
                "extra_body": {
                    "provider": {
                        "order": [model_completion_config.model_provider_slug],
                        "allow_fallbacks": False,
                    }
                },
            }

    async def _get_serializable_judge_config(self, judge_config: ModelConfig) -> dict:
        """Get judge config as a serializable dict for worker processes."""
        return await self._create_judge_client_parameters(judge_config)

    async def _write_results(
        self,
        trace: Trace,
        request: EvaluationRequest,
        pipeline_output: dict,
    ) -> None:
        """Write evaluation results to database as events."""
        # Create spec event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="spec",
            data={
                "dataset_name": request.dataset_name,
                "guideline_names": request.guideline_names,
                "completion_model": request.model_completion_config.model_name,
                "model_provider": request.model_completion_config.model_provider,
                "judge_model": request.judge_config.model_name,
                "sample_count": pipeline_output["sample_count"],
            },
        )

        # Upload evaluation results directory to S3
        s3_path = self.s3.upload_eval_results(trace.id, pipeline_output["temp_dir"])

        # Create sampling event with S3 path
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="sampling",
            data={"s3_path": s3_path},
        )

        # Create report event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="report",
            data={"scores": pipeline_output["summary"]},
        )

    async def _write_task_results(
        self,
        trace: Trace,
        request: TaskEvaluationRequest,
        pipeline_output: dict,
        metric_names: list[str],
    ) -> None:
        """Write task evaluation results to database as events."""
        # Create spec event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="spec",
            data={
                "task_name": request.task_name,
                "completion_model": request.model_completion_config.model_name,
                "model_provider": request.model_completion_config.model_provider,
                "guideline_names": metric_names,
                "sample_count": request.dataset_config.n_samples,
                "n_fewshots": request.dataset_config.n_fewshots,
            },
        )

        # Upload evaluation results directory to S3
        s3_path = self.s3.upload_eval_results(trace.id, pipeline_output["temp_dir"])

        # Create sampling event with S3 path
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="sampling",
            data={"s3_path": s3_path},
        )

        # Create report event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="report",
            data={
                "scores": pipeline_output["summary"],
            },
        )

    async def _write_flexible_results(
        self,
        trace: Trace,
        request: FlexibleEvaluationRequest,
        pipeline_output: dict,
        metric_names: list[str],
    ) -> None:
        """Write flexible evaluation results to database as events."""
        judge_model = request.judge_config.model_name if request.judge_config else ""
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="spec",
            data={
                "dataset_name": request.dataset_name,
                "input_field": request.input_field,
                "output_type": request.output_type.value,
                "judge_type": request.judge_type.value,
                "completion_model": request.model_completion_config.model_name,
                "model_provider": request.model_completion_config.model_provider,
                "judge_model": judge_model,
                "guideline_names": metric_names,
                "sample_count": pipeline_output["sample_count"],
            },
        )

        s3_path = self.s3.upload_eval_results(trace.id, pipeline_output["temp_dir"])

        await self.repository.create_event(
            trace_id=trace.id,
            event_type="sampling",
            data={"s3_path": s3_path},
        )

        await self.repository.create_event(
            trace_id=trace.id,
            event_type="report",
            data={"scores": pipeline_output["summary"]},
        )

    def _extract_summary(
        self, pipeline_output: dict, guidelines: list[Guideline]
    ) -> dict:
        """Extract summary statistics from pipeline output."""
        summary = {}

        for guideline in guidelines:
            metric_name = guideline.name
            scores = pipeline_output["scores"].get(metric_name, [])
            failed_count = pipeline_output["sample_count"] - len(scores)

            # Calculate statistics based on scoring scale
            if guideline.scoring_scale in [
                GuidelineScoringScale.BOOLEAN,
                GuidelineScoringScale.CUSTOM_CATEGORY,
            ]:
                # Categorical: distribution + mode
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
                # Numeric/Percentage: mean, std
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

    def _extract_task_summary(self, pipeline_output: dict) -> dict:
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

    def _extract_flexible_summary(
        self,
        pipeline_output: dict,
        request: FlexibleEvaluationRequest,
        guidelines: list[Guideline],
    ) -> dict:
        """Extract summary statistics from flexible evaluation output."""
        if request.judge_type == JudgeType.LLM_AS_JUDGE:
            return self._extract_summary(pipeline_output, guidelines)

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

    def _build_task_name(self, request: TaskEvaluationRequest) -> str:
        if "|" in request.task_name:
            return request.task_name
        return f"{request.task_name}|{request.dataset_config.n_fewshots}"

    async def _upload_trace_jsonl_simple(self, trace: Trace) -> None:
        """Upload trace events as JSONL to S3."""
        events = await self.repository.get_events_by_trace(trace.id)

        lines = []
        for event in events:
            line_data = {
                "event_type": event.event_type,
                "trace_id": event.trace_id,
                "sample_id": event.sample_id,
                "guideline_name": event.guideline_name,
                "data": event.data,
                "created_at": (
                    event.created_at.isoformat() if event.created_at else None
                ),
            }
            line_data = {k: v for k, v in line_data.items() if v is not None}
            lines.append(json.dumps(line_data))

        content = "\n".join(lines)
        safe_model_name = trace.completion_model.replace("/", "-")
        filename = f"{trace.id}_{safe_model_name}-{trace.dataset_name}"
        self.s3.upload_trace(filename, content)

    async def _load_guidelines(self, guideline_names: list[str]) -> list[Guideline]:
        """Load guidelines from database."""
        guidelines = []
        for name in guideline_names:
            guideline = await self.guideline_service.get_guideline_by_name(name)
            guidelines.append(guideline)
        return guidelines

    # ==================== Public Query Methods ====================

    async def get_traces(self) -> list[Trace]:
        """Get all traces for the current user."""
        return await self.repository.get_traces_by_user(self.user_id)

    async def get_trace(self, trace_id: int) -> Trace:
        """Get a specific trace."""
        trace = await self.repository.get_trace_by_id(trace_id)

        if trace.user_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this trace",
            )

        return trace

    async def get_trace_samples(self, request: TraceSamplesRequest) -> TraceSamplesResponse:
        """Get samples for a trace from S3 details parquet files."""
        trace = await self.get_trace(request.trace_id)
        
        # We need to find the details file for this trace in S3
        # The path structure is defined in EvaluationTracker and S3Storage
        # EVAL_RESULTS_PREFIX/{trace_id}/{relative_path}
        
        # First list files for this trace
        from api.core.s3 import EVAL_RESULTS_PREFIX
        prefix = f"{EVAL_RESULTS_PREFIX}/{trace.id}/details"
        
        s3_files = self.s3.list_files(prefix)
        logger.debug(f"Found {len(s3_files)} files for trace {trace.id}")
        
        if not s3_files:
            return TraceSamplesResponse(samples=[])
        
        # Find parquet files
        parquet_files = [f for f in s3_files if f.endswith(".parquet")]
        if not parquet_files:
            return TraceSamplesResponse(samples=[])
            
        # Download the first parquet file to a temporary location
        # In a more robust implementation we might want to sample from multiple files
        # or handle multiple tasks properly. For now we take the first available one.
        import pandas as pd
        import tempfile
        import os
        
        samples = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for s3_key in parquet_files:
                filename = os.path.basename(s3_key)
                local_path = os.path.join(temp_dir, filename)
                
                self.s3.download_file(s3_key, local_path)
                
                try:
                    df = pd.read_parquet(local_path)
                    
                    # Take up to n_samples
                    # We iterate to find good samples (non-empty)
                    count = 0
                    
                    # Helper for safe extraction
                    def safe_get(obj, key, default=None):
                        if isinstance(obj, dict):
                            return obj.get(key, default)
                        if hasattr(obj, "__getitem__"):
                            try:
                                return obj[key]
                            except (Exception):
                                pass
                        if hasattr(obj, key):
                            return getattr(obj, key)
                        return default

                    for _, row in df.iterrows():
                        if count >= request.n_samples:
                            break
                            
                        # Extract data from the row
                        # The structure matches DetailsLogger.Detail
                        
                        doc_obj = row.get("doc")
                        model_resp_obj = row.get("model_response")
                        metrics_obj = row.get("metric")
                        
                        # Input
                        input_text = ""
                        if doc_obj is not None:
                             input_text = safe_get(doc_obj, "query", "")
                        
                        # Prediction
                        prediction = ""
                        if model_resp_obj is not None:
                            text_val = safe_get(model_resp_obj, "text")
                            
                            # Handle numpy array conversion
                            if hasattr(text_val, "tolist"):
                                text_val = text_val.tolist()
                                
                            if isinstance(text_val, (list, tuple)) and len(text_val) > 0:
                                prediction = text_val[0]
                            elif isinstance(text_val, str):
                                prediction = text_val
                        
                        # Gold
                        gold = None
                        if doc_obj is not None:
                            # Try to get gold from gold_index and choices (MCQ style)
                            gold_idx = safe_get(doc_obj, "gold_index")
                            choices = safe_get(doc_obj, "choices", [])
                            
                            # Handle numpy array conversion
                            if hasattr(choices, "tolist"):
                                choices = choices.tolist()
                                
                            # Convert choices to list if it is not already
                            if not isinstance(choices, (list, tuple)) and choices is not None:
                                choices = [choices]

                            if gold_idx is not None and choices:
                                if hasattr(gold_idx, "tolist"):
                                     gold_idx = gold_idx.tolist()
                                     
                                if isinstance(gold_idx, (list, tuple)):
                                    gold = []
                                    for i in gold_idx:
                                        if isinstance(i, int) and 0 <= i < len(choices):
                                            gold.append(choices[i])
                                elif isinstance(gold_idx, int) and 0 <= gold_idx < len(choices):
                                    gold = choices[gold_idx]
                            
                            # Fallback: Try to get gold from choices directly if gold_index logic failed or wasn't applicable
                            # Some tasks store gold directly in choices if it's a generative task with reference answers
                            if gold is None and choices and len(choices) > 0:
                                # For some generative tasks, choices might contain the reference answers directly
                                # This is common in lighteval for tasks like exact_match where choices acts as references
                                gold = choices
                                
                            # If gold is still None but gold_index was not None, maybe gold_index IS the answer (if choices was empty)
                            if gold is None and gold_idx is not None and not choices:
                                gold = str(gold_idx)

                        # Metrics
                        metric_scores = {}
                        if metrics_obj is not None:
                            if hasattr(metrics_obj, "items"):
                                try:
                                    for k, v in metrics_obj.items():
                                        metric_scores[k] = float(v)
                                except:
                                    pass

                        samples.append(TraceSample(
                            input=input_text,
                            prediction=prediction,
                            gold=gold,
                            metric_scores=metric_scores
                        ))
                        count += 1
                        
                    if len(samples) >= request.n_samples:
                        break
                        
                except Exception as e:
                    logger.error(f"Failed to read parquet file {filename}: {e}")
                    continue
                    
        return TraceSamplesResponse(samples=samples[:request.n_samples])
