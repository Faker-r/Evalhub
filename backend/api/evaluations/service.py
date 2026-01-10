import asyncio
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from fastapi import HTTPException, status
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.evaluations.models import Trace
from api.evaluations.repository import EvaluationRepository
from api.evaluations.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    CategoricalScoreDistribution,
    NumericScoreDistribution,
)
from api.guidelines.models import Guideline
from api.guidelines.service import GuidelineService
from api.guidelines.schemas import GuidelineScoringScale
from api.evaluations.eval_pipeline.dataset_task import DatasetTask
from api.evaluations.eval_pipeline.eval_pipeline import (
    EvaluationPipeline,
    EvaluationPipelineParameters,
)
from api.evaluations.eval_pipeline.guideline_judge import GuidelineJudgeMetric

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.endpoints.litellm_model import LiteLLMModelConfig, LiteLLMClient
from lighteval.tasks.registry import Registry

logger = get_logger(__name__)

# Threadpool configuration for parallel API calls
MAX_WORKERS = 20

# Default API bases for providers
DEFAULT_API_BASES = {
    "openai": "https://api.openai.com/v1",
    "baseten": "https://bridge.baseten.co/v1/direct",
    "together": "https://api.together.xyz/v1",
    "anyscale": "https://api.endpoints.anyscale.com/v1",
}


@dataclass
class EvaluationContext:
    """Context object to hold evaluation state."""

    completion_client: OpenAI
    judge_client: OpenAI
    request: EvaluationRequest
    samples: list[dict]
    guidelines: list[Guideline]
    trace: Trace | None = None
    scores_per_guideline: dict[str, list[int | None]] = field(default_factory=dict)
    failed_per_guideline: dict[str, int] = field(default_factory=dict)


