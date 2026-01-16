"""
UserRoleHistory model for tracking role changes.

This module implements Task 2.2 from the project epic:
- Tracks who changed whose role
- Records previous and new role values
- Stores when the change occurred
- Optionally captures the reason for the change

This provides a complete audit trail for role modifications,
which is essential for security compliance and debugging.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.db.base import BaseModel
from app.v1.models.user import UserRole

if TYPE_CHECKING:
    from app.v1.models.user import User


class UserRoleHistory(BaseModel):
    """
    Audit log for user role changes.
    
    Every time a user's role is modified, a new record is created here.
    This provides a complete history of role changes for compliance and debugging.
    
    Inherits from BaseModel which provides:
    - id: Auto-increment primary key
    - created_at: When this record was created (same as changed_at)
    - updated_at: Last modification timestamp
    - deleted_at: Soft delete timestamp
    - deleted_by_id: FK to user who deleted this record
    
    Relationships:
    - user: The user whose role was changed
    - changed_by: The user who performed the change
    
    Example:
        When admin promotes user to admin:
        UserRoleHistory(
            user_id=5,
            old_role=UserRole.USER,
            new_role=UserRole.ADMIN,
            changed_by_id=1,  # admin's id
            reason="Promoted for team lead position"
        )
    """
    
    __tablename__ = "user_role_history"
    
    # ==================== Core Fields ====================
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="FK to the user whose role was changed",
    )
    
    old_role: Mapped[UserRole] = mapped_column(
        nullable=False,
        doc="The role before the change",
    )
    
    new_role: Mapped[UserRole] = mapped_column(
        nullable=False,
        doc="The role after the change",
    )
    
    changed_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        doc="FK to the user who made the change",
    )
    
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the role change occurred",
    )
    
    reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        doc="Optional explanation for the role change",
    )
    
    # ==================== Relationships ====================
    
    # The user whose role was changed
    user: Mapped["User"] = relationship(
        "User",
        back_populates="role_changes",
        foreign_keys=[user_id],
        doc="The user whose role was changed",
    )
    
    # The user who performed the change
    changed_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[changed_by_id],
        doc="The user who performed the role change",
    )
    
    # ==================== Table Configuration ====================
    
    __table_args__ = (
        # Index for querying a user's role history ordered by time
        Index("ix_user_role_history_user_changed", "user_id", "changed_at"),
        # Index for auditing who made changes
        Index("ix_user_role_history_changed_by", "changed_by_id"),
    )
    
    # ==================== Class Methods ====================
    
    @classmethod
    def create_for_role_change(
        cls,
        user: "User",
        new_role: UserRole,
        changed_by: "User",
        reason: Optional[str] = None,
    ) -> "UserRoleHistory":
        """
        Factory method to create a role history record.
        
        This captures the current role as old_role before the change.
        The actual role change on the User object must be done separately.
        
        Args:
            user: The user whose role is being changed.
            new_role: The new role to assign.
            changed_by: The user performing the change.
            reason: Optional explanation for the change.
            
        Returns:
            New UserRoleHistory instance (not yet committed).
            
        Example:
            >>> history = UserRoleHistory.create_for_role_change(
            ...     user=target_user,
            ...     new_role=UserRole.ADMIN,
            ...     changed_by=current_admin,
            ...     reason="Promoted to team lead"
            ... )
            >>> target_user.role = UserRole.ADMIN
            >>> session.add(history)
            >>> await session.commit()
        """
        return cls(
            user_id=user.id,
            old_role=user.role,
            new_role=new_role,
            changed_by_id=changed_by.id,
            reason=reason,
        )
    
    # ==================== Properties ====================
    
    @property
    def was_promotion(self) -> bool:
        """
        Check if this change was a promotion (higher role).
        
        Returns:
            True if new_role > old_role.
        """
        return self.new_role.value > self.old_role.value
    
    @property
    def was_demotion(self) -> bool:
        """
        Check if this change was a demotion (lower role).
        
        Returns:
            True if new_role < old_role.
        """
        return self.new_role.value < self.old_role.value
    
    @property
    def role_change_description(self) -> str:
        """
        Human-readable description of the role change.
        
        Returns:
            String describing the change (e.g., "USER → ADMIN (promotion)").
        """
        direction = ""
        if self.was_promotion:
            direction = " (promotion)"
        elif self.was_demotion:
            direction = " (demotion)"
        
        return f"{self.old_role.name} → {self.new_role.name}{direction}"
    
    # ==================== Dunder Methods ====================
    
    def __repr__(self) -> str:
        """
        String representation for debugging.
        
        Returns:
            String with history id, user_id, role change, and timestamp.
        """
        return (
            f"<UserRoleHistory(id={self.id}, user_id={self.user_id}, "
            f"change={self.old_role.name}→{self.new_role.name}, "
            f"changed_at={self.changed_at})>"
        )
    
    def __str__(self) -> str:
        """
        Human-readable string representation.
        
        Returns:
            Description of the role change.
        """
        return f"Role change for user {self.user_id}: {self.role_change_description}"
