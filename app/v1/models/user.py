"""
User model and UserRole enumeration.

This module implements Task 2.1 from the project epic:
- UserRole IntEnum with permission levels and can_manage() method
- User model with all fields, relationships, and business logic

The role hierarchy follows: SUPERADMIN (3) > ADMIN (2) > USER (1)
Higher roles can manage (create, update, delete) users with lower roles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.db.base import BaseModel

if TYPE_CHECKING:
    from app.v1.models.user_role_history import UserRoleHistory


class UserRole(IntEnum):
    """
    User role enumeration with permission hierarchy.
    
    Permission levels determine what actions a user can perform:
    - USER (1): Standard user, can only manage own resources
    - ADMIN (2): Can manage regular users and their resources
    - SUPERADMIN (3): Full system access, can manage everyone
    
    The numeric values enable natural comparison for hierarchy checks:
        SUPERADMIN > ADMIN > USER
    
    Example:
        >>> UserRole.ADMIN.can_manage(UserRole.USER)
        True
        >>> UserRole.USER.can_manage(UserRole.ADMIN)
        False
    """
    
    USER = 1
    ADMIN = 2
    SUPERADMIN = 3
    
    def can_manage(self, other: UserRole) -> bool:
        """
        Check if this role can manage another role.
        
        A role can manage another role only if it has a strictly higher
        permission level. Same-level roles cannot manage each other.
        
        Args:
            other: The role to check management permission against.
            
        Returns:
            True if this role can manage the other role, False otherwise.
            
        Example:
            >>> UserRole.SUPERADMIN.can_manage(UserRole.ADMIN)
            True
            >>> UserRole.ADMIN.can_manage(UserRole.ADMIN)
            False
        """
        return self.value > other.value
    
    @property
    def display_name(self) -> str:
        """Human-readable role name."""
        return self.name.lower()


class User(BaseModel):
    """
    User model representing system users.
    
    Inherits from BaseModel which provides:
    - id: Auto-increment primary key
    - created_at: Creation timestamp
    - updated_at: Last modification timestamp
    - deleted_at: Soft delete timestamp (None = active)
    - deleted_by_id: FK to user who performed deletion
    
    Self-referential Relationships:
    - created_by: User who created this account (None for self-registered)
    - deleted_by: User who soft-deleted this account
    - users_created: Users created by this user
    
    Related Collections:
    - role_changes: History of role changes for this user
    - todos: Todo items owned by this user (defined in Todo model)
    """
    
    __tablename__ = "users"
    
    # ==================== Core Fields ====================
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User's email address, used for authentication",
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt-hashed password (never store plain text)",
    )
    
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="User's full display name",
    )
    
    role: Mapped[UserRole] = mapped_column(
        default=UserRole.USER,
        nullable=False,
        doc="User's permission role (USER, ADMIN, SUPERADMIN)",
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active (can login)",
    )
    
    # ==================== Self-Referential FKs ====================
    
    created_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        doc="FK to user who created this account (None for self-registered/superadmin)",
    )
    
    # Note: deleted_by_id is inherited from TimestampMixin via BaseModel
    
    # ==================== Relationships ====================
    
    # Self-referential: who created this user
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[created_by_id],
        back_populates="users_created",
        doc="The user who created this account",
    )
    
    # Self-referential: users created by this user
    users_created: Mapped[List["User"]] = relationship(
        "User",
        back_populates="created_by",
        foreign_keys=[created_by_id],
        doc="Users created by this user",
    )
    
    # Self-referential: who deleted this user (via TimestampMixin.deleted_by_id)
    deleted_by: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys="User.deleted_by_id",
        post_update=True,  # Avoid circular dependency issues
        doc="The user who soft-deleted this account",
    )
    
    # Role change history for this user
    role_changes: Mapped[List["UserRoleHistory"]] = relationship(
        "UserRoleHistory",
        back_populates="user",
        foreign_keys="UserRoleHistory.user_id",
        order_by="desc(UserRoleHistory.changed_at)",
        doc="History of role changes for this user",
    )
    
    # ==================== Table Configuration ====================
    
    __table_args__ = (
        # Composite index for common query patterns
        Index("ix_users_role_is_active", "role", "is_active"),
        Index("ix_users_email_is_active", "email", "is_active"),
    )
    
    # ==================== Computed Properties ====================
    
    @property
    def is_admin(self) -> bool:
        """
        Check if user has admin privileges (ADMIN or SUPERADMIN).
        
        Returns:
            True if user role is ADMIN or higher.
        """
        return self.role >= UserRole.ADMIN
    
    @property
    def is_superadmin(self) -> bool:
        """
        Check if user is a superadmin.
        
        Returns:
            True if user role is SUPERADMIN.
        """
        return self.role == UserRole.SUPERADMIN
    
    @property
    def is_deleted(self) -> bool:
        """
        Check if user has been soft-deleted.
        
        Returns:
            True if deleted_at is set.
        """
        return self.deleted_at is not None
    
    @property
    def todo_count(self) -> int:
        """
        Get count of user's todos.
        
        Note: This requires the todos relationship to be loaded.
        For performance, prefer using a repository method with COUNT query.
        
        Returns:
            Number of todos owned by this user.
        """
        # This will be populated when Todo model is implemented
        # For now, return 0 as a placeholder
        if hasattr(self, "todos"):
            return len(self.todos)
        return 0
    
    # ==================== Instance Methods ====================
    
    def can_manage(self, other_user: User) -> bool:
        """
        Check if this user can manage another user.
        
        Management includes: update profile, change role, deactivate, delete.
        
        Rules:
        1. Cannot manage yourself (prevents self-demotion/deletion)
        2. Must have strictly higher permission level
        
        Args:
            other_user: The user to check management permission against.
            
        Returns:
            True if this user can manage the other user.
            
        Example:
            >>> superadmin.can_manage(admin)
            True
            >>> admin.can_manage(admin)  # Same level
            False
            >>> admin.can_manage(superadmin)  # Lower level
            False
        """
        # Rule 1: Cannot manage yourself
        if self.id == other_user.id:
            return False
        
        # Rule 2: Must have higher permission level
        return self.role.can_manage(other_user.role)
    
    def soft_delete(self, deleted_by: User) -> None:
        """
        Soft delete this user.
        
        Sets deleted_at timestamp and records who performed the deletion.
        The user will be excluded from normal queries but remains in database.
        
        Args:
            deleted_by: The user performing the deletion (for audit trail).
            
        Raises:
            ValueError: If deleted_by cannot manage this user.
            
        Note:
            This method only sets fields. Caller must commit the session.
        """
        if not deleted_by.can_manage(self):
            raise ValueError(
                f"User {deleted_by.email} (role={deleted_by.role.name}) "
                f"cannot delete user {self.email} (role={self.role.name})"
            )
        
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by_id = deleted_by.id
        self.is_active = False  # Also deactivate the account
    
    def restore(self) -> None:
        """
        Restore a soft-deleted user.
        
        Clears deleted_at and deleted_by_id, but does NOT automatically
        reactivate the account (is_active remains unchanged).
        
        Note:
            This method only sets fields. Caller must commit the session.
        """
        self.deleted_at = None
        self.deleted_by_id = None
    
    # ==================== Dunder Methods ====================
    
    def __repr__(self) -> str:
        """
        String representation for debugging.
        
        Returns:
            String with user id, email, and role.
        """
        status = "deleted" if self.is_deleted else ("active" if self.is_active else "inactive")
        return f"<User(id={self.id}, email='{self.email}', role={self.role.name}, status={status})>"
    
    def __str__(self) -> str:
        """
        Human-readable string representation.
        
        Returns:
            User's full name and email.
        """
        return f"{self.full_name} ({self.email})"
