# Changelog

All notable changes to the **auth_service** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Full auth API** under `POST/GET /api/v1/auth/*`:
  - `POST /api/v1/auth/signup` — create a customer account and sign in immediately.
  - `POST /api/v1/auth/signin` — exchange email + password for an access/refresh token pair.
  - `POST /api/v1/auth/refresh` — rotate a refresh token and return a fresh token pair.
  - `POST /api/v1/auth/logout` — revoke a refresh token (idempotent).
  - `GET /api/v1/auth/me` — return the profile of the authenticated user.
- **Authentication core** (`core/security.py`):
  - bcrypt password hashing/verification with per-user salts.
  - Short-lived JWT access tokens (`sub`, `type: access`, `iat`, `exp`).
  - Opaque, cryptographically random refresh tokens stored as SHA-256 digests.
- **SQLAlchemy async models** for the `auth_schema` schema (`models/`):
  - `User` (email, hashed password, `UserRole` enum, active flag, timestamps).
  - `RefreshToken` (hashed token, expiry, revocation flag, FK to users with CASCADE).
  - `UserRole` enum (`CUSTOMER`, `ARTIST`, `ADMIN`).
- **Repository layer** (`repositories/user_repository.py`) for user and refresh-token
  persistence.
- **Service layer** (`services/auth_service.py`) implementing signup, signin, token
  rotation, and logout business logic.
- **Pydantic schemas** (`schemas/`) for request validation (email format, password
  length) and API responses (token pairs, user payloads).
- **Alembic migration** `0001_initial_auth_schema` creating the `auth_schema` schema
  with `users` and `refresh_tokens` tables.
- **Settings** (`core/config.py`) loaded from `services/auth_service/.env` with
  defaults for database, JWT, and Supabase configuration.
- **Supabase client factory** (`core/supabase.py`), created lazily so the app runs
  without Supabase configured until the client is actually used.
- **Windows support**: selector-based event loop factory (`core/loops.py`) so
  psycopg's async driver works under uvicorn on Windows.
- **`GET /health`** endpoint for the service.
- **Test suite** (`tests/`) covering security primitives, schemas, the service
  layer, and the full API (DB-backed tests skip when Postgres is unreachable).
- **`.env.example`** documenting all required environment variables.

### Changed

- **Replaced passlib with direct bcrypt** usage — passlib 1.7.4 breaks with
  bcrypt >= 4.1; bcrypt is now a hard dependency.
- **Dependency updates** (`pyproject.toml`):
  - `psycopg[binary]` for the async driver.
  - `supabase` client added.
  - `passlib` removed.
- **Model files renamed** from `users.py`/`refresh_tokens.py` to
  `user.py`/`refresh_token.py` (single-table-per-module convention).
- **Stub endpoints** `signin.py`/`signup.py` replaced by a single `auth.py`
  endpoint module.
- **Root workspace**: `pytest` added to the root dev dependency group and
  `uv.lock` regenerated across the workspace.
