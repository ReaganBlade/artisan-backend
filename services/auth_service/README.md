# Auth Service

Identity & Auth microservice — owns the `auth_schema` database schema.

## Endpoints

- `POST /api/v1/auth/signup` — Register a new account
- `POST /api/v1/auth/signin` — Sign in with email + password
- `POST /api/v1/auth/refresh` — Rotate a refresh token
- `POST /api/v1/auth/logout` — Revoke a refresh token
- `GET /api/v1/auth/me` — Get current user profile
- `GET /health` — Health check

## Running locally with Docker

```bash
cd services/auth_service
docker compose up --build
```

## Running locally without docker

```
uv run uvicorn auth_service.main:app --host 0.0.0.0 --port 8001
```

The service will be available at `http://localhost:8001`.
PostgreSQL runs on port `5432`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/artisan` | PostgreSQL connection string |
| `DEBUG` | `false` | Enable SQLAlchemy query logging |
| `ENVIRONMENT` | `development` | Runtime environment |
| `JWT_SECRET_KEY` | (dev default) | Secret for JWT signing |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `AUTO_MIGRATE` | `true` | Run Alembic migrations on startup |
