# GraphQL FastAPI Project Plan

This document provides a comprehensive project breakdown for building a production-ready GraphQL API using FastAPI and Strawberry. The plan is structured into logical epics and tasks that can be easily imported into GitHub Projects for tracking and management.

## Project Overview

The project is a production-ready GraphQL Todo API with the following key features:

- JWT authentication with access and refresh tokens
- Role-based access control (user, admin, superadmin)
- Complete CRUD operations for users and todos
- Basic statistics
- Docker containerization
- API documentation

### Technology Stack

- **FastAPI** 0.115+
- **Strawberry GraphQL** 0.254+
- **SQLAlchemy** 2.0 async
- **Pydantic** v2
- **MySQL** database
- **Alembic** migrations
- **Docker Compose** for container orchestration

---

## Epic 1: Project Foundation

This epic covers the initial setup and configuration of the project environment, including dependency management, Docker infrastructure, and basic application structure.

### Task 1.1: Initialize Project Structure and Dependencies

Create the project directory structure following clean architecture principles. The structure should separate concerns into core configuration, database layer, models, repositories, and GraphQL components.

**Actions:**
- Set up the `pyproject.toml` or `requirements.txt` with all necessary dependencies
- Include FastAPI, Strawberry GraphQL, SQLAlchemy with async support, Pydantic v2, Alembic
- Add Docker configuration files
- Verify that the project can be installed in development mode
- Ensure all dependencies resolve correctly

**Expected Deliverables:**
- Project directory structure
- Dependency files (`requirements.txt` or `pyproject.toml`)
- Configured Python environment ready for development

---

### Task 1.2: Configure Docker Infrastructure

Create the docker-compose.yml file to orchestrate three services: the API application, MySQL 8.0 database, and Adminer for database management.

**Actions:**
- Configure networking between services using a bridge network
- Set up volume persistence for MySQL data
- Define health checks for both the API and database services
- Configure environment variable handling to support different environments (development, production)
- Create the Dockerfile using a multi-stage build process to minimize image size

**Expected Deliverables:**
- `docker-compose.yml`
- `Dockerfile`
- Docker network and volume configuration
- Health check endpoints configured

---

### Task 1.3: Set Up Environment Configuration

Create the `.env.example` file documenting all required environment variables.

**Actions:**
- Implement the settings configuration using Pydantic Settings for type-safe environment variable loading
- Configure validation rules for production safety (e.g., DEBUG must be False in production, SECRET_KEY minimum length)
- Set up CORS origins configuration
- Implement the configuration module to load from `.env` file and support environment variable overrides

**Expected Deliverables:**
- `.env.example`
- `app/core/config.py` with Settings class
- Validation rules implemented
- CORS configuration ready

---

### Task 1.4: Create Database Layer Foundation

Implement the SQLAlchemy 2.0 async engine and session factory in `app/db/database.py`.

**Actions:**
- Configure connection pooling with appropriate settings for MySQL (pool_size, max_overflow, pool_recycle, pool_pre_ping)
- Create the base model class in `app/db/base.py` using SQLAlchemy 2.0 DeclarativeBase with type hints
- Define common columns (id, created_at, updated_at) that all models will inherit
- Set up async session maker with proper configuration for request-scoped sessions

**Expected Deliverables:**
- Async engine and session factory
- Base model class
- Common column mixins
- Database connection pooling configured

---

## Epic 2: User Management System

This epic covers the complete implementation of the user management domain, including models, repositories, GraphQL types, and authentication logic.

### Task 2.1: Implement User Model

Create the User model in `app/models/user.py` with SQLAlchemy 2.0 type hints.

**Actions:**
- Define fields including:
  - `email` (unique, indexed)
  - `hashed_password`
  - `full_name`
  - `role` (enum: user, admin, superadmin)
  - `is_active` boolean
  - `created_by_id` for tracking who created each user
  - Timestamps
- Implement the `UserRole` enum with value-based role hierarchy checks (`can_manage` method)
- Add password hashing integration with bcrypt
- Set up the `__repr__` and helper properties for computed fields like `is_admin` and `todo_count`

**Expected Deliverables:**
- User model with all fields
- UserRole enum with hierarchy methods
- Password hashing methods
- Computed properties

---

### Task 2.2: Create User Repository

Implement the base repository class in `app/repositories/base.py` with generic CRUD operations.

**Actions:**
- Create base repository with methods: `get`, `get_multi`, `update`, `delete`
- Create user-specific repository methods in `app/repositories/user_repository.py`:
  - `get_by_email`
  - `create_user` with password hashing
  - User statistics queries
  - Soft delete support
