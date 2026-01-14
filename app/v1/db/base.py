from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Mixin class providing created_at and updated_at timestamp columns."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )



class BaseModel(Base, TimestampMixin):
    """
    Base model class with common columns.
    
    All models should inherit from this class to get:
    - id: Primary key
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    - deleted_at: Timestamp when record was soft-deleted (nullable)
    """
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
