# GraphQL FastAPI Project Plan (v2)

This document provides a comprehensive project breakdown for building a production-ready GraphQL API using FastAPI and Strawberry. The plan is structured into logical epics and tasks that can be easily imported into GitHub Projects for tracking and management.

> **Version 2 Changes:**
> - UserRole as Python IntEnum with permission levels (not lookup table)
> - Soft delete with `deleted_by_id` tracking in TimestampMixin (available to ALL models)
> - UserRoleHistory table for tracking role changes
> - Delete Permission Matrix: User/Admin/Superadmin with different soft/hard delete rights
> - Runnable checkpoints after each epic

---

## Project Overview

The project is a production-ready GraphQL Todo API with the following key features:

- JWT authentication with access and refresh tokens
- Role-based access control (user, admin, superadmin) with permission hierarchy
- Complete CRUD operations for users and todos
- Soft delete with audit trail (who deleted, when)
- Role change history tracking
- Basic statistics
- Docker containerization
- API documentation

### Technology Stack

- **FastAPI** 0.115+
- **Strawberry GraphQL** 0.254+
- **SQLAlchemy** 2.0 async with aiomysql
- **Pydantic** v2
- **MySQL** 8.0 database
- **Alembic** migrations
- **Passlib** with bcrypt for password hashing
- **PyJWT** for token management
- **Docker Compose** for container orchestration
- **UV** for package management

---

## Architecture Decisions

### 1. Role System: IntEnum (Not Lookup Table)

```
SUPERADMIN (level 3)  →  Can manage everyone below
       ↓
    ADMIN (level 2)   →  Can manage users only
       ↓
    USER (level 1)    →  Cannot manage anyone
```

**Rationale:** Three fixed roles don't require runtime flexibility. IntEnum allows natural comparison for hierarchy checks.

### 2. Soft Delete with Audit Trail

All models inherit from `TimestampMixin` which includes:
- `created_at` - When record was created
- `updated_at` - When record was last modified
- `deleted_at` - When soft-deleted (None = active)
- `deleted_by_id` - FK to users.id (who performed deletion)

### 3. Delete Permission Matrix

| Actor | Can Soft Delete | Can Hard Delete |
|-------|-----------------|-----------------|
| **USER** | Own Todos only | ❌ Nothing |
| **ADMIN** | Users, Todos | Todos only |
| **SUPERADMIN** | Users, Todos | Users AND Todos |

### 4. Role Change Tracking

Dedicated `UserRoleHistory` table tracks:
- Who changed whose role
- Previous and new role values
- When it happened
- Optional reason

---

## Epic 1: Project Foundation

This epic covers the initial setup and configuration of the project environment, including dependency management, Docker infrastructure, and basic application structure.

### Task 1.1: Initialize Project Structure and Dependencies

Create the project directory structure following clean architecture principles. The structure should separate concerns into core configuration, database layer, models, repositories, and GraphQL components.

**Actions:**
- Set up the `pyproject.toml` with UV package manager
- Include dependencies:
  - FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 async, aiomysql
  - Pydantic v2, Pydantic-settings
  - Alembic for migrations
  - Passlib[bcrypt] for password hashing
  - PyJWT for tokens
  - Structlog for logging
- Add Docker configuration files
- Verify that the project can be installed in development mode
- Ensure all dependencies resolve correctly

**Expected Deliverables:**
- Project directory structure
- `pyproject.toml` with all dependencies
- Configured Python environment ready for development

**Directory Structure:**
```
app/
├── v1/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── user_role_history.py
│   │   └── todo.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   └── todo_repository.py
│   └── graphql/
│       ├── __init__.py
│       ├── schema.py
│       ├── context.py
│       ├── permissions.py
│       ├── types/
│       │   ├── __init__.py
│       │   ├── user_types.py
│       │   └── todo_types.py
│       └── resolvers/
│           ├── __init__.py
│           ├── user_resolvers.py
│           └── todo_resolvers.py
├── main.py
└── __init__.py
```

---

### Task 1.2: Configure Docker Infrastructure

Create the docker-compose.yml file to orchestrate three services: the API application, MySQL 8.0 database, and Adminer for database management.

**Actions:**
- Configure networking between services using a bridge network
- Set up volume persistence for MySQL data
- Define health checks for both the API and database services
- Configure environment variable handling to support different environments (development, production)
- Create the Dockerfile using UV for package management

**Expected Deliverables:**
- `docker-compose.yml`
- `Dockerfile` with UV installation
- Docker network and volume configuration
- Health check endpoints configured

---

### Task 1.3: Set Up Environment Configuration

Create the `.env.example` file documenting all required environment variables.

