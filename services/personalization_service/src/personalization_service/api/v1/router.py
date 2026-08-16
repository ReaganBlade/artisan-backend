from fastapi import APIRouter

from .endpoints import feed

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(feed.router)
