# User Management System - UML Documentation

## Task 2.1: User Model Architecture

This document contains the complete UML representation for the User Management System, including class diagrams, entity-relationship diagrams, and behavioral diagrams.

---

## 1. Class Diagram (Primary)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           USER MANAGEMENT - CLASS DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────┐
    │         «enumeration»                 │
    │           UserRole                    │
    ├───────────────────────────────────────┤
    │  USER = "user"                        │
    │  ADMIN = "admin"                      │
    │  SUPERADMIN = "superadmin"            │
    ├───────────────────────────────────────┤
    │  + can_manage(other: UserRole): bool  │
    └───────────────────────────────────────┘
                      ▲
                      │ uses
                      │
    ┌─────────────────┴─────────────────────┐
    │                                       │
    │                                       │
┌───┴───────────────────────┐    ┌──────────┴──────────────────────┐
│    «mixin»                │    │       «abstract»                │
│   TimestampMixin          │    │         Base                    │
├───────────────────────────┤    │   (DeclarativeBase)             │
│ + created_at: datetime    │    └─────────────────────────────────┘
│ + updated_at: datetime    │                    ▲
│ + deleted_at: datetime?   │                    │ inherits
│ + deleted_by_id: int?     │                    │
└───────────────────────────┘    ┌───────────────┴─────────────────┐
            ▲                    │        «abstract»               │
            │ inherits           │        BaseModel                │
            │                    ├─────────────────────────────────┤
            └────────────────────│ + id: int «PK, auto»            │
                                 └─────────────────────────────────┘
                                                 ▲
                                                 │ inherits
                         ┌───────────────────────┴───────────────────────┐
                         │                                               │
    ┌────────────────────┴────────────────────────────┐    ┌─────────────┴─────────────────────┐
    │                     User                        │    │        UserRoleHistory            │
    ├─────────────────────────────────────────────────┤    ├───────────────────────────────────┤
    │ + id: int «PK»                                  │    │ + id: int «PK»                    │
    │ + email: str «unique, indexed»                  │    │ + user_id: int «FK, indexed»      │
    │ + hashed_password: str                          │    │ + old_role: UserRole              │
    │ + full_name: str                                │    │ + new_role: UserRole              │
    │ + role: UserRole «default: USER»                │    │ + changed_by_id: int «FK»         │
    │ + is_active: bool «default: True»               │    │ + changed_at: datetime            │
    │ + created_by_id: int? «FK → users.id»           │    │ + reason: str?                    │
    │ ─────────────── from TimestampMixin ─────────── │    ├───────────────────────────────────┤
    │ + created_at: datetime                          │    │ (inherits id, timestamps from     │
    │ + updated_at: datetime                          │    │  BaseModel)                       │
    │ + deleted_at: datetime?                         │    └───────────────────────────────────┘
    │ + deleted_by_id: int? «FK → users.id»           │                    │
    ├─────────────────────────────────────────────────┤                    │
    │ «property» + is_admin: bool                     │                    │
    │ «property» + is_superadmin: bool                │                    │
    │ «property» + todo_count: int                    │                    │
    ├─────────────────────────────────────────────────┤                    │
    │ + can_manage(other: User): bool                 │                    │
    │ + set_password(plain: str): void                │◄───────────────────┘
    │ + verify_password(plain: str): bool             │     user_id, changed_by_id
    │ + soft_delete(deleted_by: User): void           │
    │ + __repr__(): str                               │
    └─────────────────────────────────────────────────┘
                         │
                         │ self-referential
                         │ (created_by_id, deleted_by_id)
                         ▼
                    ┌─────────┐
                    │  User   │
                    └─────────┘
