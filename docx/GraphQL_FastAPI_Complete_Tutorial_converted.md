**GraphQL API with FastAPI & Strawberry**

Complete Production-Ready Tutorial

SQLAlchemy 2.0 Async | Pydantic v2 | JWT Authentication | Repository Pattern | Docker

*Senior Backend Developer Reference Guide*

# Table of Contents

# 1. Introduction

This document provides a complete, production-ready implementation of a GraphQL API using FastAPI and Strawberry GraphQL. The project demonstrates senior-level backend patterns including the Repository Pattern, 12-Factor App principles, JWT authentication with refresh tokens, role-based access control, and soft delete functionality.

The codebase uses the latest versions of all frameworks: FastAPI 0.115+, Strawberry GraphQL 0.254+, SQLAlchemy 2.0+ with async support, and Pydantic v2. All code follows modern Python 3.12+ patterns and type hints.

## 1.1 What is GraphQL?

GraphQL is a query language for APIs that provides a complete and understandable description of the data in your API. Unlike REST where you have multiple endpoints returning fixed data structures, GraphQL exposes a single endpoint where clients can request exactly the data they need.

Key GraphQL concepts: Queries (read data), Mutations (write data), Types (data shapes), Resolvers (functions that return data), and Schema (the contract between client and server).

## 1.2 Stack Overview

FastAPI: Modern, fast web framework for building APIs. Strawberry: Python GraphQL library using type hints. SQLAlchemy 2.0: ORM with async support. Pydantic v2: Data validation. Alembic: Database migrations. MySQL: Database. Docker: Containerization.

# 2. Project Structure

The project follows a clean architecture with separation of concerns. Each layer has a specific responsibility: models define data, repositories handle data access, and GraphQL resolvers handle API logic.

graphql-todo-api/

├── docker-compose.yml

├── Dockerfile

├── .env.example

├── .env

├── requirements.txt

├── alembic.ini

├── alembic/

│   ├── env.py

│   ├── script.py.mako

│   └── versions/

│       └── 001_initial_migration.py

├── app/

│   ├── __init__.py

│   ├── main.py

│   ├── core/

│   │   ├── __init__.py

│   │   ├── config.py

│   │   ├── security.py

│   │   └── dependencies.py

│   ├── db/

│   │   ├── __init__.py

│   │   ├── database.py

│   │   └── base.py

│   ├── models/

│   │   ├── __init__.py

│   │   ├── user.py

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

│       ├── types/

│       │   ├── __init__.py

│       │   ├── user_types.py

│       │   ├── todo_types.py

│       │   └── common_types.py

│       ├── inputs/

│       │   ├── __init__.py

│       │   ├── user_inputs.py

│       │   └── todo_inputs.py

│       ├── resolvers/

│       │   ├── __init__.py

│       │   ├── user_resolvers.py

│       │   └── todo_resolvers.py

│       └── permissions.py

└── scripts/

    └── seed_superadmin.py

# 3. Docker Configuration

The application is fully containerized with Docker Compose managing three services: the API, MySQL database, and Adminer for database management.

## 3.1 docker-compose.yml

# docker-compose.yml

# =============================================================================

# Docker Compose for GraphQL Todo API

# 

# SERVICES:

# - api:     FastAPI + Strawberry GraphQL backend

# - db:      MySQL 8.0 database

# - adminer: Database management UI

#

# 12-FACTOR APP PRINCIPLES APPLIED:

# - Config: All configuration via environment variables

# - Backing Services: Database as attached resource

# - Port Binding: Export services via port mapping

# - Dev/Prod Parity: Same setup works in both environments

# =============================================================================

version: "3.8"

services:

  # ===========================================================================

  # API SERVICE - FastAPI + Strawberry GraphQL

  # ===========================================================================

  api:

    build:

      context: .

      dockerfile: Dockerfile

    container_name: graphql-api

    ports:

      - "8000:8000"

    environment:

      # Database Configuration

      - DATABASE_URL=mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db:3306/${MYSQL_DATABASE}

      # JWT Configuration

      - SECRET_KEY=${SECRET_KEY}

      - ALGORITHM=HS256

      - ACCESS_TOKEN_EXPIRE_MINUTES=30

      - REFRESH_TOKEN_EXPIRE_DAYS=7

      # App Configuration

      - DEBUG=${DEBUG:-false}

      - ENVIRONMENT=${ENVIRONMENT:-development}

    depends_on:

      db:

        condition: service_healthy

    volumes:

      # Development: mount source for hot reload

      - ./app:/app/app:ro

    networks:

      - graphql-network

    # Health check for the API

    healthcheck:

      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

      interval: 30s

      timeout: 10s

      retries: 3

      start_period: 40s

  # ===========================================================================

  # DATABASE SERVICE - MySQL 8.0

  # ===========================================================================

  db:

    image: mysql:8.0

    container_name: graphql-db

    restart: unless-stopped

    environment:

      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

      - MYSQL_DATABASE=${MYSQL_DATABASE}

      - MYSQL_USER=${MYSQL_USER}

      - MYSQL_PASSWORD=${MYSQL_PASSWORD}

    ports:

      - "3306:3306"

    volumes:

      # Persist database data

      - mysql_data:/var/lib/mysql

    networks:

      - graphql-network

    # Health check for MySQL

    healthcheck:

      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]

      interval: 10s

      timeout: 5s

      retries: 5

      start_period: 30s

    # MySQL Configuration for better performance

    command: >

      --default-authentication-plugin=mysql_native_password

      --character-set-server=utf8mb4

      --collation-server=utf8mb4_unicode_ci

  # ===========================================================================

  # ADMINER - Database Management UI

  # ===========================================================================

  adminer:

    image: adminer:latest

    container_name: graphql-adminer

    restart: unless-stopped

    ports:

      - "8080:8080"

    environment:

      - ADMINER_DEFAULT_SERVER=db

    depends_on:

      - db

    networks:

      - graphql-network

# =============================================================================

# NETWORKS

# =============================================================================

networks:

  graphql-network:

    driver: bridge

# =============================================================================

# VOLUMES

# =============================================================================

volumes:

  mysql_data:

    driver: local

## 3.2 Dockerfile

# Dockerfile

# =============================================================================

# Multi-stage Dockerfile for GraphQL Todo API

#

# STAGES:

# 1. builder: Install dependencies and prepare the app

# 2. production: Slim production image

#

# BEST PRACTICES APPLIED:

# - Multi-stage build for smaller final image

# - Non-root user for security

# - Layer caching optimization

# - Health check included

# =============================================================================

# ===========================================================================

# STAGE 1: Builder

# ===========================================================================

FROM python:3.12-slim as builder

# Set environment variables

ENV PYTHONDONTWRITEBYTECODE=1 \

    PYTHONUNBUFFERED=1 \

    PIP_NO_CACHE_DIR=1 \

    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies needed for building Python packages

RUN apt-get update && apt-get install -y --no-install-recommends \

    build-essential \

    curl \

    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ===========================================================================

# STAGE 2: Production

# ===========================================================================

FROM python:3.12-slim as production

# Set environment variables

ENV PYTHONDONTWRITEBYTECODE=1 \

    PYTHONUNBUFFERED=1 \

    # App runs on port 8000

    PORT=8000

WORKDIR /app

# Install runtime dependencies only

