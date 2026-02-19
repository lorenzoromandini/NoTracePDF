"""
Schemas package.
"""
from app.schemas.pdf import (
    SplitMode,
    WatermarkPosition,
    PageSelection,
    QualityPreset,
    ImageFormat,
    PageSize,
    MergeRequest,
    SplitRequest,
    RotateRequest,
    ReorderRequest,
    DeletePagesRequest,
    CompressRequest,
    PasswordRequest,
    RemovePasswordRequest,
    TextWatermarkRequest,
    ImageWatermarkRequest,
    ExtractTextRequest,
    ExtractTextResponse,
    ExtractImagesRequest,
    ExtractPagesRequest,
)
from app.schemas.image import PdfToImageRequest, ImageToPdfRequest

__all__ = [
    # Enums
    "SplitMode",
    "WatermarkPosition",
    "PageSelection",
    "QualityPreset",
    "ImageFormat",
    "PageSize",
    # PDF schemas
    "MergeRequest",
    "SplitRequest",
    "RotateRequest",
    "ReorderRequest",
    "DeletePagesRequest",
    "CompressRequest",
    "PasswordRequest",
    "RemovePasswordRequest",
    "TextWatermarkRequest",
    "ImageWatermarkRequest",
    "ExtractTextRequest",
    "ExtractTextResponse",
    "ExtractImagesRequest",
    "ExtractPagesRequest",
    # Image schemas
    "PdfToImageRequest",
    "ImageToPdfRequest",
]
