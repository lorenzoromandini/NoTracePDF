# Project Research Summary

**Project:** NoTracePDF
**Domain:** Privacy-focused, self-hosted PDF processing toolkit
**Researched:** 2026-02-19
**Confidence:** HIGH (with one gap noted)

## Executive Summary

NoTracePDF is a self-hosted PDF manipulation toolkit with a unique zero-trace architecture: files exist only in memory during processing and disappear immediately after download. This differentiates it from competitors like iLovePDF (cloud-based) and Stirling-PDF (optional persistence). The recommended approach uses Python with FastAPI for async performance, pikepdf/PyMuPDF for PDF operations, and Docker with tmpfs mounts to guarantee zero disk persistence.

The core architectural constraint is **in-memory processing with zero persistence**—every technology choice flows from this requirement. This enables the privacy guarantee but introduces complexity around memory limits, compression bomb protection, and careful handling of edge cases like LibreOffice conversion (which requires temporary files on tmpfs). Critical pitfalls to avoid include logging user data, browser caching of downloads, and Docker volume persistence—all of which would violate the zero-trace promise.

## Key Findings

### Recommended Stack

Python-based stack optimized for async in-memory processing. FastAPI provides streaming file handling and automatic OpenAPI docs. pikepdf (built on qpdf C++ library) handles PDF manipulation with full BytesIO support. Docker with tmpfs mounts ensures files never touch persistent storage.

**Core technologies:**
- **Python 3.10+**: Runtime with async/await improvements
- **FastAPI 0.129.0**: Async web framework with native streaming support
- **pikepdf 10.4.0+**: PDF manipulation (merge, split, encrypt, compress) — fastest, full in-memory support
- **PyMuPDF 1.25+**: PDF text/image extraction — fastest for rendering
- **Pillow 12.1.0+**: Image format conversion — native BytesIO support
- **WeasyPrint 63+**: HTML/CSS to PDF generation — pure Python, no browser required
- **Docker + tmpfs**: Deployment with RAM-backed temporary storage

**Critical constraint:** Every library must support BytesIO/memory streams. Avoid libraries that require disk I/O for user files.

### Expected Features

Research identified 30+ features across table stakes, differentiators, and anti-features. Competitors offer 25-50+ tools; focused approach of ~20 core tools recommended.

**Must have (table stakes):**
- Merge PDF — most common operation, establishes trust
- Split PDF — by range, by page, extract specific pages
- Rotate PDF — fix scanned document orientation
- Compress PDF — quality presets, image optimization
- Password Protect/Remove — security expected feature
- Add Watermark — text or image with positioning
- PDF ↔ Images — bidirectional conversion (PNG/JPG/WebP)
- Images → PDF — create PDFs from photos/scans
- Delete/Reorder Pages — basic document organization

**Should have (competitive):**
- Zero-Trace Processing — core differentiator, non-negotiable
- Self-Hosted Docker — deployment method, expected
- No User Accounts — no tracking, simplified architecture
- Remove Metadata — privacy-critical feature
- Redact PDF — permanently black out sensitive text
- PDF ↔ Office Conversion — requires LibreOffice headless
- Compare PDFs — side-by-side diff highlighting

**Defer (v2+):**
- OCR — requires Tesseract + language packs (~50-200MB per language)
- Client-Side Fallback — ultimate privacy, significant frontend work
- Batch Processing (ZIP) — high leverage but requires ZIP handling
- PDF Preview — nice to have, requires PDF.js integration

**Anti-features (explicitly NOT building):**
- User accounts / "My Documents" — violates zero-trace
- Shareable links with expiration — creates persistence
- Cloud sync / backup — violates privacy promise
- Analytics / telemetry — violates privacy promise

### Architecture Approach

*Note: ARCHITECTURE.md was not created by researcher. Architecture implications derived from STACK.md and PITFALLS.md.*

