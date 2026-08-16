from fastapi import APIRouter

from .endpoints import cart, checkout

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cart.router)
api_router.include_router(checkout.router)
