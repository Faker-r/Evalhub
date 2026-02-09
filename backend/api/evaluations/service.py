from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.evaluations.models import Trace
from api.evaluations.repository import EvaluationRepository
from api.evaluations.schemas import (
    FlexibleEvaluationRequest,
    JudgeType,
    ModelConfig,
    TaskEvaluationRequest,
    TaskEvaluationResponse,
    TraceDetailsResponse,
    TraceSample,
    TraceSamplesRequest,
    TraceSamplesResponse,
)
from api.evaluations.tasks import run_flexible_evaluation_task, run_task_evaluation_task
from api.guidelines.models import Guideline
from api.guidelines.schemas import GuidelineScoringScale
from api.guidelines.service import GuidelineService
from api.models_and_providers.service import ModelsAndProvidersService

logger = get_logger(__name__)

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

    async def run_task_evaluation(
        self, request: TaskEvaluationRequest
    ) -> TaskEvaluationResponse:
        """Run an evaluation on a task using lighteval."""

        # Initialize trace in database
        trace = await self._create_task_trace(request)

        # Prepare serializable data for Celery task
        model_config_data = await self._get_serializable_model_config(
            request.model_completion_config
        )
        task_name = self._build_task_name(request)

        request_data = {
            "task_name": request.task_name,
            "completion_model": request.model_completion_config.model_name,
            "model_provider": request.model_completion_config.model_provider,
            "n_samples": request.dataset_config.n_samples,
            "n_fewshots": request.dataset_config.n_fewshots,
        }

        # Dispatch to Celery
        run_task_evaluation_task.delay(
            trace_id=trace.id,
            user_id=self.user_id,
            task_name=task_name,
            n_samples=request.dataset_config.n_samples,
            n_fewshots=request.dataset_config.n_fewshots,
            model_config_data=model_config_data,
            request_data=request_data,
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

    async def run_flexible_evaluation(
        self, request: FlexibleEvaluationRequest
    ) -> TaskEvaluationResponse:
        """Run a flexible evaluation on a dataset with configurable parsing and judging."""
        trace = await self._create_flexible_trace(request)

        # Prepare serializable data for Celery task
        dataset_content = self._load_dataset_content(request.dataset_name)

        guidelines_data = []
        if request.judge_type == JudgeType.LLM_AS_JUDGE and request.guideline_names:
            guidelines = await self._load_guidelines(request.guideline_names)
            guidelines_data = [self._convert_guideline_to_dict(g) for g in guidelines]

        model_config_data = await self._get_serializable_model_config(
            request.model_completion_config
        )

        judge_config_data = None
        if request.judge_config:
            judge_config_data = await self._get_serializable_judge_config(
                request.judge_config
            )

        text_config_data = (
            request.text_config.model_dump() if request.text_config else None
        )
        mc_config_data = (
            request.mc_config.model_dump() if request.mc_config else None
        )

        judge_model = request.judge_config.model_name if request.judge_config else ""

        request_data = {
            "dataset_name": request.dataset_name,
            "input_field": request.input_field,
            "output_type": request.output_type.value,
            "judge_type": request.judge_type.value,
            "completion_model": request.model_completion_config.model_name,
            "model_provider": request.model_completion_config.model_provider,
            "judge_model": judge_model,
        }

        # Dispatch to Celery
        run_flexible_evaluation_task.delay(
            trace_id=trace.id,
            user_id=self.user_id,
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
            request_data=request_data,
        )

        # Return immediately with running status
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

    def _build_task_name(self, request: TaskEvaluationRequest) -> str:
        if "|" in request.task_name:
            return request.task_name
        return f"{request.task_name}|{request.dataset_config.n_fewshots}"

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

    async def get_trace_details(self, trace_id: int) -> TraceDetailsResponse:
        """Get trace details from the spec event."""
        trace = await self.get_trace(trace_id)
        spec_event = await self.repository.get_spec_event_by_trace_id(trace_id)
        if not spec_event:
            raise NotFoundException("Trace details not found")
        return TraceDetailsResponse(
            trace_id=trace.id,
            status=trace.status,
            created_at=trace.created_at,
            judge_model_provider=trace.judge_model_provider,
            spec=spec_event.data,
        )

    async def get_trace_samples(
        self, request: TraceSamplesRequest
    ) -> TraceSamplesResponse:
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
        import os
        import tempfile

        import pandas as pd

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
                            except Exception:
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
                        if model_resp_obj is not None:
                            try:
                                input_text = "\n".join(
                                    [
                                        line["content"]
                                        for line in safe_get(
                                            model_resp_obj, "input", []
                                        )
                                    ]
                                )
                            except Exception as e:
                                logger.error(
                                    f"Failed to extract input text for trace {trace.id}: {e}"
                                )

                        # Fallback to doc object if input text is empty
                        if input_text == "":
                            if doc_obj is not None:
                                input_text = safe_get(doc_obj, "query", "")

                        # Prediction
                        prediction = ""
                        if model_resp_obj is not None:
                            text_val = safe_get(model_resp_obj, "text")

                            # Handle numpy array conversion
                            if hasattr(text_val, "tolist"):
                                text_val = text_val.tolist()

                            if (
                                isinstance(text_val, (list, tuple))
                                and len(text_val) > 0
                            ):
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
                            if (
                                not isinstance(choices, (list, tuple))
                                and choices is not None
                            ):
                                choices = [choices]

                            if gold_idx is not None and choices:
                                if hasattr(gold_idx, "tolist"):
                                    gold_idx = gold_idx.tolist()

                                if isinstance(gold_idx, (list, tuple)):
                                    gold = []
                                    for i in gold_idx:
                                        if isinstance(i, int) and 0 <= i < len(choices):
                                            gold.append(choices[i])
                                elif isinstance(gold_idx, int) and 0 <= gold_idx < len(
                                    choices
                                ):
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
                                for metric_name in trace.guideline_names:
                                    metric_value = safe_get(metrics_obj, metric_name)
                                    normalized = None
                                    if (
                                        hasattr(metric_value, "item")
                                        and getattr(metric_value, "size", 2) == 1
                                    ):
                                        metric_value = metric_value.item()
                                    if isinstance(metric_value, bool):
                                        normalized = metric_value
                                    elif isinstance(metric_value, int):
                                        normalized = metric_value
                                    elif isinstance(metric_value, float):
                                        normalized = (
                                            int(metric_value)
                                            if metric_value == int(metric_value)
                                            else metric_value
                                        )
                                    elif isinstance(metric_value, str):
                                        normalized = metric_value
                                    else:
                                        normalized = str(metric_value)
                                    metric_scores[metric_name] = normalized

                        samples.append(
                            TraceSample(
                                input=input_text,
                                prediction=prediction,
                                gold=gold,
                                metric_scores=metric_scores,
                            )
                        )
                        count += 1

                    if len(samples) >= request.n_samples:
                        break

                except Exception as e:
                    logger.error(f"Failed to read parquet file {filename}: {e}")
                    continue

        return TraceSamplesResponse(samples=samples[: request.n_samples])