**Core architectural pattern:** In-memory request-response pipeline. Uploads stream into BytesIO, processing happens entirely in memory, response streams directly to client. No disk writes except for tmpfs-mounted /tmp (RAM-backed, ephemeral).

**Major components:**
1. **FastAPI Application Layer** — Async request handling, file upload parsing, streaming responses, privacy-aware logging middleware
2. **PDF Processing Engine** — pikepdf for manipulation, PyMuPDF for extraction, Pillow for images; all operate on BytesIO streams
3. **Conversion Service** — LibreOffice headless (via unoserver) for Office↔PDF; requires tmpfs for temp files
4. **Docker Runtime** — tmpfs mounts for /tmp and uploads, memory limits, read-only root filesystem where possible

**Security boundaries:**
- No persistent volumes (Docker)
- No logging of filenames, IPs, file sizes, or content
- Cache-Control headers on all downloads
- Request timeouts and memory limits per container

### Critical Pitfalls

Top pitfalls that could break the zero-trace guarantee or cause security issues:

1. **Memory Exhaustion via Compression Bombs** — Malicious PDFs can decompress from KB to GB. Prevention: Container memory limits, request timeouts, streaming processing where possible.

2. **Temporary File Leakage** — Files left in /tmp expose user data. Prevention: Process entirely in memory; if disk required, use tmpfs and cleanup handlers for all exit paths (success, error, SIGTERM).

3. **Logging User Data** — Default logging captures filenames, IPs, request bodies. Prevention: Custom logging middleware that sanitizes all user input; log only method and path.

4. **Browser Caching Downloads** — Generated PDFs cached by browsers violate zero-trace. Prevention: Always set `Cache-Control: no-store, no-cache, must-revalidate, private` on download responses.

5. **Docker Volume Persistence** — Accidental volumes or bind mounts persist data. Prevention: No `VOLUME` in Dockerfile, no `volumes:` in docker-compose, use tmpfs only.

## Implications for Roadmap

Based on research, suggested 5-phase structure:

### Phase 1: Core PDF Operations + Zero-Trace Foundation
**Rationale:** Security and privacy foundation must be established before any user file processing. Table stakes features validate the concept.
**Delivers:** Working MVP with 9 core tools, Docker deployment, zero-persistence verification
**Addresses:** Merge, Split, Rotate, Compress, Password, Watermark, PDF↔Images, Images→PDF, Delete/Reorder Pages
**Avoids:** All 5 critical pitfalls (memory limits, tmpfs, logging, cache headers, no volumes)
**Stack:** FastAPI, pikepdf, Pillow, python-multipart, Docker+tmpfs

### Phase 2: Extended Conversion (Office & HTML)
**Rationale:** LibreOffice integration is high-complexity; separate phase allows focused testing of resource-intensive operations.
**Delivers:** PDF↔Word/Excel/PPT, HTML→PDF, Markdown→PDF
**Uses:** LibreOffice headless, unoserver, WeasyPrint, pypandoc
**Implements:** Conversion Service component
**Warning:** LibreOffice adds ~500MB+ to container size; consider separate "full" Docker image variant

### Phase 3: Privacy Enhancement Features
**Rationale:** Features that differentiate NoTracePDF from competitors, building on stable core.
**Delivers:** Remove Metadata, Redact PDF, Compare PDFs, Flatten Annotations, Crop/Scale Pages
**Uses:** PyMuPDF (text extraction), pikepdf (metadata stripping)
**Addresses:** Differentiator features from FEATURES.md

### Phase 4: Advanced Features
**Rationale:** Higher complexity features that expand utility but require significant dependencies.
**Delivers:** OCR (Tesseract), Batch Processing (ZIP handling)
**Dependencies:** Tesseract + language packs, ZIP stream handling
**Note:** OCR language packs add 50-200MB each; default to English only

