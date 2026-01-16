"""
Database base classes and mixins.

This module provides the foundational SQLAlchemy classes used throughout the application:
- Base: The DeclarativeBase for all models
- TimestampMixin: Audit trail timestamps with soft delete support
- BaseModel: Abstract base combining Base + TimestampMixin + auto-increment id
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """
    Mixin class providing audit trail timestamp columns.
    
    Provides soft delete functionality with tracking of who performed the deletion.
    All models inheriting from BaseModel will have these fields available.
    
    Attributes:
        created_at: Timestamp when record was created (auto-set)
        updated_at: Timestamp when record was last modified (auto-updated)
        deleted_at: Timestamp when record was soft-deleted (None = active)
        deleted_by_id: FK to users.id indicating who performed the deletion
    """
    
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
        index=True,  # Index for efficient soft-delete filtering
    )

    # Note: deleted_by_id FK is defined here but references users.id
    # The relationship is defined in models that need it (e.g., User)
    @declared_attr
    def deleted_by_id(cls) -> Mapped[int | None]:
        """Foreign key to the user who performed the soft delete."""
        return mapped_column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            default=None,
        )



class BaseModel(Base, TimestampMixin):
    """
    Abstract base model class with common columns.
    
    All domain models should inherit from this class to get:
    - id: Auto-increment primary key
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    - deleted_at: Timestamp when record was soft-deleted (None = active)
    - deleted_by_id: FK to users.id indicating who deleted the record
    
    Example:
        class Todo(BaseModel):
            __tablename__ = "todos"
            title: Mapped[str] = mapped_column(String(200))
    """
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
