from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from api.core.database import Base


class Trace(Base):
    """Trace model - represents one evaluation run."""

    __tablename__ = "traces"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)  # Supabase UUID
    dataset_name = Column(String, nullable=False)
    guideline_names = Column(JSONB, nullable=False)  # ["humor_likert", "clarity"]
    completion_model_config = Column(JSONB, nullable=False)
    judge_model_config = Column(JSONB, nullable=False)
    status = Column(
        String, nullable=False, default="running"
    )  # running, completed, failed
    summary = Column(JSONB, nullable=True)  # Final scores summary
    count_on_leaderboard = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def completion_model(self) -> str:
        return (self.completion_model_config or {}).get("api_name", "")

    @property
    def model_provider(self) -> str:
        return (self.completion_model_config or {}).get("provider_slug", "")

    @property
    def judge_model(self) -> str:
        return (self.judge_model_config or {}).get("api_name", "")

    @property
    def judge_model_provider(self) -> str:
        return (self.judge_model_config or {}).get("provider_slug", "")


class TraceEvent(Base):
    """TraceEvent model - represents one event in an evaluation run."""

    __tablename__ = "trace_events"

    id = Column(Integer, primary_key=True)
    trace_id = Column(Integer, ForeignKey("traces.id"), nullable=False)
    event_type = Column(String, nullable=False)  # spec, sampling, judge, report, error
    sample_id = Column(String, nullable=True)  # null for spec/report events
    guideline_name = Column(String, nullable=True)  # null for sampling/spec events
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
