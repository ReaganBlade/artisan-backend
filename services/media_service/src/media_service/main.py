from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.session import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gracefully release the async engine's connection pool on shutdown."""
    yield
    await close_db()


app = FastAPI(
    title="Media Service",
    description="Catalog & Media microservice — owns the media_schema database schema.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "media-service"}
