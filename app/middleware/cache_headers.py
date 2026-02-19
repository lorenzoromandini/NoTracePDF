"""
Cache control headers middleware that prevents browser caching.

This middleware ensures that ALL responses include privacy-preserving
cache headers to prevent browsers from storing user files locally.

Headers added:
- Cache-Control: no-store, no-cache, must-revalidate, private
- Pragma: no-cache
- Expires: 0
- X-Content-Type-Options: nosniff

Reference: PITFALLS.md "Browser Caching of Sensitive Downloads"
Requirement: ARCH-05
"""
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds privacy-preserving cache headers to all responses.
    
    This prevents browsers and proxies from caching any responses,
    ensuring that processed files are not stored in browser cache.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process request
        response = await call_next(request)
        
        # Add privacy-preserving cache headers to ALL responses
        # These headers prevent browser caching of any content
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response
