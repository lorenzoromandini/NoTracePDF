"""
Image Conversion Service.

Provides PDF-to-image and image-to-PDF conversion
using PyMuPDF for robust, simple implementation.

Reference: IMG-01 to IMG-06
"""
from io import BytesIO
from typing import List, Tuple, Union, Optional
import math

import fitz  # PyMuPDF
from PIL import Image

from app.schemas.pdf import PageSelection, PageSize
from app.schemas.image import PdfToImageRequest, ImageToPdfRequest
from app.utils.file_utils import validate_page_numbers


# Page size dimensions in points (1 point = 1/72 inch)
PAGE_DIMENSIONS = {
    PageSize.A4: (595.28, 841.89),
    PageSize.LETTER: (612, 792),
}


def pdf_to_images(
    file: BytesIO,
    request: PdfToImageRequest
) -> List[Tuple[str, BytesIO]]:
    """
    Convert PDF pages to images using PyMuPDF.
    
    Args:
        file: PDF BytesIO object
        request: PdfToImageRequest with conversion parameters
        
    Returns:
        List of (filename, BytesIO) tuples
    """
    file.seek(0)
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    
    try:
        total_pages = len(pdf)
        
        # Determine which pages to convert
        if request.pages == PageSelection.ALL:
            page_indices = list(range(total_pages))
        elif request.pages == PageSelection.FIRST:
            page_indices = [0]
        elif request.pages == PageSelection.LAST:
            page_indices = [total_pages - 1]
        else:
            validate_page_numbers(request.pages, total_pages)
            page_indices = [p - 1 for p in request.pages]
        
        results = []
        
        for idx in page_indices:
            page = pdf[idx]
            
            # Render page to pixmap
            mat = fitz.Matrix(request.dpi/72, request.dpi/72)  # Scale by DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save to BytesIO
            output = BytesIO()
            if request.format.value == 'png':
                img.save(output, format='PNG')
                ext = 'png'
            elif request.format.value == 'jpg' or request.format.value == 'jpeg':
                img.save(output, format='JPEG', quality=request.quality)
                ext = 'jpg'
            elif request.format.value == 'webp':
                img.save(output, format='WEBP', quality=request.quality)
                ext = 'webp'
            else:
                img.save(output, format='PNG')
                ext = 'png'
            
            output.seek(0)
            filename = f"page_{idx + 1:03d}.{ext}"
            results.append((filename, output))
        
        return results
        
    finally:
        pdf.close()


def images_to_pdf(
    files: List[Tuple[BytesIO, str]],
    request: ImageToPdfRequest
) -> BytesIO:
    """
    Convert multiple images to a single PDF using PyMuPDF.
    
    Args:
        files: List of (BytesIO, format) tuples for each image
        request: ImageToPdfRequest with conversion parameters
        
    Returns:
        BytesIO: Combined PDF
    """
    output = BytesIO()
    
    # Create new PDF
    pdf = fitz.open()
    
    try:
        for img_bytes, img_format in files:
            img_bytes.seek(0)
            img = Image.open(img_bytes)
            
            # Convert to RGB/RGBA for PDF compatibility
            if img.mode == 'P':
                img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Get image dimensions
            img_width, img_height = img.size
            img_aspect = img_width / img_height
            
            # Determine page size
            if request.page_size == PageSize.FIT or request.page_size == PageSize.ORIGINAL:
                # Size page to fit image
                if img_width > img_height:
                    page_width = 595.28  # A4 width
                    page_height = page_width / img_aspect
                else:
                    page_height = 841.89  # A4 height
                    page_width = page_height * img_aspect
            else:
                page_width, page_height = PAGE_DIMENSIONS[request.page_size]
            
            # Create new page
            page = pdf.new_page(width=page_width, height=page_height)
            
            # Calculate position and size
            if request.fit_to_page:
                # Calculate scale to fit with margins
                margin = 36  # 0.5 inch margin
                available_width = page_width - 2 * margin
                available_height = page_height - 2 * margin
                
                scale_w = available_width / img_width if img_width > 0 else 1
                scale_h = available_height / img_height if img_height > 0 else 1
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale
                
                final_width = img_width * scale
                final_height = img_height * scale
                
                # Center on page
                x = (page_width - final_width) / 2
                y = (page_height - final_height) / 2
            else:
                # Center at original size
                x = (page_width - img_width) / 2
                y = (page_height - img_height) / 2
                final_width = img_width
                final_height = img_height
            
            # Insert image
            rect = fitz.Rect(x, y, x + final_width, y + final_height)
            
            # Convert PIL image to bytes
            img_byte_arr = BytesIO()
            if img.mode == 'RGBA':
                # For transparency, use PNG
                img.save(img_byte_arr, format='PNG')
            else:
                # For JPEG, use quality 95
                img.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)
            
            # Insert into PDF
            page.insert_image(rect, stream=img_byte_arr.read())
        
        # Save PDF with compression
        pdf.save(output, garbage=4, deflate=True)
        output.seek(0)
        return output
        
    finally:
        pdf.close()


def image_to_pdf_simple(
    files: List[Tuple[BytesIO, str]],
    page_size: PageSize = PageSize.A4,
    fit_to_page: bool = True
) -> BytesIO:
    """
    Simplified image to PDF conversion using PyMuPDF.
    
    This is a wrapper around images_to_pdf for API compatibility.
    
    Args:
        files: List of (BytesIO, format) tuples
        page_size: Page size for output
        fit_to_page: Whether to scale images to fit page
        
    Returns:
        BytesIO: Combined PDF
    """
    from app.schemas.image import ImageToPdfRequest
    
    request = ImageToPdfRequest(
        page_size=page_size,
        fit_to_page=fit_to_page
    )
    return images_to_pdf(files, request)