**Actions:**
- Implement the settings configuration using Pydantic Settings for type-safe environment variable loading
- Configure validation rules for production safety:
  - DEBUG must be False in production
  - SECRET_KEY minimum length (32+ characters)
  - Database URL validation
- Set up CORS origins configuration
- Implement singleton pattern for settings instance
- Add JWT configuration (access token expiry, refresh token expiry)

**Expected Deliverables:**
- `.env.example`
- `app/v1/core/config.py` with Settings class (singleton pattern)
- Validation rules implemented
- CORS and JWT configuration ready

---

### Task 1.4: Create Database Layer Foundation

Implement the SQLAlchemy 2.0 async engine and session factory in `app/v1/db/database.py`.

**Actions:**
- Configure connection pooling with appropriate settings for MySQL:
  - `pool_size=10`
  - `max_overflow=20`
  - `pool_recycle=3600`
  - `pool_pre_ping=True`
- Create the base model class in `app/v1/db/base.py` using SQLAlchemy 2.0 DeclarativeBase with type hints
- Implement `TimestampMixin` with:
  - `created_at: Mapped[datetime]`
  - `updated_at: Mapped[datetime]`
  - `deleted_at: Mapped[datetime | None]` - for soft delete
  - `deleted_by_id: Mapped[int | None]` - **NEW: tracks who deleted**
- Create `BaseModel` class combining Base + TimestampMixin + auto-increment id
- Set up async session maker with `expire_on_commit=False` (critical for async)

**Expected Deliverables:**
- Async engine and session factory
- `Base` class (DeclarativeBase)
- `TimestampMixin` with soft delete support
- `BaseModel` with id + timestamps
- Database connection pooling configured

---

### 🏁 CHECKPOINT 1: Project Runnable

After completing Epic 1, the project should be runnable with:
```bash
docker-compose up -d
# API starts (returns 404 on / but no errors)
# Database is accessible
# Health check passes
```

**Verification:**
- [ ] `docker-compose up` starts all services
- [ ] MySQL is accessible via Adminer (localhost:8080)
- [ ] Python app starts without import errors

---

## Epic 2: User Management System

This epic covers the complete implementation of the user management domain, including models, repositories, GraphQL types, and authentication logic.

### Task 2.1: Implement User Model and UserRole Enum

Create the User model in `app/v1/models/user.py` with SQLAlchemy 2.0 type hints.

**Actions:**
- Implement `UserRole` as Python `IntEnum` with permission levels:
  ```python
  class UserRole(IntEnum):
      USER = 1
      ADMIN = 2
      SUPERADMIN = 3
      
      def can_manage(self, other: "UserRole") -> bool:
          """Check if this role can manage another role."""
          return self.value > other.value
  ```
- Define User model fields:
  - `email: Mapped[str]` (unique, indexed)
  - `hashed_password: Mapped[str]`
  - `full_name: Mapped[str]`
  - `role: Mapped[UserRole]` (default: USER)
  - `is_active: Mapped[bool]` (default: True)
  - `created_by_id: Mapped[int | None]` (FK → users.id, self-referential)
  - Inherits: id, created_at, updated_at, deleted_at, deleted_by_id from BaseModel
- Implement computed properties:
  - `is_admin: bool` → `role >= UserRole.ADMIN`
  - `is_superadmin: bool` → `role == UserRole.SUPERADMIN`
  - `todo_count: int` → count of related todos (deferred)
- Implement instance methods:
  - `can_manage(other_user: User) -> bool`
  - `soft_delete(deleted_by: User) -> None`
  - `__repr__() -> str`
- Configure self-referential relationships:
  - `created_by` → User who created this user
  - `deleted_by` → User who soft-deleted this user (via TimestampMixin)

**Expected Deliverables:**
- `UserRole` IntEnum with `can_manage()` method
- User model with all fields
- Self-referential relationships configured
- Computed properties implemented

---

### Task 2.2: Implement UserRoleHistory Model

Create the UserRoleHistory model in `app/v1/models/user_role_history.py` for tracking role changes.

**Actions:**
- Define UserRoleHistory model fields:
  - `user_id: Mapped[int]` (FK → users.id, indexed)
  - `old_role: Mapped[UserRole]`
  - `new_role: Mapped[UserRole]`
  - `changed_by_id: Mapped[int]` (FK → users.id)
  - `changed_at: Mapped[datetime]` (default: now)
  - `reason: Mapped[str | None]` (optional explanation)
  - Inherits: id, created_at, updated_at from BaseModel
- Configure relationships:
  - `user` → The user whose role changed
  - `changed_by` → The user who made the change
