from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from api.leaderboard.repository import LeaderboardRepository
from api.leaderboard.schemas import (
    GuidelineScore,
    LeaderboardEntry,
    LeaderboardResponse,
)

logger = get_logger(__name__)


class LeaderboardService:
    """Service for leaderboard operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = LeaderboardRepository(session)

    async def get_leaderboard(self, dataset_name: str) -> LeaderboardResponse:
        """Get leaderboard for a dataset, ranked by normalized average scores."""
        # Get dataset info
        dataset = await self.repository.get_dataset_by_name(dataset_name)
        if not dataset:
            raise NotFoundException(f"Dataset not found: {dataset_name}")

        # Get all completed traces for this dataset
        traces = await self.repository.get_completed_traces_by_dataset(dataset_name)

        if not traces:
            return LeaderboardResponse(
                dataset_name=dataset_name,
                sample_count=dataset.sample_count,
                entries=[],
            )

        # Collect all unique guideline names across all traces
        all_guideline_names: set[str] = set()
        for trace in traces:
            if trace.guideline_names:
                all_guideline_names.update(trace.guideline_names)

        # Fetch guidelines
        guidelines = await self.repository.get_guidelines_by_names(
            list(all_guideline_names)
        )

        # Build leaderboard entries
        entries: list[LeaderboardEntry] = []
        for trace in traces:
            entry = self._build_entry(trace, guidelines)
            if entry:
                entries.append(entry)

        # Sort by normalized_avg_score descending
        entries.sort(key=lambda e: e.normalized_avg_score, reverse=True)

        return LeaderboardResponse(
            dataset_name=dataset_name,
            sample_count=dataset.sample_count,
            entries=entries,
        )

    def _build_entry(
        self, trace, guidelines: dict
    ) -> LeaderboardEntry | None:
        """Build a leaderboard entry from a trace."""
        if not trace.summary or "scores" not in trace.summary:
            logger.warning(f"Trace {trace.id} has no summary scores, skipping")
            return None

        scores_data = trace.summary["scores"]
        guideline_scores: list[GuidelineScore] = []
        total_failures = 0
        normalized_scores: list[float] = []

        for guideline_name in trace.guideline_names:
            if guideline_name not in scores_data:
                logger.warning(
                    f"Trace {trace.id} missing score for guideline {guideline_name}"
                )
                continue

            score_info = scores_data[guideline_name]
            mean = score_info.get("mean", 0.0)
            failed = score_info.get("failed", 0)

            # Get guideline from database
            guideline = guidelines.get(guideline_name)
            if not guideline:
                logger.warning(
                    f"Guideline {guideline_name} not found in database, skipping"
                )
                continue

            # Calculate max_score based on scoring scale
            max_score = self._get_max_score(guideline)
            normalized = mean / max_score if max_score > 0 else 0.0

            guideline_scores.append(
                GuidelineScore(
                    guideline_name=guideline_name,
                    mean=mean,
                    max_score=max_score,
                    normalized=round(normalized, 4),
                    failed=failed,
                )
            )

            total_failures += failed
            normalized_scores.append(normalized)

        if not normalized_scores:
            logger.warning(f"Trace {trace.id} has no valid guideline scores, skipping")
            return None

        # Calculate average of normalized scores
        normalized_avg = sum(normalized_scores) / len(normalized_scores)

        return LeaderboardEntry(
            trace_id=trace.id,
            completion_model=trace.completion_model,
            model_provider=trace.model_provider,
            judge_model=trace.judge_model,
            scores=guideline_scores,
            total_failures=total_failures,
            normalized_avg_score=round(normalized_avg, 4),
            created_at=trace.created_at,
        )

    def _get_max_score(self, guideline) -> int:
        """Get max score from guideline based on scoring scale."""
        if guideline.scoring_scale == "boolean":
            return 1
        elif guideline.scoring_scale == "numeric":
            return guideline.scoring_scale_config.get("max_value", 10)
        elif guideline.scoring_scale == "percentage":
            return 100
        elif guideline.scoring_scale == "custom_category":
            return len(guideline.scoring_scale_config.get("categories", [])) - 1 if guideline.scoring_scale_config.get("categories") else 1
        return 1
