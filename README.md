# NoTracePDF

Self-hosted, zero-trace, ephemeral PDF toolkit. Like iLovePDF, but nothing is ever saved, logged, or traced — files exist only during processing and disappear forever after download.

## Why NoTracePDF?

- **Zero persistence**: Files processed in-memory only, never written to disk
- **No traces**: No logging of filenames, IPs, file sizes, or timestamps  
- **Self-hosted**: Run on your own NAS/VPS/home lab
- **No accounts**: No tracking, no sessions, no data collection
- **Ephemeral**: Files deleted immediately after download

## Use Cases

- **Privacy-conscious individuals**: Process sensitive documents without cloud exposure
- **Legal professionals**: Handle confidential documents securely
- **Healthcare**: Process patient documents with privacy compliance
- **Finance**: Handle financial documents without data retention
- **Home labs**: Self-hosted PDF toolkit for personal use

## Quick Start

```bash
git clone https://github.com/lorenzoromandini/NoTracePDF.git
cd NoTracePDF
docker compose up -d
open http://localhost:8000
```

## Features (42 Tools)

### Core PDF Operations
Merge, Split, Rotate, Reorder, Delete pages, Compress, Password protect/remove, Text/Image watermark, Extract text/images/pages

### Image Conversion
PDF → Images (PNG/JPG/WebP), Images → PDF

### Document Conversions
PDF ↔ Word/Excel/PowerPoint, HTML → PDF, Markdown → PDF, URL → PDF, Text → PDF, RTF → PDF

### Extended Operations
Crop, Scale, Resize, Page numbers, Flatten annotations, Remove metadata, Compare PDFs, Redact text

### Advanced
OCR (Tesseract), Batch ZIP processing, Client-side fallback (<20MB), PDF preview, Dark mode, Responsive UI

## Deployment

### Docker Compose (Recommended)

```bash
docker compose up -d
```

### Docker Run

```bash
docker run -d --name notracepdf \
  --tmpfs /tmp:rw,noexec,nosuid,size=512m \
  --tmpfs /app/uploads:rw,noexec,nosuid,size=256m \
  --memory=1g -p 8000:8000 notracepdf
```

### Verify

```bash
curl http://localhost:8000/health
# {"status":"ok","app":"NoTracePDF"}

docker exec notracepdf mount | grep tmpfs
# Should show /tmp and /app/uploads as tmpfs
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | NoTracePDF | Application name |
| `DEBUG` | false | Enable debug mode |
| `MAX_FILE_SIZE_MB` | 100 | Maximum upload file size |

## API Endpoints

### PDF Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/pdf/merge` | POST | Merge multiple PDFs |
| `/api/v1/pdf/split` | POST | Split PDF by range or pages |
| `/api/v1/pdf/rotate` | POST | Rotate pages |
| `/api/v1/pdf/reorder` | POST | Reorder pages |
| `/api/v1/pdf/delete-pages` | POST | Delete pages |
| `/api/v1/pdf/compress` | POST | Compress with quality presets |
| `/api/v1/pdf/password/add` | POST | Add password protection |
| `/api/v1/pdf/password/remove` | POST | Remove password |
| `/api/v1/pdf/watermark/text` | POST | Add text watermark |
| `/api/v1/pdf/watermark/image` | POST | Add image watermark |
| `/api/v1/pdf/extract/text` | POST | Extract text from PDF |
| `/api/v1/pdf/extract/images` | POST | Extract images from PDF |
| `/api/v1/pdf/extract/pages` | POST | Extract pages as separate PDFs |
| `/api/v1/pdf/crop` | POST | Crop pages to dimensions |
| `/api/v1/pdf/scale` | POST | Scale pages by percentage |
| `/api/v1/pdf/resize` | POST | Resize pages to standard sizes |
| `/api/v1/pdf/page-numbers` | POST | Add page numbers |
| `/api/v1/pdf/flatten` | POST | Flatten annotations |
| `/api/v1/pdf/metadata/remove` | POST | Remove all metadata |
| `/api/v1/pdf/compare` | POST | Compare two PDFs (diff) |
| `/api/v1/pdf/redact` | POST | Permanently redact text |
| `/api/v1/pdf/ocr` | POST | OCR text extraction |

### Document Conversions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/convert/pdf-to-word` | POST | PDF → Word (.docx) |
| `/api/v1/convert/pdf-to-excel` | POST | PDF → Excel (.xlsx) |
| `/api/v1/convert/pdf-to-ppt` | POST | PDF → PowerPoint (.pptx) |
| `/api/v1/convert/word-to-pdf` | POST | Word → PDF |
| `/api/v1/convert/excel-to-pdf` | POST | Excel → PDF |
| `/api/v1/convert/ppt-to-pdf` | POST | PowerPoint → PDF |
| `/api/v1/convert/html-to-pdf` | POST | HTML → PDF |
| `/api/v1/convert/markdown-to-pdf` | POST | Markdown → PDF |
| `/api/v1/convert/url-to-pdf` | POST | URL → PDF |
| `/api/v1/convert/text-to-pdf` | POST | Plain text → PDF |
| `/api/v1/convert/rtf-to-pdf` | POST | RTF → PDF |

### Image Conversion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/image/pdf-to-images` | POST | PDF → Images (PNG/JPG/WebP) |
| `/api/v1/image/images-to-pdf` | POST | Images → PDF |

### Batch Processing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/batch/process` | POST | Batch process PDFs via ZIP |

### Examples

```bash
# Merge PDFs
curl -X POST http://localhost:8000/api/v1/pdf/merge \
  -F "files=@doc1.pdf" -F "files=@doc2.pdf" \
  --output merged.pdf

# Add password
curl -X POST http://localhost:8000/api/v1/pdf/password/add \
  -F "file=@doc.pdf" -F "password=secret123" \
  --output protected.pdf

# Convert URL to PDF
curl -X POST http://localhost:8000/api/v1/convert/url-to-pdf \
  -F "url=https://example.com" \
  --output page.pdf
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v
```

## Security

| Feature | Implementation |
|---------|---------------|
| Non-root container | Runs as `appuser` |
| No persistent storage | Zero Docker volumes |
| RAM-only temp storage | tmpfs for /tmp and /app/uploads |
| Memory limits | 1GB container limit |
| Privacy logging | No filenames, IPs, or file sizes logged |
| Browser privacy | Cache-Control: no-store headers |
| Encryption | AES-256 for password protection |

## Tech Stack

- **Backend**: FastAPI + Python 3.12 + pikepdf + PyMuPDF
- **Frontend**: Vanilla JS + CSS (no frameworks)
- **Docker**: Debian Slim + tmpfs (no persistent volumes)
- **OCR**: Tesseract
- **Office**: LibreOffice headless

## License

MIT License

---

*Built for privacy-conscious individuals and teams.*
