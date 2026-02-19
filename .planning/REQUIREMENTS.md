# Requirements: NoTracePDF

**Defined:** 2026-02-19
**Core Value:** Total privacy by design — no user data ever persists. Files exist only in memory during processing and are immediately destroyed after download.

## v1 Requirements

### Architecture & Security

- [x] **ARCH-01**: All file processing uses in-memory streams (BytesIO) — no disk writes for user data
- [x] **ARCH-02**: Docker container has zero persistent volumes for user data
- [x] **ARCH-03**: Temporary files (if required) use tmpfs-mounted /tmp — RAM-backed, ephemeral
- [x] **ARCH-04**: Server logs contain no filenames, IP addresses, file sizes, or timestamps of user activity
- [x] **ARCH-05**: All download responses include `Cache-Control: no-store, no-cache, must-revalidate, private` headers
- [x] **ARCH-06**: Container memory limits prevent memory exhaustion from malicious PDFs
- [x] **ARCH-07**: Request timeouts prevent DoS via slow uploads
- [x] **ARCH-08**: Cleanup handlers run on all exit paths (success, error, SIGTERM)

### Core PDF Operations (MVP)

- [x] **PDF-01**: User can merge multiple PDFs into single document
- [x] **PDF-02**: User can split PDF by page range
- [x] **PDF-03**: User can split PDF by extracting every N pages
- [x] **PDF-04**: User can extract specific pages from PDF
- [x] **PDF-05**: User can rotate pages (single or all)
- [x] **PDF-06**: User can reorder pages via visual interface
- [x] **PDF-07**: User can delete pages from PDF
- [x] **PDF-08**: User can compress PDF with quality presets (low/medium/high)
- [x] **PDF-09**: User can add password protection with open password
- [x] **PDF-10**: User can set PDF permissions (print, copy, edit)
- [x] **PDF-11**: User can remove password protection (with valid password)
- [x] **PDF-12**: User can add text watermark with positioning options
- [x] **PDF-13**: User can add image watermark with positioning options
- [x] **PDF-14**: User can extract text from PDF
- [x] **PDF-15**: User can extract images from PDF
- [x] **PDF-16**: User can extract pages from PDF as separate files

### Image Conversion (MVP)

- [x] **IMG-01**: User can convert PDF pages to PNG images
- [x] **IMG-02**: User can convert PDF pages to JPG images
- [x] **IMG-03**: User can convert PDF pages to WebP images
- [x] **IMG-04**: User can convert single PDF page or all pages
- [x] **IMG-05**: User can convert multiple images (PNG/JPG/WebP) into single PDF
- [x] **IMG-06**: User can specify page sizing when creating PDF from images

### User Interface

- [x] **UI-01**: Clean, modern, single-page web UI with tool cards in grid layout
- [x] **UI-02**: Drag and drop upload zone supporting multiple files
- [x] **UI-03**: Tool-specific options panel (page ranges, quality slider, password field, etc.)
- [x] **UI-04**: Real-time progress bar during processing (via SSE or WebSocket)
- [x] **UI-05**: Instant download with sensible default filename
- [x] **UI-06**: Post-download message: "All files have been permanently deleted from the server"
- [x] **UI-07**: No history, no "recent files", no cookies except optional UI preferences
- [x] **UI-08**: Responsive design supporting mobile devices

### Deployment

- [x] **DEPLOY-01**: Self-hosted Docker deployment
- [x] **DEPLOY-02**: Single container deployment (no external dependencies)
- [x] **DEPLOY-03**: MIT or AGPLv3 license
- [x] **DEPLOY-04**: Runs on NAS/VPS/home lab hardware

## Tier 1 Requirements (Post-MVP)

### Extended PDF Operations

- [ ] **PDF-17**: User can crop pages to specific dimensions
- [ ] **PDF-18**: User can scale pages to specific sizes
- [ ] **PDF-19**: User can resize pages
- [ ] **PDF-20**: User can add page numbers with position and format options
- [ ] **PDF-21**: User can flatten annotations into document content
- [ ] **PDF-22**: User can remove metadata (author, timestamps, hidden data)
- [ ] **PDF-23**: User can compare two PDFs with diff highlighting
- [ ] **PDF-24**: User can redact (permanently black out) sensitive text

### Document Conversion

- [ ] **CONV-01**: User can convert PDF to Word (.docx)
- [ ] **CONV-02**: User can convert PDF to Excel (.xlsx)
- [ ] **CONV-03**: User can convert PDF to PowerPoint (.pptx)
- [ ] **CONV-04**: User can convert Word (.docx) to PDF
- [ ] **CONV-05**: User can convert Excel (.xlsx) to PDF
- [ ] **CONV-06**: User can convert PowerPoint (.pptx) to PDF
- [ ] **CONV-07**: User can convert HTML to PDF
- [ ] **CONV-08**: User can convert Markdown to PDF
- [ ] **CONV-09**: User can convert URL (web page) to PDF
- [ ] **CONV-10**: User can convert plain text to PDF
- [ ] **CONV-11**: User can convert RTF to PDF

