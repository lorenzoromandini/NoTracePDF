# NoTracePDF

Self-hosted, zero-trace, ephemeral PDF and file conversion toolkit.

Like iLovePDF or PDF24Tools, but nothing is ever saved, logged, or traced — files exist only during processing and disappear forever the moment the download finishes.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/NoTracePDF.git
cd NoTracePDF

# Start with Docker Compose
docker compose up -d

# Access the application
open http://localhost:8000
```

## Features

### MVP (Phase 1) - Complete ✓

| Feature | Status | Description |
|---------|--------|-------------|
| Merge PDFs | ✅ | Combine multiple PDFs into one |
| Split PDF | ✅ | By page range, every N pages, or extract specific pages |
| Rotate Pages | ✅ | Rotate single or all pages |
| Reorder Pages | ✅ | Drag and drop page reordering |
| Delete Pages | ✅ | Remove unwanted pages |
| Compress PDF | ✅ | Quality presets (low/medium/high) with image optimization |
| Password Protect | ✅ | AES-256 encryption with permissions |
| Remove Password | ✅ | Unlock protected PDFs |
| Text Watermark | ✅ | Add text watermarks with positioning |
| Image Watermark | ✅ | Add image watermarks with positioning |
| Extract Text | ✅ | Extract text content from PDF |
| Extract Images | ✅ | Extract embedded images |
| Extract Pages | ✅ | Export pages as separate PDFs |
| PDF to Images | ✅ | Convert to PNG, JPG, or WebP |
| Images to PDF | ✅ | Create PDF from multiple images |
| Web UI | ✅ | Modern drag-and-drop interface |
| Zero-Trace | ✅ | Verified privacy architecture |

### Extended (Phase 2) - Complete ✓

| Feature | Status | Description |
|---------|--------|-------------|
| Crop Pages | ✅ | Crop pages to specific dimensions |
| Scale Pages | ✅ | Scale pages to percentage or fit |
| Resize Pages | ✅ | Resize pages to specific size (A4, Letter, etc.) |
| Add Page Numbers | ✅ | Customizable position, format, and font |
| Flatten Annotations | ✅ | Lock comments/highlights into content |
| Remove Metadata | ✅ | Strip author, timestamps, hidden data |
| Compare PDFs | ✅ | Visual diff highlighting between two PDFs |
| Redact Text | ✅ | Permanently black out sensitive text |

### Coming Soon (Phase 3-4)

- PDF → Office (Word, Excel, PowerPoint)
- Office files → PDF
- HTML / Markdown / URL → PDF
- Text / RTF → PDF
- OCR on scanned PDFs
- Batch processing via ZIP
- Client-side fallback for small files
- PDF preview
- Dark mode

## Architecture

### Zero-Trace Guarantee

Every component is designed for privacy from the ground up:

| Layer | Implementation | Purpose |
|-------|---------------|---------|
| **Processing** | BytesIO streams | All PDF operations happen in memory |
| **Storage** | tmpfs mounts | `/tmp` and `/app/uploads` are RAM-backed |
| **Docker** | No volumes | Container has zero persistent storage |
| **Logging** | Privacy middleware | Logs only method/path/status, never user data |
| **Browser** | Cache-Control headers | Prevents browser caching of downloads |

### Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                         │
│  Vanilla JS + CSS (no frameworks, no dependencies) │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/SSE
┌─────────────────────▼───────────────────────────────┐
│                 FastAPI Backend                     │
│  Python 3.12 + Uvicorn + Gunicorn                  │
├─────────────────────────────────────────────────────┤
│  PDF Engine     │  pikepdf (qpdf) + PyMuPDF        │
│  Image Engine   │  Pillow + pdf2image              │
│  Security       │  AES-256 encryption              │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Docker Runtime                      │
│  Debian Slim + tmpfs (no persistent volumes)       │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
NoTracePDF/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── core/
│   │   └── config.py           # Settings and configuration
│   ├── middleware/
│   │   ├── privacy_logging.py  # Strips user data from logs
│   │   └── cache_headers.py    # Adds no-store headers
│   ├── services/
│   │   ├── pdf_service.py      # Merge, split, rotate, reorder
│   │   ├── pdf_security_service.py  # Compress, encrypt
│   │   ├── pdf_watermark_service.py # Watermarks
│   │   ├── pdf_extract_service.py   # Extract text/images/pages
│   │   └── image_service.py    # PDF↔image conversion
│   ├── api/v1/
│   │   ├── pdf.py              # PDF endpoints
│   │   └── image.py            # Image conversion endpoints
│   ├── schemas/
│   │   ├── pdf.py              # PDF request/response models
│   │   └── image.py            # Image conversion models
│   └── static/
│       ├── index.html          # Web UI
│       ├── css/styles.css      # Styles
│       └── js/                 # Frontend JavaScript
├── tests/
│   ├── test_zero_trace.py      # Privacy verification
│   ├── test_security.py        # Security tests
│   ├── test_api.py             # API tests
│   └── test_integration.py     # End-to-end tests
├── scripts/
│   └── verify_deployment.sh    # Deployment verification
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | NoTracePDF | Application name |
| `DEBUG` | false | Enable debug mode |
| `MAX_FILE_SIZE_MB` | 100 | Maximum upload file size |
| `UPLOAD_DIR` | /app/uploads | Temporary upload directory (tmpfs) |
| `REQUEST_TIMEOUT_SECONDS` | 30 | Request timeout in seconds |

## Deployment

### Docker Compose (Recommended)

```bash
docker compose up -d
```

### Docker Run

```bash
docker run -d \
  --name notracepdf \
  --tmpfs /tmp:rw,noexec,nosuid,size=512m \
  --tmpfs /app/uploads:rw,noexec,nosuid,size=256m \
  --memory=1g \
  --cpus=2 \
  -p 8000:8000 \
  notracepdf
