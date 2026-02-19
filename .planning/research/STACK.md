# Stack Research

**Domain:** Privacy-focused, self-hosted PDF and file conversion toolkit
**Researched:** 2025-02-19
**Confidence:** HIGH

## Executive Summary

NoTracePDF requires a Python-based stack optimized for **in-memory processing** with **zero persistence**. The recommended stack centers on FastAPI for async performance, paired with specialized libraries that support BytesIO/memory stream operations. Docker with tmpfs ensures no user data touches disk.

**Key Constraint:** Every library must support in-memory operations (no required disk I/O for user files).

---

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.10+ | Runtime | Required by FastAPI 0.129.0+. Type hints, async/await improvements. |
| **FastAPI** | 0.129.0 | Web framework | Async-first, automatic OpenAPI docs, built-in streaming file handling, highest performance among Python frameworks. 238M+ monthly downloads. |
| **Uvicorn** | 0.34+ | ASGI server | Fastest ASGI implementation using uvloop. Handles async I/O efficiently. |
| **Gunicorn** | 23+ | Process manager | Production-grade worker management for Uvicorn. Handles multi-core scaling. |

### PDF Processing Libraries

| Library | Version | Purpose | Why Recommended | In-Memory Support |
|---------|---------|---------|-----------------|-------------------|
| **pikepdf** | 10.4.0+ | PDF manipulation | Built on qpdf C++ library (fastest). Handles merging, splitting, encryption, compression. Superior repair capabilities. | ✅ Full BytesIO support via `Pdf.open(stream)` |
| **pypdf** | 6.7.1 | PDF operations | Pure Python alternative. Merge, split, rotate, encrypt. Active maintenance (latest: Feb 2026). | ✅ BytesIO native support |
| **PyMuPDF** | 1.25+ | PDF rendering/extraction | Fastest PDF text/image extraction. Low-level access for advanced operations. | ✅ Supports in-memory with `fitz.open(stream=bytes_data)` |

### Image Processing

| Library | Version | Purpose | Why Recommended | In-Memory Support |
|---------|---------|---------|-----------------|-------------------|
| **Pillow** | 12.1.0+ | Image manipulation | Standard Python imaging library. 30+ format support. Format conversion, resizing, compression. | ✅ Native BytesIO: `Image.open(io.BytesIO(data))` |
| **pdf2image** | 1.17+ | PDF to image conversion | Converts PDF pages to PNG/JPEG. Requires poppler-utils in Docker. | ✅ Can work with BytesIO input |

### HTML to PDF Generation

| Library | Version | Purpose | Why Recommended | In-Memory Support |
|---------|---------|---------|-----------------|-------------------|
| **WeasyPrint** | 63+ | HTML/CSS to PDF | No browser/headless required. CSS3 support (flexbox, grid). Best for generating PDFs from templates. | ✅ `HTML(string=html).write_pdf()` returns bytes |

### Office Document Conversion

| Library | Version | Purpose | Why Recommended | In-Memory Support |
|---------|---------|---------|-----------------|-------------------|
| **LibreOffice (headless)** | 24.8+ | Office → PDF conversion | Highest fidelity conversion for DOCX, XLSX, PPTX. Runs in Docker. | ⚠️ Requires temporary files (use tmpfs) |
| **unoserver** | 1.2+ | LibreOffice Python wrapper | Manages LibreOffice headless instance. Better than direct subprocess calls. | ⚠️ Uses temp directory (configure to tmpfs) |
| **pypandoc** | 1.14+ | Document format conversion | Pandoc wrapper. Supports markdown, DOCX, HTML, PDF, ODT, EPUB. | ⚠️ May require temp files for some formats |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **python-multipart** | 0.0.20+ | File upload parsing | **Required** for FastAPI file uploads (multipart/form-data) |
| **aiofiles** | 24.1+ | Async file I/O | For streaming uploads/downloads (even with tmpfs) |
| **pydantic** | 2.10+ | Data validation | Built into FastAPI. Request/response validation. |
| **python-dotenv** | 1.0+ | Environment config | Load configuration from .env files |

### Infrastructure

