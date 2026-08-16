from fastapi import APIRouter

from .endpoints import artworks, profiles

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(artworks.router)
api_router.include_router(profiles.router)
