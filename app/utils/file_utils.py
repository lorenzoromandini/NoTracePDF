"""
File handling utilities for in-memory processing.

All functions work with BytesIO to maintain zero-trace guarantee.
NO files are written to disk for user data.

Reference: ARCH-01, ARCH-06
"""
import zipfile
import os
from io import BytesIO
from typing import List, Tuple, Optional
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.core.config import settings


# Allowed MIME types for uploads
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"
}
ALLOWED_OFFICE_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
    "application/msword",  # doc (legacy)
    "application/vnd.ms-excel",  # xls (legacy)
    "application/vnd.ms-powerpoint",  # ppt (legacy)
    "application/rtf",  # rtf
    "text/rtf",  # rtf alternate
}
ALLOWED_ALL_TYPES = ALLOWED_PDF_TYPES | ALLOWED_IMAGE_TYPES | ALLOWED_OFFICE_TYPES


class FileValidationError(HTTPException):
    """Raised when file validation fails."""
    pass


class InvalidPageError(Exception):
    """Raised when page number is out of range."""
    pass


class InvalidRotationError(Exception):
    """Raised when rotation value is invalid."""
    pass


class EmptyResultError(Exception):
    """Raised when operation would result in empty output."""
    pass


async def validate_pdf(file: UploadFile) -> BytesIO:
    """
    Validate PDF file and return as BytesIO for in-memory processing.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        BytesIO: File content in memory
        
    Raises:
        FileValidationError: If file is invalid
    """
    # Check content type
    if file.content_type not in ALLOWED_PDF_TYPES:
        # Some browsers may not send correct content-type, check extension
        filename = file.filename or ""
        if not filename.lower().endswith('.pdf'):
            raise FileValidationError(
                status_code=415,
                detail=f"Invalid file type: {file.content_type}. Expected PDF."
            )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    # Check if empty
    if len(content) == 0:
        raise FileValidationError(
            status_code=400,
            detail="Empty file provided."
        )
    
    # Basic PDF header check
    if not content.startswith(b'%PDF-'):
        raise FileValidationError(
            status_code=400,
            detail="Invalid PDF file. File does not start with PDF header."
        )
    
    return BytesIO(content)


async def validate_image(file: UploadFile) -> Tuple[BytesIO, str]:
    """
    Validate image file and return as BytesIO for in-memory processing.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        Tuple[BytesIO, str]: (File content in memory, detected format)
        
    Raises:
        FileValidationError: If file is invalid
    """
    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        # Check extension as fallback
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}:
            raise FileValidationError(
                status_code=415,
                detail=f"Invalid file type: {file.content_type}. Expected image."
            )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    # Check if empty
    if len(content) == 0:
        raise FileValidationError(
            status_code=400,
            detail="Empty file provided."
        )
    
    # Detect format from content
    detected_format = detect_image_format(content)
    
    return BytesIO(content), detected_format


async def validate_any_file(file: UploadFile) -> Tuple[BytesIO, str]:
    """
    Validate any allowed file type (PDF or image).
    
    Returns:
        Tuple[BytesIO, str]: (File content, file type category: 'pdf' or 'image')
    """
    if file.content_type in ALLOWED_PDF_TYPES:
        content = await validate_pdf(file)
        return content, 'pdf'
    elif file.content_type in ALLOWED_IMAGE_TYPES:
        content, _ = await validate_image(file)
        return content, 'image'
    else:
        # Check extension
        filename = file.filename or ""
        if filename.lower().endswith('.pdf'):
            content = await validate_pdf(file)
            return content, 'pdf'
        else:
            content, _ = await validate_image(file)
            return content, 'image'


def detect_image_format(content: bytes) -> str:
    """
    Detect image format from file content using magic bytes.
    
    Args:
        content: Raw file bytes
        
    Returns:
        str: Detected format (png, jpeg, gif, webp, bmp, or unknown)
    """
    if content.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif content.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
        return 'gif'
    elif content.startswith(b'RIFF') and content[8:12] == b'WEBP':
        return 'webp'
    elif content.startswith(b'BM'):
        return 'bmp'
    else:
        return 'unknown'


def generate_filename(operation: str, original_name: str, suffix: str = "") -> str:
    """
    Generate a sensible download filename.
    
    Args:
        operation: Operation type (merge, split, rotate, etc.)
        original_name: Original filename
        suffix: Optional suffix
        
    Returns:
        str: Generated filename
    """
    # Get base name without extension
    base = Path(original_name).stem
    if suffix:
        return f"{base}_{operation}_{suffix}.pdf"
    return f"{base}_{operation}.pdf"


