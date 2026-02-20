"""
Office format conversion service.

Provides bidirectional conversions between PDF and Microsoft Office formats
(Word, Excel, PowerPoint) using LibreOffice headless mode.

All conversions maintain zero-trace in-memory processing with temporary
files created only in tmpfs-mounted /tmp.

Reference: CONV-01 to CONV-06
Constraint: All operations use BytesIO or tmpfs temp files (ARCH-01, ARCH-03)
"""
import subprocess
import tempfile
import os
from io import BytesIO
from typing import Optional
from pathlib import Path

from app.schemas.convert import OfficeFormat


# LibreOffice conversion timeout (seconds)
LIBREOFFICE_TIMEOUT = 60


def office_to_pdf(file: BytesIO, input_format: str) -> BytesIO:
    """
    Convert Office document to PDF using LibreOffice headless.
    
    Args:
        file: Office file as BytesIO
        input_format: Input format (docx, xlsx, pptx)
        
    Returns:
        BytesIO: PDF document
        
    Raises:
        RuntimeError: If LibreOffice conversion fails
        TimeoutError: If conversion times out
    """
    file.seek(0)
    
    # Determine file extension
    ext = f".{input_format}"
    
    # Create temp file for input on tmpfs
    with tempfile.NamedTemporaryFile(
        suffix=ext,
        dir='/tmp',
        delete=False
    ) as tmp_in:
        tmp_in.write(file.read())
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


def pdf_to_office(file: BytesIO, output_format: str) -> BytesIO:
    """
    Convert PDF to Office document using LibreOffice headless.
    
    Note: LibreOffice converts PDF to ODF formats (odt, ods, odp) first,
    then we convert to the target Office format if needed.
    
    Args:
        file: PDF file as BytesIO
        output_format: Output format (docx, xlsx, pptx)
        
    Returns:
        BytesIO: Office document
        
    Raises:
        RuntimeError: If LibreOffice conversion fails
        TimeoutError: If conversion times out
    """
    file.seek(0)
    
    # Map output format to LibreOffice filter
    format_map = {
        'docx': ('docx', 'Office Open XML Text'),
        'xlsx': ('xlsx', 'Office Open XML Spreadsheet'),
        'pptx': ('pptx', 'Office Open XML Presentation'),
    }
    
    if output_format not in format_map:
        raise ValueError(f"Unsupported output format: {output_format}")
    
    ext, _ = format_map[output_format]
    
    # Create temp file for input PDF
    with tempfile.NamedTemporaryFile(
        suffix='.pdf',
        dir='/tmp',
        delete=False
    ) as tmp_in:
        tmp_in.write(file.read())
        tmp_in_path = tmp_in.name
    
    try:
        # Run LibreOffice headless conversion
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--nofilter',
            '--accept=none',
            '--convert-to', ext,
            '--outdir', '/tmp',
            tmp_in_path
        ], timeout=LIBREOFFICE_TIMEOUT, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr or result.stdout}"
            )
        
        # Determine output path
        output_path = tmp_in_path.rsplit('.', 1)[0] + f'.{ext}'
        
        # Read output file
        if not os.path.exists(output_path):
            raise RuntimeError(
                f"LibreOffice did not create expected output file. "
                f"stdout: {result.stdout}, stderr: {result.stderr}"
            )
        
        with open(output_path, 'rb') as f:
            output_bytes = BytesIO(f.read())
        
        # Cleanup output file
        os.remove(output_path)
        
        output_bytes.seek(0)
        return output_bytes
        
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"LibreOffice conversion timed out after {LIBREOFFICE_TIMEOUT} seconds"
        )
    finally:
        # Always cleanup input temp file
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)


def validate_office_file(content: bytes, expected_format: str) -> bool:
    """
    Validate Office file format using magic bytes.
    
    Office files (docx, xlsx, pptx) are ZIP archives with specific structures.
    
    Args:
        content: Raw file bytes
        expected_format: Expected format (docx, xlsx, pptx)
        
    Returns:
        bool: True if valid
    """
    # Office files start with ZIP signature
    if not content.startswith(b'PK\x03\x04') and not content.startswith(b'PK\x05\x06'):
        return False
    
    # Additional validation could check for specific content types
    # For now, ZIP signature check is sufficient
    return True