```

### Verify Deployment

```bash
# Check container is running
docker ps

# Verify tmpfs mounts
docker exec notracepdf mount | grep tmpfs

# Check health endpoint
curl http://localhost:8000/health
# Expected: {"status":"ok","app":"NoTracePDF"}

# Verify cache headers
curl -I http://localhost:8000/health | grep Cache-Control
# Expected: Cache-Control: no-store, no-cache, must-revalidate, private
```

### Run Verification Script

```bash
./scripts/verify_deployment.sh
```

This checks:
- Container is running
- tmpfs mounts are configured
- No persistent volumes
- Memory limits are set
- Health endpoint responds
- Cache headers are correct

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term

# Run specific test category
pytest tests/test_zero_trace.py -v
```

### Test Categories

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `test_zero_trace.py` | 11 | Verify no file persistence, tmpfs config |
| `test_security.py` | 17 | Cache headers, logging privacy, limits |
| `test_api.py` | 14 | API endpoint functionality |
| `test_integration.py` | 12 | End-to-end workflow tests |

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
| `/api/v1/pdf/crop` | POST | Crop pages to specific dimensions |
| `/api/v1/pdf/scale` | POST | Scale pages to percentage or fit |
| `/api/v1/pdf/resize` | POST | Resize pages to specific size |
| `/api/v1/pdf/page-numbers` | POST | Add page numbers |
| `/api/v1/pdf/flatten` | POST | Flatten annotations into content |
| `/api/v1/pdf/metadata/remove` | POST | Remove all metadata |
| `/api/v1/pdf/compare` | POST | Compare two PDFs with diff highlighting |
| `/api/v1/pdf/redact` | POST | Permanently redact text |

### Image Conversion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/image/pdf-to-images` | POST | Convert PDF to images (PNG/JPG/WebP) |
| `/api/v1/image/images-to-pdf` | POST | Convert images to PDF |

### Example: Merge PDFs

```bash
curl -X POST http://localhost:8000/api/v1/pdf/merge \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  --output merged.pdf
```

### Example: Add Password

```bash
curl -X POST http://localhost:8000/api/v1/pdf/password/add \
  -F "file=@document.pdf" \
  -F "password=secret123" \
  -F "permissions=print,copy" \
  --output protected.pdf
```

## Security

| Feature | Implementation |
|---------|---------------|
| Non-root container | Runs as `appuser` |
| No persistent storage | Zero Docker volumes |
| RAM-only temp storage | tmpfs for `/tmp` and `/app/uploads` |
| Memory limits | 1GB container limit |
| Request timeouts | 30s timeout prevents DoS |
| Privacy logging | No filenames, IPs, or file sizes logged |
| Browser privacy | Cache-Control: no-store headers |
| Encryption | AES-256 for password protection |

## Philosophy

- **Zero persistence**: Files processed in-memory only, never written to disk
- **No traces**: No logging of filenames, IPs, file sizes, or timestamps
- **Self-hosted**: Run on your own NAS/VPS/home lab
- **No accounts**: No tracking, no sessions, no data collection
- **Ephemeral**: Files deleted immediately after download

## Use Cases

- **Privacy-conscious individuals**: Process sensitive documents without cloud exposure
- **Legal professionals**: Handle confidential documents securely
- **Healthcare**: Process patient documents with HIPAA compliance
- **Finance**: Handle financial documents without data retention
- **Home labs**: Self-hosted PDF toolkit for personal use

## License

MIT License - See [LICENSE](LICENSE)

## Contributing

Contributions are welcome! Please ensure any contributions maintain the zero-trace architecture:

1. All file operations must use in-memory processing
2. No persistent storage or logging of user data
3. All responses must include appropriate cache headers

---

*Built for privacy-conscious individuals and teams who want PDF manipulation features on their own server.*
