"""
Schemas for image conversion operations.
"""
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.pdf import PageSelection, ImageFormat, PageSize


class PdfToImageRequest(BaseModel):
    """Request model for converting PDF to images."""
    format: ImageFormat = Field(default=ImageFormat.PNG, description="Output format")
    pages: Union[PageSelection, List[int]] = Field(
        default=PageSelection.ALL,
        description="Pages to convert: 'all', 'first', or list of page numbers"
    )
    dpi: int = Field(default=200, ge=72, le=600, description="DPI for rendering")
    quality: int = Field(default=85, ge=1, le=100, description="Quality for JPG/WebP (1-100)")


class ImageToPdfRequest(BaseModel):
    """Request model for converting images to PDF."""
    page_size: PageSize = Field(
        default=PageSize.A4,
        description="Page size: a4, letter, fit, or original"
    )
    margin: int = Field(default=0, ge=0, le=100, description="Margin in pixels")
    fit_to_page: bool = Field(
        default=True,
        description="Scale image to fit page (true) or center at original size (false)"
    )