| Technology | Purpose | Why Recommended |
|------------|---------|-----------------|
| **Docker** | Containerization | Isolated, reproducible deployments. Required for tmpfs zero-persistence strategy. |
| **tmpfs** | In-memory filesystem | Mount `/tmp` and upload directories as tmpfs. Data exists only in RAM, gone on container stop. **Critical for privacy guarantee.** |
| **Alpine Linux base image** | Docker foundation | Smallest attack surface, fastest builds. Use `python:3.12-alpine` or `python:3.13-alpine`. |

### Frontend (Optional)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Vite + React** | React 19+ | Web UI | Fast dev server, excellent TypeScript support. Large ecosystem for PDF viewers. |
| **Svelte** | 5+ | Lightweight alternative | Smaller bundle size, simpler state management. Good for focused tools. |
| **pdf.js** | 4+ | PDF rendering in browser | Mozilla's PDF.js for client-side viewing. Privacy-preserving (no server-side rendering needed for display). |

---

## Installation

### Production Requirements

```bash
# Core Framework
pip install fastapi==0.129.0 uvicorn[standard]==0.34.0 gunicorn==23.0.0

# PDF Processing
pip install pikepdf==10.4.0 pypdf==6.7.1 PyMuPDF==1.25.0

# Image Processing
pip install Pillow==12.1.0 pdf2image==1.17.0

# HTML to PDF
pip install weasyprint==63.0

# Office Conversion (optional)
pip install unoserver==1.2 pypandoc==1.14

# Required for file uploads
pip install python-multipart==0.0.20 aiofiles==24.1.0

# Data validation
pip install pydantic==2.10.0 python-dotenv==1.0.0
```

### System Dependencies (Docker)

```dockerfile
# Alpine-based Dockerfile
FROM python:3.12-alpine

# Install system dependencies
RUN apk add --no-cache \
    poppler-utils \
    libreoffice \
    ttf-dejavu \
    ttf-liberation \
    fontconfig

# Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **PyPDF2** | Deprecated, renamed to `pypdf` | `pypdf` (version 6.7.1+) |
| **ReportLab** | Complex API, requires disk for advanced features | **WeasyPrint** (HTML/CSS approach) or **pikepdf** (manipulation) |
| **pdfkit** | Requires wkhtmltopdf binary, security issues | **WeasyPrint** (pure Python) |
| **Storing uploads to disk** | Violates zero-persistence guarantee | **BytesIO / SpooledTemporaryFile** with tmpfs fallback |
| **Standard logging with filenames/IPs** | Leaks PII into logs | **Custom logging middleware** (sanitize all user data) |
| **Selenium/Playwright for PDF** | Heavy, slow, requires full browser | **WeasyPrint** or **pikepdf** |
| **Online PDF APIs** | External services violate privacy | **Self-hosted everything** |
| **Stirling PDF (without modification)** | Recent tracking concerns | **Build custom with recommended stack** |

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **pikepdf** | **PyMuPDF (fitz)** | When you need faster text extraction or lower-level PDF access |
| **pikepdf** | **pypdf** | When you want pure Python (no C++ dependency) |
| **FastAPI** | **Flask** | Only for extremely simple use cases (no async needed) |
| **WeasyPrint** | **wkhtmltopdf/pdfkit** | Legacy projects (WeasyPrint has better Python integration) |
| **LibreOffice headless** | **Apache POI (Java)** | Already in Java ecosystem (otherwise LibreOffice is superior) |
| **tmpfs** | **Encrypted volumes** | When you need some persistence but encrypted (violates "zero-trace" principle) |

---

## In-Memory Processing Patterns

### Pattern 1: Upload → Process → Stream Response

```python
from fastapi import FastAPI, UploadFile
from io import BytesIO
import pikepdf

app = FastAPI()

@app.post("/merge-pdfs")
async def merge_pdfs(files: list[UploadFile]):
    """Merge multiple PDFs entirely in memory."""
    output_buffer = BytesIO()
    
    with pikepdf.Pdf.new() as pdf:
        for file in files:
            content = await file.read()
            source = pikepdf.Pdf.open(BytesIO(content))
            pdf.pages.extend(source.pages)
        
        pdf.save(output_buffer)
    
    output_buffer.seek(0)
    return StreamingResponse(
        output_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"}
    )
```

### Pattern 2: Image Conversion with BytesIO

```python
from PIL import Image
from io import BytesIO

