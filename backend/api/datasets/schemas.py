from enum import Enum

from pydantic import BaseModel, ConfigDict


class DatasetVisibility(str, Enum):
    """Enum for dataset visibility."""

    PUBLIC = "public"
    PRIVATE = "private"


class DatasetResponse(BaseModel):
    """Dataset response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    sample_count: int
    visibility: DatasetVisibility
    user_id: str | None


class DatasetListResponse(BaseModel):
    """Response schema for listing datasets."""

    datasets: list[DatasetResponse]


class DatasetPreviewResponse(BaseModel):
    """Response schema for dataset preview."""

    samples: list[dict]
