# Feature Research

**Domain:** PDF Processing Tools (Privacy-Focused, Self-Hosted)
**Researched:** 2026-02-19
**Confidence:** HIGH (verified via official sources: iLovePDF, PDF24, Stirling-PDF, PurePDF, HonestPDF, LocalPDF)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Merge PDF** | Core operation everyone needs — combining contracts, reports, scans | LOW | Table stakes. Every PDF tool has this. |
| **Split PDF** | Extracting pages, separating documents | LOW | By range, by page, extract specific pages |
| **Compress PDF** | Reducing file sizes for email/ sharing | MEDIUM | Quality presets (low/medium/high), image optimization |
| **Rotate PDF** | Fixing scanned documents in wrong orientation | LOW | Single pages or entire document |
| **Password Protect** | Securing sensitive documents | MEDIUM | Set open password + permissions (print, copy, edit) |
| **Remove Password** | Unlocking protected PDFs | LOW | Remove restrictions when you have the password |
| **Add Watermark** | Branding, draft stamps, confidential markers | LOW | Text or image watermark with positioning |
| **PDF to Images** | Converting pages to PNG/JPG/WebP | LOW | Single page or all pages, quality options |
| **Images to PDF** | Creating PDFs from photos/scans | LOW | Multiple images, page sizing options |
| **Delete/Reorder Pages** | Basic document organization | LOW | Visual page sorter expected |
| **Add Page Numbers** | Professional document formatting | LOW | Position, font, format options |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valued — especially for privacy-focused positioning.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Zero-Trace Processing** | Core differentiator for NoTracePDF — files exist only in memory, deleted after download | MEDIUM | Requires careful architecture (tmpfs, in-memory streams) |
| **Self-Hosted Deployment** | Users control their own server/NAS/VPS — no cloud dependency | LOW | Docker-first, simple deployment |
| **No User Accounts** | No tracking, no session management, no data collection | LOW | Simplifies architecture, aligns with privacy mission |
| **Client-Side Fallback** | Browser-based processing for small files (<20MB) — zero server involvement | HIGH | Uses pdf-lib.js, PDF.js — ultimate privacy for small files |
| **Dark Mode + Responsive UI** | Modern UX expectations | MEDIUM | Mobile-first design expected in 2026 |
| **PDF Preview** | See pages before processing | MEDIUM | Uses PDF.js for rendering |
| **Batch Processing (ZIP)** | Process multiple files at once | MEDIUM | Upload ZIP → process all → return ZIP |
| **Flatten Annotations** | Lock comments/highlights into content | LOW | Professional document finalization |
| **Remove Metadata** | Strip author, timestamps, hidden data | LOW | Privacy-critical feature |
| **Compare PDFs** | Side-by-side diff highlighting | MEDIUM | Version comparison for legal/professional use |
| **PDF ↔ Office Conversion** | Word/Excel/PPT ↔ PDF | HIGH | Requires LibreOffice headless |
| **HTML/URL → PDF** | Web page to PDF | MEDIUM | Common request, useful for archiving |
| **OCR** | Make scanned PDFs searchable | HIGH | Tesseract integration |
| **Crop/Scale Pages** | Precise page sizing | LOW | Print preparation |
| **Redact PDF** | Permanently black out sensitive text | MEDIUM | Critical for legal/privacy use cases |
| **PDF/A Conversion** | Long-term archival format | MEDIUM | ISO-standardized for preservation |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for privacy-focused tools.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **User Accounts / "My Documents"** | Users want to save files for later | Violates core value of zero-trace; creates liability | Make this explicitly NOT available; document ephemeral nature clearly |
| **Shareable Links with Expiration** | Convenience for collaboration | Creates persistent storage; requires tracking | Users must download and share via their own means |
| **E-Signing with Server Storage** | Digital signature workflows | Requires document persistence for multi-party signing | Support self-contained signing (draw signature, embed) but no workflow storage |
| **Analytics / Telemetry** | Understanding usage patterns | Violates privacy promise | Use anonymous error logs only (no filenames, IPs, timestamps) |
| **Cloud Sync / Backup** | "My files follow me" | Creates data persistence | Self-hosted means user controls their own backup if desired |
| **Collaborative Editing** | Real-time document collaboration | Requires session management, persistence | Outside scope for single-user PDF manipulation |
| **AI Features (Translation, Summarization)** | Modern convenience | Requires sending content to external services | Could offer local-only AI in future if fully self-contained |

