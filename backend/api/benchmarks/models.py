from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from api.core.database import Base


class Benchmark(Base):
    """Benchmark model for storing lighteval task information."""

    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True)
    tasks = Column(JSONB, nullable=True)
    dataset_name = Column(String, nullable=False)
    hf_repo = Column(String, nullable=False)
    description = Column(String, nullable=True)
    author = Column(String, nullable=True)
    downloads = Column(Integer, nullable=True)
    tags = Column(JSONB, nullable=True)
    repo_type = Column(String, nullable=True)
    created_at_hf = Column(DateTime, nullable=True)
    private = Column(Boolean, nullable=True)
    gated = Column(Boolean, nullable=True)
    files = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship to tasks
    tasks_rel = relationship(
        "BenchmarkTask", back_populates="benchmark", cascade="all, delete-orphan"
    )


class BenchmarkTask(Base):
    """Task-level metadata for benchmarks (size, tokens per task variant)."""

    __tablename__ = "benchmark_tasks"

    id = Column(Integer, primary_key=True)
    benchmark_id = Column(
        Integer, ForeignKey("benchmarks.id", ondelete="CASCADE"), nullable=False
    )
    task_name = Column(String, nullable=False)  # e.g., "math:algebra", "gpqa:diamond"
    hf_subset = Column(String, nullable=True)  # HuggingFace subset/config used
    evaluation_splits = Column(
        JSONB, nullable=True
    )  # List of splits used for evaluation
    dataset_size = Column(Integer, nullable=True)  # Number of rows in evaluation splits
    estimated_input_tokens = Column(
        Integer, nullable=True
    )  # Total tokens for this task
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship back to benchmark
    benchmark = relationship("Benchmark", back_populates="tasks_rel")
