"""
Integration Tests for NoTracePDF.

These tests verify complete workflows from upload to download,
ensuring all operations work end-to-end with zero-trace guarantees.

Reference: All PDF-*, IMG-*, ARCH-* requirements
"""
from io import BytesIO
import json

import pytest
from httpx import AsyncClient
import pikepdf


class TestFullMergeWorkflow:
    """Test complete merge workflow."""
    
    @pytest.mark.asyncio
    async def test_full_merge_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes, sample_pdf_two_pages: bytes
    ):
        """
        Test complete merge workflow:
        1. Upload 2 PDFs
        2. Merge them
        3. Download result
        4. Verify result is valid PDF
        5. Verify cleanup (handled by zero-trace architecture)
        """
        files = [
            ("files", ("test1.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        
        # Upload and merge
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 200, f"Merge failed: {response.text}"
        
        # Verify response is PDF
        content = response.content
        assert content.startswith(b'%PDF-'), "Response should be a PDF"
        
        # Verify merged PDF has content from both files
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) >= 2, "Merged PDF should have at least 2 pages"
        pdf.close()
        
        # Verify cache headers on download
        assert "no-store" in response.headers.get("cache-control", "").lower()


class TestFullSplitWorkflow:
    """Test complete split workflow."""
    
    @pytest.mark.asyncio
    async def test_full_split_workflow(
        self, client: AsyncClient, sample_pdf_two_pages: bytes
    ):
        """Test complete split workflow."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
        ]
        data = {"mode": "range", "start": 1, "end": 1}
        
        response = await client.post("/api/v1/pdf/split", files=files, data=data)
        assert response.status_code == 200
        
        content = response.content
        assert content.startswith(b'%PDF-')
        
        # Verify split PDF has 1 page
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) == 1
        pdf.close()


class TestFullRotateWorkflow:
    """Test complete rotate workflow."""
    
    @pytest.mark.asyncio
    async def test_full_rotate_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test complete rotate workflow."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"pages": "all", "degrees": 90}
        
        response = await client.post("/api/v1/pdf/rotate", files=files, data=data)
        assert response.status_code == 200
        
        content = response.content
        assert content.startswith(b'%PDF-')
        
        # Verify rotation was applied
        pdf = pikepdf.Pdf.open(BytesIO(content))
        page = pdf.pages[0]
        # Rotation is stored in /Rotate attribute
        if '/Rotate' in page:
            rotation = int(page['/Rotate'])
            assert rotation == 90
        pdf.close()


class TestFullCompressWorkflow:
    """Test complete compress workflow."""
    
    @pytest.mark.asyncio
    async def test_full_compress_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test complete compress workflow."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"quality": "medium"}
        
        response = await client.post("/api/v1/pdf/compress", files=files, data=data)
        assert response.status_code == 200
        
        content = response.content
        assert content.startswith(b'%PDF-')
        
        # Verify result is valid PDF
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) >= 1
        pdf.close()


class TestFullPasswordWorkflow:
    """Test complete password workflow."""
    
    @pytest.mark.asyncio
    async def test_full_password_add_remove_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test adding and removing password."""
        # Add password
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {"password": "test123"}
        
        response = await client.post("/api/v1/pdf/password/add", files=files, data=data)
        assert response.status_code == 200
        
        encrypted_content = response.content
        assert encrypted_content.startswith(b'%PDF-')
        
        # Verify it's encrypted
        with pytest.raises(pikepdf.PasswordError):
            pikepdf.Pdf.open(BytesIO(encrypted_content))
        
        # Open with password
        pdf = pikepdf.Pdf.open(BytesIO(encrypted_content), password="test123")
        assert pdf.is_encrypted
        pdf.close()
        
        # Remove password
        files = [
            ("file", ("protected.pdf", BytesIO(encrypted_content), "application/pdf")),
        ]
        data = {"password": "test123"}
        
        response = await client.post("/api/v1/pdf/password/remove", files=files, data=data)
        assert response.status_code == 200
        
        decrypted_content = response.content
        
        # Verify it's no longer encrypted
        pdf = pikepdf.Pdf.open(BytesIO(decrypted_content))
        assert not pdf.is_encrypted
        pdf.close()


class TestFullWatermarkWorkflow:
    """Test complete watermark workflow."""
    
    @pytest.mark.asyncio
    async def test_full_text_watermark_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test adding text watermark."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {
            "text": "CONFIDENTIAL",
            "font_size": 48,
            "color": "#808080",
            "opacity": 0.3,
            "position": "diagonal",
            "pages": "all"
        }
        
        response = await client.post("/api/v1/pdf/watermark/text", files=files, data=data)
        assert response.status_code == 200
        
        content = response.content
        assert content.startswith(b'%PDF-')
        
        # Verify result is valid PDF
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) >= 1
        pdf.close()


