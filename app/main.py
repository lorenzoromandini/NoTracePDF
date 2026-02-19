"""
NoTracePDF - Self-hosted, zero-trace PDF processing toolkit.

Main FastAPI application with privacy-first middleware.
"""
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.cleanup import register_cleanup_handlers
from app.middleware.privacy_logging import PrivacyLoggingMiddleware
from app.middleware.cache_headers import CacheHeadersMiddleware
from app.api.v1 import api_router


# Static files directory
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    register_cleanup_handlers()
    yield
    # Shutdown - cleanup is handled by signal handlers


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Self-hosted, zero-trace PDF processing toolkit",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware (allow all origins for self-hosted)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add privacy-aware logging middleware
app.add_middleware(PrivacyLoggingMiddleware)

# Add cache control headers middleware
app.add_middleware(CacheHeadersMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/test-cache")
async def test_cache() -> dict:
    """Test endpoint to verify cache headers are applied."""
    return {"message": "Cache headers should be present in response"}


# Mount static files for web UI (must be after API routes)
# Serve static assets (CSS, JS)
app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")


# Serve index.html for root and SPA fallback
@app.get("/", response_class=FileResponse)
async def serve_index():
    """Serve the main web UI."""
    return FileResponse(STATIC_DIR / "index.html")
