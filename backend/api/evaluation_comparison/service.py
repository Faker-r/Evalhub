"""Service for evaluation comparison: overlapping datasets and side-by-side reports."""

from collections import defaultdict
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.evaluation_comparison.schemas import (
    ModelProviderPair,
    OverlappingDatasetsResult,
    SideBySideReportEntry,
    SideBySideReportResult,
    SpecEvent,
)
from api.evaluations.models import Trace, TraceEvent


class EvaluationComparisonService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _fetch_overlapping_data(
        self,
        model_provider_pairs: list[tuple[str, str]],
    ) -> tuple[list[str], dict[str, dict[tuple[str, str], Trace]], dict[int, Any]]:
        """Return (overlapping_dataset_names, by_dataset_pair, spec_by_trace)."""
        if not model_provider_pairs:
            return [], {}, {}

        pair_filter = or_(
            and_(
                Trace.completion_model_config["api_name"].astext == m,
                Trace.completion_model_config["provider_slug"].astext == p,
            )
            for m, p in model_provider_pairs
        )
        ranked = select(
            Trace,
            func.row_number()
            .over(
                partition_by=[
                    Trace.dataset_name,
                    Trace.completion_model_config["api_name"].astext,
                    Trace.completion_model_config["provider_slug"].astext,
                ],
                order_by=Trace.created_at.desc(),
            )
            .label("rn"),
        ).where(
            Trace.status == "completed",
            Trace.summary.isnot(None),
            pair_filter,
        )
        ranked_subq = ranked.subquery()
        latest_subq = select(ranked_subq).where(ranked_subq.c.rn == 1).subquery()
        datasets_with_all = (
            select(latest_subq.c.dataset_name)
            .group_by(latest_subq.c.dataset_name)
            .having(func.count(latest_subq.c.id) == len(model_provider_pairs))
        )
        query = select(latest_subq).where(
            latest_subq.c.dataset_name.in_(datasets_with_all)
        )

        result = await self.session.execute(query)
        rows = result.all()
        trace_ids = [row.id for row in rows]
        if not trace_ids:
            return [], {}, {}

        traces_result = await self.session.execute(
            select(Trace).where(Trace.id.in_(trace_ids))
        )
        trace_map = {t.id: t for t in traces_result.scalars().all()}

        by_dataset_pair: dict[str, dict[tuple[str, str], Trace]] = defaultdict(dict)
        for row in rows:
            cfg = row.completion_model_config or {}
            key = (cfg.get("api_name", ""), cfg.get("provider_slug", ""))
            by_dataset_pair[row.dataset_name][key] = trace_map[row.id]
        overlapping_datasets = list(by_dataset_pair.keys())

        spec_by_trace: dict[int, Any] = {}
        spec_query = select(TraceEvent).where(
            TraceEvent.trace_id.in_(trace_ids),
            TraceEvent.event_type == "spec",
        )
        spec_result = await self.session.execute(spec_query)
        for ev in spec_result.scalars().all():
            spec_by_trace[ev.trace_id] = ev
        for tid in trace_ids:
            spec_by_trace.setdefault(tid, None)

        return overlapping_datasets, by_dataset_pair, spec_by_trace

    async def get_overlapping_datasets(
        self,
        model_provider_pairs: list[ModelProviderPair],
    ) -> OverlappingDatasetsResult:
        """Return the number and names of datasets that have completed traces for all given model-provider pairs."""
        pairs = [(p.model, p.provider) for p in model_provider_pairs]
        overlapping, _, _ = await self._fetch_overlapping_data(pairs)
        return OverlappingDatasetsResult(
            count=len(overlapping), dataset_names=overlapping
        )

    async def generate_side_by_side_report(
        self,
        model_provider_pairs: list[ModelProviderPair],
    ) -> SideBySideReportResult:
        """Return map of (model, provider, dataset, metric) -> (trace_id, created_at, score) for overlapping datasets."""
        pairs = [(p.model, p.provider) for p in model_provider_pairs]
        overlapping, by_dataset_pair, spec_by_trace = (
            await self._fetch_overlapping_data(pairs)
        )

        entries: list[SideBySideReportEntry] = []
        for dataset_name in overlapping:
            pairs_map = by_dataset_pair[dataset_name]
            for (model, provider), trace in pairs_map.items():
                summary = trace.summary or {}
                for metric_name, metric_data in (summary.get("scores") or {}).items():
                    entries.append(
                        SideBySideReportEntry(
                            model=model,
                            provider=provider,
                            dataset_name=dataset_name,
                            metric_name=metric_name,
                            trace_id=trace.id,
                            created_at=trace.created_at,
                            score=metric_data,
                        )
                    )
        spec_serialized = {
            tid: (SpecEvent.model_validate(ev) if ev is not None else None)
            for tid, ev in spec_by_trace.items()
        }
        return SideBySideReportResult(entries=entries, spec_by_trace=spec_serialized)
