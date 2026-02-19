# NoTracePDF

Self-hosted, zero-trace, ephemeral PDF and file conversion toolkit.

Like iLovePDF or PDF24Tools, but nothing is ever saved, logged, or traced — files exist only during processing and disappear forever the moment the download finishes.

## Quick Start

```bash
# Clone and run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000
```

## Features

### MVP (Phase 1) - Complete
- [x] Merge multiple PDFs
- [x] Split PDF (by page range, every N pages, extract specific pages)
- [x] Rotate pages / reorder / delete pages
- [x] Compress PDF (with quality presets + image optimization)
- [x] Add / remove password & set permissions
- [x] Add text/image watermark or stamp
- [x] Extract text / images / pages from PDF
- [x] PDF ↔ Images (PNG, JPG, WEBP)
- [x] Images → PDF
- [x] Web UI with drag-and-drop, progress tracking
- [x] Zero-trace architecture verified

### Tier 1 (Phase 2-3)
- [ ] Crop / scale / resize pages
- [ ] Add page numbers
- [ ] Flatten annotations / remove metadata
- [ ] Compare two PDFs (diff highlighting)
- [ ] Redact sensitive text
- [ ] PDF ↔ Office (Word, Excel, PowerPoint)
- [ ] HTML / Markdown / URL → PDF
- [ ] Text / RTF → PDF

### Tier 2 (Phase 4)
- [ ] OCR on scanned PDFs (Tesseract)
- [ ] Batch processing via ZIP
- [ ] Client-side fallback for small files (<20MB)
- [ ] PDF preview
- [ ] Dark mode + responsive mobile UI

## Architecture

### Zero-Trace Guarantee

Every component is designed for privacy:

1. **In-Memory Processing**: All PDF operations use `BytesIO` streams — no user data touches disk
2. **tmpfs Mounts**: `/tmp` and `/app/uploads` are RAM-backed, ephemeral filesystems
3. **No Persistent Volumes**: Docker container has zero persistent storage
4. **Privacy Logging**: Middleware logs only method/path/status — never filenames, IPs, or file sizes
5. **Cache Headers**: All responses include `Cache-Control: no-store, no-cache, must-revalidate, private`

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI + Python 3.12 | Async web framework |
| PDF Processing | pikepdf + PyMuPDF | PDF manipulation and extraction |
| Image Processing | Pillow + pdf2image | Image conversion |
| Deployment | Docker + tmpfs | Zero-persistence container |
| Frontend | Vanilla JS + CSS | Minimal footprint, no external dependencies |

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
docker-compose up -d
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

Run the deployment verification script:

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
```

### Test Categories

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `test_zero_trace.py` | 11 | Verify no file persistence, tmpfs config, no volumes |
| `test_security.py` | 17 | Cache headers, logging privacy, file size limits |
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

### Image Conversion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/image/pdf-to-images` | POST | Convert PDF to images |
| `/api/v1/image/images-to-pdf` | POST | Convert images to PDF |

## Security

- Container runs as non-root user
- No persistent Docker volumes
- tmpfs mounts for all temporary storage (RAM-backed)
- Memory limits prevent resource exhaustion
- Request timeouts prevent DoS attacks
- No user data logged (filenames, IPs, file sizes)
- AES-256 encryption for password protection

## Philosophy

- **Zero persistence**: Files processed in-memory only, never written to disk
- **No traces**: No logging of filenames, IPs, file sizes, or timestamps
- **Self-hosted**: Run on your own NAS/VPS/home lab
- **No accounts**: No tracking, no sessions, no data collection
- **Ephemeral**: Files deleted immediately after download

## License

MIT License - See [LICENSE](LICENSE)

---

*Built for privacy-conscious individuals and teams who want PDF manipulation features on their own server.*
