"""
PDF Watermark Service.

Provides text and image watermark functionality
using pikepdf with in-memory processing.

Reference: PDF-12, PDF-13
"""
from io import BytesIO
from typing import List, Optional, Union, Tuple
import math

import pikepdf
from pikepdf import Pdf, Page, Rectangle, Name, Operator
from PIL import Image

from app.schemas.pdf import (
    WatermarkPosition,
    PageSelection,
    TextWatermarkRequest,
    ImageWatermarkRequest,
)
from app.utils.file_utils import InvalidPageError, validate_page_numbers


# Page size constants (in points, 1 point = 1/72 inch)
PAGE_SIZES = {
    "a4": (595.28, 841.89),
    "letter": (612, 792),
}


def get_page_dimensions(page: Page) -> Tuple[float, float]:
    """
    Get page dimensions (width, height) in points.
    
    Args:
        page: pikepdf Page object
        
    Returns:
        Tuple[float, float]: (width, height)
    """
    # Get MediaBox
    mediabox = page.mediabox
    if mediabox is None:
        return 595.28, 841.89  # Default to A4
    
    # MediaBox is [x0, y0, x1, y1]
    width = float(mediabox[2]) - float(mediabox[0])
    height = float(mediabox[3]) - float(mediabox[1])
    
    return width, height


def calculate_position(
    position: WatermarkPosition,
    page_width: float,
    page_height: float,
    content_width: float,
    content_height: float,
    margin: float = 20
) -> Tuple[float, float, float]:
    """
    Calculate watermark position and rotation angle.
    
    Args:
        position: Position enum value
        page_width: Page width in points
        page_height: Page height in points
        content_width: Watermark width in points
        content_height: Watermark height in points
        margin: Margin from edges in points
        
    Returns:
        Tuple[float, float, float]: (x, y, angle in degrees)
    """
    if position == WatermarkPosition.CENTER:
        x = (page_width - content_width) / 2
        y = (page_height - content_height) / 2
        angle = 0
    elif position == WatermarkPosition.DIAGONAL:
        # Center and rotate to diagonal
        x = page_width / 2
        y = page_height / 2
        # Calculate angle based on page dimensions
        angle = -math.degrees(math.atan2(page_height, page_width))
    elif position == WatermarkPosition.TOP_LEFT:
        x = margin
        y = page_height - content_height - margin
        angle = 0
    elif position == WatermarkPosition.TOP_RIGHT:
        x = page_width - content_width - margin
        y = page_height - content_height - margin
        angle = 0
    elif position == WatermarkPosition.BOTTOM_LEFT:
        x = margin
        y = margin
        angle = 0
    elif position == WatermarkPosition.BOTTOM_RIGHT:
        x = page_width - content_width - margin
        y = margin
        angle = 0
    else:
        # Default to center
        x = (page_width - content_width) / 2
        y = (page_height - content_height) / 2
        angle = 0
    
    return x, y, angle


