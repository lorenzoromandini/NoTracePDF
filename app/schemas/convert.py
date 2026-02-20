"""
Schemas for document conversion operations.

Reference: CONV-01 to CONV-11
"""
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class OfficeFormat(str, Enum):
    """Office format options for conversion."""
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"


class WebConversionFormat(str, Enum):
    """Web content format options."""
    HTML = "html"
    MARKDOWN = "markdown"
    URL = "url"


class TextConversionFormat(str, Enum):
    """Text format options."""
    TEXT = "text"
    RTF = "rtf"


# === PDF to Office Request ===
class PdfToOfficeRequest(BaseModel):
    """Request model for PDF to Office conversion."""
    output_format: OfficeFormat = Field(
        ...,
        description="Output format: docx, xlsx, or pptx"
    )


# === Office to PDF Request ===
class OfficeToPdfRequest(BaseModel):
    """Request model for Office to PDF conversion."""
    input_format: OfficeFormat = Field(
        ...,
        description="Input format: docx, xlsx, or pptx"
    )


# === HTML to PDF Request ===
class HtmlToPdfRequest(BaseModel):
    """Request model for HTML to PDF conversion."""
    html: str = Field(..., min_length=1, description="HTML content to convert")
    base_url: Optional[str] = Field(
        None,
        description="Base URL for resolving relative links"
    )


# === Markdown to PDF Request ===
class MarkdownToPdfRequest(BaseModel):
    """Request model for Markdown to PDF conversion."""
    markdown: str = Field(..., min_length=1, description="Markdown content to convert")


# === URL to PDF Request ===
class UrlToPdfRequest(BaseModel):
    """Request model for URL to PDF conversion."""
    url: str = Field(..., description="URL to convert to PDF")
    timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Fetch timeout in seconds"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL scheme."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


# === Text to PDF Request ===
class TextToPdfRequest(BaseModel):
    """Request model for plain text to PDF conversion."""
    text: str = Field(..., min_length=1, description="Text content to convert")
    font_size: int = Field(default=12, ge=6, le=72, description="Font size in points")
    font_family: str = Field(
        default="helv",
        description="Font family: helv (Helvetica), cour (Courier), tim (Times)"
    )

    @field_validator('font_family')
    @classmethod
    def validate_font_family(cls, v):
        """Validate font family."""
        valid_fonts = ['helv', 'cour', 'tim', 'symbol', 'zdbf']
        if v.lower() not in valid_fonts:
            raise ValueError(f"Font family must be one of: {', '.join(valid_fonts)}")
        return v.lower()


# === RTF to PDF Request ===
class RtfToPdfRequest(BaseModel):
    """Request model for RTF to PDF conversion."""
    # File is uploaded, no additional parameters needed
    pass