def create_zip_archive(files: List[Tuple[str, BytesIO]]) -> BytesIO:
    """
    Create an in-memory ZIP archive from list of files.
    
    Args:
        files: List of (filename, BytesIO) tuples
        
    Returns:
        BytesIO: ZIP archive in memory
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files:
            content.seek(0)
            zf.writestr(filename, content.read())
    
    zip_buffer.seek(0)
    return zip_buffer


def get_page_count(pdf_bytes: BytesIO) -> int:
    """
    Get the number of pages in a PDF.
    
    Args:
        pdf_bytes: PDF content as BytesIO
        
    Returns:
        int: Number of pages
    """
    import pikepdf
    
    pdf_bytes.seek(0)
    with pikepdf.Pdf.open(pdf_bytes) as pdf:
        return len(pdf.pages)


def validate_page_numbers(pages: List[int], total_pages: int) -> None:
    """
    Validate that page numbers are within range.
    
    Args:
        pages: List of page numbers (1-indexed)
        total_pages: Total number of pages in PDF
        
    Raises:
        InvalidPageError: If any page is out of range
    """
    for page in pages:
        if page < 1 or page > total_pages:
            raise InvalidPageError(
                f"Page {page} is out of range. PDF has {total_pages} pages."
            )


async def validate_docx(file: UploadFile) -> BytesIO:
    """
    Validate Word document (.docx) and return as BytesIO.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        BytesIO: File content in memory
        
    Raises:
        FileValidationError: If file is invalid
    """
    # Check content type or extension
    valid_types = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }
    
    filename = file.filename or ""
    if file.content_type not in valid_types and not filename.lower().endswith(('.docx', '.doc')):
        raise FileValidationError(
            status_code=415,
            detail=f"Invalid file type: {file.content_type}. Expected Word document."
        )
    
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    if len(content) == 0:
        raise FileValidationError(status_code=400, detail="Empty file provided.")
    
    # Check for Office file signature (ZIP format)
    if not content.startswith(b'PK'):
        raise FileValidationError(
            status_code=400,
            detail="Invalid Word document. File does not have expected format."
        )
    
    return BytesIO(content)


async def validate_xlsx(file: UploadFile) -> BytesIO:
    """
    Validate Excel spreadsheet (.xlsx) and return as BytesIO.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        BytesIO: File content in memory
        
    Raises:
        FileValidationError: If file is invalid
    """
    valid_types = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    }
    
    filename = file.filename or ""
    if file.content_type not in valid_types and not filename.lower().endswith(('.xlsx', '.xls')):
        raise FileValidationError(
            status_code=415,
            detail=f"Invalid file type: {file.content_type}. Expected Excel spreadsheet."
        )
    
    content = await file.read()
    
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    if len(content) == 0:
        raise FileValidationError(status_code=400, detail="Empty file provided.")
    
    if not content.startswith(b'PK'):
        raise FileValidationError(
            status_code=400,
            detail="Invalid Excel file. File does not have expected format."
        )
    
    return BytesIO(content)


async def validate_pptx(file: UploadFile) -> BytesIO:
    """
    Validate PowerPoint presentation (.pptx) and return as BytesIO.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        BytesIO: File content in memory
        
    Raises:
        FileValidationError: If file is invalid
    """
    valid_types = {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
    }
    
    filename = file.filename or ""
    if file.content_type not in valid_types and not filename.lower().endswith(('.pptx', '.ppt')):
        raise FileValidationError(
            status_code=415,
            detail=f"Invalid file type: {file.content_type}. Expected PowerPoint presentation."
        )
    
    content = await file.read()
    
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    if len(content) == 0:
        raise FileValidationError(status_code=400, detail="Empty file provided.")
    
    if not content.startswith(b'PK'):
        raise FileValidationError(
            status_code=400,
            detail="Invalid PowerPoint file. File does not have expected format."
        )
    
    return BytesIO(content)


async def validate_rtf(file: UploadFile) -> BytesIO:
    """
    Validate RTF document and return as BytesIO.
    
    Args:
        file: UploadFile from FastAPI
        
    Returns:
        BytesIO: File content in memory
        
    Raises:
        FileValidationError: If file is invalid
    """
    valid_types = {"application/rtf", "text/rtf"}
    
    filename = file.filename or ""
    if file.content_type not in valid_types and not filename.lower().endswith('.rtf'):
        raise FileValidationError(
            status_code=415,
            detail=f"Invalid file type: {file.content_type}. Expected RTF document."
        )
    
    content = await file.read()
    
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    if len(content) == 0:
        raise FileValidationError(status_code=400, detail="Empty file provided.")
    
    # RTF files start with {\rtf1
    if not content.startswith(b'{\\rtf'):
        raise FileValidationError(
            status_code=400,
            detail="Invalid RTF file. File does not have RTF header."
        )
    
    return BytesIO(content)