class EvaluationService:
    """Service for running evaluations."""

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.repository = EvaluationRepository(session)
        self.guideline_service = GuidelineService(session)
        self.s3 = S3Storage()

    # ==================== Main Entry Point ====================

    async def run_evaluation(self, request: EvaluationRequest) -> EvaluationResponse:
        """Run an evaluation on a dataset with given guidelines using lighteval."""
        # Setup phase
        dataset_content = self._load_dataset_content(request.dataset_name)
        guidelines = await self._load_guidelines(request.guideline_names)

        # Initialize trace in database
        trace = await self._create_trace(request)

        try:
            # Run lighteval pipeline
            results = await self._run_lighteval_pipeline(
                request, dataset_content, guidelines
            )

            # Write results to database
            await self._write_lighteval_results(trace, request, results, guidelines)

            # Finalize
            summary = self._extract_summary(results, guidelines)
            trace = await self.repository.update_trace_status(
                trace.id, "completed", {"scores": summary}
            )

            # Upload trace to S3
            await self._upload_trace_jsonl_simple(trace)

            return self._build_response_from_summary(
                trace, request, len(results["samples"]), summary
            )

        except Exception as e:
            logger.error("Evaluation failed: %s", e)
            await self.repository.update_trace_status(
                trace.id, "failed", {"error": str(e)}
            )
            raise

    # ==================== Lighteval Integration ====================

    def _load_dataset_content(self, dataset_name: str) -> str:
        """Load dataset content from S3."""
        return self.s3.download_dataset(dataset_name)

    async def _create_trace(self, request: EvaluationRequest) -> Trace:
        """Create initial trace in database."""
        return await self.repository.create_trace(
            user_id=self.user_id,
            dataset_name=request.dataset_name,
            guideline_names=request.guideline_names,
            completion_model=request.completion_model,
            model_provider=request.model_provider,
            judge_model=request.judge_model,
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

    async def _run_lighteval_pipeline(
        self,
        request: EvaluationRequest,
        dataset_content: str,
        guidelines: list[Guideline],
    ) -> dict:
        """Run evaluation using lighteval pipeline."""
        # Get API key for judge model
        judge_api_key = self.s3.download_api_key(
            self.user_id, request.judge_model_provider
        )
        judge_url = request.judge_api_base or DEFAULT_API_BASES.get(
            request.judge_model_provider, DEFAULT_API_BASES["openai"]
        )

        # Create judge metrics from guidelines
        metrics = []
        for guideline in guidelines:
            guideline_dict = self._convert_guideline_to_dict(guideline)
            metric = GuidelineJudgeMetric(
                guideline=guideline_dict,
                model=request.judge_model,
                url=judge_url,
                api_key=judge_api_key,
            )
            metrics.append(metric)

        # Create DatasetTask
        dataset_task = DatasetTask(
            dataset_name=request.dataset_name,
            dataset_content=dataset_content,
            metrics=metrics,
        )
        task = dataset_task.build_lighteval_task()

        # Create registry for proper cache hashing
        registry = Registry(tasks=None)
        registry._task_registry[request.dataset_name] = task.config
        registry.task_to_configs = {request.dataset_name: [task.config]}

        # Create model client
        model_api_key = self.s3.download_api_key(self.user_id, request.model_provider)
        model_url = request.api_base or DEFAULT_API_BASES.get(
            request.model_provider, DEFAULT_API_BASES["openai"]
        )

        model_config = LiteLLMModelConfig(
            model_name=request.completion_model,
            base_url=model_url,
            api_key=model_api_key,
        )
        model = LiteLLMClient(model_config)

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
        pipeline = EvaluationPipeline(
            task=task,
            evaluation_tracker=evaluation_tracker,
            model=model,
            params=EvaluationPipelineParameters(
                max_samples=None, save_details=True, use_cache=True
            ),
        )

        results = pipeline.evaluate()
        pipeline.save_and_push_results()

        # Cleanup
        dataset_task.cleanup()

        return results

    async def _write_lighteval_results(
        self,
        trace: Trace,
        request: EvaluationRequest,
        results: dict,
        guidelines: list[Guideline],
    ) -> None:
        """Write lighteval results to database as events."""
        # Create spec event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="spec",
            data={
                "dataset_name": request.dataset_name,
                "guideline_names": request.guideline_names,
                "completion_model": request.completion_model,
                "model_provider": request.model_provider,
                "judge_model": request.judge_model,
                "sample_count": len(results["samples"]),
            },
        )

        # Write sample-level results
        for idx, sample_result in enumerate(results["samples"]):
            sample_id = str(idx)

            # Extract completion from the result (stored in judge prompts)
            completion = None
            for guideline in guidelines:
                prompt_key = f"user_prompt_judge_{guideline.name}"
                if prompt_key in sample_result:
                    # Parse completion from judge prompt
                    prompt_text = sample_result[prompt_key]
                    if "The response is:" in prompt_text:
                        completion = (
                            prompt_text.split("The response is:")[1]
                            .split("\n")[0]
                            .strip()
                        )
                        break

            # Log sampling event (if we found completion)
            if completion:
                await self.repository.create_event(
                    trace_id=trace.id,
                    event_type="sampling",
                    sample_id=sample_id,
                    data={
                        "completion": completion,
                        "model": request.completion_model,
                    },
                )

            # Log judge events
            for guideline in guidelines:
                guideline_name = guideline.name
                score = sample_result.get(guideline_name)
                judge_key = f"judgement_judge_{guideline_name}"
                prompt_key = f"user_prompt_judge_{guideline_name}"

                event_data = {}
                if prompt_key in sample_result:
                    event_data["prompt"] = sample_result[prompt_key]
                if judge_key in sample_result:
                    event_data["response"] = str(sample_result[judge_key])
                if score is not None:
                    event_data["score"] = score

                await self.repository.create_event(
                    trace_id=trace.id,
                    event_type="judge",
                    sample_id=sample_id,
                    guideline_name=guideline_name,
                    data=event_data,
                )

        # Create report event
        await self.repository.create_event(
            trace_id=trace.id,
            event_type="report",
            data={"scores": results["summary"]},
        )

    def _extract_summary(self, results: dict, guidelines: list[Guideline]) -> dict:
        """Extract summary statistics from lighteval results."""
        summary = {}

        for guideline in guidelines:
            metric_name = guideline.name
            scores = [
                s.get(metric_name)
                for s in results["samples"]
                if s.get(metric_name) is not None
            ]
            failed_count = len(results["samples"]) - len(scores)

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
                # Numeric/Percentage: mean, std, min, max, percentiles
                if scores:
                    import statistics

                    sorted_scores = sorted(scores)
                    mean = statistics.mean(scores)
                    std = statistics.stdev(scores) if len(scores) > 1 else 0.0
                    min_score = min(scores)
                    max_score = max(scores)

                    # Calculate percentiles
                    def percentile(data, p):
                        n = len(data)
                        pos = (n - 1) * p
                        lower = int(pos)
                        upper = lower + 1
                        weight = pos - lower
                        if upper >= n:
                            return data[-1]
                        return data[lower] * (1 - weight) + data[upper] * weight

                    p25 = percentile(sorted_scores, 0.25)
                    p50 = percentile(sorted_scores, 0.50)
                    p75 = percentile(sorted_scores, 0.75)

                    summary[metric_name] = {
                        "type": "numeric",
                        "mean": round(mean, 2),
                        "std": round(std, 2),
                        "min": round(min_score, 2),
                        "max": round(max_score, 2),
                        "p25": round(p25, 2),
                        "p50": round(p50, 2),
                        "p75": round(p75, 2),
                        "failed": failed_count,
                    }
                else:
                    summary[metric_name] = {
                        "type": "numeric",
                        "mean": 0.0,
                        "std": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                        "p25": 0.0,
                        "p50": 0.0,
                        "p75": 0.0,
                        "failed": failed_count,
                    }

        return summary

    def _build_response_from_summary(
        self, trace: Trace, request: EvaluationRequest, sample_count: int, summary: dict
    ) -> EvaluationResponse:
        """Build evaluation response from summary."""
        scores = {}
        for name in request.guideline_names:
            summary_data = summary[name]
            if summary_data["type"] == "categorical":
                scores[name] = CategoricalScoreDistribution(
                    distribution=summary_data["distribution"],
                    mode=summary_data["mode"],
                    failed=summary_data["failed"],
                )
            else:  # numeric
                scores[name] = NumericScoreDistribution(
                    mean=summary_data["mean"],
                    std=summary_data["std"],
                    min=summary_data["min"],
                    max=summary_data["max"],
                    p25=summary_data["p25"],
                    p50=summary_data["p50"],
                    p75=summary_data["p75"],
                    failed=summary_data["failed"],
                )

        return EvaluationResponse(
            trace_id=trace.id,
            status=trace.status,
            dataset_name=request.dataset_name,
            sample_count=sample_count,
            guideline_names=request.guideline_names,
            completion_model=request.completion_model,
            model_provider=request.model_provider,
            judge_model=request.judge_model,
            scores=scores,
            created_at=trace.created_at,
        )

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

    # ==================== Old Setup Phase (kept for reference) ====================

    async def _setup_evaluation(self, request: EvaluationRequest) -> EvaluationContext:
        """Set up evaluation context with clients, data, and guidelines."""
        completion_client = self._create_client(
            request.model_provider, request.api_base
        )
        judge_client = self._create_client(
            request.judge_model_provider, request.judge_api_base
        )

        samples = self._load_dataset(request.dataset_name)
        guidelines = await self._load_guidelines(request.guideline_names)

        return EvaluationContext(
            completion_client=completion_client,
            judge_client=judge_client,
            request=request,
            samples=samples,
            guidelines=guidelines,
            scores_per_guideline={g.name: [] for g in guidelines},
            failed_per_guideline={g.name: 0 for g in guidelines},
        )

    def _create_client(self, provider: str, api_base: str | None) -> OpenAI:
        """Create OpenAI client with user's API key for a given provider."""
        try:
            api_key = self.s3.download_api_key(self.user_id, provider)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No API key found for provider: {provider}",
            )

        base_url = api_base or DEFAULT_API_BASES.get(
            provider, DEFAULT_API_BASES["openai"]
        )

        return OpenAI(api_key=api_key, base_url=base_url)

    def _load_dataset(self, dataset_name: str) -> list[dict]:
        """Load and parse dataset from S3."""
        content = self.s3.download_dataset(dataset_name)
        return self._parse_jsonl(content)

    async def _load_guidelines(self, guideline_names: list[str]) -> list[Guideline]:
        """Load guidelines from database."""
        guidelines = []
        for name in guideline_names:
            guideline = await self.guideline_service.get_guideline_by_name(name)
            guidelines.append(guideline)
        return guidelines

    # ==================== Trace Initialization ====================

    async def _initialize_trace(self, ctx: EvaluationContext) -> None:
        """Create trace and spec event in database."""
        ctx.trace = await self.repository.create_trace(
            user_id=self.user_id,
            dataset_name=ctx.request.dataset_name,
            guideline_names=ctx.request.guideline_names,
            completion_model=ctx.request.completion_model,
            model_provider=ctx.request.model_provider,
            judge_model=ctx.request.judge_model,
        )

        await self.repository.create_event(
            trace_id=ctx.trace.id,
            event_type="spec",
            data={
                "dataset_name": ctx.request.dataset_name,
                "guideline_names": ctx.request.guideline_names,
                "completion_model": ctx.request.completion_model,
                "model_provider": ctx.request.model_provider,
                "judge_model": ctx.request.judge_model,
                "sample_count": len(ctx.samples),
            },
        )

    # ==================== Sample Processing ====================

    async def _process_all_samples(self, ctx: EvaluationContext) -> None:
        """Process all samples in parallel using a threadpool."""
        loop = asyncio.get_event_loop()

        # Extract guideline data for thread-safe access (ORM objects aren't thread-safe)
        guidelines_data = [
            {
                "name": g.name,
                "prompt": g.prompt,
                "scoring_scale": g.scoring_scale,
                "scoring_scale_config": g.scoring_scale_config,
            }
            for g in ctx.guidelines
        ]

        # Process samples in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = [
                loop.run_in_executor(
                    executor,
                    self._process_single_sample_sync,
                    ctx.completion_client,
                    ctx.judge_client,
                    ctx.request.completion_model,
                    ctx.request.judge_model,
                    guidelines_data,
                    str(idx),
                    sample,
                )
                for idx, sample in enumerate(ctx.samples)
            ]

            results = await asyncio.gather(*tasks)

        # Write all results to database (must be done in async context)
        await self._write_sample_results(ctx, results)

    def _process_single_sample_sync(
        self,
        completion_client: OpenAI,
        judge_client: OpenAI,
        completion_model: str,
        judge_model: str,
        guidelines_data: list[dict],
        sample_id: str,
        sample: dict,
    ) -> dict:
        """Process a single sample synchronously (runs in threadpool).

        Returns a dict with all data needed for DB writes.
        """
        input_text = sample.get("input", "")
        result = {
            "sample_id": sample_id,
            "input_text": input_text,
            "completion": None,
            "judge_results": [],
            "error": None,
        }

        try:
            # Generate completion
            completion = self._generate_completion(
                completion_client, completion_model, input_text
            )
            result["completion"] = completion

            # Judge with each guideline
            for guideline in guidelines_data:
                score, judge_response, error = self._judge_completion(
                    judge_client,
                    judge_model,
                    guideline["prompt"],
                    guideline["scoring_scale"],
                    guideline["scoring_scale_config"],
                    completion,
                )

                result["judge_results"].append(
                    {
                        "guideline_name": guideline["name"],
                        "score": score,
                        "judge_response": judge_response,
                        "error": error,
                        "prompt": self._build_judge_prompt(
                            guideline["prompt"],
                            guideline["scoring_scale"],
                            guideline["scoring_scale_config"],
                            completion,
                        ),
                    }
                )

        except Exception as e:
            logger.error("Error processing sample %s: %s", sample_id, e)
            result["error"] = str(e)

        return result

    async def _write_sample_results(
        self, ctx: EvaluationContext, results: list[dict]
    ) -> None:
        """Write all sample results to the database and update context scores."""
        for result in results:
            sample_id = result["sample_id"]

            if result["error"]:
                # Sample-level error (e.g., completion failed)
                await self.repository.create_event(
                    trace_id=ctx.trace.id,
                    event_type="error",
                    sample_id=sample_id,
                    data={"error": result["error"]},
                )
                continue

            # Log sampling event
            await self.repository.create_event(
                trace_id=ctx.trace.id,
                event_type="sampling",
                sample_id=sample_id,
                data={
                    "input": result["input_text"],
                    "completion": result["completion"],
                    "model": ctx.request.completion_model,
                },
            )

            # Log judge events and update scores
            for judge_result in result["judge_results"]:
                guideline_name = judge_result["guideline_name"]

                event_data = {
                    "prompt": judge_result["prompt"],
                    "response": judge_result["judge_response"],
                }

                if judge_result["error"]:
                    event_data["error"] = judge_result["error"]
                    ctx.failed_per_guideline[guideline_name] += 1
                    ctx.scores_per_guideline[guideline_name].append(None)
                else:
                    event_data["score"] = judge_result["score"]
                    ctx.scores_per_guideline[guideline_name].append(
                        judge_result["score"]
                    )

                await self.repository.create_event(
                    trace_id=ctx.trace.id,
                    event_type="judge",
                    sample_id=sample_id,
                    guideline_name=guideline_name,
                    data=event_data,
                )

    # ==================== Finalization ====================

    async def _finalize_evaluation(self, ctx: EvaluationContext) -> EvaluationResponse:
        """Finalize evaluation: calculate summary, update trace, upload to S3."""
        summary = self._calculate_summary(
            ctx.scores_per_guideline, ctx.failed_per_guideline, ctx.guidelines
        )

        # Create report event
        await self.repository.create_event(
            trace_id=ctx.trace.id,
            event_type="report",
            data={"scores": summary},
        )

        # Update trace with summary
        ctx.trace = await self.repository.update_trace_status(
            ctx.trace.id, "completed", {"scores": summary}
        )

        # Upload trace to S3
        await self._upload_trace_jsonl(ctx)

        return self._build_response(ctx, summary)

    def _build_response(
        self, ctx: EvaluationContext, summary: dict
    ) -> EvaluationResponse:
        """Build the evaluation response object."""
        scores = {}
        for name in ctx.request.guideline_names:
            summary_data = summary[name]
            if summary_data["type"] == "categorical":
                scores[name] = CategoricalScoreDistribution(
                    distribution=summary_data["distribution"],
                    mode=summary_data["mode"],
                    failed=summary_data["failed"],
                )
            else:  # numeric
                scores[name] = NumericScoreDistribution(
                    mean=summary_data["mean"],
                    std=summary_data["std"],
                    min=summary_data["min"],
                    max=summary_data["max"],
                    p25=summary_data["p25"],
                    p50=summary_data["p50"],
                    p75=summary_data["p75"],
                    failed=summary_data["failed"],
                )

        return EvaluationResponse(
            trace_id=ctx.trace.id,
            status=ctx.trace.status,
            dataset_name=ctx.request.dataset_name,
            sample_count=len(ctx.samples),
            guideline_names=ctx.request.guideline_names,
            completion_model=ctx.request.completion_model,
            model_provider=ctx.request.model_provider,
            judge_model=ctx.request.judge_model,
            scores=scores,
            created_at=ctx.trace.created_at,
        )

    # ==================== LLM Operations ====================

    def _generate_completion(self, client: OpenAI, model: str, input_text: str) -> str:
        """Generate a completion for the given input."""
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": input_text}],
        )
        return response.choices[0].message.content

    def _judge_completion(
        self,
        client: OpenAI,
        judge_model: str,
        guideline_prompt: str,
        scoring_scale: str,
        scoring_scale_config: dict,
        completion: str,
    ) -> tuple[int | None, str, str | None]:
        """Judge a completion using the guideline.

        Returns:
            tuple: (score, response, error) - score is None if parsing failed
        """
        prompt = self._build_judge_prompt(
            guideline_prompt, scoring_scale, scoring_scale_config, completion
        )

        response = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.choices[0].message.content

        score, error = self._parse_score(
            response_text, scoring_scale, scoring_scale_config
        )
        return score, response_text, error

    def _build_judge_prompt(
        self,
        guideline_prompt: str,
        scoring_scale: str,
        scoring_scale_config: dict,
        completion: str,
    ) -> str:
        """Build the full judge prompt with completion and scoring instructions."""
        prompt = guideline_prompt.replace("{completion}", completion)

        if scoring_scale == "boolean":
            choices = '"0" or "1"'
        elif scoring_scale == "numeric":
            min_val = scoring_scale_config.get("min_value", 0)
            max_val = scoring_scale_config.get("max_value", 10)
            choices = " or ".join([f'"{i}"' for i in range(min_val, max_val + 1)])
        elif scoring_scale == "percentage":
            choices = "a number from 0 to 100"
        elif scoring_scale == "custom_category":
            categories = scoring_scale_config.get("categories", [])
            choices = " or ".join([f'"{i}"' for i in range(len(categories))])
        else:
            choices = '"1"'

        prompt += f"""

First, write out in a step by step manner your reasoning to be sure that your conclusion is correct. Avoid simply stating the correct answer at the outset. Then print only a single choice from {choices} (without quotes or punctuation) on its own line corresponding to the correct answer. At the end, repeat just the answer by itself on a new line.

Reasoning:"""

        return prompt

    # ==================== Utility Methods ====================

    def _parse_jsonl(self, content: str) -> list[dict]:
        """Parse JSONL content into a list of dicts."""
        samples = []
        for line in content.strip().split("\n"):
            if line.strip():
                samples.append(json.loads(line))
        return samples

    def _parse_score(
        self, response: str, scoring_scale: str, scoring_scale_config: dict
    ) -> tuple[int | None, str | None]:
        """Parse the score from the last line of the judge's response."""
        last_line = response.strip().split("\n")[-1].strip()

        try:
            score = int(last_line)
        except ValueError:
            return None, f"Last line is not an integer: '{last_line}'"

        # Validate score based on scoring scale
        if scoring_scale == "boolean":
            if score in [0, 1]:
                return score, None
            return None, f"Score {score} out of range (0-1)"
        elif scoring_scale == "numeric":
            min_val = scoring_scale_config.get("min_value", 0)
            max_val = scoring_scale_config.get("max_value", 10)
            if min_val <= score <= max_val:
                return score, None
            return None, f"Score {score} out of range ({min_val}-{max_val})"
        elif scoring_scale == "percentage":
            if 0 <= score <= 100:
                return score, None
            return None, f"Score {score} out of range (0-100)"
        elif scoring_scale == "custom_category":
            categories = scoring_scale_config.get("categories", [])
            if 0 <= score < len(categories):
                return score, None
            return None, f"Score {score} out of range (0-{len(categories)-1})"

        return None, f"Unknown scoring scale: {scoring_scale}"

    def _calculate_summary(
        self,
        scores_per_guideline: dict[str, list[int | None]],
        failed_per_guideline: dict[str, int],
        guidelines: list[Guideline],
    ) -> dict:
        """Calculate summary statistics for each guideline."""
        summary = {}

        for guideline in guidelines:
            name = guideline.name
            valid_scores = [s for s in scores_per_guideline[name] if s is not None]
            failed_count = failed_per_guideline[name]

            # Calculate statistics based on scoring scale
            if guideline.scoring_scale in [
                GuidelineScoringScale.BOOLEAN,
                GuidelineScoringScale.CUSTOM_CATEGORY,
            ]:
                # Categorical: distribution + mode
                distribution: dict[str, int] = {}
                for score in valid_scores:
                    key = str(score)
                    distribution[key] = distribution.get(key, 0) + 1

                mode = None
                if distribution:
                    mode = max(distribution, key=distribution.get)

                summary[name] = {
                    "type": "categorical",
                    "distribution": distribution,
                    "mode": mode,
                    "failed": failed_count,
                }
            else:
                # Numeric/Percentage: mean, std, min, max, percentiles
                if valid_scores:
                    import statistics

                    sorted_scores = sorted(valid_scores)
                    mean = statistics.mean(valid_scores)
                    std = (
                        statistics.stdev(valid_scores) if len(valid_scores) > 1 else 0.0
                    )
                    min_score = min(valid_scores)
                    max_score = max(valid_scores)

                    # Calculate percentiles
                    def percentile(data, p):
                        n = len(data)
                        pos = (n - 1) * p
                        lower = int(pos)
                        upper = lower + 1
                        weight = pos - lower
                        if upper >= n:
                            return data[-1]
                        return data[lower] * (1 - weight) + data[upper] * weight

                    p25 = percentile(sorted_scores, 0.25)
                    p50 = percentile(sorted_scores, 0.50)
                    p75 = percentile(sorted_scores, 0.75)

                    summary[name] = {
                        "type": "numeric",
                        "mean": round(mean, 2),
                        "std": round(std, 2),
                        "min": round(min_score, 2),
                        "max": round(max_score, 2),
                        "p25": round(p25, 2),
                        "p50": round(p50, 2),
                        "p75": round(p75, 2),
                        "failed": failed_count,
                    }
                else:
                    summary[name] = {
                        "type": "numeric",
                        "mean": 0.0,
                        "std": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                        "p25": 0.0,
                        "p50": 0.0,
                        "p75": 0.0,
                        "failed": failed_count,
                    }

        return summary

    async def _upload_trace_jsonl(self, ctx: EvaluationContext) -> None:
        """Upload trace events as JSONL to S3."""
        events = await self.repository.get_events_by_trace(ctx.trace.id)

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
        # Sanitize model name to avoid creating nested S3 "folders" (slashes become dashes)
        safe_model_name = ctx.request.completion_model.replace("/", "-")
        filename = f"{ctx.trace.id}_{safe_model_name}-{ctx.request.dataset_name}"
        self.s3.upload_trace(filename, content)

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
