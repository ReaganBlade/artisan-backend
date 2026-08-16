from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .db.session import close_db

# Dev-only: allow the Next.js dev server to call this service directly.
# Replace with your production frontend origin(s) before deploying.
CORS_ORIGINS = ["http://localhost:3000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gracefully release the async engine's connection pool on shutdown."""
    yield
    await close_db()


app = FastAPI(
    title="Commerce Service",
    description="Commerce & Cart microservice — owns the commerce_schema database schema.",
    version="0.1.0",
    lifespan=lifespan,
)

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
    return {"status": "ok", "service": "commerce-service"}
