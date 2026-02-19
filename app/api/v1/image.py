"""
Image Conversion API Endpoints.

All endpoints use in-memory processing with BytesIO.
No user data is written to disk.

Reference: IMG-01 to IMG-06
"""
from io import BytesIO
from typing import List, Optional, Union
import json

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.pdf import PageSelection, ImageFormat, PageSize
from app.schemas.image import PdfToImageRequest, ImageToPdfRequest
from app.services.image_service import pdf_to_images, images_to_pdf, image_to_pdf_simple
from app.utils.file_utils import (
    validate_pdf,
    validate_image,
    generate_filename,
    create_zip_archive,
    InvalidPageError,
    FileValidationError,
)


router = APIRouter(prefix="/image", tags=["Image Conversion"])


# ==================== PDF TO IMAGES ====================

@router.post("/pdf-to-images")
async def api_pdf_to_images(
    file: UploadFile = File(..., description="PDF file"),
    format: str = Form("png", description="Output format: png, jpg, or webp"),
    pages: str = Form("all", description="Pages to convert: all, first, or JSON array"),
    dpi: int = Form(200, description="DPI for rendering (72-600)"),
    quality: int = Form(85, description="Quality for JPG/WebP (1-100)")
):
    """
    Convert PDF pages to images.
    
    - format: png (lossless), jpg (lossy, smaller), webp (modern)
    - pages: 'all', 'first', or JSON array like [1, 3, 5]
    - dpi: Resolution (72=low, 200=default, 300=high)
    - quality: Only applies to jpg/webp (1-100)
    
    Returns:
    - Single image if pages='first' or single page
    - ZIP archive if multiple pages
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse format
        try:
            format_enum = ImageFormat(format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Must be one of: png, jpg, webp"
            )
        
        # Parse pages
        if pages in ("all", "first", "last"):
            pages_value = PageSelection(pages)
        else:
            try:
                pages_value = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format.")
        
        # Create request
        request = PdfToImageRequest(
            format=format_enum,
            pages=pages_value,
            dpi=dpi,
            quality=quality
        )
        
        # Convert PDF to images
        results = pdf_to_images(pdf_bytes, request)
        
        if len(results) == 1:
            # Single image - return directly
            filename, content = results[0]
            
            # Determine media type
            media_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'webp': 'image/webp'
            }
            ext = filename.rsplit('.', 1)[-1]
            media_type = media_types.get(ext, 'image/png')
            
            return StreamingResponse(
                content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        else:
            # Multiple images - return as ZIP
            zip_content = create_zip_archive(results)
            base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
            
            return StreamingResponse(
                zip_content,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{base_name}_images.zip"'
                }
            )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting PDF to images: {str(e)}")


# ==================== IMAGES TO PDF ====================

@router.post("/images-to-pdf")
async def api_images_to_pdf(
    files: List[UploadFile] = File(..., description="Image files (PNG, JPG, WebP, GIF, BMP)"),
    page_size: str = Form("a4", description="Page size: a4, letter, fit, or original"),
    margin: int = Form(0, description="Margin in pixels"),
    fit_to_page: bool = Form(True, description="Scale images to fit page")
):
    """
    Convert multiple images to a single PDF.
    
    - page_size:
      - a4: A4 paper size (210x297mm)
      - letter: US Letter (8.5x11in)
      - fit: Size each page to fit its image
      - original: Each page sized to its image
    - margin: Whitespace around images (pixels)
    - fit_to_page: Scale image to fit page (true) or center at original size (false)
    
    Returns single PDF with all images as pages.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    try:
        # Parse page size
        try:
            page_size_enum = PageSize(page_size)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid page_size. Must be one of: a4, letter, fit, original"
            )
        
        # Validate and load all images
        image_buffers = []
        for file in files:
            img_bytes, img_format = await validate_image(file)
            image_buffers.append((img_bytes, img_format))
        
        # Create request
        request = ImageToPdfRequest(
            page_size=page_size_enum,
            margin=margin,
            fit_to_page=fit_to_page
        )
        
        # Convert images to PDF
        # Use simplified method for better compatibility
        pdf_bytes = image_to_pdf_simple(
            image_buffers,
            page_size=page_size_enum,
            fit_to_page=fit_to_page
        )
        
        # Generate filename
        first_name = files[0].filename or "images"
        base_name = first_name.rsplit('.', 1)[0]
        filename = f"{base_name}_combined.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting images to PDF: {str(e)}")
