from fastapi import APIRouter

from .endpoints import moderation

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(moderation.router)
