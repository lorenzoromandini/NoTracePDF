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
`POST /api/v1/pdf/merge` `split` `rotate` `reorder` `delete-pages` `compress` `password/add` `password/remove` `watermark/text` `watermark/image` `extract/text` `extract/images` `extract/pages` `crop` `scale` `resize` `page-numbers` `flatten` `metadata/remove` `compare` `redact` `ocr`

### Conversions
`POST /api/v1/convert/pdf-to-word` `pdf-to-excel` `pdf-to-ppt` `word-to-pdf` `excel-to-pdf` `ppt-to-pdf` `html-to-pdf` `markdown-to-pdf` `url-to-pdf` `text-to-pdf` `rtf-to-pdf`

### Batch & Images
`POST /api/v1/batch/process` `image/pdf-to-images` `image/images-to-pdf`

### Example

```bash
curl -X POST http://localhost:8000/api/v1/pdf/merge \
  -F "files=@doc1.pdf" -F "files=@doc2.pdf" \
  --output merged.pdf
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
