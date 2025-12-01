from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from api.core.database import Base


class Trace(Base):
    """Trace model - represents one evaluation run."""

    __tablename__ = "traces"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_name = Column(String, nullable=False)
    guideline_names = Column(JSONB, nullable=False)  # ["humor_likert", "clarity"]
    completion_model = Column(String, nullable=False)
    model_provider = Column(String, nullable=False)
    judge_model = Column(String, nullable=False)
    status = Column(String, nullable=False, default="running")  # running, completed, failed
    summary = Column(JSONB, nullable=True)  # Final scores summary
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


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

