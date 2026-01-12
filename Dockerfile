# =============================================================================
# Multi-stage Dockerfile for GraphQL Todo API
# =============================================================================
# STAGES:
# 1. builder: Install dependencies using UV into a virtual environment
# 2. production: Slim image with only runtime dependencies
#
# KEY FIX: Removed --system flag from uv pip install
# The --system flag was installing packages to system Python, not the venv!
# =============================================================================

# ===========================================================================
# STAGE 1: Builder - Install dependencies
# ===========================================================================
FROM python:3.13-slim AS builder

# Install UV package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml uv.lock* requirements.txt* ./

# Create virtual environment and install dependencies
# CRITICAL: Do NOT use --system flag - we want packages IN the venv
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r requirements.txt

# ===========================================================================
# STAGE 2: Production - Slim runtime image
# ===========================================================================
FROM python:3.13-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Add virtual environment to PATH - this is how uvicorn will be found
    PATH="/opt/venv/bin:$PATH" \
    # Default port
    PORT=8000

# Install runtime system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder (contains all installed packages)
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check - using curl is more reliable than Python urllib
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with uvicorn
# The uvicorn executable is now properly available at /opt/venv/bin/uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
