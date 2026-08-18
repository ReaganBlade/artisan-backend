import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from .api.v1.router import api_router
from .core.limiter import limiter
from .db.session import close_db

logger = logging.getLogger(__name__)

# Dev-only: allow the Next.js dev server to call this service directly.
# Replace with your production frontend origin(s) before deploying.
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8001"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run Alembic migrations on startup, then gracefully release DB pool on shutdown."""
    # Auto-run Alembic migrations so Docker containers stay in sync.
    from pathlib import Path

    from .core.config import settings
    if settings.AUTO_MIGRATE:
        try:
            # Resolve alembic.ini relative to this source file (works regardless of CWD).
            service_root = Path(__file__).resolve().parents[2]
            alembic_ini = service_root / "alembic.ini"
            alembic_cfg = AlembicConfig(str(alembic_ini))
            # Override script_location to be absolute so it works regardless of CWD.
            alembic_cfg.set_main_option("script_location", str(service_root / "alembic"))
            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic migrations applied successfully.")
        except Exception:
            logger.exception("Alembic migration failed — continuing anyway.")
    yield
    await close_db()


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


app = FastAPI(
    title="Auth Service",
    description="Identity & Auth microservice — owns the auth_schema database schema.",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "auth-service"}
