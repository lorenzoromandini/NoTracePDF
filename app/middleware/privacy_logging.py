"""
Privacy-aware logging middleware that sanitizes all request data.

This middleware ensures that NO user data is ever logged:
- No IP addresses
- No filenames
- No file sizes
- No request bodies
- No query parameters containing user data

Reference: PITFALLS.md "Logging User Data" section
Requirement: ARCH-04
"""
import time
import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notracepdf")


class PrivacyLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs request information without any user data.
    
    Logs ONLY:
    - Timestamp
    - HTTP method
    - Request path (sanitized)
    - Response status code
    - Processing time in milliseconds
    - Request ID (for tracing without user data)
    
    NEVER logs:
    - IP addresses
    - Request body
    - Query parameters (may contain file info)
    - Filenames
    - File sizes
    - User agent (could contain identifiable info)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        
        # Sanitize path - remove any query parameters that might contain user data
        path = request.url.path
        
        # Record start time
        start_time = time.perf_counter()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Log only sanitized, non-user data
        # Format: JSON-like structured log
        logger.info(
            '{"request_id": "%s", "method": "%s", "path": "%s", "status": %d, "duration_ms": %.2f}',
            request_id,
            request.method,
            path,
            response.status_code,
            process_time_ms
        )
        
        # Add request ID to response headers for debugging (no user data)
        response.headers["X-Request-ID"] = request_id
        
        return response
