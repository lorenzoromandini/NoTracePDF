"""
Schemas for PDF operations.

All schemas use Pydantic for validation and serialization.
"""
from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class SplitMode(str, Enum):
    """Split mode options."""
    RANGE = "range"
    EVERY_N = "every_n"
    SPECIFIC = "specific"


class WatermarkPosition(str, Enum):
    """Watermark position options."""
    CENTER = "center"
    DIAGONAL = "diagonal"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class PageSelection(str, Enum):
    """Page selection options."""
    ALL = "all"
    FIRST = "first"
    LAST = "last"


class QualityPreset(str, Enum):
    """Compression quality presets."""
    LOW = "low"      # 72 DPI, aggressive compression
    MEDIUM = "medium"  # 150 DPI, balanced
    HIGH = "high"    # 300 DPI, minimal compression


class ImageFormat(str, Enum):
    """Image format options."""
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    ORIGINAL = "original"


class PageSize(str, Enum):
    """Page size options for image to PDF conversion."""
    A4 = "a4"
    LETTER = "letter"
    FIT = "fit"
    ORIGINAL = "original"


# === Merge Request ===
class MergeRequest(BaseModel):
    """Request model for merging PDFs."""
    # No body needed - files uploaded via multipart


# === Split Request ===
class SplitRequest(BaseModel):
    """Request model for splitting PDFs."""
    mode: SplitMode
    start: Optional[int] = Field(None, description="Start page (1-indexed) for range mode")
    end: Optional[int] = Field(None, description="End page (1-indexed) for range mode")
    n_pages: Optional[int] = Field(None, description="Split every N pages")
    pages: Optional[List[int]] = Field(None, description="Specific pages to extract (1-indexed)")

    @field_validator('start', 'end', 'n_pages', 'pages', mode='before')
    @classmethod
    def validate_mode_params(cls, v, info):
        """Validate that appropriate parameters are provided for each mode."""
        return v


# === Rotate Request ===
class RotateRequest(BaseModel):
    """Request model for rotating PDF pages."""
    pages: Union[str, List[int]] = Field(
        default="all",
        description="Pages to rotate: 'all' or list of page numbers (1-indexed)"
    )
    degrees: int = Field(..., description="Rotation degrees: 90, 180, or 270")

    @field_validator('degrees')
    @classmethod
    def validate_degrees(cls, v):
        """Validate rotation degrees."""
        if v not in [90, 180, 270, -90, -180, -270]:
            raise ValueError("Degrees must be 90, 180, or 270")
        return v


# === Reorder Request ===
class ReorderRequest(BaseModel):
    """Request model for reordering PDF pages."""
    page_order: List[int] = Field(
        ...,
        description="New page order as list (1-indexed, e.g., [3, 1, 2, 4])"
    )


# === Delete Pages Request ===
class DeletePagesRequest(BaseModel):
    """Request model for deleting PDF pages."""
    pages: List[int] = Field(
        ...,
        description="Pages to delete (1-indexed)"
    )


# === Compress Request ===
class CompressRequest(BaseModel):
    """Request model for compressing PDFs."""
    quality: QualityPreset = Field(
        default=QualityPreset.MEDIUM,
        description="Compression quality preset"
    )


# === Password Request ===
class PasswordRequest(BaseModel):
    """Request model for adding password protection."""
    password: str = Field(..., min_length=1, description="Password to set")
    permissions: Optional[List[str]] = Field(
        default=None,
        description="Permissions: print, copy, edit, annotate, fill_forms, extract"
    )


# === Remove Password Request ===
class RemovePasswordRequest(BaseModel):
    """Request model for removing password protection."""
    password: str = Field(..., description="Current password")


