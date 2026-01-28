"""Models and providers database models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from api.core.database import Base

# Many-to-many relationship table between models and providers
model_provider_association = Table(
    "model_provider_association",
    Base.metadata,
    Column("model_id", Integer, ForeignKey("models.id", ondelete="CASCADE"), primary_key=True),
    Column("provider_id", Integer, ForeignKey("providers.id", ondelete="CASCADE"), primary_key=True),
)


class Provider(Base):
    """Provider model for storing API provider information."""

    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    base_url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    models = relationship(
        "Model",
        secondary=model_provider_association,
        back_populates="providers",
    )


class Model(Base):
    """Model model for storing AI model information."""

    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    display_name = Column(String, nullable=False)
    developer = Column(String, nullable=False)
    api_name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    providers = relationship(
        "Provider",
        secondary=model_provider_association,
        back_populates="models",
    )
