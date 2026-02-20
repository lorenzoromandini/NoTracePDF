"""
Text and RTF conversion service.

Provides conversions from plain text and RTF documents to PDF
using PyMuPDF (fitz) for text and LibreOffice for RTF.

All conversions maintain zero-trace in-memory processing.

Reference: CONV-10, CONV-11
Constraint: All operations use BytesIO or tmpfs temp files (ARCH-01, ARCH-03)
"""
import subprocess
import tempfile
import os
from io import BytesIO
from typing import Optional, Tuple

import fitz  # PyMuPDF


# Default page settings
DEFAULT_PAGE_SIZE = (595, 842)  # A4 in points
DEFAULT_MARGIN = 72  # 1 inch
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = "helv"  # Helvetica

# LibreOffice conversion timeout (seconds)
LIBREOFFICE_TIMEOUT = 60


def text_to_pdf(
    text_content: str,
    font_size: int = DEFAULT_FONT_SIZE,
    font_family: str = DEFAULT_FONT_FAMILY,
    page_size: Tuple[int, int] = DEFAULT_PAGE_SIZE,
    margin: int = DEFAULT_MARGIN
) -> BytesIO:
    """
    Convert plain text to PDF.
    
    Handles text wrapping and multi-page documents automatically.
    
    Args:
        text_content: Plain text string to convert
        font_size: Font size in points (default: 12)
        font_family: PyMuPDF font name (helv, cour, tim)
        page_size: (width, height) in points (default: A4)
        margin: Margin in points (default: 72 = 1 inch)
        
    Returns:
        BytesIO: PDF document
    """
    output = BytesIO()
    doc = fitz.open()
    
    # Calculate text area dimensions
    text_width = page_size[0] - 2 * margin
    text_height = page_size[1] - 2 * margin
    
    # Line height based on font size
    line_height = font_size * 1.5
    
    # Split content into lines
    lines = text_content.split('\n')
    
    # Track position and page
    y_position = margin
    current_page = None
    
    for line in lines:
        # Check if we need a new page
        if current_page is None or y_position > (page_size[1] - margin - line_height):
            current_page = doc.new_page(
                width=page_size[0],
                height=page_size[1]
            )
            y_position = margin
        
        # Handle empty lines
        if not line:
            y_position += line_height
            continue
        
        # Calculate available width for this line
        # Use text insertion with wrapping
        text_rect = fitz.Rect(
            margin,
            y_position,
            page_size[0] - margin,
            y_position + line_height * 5  # Allow for wrapped text
        )
        
        # Insert text with wrapping
        # For long lines, we need to handle wrapping manually
        remaining_text = line
        while remaining_text:
            # Check if we need a new page
            if y_position > (page_size[1] - margin - line_height):
                current_page = doc.new_page(
                    width=page_size[0],
                    height=page_size[1]
                )
                y_position = margin
            
            # Get font metrics for width calculation
            font_metrics = current_page.get_fontmetrics(font_family, font_size)
            
            # Calculate how many characters fit
            char_width = font_size * 0.5  # Approximate
            max_chars = int(text_width / char_width)
            
            if len(remaining_text) <= max_chars:
                # Whole line fits
                current_page.insert_text(
                    (margin, y_position + font_size),  # Baseline position
                    remaining_text,
                    fontsize=font_size,
                    fontname=font_family,
                    color=(0, 0, 0)  # Black
                )
                y_position += line_height
                remaining_text = ""
            else:
                # Need to wrap - find a good break point
                break_point = max_chars
                # Try to break at a space
                space_pos = remaining_text[:max_chars].rfind(' ')
                if space_pos > max_chars // 2:
                    break_point = space_pos + 1
                
                current_line = remaining_text[:break_point].rstrip()
                remaining_text = remaining_text[break_point:].lstrip()
                
                current_page.insert_text(
                    (margin, y_position + font_size),
                    current_line,
                    fontsize=font_size,
                    fontname=font_family,
                    color=(0, 0, 0)
                )
                y_position += line_height
    
    # Save PDF
    doc.save(output)
    doc.close()
    
    output.seek(0)
    return output


def rtf_to_pdf(rtf_content: BytesIO) -> BytesIO:
    """
    Convert RTF document to PDF using LibreOffice headless.
    
    RTF files are converted via LibreOffice Writer.
    Temp files are created in /tmp (tmpfs) and cleaned up.
    
    Args:
        rtf_content: RTF file as BytesIO
        
    Returns:
        BytesIO: PDF document
        
    Raises:
        RuntimeError: If LibreOffice conversion fails
        TimeoutError: If conversion times out
    """
    rtf_content.seek(0)
    
    # Create temp file for RTF input
    with tempfile.NamedTemporaryFile(
        suffix='.rtf',
        dir='/tmp',
        delete=False
    ) as tmp_in:
        tmp_in.write(rtf_content.read())
        tmp_in_path = tmp_in.name
    
    try:
        # Run LibreOffice headless conversion
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--nofilter',
            '--accept=none',
            '--convert-to', 'pdf',
            '--outdir', '/tmp',
            tmp_in_path
        ], timeout=LIBREOFFICE_TIMEOUT, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr or result.stdout}"
            )
        
        # Determine output path
        pdf_path = tmp_in_path.rsplit('.', 1)[0] + '.pdf'
        
        # Read output PDF
        if not os.path.exists(pdf_path):
            raise RuntimeError(
                f"LibreOffice did not create expected output file. "
                f"stdout: {result.stdout}, stderr: {result.stderr}"
            )
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = BytesIO(f.read())
        
        # Cleanup output file
        os.remove(pdf_path)
        
        pdf_bytes.seek(0)
        return pdf_bytes
        
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"LibreOffice conversion timed out after {LIBREOFFICE_TIMEOUT} seconds"
        )
    finally:
        # Always cleanup input temp file
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)


def validate_rtf_content(content: bytes) -> bool:
    """
    Validate RTF file content.
    
    RTF files start with {\rtf1
    
    Args:
        content: Raw file bytes
        
    Returns:
        bool: True if valid RTF header
    """
    return content.startswith(b'{\\rtf')
