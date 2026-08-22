from fastapi import APIRouter

from .endpoints import artworks, media, profiles

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(profiles.router)
api_router.include_router(artworks.router)
api_router.include_router(media.router)
api_router.include_router(media.media_router)