## Tier 2 Requirements (Future)

### Advanced Features

- [ ] **ADV-01**: User can perform OCR on scanned PDFs (Tesseract)
- [ ] **ADV-02**: User can batch process files via ZIP upload/download
- [ ] **ADV-03**: Client-side fallback for merge/split/rotate on files < 20MB (zero server load)
- [ ] **ADV-04**: User can preview uploaded PDFs (PDF.js rendering)
- [ ] **ADV-05**: Dark mode UI theme
- [ ] **ADV-06**: Fully responsive mobile-first UI design

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / login | Violates core value of zero-trace; creates liability |
| Persistent storage / "My Documents" | Contradicts core value of ephemeral processing |
| Shareable links with expiration | Creates persistence; requires tracking |
| E-signing with server storage | Requires document persistence |
| Analytics / telemetry | Violates privacy promise |
| Cloud sync / backup | Creates data persistence |
| Video/audio conversion | Outside document scope |
| Real-time collaborative editing | Requires session management and persistence |
| AI features (translation, summarization) | Requires sending content to external services |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 1 | Complete |
| ARCH-02 | Phase 1 | Complete |
| ARCH-03 | Phase 1 | Complete |
| ARCH-04 | Phase 1 | Complete |
| ARCH-05 | Phase 1 | Complete |
| ARCH-06 | Phase 1 | Complete |
| ARCH-07 | Phase 1 | Complete |
| ARCH-08 | Phase 1 | Complete |
| PDF-01 | Phase 1 | Complete |
| PDF-02 | Phase 1 | Complete |
| PDF-03 | Phase 1 | Complete |
| PDF-04 | Phase 1 | Complete |
| PDF-05 | Phase 1 | Complete |
| PDF-06 | Phase 1 | Complete |
| PDF-07 | Phase 1 | Complete |
| PDF-08 | Phase 1 | Complete |
| PDF-09 | Phase 1 | Complete |
| PDF-10 | Phase 1 | Complete |
| PDF-11 | Phase 1 | Complete |
| PDF-12 | Phase 1 | Complete |
| PDF-13 | Phase 1 | Complete |
| PDF-14 | Phase 1 | Complete |
| PDF-15 | Phase 1 | Complete |
| PDF-16 | Phase 1 | Complete |
| IMG-01 | Phase 1 | Complete |
| IMG-02 | Phase 1 | Complete |
| IMG-03 | Phase 1 | Complete |
| IMG-04 | Phase 1 | Complete |
| IMG-05 | Phase 1 | Complete |
| IMG-06 | Phase 1 | Complete |
| UI-01 | Phase 1 | Complete |
| UI-02 | Phase 1 | Complete |
| UI-03 | Phase 1 | Complete |
| UI-04 | Phase 1 | Complete |
| UI-05 | Phase 1 | Complete |
| UI-06 | Phase 1 | Complete |
| UI-07 | Phase 1 | Complete |
| UI-08 | Phase 1 | Complete |
| DEPLOY-01 | Phase 1 | Complete |
| DEPLOY-02 | Phase 1 | Complete |
| DEPLOY-03 | Phase 1 | Complete |
| DEPLOY-04 | Phase 1 | Complete |
| PDF-17 | Phase 2 | Pending |
| PDF-18 | Phase 2 | Pending |
| PDF-19 | Phase 2 | Pending |
| PDF-20 | Phase 2 | Pending |
| PDF-21 | Phase 2 | Pending |
| PDF-22 | Phase 2 | Pending |
| PDF-23 | Phase 2 | Pending |
| PDF-24 | Phase 2 | Pending |
| CONV-01 | Phase 3 | Pending |
| CONV-02 | Phase 3 | Pending |
| CONV-03 | Phase 3 | Pending |
| CONV-04 | Phase 3 | Pending |
| CONV-05 | Phase 3 | Pending |
| CONV-06 | Phase 3 | Pending |
| CONV-07 | Phase 3 | Pending |
| CONV-08 | Phase 3 | Pending |
| CONV-09 | Phase 3 | Pending |
| CONV-10 | Phase 3 | Pending |
| CONV-11 | Phase 3 | Pending |
| ADV-01 | Phase 4 | Pending |
| ADV-02 | Phase 4 | Pending |
| ADV-03 | Phase 4 | Pending |
| ADV-04 | Phase 4 | Pending |
| ADV-05 | Phase 4 | Pending |
| ADV-06 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 44 total
- Tier 1 requirements: 19 total
- Tier 2 requirements: 6 total
- Mapped to phases: 69
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-19*
*Last updated: 2026-02-19 after Plan 01-07 completion (Web UI)*
