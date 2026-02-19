# NoTracePDF

## What This Is

Self-hosted, zero-trace, ephemeral PDF and file conversion toolkit. Like iLovePDF or PDF24Tools, but nothing is ever saved, logged, or traced — files exist only during processing and disappear forever the moment the download finishes. Built for privacy-conscious individuals and teams who want PDF manipulation features on their own server/NAS/VPS/home lab.

## Core Value

Total privacy by design — no user data ever persists. Files exist only in memory during processing and are immediately destroyed after download. Zero logging, zero tracking, zero traces.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**MVP Features (Must be working in first 2 weeks):**
- [ ] Merge multiple PDFs
- [ ] Split PDF (by page range, every N pages, extract specific pages)
- [ ] Rotate pages / reorder / delete pages
- [ ] Compress PDF (with quality presets + image optimization)
- [ ] Add / remove password & set permissions
- [ ] Add text/image watermark or stamp
- [ ] Extract text / images / pages from PDF
- [ ] PDF ↔ Images (PNG, JPG, WEBP – single or all pages)
- [ ] Images → PDF (multiple images into one PDF, with optional page sizing)

**Tier 1 Features (Add immediately after MVP):**
- [ ] Crop / scale / resize pages
- [ ] Add page numbers
- [ ] Flatten annotations / remove metadata
- [ ] Compare two PDFs (basic diff highlight)
- [ ] PDF → Word (.docx), Excel (.xlsx), PowerPoint (.pptx) via LibreOffice headless
- [ ] Office files → PDF
- [ ] HTML / Markdown / URL → PDF
- [ ] Text / RTF → PDF

**Tier 2 Features (Nice-to-have after core is stable):**
- [ ] OCR on scanned PDFs (Tesseract)
- [ ] Batch processing: upload ZIP → process all files → return ZIP
- [ ] Client-side fallbacks (pdf-lib.js + PDF.js) for merge/split/rotate when file < 20 MB
- [ ] Simple preview of uploaded PDFs (using PDF.js)
- [ ] Dark mode + fully responsive mobile-first UI

### Out of Scope

- Any form of persistent storage or "My Documents" — contradicts core value
- User accounts / login — contradicts core value
- Shareable links with expiration — contradicts core value
- E-signing that requires server storage — contradicts core value
- Video/audio conversion — outside document scope
- Anything unrelated to documents/PDFs — outside scope
- Analytics or telemetry — contradicts core value

## Context

**Target Users:** Privacy-conscious individuals and teams who want iLovePDF features on their own server/NAS/VPS/home lab.

**Inspiration:** iLovePDF, PDF24Tools — same functionality but without any data collection or persistence.

**License:** MIT (or AGPLv3 if copyleft preferred).

## Constraints

- **Zero Persistence:** Uploaded files and generated results must never be written to disk permanently. Use in-memory processing (BytesIO, memory streams) wherever possible. Any temporary files must be created inside a RAM-backed tmpfs or auto-deleted BEFORE the HTTP response is sent.
- **No Traces:** No logs of filenames, IP addresses (except error-level anonymous logs), file sizes, or timestamps of user activity. Server must be runnable entirely from RAM (tmpfs /tmp). Docker container must have zero persistent volumes for user data.
- **Scope:** ONLY PDF manipulation tools + common file-format conversions. Nothing else.
- **Ephemeral Only:** After user downloads result, original files and result must be immediately garbage-collected or deleted.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| In-memory processing | Guarantees no disk persistence | — Pending |
| No user accounts | Eliminates session tracking | — Pending |
| Self-hosted only | User controls all data | — Pending |

---
*Last updated: 2026-02-19 after initialization*
