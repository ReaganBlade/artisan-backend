from fastapi import APIRouter

from .endpoints import search

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(search.router)