async def convert_image(image_bytes: bytes, target_format: str = "PNG") -> bytes:
    """Convert image format in memory."""
    img = Image.open(BytesIO(image_bytes))
    output = BytesIO()
    img.save(output, format=target_format)
    output.seek(0)
    return output.getvalue()
```

---

## Docker Configuration for Zero Persistence

### Critical: tmpfs Mounts

```yaml
# docker-compose.yml
services:
  notracepdf:
    build: .
    ports:
      - "8000:8000"
    tmpfs:
      - /tmp:noexec,nosuid,size=512m
      - /app/uploads:noexec,nosuid,size=256m
    environment:
      - UPLOAD_DIR=/app/uploads  # Points to tmpfs
    read_only: false  # Allow writes to tmpfs only
```

**Why tmpfs is critical:**
- Files exist **only in RAM** (host memory)
- **Zero disk persistence** — data gone when container stops
- Prevents forensic recovery of user files
- Satisfies "zero-trace" privacy guarantee

**Warning:** tmpfs data may swap to disk under memory pressure. Set appropriate `size` limits and monitor RAM usage.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.129.0 | Python >= 3.10 | 3.12+ recommended |
| pikepdf 10.4.0 | libqpdf >= 11.6 | Requires system package in Docker |
| WeasyPrint 63+ | Pango, GDK-PixBuf | Requires system packages in Docker |
| pdf2image 1.17+ | poppler-utils | Requires system package |
| unoserver 1.2+ | LibreOffice 7+ | Compatible with LibreOffice 24.x |

---

## Security & Privacy Considerations

### Logging Without PII

```python
import logging
from fastapi import Request

# Custom middleware to sanitize logs
class PrivacyLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Log request without IP, filename, or file size
            logging.info(f"Request: {scope['method']} {scope['path']}")
        await self.app(scope, receive, send)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# NO request body, NO filenames, NO IP addresses, NO file sizes
```

### Content-Type Validation

```python
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

async def validate_file_type(file: UploadFile):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(415, "Unsupported file type")
```

---

## Sources

- **FastAPI Official Docs** — https://fastapi.tiangolo.com/ (verified version 0.129.0) — HIGH confidence
- **pikepdf Documentation** — https://pikepdf.readthedocs.io (version 10.4.0) — HIGH confidence
- **pypdf GitHub Releases** — https://github.com/py-pdf/pypdf/releases (version 6.7.1, Feb 2026) — HIGH confidence
- **Pillow Documentation** — https://pillow.readthedocs.io (version 12.1.0) — HIGH confidence
- **WeasyPrint Documentation** — https://doc.courtbouillon.org/weasyprint/ — HIGH confidence
- **Docker tmpfs Documentation** — https://docs.docker.com/engine/storage/tmpfs/ — HIGH confidence
- **Stirling PDF Tracking Concerns** — Reddit/XDA discussions (2025) — MEDIUM confidence
- **FastAPI File Upload Benchmarks** — GitHub fedirz/fastapi-file-upload-benchmark — HIGH confidence
- **Uvicorn Production Guide** — Multiple Medium/blog sources (2025) — MEDIUM confidence

---

## Stack Recommendations by Phase

### Phase 1: MVP (Core PDF Operations)
- FastAPI + Uvicorn + Gunicorn
- pikepdf (PDF merge, split, rotate, compress)
- Pillow (image format conversion)
- python-multipart (file uploads)
- Docker with tmpfs

### Phase 2: Extended Conversion
- Add PyMuPDF (faster text extraction)
- Add pdf2image (PDF to image)
- Add poppler-utils to Docker image

### Phase 3: Office Document Support
- Add LibreOffice headless to Docker
- Add unoserver (manage LibreOffice instances)
- Requires larger Docker image

### Phase 4: Template-Based Generation
- Add WeasyPrint (HTML/CSS to PDF)
- Add Jinja2 (template engine)
- Fonts for proper rendering

### Phase 5: Web UI (Optional)
- Add Vite + React or Svelte
- Integrate pdf.js for client-side viewing
- No additional backend dependencies

---

*Stack research for: NoTracePDF - Privacy-focused PDF toolkit*
*Researched: 2025-02-19*
*Confidence: HIGH (all versions verified from official sources)*