- Add indexes for efficient queries:
  - Index on `(user_id, changed_at)` for user role history
  - Index on `changed_by_id` for audit queries

**Expected Deliverables:**
- UserRoleHistory model with all fields
- Relationships to User model
- Proper indexes for query performance

---

### Task 2.3: Create User Repository

Implement the base repository class in `app/v1/repositories/base.py` with generic CRUD operations.

**Actions:**
- Create generic base repository with methods:
  - `get(id: int) -> Model | None` - excludes soft-deleted by default
  - `get_including_deleted(id: int) -> Model | None` - includes soft-deleted
  - `get_multi(skip: int, limit: int) -> list[Model]` - excludes soft-deleted
  - `create(obj_in: CreateSchema) -> Model`
  - `update(db_obj: Model, obj_in: UpdateSchema) -> Model`
  - `soft_delete(db_obj: Model, deleted_by: User) -> Model`
  - `hard_delete(db_obj: Model) -> None`
- Create user-specific repository in `app/v1/repositories/user_repository.py`:
  - `get_by_email(email: str) -> User | None`
  - `create_user(user_in: UserCreate, created_by: User | None) -> User`
  - `update_user_role(user: User, new_role: UserRole, changed_by: User, reason: str | None) -> User`
    - Creates UserRoleHistory record automatically
  - `get_user_statistics() -> UserStatistics`
  - `get_active_users(skip: int, limit: int) -> list[User]`
  - `get_users_by_role(role: UserRole) -> list[User]`
- Implement pagination support for list queries
- **Default behavior: exclude soft-deleted records** (WHERE deleted_at IS NULL)

**Expected Deliverables:**
- Generic base repository class
- User repository with domain-specific methods
- Automatic role history tracking on role changes
- Soft delete exclusion by default
- Pagination support

---

### Task 2.4: Build User GraphQL Types

Create GraphQL types in `app/v1/graphql/types/user_types.py` using Strawberry.

**Actions:**
- Define `UserRoleEnum` for GraphQL:
  ```python
  @strawberry.enum
  class UserRoleEnum(Enum):
      USER = "user"
      ADMIN = "admin"
      SUPERADMIN = "superadmin"
  ```
- Define `UserType` with fields:
  - id, email, full_name, role, is_active
  - created_at, updated_at
  - is_admin, is_superadmin (computed)
  - created_by (lazy resolver)
  - **Exclude:** hashed_password, deleted_at, deleted_by_id (internal)
- Create authentication types:
  - `TokenPair` (access_token, refresh_token, token_type)
  - `AuthPayload` (user: UserType, tokens: TokenPair)
- Create operation types:
  - `OperationResult` (success: bool, message: str)
  - `UserStatistics` (total, active, by_role counts)
- Create input types:
  - `SignupInput` (email, password, full_name)
  - `LoginInput` (email, password)
  - `CreateUserInput` (email, password, full_name, role)
  - `UpdateUserInput` (full_name?, role?, is_active?)
  - `UpdateUserRoleInput` (user_id, new_role, reason?)
- Create `UserRoleHistoryType` for role change audit

**Expected Deliverables:**
- UserType (excluding sensitive fields)
- UserRoleEnum
- TokenPair, AuthPayload
- OperationResult, UserStatistics
- All input types
- UserRoleHistoryType

---

### Task 2.5: Implement Security Module

Create the security module in `app/v1/core/security.py` with password hashing using bcrypt (passlib).

**Actions:**
- Configure Passlib CryptContext for bcrypt:
  ```python
  pwd_context = CryptContext(
      schemes=["bcrypt"],
      deprecated="auto",
      bcrypt__rounds=12,  # ~280ms hash time (2024 recommendation)
  )
  ```
- Implement password functions:
  - `hash_password(plain_password: str) -> str`
  - `verify_password(plain_password: str, hashed_password: str) -> bool`
- Implement JWT token functions:
  - `create_access_token(user_id: int, role: UserRole) -> str` (30 min expiry)
  - `create_refresh_token(user_id: int) -> str` (7 days expiry)
  - `decode_token(token: str) -> TokenPayload | None`
- Create `TokenPayload` dataclass:
  - `sub: str` (user_id)
  - `role: str | None`
  - `exp: datetime`
  - `type: str` ("access" or "refresh")
- Implement proper error handling for:
  - Expired tokens
  - Invalid tokens
  - Malformed tokens

**Expected Deliverables:**
- Password hashing functions (bcrypt, 12 rounds)
- JWT token creation (access/refresh)
- Token decoding and verification
- TokenPayload dataclass
- Error handling

---

### Task 2.6: Build User Resolvers

Implement GraphQL resolvers in `app/v1/graphql/resolvers/user_resolvers.py` for all user operations.

