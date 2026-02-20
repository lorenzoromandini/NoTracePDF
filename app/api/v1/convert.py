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
from app.services.web_conversion_service import (
    html_to_pdf,
    markdown_to_pdf,
    url_to_pdf,
)
from app.services.text_conversion_service import (
    text_to_pdf,
    rtf_to_pdf,
    validate_rtf_content,
)
from app.utils.file_utils import (
    validate_pdf,
    validate_docx,
    validate_xlsx,
    validate_pptx,
    validate_rtf,
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


# =====================================================
# HTML/Markdown/URL to PDF Conversions (CONV-07 to CONV-09)
# =====================================================


@router.post("/html-to-pdf")
async def api_html_to_pdf(
    html: str = Form(..., description="HTML content to convert"),
    base_url: Optional[str] = Form(None, description="Base URL for relative links")
):
    """
    Convert HTML content to PDF.
    
    Accepts HTML string and converts it to PDF using WeasyPrint.
    CSS styles in the HTML are preserved.
    
    Optionally provide base_url to resolve relative URLs in the HTML.
    """
    try:
        # Convert HTML to PDF
        pdf_bytes = html_to_pdf(html, base_url)
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="converted.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting HTML to PDF: {str(e)}")


@router.post("/markdown-to-pdf")
async def api_markdown_to_pdf(
    markdown: str = Form(..., description="Markdown content to convert")
):
    """
    Convert Markdown content to PDF.
    
    Accepts Markdown string and converts it to PDF.
    Supports common Markdown features:
    - Tables
    - Code blocks with syntax highlighting style
    - Headers
    - Lists
    - Blockquotes
    """
    try:
        # Convert Markdown to PDF
        pdf_bytes = markdown_to_pdf(markdown)
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="converted.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting Markdown to PDF: {str(e)}")


@router.post("/url-to-pdf")
async def api_url_to_pdf(
    url: str = Form(..., description="URL to convert to PDF"),
    timeout: int = Form(30, description="Fetch timeout in seconds", ge=5, le=120)
):
    """
    Convert web page URL to PDF.
    
    Fetches the web page at the given URL and converts it to PDF.
    
    SECURITY RESTRICTIONS:
    - Only HTTP/HTTPS URLs are allowed
    - Private IP addresses are blocked (SSRF prevention)
    - Localhost and internal URLs are blocked
    
    The fetched page's CSS styling is preserved in the PDF.
    """
    try:
        # Convert URL to PDF (includes SSRF validation)
        pdf_bytes = await url_to_pdf(url, timeout)
        
        # Generate filename from URL
        from urllib.parse import urlparse as parse_url
        parsed = parse_url(url)
        domain = parsed.netloc or "converted"
        # Clean domain for filename
        safe_domain = "".join(c if c.isalnum() or c in '-_' else '_' for c in domain)
        filename = f"{safe_domain}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except ValueError as e:
        # URL validation failed (SSRF protection)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower():
            raise HTTPException(status_code=504, detail=f"URL fetch timed out: {error_msg}")
        if "404" in error_msg or "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"URL not found: {url}")
        if "403" in error_msg or "forbidden" in error_msg.lower():
            raise HTTPException(status_code=403, detail=f"Access forbidden: {url}")
        raise HTTPException(status_code=500, detail=f"Error converting URL to PDF: {error_msg}")


# =====================================================
# Text/RTF to PDF Conversions (CONV-10, CONV-11)
# =====================================================


@router.post("/text-to-pdf")
async def api_text_to_pdf(
    text: Optional[str] = Form(None, description="Text content to convert"),
    file: Optional[UploadFile] = File(None, description="Text file to convert (.txt)"),
    font_size: int = Form(12, description="Font size in points", ge=6, le=72),
    font_family: str = Form("helv", description="Font family: helv, cour, or tim")
):
    """
    Convert plain text to PDF.
    
    Provide either 'text' (string) or 'file' (.txt upload), not both.
    
    Font family options:
    - helv: Helvetica (sans-serif, default)
    - cour: Courier (monospace)
    - tim: Times (serif)
    
    Text wrapping and multi-page documents are handled automatically.
    """
    try:
        # Validate font family
        valid_fonts = {'helv', 'cour', 'tim'}
        if font_family.lower() not in valid_fonts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid font family. Must be one of: {', '.join(valid_fonts)}"
            )
        
        # Get text content
        if file:
            content = await file.read()
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Could not decode text file. Please use UTF-8 encoding."
                    )
        elif text:
            text_content = text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'text' or 'file' parameter is required"
            )
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Text content is empty")
        
        # Convert to PDF
        pdf_bytes = text_to_pdf(
            text_content,
            font_size=font_size,
            font_family=font_family.lower()
        )
        
        # Generate filename
        if file and file.filename:
            base_name = file.filename.rsplit('.', 1)[0]
        else:
            base_name = "converted"
        filename = f"{base_name}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting text to PDF: {str(e)}")


@router.post("/rtf-to-pdf")
async def api_rtf_to_pdf(
    file: UploadFile = File(..., description="RTF file to convert")
):
    """
    Convert RTF document to PDF.
    
    RTF files are converted using LibreOffice headless.
    Formatting (bold, italic, tables, etc.) is preserved.
    
    All processing uses in-memory streams with temp files only in tmpfs.
    """
    try:
        # Read content
        content = await file.read()
        
        # Validate RTF header
        if not validate_rtf_content(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid RTF file. File does not have RTF header."
            )
        
        # Convert to PDF
        rtf_bytes = BytesIO(content)
        pdf_bytes = rtf_to_pdf(rtf_bytes)
        
        base_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        filename = f"{base_name}.pdf"
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting RTF to PDF: {str(e)}")
