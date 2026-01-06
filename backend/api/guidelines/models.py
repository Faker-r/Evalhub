from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from api.core.database import Base


class Guideline(Base):
    """Guideline model."""

    __tablename__ = "guidelines"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    prompt = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    max_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
