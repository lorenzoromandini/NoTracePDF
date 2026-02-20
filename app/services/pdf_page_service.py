"""
PDF Page Dimension Service.

Provides crop, scale, and resize operations for PDF pages
using pikepdf with in-memory processing.

Reference: PDF-17, PDF-18, PDF-19
Constraint: All operations use BytesIO (ARCH-01)
"""
from io import BytesIO
from typing import Union, List, Optional
import math

import pikepdf

from app.utils.file_utils import (
    InvalidPageError,
    validate_page_numbers,
)


def crop_pages(
    file: BytesIO,
    left: float,
    right: float,
    top: float,
    bottom: float,
    pages: Union[str, List[int]] = "all"
) -> BytesIO:
    """
    Crop PDF pages to specific dimensions.
    
    This sets the CropBox for specified pages, effectively hiding
    content outside the crop region.
    
    Args:
        file: PDF BytesIO object
        left: Left margin in points (from left edge)
        right: Right margin in points (from right edge)
        top: Top margin in points (from top edge)
        bottom: Bottom margin in points (from bottom edge)
        pages: 'all' or list of page numbers (1-indexed)
        
    Returns:
        BytesIO: Cropped PDF
        
    Raises:
        InvalidPageError: If page numbers are invalid
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Determine which pages to crop
        if pages == "all":
            pages_to_process = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            pages_to_process = [p - 1 for p in pages]  # Convert to 0-indexed
        
        for page_idx in pages_to_process:
            page = pdf.pages[page_idx]
            
            # Get current MediaBox
            mediabox = page.mediabox
            if mediabox is None:
                continue
                
            # MediaBox is [x0, y0, x1, y1]
            x0 = float(mediabox[0])
            y0 = float(mediabox[1])
            x1 = float(mediabox[2])
            y1 = float(mediabox[3])
            
            # Calculate new CropBox
            # left/right are from edges, top/bottom from edges
            new_x0 = x0 + left
            new_y0 = y0 + bottom
            new_x1 = x1 - right
            new_y1 = y1 - top
            
            # Validate crop dimensions
            if new_x0 >= new_x1 or new_y0 >= new_y1:
                raise InvalidPageError(
                    f"Invalid crop dimensions for page {page_idx + 1}: "
                    f"crop region would be empty or inverted"
                )
            
            # Set CropBox
            page.CropBox = pikepdf.Rectangle(new_x0, new_y0, new_x1, new_y1)
        
        pdf.save(output)
    
    output.seek(0)
    return output


def scale_pages(
    file: BytesIO,
    scale: float,
    pages: Union[str, List[int]] = "all"
) -> BytesIO:
    """
    Scale page content by a factor.
    
    This scales the page content while keeping the page size the same.
    Content is scaled around the center of the page.
    
    Args:
        file: PDF BytesIO object
        scale: Scale factor (e.g., 0.5 = 50%, 2.0 = 200%)
        pages: 'all' or list of page numbers (1-indexed)
        
    Returns:
        BytesIO: Scaled PDF
        
    Raises:
        InvalidPageError: If page numbers are invalid
        ValueError: If scale factor is invalid
    """
    if scale <= 0:
        raise ValueError("Scale factor must be positive")
    
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Determine which pages to scale
        if pages == "all":
            pages_to_process = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            pages_to_process = [p - 1 for p in pages]
        
        for page_idx in pages_to_process:
            page = pdf.pages[page_idx]
            
            # Get page dimensions
            mediabox = page.mediabox
            if mediabox is None:
                continue
            
            page_width = float(mediabox[2]) - float(mediabox[0])
            page_height = float(mediabox[3]) - float(mediabox[1])
            
            # Calculate center point
            center_x = page_width / 2
            center_y = page_height / 2
            
            # Create transformation matrix for scaling around center
            # The transformation: translate to origin, scale, translate back
            # Matrix: [sx 0 0 sy tx ty]
            # For scaling around center:
            # tx = center_x - scale * center_x = center_x * (1 - scale)
            # ty = center_y - scale * center_y = center_y * (1 - scale)
            
            tx = center_x * (1 - scale)
            ty = center_y * (1 - scale)
            
            # Create the content stream for transformation
            transform_content = f"q {scale} 0 0 {scale} {tx:.2f} {ty:.2f} cm\n".encode()
            
            # Get or create page contents
            if '/Contents' in page:
                existing = page['/Contents']
                if isinstance(existing, pikepdf.Array):
                    # Multiple content streams - prepend transformation
                    stream = pdf.make_stream(transform_content)
                    new_contents = pikepdf.Array([stream] + list(existing))
                    page['/Contents'] = new_contents
                else:
                    # Single content stream - prepend transformation
                    stream = pdf.make_stream(transform_content)
                    new_contents = pikepdf.Array([stream, existing])
                    page['/Contents'] = new_contents
            else:
                # No existing content
                stream = pdf.make_stream(transform_content + b"\nQ\n")
                page['/Contents'] = stream
                continue
            
            # Add closing Q at the end
            if isinstance(page['/Contents'], pikepdf.Array) and len(page['/Contents']) > 0:
                last_stream = page['/Contents'][-1]
                if hasattr(last_stream, 'read_bytes'):
                    existing_content = last_stream.read_bytes()
                    new_content = existing_content + b"\nQ\n"
                    page['/Contents'][-1] = pdf.make_stream(new_content)
                else:
                    # Add Q as separate stream
                    page['/Contents'].append(pdf.make_stream(b"Q\n"))
        
        pdf.save(output)
    
    output.seek(0)
    return output


def resize_pages(
    file: BytesIO,
    width: float,
    height: float,
    pages: Union[str, List[int]] = "all"
) -> BytesIO:
    """
    Resize page canvas to specified dimensions.
    
    This changes the page MediaBox size without scaling the content.
    Content position is preserved.
    
    Args:
        file: PDF BytesIO object
        width: New page width in points
        height: New page height in points
        pages: 'all' or list of page numbers (1-indexed)
        
    Returns:
        BytesIO: Resized PDF
        
    Raises:
        InvalidPageError: If page numbers are invalid
        ValueError: If dimensions are invalid
    """
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")
    
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Determine which pages to resize
        if pages == "all":
            pages_to_process = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            pages_to_process = [p - 1 for p in pages]
        
        for page_idx in pages_to_process:
            page = pdf.pages[page_idx]
            
            # Set new MediaBox
            # Origin is at (0, 0), so MediaBox is [0, 0, width, height]
            page.MediaBox = pikepdf.Rectangle(0, 0, width, height)
        
        pdf.save(output)
    
    output.seek(0)
    return output


def get_page_dimensions(file: BytesIO) -> List[dict]:
    """
    Get dimensions of all pages in a PDF.
    
    Args:
        file: PDF BytesIO object
        
    Returns:
        List of dicts with page dimensions
    """
    file.seek(0)
    
    with pikepdf.Pdf.open(file) as pdf:
        dimensions = []
        
        for i, page in enumerate(pdf.pages):
            mediabox = page.mediabox
            if mediabox is not None:
                width = float(mediabox[2]) - float(mediabox[0])
                height = float(mediabox[3]) - float(mediabox[1])
                
                # Also check for CropBox
                cropbox = page.get('/CropBox')
                if cropbox is not None:
                    crop_width = float(cropbox[2]) - float(cropbox[0])
                    crop_height = float(cropbox[3]) - float(cropbox[1])
                else:
                    crop_width = width
                    crop_height = height
                
                dimensions.append({
                    "page": i + 1,
                    "width": round(width, 2),
                    "height": round(height, 2),
                    "width_mm": round(width * 25.4 / 72, 2),
                    "height_mm": round(height * 25.4 / 72, 2),
                    "crop_width": round(crop_width, 2),
                    "crop_height": round(crop_height, 2),
                })
            else:
                dimensions.append({
                    "page": i + 1,
                    "width": None,
                    "height": None,
                    "width_mm": None,
                    "height_mm": None,
                    "crop_width": None,
                    "crop_height": None,
                })
        
        return dimensions
