FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy workspace-level dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Copy the auth_service pyproject.toml (needed for workspace resolution)
COPY services/auth_service/pyproject.toml services/auth_service/pyproject.toml

# Install dependencies (workspace-aware: uv resolves from root lockfile)
RUN uv sync --frozen --no-dev --no-install-project --package auth-service

# Copy the auth_service source and alembic config
COPY services/auth_service/src services/auth_service/src
COPY services/auth_service/alembic services/auth_service/alembic
COPY services/auth_service/alembic.ini services/auth_service/alembic.ini
COPY services/auth_service/README.md services/auth_service/README.md

# Install the auth-service package itself
RUN uv sync --frozen --no-dev --package auth-service

EXPOSE 8001

CMD ["uv", "run", "--package", "auth-service", "uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