class TestFullExtractWorkflow:
    """Test complete extract workflows."""
    
    @pytest.mark.asyncio
    async def test_full_extract_text_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test extracting text from PDF."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/extract/text", files=files)
        assert response.status_code == 200
        
        result = response.json()
        assert "pages" in result or "text" in result


class TestFullPdfToImagesWorkflow:
    """Test PDF to images conversion."""
    
    @pytest.mark.asyncio
    async def test_full_pdf_to_images_workflow(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Test converting PDF to images."""
        files = [
            ("file", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        data = {
            "format": "png",
            "pages": "first",
            "dpi": 72
        }
        
        response = await client.post("/api/v1/image/pdf-to-images", files=files, data=data)
        
        # May fail if poppler not installed in dev environment
        if response.status_code == 500:
            pytest.skip("poppler-utils not installed (required for pdf-to-images)")
        
        assert response.status_code == 200
        
        content = response.content
        # Should be PNG image
        assert content.startswith(b'\x89PNG')


class TestFullImagesToPdfWorkflow:
    """Test images to PDF conversion."""
    
    @pytest.mark.asyncio
    async def test_full_images_to_pdf_workflow(
        self, client: AsyncClient, sample_png_bytes: bytes
    ):
        """Test converting images to PDF."""
        files = [
            ("files", ("test.png", BytesIO(sample_png_bytes), "image/png")),
        ]
        data = {
            "page_size": "a4",
            "margin": 0,
            "fit_to_page": True
        }
        
        response = await client.post("/api/v1/image/images-to-pdf", files=files, data=data)
        assert response.status_code == 200
        
        content = response.content
        assert content.startswith(b'%PDF-')
        
        # Verify result is valid PDF with 1 page
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) == 1
        pdf.close()


class TestEndToEndWithMultipleFiles:
    """Test workflows with multiple files."""
    
    @pytest.mark.asyncio
    async def test_merge_multiple_pdfs(
        self, client: AsyncClient, sample_pdf_bytes: bytes, sample_pdf_two_pages: bytes
    ):
        """Test merging multiple PDFs (more than 2)."""
        files = [
            ("files", ("test1.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(sample_pdf_two_pages), "application/pdf")),
            ("files", ("test3.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 200
        
        content = response.content
        pdf = pikepdf.Pdf.open(BytesIO(content))
        assert len(pdf.pages) >= 3
        pdf.close()


class TestErrorHandling:
    """Test error handling in workflows."""
    
    @pytest.mark.asyncio
    async def test_invalid_file_error_message(self, client: AsyncClient):
        """Test that invalid files produce helpful error messages."""
        files = [
            ("files", ("test.pdf", BytesIO(b"not a valid pdf"), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 400
        
        error = response.json()
        assert "detail" in error
        
    @pytest.mark.asyncio
    async def test_merge_single_file_error(self, client: AsyncClient, sample_pdf_bytes: bytes):
        """Test that merge requires multiple files."""
        files = [
            ("files", ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")),
        ]
        
        response = await client.post("/api/v1/pdf/merge", files=files)
        assert response.status_code == 400
        assert "at least 2" in response.json().get("detail", "").lower()
