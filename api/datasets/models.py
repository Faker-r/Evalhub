from sqlalchemy import Column, Integer, String

from api.core.database import Base


class Dataset(Base):
    """Dataset model."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    sample_count = Column(Integer, nullable=False)
