# NoTracePDF

Self-hosted, zero-trace, ephemeral PDF and file conversion toolkit.

Like iLovePDF or PDF24Tools, but nothing is ever saved, logged, or traced — files exist only during processing and disappear forever the moment the download finishes.

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

## Deployment

Docker deployment with tmpfs mounts for zero persistence:

```bash
docker run -d \
  --tmpfs /tmp:rw,noexec,nosuid,size=1g \
  -p 8000:8000 \
  notracepdf
```

## License

MIT or AGPLv3

## Status

Project initialized. See `.planning/ROADMAP.md` for development phases.

---
*Last updated: 2026-02-19*