# === Text Watermark Request ===
class TextWatermarkRequest(BaseModel):
    """Request model for adding text watermark."""
    text: str = Field(..., min_length=1, description="Watermark text")
    font_size: int = Field(default=48, ge=8, le=200, description="Font size")
    color: str = Field(default="#808080", description="Hex color code")
    opacity: float = Field(default=0.3, ge=0.0, le=1.0, description="Opacity 0-1")
    position: WatermarkPosition = Field(default=WatermarkPosition.DIAGONAL)
    pages: Union[PageSelection, List[int]] = Field(
        default=PageSelection.ALL,
        description="Pages to watermark"
    )


# === Image Watermark Request ===
class ImageWatermarkRequest(BaseModel):
    """Request model for adding image watermark."""
    opacity: float = Field(default=0.3, ge=0.0, le=1.0, description="Opacity 0-1")
    position: WatermarkPosition = Field(default=WatermarkPosition.CENTER)
    scale: float = Field(default=0.5, ge=0.1, le=1.0, description="Scale relative to page")
    pages: Union[PageSelection, List[int]] = Field(
        default=PageSelection.ALL,
        description="Pages to watermark"
    )


# === Extract Text Request ===
class ExtractTextRequest(BaseModel):
    """Request model for extracting text from PDF."""
    pages: Optional[List[int]] = Field(
        default=None,
        description="Pages to extract (1-indexed), None for all pages"
    )


class PageText(BaseModel):
    """Text content from a single page."""
    page_number: int
    text: str
    character_count: int


class ExtractTextResponse(BaseModel):
    """Response model for text extraction."""
    total_pages: int
    total_characters: int
    pages: List[PageText]


# === Extract Images Request ===
class ExtractImagesRequest(BaseModel):
    """Request model for extracting images from PDF."""
    pages: Optional[List[int]] = Field(
        default=None,
        description="Pages to extract from (1-indexed), None for all"
    )
    format: ImageFormat = Field(
        default=ImageFormat.ORIGINAL,
        description="Output format for images"
    )


# === Extract Pages Request ===
class ExtractPagesRequest(BaseModel):
    """Request model for extracting pages as separate PDFs."""
    pages: List[int] = Field(
        ...,
        description="Pages to extract as separate PDFs (1-indexed)"
    )


# =====================================================
# Phase 2: Extended PDF Operations (PDF-17 to PDF-24)
# =====================================================

# === Page Dimensions ===
class PageDimensions(BaseModel):
    """Page dimensions in points."""
    width: float = Field(..., description="Page width in points")
    height: float = Field(..., description="Page height in points")


# === Crop Request ===
class CropRequest(BaseModel):
    """Request model for cropping PDF pages."""
    left: float = Field(default=0, ge=0, description="Left margin in points")
    right: float = Field(default=0, ge=0, description="Right margin in points")
    top: float = Field(default=0, ge=0, description="Top margin in points")
    bottom: float = Field(default=0, ge=0, description="Bottom margin in points")
    pages: Union[str, List[int]] = Field(
        default="all",
        description="Pages to crop: 'all' or list of page numbers (1-indexed)"
    )


# === Scale Request ===
class ScaleRequest(BaseModel):
    """Request model for scaling PDF page content."""
    scale: float = Field(..., gt=0, description="Scale factor (e.g., 0.5 = 50%, 2.0 = 200%)")
    pages: Union[str, List[int]] = Field(
        default="all",
        description="Pages to scale: 'all' or list of page numbers (1-indexed)"
    )

    @field_validator('scale')
    @classmethod
    def validate_scale(cls, v):
        """Validate scale is reasonable."""
        if v <= 0:
            raise ValueError("Scale must be positive")
        if v > 10:
            raise ValueError("Scale cannot exceed 10x (1000%)")
        return v


# === Resize Request ===
class ResizeRequest(BaseModel):
    """Request model for resizing PDF page canvas."""
    width: float = Field(..., gt=0, description="New page width in points")
    height: float = Field(..., gt=0, description="New page height in points")
    pages: Union[str, List[int]] = Field(
        default="all",
        description="Pages to resize: 'all' or list of page numbers (1-indexed)"
    )