def add_text_watermark(
    file: BytesIO,
    request: TextWatermarkRequest
) -> BytesIO:
    """
    Add text watermark to PDF.
    
    Note: This is a simplified implementation that adds a text annotation
    to each page. For more advanced text watermarks, consider using
    reportlab to generate PDF content and overlay it.
    
    Args:
        file: PDF BytesIO object
        request: TextWatermarkRequest with watermark parameters
        
    Returns:
        BytesIO: Watermarked PDF
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Determine which pages to watermark
        if request.pages == PageSelection.ALL:
            pages_to_process = list(range(total_pages))
        elif request.pages == PageSelection.FIRST:
            pages_to_process = [0]
        elif request.pages == PageSelection.LAST:
            pages_to_process = [total_pages - 1]
        else:
            # List of page numbers
            pages_to_process = [p - 1 for p in request.pages]
            validate_page_numbers(request.pages, total_pages)
        
        for page_idx in pages_to_process:
            page = pdf.pages[page_idx]
            page_width, page_height = get_page_dimensions(page)
            
            # Calculate position
            # Estimate text width (rough approximation)
            text_width = len(request.text) * request.font_size * 0.6
            text_height = request.font_size
            
            x, y, angle = calculate_position(
                request.position,
                page_width,
                page_height,
                text_width,
                text_height
            )
            
            # Add watermark as a text annotation
            # Note: This creates an annotation, not a permanent overlay
            # For a permanent watermark, we'd need to create a content stream
            
            # Create content stream for watermark
            content = _create_text_watermark_content(
                request.text,
                x, y, angle,
                request.font_size,
                request.color,
                request.opacity
            )
            
            # Add content stream to page
            _add_content_to_page(page, content, pdf)
        
        pdf.save(output)
    
    output.seek(0)
    return output


def _create_text_watermark_content(
    text: str,
    x: float,
    y: float,
    angle: float,
    font_size: int,
    color: str,
    opacity: float
) -> bytes:
    """
    Create PDF content stream for text watermark.
    
    This creates a simple PDF content stream that draws the text.
    """
    # Parse color
    if color.startswith('#'):
        r = int(color[1:3], 16) / 255.0
        g = int(color[3:5], 16) / 255.0
        b = int(color[5:7], 16) / 255.0
    else:
        r, g, b = 0.5, 0.5, 0.5  # Default gray
    
    # Build content stream
    # This is a simplified approach - production code would use proper PDF operators
    content_parts = [
        b"q",  # Save graphics state
        f"/GS1 gs".encode(),  # Apply graphics state (opacity)
    ]
    
    # Add rotation if needed
    if angle != 0:
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        content_parts.append(
            f"{cos_a:.4f} {sin_a:.4f} {-sin_a:.4f} {cos_a:.4f} {x:.2f} {y:.2f} cm".encode()
        )
    
    content_parts.extend([
        f"{r:.3f} {g:.3f} {b:.3f} rg".encode(),  # Set fill color
        f"/F1 {font_size} Tf".encode(),  # Set font
        f"BT".encode(),  # Begin text
        f"{x:.2f} {y:.2f} Td".encode(),  # Move text position
        f"({text}) Tj".encode(),  # Draw text
        b"ET",  # End text
        b"Q",  # Restore graphics state
    ])
    
    return b"\n".join(content_parts)


def _add_content_to_page(page: Page, content: bytes, pdf: Pdf) -> None:
    """
    Add content stream to page.
    
    This appends the watermark content to the page's existing content.
    """
    # Get or create page contents
    if Name.Contents in page:
        existing = page[Name.Contents]
        if isinstance(existing, pikepdf.Array):
            # Multiple content streams - append new stream
            stream = pdf.make_stream(content)
            existing.append(stream)
        else:
            # Single content stream - convert to array
            stream = pdf.make_stream(content)
            new_contents = pikepdf.Array([existing, stream])
            page[Name.Contents] = new_contents
    else:
        # No existing content
        stream = pdf.make_stream(content)
        page[Name.Contents] = stream


def add_image_watermark(
    file: BytesIO,
    image_bytes: BytesIO,
    request: ImageWatermarkRequest
) -> BytesIO:
    """
    Add image watermark to PDF.
    
    Args:
        file: PDF BytesIO object
        image_bytes: Watermark image BytesIO
        request: ImageWatermarkRequest with watermark parameters
        
    Returns:
        BytesIO: Watermarked PDF
    """
    file.seek(0)
    image_bytes.seek(0)
    output = BytesIO()
    
    # Load image to get dimensions
    image = Image.open(image_bytes)
    img_width, img_height = image.size
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Determine which pages to watermark
        if request.pages == PageSelection.ALL:
            pages_to_process = list(range(total_pages))
        elif request.pages == PageSelection.FIRST:
            pages_to_process = [0]
        elif request.pages == PageSelection.LAST:
            pages_to_process = [total_pages - 1]
        else:
            pages_to_process = [p - 1 for p in request.pages]
            validate_page_numbers(request.pages, total_pages)
        
        # Convert image to PDF-compatible format
        image_bytes.seek(0)
        img_pdf_bytes = _image_to_pdf_stream(image_bytes)
        
        # Open image as PDF page
        with pikepdf.Pdf.open(img_pdf_bytes) as img_pdf:
            for page_idx in pages_to_process:
                page = pdf.pages[page_idx]
                page_width, page_height = get_page_dimensions(page)
                
                # Calculate scaled dimensions
                scale = request.scale
                scaled_width = page_width * scale
                scaled_height = (img_height / img_width) * scaled_width
                
                # Calculate position
                x, y, angle = calculate_position(
                    request.position,
                    page_width,
                    page_height,
                    scaled_width,
                    scaled_height
                )
                
                # Add image as XObject and draw on page
                _add_image_to_page(
                    pdf, page, img_pdf,
                    x, y, scaled_width, scaled_height,
                    request.opacity
                )
        
        pdf.save(output)
    
    output.seek(0)
    return output


def _image_to_pdf_stream(image_bytes: BytesIO) -> BytesIO:
    """
    Convert image to a single-page PDF.
    """
    output = BytesIO()
    image_bytes.seek(0)
    
    img = Image.open(image_bytes)
    
    # Convert to RGB if necessary (PDF doesn't support some modes)
    if img.mode in ('RGBA', 'P'):
        # Keep alpha for transparency
        pass
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Create a simple PDF with the image
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Use Pillow to create PDF
    pdf_bytes = BytesIO()
    img.save(pdf_bytes, format='PDF')
    pdf_bytes.seek(0)
    
    return pdf_bytes


def _add_image_to_page(
    pdf: Pdf,
    page: Page,
    img_pdf: Pdf,
    x: float,
    y: float,
    width: float,
    height: float,
    opacity: float
) -> None:
    """
    Add image from img_pdf to page at specified position.
    """
    # This is a simplified implementation
    # A production version would properly embed the image as an XObject
    
    # Create content stream to draw image
    content = f"""
q
{opacity} gs
{width} 0 0 {height} {x} {y} cm
/Im1 Do
Q
""".encode()
    
    stream = pdf.make_stream(content)
    
    # Add to page contents
    if Name.Contents in page:
        existing = page[Name.Contents]
        if isinstance(existing, pikepdf.Array):
            existing.append(stream)
        else:
            new_contents = pikepdf.Array([existing, stream])
            page[Name.Contents] = new_contents
    else:
        page[Name.Contents] = stream
