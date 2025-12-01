from pydantic import BaseModel, ConfigDict


class GuidelineBase(BaseModel):
    """Base guideline schema."""

    name: str
    prompt: str
    category: str
    max_score: int


class GuidelineCreate(GuidelineBase):
    """Guideline creation schema."""

    pass


class GuidelineResponse(GuidelineBase):
    """Guideline response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class GuidelineListResponse(BaseModel):
    """Response schema for listing guidelines."""

    guidelines: list[GuidelineResponse]
