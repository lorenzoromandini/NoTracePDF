# Roadmap: NoTracePDF

## Overview

NoTracePDF is a self-hosted, zero-trace PDF processing toolkit. The journey delivers a complete MVP in Phase 1 (all core PDF operations with privacy-first architecture), then extends capabilities through document conversions and advanced features. Every phase reinforces the core value: no user data ever persists.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: MVP Foundation** - Complete zero-trace PDF toolkit with 9 core tools, UI, and Docker deployment
- [x] **Phase 2: Extended PDF Operations** - Crop, scale, page numbers, metadata removal, comparison, redaction
- [x] **Phase 3: Document Conversions** - PDF ↔ Office formats, HTML/Markdown/URL → PDF
- [ ] **Phase 4: Advanced Features** - OCR, batch processing, client-side fallback, PDF preview, dark mode

## Phase Details

### Phase 1: MVP Foundation
**Goal**: Users have a complete, self-hosted PDF toolkit that works entirely in-memory with zero data persistence
**Depends on**: Nothing (first phase)
**Requirements**: ARCH-01 to ARCH-08, PDF-01 to PDF-16, IMG-01 to IMG-06, UI-01 to UI-08, DEPLOY-01 to DEPLOY-04 (44 total)
**Success Criteria** (what must be TRUE):
  1. User can merge, split, rotate, compress, and password-protect PDFs through a web interface
  2. User can add watermarks and extract text/images/pages from PDFs
  3. User can convert between PDF and images (PNG/JPG/WebP) in both directions
  4. Zero-trace architecture is verifiable — no files persist after download, no user data logged, cache headers prevent browser caching
  5. Web UI provides drag-and-drop upload, real-time progress, instant download, and clear "files deleted" confirmation
  6. Single Docker container runs on any NAS/VPS/home lab with no external dependencies
**Plans**: 8 plans in 4 waves

Plans:
- [x] 01-01-PLAN.md — Project foundation with privacy logging and cache headers (ARCH-01, ARCH-04, ARCH-05, ARCH-08)
- [x] 01-02-PLAN.md — Docker infrastructure with tmpfs and zero persistence (ARCH-02, ARCH-03, ARCH-06, ARCH-07, DEPLOY-01 to DEPLOY-04)
- [x] 01-03-PLAN.md — PDF core operations: merge, split, rotate, reorder, delete (PDF-01 to PDF-07)
- [x] 01-04-PLAN.md — PDF security: compress, password, watermark (PDF-08 to PDF-13)
- [x] 01-05-PLAN.md — PDF extraction: text, images, pages (PDF-14 to PDF-16)
- [x] 01-06-PLAN.md — Image conversion: PDF↔images (IMG-01 to IMG-06)
- [x] 01-07-PLAN.md — Web UI with all features (UI-01 to UI-08)
- [x] 01-08-PLAN.md — Zero-trace verification and deployment testing (All ARCH, DEPLOY)

### Phase 2: Extended PDF Operations
**Goal**: Users have advanced document manipulation capabilities for professional workflows
**Depends on**: Phase 1
**Requirements**: PDF-17 to PDF-24 (8 total)
**Success Criteria** (what must be TRUE):
  1. User can crop, scale, and resize PDF pages to specific dimensions
  2. User can add page numbers with customizable position and format
  3. User can remove all metadata for complete document anonymization
  4. User can compare two PDFs with visual diff highlighting
  5. User can redact sensitive text permanently (blacked out, not removable)
**Plans**: 4 plans in 1 wave

Plans:
- [x] 02-01-PLAN.md — Page dimension operations: crop, scale, resize (PDF-17, PDF-18, PDF-19)
- [x] 02-02-PLAN.md — Page numbers and anonymization: numbers, flatten, metadata (PDF-20, PDF-21, PDF-22)
- [x] 02-03-PLAN.md — PDF comparison with visual diff highlighting (PDF-23)
- [x] 02-04-PLAN.md — Permanent text redaction (PDF-24)

### Phase 3: Document Conversions
**Goal**: Users can convert between PDF and common document formats without leaving the zero-trace environment
**Depends on**: Phase 2
**Requirements**: CONV-01 to CONV-11 (11 total)
**Success Criteria** (what must be TRUE):
  1. User can convert PDF to Word/Excel/PowerPoint and vice versa
  2. User can convert HTML pages to PDF (from URL or pasted HTML)
  3. User can convert Markdown documents to PDF
  4. User can convert plain text and RTF files to PDF
  5. All conversions maintain zero-trace guarantee (in-memory processing, no persistence)
**Plans**: 3 plans in 2 waves

Plans:
- [x] 03-01-PLAN.md — Office ↔ PDF conversions with LibreOffice headless (CONV-01 to CONV-06)
- [x] 03-02-PLAN.md — HTML/Markdown/URL → PDF with WeasyPrint (CONV-07 to CONV-09)
- [x] 03-03-PLAN.md — Text/RTF → PDF conversions (CONV-10, CONV-11)

### Phase 4: Advanced Features
**Goal**: Users have enterprise-grade capabilities while maintaining privacy-first architecture
**Depends on**: Phase 3
**Requirements**: ADV-01 to ADV-06 (6 total)
**Success Criteria** (what must be TRUE):
  1. User can extract text from scanned PDFs via OCR
  2. User can batch process multiple files via ZIP upload/download
  3. User can process small files (<20MB) entirely client-side for maximum privacy
  4. User can preview PDFs before processing
  5. UI supports dark mode and is fully responsive on mobile devices
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. MVP Foundation | 8/8 | Complete | 01-01, 01-02, 01-03, 01-04, 01-05, 01-06, 01-07, 01-08 |
| 2. Extended PDF Operations | 4/4 | Complete | 02-01, 02-02, 02-03, 02-04 |
| 3. Document Conversions | 3/3 | Complete | 03-01, 03-02, 03-03 |
| 4. Advanced Features | 0/TBD | Not started | - |

---
*Roadmap created: 2026-02-19*
*Depth: comprehensive*
*Coverage: 69/69 requirements mapped*
*Last updated: 2026-02-20 after Phase 3 planning*