**Actions:**
- Create queries:
  - `me` → Current authenticated user
  - `user(id: int)` → Get user by ID (admin only)
  - `users(skip: int, limit: int)` → List users (admin only, excludes soft-deleted)
  - `userStatistics` → User counts by role (admin only)
  - `userRoleHistory(user_id: int)` → Role change history (admin only)
- Implement mutations:
  - `signup(input: SignupInput)` → Create new user account
  - `login(input: LoginInput)` → Authenticate and return tokens
  - `refreshToken(refresh_token: str)` → Exchange refresh for new access token
  - `createUser(input: CreateUserInput)` → Admin creates user
  - `updateUser(id: int, input: UpdateUserInput)` → Update user profile
  - `updateUserRole(input: UpdateUserRoleInput)` → Change user role (creates history)
  - `deleteUser(id: int)` → Soft delete user (admin: soft, superadmin: can hard delete)
  - `hardDeleteUser(id: int)` → Permanently delete user (superadmin only)
- Implement permission checks:
  - `can_manage()` for role-based operations
  - Delete permission matrix enforcement
- Add meaningful error messages for all failure cases

**Expected Deliverables:**
- User queries (me, user, users, userStatistics, userRoleHistory)
- User mutations (signup, login, refreshToken, createUser, updateUser, updateUserRole, deleteUser, hardDeleteUser)
- Permission enforcement with can_manage()
- Role history tracking on role changes

---

### 🏁 CHECKPOINT 2: User Management Runnable

After completing Epic 2, the project should have working user management:
```bash
# Start the services
docker-compose up -d

# Test via GraphQL Playground (localhost:8000/graphql)
mutation { signup(input: { email: "test@test.com", password: "test123", fullName: "Test User" }) { user { id email } tokens { accessToken } } }
mutation { login(input: { email: "test@test.com", password: "test123" }) { user { id role } tokens { accessToken } } }
query { me { id email role isAdmin } }
```

**Verification:**
- [ ] Can signup new user
- [ ] Can login and receive tokens
- [ ] Can query `me` with valid token
- [ ] Role hierarchy enforced (user cannot access admin endpoints)
- [ ] Soft delete sets deleted_at and deleted_by_id
- [ ] Role changes create UserRoleHistory records

---

## Epic 3: Todo Management System

This epic covers the todo item management domain with full CRUD operations, filtering, and statistics.

### Task 3.1: Implement Todo Model

Create the Todo model in `app/v1/models/todo.py` with SQLAlchemy 2.0 type hints.

**Actions:**
- Define Todo model fields:
  - `title: Mapped[str]` (required, max 200 chars)
  - `description: Mapped[str | None]` (optional, text)
  - `priority: Mapped[TodoPriority]` (enum: low, medium, high, urgent)
  - `status: Mapped[TodoStatus]` (enum: pending, in_progress, completed, cancelled)
  - `due_date: Mapped[datetime | None]`
  - `owner_id: Mapped[int]` (FK → users.id, indexed)
  - `is_completed: Mapped[bool]` (default: False)
  - `completed_at: Mapped[datetime | None]`
  - Inherits: id, created_at, updated_at, deleted_at, deleted_by_id from BaseModel
- Implement enums:
  ```python
  class TodoPriority(IntEnum):
      LOW = 1
      MEDIUM = 2
      HIGH = 3
      URGENT = 4
  
  class TodoStatus(str, Enum):
      PENDING = "pending"
      IN_PROGRESS = "in_progress"
      COMPLETED = "completed"
      CANCELLED = "cancelled"
  ```
- Add computed properties:
  - `is_overdue: bool` → due_date < now and not completed
- Configure relationships:
  - `owner` → User who owns this todo
  - `deleted_by` → User who deleted this todo (via TimestampMixin)

**Expected Deliverables:**
- Todo model with all fields
- TodoPriority and TodoStatus enums
- Overdue checking property
- Soft delete inherited from BaseModel

---

### Task 3.2: Create Todo Repository

Implement todo repository in `app/v1/repositories/todo_repository.py` with all CRUD operations.

**Actions:**
- Implement CRUD operations extending base repository:
  - `get_by_owner(owner_id: int, skip: int, limit: int)` → User's todos
  - `get_by_owner_with_filters(owner_id: int, status?: TodoStatus, priority?: TodoPriority)`
  - `create_todo(todo_in: TodoCreate, owner: User) -> Todo`
  - `complete_todo(todo: Todo) -> Todo` → Sets is_completed, completed_at
  - `soft_delete_todo(todo: Todo, deleted_by: User) -> Todo`
  - `hard_delete_todo(todo: Todo) -> None`
