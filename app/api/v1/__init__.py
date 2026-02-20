"""
API v1 package.
"""
from fastapi import APIRouter

from app.api.v1.pdf import router as pdf_router
from app.api.v1.image import router as image_router
from app.api.v1.convert import router as convert_router

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(pdf_router)
api_router.include_router(image_router)
api_router.include_router(convert_router)

__all__ = ["api_router"]