- Implement pagination support for list queries
- Add filter methods for active/inactive users and role-based queries

**Expected Deliverables:**
- Base repository class
- User repository with domain-specific methods
- Pagination support
- Filtering capabilities

---

### Task 2.3: Build User GraphQL Types

Create GraphQL types in `app/graphql/types/user_types.py` using Strawberry.

**Actions:**
- Define `UserType` with all user fields exposed to GraphQL
- Create `UserRoleEnum` for role values
- Create user-related output types
- Implement authentication-specific types:
  - `TokenPair` (access and refresh tokens)
  - `AuthPayload` (user plus tokens)
  - `OperationResult` for mutation responses
- Add input types for login and signup mutations

**Expected Deliverables:**
- UserType
- UserRoleEnum
- TokenPair
- AuthPayload
- OperationResult
- Login/signup input types

---

### Task 2.4: Implement Security Module

Create the security module in `app/core/security.py` with password hashing using bcrypt (passlib).

**Actions:**
- Implement JWT token creation for:
  - Access tokens (short-lived, 30 minutes)
  - Refresh tokens (long-lived, 7 days)
- Build token verification and decoding functions with type checking
- Create the `TokenPayload` class for structured token data
- Implement proper error handling for invalid or expired tokens

**Expected Deliverables:**
- Password hashing functions
- JWT token creation (access/refresh)
- Token decoding and verification
- TokenPayload class

---

### Task 2.5: Build User Resolvers

Implement GraphQL resolvers in `app/graphql/resolvers/user_resolvers.py` for all user operations.

**Actions:**
- Create queries:
  - `me` - retrieving current user
  - `users` - listing users (admin)
  - `user` - getting user by ID
  - `userStatistics` - user statistics
- Implement mutations:
  - `signup`
  - `login`
  - `refreshToken` - token refresh
  - `createUser` - creating users (admin)
  - `updateUser` - updating users
  - `deleteUser` - deleting users
- Add role-based permission checks throughout
- Implement proper error handling with meaningful messages

**Expected Deliverables:**
- User queries (me, users, user, userStatistics)
- User mutations (signup, login, refreshToken, createUser, updateUser, deleteUser)
- Permission enforcement

---

## Epic 3: Todo Management System

This epic covers the todo item management domain with full CRUD operations, filtering, and statistics.

### Task 3.1: Implement Todo Model

Create the Todo model in `app/models/todo.py` with SQLAlchemy 2.0 type hints.

**Actions:**
- Define fields including:
  - `title` (required)
  - `description` (optional)
  - `priority` (enum: low, medium, high, urgent)
  - `status` (enum: pending, in_progress, completed, cancelled)
  - `due_date`
  - `owner_id` (FK to users)
  - `is_completed`
  - `completed_at`
  - Soft delete fields (`deleted_at`, `deleted_by_id`, `deletion_reason`)
- Implement the `TodoPriority` and `TodoStatus` enums
- Add computed properties for checking if todo is overdue

**Expected Deliverables:**
- Todo model with all fields
- TodoPriority and TodoStatus enums
- Overdue checking property

---

### Task 3.2: Create Todo Repository

Implement todo repository in `app/repositories/todo_repository.py` with all CRUD operations.

**Actions:**
- Add methods for getting user-specific todos with filtering by status and priority
- Implement soft delete with audit trail (records who deleted and why)
- Add statistics aggregation for todo counts by status and priority
- Implement completion tracking and overdue detection

**Expected Deliverables:**
- Todo repository with CRUD
- User todo queries
- Soft delete with audit
- Statistics aggregation

---

### Task 3.3: Build Todo GraphQL Types

Create GraphQL types in `app/graphql/types/todo_types.py` using Strawberry.

**Actions:**
- Define `TodoType` with all todo fields
- Create `TodoPriorityEnum`
- Create `TodoStatusEnum`
- Create `TodoStatistics` type for aggregated stats
- Create delete input type for admin operations
- Create input types for create, update, and delete operations

**Expected Deliverables:**
- TodoType
- TodoPriorityEnum
- TodoStatusEnum
- TodoStatistics
- Input types (CreateTodoInput, UpdateTodoInput, DeleteTodoInput)

---

### Task 3.4: Build Todo Resolvers

Implement GraphQL resolvers in `app/graphql/resolvers/todo_resolvers.py` for all todo operations.

**Actions:**
- Create queries:
  - `myTodos` - retrieving current user's todos (with filtering)
  - `todo` - getting specific todo by ID
  - `allTodos` - admin query for all todos
  - `todoStatistics` - todo statistics
