from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.leaderboard.repository import LeaderboardRepository
from api.leaderboard.schemas import (
    DatasetLeaderboard,
    LeaderboardEntry,
    LeaderboardResponse,
    MetricScore,
)

logger = get_logger(__name__)


class LeaderboardService:
    """Service for leaderboard operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = LeaderboardRepository(session)

    async def get_leaderboard(self) -> LeaderboardResponse:
        """Get leaderboard for all datasets, grouped by dataset."""
        traces = await self.repository.get_all_leaderboard_traces()

        traces_by_dataset: dict[str, list] = {}
        for trace in traces:
            if trace.dataset_name not in traces_by_dataset:
                traces_by_dataset[trace.dataset_name] = []
            traces_by_dataset[trace.dataset_name].append(trace)

        dataset_leaderboards: list[DatasetLeaderboard] = []
        for dataset_name, dataset_traces in traces_by_dataset.items():
            entries: list[LeaderboardEntry] = []
            for trace in dataset_traces:
                entry = self._build_entry(trace)
                if entry:
                    entries.append(entry)

            dataset = await self.repository.get_dataset_by_name(dataset_name)
            sample_count = dataset.sample_count if dataset else 0

            dataset_leaderboards.append(
                DatasetLeaderboard(
                    dataset_name=dataset_name,
                    sample_count=sample_count,
                    entries=entries,
                )
            )

        return LeaderboardResponse(datasets=dataset_leaderboards)

    def _build_entry(self, trace) -> LeaderboardEntry | None:
        """Build a leaderboard entry from a trace."""
        if not trace.summary or "scores" not in trace.summary:
            logger.warning(f"Trace {trace.id} has no summary scores, skipping")
            return None

        scores_data = trace.summary["scores"]
        metric_scores: list[MetricScore] = []
        total_failures = 0

        for metric_name, score_info in scores_data.items():
            mean = score_info.get("mean", 0.0)
            std = score_info.get("std", 0.0)
            failed = score_info.get("failed", 0)

            metric_scores.append(
                MetricScore(
                    metric_name=metric_name,
                    mean=round(mean, 4),
                    std=round(std, 4),
                    failed=failed,
                )
            )

            total_failures += failed

        if not metric_scores:
            logger.warning(f"Trace {trace.id} has no valid metric scores, skipping")
            return None

        return LeaderboardEntry(
            trace_id=trace.id,
            dataset_name=trace.dataset_name,
            completion_model=trace.completion_model,
            model_provider=trace.model_provider,
            judge_model=trace.judge_model,
            scores=metric_scores,
            total_failures=total_failures,
            created_at=trace.created_at,
        )
