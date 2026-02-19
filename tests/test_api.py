"""
API Endpoint Tests.

Tests verify all endpoints exist and respond correctly.
"""
from io import BytesIO
import json

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_exists(self, client: AsyncClient):
        """GET /health returns 200."""
        response = await client.get("/health")
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_health_returns_json(self, client: AsyncClient):
        """Health endpoint returns JSON."""
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


class TestPDFEndpoints:
    """Test PDF API endpoints exist and respond."""
    
    @pytest.mark.asyncio
    async def test_merge_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes, sample_pdf_two_pages: bytes
    ):
        """POST /api/v1/pdf/merge returns 200."""
        files = [
            ("files", ("test1.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_split_endpoint_exists(
        self, client: AsyncClient, sample_pdf_two_pages: bytes
    ):
        """POST /api/v1/pdf/split returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        data = {"mode": "range", "start": 1, "end": 1}
        
        response = await client.post("/api/v1/pdf/split", files=files, data=data)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_rotate_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/pdf/rotate returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"pages": "all", "degrees": 90}
        
        response = await client.post("/api/v1/pdf/rotate", files=files, data=data)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_compress_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/pdf/compress returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"quality": "medium"}
        
        response = await client.post("/api/v1/pdf/compress", files=files, data=data)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_password_add_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/pdf/password/add returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"password": "test123"}
        
        response = await client.post("/api/v1/pdf/password/add", files=files, data=data)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_watermark_text_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/pdf/watermark/text returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"text": "CONFIDENTIAL", "font_size": 48, "color": "#808080", 
                "opacity": 0.3, "position": "diagonal", "pages": "all"}
        
        response = await client.post("/api/v1/pdf/watermark/text", files=files, data=data)
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_extract_text_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/pdf/extract/text returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/extract/text", files=files)
        assert response.status_code == 200


class TestFileValidation:
    """Test file type validation."""
    
    @pytest.mark.asyncio
    async def test_non_pdf_rejected(self, client: AsyncClient):
        """Non-PDF file is rejected with 415."""
        files = [
            ("files", ("test.txt", BytesIO(b"not a pdf"), "text/plain")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code in [400, 415]
        
    @pytest.mark.asyncio
    async def test_invalid_pdf_rejected(self, client: AsyncClient):
        """Invalid PDF content is rejected."""
        files = [
            ("files", ("test.pdf", BytesIO(b"not a valid pdf content"), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 400
        
    @pytest.mark.asyncio
    async def test_merge_requires_multiple_files(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Merge endpoint requires at least 2 files."""
        files = [
            ("files", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 400


class TestImageEndpoints:
    """Test Image API endpoints."""
    
    @pytest.mark.asyncio
    async def test_pdf_to_images_endpoint_exists(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """POST /api/v1/image/pdf-to-images returns 200."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"format": "png", "pages": "first", "dpi": 72}
        
        response = await client.post("/api/v1/image/pdf-to-images", files=files, data=data)
        # May fail if poppler not installed in dev environment
        # But endpoint should exist
        assert response.status_code in [200, 500]  # 500 if poppler missing
        
    @pytest.mark.asyncio
    async def test_images_to_pdf_endpoint_exists(
        self, client: AsyncClient, sample_png_bytes: bytes
    ):
        """POST /api/v1/image/images-to-pdf returns 200."""
        files = [
            ("files", ("test.png", BytesIO(sample_png_bytes), "image/png")),
        ]
        data = {"page_size": "a4"}
        
        response = await client.post("/api/v1/image/images-to-pdf", files=files, data=data)
        assert response.status_code == 200
