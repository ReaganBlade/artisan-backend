from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1.router import api_router
from .db.session import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gracefully release the async engine's connection pool on shutdown."""
    yield
    await close_db()


app = FastAPI(
    title="Auth Service",
    description="Identity & Auth microservice — owns the auth_schema database schema.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "auth-service"}
