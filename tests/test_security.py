"""
Security Verification Tests.

These tests verify security requirements:
- Cache headers prevent browser caching (ARCH-05)
- No sensitive data in logs (ARCH-04)
- File size limits enforced (ARCH-06)
- Request timeout (ARCH-07)

Reference: PITFALLS.md - Browser Caching of Sensitive Downloads, Logging User Data
"""
import io
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient

from app.core.config import settings


class TestCacheHeaders:
    """Test cache headers are set on all responses."""
    
    @pytest.mark.asyncio
    async def test_cache_headers_on_health(self, client: AsyncClient):
        """
        Verify cache headers on health endpoint.
        
        Reference: ARCH-05
        """
        response = await client.get("/health")
        assert response.status_code == 200
        
        # Check required cache headers
        assert "cache-control" in response.headers
        cache_control = response.headers["cache-control"].lower()
        
        # Must contain no-store and no-cache
        assert "no-store" in cache_control, \
            f"Cache-Control should contain 'no-store', got: {cache_control}"
        assert "no-cache" in cache_control, \
            f"Cache-Control should contain 'no-cache', got: {cache_control}"
        assert "must-revalidate" in cache_control, \
            f"Cache-Control should contain 'must-revalidate', got: {cache_control}"
        assert "private" in cache_control, \
            f"Cache-Control should contain 'private', got: {cache_control}"
            
    @pytest.mark.asyncio
    async def test_cache_headers_on_test_endpoint(self, client: AsyncClient):
        """Verify cache headers on test endpoint."""
        response = await client.get("/test-cache")
        assert response.status_code == 200
        
        cache_control = response.headers.get("cache-control", "")
        assert "no-store" in cache_control.lower()
        
    @pytest.mark.asyncio
    async def test_cache_headers_on_download(
        self, client: AsyncClient, sample_pdf_bytes: bytes, sample_pdf_two_pages: bytes
    ):
        """
        Verify cache headers on PDF download.
        
        Reference: ARCH-05
        """
        files = [
            ("files", ("test1.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 200
        
        # Verify cache headers on download response
        cache_control = response.headers.get("cache-control", "")
        assert "no-store" in cache_control.lower(), \
            f"Download response should have no-store, got: {cache_control}"
            
    @pytest.mark.asyncio
    async def test_pragma_header(self, client: AsyncClient):
        """Verify Pragma: no-cache header."""
        response = await client.get("/health")
        
        pragma = response.headers.get("pragma", "").lower()
        assert "no-cache" in pragma, \
            f"Pragma should be 'no-cache', got: {pragma}"
            
    @pytest.mark.asyncio
    async def test_expires_header(self, client: AsyncClient):
        """Verify Expires: 0 header."""
        response = await client.get("/health")
        
        expires = response.headers.get("expires", "")
        assert expires == "0", f"Expires should be '0', got: {expires}"
        
    @pytest.mark.asyncio
    async def test_x_content_type_options(self, client: AsyncClient):
        """Verify X-Content-Type-Options: nosniff header."""
        response = await client.get("/health")
        
        x_content_type = response.headers.get("x-content-type-options", "").lower()
        assert "nosniff" in x_content_type, \
            f"X-Content-Type-Options should be 'nosniff', got: {x_content_type}"


class TestNoSensitiveDataInLogs:
    """Test that no sensitive data appears in logs."""
    
    def test_logging_middleware_exists(self):
        """Verify privacy logging middleware exists."""
        from app.middleware.privacy_logging import PrivacyLoggingMiddleware
        assert PrivacyLoggingMiddleware is not None
        
    def test_logging_middleware_sanitizes(self):
        """
        Verify middleware only logs method/path/status.
        
        Reference: ARCH-04
        """
        from app.middleware.privacy_logging import PrivacyLoggingMiddleware
        import inspect
        
        source = inspect.getsource(PrivacyLoggingMiddleware.dispatch)
        
        # Verify the middleware logs method and path
        assert "method" in source.lower() or "request.method" in source, \
            "Should log HTTP method"
        assert "path" in source.lower() or "request.url.path" in source, \
            "Should log request path"
            
        # Verify it does NOT log request body or other sensitive data
        # The source should NOT have body logging
        assert "request.body()" not in source, \
            "Should NOT log request body"
        assert "client.host" not in source and "client" not in source.split("request.")[0] if "request." in source else True, \
            "Should NOT log client IP"
            
    @pytest.mark.asyncio
    async def test_filename_not_in_response_headers(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Verify original filename is not exposed in response headers."""
        # Use a distinctive filename
        sensitive_filename = "CONFIDENTIAL_BANK_STATEMENT.pdf"
        files = [
            ("file", (sensitive_filename, BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"degrees": 90, "pages": "all"}
        
        response = await client.post("/api/v1/pdf/rotate", files=files, data=data)
        assert response.status_code == 200
        
        # The Content-Disposition should NOT contain the original filename
        # It should be a sanitized/generic name
        content_disp = response.headers.get("content-disposition", "")
        # Should not leak the original sensitive filename
        assert sensitive_filename not in content_disp, \
            f"Original filename should not be in Content-Disposition: {content_disp}"


class TestFileSizeLimits:
    """Test file size limits are enforced."""
    
    @pytest.mark.asyncio
    async def test_file_size_limit_enforced(self, client: AsyncClient):
        """
        Verify file size limit is enforced.
        
        Reference: ARCH-06
        """
        # Create a file larger than MAX_FILE_SIZE_MB
        # Default is 100MB, so create a 101MB file
        large_size = (settings.MAX_FILE_SIZE_MB + 1) * 1024 * 1024
        large_content = b"X" * large_size
        
        files = [
            ("files", ("large.pdf", BytesIO(large_content), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        
        # Should reject with 413 Request Entity Too Large or 400 Bad Request
        # (400 if validation catches it before size check)
        assert response.status_code in [400, 413], \
            f"Should reject large file with 400 or 413, got: {response.status_code}"
            
    @pytest.mark.asyncio
    async def test_empty_file_rejected(self, client: AsyncClient):
        """Verify empty files are rejected."""
        files = [
            ("files", ("empty.pdf", BytesIO(b""), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        
        assert response.status_code == 400, \
            f"Should reject empty file with 400, got: {response.status_code}"
            
    @pytest.mark.asyncio
    async def test_normal_size_accepted(
        self, client: AsyncClient, sample_pdf_bytes: bytes, sample_pdf_two_pages: bytes
    ):
        """Verify normal-sized files are accepted."""
        files = [
            ("files", ("test1.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        
        assert response.status_code == 200, \
            f"Normal files should be accepted, got: {response.status_code}"


class TestRequestTimeout:
    """Test request timeout configuration."""
    
    def test_timeout_configured(self):
        """Verify request timeout is configured."""
        assert hasattr(settings, "REQUEST_TIMEOUT_SECONDS"), \
            "Settings should have REQUEST_TIMEOUT_SECONDS"
        assert settings.REQUEST_TIMEOUT_SECONDS > 0, \
            "Request timeout should be positive"
            
    def test_timeout_reasonable(self):
        """Verify timeout is set to a reasonable value."""
        # Should be between 10 and 300 seconds
        assert 10 <= settings.REQUEST_TIMEOUT_SECONDS <= 300, \
            f"Timeout should be between 10-300s, got: {settings.REQUEST_TIMEOUT_SECONDS}"
            
    def test_dockerfile_timeout_configured(self):
        """Verify Gunicorn timeout is set in Dockerfile."""
        dockerfile_path = Path("/home/ubuntu/projects/NoTracePDF/Dockerfile")
        if dockerfile_path.exists():
            content = dockerfile_path.read_text()
            assert "--timeout" in content, \
                "Dockerfile should have Gunicorn timeout configured"


class TestMemoryLimits:
    """Test memory limits configuration."""
    
    def test_docker_memory_limit(self):
        """Verify Docker memory limit is configured."""
        compose_path = Path("/home/ubuntu/projects/NoTracePDF/docker-compose.yml")
        if compose_path.exists():
            content = compose_path.read_text()
            assert "memory:" in content.lower(), \
                "docker-compose.yml should have memory limit configured"
            assert "1G" in content or "1g" in content.lower() or "1024M" in content, \
                "Memory limit should be set (expected 1G)"
                
    def test_memory_limit_prevents_oom(self):
        """
        Verify memory limit would prevent host OOM.
        
        Reference: ARCH-06
        """
        compose_path = Path("/home/ubuntu/projects/NoTracePDF/docker-compose.yml")
        if compose_path.exists():
            content = compose_path.read_text()
            # Verify limits section exists
            assert "limits:" in content, \
                "docker-compose.yml should have resource limits"