- Implement mutations:
  - `createTodo`
  - `updateTodo`
  - `completeTodo`
  - `deleteTodo` - deleting own todos
  - `adminDeleteTodo` - admin deletion with reason
- Add permission checks ensuring users can only modify their own todos

**Expected Deliverables:**
- Todo queries (myTodos, todo, allTodos, todoStatistics)
- Todo mutations (createTodo, updateTodo, completeTodo, deleteTodo, adminDeleteTodo)
- Permission enforcement

---

## Epic 4: GraphQL Schema and Permissions

This epic covers the integration of all resolvers into a unified GraphQL schema and implements the permission system.

### Task 4.1: Create GraphQL Context

Implement the context module in `app/graphql/context.py` to provide request-scoped data to resolvers.

**Actions:**
- Extract and validate the Authorization header from requests
- Decode JWT tokens and retrieve the current user
- Handle both authenticated and unauthenticated requests appropriately
- Pass database session and current user to all resolvers through the context

**Expected Deliverables:**
- Context function
- Token extraction from Authorization header
- Current user resolution
- Session management

---

### Task 4.2: Implement Permission Classes

Create permission classes in `app/graphql/permissions.py` using Strawberry's permission system.

**Actions:**
- Implement `IsAuthenticated` to reject unauthenticated requests
- Implement `IsAdmin` to restrict operations to admin and superadmin roles
- Add permission check methods that can be used as decorators on resolver fields
- Ensure proper error handling for permission denials

**Expected Deliverables:**
- IsAuthenticated permission class
- IsAdmin permission class
- Permission check integration with resolvers

---

### Task 4.3: Build Unified GraphQL Schema

Create the schema file in `app/graphql/schema.py` combining all Query and Mutation classes.

**Actions:**
- Import Query and Mutation from user_resolvers and todo_resolvers
- Use Strawberry's type inheritance to combine all resolvers into a single schema
- Generate the final schema object
- Test that all fields from both domains are accessible through the combined schema

**Expected Deliverables:**
- Combined Query class
- Combined Mutation class
- Schema generation
- All resolvers accessible

---

### Task 4.4: Configure GraphQL Router

Update `app/main.py` to integrate the GraphQL router with FastAPI.

**Actions:**
- Mount the GraphQL router at `/graphql` endpoint
- Configure GraphiQL IDE for development mode
- Set up context getter for passing request data to resolvers
- Add CORS middleware configuration for frontend integration

**Expected Deliverables:**
- GraphQL router mounted
- GraphiQL configured
- Context getter integrated
- CORS configured

---

## Epic 5: Database Migrations

This epic covers setting up Alembic for database migration management and creating the initial schema.

### Task 5.1: Configure Alembic

Create the `alembic.ini` configuration file with proper settings.

**Actions:**
- Set up migration script location
- Configure file naming templates
- Set up logging configuration
- Create the `alembic/env.py` file configured for async SQLAlchemy 2.0 operations
- Set up the migration environment to import models and settings automatically
- Configure offline and online migration modes

**Expected Deliverables:**
- `alembic.ini`
- `alembic/env.py` with async support
- Migration script template

---

### Task 5.2: Create Initial Migration

Generate and customize the initial migration file (`001_initial_migration.py`).

**Actions:**
- Create the users and todos tables
- Define all columns with proper types, constraints, and defaults
- Create foreign key relationships between todos and users
- Add indexes for frequently queried fields (email unique index, owner_id index, deleted_at index)
- Implement the downgrade method for rollback capability
- Test the migration can be applied and reverted successfully

**Expected Deliverables:**
- Initial migration file with users and todos tables
- Indexes and constraints
- Downgrade implementation tested

---

## Epic 6: Application Entry Point

This epic covers the main FastAPI application configuration and health check endpoints.

### Task 6.1: Create Main Application

Implement `app/main.py` with FastAPI application initialization.

**Actions:**
- Configure structured logging with structlog for JSON-formatted logs
- Implement lifespan events:
  - Startup (database connection verification)
  - Shutdown (connection disposal)
- Create the `/health` endpoint required for Docker health checks
- Create the root endpoint providing API information
- Configure API documentation (Swagger/ReDoc) based on DEBUG setting

**Expected Deliverables:**
- FastAPI application
- Lifespan management
- Health check endpoint
- Root endpoint
- Structured logging configured

---

### Task 6.2: Create Seed Script

Implement `scripts/seed_superadmin.py` to create the initial superadmin account.

