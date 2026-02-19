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

### MVP (Phase 1)
- Merge multiple PDFs
- Split PDF (by page range, every N pages, extract specific pages)
- Rotate pages / reorder / delete pages
- Compress PDF (with quality presets + image optimization)
- Add / remove password & set permissions
- Add text/image watermark or stamp
- Extract text / images / pages from PDF
- PDF ↔ Images (PNG, JPG, WEBP)
- Images → PDF

### Tier 1 (Phase 2-3)
- Crop / scale / resize pages
- Add page numbers
- Flatten annotations / remove metadata
- Compare two PDFs (diff highlighting)
- Redact sensitive text
- PDF ↔ Office (Word, Excel, PowerPoint)
- HTML / Markdown / URL → PDF
- Text / RTF → PDF

### Tier 2 (Phase 4)
- OCR on scanned PDFs (Tesseract)
- Batch processing via ZIP
- Client-side fallback for small files (<20MB)
- PDF preview
- Dark mode + responsive mobile UI

## Philosophy

- **Zero persistence**: Files processed in-memory only, never written to disk
- **No traces**: No logging of filenames, IPs, file sizes, or timestamps
- **Self-hosted**: Run on your own NAS/VPS/home lab
- **No accounts**: No tracking, no sessions, no data collection
- **Ephemeral**: Files deleted immediately after download

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

## Security

- Container runs as non-root user
- No persistent Docker volumes
- tmpfs mounts for all temporary storage (RAM-backed)
- Memory limits prevent resource exhaustion
- Request timeouts prevent DoS attacks
- No user data logged (filenames, IPs, file sizes)

## License

MIT License - See [LICENSE](LICENSE)

---

*Built for privacy-conscious individuals and teams who want PDF manipulation features on their own server.*
