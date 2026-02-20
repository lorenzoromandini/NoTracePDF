"""
Batch Schema Definitions.

Reference: ADV-02
"""
from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class BatchOperation(str, Enum):
    """Supported batch operations."""
    COMPRESS = "compress"
    ROTATE = "rotate"
    SPLIT = "split"
    PASSWORD = "password"


class BatchOptions(BaseModel):
    """Options for batch processing."""
    operation: BatchOperation
    # Compress options
    quality: Optional[str] = "medium"  # low, medium, high
    # Rotate options
    degrees: Optional[int] = 90  # 90, 180, 270
    # Split options
    split_mode: Optional[str] = "range"  # range, every_n
    n_pages: Optional[int] = 1  # for every_n mode
    # Password options
    password: Optional[str] = None


class BatchResultFile(BaseModel):
    """Result for a single file in batch."""
    original_name: str
    result_name: Optional[str] = None
    success: bool
    error: Optional[str] = None


class BatchResponse(BaseModel):
    """Batch processing response."""
    total_files: int
    processed: int
    failed: int
    files: List[BatchResultFile]