### Phase 5: Web UI & Client-Side Fallback
**Rationale:** Frontend work can proceed in parallel but delivery depends on stable backend API.
**Delivers:** Modern responsive UI (dark mode), PDF preview, client-side processing for small files
**Uses:** Vite+React or Svelte, pdf.js (preview), pdf-lib.js (client-side manipulation)
**Value:** Ultimate privacy for small files (<20MB) — zero server involvement

### Phase Ordering Rationale

- **Security first:** Phase 1 establishes the zero-trace foundation before any processing happens
- **Dependencies respected:** LibreOffice (Phase 2) requires larger container; Tesseract (Phase 4) needs language packs
- **Complexity progressive:** Core operations (pikepdf) are simpler than LibreOffice conversion, which is simpler than OCR
- **Validation loop:** Phase 1 MVP validates concept before investing in heavier features

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** LibreOffice headless integration — complex setup, security considerations (CVE-2024-12425), resource tuning
- **Phase 4:** OCR integration — language pack management, Tesseract configuration, accuracy tuning

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented FastAPI + pikepdf patterns, clear Docker tmpfs configuration
- **Phase 5:** pdf.js and pdf-lib.js have excellent documentation and examples

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified from official sources; pikepdf, FastAPI, Pillow have excellent in-memory support documentation |
| Features | HIGH | Competitor analysis from 6+ sources; feature priorities validated against multiple PDF tools |
| Architecture | MEDIUM | ARCHITECTURE.md not created; derived from STACK.md and PITFALLS.md — needs validation during planning |
| Pitfalls | HIGH | CVE sources, OWASP guides, Docker documentation — all high-quality references |

**Overall confidence:** HIGH

### Gaps to Address

1. **Missing ARCHITECTURE.md:** Architecture implications derived from STACK.md and PITFALLS.md. During planning, explicitly define:
   - Component boundaries between FastAPI app and processing modules
   - Error handling and cleanup patterns
   - Async processing patterns for large files

2. **LibreOffice resource tuning:** PITFALLS.md notes LibreOffice security concerns. Phase 2 planning should research:
   - Optimal memory/CPU limits for LibreOffice container
   - unoserver vs direct subprocess calls
   - Read-only filesystem configuration

3. **Client-side fallback scope:** pdf-lib.js supports merge/split/rotate but not all operations. Phase 5 planning should define:
   - Which operations support client-side fallback
   - File size threshold implementation
   - Fallback detection and routing logic

## Sources

### Primary (HIGH confidence)
- **FastAPI Official Docs** — https://fastapi.tiangolo.com/ (version 0.129.0)
- **pikepdf Documentation** — https://pikepdf.readthedocs.io (version 10.4.0)
- **pypdf GitHub Releases** — https://github.com/py-pdf/pypdf/releases (version 6.7.1)
- **Pillow Documentation** — https://pillow.readthedocs.io (version 12.1.0)
- **WeasyPrint Documentation** — https://doc.courtbouillon.org/weasyprint/
- **Docker tmpfs Documentation** — https://docs.docker.com/engine/storage/tmpfs/
- **Stirling-PDF GitHub** — https://github.com/Stirling-Tools/Stirling-PDF (74.3k stars)

### Secondary (MEDIUM confidence)
- **iLovePDF** — https://www.ilovepdf.com/ (competitor feature analysis)
- **PDF24 Tools** — https://www.pdf24.org/ (competitor feature analysis)
- **PurePDF, HonestPDF, LocalPDF** — client-side processing examples
- **Uvicorn Production Guide** — Multiple sources (2025)

### Security Sources (HIGH confidence)
- **CVE-2025-68428** — jsPDF Path Traversal
- **CVE-2025-62708** — pypdf LZWDecode RAM Exhaustion
- **CVE-2024-12425** — LibreOffice File Write vulnerability
- **OWASP Testing Guide** — Browser Cache Weaknesses
- **Docker Resource Constraints** — Official documentation

---
*Research completed: 2026-02-19*
*Ready for roadmap: yes*
*Note: ARCHITECTURE.md missing — architecture derived from available research*