```

---

## 2. Entity-Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         ENTITY-RELATIONSHIP DIAGRAM                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                           users                                 │
    ├─────────────────────────────────────────────────────────────────┤
    │ «PK»  id              INT AUTO_INCREMENT                        │
    │       email           VARCHAR(255) UNIQUE NOT NULL   [indexed]  │
    │       hashed_password VARCHAR(255) NOT NULL                     │
    │       full_name       VARCHAR(100) NOT NULL                     │
    │       role            VARCHAR(20) NOT NULL DEFAULT 'user'       │
    │       is_active       BOOLEAN NOT NULL DEFAULT TRUE             │
    │ «FK»  created_by_id   INT NULL → users.id                       │
    │       created_at      DATETIME NOT NULL DEFAULT NOW()           │
    │       updated_at      DATETIME NOT NULL DEFAULT NOW()           │
    │       deleted_at      DATETIME NULL                  [indexed]  │
    │ «FK»  deleted_by_id   INT NULL → users.id                       │
    └─────────────────────────────────────────────────────────────────┘
           │                    │
           │ 1                  │ 1
           │                    │
           │ created_by        │ deleted_by
           │                    │
           ▼ 0..*               ▼ 0..*
    ┌──────┴──────┐      ┌──────┴──────┐
    │    users    │      │    users    │
    └─────────────┘      └─────────────┘


    ┌─────────────────────────────────────────────────────────────────┐
    │                      user_role_history                          │
    ├─────────────────────────────────────────────────────────────────┤
    │ «PK»  id              INT AUTO_INCREMENT                        │
    │ «FK»  user_id         INT NOT NULL → users.id        [indexed]  │
    │       old_role        VARCHAR(20) NOT NULL                      │
    │       new_role        VARCHAR(20) NOT NULL                      │
    │ «FK»  changed_by_id   INT NOT NULL → users.id                   │
    │       changed_at      DATETIME NOT NULL DEFAULT NOW()           │
    │       reason          VARCHAR(500) NULL                         │
    │       ─────────────── from BaseModel ───────────────            │
    │       created_at      DATETIME NOT NULL DEFAULT NOW()           │
    │       updated_at      DATETIME NOT NULL DEFAULT NOW()           │
    │       deleted_at      DATETIME NULL                             │
    │       deleted_by_id   INT NULL                                  │
    └─────────────────────────────────────────────────────────────────┘
           │                    │
           │ N                  │ N
           │                    │
           │ user_id           │ changed_by_id
           │                    │
           ▼ 1                  ▼ 1
    ┌──────┴──────┐      ┌──────┴──────┐
    │    users    │      │    users    │
    └─────────────┘      └─────────────┘


    ┌─────────────────────────────────────────────────────────────────┐
    │                    RELATIONSHIP SUMMARY                         │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   users.created_by_id  ───────►  users.id      (self, 0..1:1)  │
    │   users.deleted_by_id  ───────►  users.id      (self, 0..1:1)  │
    │   user_role_history.user_id ──►  users.id      (N:1)           │
    │   user_role_history.changed_by_id ► users.id   (N:1)           │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 3. Delete Permission Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          DELETE PERMISSION MATRIX                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┬────────────────────────────┬────────────────────────────┐
    │    Actor     │        SOFT DELETE         │        HARD DELETE         │
    ├──────────────┼────────────────────────────┼────────────────────────────┤
    │              │                            │                            │
    │    USER      │  ✅ Own Todos only         │  ❌ Nothing                │
    │              │                            │                            │
    ├──────────────┼────────────────────────────┼────────────────────────────┤
    │              │                            │                            │
    │   ADMIN      │  ✅ Users                  │  ✅ Todos                  │
    │              │  ✅ Todos                  │  ❌ Users                  │
    │              │                            │                            │
    ├──────────────┼────────────────────────────┼────────────────────────────┤
    │              │                            │                            │
    │ SUPERADMIN   │  ✅ Users                  │  ✅ Users                  │
    │              │  ✅ Todos                  │  ✅ Todos                  │
    │              │                            │                            │
    └──────────────┴────────────────────────────┴────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                     SOFT DELETE BEHAVIOR                        │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   When soft_delete(deleted_by: User) is called:                 │
    │                                                                 │
    │   1. Set deleted_at = datetime.now(UTC)                         │
    │   2. Set deleted_by_id = deleted_by.id                          │
    │   3. Record remains in database (queryable with filter)         │
    │   4. Default queries exclude soft-deleted records               │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 4. Role Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            ROLE HIERARCHY                                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │   SUPERADMIN    │  Permission Level: 3
                            │  (Full Access)  │
                            └────────┬────────┘
                                     │
                                     │ can_manage ✅
                                     ▼
                            ┌─────────────────┐
                            │     ADMIN       │  Permission Level: 2
                            │ (User Manager)  │
                            └────────┬────────┘
                                     │
                                     │ can_manage ✅
                                     ▼
                            ┌─────────────────┐
                            │      USER       │  Permission Level: 1
                            │ (Standard User) │
                            └─────────────────┘


    ┌─────────────────────────────────────────────────────────────────┐
    │                   can_manage() LOGIC                            │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   def can_manage(self, other_user: User) -> bool:               │
    │       # Rule 1: Cannot manage yourself                          │
    │       if self.id == other_user.id:                              │
    │           return False                                          │
    │                                                                 │
    │       # Rule 2: Must have higher permission level               │
    │       return self.role.permission_level > \                     │
    │              other_user.role.permission_level                   │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                   PERMISSION EXAMPLES                           │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   SUPERADMIN.can_manage(ADMIN)      → ✅ True                   │
    │   SUPERADMIN.can_manage(USER)       → ✅ True                   │
    │   SUPERADMIN.can_manage(SUPERADMIN) → ❌ False (same level)     │
    │                                                                 │
    │   ADMIN.can_manage(USER)            → ✅ True                   │
    │   ADMIN.can_manage(ADMIN)           → ❌ False (same level)     │
    │   ADMIN.can_manage(SUPERADMIN)      → ❌ False (lower level)    │
    │                                                                 │
    │   USER.can_manage(USER)             → ❌ False (same level)     │
    │   USER.can_manage(ADMIN)            → ❌ False (lower level)    │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 5. Role Change Workflow (Sequence Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      ROLE CHANGE SEQUENCE DIAGRAM                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐          ┌──────────┐          ┌──────┐          ┌─────────────────┐
    │  Admin  │          │ Resolver │          │ User │          │ UserRoleHistory │
    └────┬────┘          └────┬─────┘          └──┬───┘          └────────┬────────┘
         │                    │                   │                       │
         │  updateUserRole    │                   │                       │
         │  (user_id=5,       │                   │                       │
         │   new_role=ADMIN,  │                   │                       │
         │   reason="Promo")  │                   │                       │
         │───────────────────►│                   │                       │
         │                    │                   │                       │
         │                    │  1. Validate      │                       │
         │                    │     admin.can_manage(user)                │
         │                    │──────────────────►│                       │
         │                    │                   │                       │
         │                    │  ◄─ True ─────────│                       │
         │                    │                   │                       │
         │                    │  2. Get old_role  │                       │
         │                    │──────────────────►│                       │
         │                    │                   │                       │
         │                    │  ◄─ USER ─────────│                       │
         │                    │                   │                       │
         │                    │  3. Create history record                 │
         │                    │──────────────────────────────────────────►│
         │                    │                   │                       │
         │                    │   UserRoleHistory(                        │
         │                    │     user_id=5,                            │
         │                    │     old_role=USER,                        │
         │                    │     new_role=ADMIN,                       │
         │                    │     changed_by_id=admin.id,               │
         │                    │     reason="Promo"                        │
         │                    │   )                                       │
         │                    │                   │                       │
         │                    │  4. Update user.role                      │
         │                    │──────────────────►│                       │
         │                    │                   │                       │
         │                    │     user.role = ADMIN                     │
         │                    │                   │                       │
         │  ◄─ Success ───────│                   │                       │
         │                    │                   │                       │
    ┌────┴────┐          ┌────┴─────┐          ┌──┴───┐          ┌────────┴────────┐
    │  Admin  │          │ Resolver │          │ User │          │ UserRoleHistory │
    └─────────┘          └──────────┘          └──────┘          └─────────────────┘
```

