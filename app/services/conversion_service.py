"""
Office format conversion service.

Provides bidirectional conversions between PDF and Microsoft Office formats
using pdf2docx for PDF to Word and LibreOffice for other conversions.

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

# PDF2DOCX for PDF to Word conversion
try:
    from pdf2docx import Converter
    PDF2DOCX_AVAILABLE = True
except ImportError:
    PDF2DOCX_AVAILABLE = False

# LibreOffice conversion timeout (seconds)
LIBREOFFICE_TIMEOUT = 120


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
    ext_map = {
        'docx': '.docx',
        'xlsx': '.xlsx',
        'pptx': '.pptx',
    }
    
    if input_format not in ext_map:
        raise ValueError(f"Unsupported input format: {input_format}")
    
    ext = ext_map[input_format]
    
    # Create temp file for input
    with tempfile.NamedTemporaryFile(
        suffix=ext,
        dir='/tmp',
        delete=False
    ) as tmp_in:
        tmp_in.write(file.read())
        tmp_in_path = tmp_in.name
    
    try:
        # Run LibreOffice headless conversion
        env = os.environ.copy()
        env['SAL_DISABLE_CONNECT_WITH_OFFICE'] = '1'
        env['SAL_NO_FORK'] = '1'
        
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--accept=none',
            '--convert-to', 'pdf',
            '--outdir', '/tmp',
            f'-env:UserInstallation=file:///tmp/lo-office-{os.getpid()}',
            tmp_in_path
        ], timeout=LIBREOFFICE_TIMEOUT, capture_output=True, text=True, cwd='/tmp', env=env)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr or result.stdout}"
            )
        
        # Get output path
        tmp_out_path = tmp_in_path.replace(ext, '.pdf')
        
        if not os.path.exists(tmp_out_path):
            raise RuntimeError(
                f"LibreOffice did not create expected output file. stdout: {result.stdout}, stderr: {result.stderr}"
            )
        
        # Read output file
        output = BytesIO()
        with open(tmp_out_path, 'rb') as f:
            output.write(f.read())
        output.seek(0)
        
        return output
        
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_in_path):
            os.unlink(tmp_in_path)
        tmp_out_path = tmp_in_path.replace(ext, '.pdf')
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


def pdf_to_office(file: BytesIO, output_format: str) -> BytesIO:
    """
    Convert PDF to Office document.
    
    Uses pdf2docx for Word documents (docx) and LibreOffice for other formats.
    
    Args:
        file: PDF file as BytesIO
        output_format: Output format (docx, xlsx, pptx)
        
    Returns:
        BytesIO: Office document
        
    Raises:
        RuntimeError: If conversion fails
        TimeoutError: If conversion times out
    """
    file.seek(0)
    
    if output_format == 'docx':
        return _pdf_to_docx(file)
    else:
        return _pdf_to_office_libreoffice(file, output_format)


def _pdf_to_docx(file: BytesIO) -> BytesIO:
    """
    Convert PDF to Word using pdf2docx library.
    
    Args:
        file: PDF file as BytesIO
        
    Returns:
        BytesIO: Word document
    """
    if not PDF2DOCX_AVAILABLE:
        raise RuntimeError("pdf2docx library not available")
    
    # Create temp files
    with tempfile.NamedTemporaryFile(suffix='.pdf', dir='/tmp', delete=False) as tmp_in:
        tmp_in.write(file.read())
        tmp_in_path = tmp_in.name
    
    tmp_out_path = tmp_in_path.replace('.pdf', '.docx')
    
    try:
        # Convert using pdf2docx
        cv = Converter(tmp_in_path)
        cv.convert(tmp_out_path, start=0, end=None)
        cv.close()
        
        # Read output file
        output = BytesIO()
        with open(tmp_out_path, 'rb') as f:
            output.write(f.read())
        output.seek(0)
        
        return output
        
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_in_path):
            os.unlink(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


def _pdf_to_office_libreoffice(file: BytesIO, output_format: str) -> BytesIO:
    """
    Convert PDF to Office using LibreOffice (fallback for xlsx, pptx).
    
    Args:
        file: PDF file as BytesIO
        output_format: Output format (xlsx, pptx)
        
    Returns:
        BytesIO: Office document
    """
    file.seek(0)
    
    format_map = {
        'xlsx': ('xlsx', 'Calc MS Excel 2007 XML'),
        'pptx': ('pptx', 'Impress MS PowerPoint 2007 XML'),
    }
    
    if output_format not in format_map:
        raise ValueError(f"Unsupported output format: {output_format}")
    
    ext, filter_name = format_map[output_format]
    
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
        env = os.environ.copy()
        env['SAL_DISABLE_CONNECT_WITH_OFFICE'] = '1'
        env['SAL_NO_FORK'] = '1'
        
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--accept=none',
            '--convert-to', f'{ext}:{filter_name}',
            '--outdir', '/tmp',
            f'-env:UserInstallation=file:///tmp/lo-pdf-{os.getpid()}',
            tmp_in_path
        ], timeout=LIBREOFFICE_TIMEOUT, capture_output=True, text=True, cwd='/tmp', env=env)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr or result.stdout}"
            )
        
        # Get output path
        tmp_out_path = tmp_in_path.replace('.pdf', f'.{ext}')
        
        if not os.path.exists(tmp_out_path):
            raise RuntimeError(
                f"LibreOffice did not create expected output file. stdout: {result.stdout}, stderr: {result.stderr}"
            )
        
        # Read output file
        output = BytesIO()
        with open(tmp_out_path, 'rb') as f:
            output.write(f.read())
        output.seek(0)
        
        return output
        
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_in_path):
            os.unlink(tmp_in_path)
        tmp_out_path = tmp_in_path.replace('.pdf', f'.{ext}')
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)
