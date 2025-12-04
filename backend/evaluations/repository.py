from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundException
from backend.core.logging import get_logger
from backend.evaluations.models import Trace, TraceEvent

logger = get_logger(__name__)


class EvaluationRepository:
    """Repository for handling evaluation database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Trace Methods ====================

    async def create_trace(
        self,
        user_id: int,
        dataset_name: str,
        guideline_names: list[str],
        completion_model: str,
        model_provider: str,
        judge_model: str,
    ) -> Trace:
        """Create a new trace for an evaluation run."""
        trace = Trace(
            user_id=user_id,
            dataset_name=dataset_name,
            guideline_names=guideline_names,
            completion_model=completion_model,
            model_provider=model_provider,
            judge_model=judge_model,
            status="running",
            created_at=datetime.utcnow(),
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)

        logger.info(f"Created trace: {trace.id}")
        return trace

    async def update_trace_status(
        self, trace_id: int, status: str, summary: Optional[dict] = None
    ) -> Trace:
        """Update trace status and optionally summary."""
        trace = await self.get_trace_by_id(trace_id)
        trace.status = status
        if summary is not None:
            trace.summary = summary
        await self.session.commit()
        await self.session.refresh(trace)

        logger.info(f"Updated trace {trace_id} status to {status}")
        return trace

    async def get_trace_by_id(self, trace_id: int) -> Trace:
        """Get trace by ID."""
        query = select(Trace).where(Trace.id == trace_id)
        result = await self.session.execute(query)
        trace = result.scalar_one_or_none()

        if not trace:
            raise NotFoundException(f"Trace not found: {trace_id}")

        return trace

    async def get_traces_by_user(self, user_id: int) -> list[Trace]:
        """Get all traces for a user."""
        query = select(Trace).where(Trace.user_id == user_id).order_by(Trace.id.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ==================== TraceEvent Methods ====================

    async def create_event(
        self,
        trace_id: int,
        event_type: str,
        data: dict,
        sample_id: Optional[str] = None,
        guideline_name: Optional[str] = None,
    ) -> TraceEvent:
        """Create a new trace event."""
        event = TraceEvent(
            trace_id=trace_id,
            event_type=event_type,
            sample_id=sample_id,
            guideline_name=guideline_name,
            data=data,
            created_at=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)

        return event

    async def get_events_by_trace(self, trace_id: int) -> list[TraceEvent]:
        """Get all events for a trace."""
        query = (
            select(TraceEvent)
            .where(TraceEvent.trace_id == trace_id)
            .order_by(TraceEvent.id.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