---

## 6. Inheritance Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         INHERITANCE HIERARCHY                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                        ┌───────────────────────────┐
                        │   DeclarativeBase         │  SQLAlchemy's base
                        │   (from sqlalchemy.orm)   │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │          Base             │  Your custom base
                        │   (app/v1/db/base.py)     │  (currently empty)
                        └─────────────┬─────────────┘
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
               ▼                      ▼                      │
    ┌─────────────────────┐   ┌─────────────────┐           │
    │   TimestampMixin    │   │                 │           │
    ├─────────────────────┤   │   (combined)    │           │
    │ + created_at        │───┼────────────────►│           │
    │ + updated_at        │   │                 │           │
    │ + deleted_at        │   │                 │           │
    │ + deleted_by_id     │   │                 │           │
    └─────────────────────┘   └────────┬────────┘           │
                                       │                    │
                                       ▼                    │
                        ┌───────────────────────────┐       │
                        │        BaseModel          │◄──────┘
                        │      «abstract»           │
                        ├───────────────────────────┤
                        │ + id: int (PK)            │
                        │ + created_at: datetime    │
                        │ + updated_at: datetime    │
                        │ + deleted_at: datetime?   │
                        │ + deleted_by_id: int?     │
                        └─────────────┬─────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │        User           │           │   UserRoleHistory     │
        ├───────────────────────┤           ├───────────────────────┤
        │ + email               │           │ + user_id             │
        │ + hashed_password     │           │ + old_role            │
        │ + full_name           │           │ + new_role            │
        │ + role                │           │ + changed_by_id       │
        │ + is_active           │           │ + changed_at          │
        │ + created_by_id       │           │ + reason              │
        └───────────────────────┘           └───────────────────────┘