RUN apt-get update && apt-get install -y --no-install-recommends \

    curl \

    && rm -rf /var/lib/apt/lists/* \

    && apt-get clean

# Create non-root user for security

RUN groupadd --gid 1000 appgroup \

    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy installed packages from builder

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code

COPY --chown=appuser:appgroup . .

# Switch to non-root user

USER appuser

# Expose port

EXPOSE 8000

# Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \

    CMD curl -f http://localhost:8000/health || exit 1

# Run the application

# Using uvicorn with optimal settings for production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

## 3.3 Environment Variables (.env.example)

# .env.example

# =============================================================================

# Environment Variables for GraphQL Todo API

# Copy this file to .env and fill in your values

# =============================================================================

# MySQL Database Configuration

MYSQL_ROOT_PASSWORD=your_root_password_here

MYSQL_DATABASE=graphql_todo

MYSQL_USER=graphql_user

MYSQL_PASSWORD=your_db_password_here

# JWT Configuration

# Generate a secure secret key: openssl rand -hex 32

SECRET_KEY=your_super_secret_key_here_generate_with_openssl_rand_hex_32

# Application Configuration

DEBUG=true

ENVIRONMENT=development

# Superadmin Seed Configuration

SUPERADMIN_EMAIL=superadmin@example.com

SUPERADMIN_PASSWORD=SuperAdmin123!

SUPERADMIN_FULL_NAME=Super Administrator

## 3.4 requirements.txt

# requirements.txt

# =============================================================================

# Python Dependencies for GraphQL Todo API

# All versions pinned for reproducibility

# =============================================================================

# Web Framework

fastapi==0.115.6

uvicorn[standard]==0.34.0

# GraphQL

strawberry-graphql[fastapi]==0.254.0

# Database

sqlalchemy[asyncio]==2.0.36

aiomysql==0.2.0

alembic==1.14.0

# Validation

pydantic==2.10.4

pydantic-settings==2.7.1

email-validator==2.2.0

# Security

passlib[bcrypt]==1.7.4

python-jose[cryptography]==3.3.0

# Async HTTP Client (for health checks)

httpx==0.28.1

# Logging

structlog==24.4.0

# Development

python-dotenv==1.0.1

# 4. Application Core

## 4.1 app/__init__.py

# app/__init__.py

"""

GraphQL Todo API Application Package

This is the main application package containing:

- core/: Configuration, security, dependencies

- db/: Database connection and base models

- models/: SQLAlchemy ORM models

- repositories/: Data access layer (Repository Pattern)

- graphql/: GraphQL schema, types, resolvers

"""

__version__ = "1.0.0"

## 4.2 app/main.py

# app/main.py

"""

=============================================================================

Main Application Entry Point

=============================================================================

This module initializes the FastAPI application and configures:

- Strawberry GraphQL integration

- CORS middleware

- Lifespan events (startup/shutdown)

- Health check endpoint

GRAPHQL CONCEPTS EXPLAINED:

--------------------------

GraphQL is a query language for APIs that provides:

1. Single endpoint (/graphql) for all operations

2. Client-specified data shape (no over/under-fetching)

3. Strong typing with schema definition

4. Three operation types: Query, Mutation, Subscription

FASTAPI + STRAWBERRY INTEGRATION:

--------------------------------

Strawberry is a Python GraphQL library that uses type hints.

It integrates with FastAPI via GraphQLRouter.

"""

from contextlib import asynccontextmanager

from typing import AsyncGenerator

import structlog

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from strawberry.fastapi import GraphQLRouter

from app.core.config import settings

from app.db.database import engine, async_session_maker

from app.graphql.schema import schema

from app.graphql.context import get_context

# Configure structured logging

structlog.configure(

    processors=[

        structlog.stdlib.filter_by_level,

        structlog.stdlib.add_logger_name,

        structlog.stdlib.add_log_level,

        structlog.stdlib.PositionalArgumentsFormatter(),

        structlog.processors.TimeStamper(fmt="iso"),

        structlog.processors.StackInfoRenderer(),

        structlog.processors.format_exc_info,

        structlog.processors.UnicodeDecoder(),

        structlog.processors.JSONRenderer()

    ],

    wrapper_class=structlog.stdlib.BoundLogger,

    context_class=dict,

    logger_factory=structlog.stdlib.LoggerFactory(),

    cache_logger_on_first_use=True,

)

logger = structlog.get_logger(__name__)

# =============================================================================

# LIFESPAN EVENTS

# =============================================================================

# Modern FastAPI uses lifespan context manager instead of on_event decorators

# This handles startup and shutdown logic

@asynccontextmanager

async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    """

    Application lifespan manager.

    STARTUP:

    - Log application start

    - Verify database connection

    SHUTDOWN:

    - Close database connections

    - Cleanup resources

    """

    # Startup

    logger.info(

        "application_starting",

        environment=settings.ENVIRONMENT,

        debug=settings.DEBUG,

    )

    # Verify database connection

    try:

        async with engine.begin() as conn:

            await conn.execute(text("SELECT 1"))

        logger.info("database_connected")

    except Exception as e:

        logger.error("database_connection_failed", error=str(e))

        raise

    yield  # Application runs here

    # Shutdown

    logger.info("application_shutting_down")

    await engine.dispose()

    logger.info("database_connections_closed")

# =============================================================================

# FASTAPI APPLICATION

# =============================================================================

app = FastAPI(

    title="GraphQL Todo API",

    description="A production-ready GraphQL API with FastAPI and Strawberry",

    version="1.0.0",

    lifespan=lifespan,

    docs_url="/docs" if settings.DEBUG else None,  # Disable Swagger in production

    redoc_url="/redoc" if settings.DEBUG else None,

)

# =============================================================================

# CORS MIDDLEWARE

# =============================================================================

# Configure CORS for frontend integration

app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["GET", "POST", "OPTIONS"],

    allow_headers=["*"],

)

# =============================================================================

# GRAPHQL ROUTER

# =============================================================================

# This is where Strawberry GraphQL integrates with FastAPI

#

# KEY COMPONENTS:

# - schema: The GraphQL schema (Query + Mutation types)

# - context_getter: Function that provides context to resolvers

# - graphql_ide: GraphQL IDE for development (GraphiQL/Apollo)

graphql_router = GraphQLRouter(

    schema=schema,

    context_getter=get_context,

    graphql_ide="graphiql" if settings.DEBUG else None,

)

# Mount GraphQL at /graphql endpoint

app.include_router(graphql_router, prefix="/graphql")

# =============================================================================

# HEALTH CHECK ENDPOINT

# =============================================================================

# Required for Docker health checks and load balancer probes

from sqlalchemy import text

@app.get("/health")

async def health_check():

    """

    Health check endpoint.

    Returns:

        dict: Status and database connectivity

    """

    try:

        # Check database connectivity

        async with async_session_maker() as session:

            await session.execute(text("SELECT 1"))

        return {

            "status": "healthy",

            "database": "connected",

            "version": "1.0.0",

        }

    except Exception as e:

        logger.error("health_check_failed", error=str(e))

        return {

            "status": "unhealthy",

            "database": "disconnected",

            "error": str(e),

        }

# =============================================================================

# ROOT ENDPOINT

# =============================================================================

@app.get("/")

async def root():

    """Root endpoint with API information."""

    return {

        "message": "GraphQL Todo API",

        "graphql_endpoint": "/graphql",

        "health_endpoint": "/health",

        "docs": "/docs" if settings.DEBUG else "Disabled in production",

    }

## 4.3 app/core/config.py

# app/core/config.py

"""

=============================================================================

Application Configuration

=============================================================================

This module uses Pydantic Settings for configuration management.

PYDANTIC V2 CHANGES:

- ConfigDict replaces Config class

- model_validator replaces root_validator

- field_validator replaces validator

12-FACTOR APP PRINCIPLE:

- All configuration loaded from environment variables

- No hardcoded values in code

- Different configs for different environments

"""

from typing import List

from pydantic import field_validator, model_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    """

    Application settings loaded from environment variables.

    PYDANTIC SETTINGS V2 FEATURES:

    - Automatic .env file loading

    - Type coercion from string env vars

    - Validation with Pydantic validators

    """

    # =========================================================================

    # DATABASE CONFIGURATION

    # =========================================================================

    DATABASE_URL: str

    # =========================================================================

    # JWT CONFIGURATION

    # =========================================================================

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================================================================

    # APPLICATION CONFIGURATION

    # =========================================================================

    DEBUG: bool = False

    ENVIRONMENT: str = "production"

    # CORS Origins - comma-separated in env, parsed to list

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # =========================================================================

    # SUPERADMIN SEED CONFIGURATION

    # =========================================================================

    SUPERADMIN_EMAIL: str = "superadmin@example.com"

    SUPERADMIN_PASSWORD: str = "SuperAdmin123!"

    SUPERADMIN_FULL_NAME: str = "Super Administrator"

    # =========================================================================

    # PYDANTIC V2 CONFIGURATION

    # =========================================================================

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True,

        extra="ignore",  # Ignore extra env vars

    )

    # =========================================================================

    # VALIDATORS

    # =========================================================================

    @field_validator("CORS_ORIGINS", mode="before")

    @classmethod

    def parse_cors_origins(cls, v):

        """

        Parse CORS origins from comma-separated string.

        Allows: CORS_ORIGINS=http://localhost:3000,http://localhost:8000

        """

        if isinstance(v, str):

            return [origin.strip() for origin in v.split(",")]

        return v

    @model_validator(mode="after")

    def validate_settings(self):

        """

        Validate settings after all fields are populated.

        PYDANTIC V2: model_validator replaces root_validator

        """

        if self.ENVIRONMENT == "production" and self.DEBUG:

            raise ValueError("DEBUG must be False in production")

        if len(self.SECRET_KEY) < 32:

            raise ValueError("SECRET_KEY must be at least 32 characters")

        return self

# Create global settings instance

settings = Settings()

## 4.4 app/core/security.py

# app/core/security.py

"""

=============================================================================

Security Module - JWT Authentication

=============================================================================

This module handles:

- Password hashing with bcrypt

- JWT token creation (access + refresh)

- JWT token verification and decoding

JWT AUTHENTICATION EXPLAINED:

----------------------------

JWT (JSON Web Token) is a compact, URL-safe token format:

- Header: Algorithm and token type

- Payload: Claims (user data, expiration)

- Signature: Verification of token integrity

ACCESS vs REFRESH TOKENS:

------------------------

- Access Token: Short-lived (30 min), used for API requests

- Refresh Token: Long-lived (7 days), used to get new access tokens

WHY TWO TOKENS?

- If access token is compromised, damage is limited (short expiry)

- Refresh token stored more securely (httpOnly cookie)

- User doesn't need to re-login frequently

"""

from datetime import datetime, timedelta, timezone

from typing import Any, Optional

from jose import JWTError, jwt

from passlib.context import CryptContext

from app.core.config import settings

# =============================================================================

# PASSWORD HASHING

# =============================================================================

# bcrypt is the industry standard for password hashing

# - Automatically handles salting

# - Configurable work factor (rounds)

# - Resistant to rainbow table attacks

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto",

    bcrypt__rounds=12,  # Work factor (higher = slower but more secure)

)

def verify_password(plain_password: str, hashed_password: str) -> bool:

    """

    Verify a plain password against its hash.

    Args:

        plain_password: The password to verify

        hashed_password: The stored hash to verify against

    Returns:

        bool: True if password matches, False otherwise

    """

    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:

    """

    Hash a password using bcrypt.

    Args:

        password: Plain text password to hash

    Returns:

        str: Bcrypt hash of the password

    """

    return pwd_context.hash(password)

# =============================================================================

# JWT TOKEN CREATION

# =============================================================================

def create_access_token(

    data: dict[str, Any],

    expires_delta: Optional[timedelta] = None,

) -> str:

    """

    Create a JWT access token.

    TOKEN STRUCTURE:

    {

        "sub": "user_id",       # Subject (user identifier)

        "role": "admin",        # User role for authorization

        "type": "access",       # Token type

        "exp": 1234567890,      # Expiration timestamp

        "iat": 1234567800       # Issued at timestamp

    }

    Args:

        data: Dictionary of claims to encode in token

        expires_delta: Optional custom expiration time

    Returns:

        str: Encoded JWT token

    """

    to_encode = data.copy()

    # Set expiration

    expire = datetime.now(timezone.utc) + (

        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    )

    to_encode.update({

        "exp": expire,

        "iat": datetime.now(timezone.utc),

        "type": "access",

    })

    return jwt.encode(

        to_encode,

        settings.SECRET_KEY,

        algorithm=settings.ALGORITHM,

    )

def create_refresh_token(

    data: dict[str, Any],

    expires_delta: Optional[timedelta] = None,

) -> str:

    """

    Create a JWT refresh token.

    Refresh tokens have:

    - Longer expiration (7 days default)

    - Different "type" claim for validation

    - Same subject (user_id) as access token

    Args:

        data: Dictionary of claims to encode

        expires_delta: Optional custom expiration time

    Returns:

        str: Encoded JWT refresh token

    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (

        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    )

    to_encode.update({

        "exp": expire,

        "iat": datetime.now(timezone.utc),

        "type": "refresh",

    })

    return jwt.encode(

        to_encode,

        settings.SECRET_KEY,

        algorithm=settings.ALGORITHM,

    )

# =============================================================================

# JWT TOKEN VERIFICATION

# =============================================================================

class TokenPayload:

    """

    Decoded token payload structure.

    Attributes:

        sub: Subject (user ID as string)

        role: User role

        type: Token type (access/refresh)

        exp: Expiration timestamp

    """

    def __init__(self, sub: str, role: str, token_type: str, exp: datetime):

        self.sub = sub

        self.role = role

        self.type = token_type

        self.exp = exp

def decode_token(token: str, expected_type: str = "access") -> Optional[TokenPayload]:

    """

    Decode and verify a JWT token.

    VERIFICATION STEPS:

    1. Decode the token using secret key

    2. Verify signature is valid

    3. Check expiration time

    4. Verify token type matches expected

    Args:

        token: JWT token string

        expected_type: Expected token type ("access" or "refresh")

    Returns:

        TokenPayload if valid, None if invalid

    Raises:

        JWTError: If token is malformed or signature invalid

    """

    try:

        payload = jwt.decode(

            token,

            settings.SECRET_KEY,

            algorithms=[settings.ALGORITHM],

        )

        # Extract claims

        sub: str = payload.get("sub")

        role: str = payload.get("role")

        token_type: str = payload.get("type")

        exp: int = payload.get("exp")

        # Validate required claims

        if not all([sub, role, token_type, exp]):

            return None

        # Verify token type

        if token_type != expected_type:

            return None

        # Check expiration (jose does this, but explicit check is clearer)

        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)

        if datetime.now(timezone.utc) > exp_datetime:

            return None

        return TokenPayload(

            sub=sub,

            role=role,

            token_type=token_type,

            exp=exp_datetime,

        )

    except JWTError:

        return None

## 4.5 app/core/dependencies.py

# app/core/dependencies.py

"""

=============================================================================

FastAPI Dependencies

=============================================================================

Dependencies are reusable components injected into route handlers.

They handle cross-cutting concerns like authentication.

DEPENDENCY INJECTION IN FASTAPI:

-------------------------------

Dependencies can be:

- Functions that return values

- Classes with __call__ method

- Async functions for database operations

USAGE:

    @app.get("/items")

    async def get_items(db: Session = Depends(get_db)):

        ...

"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:

    """

    Dependency that provides a database session.

    ASYNC CONTEXT MANAGER:

    - Creates session at start of request

    - Commits on success

    - Rolls back on exception

    - Closes session after request

    Yields:

        AsyncSession: SQLAlchemy async session

    """

    async with async_session_maker() as session:

        try:

            yield session

            await session.commit()

        except Exception:

            await session.rollback()

            raise

        finally:

            await session.close()

# 5. Database Layer

## 5.1 app/db/database.py

# app/db/database.py

"""

=============================================================================

Database Connection Configuration

=============================================================================

This module sets up the async SQLAlchemy 2.0 engine and session factory.

SQLALCHEMY 2.0 ASYNC CHANGES:

----------------------------

- create_async_engine instead of create_engine

- AsyncSession instead of Session

- async_sessionmaker instead of sessionmaker

- All operations must be awaited

CONNECTION POOLING:

------------------

- pool_size: Number of persistent connections

- max_overflow: Additional connections when pool is full

- pool_recycle: Recreate connections after N seconds (MySQL timeout)

- pool_pre_ping: Verify connection before use

WHY ASYNC?

---------

- Non-blocking I/O for database operations

- Better scalability under high concurrency

- Required for modern async frameworks like FastAPI

"""

from sqlalchemy.ext.asyncio import (

    create_async_engine,

    AsyncSession,

    async_sessionmaker,

)

from sqlalchemy.pool import QueuePool

from app.core.config import settings

# =============================================================================

# ASYNC ENGINE

# =============================================================================

# The engine manages the connection pool and dialects

engine = create_async_engine(

    settings.DATABASE_URL,

    # Connection Pool Configuration

    poolclass=QueuePool,

    pool_size=5,           # Base connections to maintain

    max_overflow=10,       # Extra connections when needed

    pool_recycle=3600,     # Recreate after 1 hour (MySQL wait_timeout)

    pool_pre_ping=True,    # Verify connections before use

    # Echo SQL for debugging (disable in production)

    echo=settings.DEBUG,

    # Future-proof settings

    future=True,

)

# =============================================================================

# SESSION FACTORY

# =============================================================================

# Creates new session instances with consistent configuration

async_session_maker = async_sessionmaker(

    bind=engine,

    class_=AsyncSession,

    expire_on_commit=False,  # Don't expire objects after commit

    autocommit=False,

    autoflush=False,

)

# =============================================================================

# DATABASE UTILITIES

# =============================================================================

async def get_session() -> AsyncSession:

    """

    Create a new async session.

    Use this for scripts outside of FastAPI request context.

    For request handlers, use the get_db dependency instead.

    """

    async with async_session_maker() as session:

        return session

## 5.2 app/db/base.py

# app/db/base.py

"""

=============================================================================

SQLAlchemy Base Model Configuration

=============================================================================

This module defines the base class for all ORM models.

SQLALCHEMY 2.0 DECLARATIVE BASE:

-------------------------------

- DeclarativeBase replaces declarative_base()

- Type hints with Mapped[] and mapped_column()

- Better IDE support and type checking

COMMON COLUMNS:

--------------

All models inherit common columns:

- id: Primary key

- created_at: Creation timestamp

- updated_at: Last update timestamp

"""

from datetime import datetime, timezone

from typing import Optional

from sqlalchemy import func

from sqlalchemy.orm import (

    DeclarativeBase,

    Mapped,

    mapped_column,

    declared_attr,

)

class Base(DeclarativeBase):

    """

    Base class for all SQLAlchemy models.

    SQLALCHEMY 2.0 FEATURES:

    - DeclarativeBase instead of declarative_base()

    - Mapped[T] for type hints

    - mapped_column() for column definitions

    INHERITED COLUMNS:

    - id: Auto-incrementing primary key

    - created_at: Set on insert

    - updated_at: Set on insert and update

    """

    # Generate __tablename__ automatically from class name

    @declared_attr.directive

    def __tablename__(cls) -> str:

        """

        Generate table name from class name.

        Example: UserModel -> user_model

        """

        # Convert CamelCase to snake_case

        name = cls.__name__

        return ''.join(

            ['_' + c.lower() if c.isupper() else c for c in name]

        ).lstrip('_')

    # Common columns for all models

    id: Mapped[int] = mapped_column(

        primary_key=True,

        autoincrement=True,

        index=True,

    )

    created_at: Mapped[datetime] = mapped_column(

        default=lambda: datetime.now(timezone.utc),

        server_default=func.now(),

    )

    updated_at: Mapped[datetime] = mapped_column(

        default=lambda: datetime.now(timezone.utc),

        server_default=func.now(),

        onupdate=lambda: datetime.now(timezone.utc),

    )

# 6. SQLAlchemy Models

## 6.1 app/models/user.py

# app/models/user.py

"""

=============================================================================

User Model

=============================================================================

SQLAlchemy 2.0 model for user accounts with role-based access control.

SQLALCHEMY 2.0 MAPPED COLUMN SYNTAX:

-----------------------------------

OLD (SQLAlchemy 1.x):

    email = Column(String(255), unique=True, nullable=False)

NEW (SQLAlchemy 2.0):

    email: Mapped[str] = mapped_column(String(255), unique=True)

BENEFITS:

- Type hints for IDE support

- Clearer nullable handling (Optional[T])

- Better relationship typing

"""

from datetime import datetime

from enum import Enum as PyEnum

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, Enum, ForeignKey, Text

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:

    from app.models.todo import Todo

class UserRole(str, PyEnum):

    """

    User role enumeration.

    HIERARCHY:

    SUPERADMIN > ADMIN > USER

    - SUPERADMIN: Can manage all users and admins

    - ADMIN: Can manage users, view statistics

    - USER: Can manage own todos only

    """

    USER = "user"

    ADMIN = "admin"

    SUPERADMIN = "superadmin"

    def can_manage(self, target_role: "UserRole") -> bool:

        """

        Check if this role can manage the target role.

        Rules:

        - SUPERADMIN can manage ADMIN and USER

        - ADMIN can manage USER only

        - USER can manage no one

        """

        hierarchy = {

            UserRole.SUPERADMIN: 3,

            UserRole.ADMIN: 2,

            UserRole.USER: 1,

        }

        return hierarchy[self] > hierarchy[target_role]

class User(Base):

    """

    User account model.

    COLUMNS:

    - id: Primary key (inherited from Base)

    - email: Unique email address

    - hashed_password: Bcrypt password hash

    - full_name: Display name

    - role: UserRole enum

    - is_active: Account status

    - created_by_id: Admin who created the user (nullable)

    - created_at, updated_at: Timestamps (inherited)

    RELATIONSHIPS:

    - todos: One-to-many with Todo

    - created_by: Self-referential (admin who created)

    - created_users: Users created by this admin

    """

    __tablename__ = "users"

    # Core fields

    email: Mapped[str] = mapped_column(

        String(255),

        unique=True,

        index=True,

        nullable=False,

    )

    hashed_password: Mapped[str] = mapped_column(

        String(255),

        nullable=False,

    )

    full_name: Mapped[str] = mapped_column(

        String(255),

        nullable=False,

    )

    # Role and status

    role: Mapped[UserRole] = mapped_column(

        Enum(UserRole),

        default=UserRole.USER,

        nullable=False,

    )

    is_active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False,

    )

    # Self-referential foreign key (who created this user)

    created_by_id: Mapped[Optional[int]] = mapped_column(

        ForeignKey("users.id", ondelete="SET NULL"),

        nullable=True,

    )

    # ==========================================================================

    # RELATIONSHIPS

    # ==========================================================================

    # Todos owned by this user

    todos: Mapped[List["Todo"]] = relationship(

        "Todo",

        back_populates="owner",

        lazy="selectin",  # Eager load to avoid N+1

        cascade="all, delete-orphan",

    )

    # Self-referential relationship

    created_by: Mapped[Optional["User"]] = relationship(

        "User",

        remote_side="User.id",

        foreign_keys=[created_by_id],

        lazy="selectin",

    )

    # ==========================================================================

    # METHODS

    # ==========================================================================

    def __repr__(self) -> str:

        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def is_admin_or_above(self) -> bool:

        """Check if user has admin or superadmin role."""

        return self.role in (UserRole.ADMIN, UserRole.SUPERADMIN)

    def is_superadmin(self) -> bool:

        """Check if user is superadmin."""

        return self.role == UserRole.SUPERADMIN

## 6.2 app/models/todo.py

# app/models/todo.py

"""

=============================================================================

Todo Model

=============================================================================

SQLAlchemy 2.0 model for todo items with soft delete support.

SOFT DELETE PATTERN:

-------------------

Instead of actually deleting records, we:

1. Set deleted_at timestamp

2. Optionally record who deleted and why

3. Filter out deleted items in queries

BENEFITS:

- Audit trail

- Easy recovery

- Referential integrity maintained

"""

from datetime import datetime

from enum import Enum as PyEnum

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Boolean, Enum, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:

    from app.models.user import User

class TodoPriority(str, PyEnum):

    """Todo priority levels."""

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    URGENT = "urgent"

class TodoStatus(str, PyEnum):

    """Todo completion status."""

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    COMPLETED = "completed"

    CANCELLED = "cancelled"

class Todo(Base):

    """

    Todo item model with soft delete support.

    COLUMNS:

    - id: Primary key (inherited)

    - title: Todo title

    - description: Optional detailed description

    - priority: Priority level

    - status: Completion status

    - due_date: Optional deadline

    - owner_id: User who owns this todo

    - is_completed: Quick completion flag

    - completed_at: When completed

    SOFT DELETE COLUMNS:

    - deleted_at: When deleted (null = active)

    - deleted_by_id: Admin who deleted

    - deletion_reason: Why deleted

    """

    __tablename__ = "todos"

    # Core fields

    title: Mapped[str] = mapped_column(

        String(255),

        nullable=False,

    )

    description: Mapped[Optional[str]] = mapped_column(

        Text,

        nullable=True,

    )

    priority: Mapped[TodoPriority] = mapped_column(

        Enum(TodoPriority),

        default=TodoPriority.MEDIUM,

        nullable=False,

    )

    status: Mapped[TodoStatus] = mapped_column(

        Enum(TodoStatus),

        default=TodoStatus.PENDING,

        nullable=False,

    )

    due_date: Mapped[Optional[datetime]] = mapped_column(

        DateTime(timezone=True),

        nullable=True,

    )

    # Ownership

    owner_id: Mapped[int] = mapped_column(

        ForeignKey("users.id", ondelete="CASCADE"),

        nullable=False,

        index=True,

    )

    # Completion tracking

    is_completed: Mapped[bool] = mapped_column(

        Boolean,

        default=False,

        nullable=False,

    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(

        DateTime(timezone=True),

        nullable=True,

    )

    # ==========================================================================

    # SOFT DELETE FIELDS

    # ==========================================================================

    deleted_at: Mapped[Optional[datetime]] = mapped_column(

        DateTime(timezone=True),

        nullable=True,

        index=True,  # Index for filtering active items

    )

    deleted_by_id: Mapped[Optional[int]] = mapped_column(

        ForeignKey("users.id", ondelete="SET NULL"),

        nullable=True,

    )

    deletion_reason: Mapped[Optional[str]] = mapped_column(

        Text,

        nullable=True,

    )

    # ==========================================================================

    # RELATIONSHIPS

    # ==========================================================================

    owner: Mapped["User"] = relationship(

        "User",

        back_populates="todos",

        foreign_keys=[owner_id],

        lazy="selectin",

    )

    deleted_by: Mapped[Optional["User"]] = relationship(

        "User",

        foreign_keys=[deleted_by_id],

        lazy="selectin",

    )

    # ==========================================================================

    # METHODS

    # ==========================================================================

    def __repr__(self) -> str:

        return f"<Todo(id={self.id}, title={self.title}, status={self.status})>"

    @property

    def is_deleted(self) -> bool:

        """Check if todo is soft deleted."""

        return self.deleted_at is not None

    @property

    def is_overdue(self) -> bool:

        """Check if todo is past due date."""

        if self.due_date and not self.is_completed:

            return datetime.now(self.due_date.tzinfo) > self.due_date

        return False

# 7. Repository Layer

The Repository Pattern abstracts data access logic, making it easier to test and maintain. Each repository handles CRUD operations for its model.

## 7.1 app/repositories/base.py

# app/repositories/base.py

"""

=============================================================================

Base Repository - Generic CRUD Operations

=============================================================================

This module implements the generic repository pattern for SQLAlchemy 2.0.

REPOSITORY PATTERN:

------------------

- Abstracts database operations

- Provides consistent interface for all models

- Uses generics for type safety

- Async operations throughout

SQLALCHEMY 2.0 ASYNC PATTERNS:

-----------------------------

- select() instead of query()

- session.execute() returns Result

- result.scalars() for single-column results

- result.scalar_one_or_none() for single item

"""

from typing import Generic, TypeVar, Type, Optional, List, Any

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# Type variable for generic repository

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):

    """

    Generic base repository with CRUD operations.

    USAGE:

        class UserRepository(BaseRepository[User]):

            model = User

    METHODS:

    - get(id): Get by primary key

    - get_by(filters): Get one by filters

    - get_multi(filters, skip, limit): Get many

    - create(data): Create new record

    - update(id, data): Update existing

    - delete(id): Hard delete

    - count(filters): Count records

    """

    model: Type[ModelType]

    async def get(

        self,

        session: AsyncSession,

        id: int,

    ) -> Optional[ModelType]:

        """

        Get a single record by primary key.

        SQLALCHEMY 2.0:

        - select(Model) creates SELECT statement

        - session.execute() runs the query

        - result.scalar_one_or_none() returns single item or None

        Args:

            session: Async database session

            id: Primary key value

        Returns:

            Model instance or None

        """

        stmt = select(self.model).where(self.model.id == id)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by(

        self,

        session: AsyncSession,

        **filters: Any,

    ) -> Optional[ModelType]:

        """

        Get a single record by arbitrary filters.

        Args:

            session: Async database session

            **filters: Column=value filters

        Returns:

            Model instance or None

        Example:

            user = await repo.get_by(session, email="test@example.com")

        """

        stmt = select(self.model)

        for key, value in filters.items():

            column = getattr(self.model, key, None)

            if column is not None:

                stmt = stmt.where(column == value)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_multi(

        self,

        session: AsyncSession,

        *,

        skip: int = 0,

        limit: int = 100,

        **filters: Any,

    ) -> List[ModelType]:

        """

        Get multiple records with pagination.

        Args:

            session: Async database session

            skip: Number of records to skip

            limit: Maximum records to return

            **filters: Column=value filters

        Returns:

            List of model instances

        """

        stmt = select(self.model)

        for key, value in filters.items():

            column = getattr(self.model, key, None)

            if column is not None:

                stmt = stmt.where(column == value)

        stmt = stmt.offset(skip).limit(limit)

        result = await session.execute(stmt)

        return list(result.scalars().all())

    async def create(

        self,

        session: AsyncSession,

        **data: Any,

    ) -> ModelType:

        """

        Create a new record.

        Args:

            session: Async database session

            **data: Column=value data for new record

        Returns:

            Created model instance

        """

        instance = self.model(**data)

        session.add(instance)

        await session.flush()  # Get ID without committing

        await session.refresh(instance)

        return instance

    async def update(

        self,

        session: AsyncSession,

        *,

        id: int,

        **data: Any,

    ) -> Optional[ModelType]:

        """

        Update an existing record.

        Args:

            session: Async database session

            id: Primary key of record to update

            **data: Column=value data to update

        Returns:

            Updated model instance or None if not found

        """

        instance = await self.get(session, id)

        if not instance:

            return None

        for key, value in data.items():

            if hasattr(instance, key):

                setattr(instance, key, value)

        await session.flush()

        await session.refresh(instance)

        return instance

    async def delete(

        self,

        session: AsyncSession,

        *,

        id: int,

    ) -> bool:

        """

        Hard delete a record.

        Args:

            session: Async database session

            id: Primary key of record to delete

        Returns:

            True if deleted, False if not found

        """

        instance = await self.get(session, id)

        if not instance:

            return False

        await session.delete(instance)

        await session.flush()

        return True

    async def count(

        self,

        session: AsyncSession,

        **filters: Any,

    ) -> int:

        """

        Count records matching filters.

        Args:

            session: Async database session

            **filters: Column=value filters

        Returns:

            Count of matching records

        """

        stmt = select(func.count(self.model.id))

        for key, value in filters.items():

            column = getattr(self.model, key, None)

            if column is not None:

                stmt = stmt.where(column == value)

        result = await session.execute(stmt)

        return result.scalar() or 0

## 7.2 app/repositories/user_repository.py

# app/repositories/user_repository.py

"""

=============================================================================

User Repository - User-specific Data Access

=============================================================================

Extends BaseRepository with user-specific queries and operations.

"""

from typing import Optional, List

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole

from app.repositories.base import BaseRepository

from app.core.security import get_password_hash, verify_password

class UserRepository(BaseRepository[User]):

    """

    Repository for User model operations.

    ADDITIONAL METHODS:

    - get_by_email: Find user by email

    - authenticate: Verify credentials

    - create_user: Create with password hashing

    - get_users_by_role: Filter by role

    - get_user_statistics: Aggregate stats

    """

    model = User

    async def get_by_email(

        self,

        session: AsyncSession,

        email: str,

    ) -> Optional[User]:

        """

        Get user by email address.

        Args:

            session: Database session

            email: Email to search

        Returns:

            User or None

        """

        stmt = select(User).where(User.email == email)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def authenticate(

        self,

        session: AsyncSession,

        email: str,

        password: str,

    ) -> Optional[User]:

        """

        Authenticate user by email and password.

        Args:

            session: Database session

            email: User email

            password: Plain text password

        Returns:

            User if authenticated, None otherwise

        """

        user = await self.get_by_email(session, email)

        if not user:

            return None

        if not user.is_active:

            return None

        if not verify_password(password, user.hashed_password):

            return None

        return user

    async def create_user(

        self,

        session: AsyncSession,

        *,

        email: str,

        password: str,

        full_name: str,

        role: UserRole = UserRole.USER,

        created_by_id: Optional[int] = None,

    ) -> User:

        """

        Create a new user with hashed password.

        Args:

            session: Database session

            email: User email

            password: Plain text password (will be hashed)

            full_name: Display name

            role: User role

            created_by_id: ID of admin who created this user

        Returns:

            Created User instance

        """

        hashed_password = get_password_hash(password)

        return await self.create(

            session,

            email=email,

            hashed_password=hashed_password,

            full_name=full_name,

            role=role,

            created_by_id=created_by_id,

        )

    async def get_users_by_role(

        self,

        session: AsyncSession,

        role: UserRole,

        *,

        skip: int = 0,

        limit: int = 100,

        active_only: bool = True,

    ) -> List[User]:

        """

        Get users filtered by role.

        Args:

            session: Database session

            role: Role to filter by

            skip: Pagination offset

            limit: Max results

            active_only: Only return active users

        Returns:

            List of matching users

        """

        stmt = select(User).where(User.role == role)

        if active_only:

            stmt = stmt.where(User.is_active == True)

        stmt = stmt.offset(skip).limit(limit)

        result = await session.execute(stmt)

        return list(result.scalars().all())

    async def get_user_statistics(

        self,

        session: AsyncSession,

    ) -> dict:

        """

        Get aggregate user statistics.

        Returns:

            Dict with user counts by role and status

        """

        # Total users

        total_stmt = select(func.count(User.id))

        total_result = await session.execute(total_stmt)

        total = total_result.scalar() or 0

        # Active users

        active_stmt = select(func.count(User.id)).where(User.is_active == True)

        active_result = await session.execute(active_stmt)

        active = active_result.scalar() or 0

        # Users by role

        role_counts = {}

        for role in UserRole:

            role_stmt = select(func.count(User.id)).where(User.role == role)

            role_result = await session.execute(role_stmt)

            role_counts[role.value] = role_result.scalar() or 0

        return {

            "total_users": total,

            "active_users": active,

            "inactive_users": total - active,

            "users_by_role": role_counts,

        }

## 7.3 app/repositories/todo_repository.py

# app/repositories/todo_repository.py

"""

=============================================================================

Todo Repository - Todo-specific Data Access

=============================================================================

Extends BaseRepository with todo-specific queries including soft delete.

"""

from datetime import datetime, timezone

from typing import Optional, List

from sqlalchemy import select, func, and_

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo, TodoPriority, TodoStatus

from app.repositories.base import BaseRepository

class TodoRepository(BaseRepository[Todo]):

    """

    Repository for Todo model operations.

    SOFT DELETE:

    - All queries filter out deleted items by default

    - soft_delete() marks as deleted without removing

    - Hard delete still available via base delete()

    ADDITIONAL METHODS:

    - get_user_todos: Get todos for a user

    - create_todo: Create with owner

    - soft_delete: Soft delete with reason

    - get_statistics: Todo stats for admin dashboard

    """

    model = Todo

    async def get_active(

        self,

        session: AsyncSession,

        id: int,

    ) -> Optional[Todo]:

        """

        Get non-deleted todo by ID.

        Args:

            session: Database session

            id: Todo ID

        Returns:

            Todo if exists and not deleted

        """

        stmt = select(Todo).where(

            and_(

                Todo.id == id,

                Todo.deleted_at.is_(None),

            )

        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_todos(

        self,

        session: AsyncSession,

        owner_id: int,

        *,

        include_deleted: bool = False,

        status: Optional[TodoStatus] = None,

        priority: Optional[TodoPriority] = None,

        skip: int = 0,

        limit: int = 100,

    ) -> List[Todo]:

        """

        Get todos for a specific user.

        Args:

            session: Database session

            owner_id: User ID

            include_deleted: Include soft-deleted items

            status: Filter by status

            priority: Filter by priority

            skip: Pagination offset

            limit: Max results

        Returns:

            List of todos

        """

        stmt = select(Todo).where(Todo.owner_id == owner_id)

        if not include_deleted:

            stmt = stmt.where(Todo.deleted_at.is_(None))

        if status:

            stmt = stmt.where(Todo.status == status)

        if priority:

            stmt = stmt.where(Todo.priority == priority)

        stmt = stmt.order_by(Todo.created_at.desc())

        stmt = stmt.offset(skip).limit(limit)

        result = await session.execute(stmt)

        return list(result.scalars().all())

    async def create_todo(

        self,

        session: AsyncSession,

        *,

        owner_id: int,

        title: str,

        description: Optional[str] = None,

        priority: TodoPriority = TodoPriority.MEDIUM,

        due_date: Optional[datetime] = None,

    ) -> Todo:

        """

        Create a new todo.

        Args:

            session: Database session

            owner_id: User ID

            title: Todo title

            description: Optional description

            priority: Priority level

            due_date: Optional deadline

        Returns:

            Created Todo

        """

        return await self.create(

            session,

            owner_id=owner_id,

            title=title,

            description=description,

            priority=priority,

            due_date=due_date,

        )

    async def soft_delete(

        self,

        session: AsyncSession,

        *,

        id: int,

        deleted_by_id: int,

        reason: Optional[str] = None,

    ) -> Optional[Todo]:

        """

        Soft delete a todo.

        SOFT DELETE vs HARD DELETE:

        - Soft: Sets deleted_at timestamp, keeps record

        - Hard: Removes record from database

        Args:

            session: Database session

            id: Todo ID

            deleted_by_id: User performing delete

            reason: Optional deletion reason

        Returns:

            Updated Todo or None if not found

        """

        todo = await self.get_active(session, id)

        if not todo:

            return None

        todo.deleted_at = datetime.now(timezone.utc)

        todo.deleted_by_id = deleted_by_id

        todo.deletion_reason = reason

        await session.flush()

        await session.refresh(todo)

        return todo

    async def complete_todo(

        self,

        session: AsyncSession,

        id: int,

    ) -> Optional[Todo]:

        """

        Mark a todo as completed.

        Args:

            session: Database session

            id: Todo ID

        Returns:

            Updated Todo or None

        """

        todo = await self.get_active(session, id)

        if not todo:

            return None

        todo.is_completed = True

        todo.completed_at = datetime.now(timezone.utc)

        todo.status = TodoStatus.COMPLETED

        await session.flush()

        await session.refresh(todo)

        return todo

    async def get_statistics(

        self,

        session: AsyncSession,

        owner_id: Optional[int] = None,

    ) -> dict:

        """

        Get todo statistics.

        Args:

            session: Database session

            owner_id: Optional user ID for user-specific stats

        Returns:

            Dict with todo counts and statistics

        """

        base_condition = Todo.deleted_at.is_(None)

        if owner_id:

            base_condition = and_(base_condition, Todo.owner_id == owner_id)

        # Total active todos

        total_stmt = select(func.count(Todo.id)).where(base_condition)

        total_result = await session.execute(total_stmt)

        total = total_result.scalar() or 0

        # Completed todos

        completed_stmt = select(func.count(Todo.id)).where(

            and_(base_condition, Todo.is_completed == True)

        )

        completed_result = await session.execute(completed_stmt)

        completed = completed_result.scalar() or 0

        # By status

        status_counts = {}

        for status in TodoStatus:

            status_stmt = select(func.count(Todo.id)).where(

                and_(base_condition, Todo.status == status)

            )

            status_result = await session.execute(status_stmt)

            status_counts[status.value] = status_result.scalar() or 0

        # By priority

        priority_counts = {}

        for priority in TodoPriority:

            priority_stmt = select(func.count(Todo.id)).where(

                and_(base_condition, Todo.priority == priority)

            )

            priority_result = await session.execute(priority_stmt)

            priority_counts[priority.value] = priority_result.scalar() or 0

        # Overdue todos

        now = datetime.now(timezone.utc)

        overdue_stmt = select(func.count(Todo.id)).where(

            and_(

                base_condition,

                Todo.is_completed == False,

                Todo.due_date < now,

            )

        )

        overdue_result = await session.execute(overdue_stmt)

        overdue = overdue_result.scalar() or 0

        return {

            "total_todos": total,

            "completed_todos": completed,

            "pending_todos": total - completed,

            "overdue_todos": overdue,

            "completion_rate": (completed / total * 100) if total > 0 else 0,

            "by_status": status_counts,

            "by_priority": priority_counts,

        }

# 8. GraphQL Layer

## 8.1 app/graphql/context.py

# app/graphql/context.py

"""

=============================================================================

GraphQL Context

=============================================================================

Context is shared data available to all resolvers.

GRAPHQL CONTEXT EXPLAINED:

-------------------------

Context provides request-scoped data:

- Current user (from JWT)

- Database session

- Request metadata

Every resolver receives 'info' parameter with:

- info.context: The context object

- info.field_name: Name of the field being resolved

- info.return_type: Expected return type

"""

from typing import Optional, Any

from fastapi import Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker

from app.models.user import User

from app.core.security import decode_token

from app.repositories import user_repository

async def get_context(request: Request) -> dict[str, Any]:

    """

    Create GraphQL context for each request.

    CONTEXT CONTENTS:

    - request: FastAPI request object

    - session: Database session

    - current_user: Authenticated user or None

    AUTHENTICATION FLOW:

    1. Extract token from Authorization header

    2. Decode and validate JWT

    3. Fetch user from database

    4. Add to context

    Returns:

        Dict with context values

    """

    # Create database session

    session = async_session_maker()

    # Extract current user from JWT

    current_user = await get_current_user_from_request(request, session)

    return {

        "request": request,

        "session": session,

        "current_user": current_user,

    }

async def get_current_user_from_request(

    request: Request,

    session: AsyncSession,

) -> Optional[User]:

    """

    Extract and validate user from request.

    TOKEN EXTRACTION:

    Looks for: Authorization: Bearer <token>

    Args:

        request: FastAPI request

        session: Database session

    Returns:

        User if authenticated, None otherwise

    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:

        return None

    # Expected format: "Bearer <token>"

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":

        return None

    token = parts[1]

    # Decode token

    payload = decode_token(token, expected_type="access")

    if not payload:

        return None

    # Fetch user

    user_id = int(payload.sub)

    user = await user_repository.get(session, user_id)

    if not user or not user.is_active:

        return None

    return user

## 8.2 app/graphql/permissions.py

# app/graphql/permissions.py

"""

=============================================================================

GraphQL Permission Classes

=============================================================================

Strawberry uses permission classes for authorization.

PERMISSION CLASS PATTERN:

------------------------

- Inherit from BasePermission

- Implement has_permission method

- Return True to allow, False to deny

- Raise exception for custom error messages

USAGE:

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsAdmin])

    def admin_action(self) -> str:

        ...

"""

from typing import Any

import strawberry

from strawberry.permission import BasePermission

from strawberry.types import Info

from app.models.user import UserRole

class IsAuthenticated(BasePermission):

    """

    Permission: User must be logged in.

    STRAWBERRY PERMISSION:

    - has_permission() called before resolver

    - info.context contains request context

    - Return False = PermissionError raised

    """

    message = "Authentication required"

    async def has_permission(

        self,

        source: Any,

        info: Info,

        **kwargs: Any,

    ) -> bool:

        """

        Check if user is authenticated.

        Args:

            source: Parent object (for nested resolvers)

            info: Strawberry Info with context

            **kwargs: Resolver arguments

        Returns:

            True if authenticated

        """

        return info.context.get("current_user") is not None

class IsAdmin(BasePermission):

    """

    Permission: User must be admin or superadmin.

    """

    message = "Admin access required"

    async def has_permission(

        self,

        source: Any,

        info: Info,

        **kwargs: Any,

    ) -> bool:

        """Check if user has admin role."""

        user = info.context.get("current_user")

        if not user:

            return False

        return user.role in (UserRole.ADMIN, UserRole.SUPERADMIN)

class IsSuperAdmin(BasePermission):

    """

    Permission: User must be superadmin.

    """

    message = "Superadmin access required"

    async def has_permission(

        self,

        source: Any,

        info: Info,

        **kwargs: Any,

    ) -> bool:

        """Check if user is superadmin."""

        user = info.context.get("current_user")

        if not user:

            return False

        return user.role == UserRole.SUPERADMIN

class IsOwnerOrAdmin(BasePermission):

    """

    Permission: User must own the resource OR be admin.

    Used for operations where users can modify their own data,

    or admins can modify any data.

    """

    message = "You don't have permission to access this resource"

    async def has_permission(

        self,

        source: Any,

        info: Info,

        **kwargs: Any,

    ) -> bool:

        """

        Check ownership or admin status.

        NOTE: This is a basic check. For specific resources,

        the resolver should verify ownership.

        """

        user = info.context.get("current_user")

        if not user:

            return False

        # Admins always have access

        if user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):

            return True

        # For non-admins, we return True here and let

        # the resolver verify specific ownership

        return True

## 8.3 GraphQL Types

### 8.3.1 app/graphql/types/user_types.py

# app/graphql/types/user_types.py

"""

=============================================================================

User GraphQL Types

=============================================================================

STRAWBERRY TYPE DECORATORS:

--------------------------

@strawberry.type - Defines a GraphQL object type

@strawberry.enum - Defines a GraphQL enum

@strawberry.field - Defines a computed/resolver field

GRAPHQL NAMING CONVENTION:

-------------------------

Python: snake_case -> GraphQL: camelCase (automatic conversion)

full_name -> fullName

"""

from datetime import datetime

from enum import Enum

from typing import Optional, List, TYPE_CHECKING

import strawberry

from strawberry import Private

if TYPE_CHECKING:

    from app.graphql.types.todo_types import TodoType

@strawberry.enum(description="User roles for access control")

class UserRoleEnum(Enum):

    """

    GraphQL enum for user roles.

    GRAPHQL OUTPUT:

    enum UserRoleEnum {

        USER

        ADMIN

        SUPERADMIN

    }

    """

    USER = "user"

    ADMIN = "admin"

    SUPERADMIN = "superadmin"

@strawberry.type(description="User account information")

class UserType:

    """

    GraphQL type representing a user.

    FIELD TYPES:

    - Scalar: int, str, bool, datetime

    - Enum: UserRoleEnum

    - Object: TodoType (nested)

    - List: List[TodoType]

    NON-NULL vs NULLABLE:

    - int (non-null) -> Int!

    - Optional[int] (nullable) -> Int

    """

    id: int

    email: str

    full_name: str

    role: UserRoleEnum

    is_active: bool

    created_at: datetime

    updated_at: datetime

    created_by_id: Optional[int] = None

    # Private field - not exposed in GraphQL schema

    # Useful for passing data between resolvers

    _db_user: Private[object] = None

    @strawberry.field(description="Number of todos for this user")

    async def todo_count(self, info: strawberry.Info) -> int:

        """

        Computed field for todo count.

        RESOLVER PATTERN:

        - Method decorated with @strawberry.field

        - Can be sync or async

        - Has access to info.context

        """

        from app.repositories import todo_repository

        session = info.context["session"]

        return await todo_repository.count(

            session,

            owner_id=self.id,

            deleted_at=None,  # Only active todos

        )

@strawberry.type(description="JWT token pair")

class TokenPair:

    """

    Access and refresh token response.

    USED BY:

    - login mutation

    - signup mutation

    - refreshToken mutation

    """

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

@strawberry.type(description="Authentication response with user and tokens")

class AuthPayload:

    """

    Complete authentication response.

    Returns both the user data and authentication tokens.

    """

    user: UserType

    tokens: TokenPair

### 8.3.2 app/graphql/types/todo_types.py

# app/graphql/types/todo_types.py

"""

=============================================================================

Todo GraphQL Types

=============================================================================

"""

from datetime import datetime

from enum import Enum

from typing import Optional

import strawberry

from strawberry import Private

@strawberry.enum(description="Todo priority levels")

class TodoPriorityEnum(Enum):

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    URGENT = "urgent"

@strawberry.enum(description="Todo status options")

class TodoStatusEnum(Enum):

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    COMPLETED = "completed"

    CANCELLED = "cancelled"

@strawberry.type(description="Todo item")

class TodoType:

    """

    GraphQL type representing a todo.

    SOFT DELETE FIELDS:

    - deleted_at: When deleted (null = active)

    - deleted_by_id: Admin who deleted

    - deletion_reason: Why deleted

    These fields may be null/hidden based on permissions.

    """

    id: int

    title: str

    description: Optional[str] = None

    priority: TodoPriorityEnum

    status: TodoStatusEnum

    due_date: Optional[datetime] = None

    is_completed: bool

    completed_at: Optional[datetime] = None

    owner_id: int

    created_at: datetime

    updated_at: datetime

    # Soft delete fields

    deleted_at: Optional[datetime] = None

    deleted_by_id: Optional[int] = None

    deletion_reason: Optional[str] = None

    # Private reference to DB model

    _db_todo: Private[object] = None

    @strawberry.field(description="Check if todo is overdue")

    def is_overdue(self) -> bool:

        """Computed field for overdue status."""

        if self.due_date and not self.is_completed:

            return datetime.now(self.due_date.tzinfo) > self.due_date

        return False

    @strawberry.field(description="Check if todo is deleted")

    def is_deleted(self) -> bool:

        """Computed field for deleted status."""

        return self.deleted_at is not None

### 8.3.3 app/graphql/types/common_types.py

# app/graphql/types/common_types.py

"""

=============================================================================

Common GraphQL Types

=============================================================================

Shared types used across queries and mutations.

"""

from typing import Optional, Dict, Any

import strawberry

@strawberry.type(description="Generic operation result")

class OperationResult:

    """

    Standard response for operations without specific return data.

    USAGE:

    - Delete operations

    - Bulk operations

    - Status updates

    """

    success: bool

    message: str

@strawberry.type(description="Pagination information")

class PaginationInfo:

    """

    Pagination metadata for list queries.

    CURSOR-BASED vs OFFSET-BASED:

    This uses offset-based (skip/limit) for simplicity.

    For large datasets, consider cursor-based pagination.

    """

    total: int

    skip: int

    limit: int

    has_next: bool

    has_previous: bool

@strawberry.type(description="User statistics for admin dashboard")

class UserStatistics:

    """Aggregate statistics about users."""

    total_users: int

    active_users: int

    inactive_users: int

    users_by_role: str  # JSON string of role counts

    @strawberry.field

    def admins_count(self) -> int:

        """Number of admin users."""

        import json

        roles = json.loads(self.users_by_role)

        return roles.get("admin", 0)

    @strawberry.field

    def superadmins_count(self) -> int:

        """Number of superadmin users."""

        import json

        roles = json.loads(self.users_by_role)

        return roles.get("superadmin", 0)

@strawberry.type(description="Todo statistics")

class TodoStatistics:

    """Aggregate statistics about todos."""

    total_todos: int

    completed_todos: int

    pending_todos: int

    overdue_todos: int

    completion_rate: float

    by_status: str  # JSON string

    by_priority: str  # JSON string

## 8.4 GraphQL Inputs

### 8.4.1 app/graphql/inputs/user_inputs.py

# app/graphql/inputs/user_inputs.py

"""

=============================================================================

User GraphQL Input Types

=============================================================================

INPUT TYPE DECORATOR:

--------------------

@strawberry.input - Defines a GraphQL input type

INPUT vs TYPE:

- input SignupInput { ... }  -> For mutations (client sends)

- type UserType { ... }      -> For queries (server returns)

"""

from typing import Optional

import strawberry

from app.graphql.types.user_types import UserRoleEnum

@strawberry.input(description="User signup data")

class SignupInput:

    """

    Input for user self-registration.

    GRAPHQL INPUT:

    input SignupInput {

        email: String!

        password: String!

        fullName: String!

    }

    """

    email: str

    password: str

    full_name: str

@strawberry.input(description="Login credentials")

class LoginInput:

    """Input for authentication."""

    email: str

    password: str

@strawberry.input(description="Admin user creation")

class CreateUserInput:

    """

    Input for admin creating a new user.

    Includes role field that regular signup doesn't have.

    """

    email: str

    password: str

    full_name: str

    role: UserRoleEnum = UserRoleEnum.USER

@strawberry.input(description="User update data")

class UpdateUserInput:

    """

    Input for updating user profile.

    All fields optional for partial updates.

    OPTIONAL FIELDS:

    Using Optional[T] makes field nullable in GraphQL.

    Missing fields won't update the database value.

    """

    full_name: Optional[str] = None

    email: Optional[str] = None

    is_active: Optional[bool] = None

    role: Optional[UserRoleEnum] = None

### 8.4.2 app/graphql/inputs/todo_inputs.py

# app/graphql/inputs/todo_inputs.py

"""

=============================================================================

Todo GraphQL Input Types

=============================================================================

"""

from datetime import datetime

from typing import Optional

import strawberry

from app.graphql.types.todo_types import TodoPriorityEnum, TodoStatusEnum

@strawberry.input(description="Create todo data")

class CreateTodoInput:

    """Input for creating a new todo."""

    title: str

    description: Optional[str] = None

    priority: TodoPriorityEnum = TodoPriorityEnum.MEDIUM

    due_date: Optional[datetime] = None

@strawberry.input(description="Update todo data")

class UpdateTodoInput:

    """

    Input for updating a todo.

    All fields optional for partial updates.

    """

    title: Optional[str] = None

    description: Optional[str] = None

    priority: Optional[TodoPriorityEnum] = None

    status: Optional[TodoStatusEnum] = None

    due_date: Optional[datetime] = None

    is_completed: Optional[bool] = None

@strawberry.input(description="Delete todo with reason")

class DeleteTodoInput:

    """

    Input for admin deleting user's todo.

    Requires reason for audit trail.

    """

    todo_id: int

    reason: str

## 8.5 GraphQL Resolvers

### 8.5.1 app/graphql/resolvers/user_resolvers.py

# app/graphql/resolvers/user_resolvers.py

"""

=============================================================================

User Resolvers - Queries and Mutations

=============================================================================

This module contains all user-related GraphQL operations.

STRAWBERRY RESOLVER PATTERN:

---------------------------

1. Define class with @strawberry.type

2. Add methods with @strawberry.field (queries) or @strawberry.mutation

3. Methods can be sync or async

4. info.context provides request context

"""

from typing import List, Optional

import json

import strawberry

from strawberry.types import Info

from app.models.user import User, UserRole

from app.repositories import user_repository

from app.core.security import create_access_token, create_refresh_token, decode_token

from app.graphql.types import (

    UserType,

    UserRoleEnum,

    AuthPayload,

    TokenPair,

    OperationResult,

    UserStatistics,

)

from app.graphql.inputs import (

    SignupInput,

    LoginInput,

    CreateUserInput,

    UpdateUserInput,

)

from app.graphql.permissions import IsAuthenticated, IsAdmin, IsSuperAdmin

# =============================================================================

# HELPER FUNCTIONS

# =============================================================================

def user_to_type(user: User) -> UserType:

    """

    Convert SQLAlchemy User model to GraphQL UserType.

    WHY CONVERTER?

    - Decouples database model from GraphQL type

    - Allows transformation/filtering of data

    - Handles enum conversion

    """

    return UserType(

        id=user.id,

        email=user.email,

        full_name=user.full_name,

        role=UserRoleEnum(user.role.value),

        is_active=user.is_active,

        created_at=user.created_at,

        updated_at=user.updated_at,

        created_by_id=user.created_by_id,

        _db_user=user,

    )

def create_tokens_for_user(user: User) -> TokenPair:

    """Create JWT token pair for user."""

    token_data = {

        "sub": str(user.id),

        "role": user.role.value,

    }

    return TokenPair(

        access_token=create_access_token(token_data),

        refresh_token=create_refresh_token(token_data),

    )

# =============================================================================

# QUERIES

# =============================================================================

@strawberry.type

class Query:

    """

    User queries.

    QUERY EXAMPLES:

    # Get current user

    query {

        me {

            id

            email

            fullName

            role

        }

    }

    # Get all users (admin)

    query {

        users {

            id

            email

            role

        }

    }

    # Get user by ID (admin)

    query {

        user(id: 1) {

            id

            email

            fullName

        }

    }

    """

    @strawberry.field(

        description="Get current authenticated user",

        permission_classes=[IsAuthenticated],

    )

    async def me(self, info: Info) -> UserType:

        """

        Get the current authenticated user.

        AUTHENTICATION:

        - Requires valid JWT in Authorization header

        - User extracted in context.get_current_user_from_request

        """

        current_user = info.context["current_user"]

        return user_to_type(current_user)

    @strawberry.field(

        description="Get all users (admin only)",

        permission_classes=[IsAdmin],

    )

    async def users(

        self,

        info: Info,

        skip: int = 0,

        limit: int = 100,

        role: Optional[UserRoleEnum] = None,

    ) -> List[UserType]:

        """

        Get all users with optional filtering.

        AUTHORIZATION:

        - Admin: Can see users

        - Superadmin: Can see all users including admins

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        filters = {}

        # Admins can only see users, not other admins

        if current_user.role == UserRole.ADMIN:

            filters["role"] = UserRole.USER

        elif role:

            filters["role"] = UserRole(role.value)

        users = await user_repository.get_multi(

            session,

            skip=skip,

            limit=limit,

            **filters,

        )

        return [user_to_type(u) for u in users]

    @strawberry.field(

        description="Get user by ID (admin only)",

        permission_classes=[IsAdmin],

    )

    async def user(self, info: Info, id: int) -> Optional[UserType]:

        """Get a specific user by ID."""

        session = info.context["session"]

        user = await user_repository.get(session, id)

        if not user:

            return None

        return user_to_type(user)

    @strawberry.field(

        description="Get user statistics (admin only)",

        permission_classes=[IsAdmin],

    )

    async def user_statistics(self, info: Info) -> UserStatistics:

        """Get aggregate user statistics."""

        session = info.context["session"]

        stats = await user_repository.get_user_statistics(session)

        return UserStatistics(

            total_users=stats["total_users"],

            active_users=stats["active_users"],

            inactive_users=stats["inactive_users"],

            users_by_role=json.dumps(stats["users_by_role"]),

        )

# =============================================================================

# MUTATIONS

# =============================================================================

@strawberry.type

class Mutation:

    """

    User mutations.

    MUTATION EXAMPLES:

    # Signup

    mutation {

        signup(input: {

            email: "user@example.com"

            password: "Password123!"

            fullName: "John Doe"

        }) {

            user { id email }

            tokens { accessToken refreshToken }

        }

    }

    # Login

    mutation {

        login(input: {

            email: "user@example.com"

            password: "Password123!"

        }) {

            user { id }

            tokens { accessToken }

        }

    }

    """

    @strawberry.mutation(description="Register a new user account")

    async def signup(self, info: Info, input: SignupInput) -> AuthPayload:

        """

        User self-registration.

        FLOW:

        1. Check email not already taken

        2. Create user with hashed password

        3. Generate JWT tokens

        4. Return user + tokens

        """

        session = info.context["session"]

        # Check existing email

        existing = await user_repository.get_by_email(session, input.email)

        if existing:

            raise Exception("Email already registered")

        # Create user

        user = await user_repository.create_user(

            session,

            email=input.email,

            password=input.password,

            full_name=input.full_name,

            role=UserRole.USER,

        )

        # Generate tokens

        tokens = create_tokens_for_user(user)

        return AuthPayload(

            user=user_to_type(user),

            tokens=tokens,

        )

    @strawberry.mutation(description="Authenticate and get tokens")

    async def login(self, info: Info, input: LoginInput) -> AuthPayload:

        """

        User authentication.

        SECURITY:

        - Verifies email exists

        - Checks password hash

        - Verifies account active

        - Returns tokens on success

        """

        session = info.context["session"]

        user = await user_repository.authenticate(

            session,

            email=input.email,

            password=input.password,

        )

        if not user:

            raise Exception("Invalid email or password")

        tokens = create_tokens_for_user(user)

        return AuthPayload(

            user=user_to_type(user),

            tokens=tokens,

        )

    @strawberry.mutation(description="Get new access token using refresh token")

    async def refresh_token(self, info: Info, refresh_token: str) -> TokenPair:

        """

        Refresh access token.

        TOKEN REFRESH FLOW:

        1. Validate refresh token

        2. Check user still active

        3. Generate new token pair

        WHY NEW REFRESH TOKEN?

        - Rotation prevents token reuse

        - Limits window of compromise

        """

        session = info.context["session"]

        # Decode refresh token

        payload = decode_token(refresh_token, expected_type="refresh")

        if not payload:

            raise Exception("Invalid or expired refresh token")

        # Get user

        user_id = int(payload.sub)

        user = await user_repository.get(session, user_id)

        if not user or not user.is_active:

            raise Exception("User not found or inactive")

        # Generate new tokens

        return create_tokens_for_user(user)

    @strawberry.mutation(

        description="Create user (admin only)",

        permission_classes=[IsAdmin],

    )

    async def create_user(

        self,

        info: Info,

        input: CreateUserInput,

    ) -> UserType:

        """

        Admin creates a new user.

        ROLE HIERARCHY:

        - Admin can create USER only

        - Superadmin can create USER or ADMIN

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        # Check existing email

        existing = await user_repository.get_by_email(session, input.email)

        if existing:

            raise Exception("Email already registered")

        # Role permission check

        target_role = UserRole(input.role.value)

        current_role = UserRole(current_user.role.value)

        if target_role == UserRole.SUPERADMIN:

            raise Exception("Cannot create superadmin accounts")

        if target_role == UserRole.ADMIN and current_role != UserRole.SUPERADMIN:

            raise Exception("Only superadmin can create admin accounts")

        # Create user

        user = await user_repository.create_user(

            session,

            email=input.email,

            password=input.password,

            full_name=input.full_name,

            role=target_role,

            created_by_id=current_user.id,

        )

        return user_to_type(user)

    @strawberry.mutation(

        description="Update user (self or admin)",

        permission_classes=[IsAuthenticated],

    )

    async def update_user(

        self,

        info: Info,

        id: int,

        input: UpdateUserInput,

    ) -> UserType:

        """

        Update user profile.

        PERMISSIONS:

        - Users can update own profile (limited fields)

        - Admins can update users

        - Superadmins can update anyone

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        # Get target user

        user = await user_repository.get(session, id)

        if not user:

            raise Exception("User not found")

        # Permission check

        is_self = current_user.id == id

        is_admin = current_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN)

        if not is_self and not is_admin:

            raise Exception("Permission denied")

        # Regular users can only update certain fields

        update_data = {}

        if input.full_name is not None:

            update_data["full_name"] = input.full_name

        if input.email is not None:

            # Check email not taken

            existing = await user_repository.get_by_email(session, input.email)

            if existing and existing.id != id:

                raise Exception("Email already taken")

            update_data["email"] = input.email

        # Admin-only fields

        if is_admin and not is_self:

            if input.is_active is not None:

                update_data["is_active"] = input.is_active

            if input.role is not None:

                target_role = UserRole(input.role.value)

                current_role = UserRole(current_user.role.value)

                if not current_role.can_manage(target_role):

                    raise Exception("Cannot assign this role")

                update_data["role"] = target_role

        # Update

        updated_user = await user_repository.update(

            session,

            id=id,

            **update_data,

        )

        return user_to_type(updated_user)

    @strawberry.mutation(

        description="Delete user (admin only)",

        permission_classes=[IsAdmin],

    )

    async def delete_user(self, info: Info, id: int) -> OperationResult:

        """

        Delete a user account.

        RULES:

        - Cannot delete yourself

        - Cannot delete higher role

        - Hard delete (removes from database)

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        if id == current_user.id:

            raise Exception("Cannot delete yourself")

        user = await user_repository.get(session, id)

        if not user:

            raise Exception("User not found")

        # Role check

        current_role = UserRole(current_user.role.value)

        target_role = UserRole(user.role.value)

        if not current_role.can_manage(target_role):

            raise Exception("Cannot delete user with equal or higher role")

        await user_repository.delete(session, id=id)

        return OperationResult(

            success=True,

            message=f"User {user.email} deleted successfully",

        )

### 8.5.2 app/graphql/resolvers/todo_resolvers.py

# app/graphql/resolvers/todo_resolvers.py

"""

=============================================================================

Todo Resolvers - Queries and Mutations

=============================================================================

"""

from typing import List, Optional

import json

import strawberry

from strawberry.types import Info

from app.models.todo import Todo, TodoPriority, TodoStatus

from app.models.user import UserRole

from app.repositories import todo_repository

from app.graphql.types import (

    TodoType,

    TodoPriorityEnum,

    TodoStatusEnum,

    OperationResult,

    TodoStatistics,

)

from app.graphql.inputs import (

    CreateTodoInput,

    UpdateTodoInput,

    DeleteTodoInput,

)

from app.graphql.permissions import IsAuthenticated, IsAdmin

# =============================================================================

# HELPER FUNCTIONS

# =============================================================================

def todo_to_type(todo: Todo) -> TodoType:

    """Convert SQLAlchemy Todo to GraphQL TodoType."""

    return TodoType(

        id=todo.id,

        title=todo.title,

        description=todo.description,

        priority=TodoPriorityEnum(todo.priority.value),

        status=TodoStatusEnum(todo.status.value),

        due_date=todo.due_date,

        is_completed=todo.is_completed,

        completed_at=todo.completed_at,

        owner_id=todo.owner_id,

        created_at=todo.created_at,

        updated_at=todo.updated_at,

        deleted_at=todo.deleted_at,

        deleted_by_id=todo.deleted_by_id,

        deletion_reason=todo.deletion_reason,

        _db_todo=todo,

    )

# =============================================================================

# QUERIES

# =============================================================================

@strawberry.type

class Query:

    """

    Todo queries.

    QUERY EXAMPLES:

    # Get my todos

    query {

        myTodos {

            id

            title

            status

            priority

        }

    }

    # Get all todos (admin)

    query {

        allTodos(userId: 1) {

            id

            title

            owner { email }

        }

    }

    """

    @strawberry.field(

        description="Get current user's todos",

        permission_classes=[IsAuthenticated],

    )

    async def my_todos(

        self,

        info: Info,

        status: Optional[TodoStatusEnum] = None,

        priority: Optional[TodoPriorityEnum] = None,

        skip: int = 0,

        limit: int = 100,

    ) -> List[TodoType]:

        """Get todos for the authenticated user."""

        session = info.context["session"]

        current_user = info.context["current_user"]

        status_filter = TodoStatus(status.value) if status else None

        priority_filter = TodoPriority(priority.value) if priority else None

        todos = await todo_repository.get_user_todos(

            session,

            owner_id=current_user.id,

            status=status_filter,

            priority=priority_filter,

            skip=skip,

            limit=limit,

        )

        return [todo_to_type(t) for t in todos]

    @strawberry.field(

        description="Get a specific todo by ID",

        permission_classes=[IsAuthenticated],

    )

    async def todo(self, info: Info, id: int) -> Optional[TodoType]:

        """Get todo by ID (owner or admin only)."""

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.get_active(session, id)

        if not todo:

            return None

        # Permission check

        is_owner = todo.owner_id == current_user.id

        is_admin = current_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN)

        if not is_owner and not is_admin:

            raise Exception("Permission denied")

        return todo_to_type(todo)

    @strawberry.field(

        description="Get all todos (admin only)",

        permission_classes=[IsAdmin],

    )

    async def all_todos(

        self,

        info: Info,

        user_id: Optional[int] = None,

        include_deleted: bool = False,

        skip: int = 0,

        limit: int = 100,

    ) -> List[TodoType]:

        """

        Get all todos with optional filtering.

        Admin-only endpoint for viewing any user's todos.

        """

        session = info.context["session"]

        if user_id:

            todos = await todo_repository.get_user_todos(

                session,

                owner_id=user_id,

                include_deleted=include_deleted,

                skip=skip,

                limit=limit,

            )

        else:

            todos = await todo_repository.get_multi(

                session,

                skip=skip,

                limit=limit,

            )

        return [todo_to_type(t) for t in todos]

    @strawberry.field(

        description="Get todo statistics",

        permission_classes=[IsAuthenticated],

    )

    async def todo_statistics(

        self,

        info: Info,

        user_id: Optional[int] = None,

    ) -> TodoStatistics:

        """

        Get todo statistics.

        - Regular users: Can only get own stats

        - Admins: Can get any user's stats or overall

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        # Permission check

        if user_id and user_id != current_user.id:

            if current_user.role not in (UserRole.ADMIN, UserRole.SUPERADMIN):

                raise Exception("Permission denied")

        # Default to current user for non-admins

        target_user_id = user_id

        if not current_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):

            target_user_id = current_user.id

        stats = await todo_repository.get_statistics(session, owner_id=target_user_id)

        return TodoStatistics(

            total_todos=stats["total_todos"],

            completed_todos=stats["completed_todos"],

            pending_todos=stats["pending_todos"],

            overdue_todos=stats["overdue_todos"],

            completion_rate=stats["completion_rate"],

            by_status=json.dumps(stats["by_status"]),

            by_priority=json.dumps(stats["by_priority"]),

        )

# =============================================================================

# MUTATIONS

# =============================================================================

@strawberry.type

class Mutation:

    """

    Todo mutations.

    MUTATION EXAMPLES:

    # Create todo

    mutation {

        createTodo(input: {

            title: "Buy groceries"

            priority: HIGH

            dueDate: "2024-12-31T23:59:59Z"

        }) {

            id

            title

        }

    }

    # Complete todo

    mutation {

        completeTodo(id: 1) {

            id

            isCompleted

            completedAt

        }

    }

    """

    @strawberry.mutation(

        description="Create a new todo",

        permission_classes=[IsAuthenticated],

    )

    async def create_todo(

        self,

        info: Info,

        input: CreateTodoInput,

    ) -> TodoType:

        """Create a new todo for the current user."""

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.create_todo(

            session,

            owner_id=current_user.id,

            title=input.title,

            description=input.description,

            priority=TodoPriority(input.priority.value),

            due_date=input.due_date,

        )

        return todo_to_type(todo)

    @strawberry.mutation(

        description="Update a todo",

        permission_classes=[IsAuthenticated],

    )

    async def update_todo(

        self,

        info: Info,

        id: int,

        input: UpdateTodoInput,

    ) -> TodoType:

        """Update a todo (owner only)."""

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.get_active(session, id)

        if not todo:

            raise Exception("Todo not found")

        if todo.owner_id != current_user.id:

            raise Exception("Permission denied")

        # Build update data

        update_data = {}

        if input.title is not None:

            update_data["title"] = input.title

        if input.description is not None:

            update_data["description"] = input.description

        if input.priority is not None:

            update_data["priority"] = TodoPriority(input.priority.value)

        if input.status is not None:

            update_data["status"] = TodoStatus(input.status.value)

        if input.due_date is not None:

            update_data["due_date"] = input.due_date

        if input.is_completed is not None:

            update_data["is_completed"] = input.is_completed

            if input.is_completed:

                from datetime import datetime, timezone

                update_data["completed_at"] = datetime.now(timezone.utc)

                update_data["status"] = TodoStatus.COMPLETED

        updated = await todo_repository.update(

            session,

            id=id,

            **update_data,

        )

        return todo_to_type(updated)

    @strawberry.mutation(

        description="Mark todo as completed",

        permission_classes=[IsAuthenticated],

    )

    async def complete_todo(self, info: Info, id: int) -> TodoType:

        """Mark a todo as completed."""

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.get_active(session, id)

        if not todo:

            raise Exception("Todo not found")

        if todo.owner_id != current_user.id:

            raise Exception("Permission denied")

        completed = await todo_repository.complete_todo(session, id)

        return todo_to_type(completed)

    @strawberry.mutation(

        description="Delete own todo",

        permission_classes=[IsAuthenticated],

    )

    async def delete_todo(self, info: Info, id: int) -> OperationResult:

        """

        Delete user's own todo.

        This is a soft delete for regular users.

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.get_active(session, id)

        if not todo:

            raise Exception("Todo not found")

        if todo.owner_id != current_user.id:

            raise Exception("Permission denied")

        await todo_repository.soft_delete(

            session,

            id=id,

            deleted_by_id=current_user.id,

            reason="Deleted by owner",

        )

        return OperationResult(

            success=True,

            message="Todo deleted successfully",

        )

    @strawberry.mutation(

        description="Admin delete user's todo with reason",

        permission_classes=[IsAdmin],

    )

    async def admin_delete_todo(

        self,

        info: Info,

        input: DeleteTodoInput,

    ) -> OperationResult:

        """

        Admin deletes a user's todo with required reason.

        AUDIT TRAIL:

        - Records who deleted

        - Records reason for deletion

        - Keeps record (soft delete)

        """

        session = info.context["session"]

        current_user = info.context["current_user"]

        todo = await todo_repository.get_active(session, input.todo_id)

        if not todo:

            raise Exception("Todo not found")

        await todo_repository.soft_delete(

            session,

            id=input.todo_id,

            deleted_by_id=current_user.id,

            reason=input.reason,

        )

        return OperationResult(

            success=True,

            message=f"Todo deleted by admin. Reason: {input.reason}",

        )

## 8.6 app/graphql/schema.py

# app/graphql/schema.py

"""

=============================================================================

GraphQL Schema Definition

=============================================================================

The schema combines all queries and mutations into the final GraphQL schema.

SCHEMA COMPOSITION:

------------------

Strawberry allows combining multiple Query/Mutation classes using inheritance.

This keeps resolvers organized by domain (users, todos, etc.)

SCHEMA OUTPUT:

-------------

The schema generates a GraphQL SDL (Schema Definition Language):

type Query {

    me: UserType!

    users(skip: Int, limit: Int): [UserType!]!

    ...

}

type Mutation {

    signup(input: SignupInput!): AuthPayload!

    login(input: LoginInput!): AuthPayload!

    ...

}

"""

import strawberry

from app.graphql.resolvers.user_resolvers import (

    Query as UserQuery,

    Mutation as UserMutation,

)

from app.graphql.resolvers.todo_resolvers import (

    Query as TodoQuery,

    Mutation as TodoMutation,

)

# =============================================================================

# COMBINED QUERY CLASS

# =============================================================================

# Inherits from all domain-specific Query classes

@strawberry.type

class Query(UserQuery, TodoQuery):

    """

    Combined Query type.

    INHERITANCE:

    All fields from UserQuery and TodoQuery are available here.

    AVAILABLE QUERIES:

    - me: Current user

    - users: List users (admin)

    - user: Get user by ID (admin)

    - userStatistics: User stats (admin)

    - myTodos: Current user's todos

    - todo: Get todo by ID

    - allTodos: All todos (admin)

    - todoStatistics: Todo stats

    """

    pass

# =============================================================================

# COMBINED MUTATION CLASS

# =============================================================================

@strawberry.type

class Mutation(UserMutation, TodoMutation):

    """

    Combined Mutation type.

    AVAILABLE MUTATIONS:

    - signup: Register new user

    - login: Authenticate user

    - refreshToken: Get new tokens

    - createUser: Admin create user

    - updateUser: Update profile

    - deleteUser: Delete user

    - createTodo: Create todo

    - updateTodo: Update todo

    - completeTodo: Mark complete

    - deleteTodo: Delete own todo

    - adminDeleteTodo: Admin delete with reason

    """

    pass

# =============================================================================

# SCHEMA

# =============================================================================

schema = strawberry.Schema(

    query=Query,

    mutation=Mutation,

)

# 9. Database Migrations (Alembic)

## 9.1 alembic.ini

# alembic.ini

# =============================================================================

# Alembic Configuration

# =============================================================================

# Alembic is the migration tool for SQLAlchemy.

# It tracks database schema changes and applies them incrementally.

[alembic]

# Path to migration scripts

script_location = alembic

# Template for migration file names

file_template = %%(rev)s_%%(slug)s

# Timezone for revision timestamps

timezone = UTC

# Truncate long revision identifiers

truncate_slug_length = 40

# Set to 'true' to run autogenerate on create

# revision_environment = false

# Prepend sys.path with current directory

prepend_sys_path = .

# Connection string (overridden by env.py)

sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]

# Black formatter (optional)

# hooks = black

# black.type = console_scripts

# black.entrypoint = black

# black.options = -q

[loggers]

keys = root,sqlalchemy,alembic

[handlers]

keys = console

[formatters]

keys = generic

[logger_root]

level = WARN

handlers = console

qualname =

[logger_sqlalchemy]

level = WARN

handlers =

qualname = sqlalchemy.engine

[logger_alembic]

level = INFO

handlers =

qualname = alembic

[handler_console]

class = StreamHandler

args = (sys.stderr,)

level = NOTSET

formatter = generic

[formatter_generic]

format = %(levelname)-5.5s [%(name)s] %(message)s

datefmt = %H:%M:%S

## 9.2 alembic/env.py

# alembic/env.py

"""

=============================================================================

Alembic Migration Environment

=============================================================================

This file configures Alembic for async SQLAlchemy 2.0.

ASYNC MIGRATIONS:

----------------

SQLAlchemy 2.0 async requires special handling:

- Use run_async() for async operations

- Use AsyncEngine instead of Engine

- Use async with for connections

"""

import asyncio

from logging.config import fileConfig

from sqlalchemy import pool

from sqlalchemy.engine import Connection

from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import settings and models

from app.core.config import settings

from app.db.base import Base

# Import all models for autogenerate

from app.models import User, Todo

# Alembic Config object

config = context.config

# Setup logging

if config.config_file_name is not None:

    fileConfig(config.config_file_name)

# Set target metadata for autogenerate

target_metadata = Base.metadata

# Override sqlalchemy.url from settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:

    """

    Run migrations in 'offline' mode.

    This generates SQL scripts without connecting to database.

    Useful for generating migration scripts to run manually.

    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(

        url=url,

        target_metadata=target_metadata,

        literal_binds=True,

        dialect_opts={"paramstyle": "named"},

    )

    with context.begin_transaction():

        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:

    """Run migrations with the given connection."""

    context.configure(

        connection=connection,

        target_metadata=target_metadata,

    )

    with context.begin_transaction():

        context.run_migrations()

async def run_async_migrations() -> None:

    """

    Run migrations in 'online' mode with async engine.

    ASYNC MIGRATION FLOW:

    1. Create async engine

    2. Connect asynchronously

    3. Run migrations synchronously in connection context

    4. Dispose engine

    """

    connectable = async_engine_from_config(

        config.get_section(config.config_ini_section, {}),

        prefix="sqlalchemy.",

        poolclass=pool.NullPool,

    )

    async with connectable.connect() as connection:

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:

    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())

# Determine mode and run

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()

## 9.3 alembic/versions/001_initial_migration.py

"""Initial migration - create users and todos tables

Revision ID: 001_initial

Revises: 

Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision: str = '001_initial'

down_revision: Union[str, None] = None

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    """

    Create initial database schema.

    TABLES:

    - users: User accounts with role-based access

    - todos: Todo items with soft delete support

    """

    # Create users table

    op.create_table(

        'users',

        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        sa.Column('email', sa.String(255), nullable=False),

        sa.Column('hashed_password', sa.String(255), nullable=False),

        sa.Column('full_name', sa.String(255), nullable=False),

        sa.Column('role', sa.Enum('user', 'admin', 'superadmin', name='userrole'), nullable=False),

        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),

        sa.Column('created_by_id', sa.Integer(), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id'),

        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),

    )

    # Create indexes for users

    op.create_index('ix_users_id', 'users', ['id'])

    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create todos table

    op.create_table(

        'todos',

        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        sa.Column('title', sa.String(255), nullable=False),

        sa.Column('description', sa.Text(), nullable=True),

        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='todopriority'), nullable=False),

        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='todostatus'), nullable=False),

        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),

        sa.Column('owner_id', sa.Integer(), nullable=False),

        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),

        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('deleted_by_id', sa.Integer(), nullable=True),

        sa.Column('deletion_reason', sa.Text(), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id'),

        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),

        sa.ForeignKeyConstraint(['deleted_by_id'], ['users.id'], ondelete='SET NULL'),

    )

    # Create indexes for todos

    op.create_index('ix_todos_id', 'todos', ['id'])

    op.create_index('ix_todos_owner_id', 'todos', ['owner_id'])

    op.create_index('ix_todos_deleted_at', 'todos', ['deleted_at'])

def downgrade() -> None:

    """Drop all tables."""

    op.drop_index('ix_todos_deleted_at', table_name='todos')

    op.drop_index('ix_todos_owner_id', table_name='todos')

    op.drop_index('ix_todos_id', table_name='todos')

    op.drop_table('todos')

    op.drop_index('ix_users_email', table_name='users')

    op.drop_index('ix_users_id', table_name='users')

    op.drop_table('users')

    # Drop enums

    op.execute('DROP TYPE IF EXISTS todostatus')

    op.execute('DROP TYPE IF EXISTS todopriority')

    op.execute('DROP TYPE IF EXISTS userrole')

# 10. Superadmin Seeder

## 10.1 scripts/seed_superadmin.py

#!/usr/bin/env python3

"""

=============================================================================

Superadmin Seeder Script

=============================================================================

This script creates the initial superadmin account.

USAGE:

    python scripts/seed_superadmin.py

RUN AFTER:

    1. Database is created

    2. Migrations are applied

IDEMPOTENT:

    Safe to run multiple times - skips if superadmin exists.

"""

import asyncio

import sys

from pathlib import Path

# Add project root to path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

from app.db.database import async_session_maker

from app.models.user import User, UserRole

from app.repositories import user_repository

async def seed_superadmin():

    """

    Create superadmin account if it doesn't exist.

    Uses configuration from environment variables:

    - SUPERADMIN_EMAIL

    - SUPERADMIN_PASSWORD

    - SUPERADMIN_FULL_NAME

    """

    print("=" * 60)

    print("Superadmin Seeder")

    print("=" * 60)

    async with async_session_maker() as session:

        # Check if superadmin exists

        existing = await user_repository.get_by_email(

            session,

            settings.SUPERADMIN_EMAIL,

        )

        if existing:

            print(f"Superadmin already exists: {settings.SUPERADMIN_EMAIL}")

            print("Skipping creation.")

            return

        # Create superadmin

        superadmin = await user_repository.create_user(

            session,

            email=settings.SUPERADMIN_EMAIL,

            password=settings.SUPERADMIN_PASSWORD,

            full_name=settings.SUPERADMIN_FULL_NAME,

            role=UserRole.SUPERADMIN,

        )

        await session.commit()

        print(f"Superadmin created successfully!")

        print(f"  Email: {superadmin.email}")

        print(f"  Name: {superadmin.full_name}")

        print(f"  Role: {superadmin.role.value}")

        print(f"  ID: {superadmin.id}")

    print("=" * 60)

if __name__ == "__main__":

    asyncio.run(seed_superadmin())

# 11. Running the Project

Follow these steps to run the complete project:

1. Clone the repository and navigate to the project directory.

2. Copy .env.example to .env and fill in your values (generate SECRET_KEY with: openssl rand -hex 32).

3. Start the containers: docker-compose up -d --build

4. Run migrations: docker-compose exec api alembic upgrade head

5. Seed superadmin: docker-compose exec api python scripts/seed_superadmin.py

6. Access GraphQL Playground at http://localhost:8000/graphql

7. Access Adminer at http://localhost:8080 (server: db, user/pass from .env)

## 11.1 Example GraphQL Queries

# Login

mutation {

  login(input: { email: "superadmin@example.com", password: "SuperAdmin123!" }) {

    user { id email role }

    tokens { accessToken refreshToken }

  }

}

# Get current user (add Authorization: Bearer <token> header)

query {

  me {

    id

    email

    fullName

    role

    todoCount

  }

}

# Create a todo

mutation {

  createTodo(input: {

    title: "Learn GraphQL"

    description: "Complete this tutorial"

    priority: HIGH

  }) {

    id

    title

    status

    priority

  }

}

# Get my todos

query {

  myTodos {

    id

    title

    status

    priority

    isOverdue

  }

}

# Get user statistics (admin only)

query {

  userStatistics {

    totalUsers

    activeUsers

    adminsCount

  }

}

# 12. Conclusion

This document provides a complete, production-ready GraphQL API implementation. The codebase demonstrates senior-level patterns including clean architecture, repository pattern, JWT authentication with refresh tokens, role-based access control, soft deletes with audit trails, and comprehensive error handling.

Key takeaways: GraphQL provides a flexible, type-safe API layer. Strawberry integrates seamlessly with FastAPI using Python type hints. SQLAlchemy 2.0 async provides excellent performance. The repository pattern separates data access from business logic. Proper authentication and authorization are crucial for production systems.

For questions or improvements, refer to the official documentation: FastAPI (fastapi.tiangolo.com), Strawberry GraphQL (strawberry.rocks), SQLAlchemy (docs.sqlalchemy.org), Pydantic (docs.pydantic.dev).