- Implement statistics:
  - `get_user_todo_statistics(owner_id: int) -> TodoStatistics`
  - `get_global_todo_statistics() -> TodoStatistics` (admin)
- Implement permission-aware operations:
  - Users can only soft delete their own todos
  - Admins/Superadmins can hard delete any todo
- Default: exclude soft-deleted records

**Expected Deliverables:**
- Todo repository with CRUD
- Owner-scoped queries
- Soft delete with audit trail
- Statistics aggregation
- Permission-aware delete operations

---

### Task 3.3: Build Todo GraphQL Types

Create GraphQL types in `app/v1/graphql/types/todo_types.py` using Strawberry.

**Actions:**
- Define enums:
  - `TodoPriorityEnum` (LOW, MEDIUM, HIGH, URGENT)
  - `TodoStatusEnum` (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- Define `TodoType` with fields:
  - id, title, description, priority, status
  - due_date, is_completed, completed_at
  - created_at, updated_at
  - is_overdue (computed)
  - owner (lazy resolver)
  - **Exclude:** deleted_at, deleted_by_id (internal)
- Create statistics type:
  - `TodoStatistics` (total, by_status, by_priority, overdue_count)
- Create input types:
  - `CreateTodoInput` (title, description?, priority?, due_date?)
  - `UpdateTodoInput` (title?, description?, priority?, status?, due_date?)
  - `TodoFilterInput` (status?, priority?, is_overdue?)
  - `DeleteTodoInput` (id, reason?) - for admin soft delete with reason

**Expected Deliverables:**
- TodoType
- TodoPriorityEnum, TodoStatusEnum
- TodoStatistics
- Input types for all operations

---

### Task 3.4: Build Todo Resolvers

Implement GraphQL resolvers in `app/v1/graphql/resolvers/todo_resolvers.py` for all todo operations.

**Actions:**
- Create queries:
  - `myTodos(filter?: TodoFilterInput, skip: int, limit: int)` → Current user's todos
  - `todo(id: int)` → Single todo (owner or admin)
  - `allTodos(filter?: TodoFilterInput, skip: int, limit: int)` → All todos (admin only)
  - `todoStatistics` → Current user's stats (or global for admin)
- Implement mutations:
  - `createTodo(input: CreateTodoInput)` → Create for current user
  - `updateTodo(id: int, input: UpdateTodoInput)` → Update own todo
  - `completeTodo(id: int)` → Mark as completed
  - `deleteTodo(id: int)` → Soft delete own todo (USER)
  - `hardDeleteTodo(id: int)` → Hard delete todo (ADMIN, SUPERADMIN)
- Implement Delete Permission Matrix:
  ```
  USER:       soft delete own todos only
  ADMIN:      soft delete any todo, hard delete any todo
  SUPERADMIN: soft delete any todo, hard delete any todo
  ```
- Add permission checks:
  - Users can only modify their own todos
  - Admins can view/delete any todo

**Expected Deliverables:**
- Todo queries (myTodos, todo, allTodos, todoStatistics)
- Todo mutations (createTodo, updateTodo, completeTodo, deleteTodo, hardDeleteTodo)
- Permission enforcement (ownership + role-based)
- Delete permission matrix implemented

---

### 🏁 CHECKPOINT 3: Todo Management Runnable

After completing Epic 3, full todo CRUD should work:
```bash
# Create todo
mutation { createTodo(input: { title: "Learn GraphQL", priority: HIGH }) { id title priority } }

# List my todos
query { myTodos { id title status isOverdue } }

# Complete todo
mutation { completeTodo(id: 1) { id isCompleted completedAt } }

# Soft delete (as user - own todo only)
mutation { deleteTodo(id: 1) { success message } }
```

**Verification:**
- [ ] Can create todos
- [ ] Can list/filter own todos
- [ ] Can update/complete todos
- [ ] USER can only soft delete own todos
- [ ] ADMIN can hard delete any todo
- [ ] Soft-deleted todos excluded from queries by default
- [ ] deleted_by_id populated on soft delete

---

## Epic 4: GraphQL Schema and Permissions

This epic covers the integration of all resolvers into a unified GraphQL schema and implements the permission system.

### Task 4.1: Create GraphQL Context

Implement the context module in `app/v1/graphql/context.py` to provide request-scoped data to resolvers.

**Actions:**
- Extract Authorization header from requests
- Decode JWT token and validate
- Load current user from database (if authenticated)
- Create context dataclass:
  ```python
  @dataclass
  class Context:
      request: Request
      response: Response
      db: AsyncSession
      current_user: User | None
  ```
- Handle unauthenticated requests gracefully (current_user = None)
- Implement async context getter for Strawberry

**Expected Deliverables:**
- Context dataclass
- Token extraction from Authorization header
- Current user resolution from database
- Async session management

---

### Task 4.2: Implement Permission Classes

Create permission classes in `app/v1/graphql/permissions.py` using Strawberry's permission system.

**Actions:**
- Implement base permissions:
  - `IsAuthenticated` → Requires valid token
  - `IsAdmin` → Requires ADMIN or SUPERADMIN role
  - `IsSuperadmin` → Requires SUPERADMIN role only
- Implement resource-specific permissions:
  - `IsOwnerOrAdmin` → User owns resource OR is admin
  - `CanSoftDelete` → Based on delete permission matrix
  - `CanHardDelete` → Admin/Superadmin for todos, Superadmin for users
- Permission classes should:
  - Return clear error messages
  - Log permission denials for audit
  - Be composable (AND/OR logic)

**Expected Deliverables:**
- IsAuthenticated permission class
- IsAdmin, IsSuperadmin permission classes
- IsOwnerOrAdmin permission class
- CanSoftDelete, CanHardDelete permission classes
- Clear error messages

---

### Task 4.3: Build Unified GraphQL Schema

Create the schema file in `app/v1/graphql/schema.py` combining all Query and Mutation classes.

**Actions:**
- Import and combine Query classes:
  - UserQuery (me, user, users, userStatistics, userRoleHistory)
  - TodoQuery (myTodos, todo, allTodos, todoStatistics)
- Import and combine Mutation classes:
  - UserMutation (signup, login, refreshToken, createUser, updateUser, updateUserRole, deleteUser, hardDeleteUser)
  - TodoMutation (createTodo, updateTodo, completeTodo, deleteTodo, hardDeleteTodo)
- Generate final schema with proper configuration
- Enable GraphQL introspection for development

**Expected Deliverables:**
- Combined Query class
- Combined Mutation class
- Schema generation
- All resolvers accessible

---

### Task 4.4: Configure GraphQL Router

Update `app/main.py` to integrate the GraphQL router with FastAPI.

**Actions:**
- Mount Strawberry GraphQL router at `/graphql`
- Configure GraphiQL IDE (enabled in DEBUG mode only)
- Set up async context getter
- Add CORS middleware with configured origins
- Configure subscription support (if needed)

**Expected Deliverables:**
- GraphQL router mounted at /graphql
- GraphiQL configured for development
- Context getter integrated
- CORS configured

---

### 🏁 CHECKPOINT 4: Full GraphQL API Runnable

After completing Epic 4, the complete GraphQL API should be functional:
```bash
# Access GraphiQL at localhost:8000/graphql
# All queries and mutations available
# Permissions enforced correctly
```

**Verification:**
- [ ] GraphiQL accessible at /graphql
- [ ] Schema introspection works
- [ ] All user operations work with permissions
- [ ] All todo operations work with permissions
- [ ] Delete permission matrix enforced

---

## Epic 5: Database Migrations

This epic covers setting up Alembic for database migration management and creating the initial schema.

### Task 5.1: Configure Alembic

Create the `alembic.ini` configuration file with proper settings.

**Actions:**
- Set up migration script location (`alembic/versions/`)
- Configure file naming templates (timestamp-based)
- Set up logging configuration
- Create `alembic/env.py` for async SQLAlchemy 2.0:
  - Import all models for autogenerate
  - Configure async engine connection
  - Support offline and online migration modes
- Create migration script template

**Expected Deliverables:**
- `alembic.ini`
- `alembic/env.py` with async support
- Migration script template
- All models imported for autogenerate

---

### Task 5.2: Create Initial Migration

Generate and customize the initial migration file.

**Actions:**
- Create tables in order (respecting FK dependencies):
  1. `users` table
  2. `user_role_history` table
  3. `todos` table
- Define all columns with proper types:
  - Use MySQL-specific types where appropriate (e.g., `BIGINT` for IDs)
  - VARCHAR lengths specified
  - DATETIME(timezone=True) for timestamps
  - JSON type if needed
- Create indexes:
  - `users.email` (unique)
  - `users.deleted_at` (for soft delete filtering)
  - `user_role_history.user_id` + `changed_at`
  - `todos.owner_id`
  - `todos.deleted_at`
- Set up foreign key constraints with appropriate ON DELETE behavior:
  - `users.created_by_id` → SET NULL
  - `users.deleted_by_id` → SET NULL
  - `user_role_history.user_id` → CASCADE
  - `user_role_history.changed_by_id` → SET NULL
  - `todos.owner_id` → CASCADE
  - `todos.deleted_by_id` → SET NULL
- Implement downgrade method for rollback

**Expected Deliverables:**
- Initial migration with users, user_role_history, todos tables
- All indexes and constraints
- Proper FK cascade behavior
- Downgrade implementation tested

---

### 🏁 CHECKPOINT 5: Migrations Runnable

After completing Epic 5:
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Verify tables created
docker-compose exec api alembic current
```

**Verification:**
- [ ] Migrations run without errors
- [ ] All tables created with correct schema
- [ ] Indexes created
- [ ] FK constraints work correctly
- [ ] Downgrade works (alembic downgrade -1)

---

## Epic 6: Application Entry Point

This epic covers the main FastAPI application configuration and health check endpoints.

### Task 6.1: Create Main Application

Implement `app/main.py` with FastAPI application initialization.

**Actions:**
- Configure structured logging with structlog:
  - JSON format for production
  - Pretty print for development
- Implement lifespan events:
  - Startup: Verify database connection, run health check
  - Shutdown: Dispose engine connections properly
- Create REST endpoints:
  - `GET /` → API info (name, version, environment)
  - `GET /health` → Health check for Docker
  - `GET /health/db` → Database connectivity check
- Configure documentation:
  - Swagger UI at `/docs` (DEBUG only)
  - ReDoc at `/redoc` (DEBUG only)
- Add middleware:
  - CORS
  - Request ID injection
  - Request logging

**Expected Deliverables:**
- FastAPI application with lifespan management
- Health check endpoints
- Root endpoint with API info
- Structured logging configured
- Documentation configured

---

### Task 6.2: Create Seed Script

Implement `scripts/seed_superadmin.py` to create the initial superadmin account.

**Actions:**
- Read superadmin config from environment:
  - `SUPERADMIN_EMAIL`
  - `SUPERADMIN_PASSWORD`
  - `SUPERADMIN_FULL_NAME`
- Check if superadmin already exists (idempotent)
- Create superadmin user with:
  - role = SUPERADMIN
  - created_by_id = None (self-created)
  - is_active = True
- Log creation result
- Handle errors gracefully

**Expected Deliverables:**
- Seed script executable
- Idempotent operation
- Environment-based configuration
- Proper logging

---

### 🏁 CHECKPOINT 6: Production-Ready Application

After completing Epic 6:
```bash
# Start application
docker-compose up -d

# Check health
curl localhost:8000/health
# {"status": "healthy"}

# Seed superadmin
docker-compose exec api python scripts/seed_superadmin.py

# Login as superadmin
# Use GraphQL playground with superadmin credentials
```

**Verification:**
- [ ] Health endpoints return correct status
- [ ] Structured logs output correctly
- [ ] Superadmin seeded successfully
- [ ] Can login as superadmin
- [ ] Superadmin has full permissions

---

## Epic 7: Testing and Quality Assurance

This epic covers setting up testing infrastructure and ensuring code quality.

### Task 7.1: Set Up Testing Infrastructure

Configure pytest for testing the application.

**Actions:**
- Set up test database (SQLite for unit tests, MySQL for integration)
- Create `conftest.py` with fixtures:
  - `db_session` → Test database session
  - `test_user` → Regular user for tests
  - `test_admin` → Admin user for tests
  - `test_superadmin` → Superadmin for tests
  - `authenticated_client` → Client with valid token
- Configure pytest-asyncio for async tests
- Set up coverage reporting (target: 80%+)

**Expected Deliverables:**
- pytest configuration (`pyproject.toml` or `pytest.ini`)
- Test fixtures in `conftest.py`
- Async test support
- Coverage configuration

---

### Task 7.2: Write Unit Tests

Create unit tests for core modules.

**Actions:**
- Test security module:
  - Password hashing and verification
  - JWT creation and decoding
  - Token expiration handling
- Test models:
  - UserRole.can_manage() method
  - User.can_manage() method
  - Todo.is_overdue property
- Test repositories:
  - CRUD operations with mocked sessions
  - Soft delete behavior
  - Role history creation

**Expected Deliverables:**
- Unit tests for security module
- Unit tests for models
- Unit tests for repositories
- High coverage (80%+)

---

### Task 7.3: Write Integration Tests

Create integration tests for GraphQL resolvers.

**Actions:**
- Test authentication flow:
  - Signup creates user
  - Login returns valid tokens
  - Token refresh works
- Test authorization:
  - Permission denials return proper errors
  - Role hierarchy enforced
  - Delete permission matrix works
- Test CRUD operations:
  - User CRUD with permissions
  - Todo CRUD with ownership checks
  - Soft delete sets correct fields
- Test role change tracking:
  - Role changes create history records
  - History queryable

**Expected Deliverables:**
- Authentication flow tests
- Authorization tests
- CRUD operation tests
- Role history tests

---

### Task 7.4: Set Up Code Quality Tools

Configure code quality tools for the project.

**Actions:**
- Configure formatting:
  - Ruff for formatting (replaces black + isort)
  - Line length: 100
- Configure linting:
  - Ruff for linting (replaces flake8)
  - Enable recommended rules
- Configure type checking:
  - mypy with strict mode
  - pyright as secondary checker
- Set up pre-commit hooks:
  - Format on commit
  - Lint on commit
  - Type check on commit

**Expected Deliverables:**
- Ruff configuration (format + lint)
- mypy configuration
- Pre-commit hooks
- CI-ready quality checks

---

## Epic 8: Documentation

This epic covers creating comprehensive documentation for the project.

### Task 8.1: Create README Documentation

Write a comprehensive `README.md`.

**Actions:**
- Document project overview:
  - Purpose and features
  - Technology stack
  - Architecture decisions
- Document setup instructions:
  - Prerequisites
  - Environment configuration
  - Docker commands
  - Running locally
- Document API overview:
  - GraphQL endpoint
  - Authentication flow
  - Role hierarchy
- Include troubleshooting section

**Expected Deliverables:**
- Comprehensive README.md
- Setup instructions
- API overview
- Troubleshooting guide

---

### Task 8.2: Document API with Examples

Create GraphQL API documentation.

**Actions:**
- Document all queries with examples:
  - Request format
  - Response format
  - Required permissions
- Document all mutations with examples
- Document authentication:
  - How to obtain tokens
  - How to use tokens
  - Token refresh flow
- Document role-based access:
  - Permission matrix
  - Delete permissions
  - Role change process

**Expected Deliverables:**
- Query documentation with examples
- Mutation documentation with examples
- Authentication guide
- Role-based access documentation

---

### Task 8.3: Add Inline Documentation

Ensure all modules have comprehensive docstrings.

**Actions:**
- Add module-level docstrings
- Document all public classes and methods
- Add type hints everywhere
- Document complex logic with inline comments

**Expected Deliverables:**
- Complete inline documentation
- All public APIs documented
- Type hints complete

---

## Epic 9: CI/CD Pipeline

This epic covers setting up continuous integration and deployment workflows.

### Task 9.1: Create CI Pipeline

Create GitHub Actions workflow for continuous integration.

**Actions:**
- Create `.github/workflows/ci.yml`:
  - Trigger on push and PR
  - Run linting (ruff)
  - Run type checking (mypy)
  - Run tests with coverage
  - Upload coverage report
- Add security scanning:
  - Dependency vulnerability scan
  - Secret scanning

**Expected Deliverables:**
- GitHub Actions CI workflow
- Linting and type checking
- Test execution with coverage
- Security scanning

---

### Task 9.2: Create CD Pipeline

Create deployment workflow for staging/production.

**Actions:**
- Create `.github/workflows/deploy.yml`:
  - Trigger on tag push (releases)
  - Build Docker image
  - Push to container registry
  - Deploy to target environment
- Add deployment verification:
  - Health check after deploy
  - Smoke tests
  - Rollback on failure

**Expected Deliverables:**
- GitHub Actions CD workflow
- Docker image building
- Deployment automation
- Health verification
- Rollback procedure

---

## Summary

This updated project plan incorporates all architectural decisions made during the design phase:

1. **UserRole as IntEnum** - Simple, type-safe, with `can_manage()` hierarchy checks
2. **Soft delete in TimestampMixin** - Available to all models with `deleted_at` and `deleted_by_id`
3. **UserRoleHistory** - Dedicated table for tracking role changes
4. **Delete Permission Matrix** - Clear rules for who can soft/hard delete what
5. **Runnable Checkpoints** - Project can be tested after each epic

The modular structure allows for incremental development while maintaining a working application at all times. Each checkpoint provides verification steps to ensure the implementation is correct before moving forward.

---

## Quick Reference: Delete Permission Matrix

| Actor | Users (Soft) | Users (Hard) | Todos (Soft) | Todos (Hard) |
|-------|--------------|--------------|--------------|--------------|
| USER | ❌ | ❌ | ✅ Own only | ❌ |
| ADMIN | ✅ Any | ❌ | ✅ Any | ✅ Any |
| SUPERADMIN | ✅ Any | ✅ Any | ✅ Any | ✅ Any |

---

## Quick Reference: Role Hierarchy

```
SUPERADMIN (3) > ADMIN (2) > USER (1)

can_manage(other) = self.level > other.level
```

---

*Version 2.0 - Updated with soft delete, role history, and permission matrix*