**Actions:**
- Read superadmin configuration from environment variables
- Check if superadmin already exists before creation (idempotent operation)
- Use the user repository to create the account with proper password hashing
- Log the creation result and credentials

**Expected Deliverables:**
- Seed script executable
- Idempotent operation
- Superadmin account creation verified

---

## Epic 7: Testing and Quality Assurance

This epic covers setting up testing infrastructure and ensuring code quality.

### Task 7.1: Set Up Testing Infrastructure

Configure pytest for testing the application.

**Actions:**
- Set up test database using SQLite for fast unit tests
- Create `conftest.py` with fixtures for database sessions, test users, and authenticated clients
- Configure coverage reporting to track test completeness
- Set up pytest-asyncio for async test support

**Expected Deliverables:**
- pytest configuration
- Test fixtures
- Async test support
- Coverage configuration

---

### Task 7.2: Write Unit Tests

Create unit tests for core modules.

**Actions:**
- Test security module (password hashing, JWT creation/verification)
- Test repository operations with mocked database sessions
- Test model methods and computed properties
- Test configuration validation rules
- Ensure all utility functions have comprehensive test coverage

**Expected Deliverables:**
- Unit tests for security, repositories, models, configuration with high coverage

---

### Task 7.3: Write Integration Tests

Create integration tests for GraphQL resolvers using test client.

**Actions:**
- Test authentication flow (signup, login, token refresh)
- Test authorization (permission denials, role-based access)
- Test CRUD operations for todos with proper ownership checks
- Test statistics queries
- Verify soft delete behavior and audit trails

**Expected Deliverables:**
- Integration tests for all GraphQL operations
- Authentication and authorization tests
- CRUD tests with permissions

---

### Task 7.4: Set Up Code Quality Tools

Configure code quality tools for the project.

**Actions:**
- Configure black for code formatting
- Set up isort for import sorting
- Configure ruff or flake8 for linting
- Add pre-commit hooks to run quality checks before commits
- Set up mypy for type checking
- Configure pyright for enhanced type checking

**Expected Deliverables:**
- Code formatters configured
- Linters configured
- Type checking configured
- Pre-commit hooks set up

---

## Epic 8: Documentation

This epic covers creating comprehensive documentation for the project.

### Task 8.1: Create README Documentation

Write a comprehensive `README.md`.

**Actions:**
- Explain the project purpose, technology stack, and key features
- Document the project structure with directory explanations
- Provide clear instructions for local development setup
- Document environment variables and configuration options
- Include troubleshooting common issues

**Expected Deliverables:**
- README.md with project overview, features, structure, setup instructions, troubleshooting

---

### Task 8.2: Document API with Examples

Create documentation for all GraphQL queries and mutations.

**Actions:**
- Provide example requests for each operation type
- Document authentication flow and token usage
- Document role-based access restrictions
- Include GraphQL Playground access instructions

**Expected Deliverables:**
- API documentation with examples
- Authentication guide
- Role-based access documentation

---

### Task 8.3: Add Inline Documentation

Ensure all modules have comprehensive docstrings.

**Actions:**
- Add inline comments for complex logic
- Document public API functions and classes
- Ensure type hints are complete and descriptive

**Expected Deliverables:**
- Complete inline documentation
- Documented public APIs
- Clear code comments

---

## Epic 9: CI/CD Pipeline

This epic covers setting up continuous integration and deployment workflows.

### Task 9.1: Create CI Pipeline

Create GitHub Actions workflow for continuous integration.

**Actions:**
- Run linting and type checking on every push
- Run test suite with coverage reporting
- Build Docker images and push to registry (if configured)
- Notify on failure through configured channels
- Run security scans on dependencies

**Expected Deliverables:**
- GitHub Actions CI workflow
- Linting and type checking
- Test execution with coverage
- Security scanning

---

### Task 9.2: Create CD Pipeline

Create deployment workflow for production or staging environments.

**Actions:**
- Build and push Docker images
- Deploy using docker-compose or Kubernetes
- Run migrations before deployment
- Verify deployment health with smoke tests
- Implement rollback procedure for failed deployments

**Expected Deliverables:**
- GitHub Actions CD workflow
- Docker image building
- Deployment automation
- Health verification
- Rollback procedure

---

## Summary

This project plan provides a complete roadmap for building a production-ready GraphQL API with FastAPI and Strawberry. Each epic builds upon the previous one, ensuring a solid foundation before moving to more complex features. The modular structure allows for parallel development of different components while maintaining clear dependencies and integration points.
