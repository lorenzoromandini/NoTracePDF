"""
PDF Redaction Service.

Provides permanent text redaction using PyMuPDF for in-memory processing.
Redaction is PERMANENT - the text is removed from the PDF stream, not just covered.

Reference: PDF-24
Constraint: All operations use BytesIO (ARCH-01)
"""
from io import BytesIO
from typing import List, Optional, Union
import re

import fitz  # PyMuPDF

from app.utils.file_utils import (
    InvalidPageError,
    validate_page_numbers,
)


def redact_text(
    file: BytesIO,
    patterns: List[str],
    match_exact: bool = False,
    case_sensitive: bool = True,
    fill_color: str = "#000000",
    border_color: Optional[str] = None,
    pages: Union[str, List[int]] = "all"
) -> BytesIO:
    """
    Permanently redact text in a PDF.
    
    This uses PyMuPDF's apply_redactions() which removes the actual
    text content from the PDF stream, making it irrecoverable.
    Simply drawing black boxes is NOT secure redaction.
    
    Args:
        file: PDF BytesIO object
        patterns: List of text patterns to redact
        match_exact: If True, match exact text only; if False, match substrings
        case_sensitive: Whether to match case
        fill_color: Hex color for redaction fill (default black)
        border_color: Optional hex color for redaction border
        pages: 'all' or list of page numbers (1-indexed)
        
    Returns:
        BytesIO: Redacted PDF
        
    Raises:
        InvalidPageError: If page numbers are invalid
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        # Determine which pages to process
        if pages == "all":
            pages_to_process = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            pages_to_process = [p - 1 for p in pages]  # Convert to 0-indexed
        
        # Parse fill color
        fill_rgb = hex_to_rgb_normalized(fill_color)
        
        # Parse border color if provided
        border_rgb = None
        if border_color:
            border_rgb = hex_to_rgb_normalized(border_color)
        
        # Process each page
        for page_idx in pages_to_process:
            page = doc[page_idx]
            
            for pattern in patterns:
                # Search for text occurrences
                # flags: 0 = case-sensitive, fitz.TEXT_PRESERVE_WHITESPACE
                flags = 0
                if case_sensitive:
                    flags = 0
                else:
                    flags = fitz.TEXT_PRESERVE_WHITESPACE
                
                # Search for the pattern
                text_instances = page.search_for(
                    pattern,
                    quads=False,  # Return rectangles
                    flags=flags if case_sensitive else fitz.TEXT_PRESERVE_WHITESPACE
                )
                
                # If case-insensitive, we need to do manual matching
                if not case_sensitive:
                    # Get all text with positions
                    text_dict = page.get_text("dict")
                    text_instances = []
                    
                    pattern_lower = pattern.lower()
                    
                    for block in text_dict.get("blocks", []):
                        if block.get("type") != 0:  # Skip images
                            continue
                        
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text = span.get("text", "")
                                text_lower = text.lower()
                                
                                if match_exact:
                                    if text_lower == pattern_lower:
                                        bbox = fitz.Rect(span["bbox"])
                                        text_instances.append(bbox)
                                else:
                                    # Find all occurrences
                                    start = 0
                                    while True:
                                        idx = text_lower.find(pattern_lower, start)
                                        if idx == -1:
                                            break
                                        
                                        # Calculate approximate bbox for substring
                                        # This is approximate - for exact positioning,
                                        # we'd need character-level positioning
                                        bbox = fitz.Rect(span["bbox"])
                                        text_instances.append(bbox)
                                        start = idx + 1
                    
                else:
                    # Case-sensitive search with PyMuPDF
                    if match_exact:
                        # Filter to exact matches
                        filtered_instances = []
                        text_dict = page.get_text("dict")
                        
                        for inst in text_instances:
                            # Check if this is an exact match
                            # Get text in this region
                            words = page.get_text("words")
                            for word_info in words:
                                word_bbox = fitz.Rect(word_info[:4])
                                word_text = word_info[4]
                                
                                if word_bbox.intersects(inst) and word_text == pattern:
                                    filtered_instances.append(word_bbox)
                                    break
                        
                        text_instances = filtered_instances
                
                # Add redaction annotations
                for inst in text_instances:
                    # Add redaction annotation
                    page.add_redact_annot(
                        inst,
                        fill=fill_rgb,
                        text=None  # No replacement text
                    )
            
            # Apply all redactions on this page
            # This is CRITICAL - it removes the actual content
            page.apply_redactions()
        
        # Save with garbage collection to ensure redacted content is removed
        output = BytesIO()
        doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        
        return output
        
    finally:
        doc.close()


def redact_regex(
    file: BytesIO,
    regex_patterns: List[str],
    fill_color: str = "#000000",
    pages: Union[str, List[int]] = "all"
) -> BytesIO:
    """
    Redact text matching regex patterns.
    
    Useful for redacting patterns like SSNs, phone numbers, emails.
    
    Args:
        file: PDF BytesIO object
        regex_patterns: List of regex patterns to redact
        fill_color: Hex color for redaction fill
        pages: 'all' or list of page numbers (1-indexed)
        
    Returns:
        BytesIO: Redacted PDF
    """
    file.seek(0)
    pdf_bytes = file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    
    try:
        # Determine which pages to process
        if pages == "all":
            pages_to_process = list(range(total_pages))
        else:
            validate_page_numbers(pages, total_pages)
            pages_to_process = [p - 1 for p in pages]
        
        fill_rgb = hex_to_rgb_normalized(fill_color)
        
        for page_idx in pages_to_process:
            page = doc[page_idx]
            
            # Get all text with positions
            text_dict = page.get_text("dict")
            
            for pattern in regex_patterns:
                try:
                    compiled = re.compile(pattern)
                except re.error:
                    continue  # Skip invalid patterns
                
                for block in text_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue
                    
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            bbox = fitz.Rect(span["bbox"])
                            
                            # Find all matches
                            for match in compiled.finditer(text):
                                # Redact the entire span containing the match
                                # For precise character-level redaction,
                                # additional positioning calculation would be needed
                                page.add_redact_annot(
                                    bbox,
                                    fill=fill_rgb
                                )
                                break  # One redaction per span
            
            page.apply_redactions()
        
        output = BytesIO()
        doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        
        return output
        
    finally:
        doc.close()


def hex_to_rgb_normalized(hex_color: str) -> tuple:
    """
    Convert hex color to normalized RGB tuple (0.0-1.0).
    
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


# Common regex patterns for convenience
REDACTION_PATTERNS = {
    "ssn": r"\d{3}-\d{2}-\d{4}",
    "phone_us": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "credit_card": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
    "date_us": r"\d{1,2}/\d{1,2}/\d{2,4}",
    "ip_address": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
}