```

---

## 7. Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPONENTS                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    app/
    ├── v1/
    │   ├── db/
    │   │   ├── __init__.py          ◄── Exports: Base, BaseModel, TimestampMixin
    │   │   ├── base.py              ◄── UPDATE: Add deleted_by_id to TimestampMixin
    │   │   └── database.py          ◄── Existing: engine, session factory
    │   │
    │   ├── models/
    │   │   ├── __init__.py          ◄── NEW: Export User, UserRole, UserRoleHistory
    │   │   ├── user.py              ◄── NEW: User model + UserRole enum
    │   │   └── user_role_history.py ◄── NEW: UserRoleHistory model
    │   │
    │   └── core/
    │       ├── config.py            ◄── Existing: settings
    │       └── security.py          ◄── FUTURE (Task 2.4): password hashing
    │
    └── ...


    ┌─────────────────────────────────────────────────────────────────┐
    │                    FILES TO CREATE/MODIFY                       │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   MODIFY:  app/v1/db/base.py                                    │
    │            - Add deleted_by_id: Mapped[int | None] to           │
    │              TimestampMixin                                     │
    │                                                                 │
    │   CREATE:  app/v1/models/user.py                                │
    │            - UserRole enum                                      │
    │            - User model                                         │
    │                                                                 │
    │   CREATE:  app/v1/models/user_role_history.py                   │
    │            - UserRoleHistory model                              │
    │                                                                 │
    │   CREATE:  app/v1/models/__init__.py                            │
    │            - Export all models                                  │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 8. Summary Table

| Entity | Purpose | Key Attributes |
|--------|---------|----------------|
| **UserRole** | Enum defining permission levels | USER, ADMIN, SUPERADMIN with `can_manage()` |
| **TimestampMixin** | Reusable audit timestamps | created_at, updated_at, deleted_at, deleted_by_id |
| **BaseModel** | Abstract base for all models | id (PK) + TimestampMixin fields |
| **User** | Main user entity | email, password, role, is_active, created_by_id |
| **UserRoleHistory** | Tracks role changes | user_id, old_role, new_role, changed_by_id, reason |

---

## 9. Key Design Decisions

1. **Enum over Lookup Table**: UserRole is a Python IntEnum for simplicity. Three fixed roles don't require runtime flexibility.

2. **Soft Delete in Mixin**: `deleted_at` and `deleted_by_id` are in TimestampMixin, making soft delete available to ALL models (User, Todo, etc.).

3. **Self-Referential FKs**: `created_by_id` and `deleted_by_id` point to the same `users` table, tracking who performed actions.

4. **Separate Role History**: UserRoleHistory is a dedicated table (not a general audit log) for efficient role-specific queries.

5. **Permission Level in Enum**: IntEnum allows natural comparison (`SUPERADMIN > ADMIN > USER`) for hierarchy checks.

---

*Generated for Task 2.1: User Model Implementation*
*Project: GraphQL FastAPI Todo API*
