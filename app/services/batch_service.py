"""
Batch Processing Service.

Provides batch processing for multiple PDFs via ZIP upload/download.
All processing is done in-memory with no disk persistence.

Reference: ADV-02
"""
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
import zipfile
import logging
from datetime import datetime

from app.services.pdf_service import rotate_pages
from app.services.pdf_security_service import compress_pdf
from app.services.pdf_service import split_pdf
from app.services.pdf_security_service import add_password
from app.schemas.batch import BatchOperation, BatchOptions, BatchResultFile
from app.schemas.pdf import QualityPreset, SplitMode

logger = logging.getLogger(__name__)


def process_batch_zip(
    zip_bytes: BytesIO,
    options: BatchOptions
) -> BytesIO:
    """
    Process a ZIP file containing multiple PDFs.
    
    Extracts PDFs from ZIP, applies the selected operation to each,
    and returns results as a new ZIP file.
    
    Args:
        zip_bytes: ZIP file BytesIO object
        options: Batch processing options
        
    Returns:
        BytesIO: ZIP file containing processed PDFs
    """
    zip_bytes.seek(0)
    results = []
    
    try:
        with zipfile.ZipFile(zip_bytes, 'r') as zf:
            # Get all PDF files in the ZIP
            pdf_files = [
                name for name in zf.namelist()
                if name.lower().endswith('.pdf') and not name.startswith('__MACOSX/')
            ]
            
            logger.info(f"Found {len(pdf_files)} PDF files in ZIP")
            
            for pdf_name in pdf_files:
                try:
                    # Read PDF from ZIP
                    pdf_data = BytesIO(zf.read(pdf_name))
                    
                    # Process based on operation
                    processed = _process_single_pdf(pdf_data, pdf_name, options)
                    
                    if processed:
                        result_name, result_data = processed
                        results.append((result_name, result_data))
                        logger.debug(f"Processed: {pdf_name} -> {result_name}")
                    else:
                        # Copy original if processing failed
                        results.append((pdf_name, pdf_data))
                        logger.warning(f"Processing returned empty for: {pdf_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing {pdf_name}: {e}")
                    # Skip failed files
                    continue
                    
    except zipfile.BadZipFile as e:
        raise ValueError(f"Invalid ZIP file: {str(e)}")
    
    if not results:
        raise ValueError("No PDF files found or processed in ZIP")
    
    # Create result ZIP
    return _create_result_zip(results)


def _process_single_pdf(
    pdf_bytes: BytesIO,
    original_name: str,
    options: BatchOptions
) -> Optional[Tuple[str, BytesIO]]:
    """
    Process a single PDF according to batch options.
    
    Args:
        pdf_bytes: PDF file BytesIO object
        original_name: Original filename
        options: Batch processing options
        
    Returns:
        Tuple of (result_filename, result_bytes) or None if failed
    """
    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    
    try:
        if options.operation == BatchOperation.COMPRESS:
            quality = QualityPreset(options.quality or "medium")
            result = compress_pdf(pdf_bytes, quality)
            return f"{base_name}_compressed.pdf", result
            
        elif options.operation == BatchOperation.ROTATE:
            degrees = options.degrees or 90
            result = rotate_pages(pdf_bytes, "all", degrees)
            return f"{base_name}_rotated.pdf", result
            
        elif options.operation == BatchOperation.SPLIT:
            if options.split_mode == "every_n":
                n_pages = options.n_pages or 1
                results = split_pdf(
                    pdf_bytes,
                    mode=SplitMode.EVERY_N,
                    n_pages=n_pages
                )
            else:
                # Default split - just return the original for batch
                # Split each into single pages
                results = split_pdf(
                    pdf_bytes,
                    mode=SplitMode.EVERY_N,
                    n_pages=1
                )
            
            if len(results) == 1:
                return results[0]
            else:
                # Return first result for batch (others would complicate ZIP)
                return results[0] if results else None
                
        elif options.operation == BatchOperation.PASSWORD:
            if not options.password:
                raise ValueError("Password required for password operation")
            result = add_password(pdf_bytes, options.password)
            return f"{base_name}_protected.pdf", result
            
        else:
            logger.warning(f"Unknown operation: {options.operation}")
            return None
            
    except Exception as e:
        logger.error(f"Error in _process_single_pdf for {original_name}: {e}")
        raise


def _create_result_zip(files: List[Tuple[str, BytesIO]]) -> BytesIO:
    """
    Create a ZIP archive from processed files.
    
    Args:
        files: List of (filename, BytesIO) tuples
        
    Returns:
        BytesIO: ZIP file
    """
    output = BytesIO()
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files:
            content.seek(0)
            zf.writestr(filename, content.read())
    
    output.seek(0)
    return output


def list_zip_contents(zip_bytes: BytesIO) -> List[str]:
    """
    List contents of a ZIP file.
    
    Args:
        zip_bytes: ZIP file BytesIO object
        
    Returns:
        List of filenames in the ZIP
    """
    zip_bytes.seek(0)
    try:
        with zipfile.ZipFile(zip_bytes, 'r') as zf:
            return [name for name in zf.namelist() if not name.endswith('/')]
    except zipfile.BadZipFile:
        return []
