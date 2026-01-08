from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from api.core.database import Base


class Benchmark(Base):
    """Benchmark model for storing lighteval task information."""

    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True)
    task_name = Column(String, unique=True, nullable=False)
    dataset_name = Column(String, nullable=False)
    hf_repo = Column(String, nullable=False)
    author = Column(String, nullable=True)
    downloads = Column(Integer, nullable=True)
    tags = Column(JSONB, nullable=True)
    estimated_input_tokens = Column(Integer, nullable=True)
    repo_type = Column(String, nullable=True)
    created_at_hf = Column(DateTime, nullable=True)
    private = Column(Boolean, nullable=True)
    gated = Column(Boolean, nullable=True)
    files = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
