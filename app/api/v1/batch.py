"""
Batch Processing API Endpoints.

Provides batch processing for multiple PDFs via ZIP upload/download.
All processing is done in-memory with no disk persistence.

Reference: ADV-02
"""
from io import BytesIO
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.services.batch_service import process_batch_zip, list_zip_contents
from app.schemas.batch import BatchOperation
from app.utils.file_utils import FileValidationError


router = APIRouter(prefix="/batch", tags=["Batch Operations"])


@router.post("/process")
async def api_batch_process(
    file: UploadFile = File(..., description="ZIP file containing PDFs"),
    operation: str = Form(..., description="Operation: compress, rotate, split, password"),
    quality: Optional[str] = Form("medium", description="Quality for compress: low, medium, high"),
    degrees: Optional[int] = Form(90, description="Rotation degrees: 90, 180, 270"),
    split_mode: Optional[str] = Form("range", description="Split mode: range or every_n"),
    n_pages: Optional[int] = Form(1, description="Pages per split for every_n mode"),
    password: Optional[str] = Form(None, description="Password for password operation")
):
    """
    Process multiple PDFs in a ZIP file.
    
    Upload a ZIP file containing PDFs, select an operation,
    and download a ZIP with processed results.
    
    Supported operations:
    - compress: Reduce file size with quality presets
    - rotate: Rotate all pages by specified degrees
    - split: Split each PDF into pages
    - password: Add password protection
    """
    try:
        # Validate file is a ZIP
        if not file.filename or not file.filename.lower().endswith('.zip'):
            raise HTTPException(
                status_code=400,
                detail="File must be a ZIP archive"
            )
        
        content = await file.read()
        zip_bytes = BytesIO(content)
        
        # Validate operation
        try:
            batch_op = BatchOperation(operation)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation. Must be one of: {', '.join([op.value for op in BatchOperation])}"
            )
        
        # Validate specific options
        if batch_op == BatchOperation.COMPRESS:
            if quality not in ["low", "medium", "high"]:
                raise HTTPException(
                    status_code=400,
                    detail="Quality must be: low, medium, or high"
                )
        
        if batch_op == BatchOperation.ROTATE:
            if degrees not in [90, 180, 270]:
                raise HTTPException(
                    status_code=400,
                    detail="Degrees must be: 90, 180, or 270"
                )
        
        if batch_op == BatchOperation.PASSWORD:
            if not password:
                raise HTTPException(
                    status_code=400,
                    detail="Password is required for password operation"
                )
        
        # Import options here to avoid circular import
        from app.schemas.batch import BatchOptions
        
        options = BatchOptions(
            operation=batch_op,
            quality=quality,
            degrees=degrees,
            split_mode=split_mode,
            n_pages=n_pages,
            password=password
        )
        
        # Process the ZIP
        result_zip = process_batch_zip(zip_bytes, options)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "batch"
        filename = f"{base_name}_processed_{timestamp}.zip"
        
        return StreamingResponse(
            result_zip,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")
