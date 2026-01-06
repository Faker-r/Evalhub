from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    """Dataset response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    sample_count: int


class DatasetListResponse(BaseModel):
    """Response schema for listing datasets."""

    datasets: list[DatasetResponse]
