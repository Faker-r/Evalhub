from sqlalchemy import Column, Integer, String, Text

from api.core.database import Base


class Guideline(Base):
    """Guideline model."""

    __tablename__ = "guidelines"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    prompt = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    max_score = Column(Integer, nullable=False)