# === Page Number Position ===
class PageNumberPosition(str, Enum):
    """Position options for page numbers."""
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    TOP_CENTER = "top-center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"


# === Page Number Request ===
class PageNumberRequest(BaseModel):
    """Request model for adding page numbers."""
    format: str = Field(
        default="Page {page} of {total}",
        description="Format string with {page} and {total} placeholders"
    )
    position: PageNumberPosition = Field(
        default=PageNumberPosition.BOTTOM_CENTER,
        description="Position for page numbers"
    )
    font_size: int = Field(default=12, ge=6, le=72, description="Font size in points")
    color: str = Field(default="#000000", description="Hex color code")
    start_at: int = Field(default=1, ge=1, description="Starting page number")
    pages: Optional[List[int]] = Field(
        default=None,
        description="Pages to number (1-indexed), None for all pages"
    )


# === Flatten Request ===
class FlattenRequest(BaseModel):
    """Request model for flattening annotations."""
    pass  # No additional parameters needed


# === Metadata Field ===
class MetadataField(str, Enum):
    """Metadata field names."""
    TITLE = "title"
    AUTHOR = "author"
    SUBJECT = "subject"
    KEYWORDS = "keywords"
    CREATOR = "creator"
    PRODUCER = "producer"
    CREATION_DATE = "creationDate"
    MODIFICATION_DATE = "modDate"


# === Remove Metadata Request ===
class RemoveMetadataRequest(BaseModel):
    """Request model for removing metadata."""
    fields: Optional[List[str]] = Field(
        default=None,
        description="Metadata fields to remove. If None, removes all. "
                    "Valid values: title, author, subject, keywords, creator, producer, creationDate, modDate"
    )


# === Compare Options ===
class CompareOptions(BaseModel):
    """Options for PDF comparison."""
    highlight_add: str = Field(
        default="#00FF00",
        description="Hex color for additions (content in file2 not in file1)"
    )
    highlight_del: str = Field(
        default="#FF0000",
        description="Hex color for deletions (content in file1 not in file2)"
    )
    include_summary: bool = Field(
        default=True,
        description="Whether to include a summary page"
    )
    dpi: int = Field(
        default=150,
        ge=72,
        le=300,
        description="Rendering DPI for comparison"
    )


# === Compare Result ===
class CompareResult(BaseModel):
    """Statistics from PDF comparison."""
    pages_original: int
    pages_modified: int
    pages_compared: int
    pages_added: int
    pages_removed: int
    pages_changed: int


# === Redact Pattern ===
class RedactPattern(BaseModel):
    """Pattern for redaction."""
    text: str = Field(..., description="Text pattern to redact")
    match_exact: bool = Field(default=False, description="Match exact text only")
    case_sensitive: bool = Field(default=True, description="Case-sensitive matching")


# === Redact Request ===
class RedactRequest(BaseModel):
    """Request model for redacting text."""
    patterns: List[str] = Field(
        ...,
        min_length=1,
        description="List of text patterns to redact"
    )
    match_exact: bool = Field(
        default=False,
        description="If True, match exact text only; if False, match substrings"
    )
    case_sensitive: bool = Field(
        default=True,
        description="Whether to match case"
    )
    fill_color: str = Field(
        default="#000000",
        description="Hex color for redaction fill"
    )
    border_color: Optional[str] = Field(
        default=None,
        description="Optional hex color for redaction border"
    )
    pages: Union[str, List[int]] = Field(
        default="all",
        description="Pages to redact: 'all' or list of page numbers (1-indexed)"
    )


# === Page Dimensions Response ===
class PageDimensionsResponse(BaseModel):
    """Response model for page dimensions."""
    page: int
    width: Optional[float] = None
    height: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    crop_width: Optional[float] = None
    crop_height: Optional[float] = None
