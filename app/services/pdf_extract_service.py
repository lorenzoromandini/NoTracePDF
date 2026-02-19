"""
PDF Extraction Service.

Provides text, image, and page extraction functionality
using PyMuPDF (fitz) for high-performance in-memory processing.

Reference: PDF-14 to PDF-16
"""
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
import re

import fitz  # PyMuPDF
from PIL import Image

from app.schemas.pdf import ImageFormat, ExtractTextResponse, PageText
from app.utils.file_utils import (
    InvalidPageError,
    validate_page_numbers,
    create_zip_archive,
)


def extract_text(
    file: BytesIO,
    pages: Optional[List[int]] = None
) -> ExtractTextResponse:
    """
    Extract text from PDF.
    
    Args:
        file: PDF BytesIO object
        pages: Optional list of page numbers (1-indexed), None for all
        
    Returns:
        ExtractTextResponse: Structured text extraction result
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        # Determine which pages to extract
        if pages is None:
            page_indices = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            page_indices = [p - 1 for p in pages]  # Convert to 0-indexed
        
        page_results = []
        total_chars = 0
        
        for page_idx in page_indices:
            page = doc[page_idx]
            text = page.get_text("text")
            cleaned_text = clean_text(text)
            char_count = len(cleaned_text)
            total_chars += char_count
            
            page_results.append(PageText(
                page_number=page_idx + 1,
                text=cleaned_text,
                character_count=char_count
            ))
        
        return ExtractTextResponse(
            total_pages=total_pages,
            total_characters=total_chars,
            pages=page_results
        )
    finally:
        doc.close()


def extract_images(
    file: BytesIO,
    pages: Optional[List[int]] = None,
    format: ImageFormat = ImageFormat.ORIGINAL
) -> List[Tuple[str, BytesIO]]:
    """
    Extract images from PDF.
    
    Args:
        file: PDF BytesIO object
        pages: Optional list of page numbers (1-indexed), None for all
        format: Output format for images
        
    Returns:
        List of (filename, BytesIO) tuples
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        # Determine which pages
        if pages is None:
            page_indices = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            page_indices = [p - 1 for p in pages]
        
        results = []
        image_counter = 1
        
        for page_idx in page_indices:
            page = doc[page_idx]
            image_list = page.get_images(full=True)
            
            for img_info in image_list:
                xref = img_info[0]
                
                # Extract image
                base_image = doc.extract_image(xref)
                if base_image is None:
                    continue
                
                img_bytes = base_image["image"]
                img_ext = base_image["ext"]
                
                # Convert format if needed
                if format != ImageFormat.ORIGINAL:
                    img_bytes, img_ext = _convert_image_format(
                        img_bytes,
                        target_format=format.value
                    )
                
                # Generate filename
                filename = f"image_{image_counter:03d}.{img_ext}"
                results.append((filename, BytesIO(img_bytes)))
                image_counter += 1
        
        return results
    finally:
        doc.close()


def extract_pages(
    file: BytesIO,
    pages: List[int]
) -> List[Tuple[str, BytesIO]]:
    """
    Extract pages as separate PDF files.
    
    Args:
        file: PDF BytesIO object
        pages: List of page numbers to extract (1-indexed)
        
    Returns:
        List of (filename, BytesIO) tuples
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        validate_page_numbers(pages, total_pages)
        
        results = []
        
        for page_num in pages:
            # Create new PDF with single page
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
            
            # Save to bytes
            output = BytesIO()
            new_doc.save(output)
            output.seek(0)
            new_doc.close()
            
            filename = f"page_{page_num:03d}.pdf"
            results.append((filename, output))
        
        return results
    finally:
        doc.close()


def clean_text(text: str) -> str:
    """
    Clean extracted text.
    
    - Remove excessive whitespace
    - Normalize line endings
    - Handle special characters
    
    Args:
        text: Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive whitespace (more than 2 consecutive spaces/newlines)
    text = re.sub(r' {3,}', '  ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def _convert_image_format(
    img_bytes: bytes,
    target_format: str
) -> Tuple[bytes, str]:
    """
    Convert image to target format.
    
    Args:
        img_bytes: Original image bytes
        target_format: Target format (png, jpg, webp)
        
    Returns:
        Tuple[bytes, str]: (Converted bytes, file extension)
    """
    img = Image.open(BytesIO(img_bytes))
    output = BytesIO()
    
    # Handle transparency for formats that don't support it
    if target_format == 'jpg' and img.mode in ('RGBA', 'P'):
        # Convert to RGB for JPEG
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Save in target format
    format_map = {
        'png': ('PNG', 'png'),
        'jpg': ('JPEG', 'jpg'),
        'jpeg': ('JPEG', 'jpg'),
        'webp': ('WEBP', 'webp'),
    }
    
    pil_format, ext = format_map.get(target_format.lower(), ('PNG', 'png'))
    
    if pil_format == 'JPEG':
        img.save(output, format=pil_format, quality=85)
    else:
        img.save(output, format=pil_format)
    
    return output.getvalue(), ext


def get_pdf_metadata(file: BytesIO) -> Dict[str, Any]:
    """
    Get PDF metadata.
    
    Args:
        file: PDF BytesIO object
        
    Returns:
        Dict with metadata
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    try:
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": len(doc),
        }
    finally:
        doc.close()
