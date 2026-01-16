"""
SQLAlchemy models for the application.

This module exports all domain models used throughout the application.
Import from here to ensure all models are properly registered with SQLAlchemy.

Models:
    - User: System user with role-based permissions
    - UserRole: IntEnum defining permission levels (USER, ADMIN, SUPERADMIN)
    - UserRoleHistory: Audit log for role changes

Example:
    from app.v1.models import User, UserRole, UserRoleHistory
    
    user = User(
        email="user@example.com",
        hashed_password="...",
        full_name="John Doe",
        role=UserRole.USER,
    )
"""

from app.v1.models.user import User, UserRole
from app.v1.models.user_role_history import UserRoleHistory

__all__ = [
    # User management
    "User",
    "UserRole",
    "UserRoleHistory",
]
