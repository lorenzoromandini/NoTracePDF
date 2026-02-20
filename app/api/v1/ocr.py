"""
OCR API Endpoints.

Provides OCR text extraction from scanned PDFs.
All processing is done in-memory with no disk persistence.

Reference: ADV-01
"""
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.services.ocr_service import extract_text_ocr, get_available_languages
from app.utils.file_utils import validate_pdf, FileValidationError


router = APIRouter(prefix="/ocr", tags=["OCR Operations"])


@router.post("/extract")
async def api_ocr_extract(
    file: UploadFile = File(..., description="Scanned PDF file"),
    language: str = Form("eng", description="OCR language code (e.g., 'eng' for English)")
):
    """
    Extract text from scanned PDF using OCR.
    
    Converts PDF pages to images and runs Tesseract OCR.
    Returns JSON with extracted text organized by page.
    
    Supported languages depend on Tesseract installation.
    Default installation includes English ('eng').
    """
    try:
        pdf_bytes = await validate_pdf(file)
        
        # Validate language is available
        available_langs = get_available_languages()
        if language not in available_langs:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{language}' not available. Installed languages: {', '.join(available_langs)}"
            )
        
        # Run OCR
        result = extract_text_ocr(pdf_bytes, language=language)
        
        return JSONResponse(content=result.model_dump())
        
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing OCR: {str(e)}")


@router.get("/languages")
async def api_ocr_languages():
    """
    Get available OCR languages.
    
    Returns list of language codes installed in Tesseract.
    """
    try:
        languages = get_available_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting languages: {str(e)}")
