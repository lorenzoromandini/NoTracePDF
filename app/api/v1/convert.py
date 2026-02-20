"""
Document Conversion API Endpoints.

All endpoints use in-memory processing with BytesIO.
No user data is written to disk (except temp files in tmpfs for LibreOffice).

Reference: CONV-01 to CONV-11
"""
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.services.conversion_service import (
    office_to_pdf,
    pdf_to_office,
    validate_office_file,
)
from app.utils.file_utils import (
    validate_pdf,
    validate_docx,
    validate_xlsx,
    validate_pptx,
    FileValidationError,
)


router = APIRouter(prefix="/convert", tags=["Document Conversions"])

# =====================================================
# Office to PDF Conversions (CONV-04 to CONV-06)
# =====================================================


@router.post("/word-to-pdf")
async def api_word_to_pdf(
    file: UploadFile = File(..., description="Word document (.docx) to convert")
):
    """
    Convert Word document to PDF.
    
    Accepts .docx files and converts them to PDF using LibreOffice headless.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate file
        docx_bytes = await validate_docx(file)
        
        # Convert to PDF
        pdf_bytes = office_to_pdf(docx_bytes, "docx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting document: {str(e)}")


@router.post("/excel-to-pdf")
async def api_excel_to_pdf(
    file: UploadFile = File(..., description="Excel spreadsheet (.xlsx) to convert")
):
    """
    Convert Excel spreadsheet to PDF.
    
    Accepts .xlsx files and converts them to PDF using LibreOffice headless.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate file
        xlsx_bytes = await validate_xlsx(file)
        
        # Convert to PDF
        pdf_bytes = office_to_pdf(xlsx_bytes, "xlsx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "spreadsheet"
        filename = f"{base_name}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting spreadsheet: {str(e)}")


@router.post("/powerpoint-to-pdf")
async def api_powerpoint_to_pdf(
    file: UploadFile = File(..., description="PowerPoint presentation (.pptx) to convert")
):
    """
    Convert PowerPoint presentation to PDF.
    
    Accepts .pptx files and converts them to PDF using LibreOffice headless.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate file
        pptx_bytes = await validate_pptx(file)
        
        # Convert to PDF
        pdf_bytes = office_to_pdf(pptx_bytes, "pptx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "presentation"
        filename = f"{base_name}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting presentation: {str(e)}")


# =====================================================
# PDF to Office Conversions (CONV-01 to CONV-03)
# =====================================================


@router.post("/pdf-to-word")
async def api_pdf_to_word(
    file: UploadFile = File(..., description="PDF file to convert")
):
    """
    Convert PDF to Word document.
    
    Converts PDF to .docx format using LibreOffice headless.
    Note: Complex PDFs may not convert perfectly to editable Word format.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate PDF
        pdf_bytes = await validate_pdf(file)
        
        # Convert to Word
        docx_bytes = pdf_to_office(pdf_bytes, "docx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}.docx"
        
        return StreamingResponse(
            docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to Word: {str(e)}")


@router.post("/pdf-to-excel")
async def api_pdf_to_excel(
    file: UploadFile = File(..., description="PDF file to convert")
):
    """
    Convert PDF to Excel spreadsheet.
    
    Converts PDF to .xlsx format using LibreOffice headless.
    Note: Tables in PDFs may not convert perfectly to spreadsheet format.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate PDF
        pdf_bytes = await validate_pdf(file)
        
        # Convert to Excel
        xlsx_bytes = pdf_to_office(pdf_bytes, "xlsx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "spreadsheet"
        filename = f"{base_name}.xlsx"
        
        return StreamingResponse(
            xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to Excel: {str(e)}")


@router.post("/pdf-to-powerpoint")
async def api_pdf_to_powerpoint(
    file: UploadFile = File(..., description="PDF file to convert")
):
    """
    Convert PDF to PowerPoint presentation.
    
    Converts PDF to .pptx format using LibreOffice headless.
    Note: Each PDF page becomes one slide.
    All processing uses in-memory streams with zero persistence.
    """
    try:
        # Validate PDF
        pdf_bytes = await validate_pdf(file)
        
        # Convert to PowerPoint
        pptx_bytes = pdf_to_office(pdf_bytes, "pptx")
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "presentation"
        filename = f"{base_name}.pptx"
        
        return StreamingResponse(
            pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except FileValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to PowerPoint: {str(e)}")