---

## Feature Dependencies

```
PDF Preview
    └──requires──> PDF.js integration (rendering engine)

Client-Side Fallback
    └──requires──> pdf-lib.js (for merge/split/rotate)
    └──requires──> PDF.js (for preview)

OCR
    └──requires──> Tesseract OCR engine
    └──requires──> Language packs installation

PDF ↔ Office Conversion
    └──requires──> LibreOffice headless mode
    └──enhances──> Batch processing (for multiple conversions)

Batch Processing
    └──requires──> ZIP file handling
    └──enhances──> All other tools (apply to multiple files)

Compare PDF
    └──requires──> PDF rendering (visual diff)
    └──requires──> Text extraction (text diff)

Redact PDF
    └──requires──> Text extraction
    └──requires──> Coordinate mapping

Dark Mode
    └──conflicts──> Nothing (purely CSS)

User Accounts
    └──conflicts──> Zero-Trace Architecture (fundamentally incompatible)
```

### Dependency Notes

- **Client-Side Fallback requires pdf-lib.js + PDF.js:** These are browser-based libraries. pdf-lib handles manipulation (merge, split, rotate, watermark), PDF.js handles preview. Both are essential for true client-side processing.
- **OCR requires Tesseract + Language Packs:** This is server-side only. Language packs add ~50-200MB per language. Consider offering only English by default.
- **PDF ↔ Office Conversion requires LibreOffice headless:** This adds significant container size (~500MB+). Consider offering as a separate "full" Docker image variant.
- **Batch Processing enhances all tools:** Once ZIP handling exists, it applies to every operation. High leverage feature.
- **User Accounts conflicts with Zero-Trace Architecture:** This is a hard constraint. Any persistence breaks the core value proposition. Do not reconsider.

---

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **Merge PDF** — Most common operation, establishes trust
- [x] **Split PDF** — Core operation, simple implementation
- [x] **Rotate PDF** — Trivial implementation, completes basic operations
- [x] **Compress PDF** — High value, moderate complexity
- [x] **Password Protect** — Security feature, expected
- [x] **Remove Password** — Complementary to protect
- [x] **Add Watermark** — Branding feature, simple implementation
- [x] **Extract Text/Images/Pages** — Extraction operations
- [x] **PDF ↔ Images** — Bidirectional conversion
- [x] **Images → PDF** — Creating PDFs from images
- [x] **Zero-Trace Architecture** — Core differentiator, non-negotiable
- [x] **Self-Hosted Docker** — Deployment method, expected
- [x] **Clean, Simple UI** — Professional appearance required for trust

**Total MVP Features: 13 tools + architecture + UI**

### Add After Validation (v1.x)

Features to add once core is working and validated.

- [ ] **Crop/Scale Pages** — Print preparation, low complexity
- [ ] **Add Page Numbers** — Professional formatting, low complexity
- [ ] **Flatten Annotations** — Document finalization, low complexity
- [ ] **Remove Metadata** — Privacy feature, low complexity
- [ ] **Compare PDFs** — Version comparison, moderate complexity
- [ ] **PDF ↔ Office** — LibreOffice integration, high complexity
- [ ] **HTML/URL → PDF** — Web archiving, moderate complexity
- [ ] **Redact PDF** — Privacy-critical, moderate complexity

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **OCR** — Requires Tesseract + language packs, significant complexity
- [ ] **Batch Processing (ZIP)** — High leverage but requires ZIP handling
- [ ] **Client-Side Fallback** — Ultimate privacy, requires significant frontend work
- [ ] **PDF Preview** — Nice to have, requires PDF.js integration
- [ ] **Dark Mode** — UX polish, not essential for MVP
- [ ] **PDF/A Conversion** — Niche archival use case

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Merge PDF | HIGH | LOW | P1 |
| Split PDF | HIGH | LOW | P1 |
| Rotate PDF | HIGH | LOW | P1 |
| Compress PDF | HIGH | MEDIUM | P1 |
| Password Protect | HIGH | MEDIUM | P1 |
| Remove Password | MEDIUM | LOW | P1 |
| Add Watermark | MEDIUM | LOW | P1 |
| PDF ↔ Images | HIGH | LOW | P1 |
| Images → PDF | HIGH | LOW | P1 |
| Extract Text/Images | MEDIUM | LOW | P1 |
| Zero-Trace Architecture | HIGH | MEDIUM | P1 |
| Crop/Scale Pages | MEDIUM | LOW | P2 |
| Add Page Numbers | MEDIUM | LOW | P2 |
| Flatten Annotations | LOW | LOW | P2 |
| Remove Metadata | MEDIUM | LOW | P2 |
| Compare PDFs | MEDIUM | MEDIUM | P2 |
| Redact PDF | MEDIUM | MEDIUM | P2 |
| PDF ↔ Office | HIGH | HIGH | P2 |
| HTML → PDF | MEDIUM | MEDIUM | P2 |
| OCR | MEDIUM | HIGH | P3 |
| Batch Processing | HIGH | MEDIUM | P3 |
| Client-Side Fallback | HIGH | HIGH | P3 |
| PDF Preview | MEDIUM | MEDIUM | P3 |
| Dark Mode | LOW | MEDIUM | P3 |

