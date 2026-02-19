"""
PDF API Endpoints.

All endpoints use in-memory processing with BytesIO.
No user data is written to disk.

Reference: PDF-01 to PDF-16
"""
from io import BytesIO
from typing import List, Optional
import json

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from app.schemas.pdf import (
    SplitMode,
    WatermarkPosition,
    PageSelection,
    QualityPreset,
    ImageFormat,
)
from app.services.pdf_service import (
    merge_pdfs,
    split_pdf,
    rotate_pages,
    reorder_pages,
    delete_pages,
)
from app.services.pdf_security_service import (
    compress_pdf,
    add_password,
    remove_password,
    set_permissions,
)
from app.services.pdf_watermark_service import (
    add_text_watermark,
    add_image_watermark,
)
from app.services.pdf_extract_service import (
    extract_text,
    extract_images,
    extract_pages,
)
from app.utils.file_utils import (
    validate_pdf,
    validate_image,
    generate_filename,
    create_zip_archive,
    InvalidPageError,
    EmptyResultError,
    FileValidationError,
)


router = APIRouter(prefix="/pdf", tags=["PDF Operations"])


# ==================== MERGE ====================

@router.post("/merge")
async def api_merge_pdfs(
    files: List[UploadFile] = File(..., description="PDF files to merge")
):
    """
    Merge multiple PDFs into a single document.
    
    Accepts multiple PDF files and returns a merged PDF.
    All processing is done in-memory.
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 PDF files are required for merging"
        )
    
    try:
        # Validate and load all PDFs
        pdf_buffers = []
        for file in files:
            pdf_bytes = await validate_pdf(file)
            pdf_buffers.append(pdf_bytes)
        
        # Merge PDFs
        merged_pdf = merge_pdfs(pdf_buffers)
        
        # Generate filename
        first_name = files[0].filename or "document"
        filename = generate_filename("merged", first_name)
        
        return StreamingResponse(
            merged_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging PDFs: {str(e)}")


# ==================== SPLIT ====================

@router.post("/split")
async def api_split_pdf(
    file: UploadFile = File(..., description="PDF file to split"),
    mode: str = Form(..., description="Split mode: range, every_n, or specific"),
    start: Optional[int] = Form(None, description="Start page for range mode"),
    end: Optional[int] = Form(None, description="End page for range mode"),
    n_pages: Optional[int] = Form(None, description="Split every N pages"),
    pages: Optional[str] = Form(None, description="JSON array of page numbers for specific mode")
):
    """
    Split PDF by page range, every N pages, or extract specific pages.
    
    - mode=range: Extract pages from 'start' to 'end'
    - mode=every_n: Split into chunks of 'n_pages' pages each
    - mode=specific: Extract specific pages (provide 'pages' as JSON array)
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse mode
        try:
            split_mode = SplitMode(mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Must be one of: {', '.join([m.value for m in SplitMode])}"
            )
        
        # Parse pages if provided
        pages_list = None
        if pages:
            try:
                pages_list = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format. Must be JSON array.")
        
        # Split PDF
        results = split_pdf(
            pdf_bytes,
            mode=split_mode,
            start=start,
            end=end,
            n_pages=n_pages,
            pages=pages_list
        )
        
        if len(results) == 1:
            # Single file - return directly
            filename, content = results[0]
            return StreamingResponse(
                content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        else:
            # Multiple files - return as ZIP
            zip_content = create_zip_archive(results)
            base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
            return StreamingResponse(
                zip_content,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{base_name}_split.zip"'
                }
            )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error splitting PDF: {str(e)}")


# ==================== ROTATE ====================

