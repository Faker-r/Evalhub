import json
from dataclasses import dataclass, field

from fastapi import HTTPException, status
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.evaluations.models import Trace
from api.evaluations.repository import EvaluationRepository
from api.evaluations.schemas import EvaluationRequest, EvaluationResponse, ScoreDistribution
from api.guidelines.models import Guideline
from api.guidelines.service import GuidelineService

logger = get_logger(__name__)

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

    client: OpenAI
    request: EvaluationRequest
    samples: list[dict]
    guidelines: list[Guideline]
    trace: Trace | None = None
    scores_per_guideline: dict[str, list[int | None]] = field(default_factory=dict)
    failed_per_guideline: dict[str, int] = field(default_factory=dict)


class EvaluationService:
    """Service for running evaluations."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id
        self.repository = EvaluationRepository(session)
        self.guideline_service = GuidelineService(session)
        self.s3 = S3Storage()

    # ==================== Main Entry Point ====================

    async def run_evaluation(self, request: EvaluationRequest) -> EvaluationResponse:
        """Run an evaluation on a dataset with given guidelines."""
        # Setup phase
        ctx = await self._setup_evaluation(request)

        # Initialize trace in database
        await self._initialize_trace(ctx)

        # Process all samples
        await self._process_all_samples(ctx)

        # Finalize and build response
        return await self._finalize_evaluation(ctx)

    # ==================== Setup Phase ====================

    async def _setup_evaluation(self, request: EvaluationRequest) -> EvaluationContext:
        """Set up evaluation context with client, data, and guidelines."""
        client = self._create_client(request)
        samples = self._load_dataset(request.dataset_name)
        guidelines = await self._load_guidelines(request.guideline_names)

        return EvaluationContext(
            client=client,
            request=request,
            samples=samples,
            guidelines=guidelines,
            scores_per_guideline={g.name: [] for g in guidelines},
            failed_per_guideline={g.name: 0 for g in guidelines},
        )

    def _create_client(self, request: EvaluationRequest) -> OpenAI:
        """Create OpenAI client with user's API key."""
        try:
            api_key = self.s3.download_api_key(self.user_id, request.model_provider)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No API key found for provider: {request.model_provider}",
            )

        api_base = request.api_base or DEFAULT_API_BASES.get(
            request.model_provider, DEFAULT_API_BASES["openai"]
        )

        return OpenAI(api_key=api_key, base_url=api_base)

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
        """
        Process all samples in the dataset.
        #TODO: Change this to use threadpool rather than sequential. Way too slow this way
        """
        for idx, sample in enumerate(ctx.samples):
            await self._process_single_sample(ctx, str(idx), sample)

    async def _process_single_sample(
        self, ctx: EvaluationContext, sample_id: str, sample: dict
    ) -> None:
        """Process a single sample: generate completion and judge it."""
        input_text = sample.get("input", "")

        try:
            # Generate completion
            completion = self._generate_completion(
                ctx.client, ctx.request.completion_model, input_text
            )

            # Log sampling event
            await self._log_sampling_event(ctx, sample_id, input_text, completion)

            # Judge with each guideline
            for guideline in ctx.guidelines:
                await self._judge_and_log(ctx, sample_id, guideline, completion)

        except Exception as e:
            logger.error(f"Error processing sample {sample_id}: {e}")
            await self.repository.create_event(
                trace_id=ctx.trace.id,
                event_type="error",
                sample_id=sample_id,
                data={"error": str(e)},
            )

    async def _log_sampling_event(
        self, ctx: EvaluationContext, sample_id: str, input_text: str, completion: str
    ) -> None:
        """Log a sampling event to the trace."""
        await self.repository.create_event(
            trace_id=ctx.trace.id,
            event_type="sampling",
            sample_id=sample_id,
            data={
                "input": input_text,
                "completion": completion,
                "model": ctx.request.completion_model,
            },
        )

    async def _judge_and_log(
        self, ctx: EvaluationContext, sample_id: str, guideline: Guideline, completion: str
    ) -> None:
        """Judge a completion and log the result."""
        score, judge_response, error = self._judge_completion(
            ctx.client,
            ctx.request.judge_model,
            guideline.prompt,
            guideline.max_score,
            completion,
        )

        # Build event data
        event_data = {
            "prompt": self._build_judge_prompt(guideline.prompt, guideline.max_score, completion),
            "response": judge_response,
        }

        if error:
            event_data["error"] = error
            ctx.failed_per_guideline[guideline.name] += 1
            ctx.scores_per_guideline[guideline.name].append(None)
        else:
            event_data["score"] = score
            ctx.scores_per_guideline[guideline.name].append(score)

        await self.repository.create_event(
            trace_id=ctx.trace.id,
            event_type="judge",
            sample_id=sample_id,
            guideline_name=guideline.name,
            data=event_data,
        )

    # ==================== Finalization ====================

    async def _finalize_evaluation(self, ctx: EvaluationContext) -> EvaluationResponse:
        """Finalize evaluation: calculate summary, update trace, upload to S3."""
        summary = self._calculate_summary(ctx.scores_per_guideline, ctx.failed_per_guideline)

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
        await self._upload_trace_jsonl(ctx.trace.id)

        return self._build_response(ctx, summary)

    def _build_response(self, ctx: EvaluationContext, summary: dict) -> EvaluationResponse:
        """Build the evaluation response object."""
        return EvaluationResponse(
            trace_id=ctx.trace.id,
            status=ctx.trace.status,
            dataset_name=ctx.request.dataset_name,
            sample_count=len(ctx.samples),
            guideline_names=ctx.request.guideline_names,
            completion_model=ctx.request.completion_model,
            model_provider=ctx.request.model_provider,
            judge_model=ctx.request.judge_model,
            scores={
                name: ScoreDistribution(
                    mean=summary[name]["mean"],
                    distribution=summary[name]["distribution"],
                    failed=summary[name]["failed"],
                )
                for name in ctx.request.guideline_names
            },
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
        max_score: int,
        completion: str,
    ) -> tuple[int | None, str, str | None]:
        """Judge a completion using the guideline.

        Returns:
            tuple: (score, response, error) - score is None if parsing failed
        """
        prompt = self._build_judge_prompt(guideline_prompt, max_score, completion)

        response = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.choices[0].message.content

        score, error = self._parse_score(response_text, max_score)
        return score, response_text, error

    def _build_judge_prompt(self, guideline_prompt: str, max_score: int, completion: str) -> str:
        """Build the full judge prompt with completion and scoring instructions."""
        prompt = guideline_prompt.replace("{completion}", completion)
        choices = " or ".join([f'"{i}"' for i in range(1, max_score + 1)])

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

    def _parse_score(self, response: str, max_score: int) -> tuple[int | None, str | None]:
        """Parse the score from the last line of the judge's response."""
        last_line = response.strip().split("\n")[-1].strip()

        try:
            score = int(last_line)
        except ValueError:
            return None, f"Last line is not an integer: '{last_line}'"

        if 1 <= score <= max_score:
            return score, None
        else:
            return None, f"Score {score} out of range (1-{max_score})"

    def _calculate_summary(
        self,
        scores_per_guideline: dict[str, list[int | None]],
        failed_per_guideline: dict[str, int],
    ) -> dict:
        """Calculate summary statistics for each guideline."""
        summary = {}

        for name, scores in scores_per_guideline.items():
            valid_scores = [s for s in scores if s is not None]

            distribution: dict[str, int] = {}
            for score in valid_scores:
                key = str(score)
                distribution[key] = distribution.get(key, 0) + 1

            mean = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

            summary[name] = {
                "mean": round(mean, 2),
                "distribution": distribution,
                "failed": failed_per_guideline[name],
            }

        return summary

    async def _upload_trace_jsonl(self, trace_id: int) -> None:
        """Upload trace events as JSONL to S3."""
        events = await self.repository.get_events_by_trace(trace_id)

        lines = []
        for event in events:
            line_data = {
                "event_type": event.event_type,
                "trace_id": event.trace_id,
                "sample_id": event.sample_id,
                "guideline_name": event.guideline_name,
                "data": event.data,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            line_data = {k: v for k, v in line_data.items() if v is not None}
            lines.append(json.dumps(line_data))

        content = "\n".join(lines)
        self.s3.upload_trace(trace_id, content)

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
