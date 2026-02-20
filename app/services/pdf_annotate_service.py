"""
PDF Annotation and Metadata Service.

Provides page numbers, annotation flattening, and metadata removal
using PyMuPDF and pikepdf for in-memory processing.

Reference: PDF-20, PDF-21, PDF-22
Constraint: All operations use BytesIO (ARCH-01)
"""
from io import BytesIO
from typing import List, Optional
from enum import Enum

import fitz  # PyMuPDF
import pikepdf


class PageNumberPosition(str, Enum):
    """Position options for page numbers."""
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    TOP_CENTER = "top-center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"


class MetadataField(str, Enum):
    """Metadata field names."""
    TITLE = "title"
    AUTHOR = "author"
    SUBJECT = "subject"
    KEYWORDS = "keywords"
    CREATOR = "creator"
    PRODUCER = "producer"
    CREATION_DATE = "creationDate"
    MODIFICATION_DATE = "modDate"


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color string (e.g., "#000000")
        
    Returns:
        Tuple of (r, g, b) values 0.0-1.0
    """
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    return (r, g, b)


def add_page_numbers(
    file: BytesIO,
    format: str = "Page {page} of {total}",
    position: str = "bottom-center",
    font_size: int = 12,
    color: str = "#000000",
    start_at: int = 1,
    pages: Optional[List[int]] = None
) -> BytesIO:
    """
    Add page numbers to PDF.
    
    Args:
        file: PDF BytesIO object
        format: Format string with {page} and {total} placeholders
        position: Position for page numbers (bottom-center, top-left, etc.)
        font_size: Font size in points
        color: Hex color code (e.g., "#000000")
        start_at: Starting page number (default 1)
        pages: Optional list of page numbers to number (1-indexed), None for all
        
    Returns:
        BytesIO: PDF with page numbers added
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        # Determine which pages to number
        if pages is None:
            page_indices = list(range(total_pages))
        else:
            page_indices = [p - 1 for p in pages]  # Convert to 0-indexed
        
        # Parse color
        rgb = hex_to_rgb(color)
        
        # Calculate positions for each page
        for i in page_indices:
            if i < 0 or i >= total_pages:
                continue
            
            page = doc[i]
            rect = page.rect
            page_width = rect.width
            page_height = rect.height
            
            # Generate page number text
            text = format.format(page=i + start_at, total=total_pages)
            
            # Calculate position based on option
            margin = 36  # 0.5 inch margin
            
            if position == "bottom-center":
                x = page_width / 2
                y = page_height - margin
                align = 1  # center
            elif position == "bottom-left":
                x = margin
                y = page_height - margin
                align = 0  # left
            elif position == "bottom-right":
                x = page_width - margin
                y = page_height - margin
                align = 2  # right
            elif position == "top-center":
                x = page_width / 2
                y = margin
                align = 1  # center
            elif position == "top-left":
                x = margin
                y = margin
                align = 0  # left
            elif position == "top-right":
                x = page_width - margin
                y = margin
                align = 2  # right
            else:
                # Default to bottom-center
                x = page_width / 2
                y = page_height - margin
                align = 1
            
            # Insert text
            # Using insert_text with proper font
            point = fitz.Point(x, y)
            
            # For center/right alignment, we need to calculate text width
            # and adjust position
            if align == 1:  # center
                # Get text width using default font
                text_width = fitz.get_text_length(text, fontname="helv", fontsize=font_size)
                point.x = x - text_width / 2
            elif align == 2:  # right
                text_width = fitz.get_text_length(text, fontname="helv", fontsize=font_size)
                point.x = x - text_width
            
            page.insert_text(
                point,
                text,
                fontname="helv",
                fontsize=font_size,
                color=rgb
            )
        
        # Save to bytes
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output
    finally:
        doc.close()


def flatten_annotations(file: BytesIO) -> BytesIO:
    """
    Flatten all annotations into document content.
    
    This converts annotations (comments, highlights, form fields)
    into permanent content on the page.
    
    Args:
        file: PDF BytesIO object
        
    Returns:
        BytesIO: Flattened PDF
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    try:
        for page in doc:
            # Get all annotations
            annots = list(page.annots()) if page.annots() else []
            
            for annot in annots:
                # PyMuPDF doesn't have a direct "flatten" method,
                # but we can apply redactions which effectively flatten
                # For form fields and other annotations, we need to
                # render them to the page content
                
                # For text annotations and highlights, they're already visible
                # We just need to remove the annotation object
                
                # For form fields (widgets), we need to render their appearance
                if annot.type[0] == fitz.PDF_ANNOT_WIDGET:
                    # Widget (form field) - render its appearance
                    widget = annot
                    rect = widget.rect
                    
                    # Get the widget's appearance stream if available
                    # This is complex, so we'll use a simpler approach:
                    # Redraw the widget's appearance onto the page
                    
                    # For text fields, get the value
                    if hasattr(widget, 'field_value') and widget.field_value:
                        # Insert the field value as text
                        page.insert_text(
                            fitz.Point(rect.x0 + 2, rect.y1 - 2),
                            str(widget.field_value),
                            fontsize=10,
                            color=(0, 0, 0)
                        )
            
            # Clean up page contents and remove annotations
            page.clean_contents()
            
            # Remove all annotations
            for annot in annots:
                page.delete_annot(annot)
        
        # Save to bytes
        output = BytesIO()
        doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        
        return output
    finally:
        doc.close()


def remove_metadata(
    file: BytesIO,
    fields: Optional[List[str]] = None
) -> BytesIO:
    """
    Remove metadata from PDF.
    
    Args:
        file: PDF BytesIO object
        fields: Optional list of metadata fields to remove.
                If None, removes all metadata.
                Valid values: title, author, subject, keywords, 
                              creator, producer, creationDate, modDate
                
    Returns:
        BytesIO: PDF with metadata removed
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        # Map field names to PDF dictionary keys
        field_map = {
            "title": "/Title",
            "author": "/Author",
            "subject": "/Subject",
            "keywords": "/Keywords",
            "creator": "/Creator",
            "producer": "/Producer",
            "creationDate": "/CreationDate",
            "creation_date": "/CreationDate",
            "modificationDate": "/ModDate",
            "modification_date": "/ModDate",
        }
        
        if fields is None:
            # Remove all metadata
            if pdf.docinfo:
                pdf.docinfo.clear()
        else:
            # Remove specific fields
            for field in fields:
                field_lower = field.lower()
                if field_lower in field_map:
                    pdf_key = field_map[field_lower]
                    if pdf.docinfo and pdf_key in pdf.docinfo:
                        del pdf.docinfo[pdf_key]
        
        pdf.save(output)
    
    output.seek(0)
    return output


def get_metadata(file: BytesIO) -> dict:
    """
    Get metadata from PDF.
    
    Args:
        file: PDF BytesIO object
        
    Returns:
        Dict with metadata fields
    """
    file.seek(0)
    output = {}
    
    with pikepdf.Pdf.open(file) as pdf:
        if pdf.docinfo:
            for key, value in pdf.docinfo.items():
                # Convert pikepdf objects to strings
                key_str = str(key)
                try:
                    value_str = str(value)
                except:
                    value_str = repr(value)
                output[key_str] = value_str
    
    return output