**Priority key:**
- **P1:** Must have for launch (MVP)
- **P2:** Should have, add when possible (Tier 1)
- **P3:** Nice to have, future consideration (Tier 2)

---

## Competitor Feature Analysis

| Feature | iLovePDF | PDF24 | Stirling-PDF | NoTracePDF Approach |
|---------|----------|-------|--------------|---------------------|
| Merge/Split/Rotate | ✅ | ✅ | ✅ | ✅ Table stakes |
| Compress | ✅ | ✅ | ✅ | ✅ Quality presets |
| Password Protect | ✅ | ✅ | ✅ | ✅ Standard |
| Watermark | ✅ | ✅ | ✅ | ✅ Text + image |
| PDF ↔ Images | ✅ | ✅ | ✅ | ✅ PNG/JPG/WebP |
| PDF ↔ Office | ✅ | ❌ | ✅ | ✅ Tier 1 |
| OCR | ✅ Premium | ✅ | ✅ | ✅ Tier 2 |
| Compare | ✅ | ✅ | ✅ | ✅ Tier 1 |
| Redact | ✅ | ✅ | ✅ | ✅ Tier 1 |
| Client-Side Processing | ❌ | ❌ | Partial | ✅ Tier 2 — Full fallback |
| Self-Hosted | ❌ | Partial (desktop) | ✅ | ✅ Core feature |
| User Accounts | ✅ | ❌ | Optional | ❌ Explicitly NO |
| Data Retention | Cloud storage | None | Configurable | ❌ Zero by design |
| Privacy Focus | Certifications | German privacy | Privacy-first | ✅ Zero-trace = core value |
| Open Source | ❌ | ✅ | ✅ | ✅ MIT/AGPL |
| Tool Count | ~25 | ~30 | 50+ | ~20 (focused) |

### Key Competitive Insights

1. **Stirling-PDF is the main open-source competitor** — 74k+ GitHub stars, 50+ tools, active development. They have enterprise features (SSO, user management) that we explicitly avoid.

2. **Client-side processing is rare** — PurePDF, HonestPDF, LocalPDF, and ExactPDF offer browser-only processing. This is a strong differentiator but limited to small files.

3. **Zero-trace positioning is unique** — No competitor explicitly guarantees "files exist only in memory, deleted immediately after download." This is our strongest marketing position.

4. **PDF24 is closest to "no tracking"** — German company, strong privacy stance, but requires desktop install for full features. Online version uploads to their servers.

5. **Tool bloat is real** — Stirling-PDF has 50+ tools. Users don't need 50 tools. Focus on 20 core tools done well.

---

## Sources

- **iLovePDF** — https://www.ilovepdf.com/ (official, accessed 2026-02-19)
- **PDF24 Tools** — https://www.pdf24.org/ (official, accessed 2026-02-19)
- **Stirling-PDF** — https://github.com/Stirling-Tools/Stirling-PDF (74.3k stars, official docs)
- **PurePDF** — https://purepdf.app/ (client-side processing)
- **HonestPDF** — https://gethonestpdf.com/ (client-side processing)
- **LocalPDF** — https://localpdf.online/ (client-side processing)
- **ApexPDF** — https://www.apexpdf.com/ (100+ client-side tools)
- **EveryTask PDF Comparison** — https://everytask.io/blog/best-free-pdf-tools-online-2026
- **PDFEliteTools Comparison** — https://pdfelitetools.com/blog/best-free-pdf-tools-2026

---

*Feature research for: Privacy-focused, self-hosted PDF processing tools*
*Researched: 2026-02-19*