@router.post("/rotate")
async def api_rotate_pages(
    file: UploadFile = File(..., description="PDF file"),
    pages: str = Form("all", description="Pages to rotate: 'all' or JSON array of page numbers"),
    degrees: int = Form(..., description="Rotation angle: 90, 180, or 270")
):
    """
    Rotate pages in PDF.
    
    - pages: 'all' to rotate all pages, or JSON array like [1, 3, 5]
    - degrees: Rotation angle (90, 180, or 270)
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse pages
        if pages == "all":
            pages_to_rotate = "all"
        else:
            try:
                pages_to_rotate = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format. Must be 'all' or JSON array.")
        
        # Rotate pages
        rotated_pdf = rotate_pages(pdf_bytes, pages_to_rotate, degrees)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_rotated.pdf"
        
        return StreamingResponse(
            rotated_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rotating pages: {str(e)}")


# ==================== REORDER ====================

@router.post("/reorder")
async def api_reorder_pages(
    file: UploadFile = File(..., description="PDF file"),
    page_order: str = Form(..., description="New page order as JSON array (1-indexed)")
):
    """
    Reorder pages in PDF.
    
    page_order: JSON array representing new order, e.g., [3, 1, 2, 4]
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse page order
        try:
            order = json.loads(page_order)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid page_order format. Must be JSON array.")
        
        # Reorder pages
        reordered_pdf = reorder_pages(pdf_bytes, order)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_reordered.pdf"
        
        return StreamingResponse(
            reordered_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reordering pages: {str(e)}")


# ==================== DELETE PAGES ====================

@router.post("/delete-pages")
async def api_delete_pages(
    file: UploadFile = File(..., description="PDF file"),
    pages: str = Form(..., description="Pages to delete as JSON array (1-indexed)")
):
    """
    Delete pages from PDF.
    
    pages: JSON array of page numbers to delete, e.g., [2, 5, 7]
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse pages
        try:
            pages_to_delete = json.loads(pages)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid pages format. Must be JSON array.")
        
        # Delete pages
        modified_pdf = delete_pages(pdf_bytes, pages_to_delete)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_modified.pdf"
        
        return StreamingResponse(
            modified_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EmptyResultError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting pages: {str(e)}")


# ==================== COMPRESS ====================

@router.post("/compress")
async def api_compress_pdf(
    file: UploadFile = File(..., description="PDF file"),
    quality: str = Form("medium", description="Quality preset: low, medium, or high")
):
    """
    Compress PDF with quality presets.
    
    quality:
    - low: 72 DPI, aggressive compression (smallest file)
    - medium: 150 DPI, balanced compression
    - high: 300 DPI, minimal compression (best quality)
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse quality
        try:
            quality_preset = QualityPreset(quality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quality. Must be one of: {', '.join([q.value for q in QualityPreset])}"
            )
        
        # Compress PDF
        compressed_pdf = compress_pdf(pdf_bytes, quality_preset)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_compressed.pdf"
        
        return StreamingResponse(
            compressed_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compressing PDF: {str(e)}")


# ==================== PASSWORD ====================

@router.post("/password/add")
async def api_add_password(
    file: UploadFile = File(..., description="PDF file"),
    password: str = Form(..., description="Password to set"),
    permissions: Optional[str] = Form(None, description="JSON array of allowed permissions")
):
    """
    Add password protection to PDF.
    
    permissions (optional): JSON array of allowed permissions:
    - print: Allow printing
    - copy: Allow copying content
    - edit: Allow editing
    - annotate: Allow annotations
    - fill_forms: Allow form filling
    - extract: Allow content extraction
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse permissions
        perms_list = None
        if permissions:
            try:
                perms_list = json.loads(permissions)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid permissions format. Must be JSON array.")
        
        # Add password
        encrypted_pdf = add_password(pdf_bytes, password, perms_list)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_protected.pdf"
        
        return StreamingResponse(
            encrypted_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding password: {str(e)}")


@router.post("/password/remove")
async def api_remove_password(
    file: UploadFile = File(..., description="Encrypted PDF file"),
    password: str = Form(..., description="Current password")
):
    """
    Remove password protection from PDF.
    
    Requires the current password to decrypt.
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Remove password
        decrypted_pdf = remove_password(pdf_bytes, password)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_decrypted.pdf"
        
        return StreamingResponse(
            decrypted_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing password: {str(e)}")


# ==================== WATERMARK ====================

@router.post("/watermark/text")
async def api_add_text_watermark(
    file: UploadFile = File(..., description="PDF file"),
    text: str = Form(..., description="Watermark text"),
    font_size: int = Form(48, description="Font size"),
    color: str = Form("#808080", description="Hex color code"),
    opacity: float = Form(0.3, description="Opacity (0.0 to 1.0)"),
    position: str = Form("diagonal", description="Position: center, diagonal, top-left, etc."),
    pages: str = Form("all", description="Pages to watermark: all, first, last, or JSON array")
):
    """
    Add text watermark to PDF.
    
    position options: center, diagonal, top-left, top-right, bottom-left, bottom-right
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse position
        try:
            position_enum = WatermarkPosition(position)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid position. Must be one of: {', '.join([p.value for p in WatermarkPosition])}"
            )
        
        # Parse pages
        if pages in ("all", "first", "last"):
            pages_value = PageSelection(pages)
        else:
            try:
                pages_value = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format.")
        
        # Import and create request
        from app.schemas.pdf import TextWatermarkRequest
        request = TextWatermarkRequest(
            text=text,
            font_size=font_size,
            color=color,
            opacity=opacity,
            position=position_enum,
            pages=pages_value
        )
        
        # Add watermark
        watermarked_pdf = add_text_watermark(pdf_bytes, request)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_watermarked.pdf"
        
        return StreamingResponse(
            watermarked_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding watermark: {str(e)}")


@router.post("/watermark/image")
async def api_add_image_watermark(
    file: UploadFile = File(..., description="PDF file"),
    image: UploadFile = File(..., description="Watermark image"),
    opacity: float = Form(0.3, description="Opacity (0.0 to 1.0)"),
    position: str = Form("center", description="Position"),
    scale: float = Form(0.5, description="Scale relative to page (0.1 to 1.0)"),
    pages: str = Form("all", description="Pages to watermark")
):
    """
    Add image watermark to PDF.
    
    Supports PNG with transparency.
    """
    try:
        pdf_bytes = await validate_pdf(file)
        image_bytes, _ = await validate_image(image)
        
        # Parse position
        try:
            position_enum = WatermarkPosition(position)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid position. Must be one of: {', '.join([p.value for p in WatermarkPosition])}"
            )
        
        # Parse pages
        if pages in ("all", "first", "last"):
            pages_value = PageSelection(pages)
        else:
            try:
                pages_value = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format.")
        
        # Import and create request
        from app.schemas.pdf import ImageWatermarkRequest
        request = ImageWatermarkRequest(
            opacity=opacity,
            position=position_enum,
            scale=scale,
            pages=pages_value
        )
        
        # Add watermark
        watermarked_pdf = add_image_watermark(pdf_bytes, image_bytes, request)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}_watermarked.pdf"
        
        return StreamingResponse(
            watermarked_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding watermark: {str(e)}")


# ==================== EXTRACT ====================

@router.post("/extract/text")
async def api_extract_text(
    file: UploadFile = File(..., description="PDF file"),
    pages: Optional[str] = Form(None, description="Pages to extract as JSON array (optional)")
):
    """
    Extract text from PDF.
    
    Returns JSON with text content organized by page.
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse pages
        pages_list = None
        if pages:
            try:
                pages_list = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format. Must be JSON array.")
        
        # Extract text
        result = extract_text(pdf_bytes, pages_list)
        
        return JSONResponse(content=result.model_dump())
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")


@router.post("/extract/images")
async def api_extract_images(
    file: UploadFile = File(..., description="PDF file"),
    pages: Optional[str] = Form(None, description="Pages to extract from as JSON array"),
    format: str = Form("original", description="Output format: png, jpg, webp, or original")
):
    """
    Extract images from PDF.
    
    Returns ZIP archive of extracted images.
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse pages
        pages_list = None
        if pages:
            try:
                pages_list = json.loads(pages)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid pages format.")
        
        # Parse format
        try:
            format_enum = ImageFormat(format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Must be one of: {', '.join([f.value for f in ImageFormat])}"
            )
        
        # Extract images
        results = extract_images(pdf_bytes, pages_list, format_enum)
        
        if not results:
            raise HTTPException(status_code=404, detail="No images found in PDF")
        
        # Create ZIP archive
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting images: {str(e)}")


@router.post("/extract/pages")
async def api_extract_pages(
    file: UploadFile = File(..., description="PDF file"),
    pages: str = Form(..., description="Pages to extract as JSON array (1-indexed)")
):
    """
    Extract pages as separate PDF files.
    
    Returns ZIP archive of individual page PDFs.
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Parse pages
        try:
            pages_list = json.loads(pages)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid pages format. Must be JSON array.")
        
        # Extract pages
        results = extract_pages(pdf_bytes, pages_list)
        
        if len(results) == 1:
            # Single page - return directly
            filename, content = results[0]
            return StreamingResponse(
                content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        else:
            # Multiple pages - return as ZIP
            zip_content = create_zip_archive(results)
            base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
            
            return StreamingResponse(
                zip_content,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{base_name}_pages.zip"'
                }
            )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting pages: {str(e)}")
