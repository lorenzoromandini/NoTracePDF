"""
OCR Service.

Provides OCR (Optical Character Recognition) for scanned PDFs
using Tesseract and pdf2image for high-performance in-memory processing.

Reference: ADV-01
"""
from io import BytesIO
from typing import List, Optional, Dict, Any
import logging

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

from app.schemas.ocr import OCRResponse, PageOCRResult

logger = logging.getLogger(__name__)


def extract_text_ocr(
    pdf_bytes: BytesIO,
    language: str = "eng"
) -> OCRResponse:
    """
    Extract text from scanned PDF using OCR.
    
    Converts PDF pages to images and runs Tesseract OCR on each page.
    All processing is done in-memory.
    
    Args:
        pdf_bytes: PDF BytesIO object
        language: OCR language code (default: 'eng' for English)
        
    Returns:
        OCRResponse: Structured OCR result with text per page
    """
    pdf_bytes.seek(0)
    pdf_data = pdf_bytes.read()
    
    # Convert PDF pages to images
    # Using lower DPI for faster processing while maintaining accuracy
    try:
        images = convert_from_bytes(
            pdf_data,
            dpi=200,  # Good balance between speed and accuracy
            fmt='png'
        )
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise RuntimeError(f"Failed to convert PDF to images: {str(e)}")
    
    total_pages = len(images)
    page_results = []
    total_chars = 0
    
    for page_idx, image in enumerate(images):
        try:
            # Run OCR on the page image
            text = pytesseract.image_to_string(image, lang=language)
            
            # Clean up the text
            cleaned_text = _clean_ocr_text(text)
            char_count = len(cleaned_text)
            total_chars += char_count
            
            page_results.append(PageOCRResult(
                page_number=page_idx + 1,
                text=cleaned_text,
                character_count=char_count
            ))
            
            logger.debug(f"OCR page {page_idx + 1}: {char_count} characters")
            
        except Exception as e:
            # Continue processing other pages if one fails
            logger.warning(f"OCR failed for page {page_idx + 1}: {e}")
            page_results.append(PageOCRResult(
                page_number=page_idx + 1,
                text="(OCR failed for this page)",
                character_count=0
            ))
    
    return OCRResponse(
        total_pages=total_pages,
        total_characters=total_chars,
        pages=page_results
    )


def _clean_ocr_text(text: str) -> str:
    """
    Clean OCR-extracted text.
    
    - Remove excessive whitespace
    - Normalize line endings
    - Handle common OCR artifacts
    
    Args:
        text: Raw OCR text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive whitespace (more than 2 consecutive spaces/newlines)
    import re
    text = re.sub(r' {3,}', '  ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def get_available_languages() -> List[str]:
    """
    Get list of available OCR languages.
    
    Returns:
        List of language codes installed in Tesseract
    """
    try:
        langs = pytesseract.get_languages()
        return langs
    except Exception:
        # Return default if Tesseract not available
        return ['eng']
