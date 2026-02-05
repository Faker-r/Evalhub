import tempfile
import traceback
from dataclasses import asdict

from api.core.logging import get_logger
from api.evaluations.eval_pipeline.dataset_task import DatasetTask
from api.evaluations.eval_pipeline.eval_pipeline import (
    CustomTaskEvaluationPipeline,
    CustomTaskEvaluationPipelineParameters,
)
from api.evaluations.eval_pipeline.flexible_dataset_task import FlexibleDatasetTask
from api.evaluations.eval_pipeline.guideline_judge import GuidelineJudgeMetric
from api.evaluations.eval_pipeline.metric_doc_generator import MetricDocGenerator
from api.evaluations.schemas import JudgeType
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.endpoints.openai_model import (
    OpenAICompatibleClient,
    OpenAICompatibleModelConfig,
)
from lighteval.models.model_input import GenerationParameters
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.tasks.registry import Registry

logger = get_logger(__name__)

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


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


def run_lighteval_pipeline_worker(
    dataset_name: str,
    dataset_content: str,
    guidelines_data: list[dict],
    model_config_data: dict,
    judge_config_data: dict,
) -> dict:
    """
    Run the lighteval pipeline in a worker process.

    This function runs in a separate process with its own main thread,
    allowing metrics that require main-thread execution to work correctly.

    Args:
        dataset_name: Name of the dataset
        dataset_content: Raw dataset content
        guidelines_data: List of guideline dicts with name, prompt, scoring_scale, scoring_scale_config
        model_config_data: Dict with model_name, base_url, api_key, and optional extra_body
        judge_config_data: Dict with model_name, base_url, api_key, and optional extra_body

    Returns:
        Dict with keys: summary, scores, sample_count, temp_dir, or error info
    """
    try:
        # Create judge metrics from guidelines
        metrics = []
        for guideline in guidelines_data:
            metric = GuidelineJudgeMetric(
                guideline=guideline,
                model=judge_config_data["model_name"],
                url=judge_config_data["base_url"],
                api_key=judge_config_data["api_key"],
                extra_body=judge_config_data.get("extra_body", {}),
            )
            metrics.append(metric)

        # Create DatasetTask
        dataset_task = DatasetTask(
            dataset_name=dataset_name,
            dataset_content=dataset_content,
            metrics=metrics,
        )
        task = dataset_task.build_lighteval_task()

        # Create registry for proper cache hashing
        registry = Registry(tasks=None)
        registry._task_registry[dataset_name] = task.config
        registry.task_to_configs = {dataset_name: [task.config]}

        # Create model client
        model_config = _create_model_config(model_config_data)
        model = OpenAICompatibleClient(model_config)

        # Initialize registry on model cache
        if hasattr(model, "_cache") and model._cache is not None:
            model._cache._init_registry(registry)

        # Create evaluation tracker with temporary directory
        temp_dir = tempfile.mkdtemp()
        evaluation_tracker = EvaluationTracker(
            output_dir=temp_dir,
            save_details=True,
            push_to_hub=False,
        )

        # Run evaluation pipeline
        pipeline = CustomTaskEvaluationPipeline(
            task=task,
            evaluation_tracker=evaluation_tracker,
            model=model,
            params=CustomTaskEvaluationPipelineParameters(
                max_samples=None, save_details=True, use_cache=True
            ),
        )

        results = pipeline.evaluate()
        pipeline.save_and_push_results()

        # Cleanup
        dataset_task.cleanup()

        return {
            "success": True,
            "summary": results["summary"],
            "scores": results["scores"],
            "sample_count": results["sample_count"],
            "temp_dir": temp_dir,
        }
    except Exception as e:
        logger.error(f"Worker pipeline failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def run_lighteval_task_pipeline_worker(
    task_name: str,
    n_samples: int | None,
    n_fewshots: int | None,
    model_config_data: dict,
) -> dict:
    """
    Run a task evaluation pipeline in a worker process.

    Args:
        task_name: Name of the lighteval task
        n_samples: Maximum number of samples
        n_fewshots: Number of few-shot examples
        model_config_data: Dict with model_name, base_url, api_key, and optional extra_body

    Returns:
        Dict with keys: summary, scores, sample_count, temp_dir, metric_docs, or error info
    """
    try:
        # Create evaluation tracker with temporary directory
        temp_dir = tempfile.mkdtemp()
        evaluation_tracker = EvaluationTracker(
            output_dir=temp_dir,
            save_details=True,
        )

        # Create pipeline parameters
        pipeline_params = PipelineParameters(
            launcher_type=ParallelismManager.ACCELERATE,
            max_samples=n_samples,
        )

        # Create model config
        model_config = _create_model_config(model_config_data)

        # Build full task name if needed
        if "|" not in task_name:
            full_task_name = f"{task_name}|{n_fewshots}"
        else:
            full_task_name = task_name

        # Create pipeline
        pipeline = Pipeline(
            tasks=full_task_name,
            pipeline_parameters=pipeline_params,
            evaluation_tracker=evaluation_tracker,
            model_config=model_config,
        )

        # Run pipeline
        pipeline.evaluate()
        pipeline.save_and_push_results()

        results = pipeline.get_results()

        # Extract task results
        task_results = results["results"]["all"]

        # Extract scores by metric
        scores_by_metric = {}
        for metric_name, value in task_results.items():
            if not metric_name.endswith("_stderr"):
                scores_by_metric[metric_name] = value

        # Extract sample count from config_general
        actual_sample_count = results.get("config_general", {}).get(
            "max_samples", n_samples
        )

        # Generate metric docs
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
            "success": True,
            "summary": task_results,
            "scores": scores_by_metric,
            "sample_count": actual_sample_count,
            "temp_dir": temp_dir,
            "metric_docs": metric_docs_serialized,
        }
    except Exception as e:
        logger.error(f"Worker task pipeline failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def run_flexible_lighteval_pipeline_worker(
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
) -> dict:
    """
    Run a flexible evaluation pipeline in a worker process.

    Args:
        dataset_name: Name of the dataset
        dataset_content: Raw dataset content
        input_field: Field name for input
        output_type: "text" or "multiple_choice"
        judge_type: "llm_as_judge", "f1_score", or "exact_match"
        text_config: Config for text output type
        mc_config: Config for multiple choice output type
        guidelines_data: List of guideline dicts (for llm_as_judge)
        model_config_data: Dict with model_name, base_url, api_key, and optional extra_body
        judge_config_data: Dict with model_name, base_url, api_key, and optional extra_body (for llm_as_judge)

    Returns:
        Dict with keys: summary, scores, sample_count, temp_dir, or error info
    """
    try:
        from api.evaluations.schemas import (
            MultipleChoiceConfig,
            OutputType,
            TextOutputConfig,
        )

        # Convert string enums back to enum types
        output_type_enum = OutputType(output_type)
        judge_type_enum = JudgeType(judge_type)

        # Create guideline metrics if using LLM as judge
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

        # Convert configs back to Pydantic models
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
        )

        results = pipeline.evaluate()
        pipeline.save_and_push_results()

        dataset_task.cleanup()

        return {
            "success": True,
            "summary": results["summary"],
            "scores": results["scores"],
            "sample_count": results["sample_count"],
            "temp_dir": temp_dir,
        }
    except Exception as e:
        logger.error(f"Worker flexible pipeline failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
