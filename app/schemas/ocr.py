"""
OCR Schema Definitions.

Reference: ADV-01
"""
from typing import List, Optional
from pydantic import BaseModel


class OCROptions(BaseModel):
    """OCR processing options."""
    language: str = "eng"  # Language for OCR (default: English)


class PageOCRResult(BaseModel):
    """OCR result for a single page."""
    page_number: int
    text: str
    character_count: int


class OCRResponse(BaseModel):
    """OCR extraction response."""
    total_pages: int
    total_characters: int
    pages: List[PageOCRResult]
