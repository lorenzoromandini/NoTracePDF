# Pitfalls Research

**Domain:** Privacy-focused PDF processing, ephemeral file handling, self-hosted web applications
**Researched:** 2026-02-19
**Confidence:** HIGH

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

---

### Pitfall 1: PDF Library Path Traversal Vulnerabilities

**What goes wrong:**
PDF libraries often accept file paths as input for operations like `addImage()`, `loadFile()`, or `addFont()`. Without proper validation, attackers can pass paths like `../../etc/passwd` to read arbitrary files from the server, which then get embedded into generated PDFs for exfiltration.

**Why it happens:**
- Developers assume library methods only accept "safe" paths
- Path validation is often an afterthought
- The Node.js builds of some libraries have different security profiles than browser builds

**How to avoid:**
- Never pass user-controlled paths to PDF library methods
- If file paths must be used, implement strict validation (no `..`, whitelist allowed directories)
- Prefer processing files from memory/buffers rather than filesystem paths
- Keep PDF libraries updated — jsPDF < 4.0.0 is vulnerable (CVE-2025-68428)

**Warning signs:**
- User input directly used as file path argument to PDF methods
- No path sanitization before file operations
- Library version older than latest stable

**Phase to address:**
Phase 1 (Core Processing) — Security foundation must be established before any PDF operations

---

### Pitfall 2: Memory Exhaustion via Malicious PDFs

**What goes wrong:**
Maliciously crafted PDFs can use compression bombs (LZWDecode, FlateDecode) or nested structures to exhaust server memory, causing denial of service. A small PDF file (few KB) can decompress to gigabytes in memory.

**Why it happens:**
- PDF compression streams can have unbounded decompression ratios
- Libraries process entire files into memory before validation
- Size checks are often done on compressed size, not decompressed size

**How to avoid:**
- Set strict memory limits on processing containers (Docker `--memory`)
- Implement file size limits AND decompressed size limits
- Use streaming processing where possible instead of loading entire file
- Known vulnerable: FPDI (CVE-2025-54869), pypdf < 6.1.3 (CVE-2025-62708), Apache PDFBox < 2.0.24 (CVE-2021-31811)

**Warning signs:**
- No memory limits on processing containers
- Processing happens entirely in memory
- No timeout on PDF operations
- Large files cause server to become unresponsive

**Phase to address:**
Phase 1 (Core Processing) — Must implement resource constraints before processing any user files

---

### Pitfall 3: Temporary File Leakage

**What goes wrong:**
Applications create temporary files for processing but fail to clean them up. Files persist in `/tmp` or similar directories, exposing user data to:
- Other processes on the same system
- Disk forensics
- Backup systems that capture `/tmp`

**Why it happens:**
- Cleanup code skipped when exceptions occur
- Process killed before cleanup runs
- Developer assumes OS will clean `/tmp` (not immediate)
- Hardcoded predictable filenames allow race conditions

**How to avoid:**
- **Best approach:** Process entirely in memory — never write to disk
- If disk is required: Use `fs.mkdtemp()` with random names, not hardcoded paths
- Register cleanup handlers for all exit paths (success, error, SIGTERM, SIGINT)
- Use `try/finally` patterns to ensure cleanup
- Consider a RAM-based tmpfs for any required temporary storage

**Warning signs:**
- Files appearing in `/tmp` after processing
- No cleanup code in error handlers
- Predictable temp file names
- No process signal handlers

**Phase to address:**
Phase 1 (Core Processing) — Zero-persistence requirement must be architected from the start

---

### Pitfall 4: Browser Caching of Sensitive Downloads

**What goes wrong:**
Generated PDFs and uploaded files are cached by browsers, remaining on user devices long after download. This violates the "zero trace" promise and exposes sensitive data.

**Why it happens:**
- Default HTTP caching behavior allows caching
- Missing or incorrect `Cache-Control` headers
- CDN/proxy caching in between

**How to avoid:**
Always set these headers on file downloads:
```
Cache-Control: no-store, no-cache, must-revalidate, private
Pragma: no-cache
Expires: 0
X-Content-Type-Options: nosniff
```

**Warning signs:**
- No explicit cache headers on download responses
- Files visible in browser cache (chrome://settings/clearBrowserData)
- CDN/proxy between server and client without cache bypass

**Phase to address:**
Phase 1 (Core Processing) — HTTP headers must be correct from the first deployment

---

### Pitfall 5: Docker Volume Persistence

**What goes wrong:**
Docker containers accidentally persist data through volumes or bind mounts. Even when the container is removed, data remains on the host filesystem — completely violating zero-promise.

**Why it happens:**
- Using `VOLUME` instruction in Dockerfile
- Bind mounts to host directories
- Named volumes that survive container lifecycle
- Database containers with persistent storage

**How to avoid:**
- Do NOT use `VOLUME` in Dockerfile
- Do NOT define `volumes:` in docker-compose.yml for this service
- Use `tmpfs` mounts for any required temporary storage: `--mount type=tmpfs,destination=/tmp`
- Verify with: `docker inspect <container> | grep -A 10 Mounts`

**Warning signs:**
- `docker volume ls` shows volumes for this service
- Data survives container restart/recreate
- Dockerfile contains `VOLUME` instruction

**Phase to address:**
Phase 1 (Core Processing) — Docker configuration is fundamental to the privacy guarantee

---

### Pitfall 6: Logging User Data

**What goes wrong:**
Request logs, error logs, and debugging output inadvertently capture user file contents, filenames, or metadata. This creates a persistent record of user activity.

**Why it happens:**
- Framework defaults log request bodies
- Error stack traces include file contents
- Debug mode logs everything
- Third-party logging libraries capture context automatically

**How to avoid:**
- Never log file contents or user-provided data
- Configure logging levels to exclude request bodies
- Use structured logging with explicit field selection
- Implement log sanitization for any user input
- Disable or carefully configure OpenTelemetry/observability tools

**Warning signs:**
- Log files contain file names, sizes, or content snippets
- Error messages include user data
- Third-party telemetry capturing request payloads

**Phase to address:**
Phase 1 (Core Processing) — Logging configuration must be established before any processing

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Store files to disk temporarily | Simpler processing code | Data persists, cleanup complexity | Never for privacy-focused app |
| Log full request for debugging | Faster debugging | User data in logs | Never |
| Skip file type validation | Faster uploads | Malicious file uploads | Never |
| Use single processing queue | Simpler architecture | Memory exhaustion from concurrent large files | Only with strict limits |
| Skip container resource limits | Faster processing | DoS vulnerability | Never |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| LibreOffice headless | Running without sandboxing, no resource limits | Use dedicated container with memory/CPU limits, read-only filesystem |
| ImageMagick | Processing untrusted files without policy.xml | Define strict resource limits in policy.xml, sandbox execution |
| PDF libraries | Passing user paths to `loadFile()` methods | Load from buffers, never from user-provided paths |
| Cloud storage | Using as temporary processing storage | Process in memory, never persist to external storage |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| In-memory PDF processing without limits | OOM kills, crashes | Set container memory limits, implement request timeouts | Single large file |
| Concurrent processing unlimited | Server becomes unresponsive | Limit concurrent operations, queue with size limits | ~10 concurrent large files |
| No request timeout | Hanging connections | Set HTTP and processing timeouts (30s recommended) | Malformed PDF that loops forever |
| Sync processing in web handler | Slow responses, timeouts | Use async processing with status polling | Files > 10MB |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Path traversal in PDF libraries | Arbitrary file read | Never use user paths, load from buffers only |
| Compression bomb (PDF bomb) | DoS via memory exhaustion | Limit decompressed size, set memory limits |
| LibreOffice arbitrary file write (CVE-2024-12425) | Remote code execution | Update LibreOffice, use read-only container filesystem |
| MIME type spoofing | Malicious file execution | Validate actual file content, not just extension |
| PDF JavaScript execution | XSS in PDF viewers | Strip JavaScript from PDFs, disable actions |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress indication during processing | User thinks app is frozen | Show processing animation, estimated time |
| No file size limit warning | Upload fails silently | Show limits upfront, validate client-side |
| Generic error messages | User doesn't understand what went wrong | Specific errors (file too large, corrupt PDF, unsupported format) |
| No confirmation before download | User loses track of file | Clear download flow, auto-generated safe filenames |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Zero persistence:** Often missing actual verification — verify no files in `/tmp`, no Docker volumes, no logs with data
- [ ] **Cache headers:** Often missing on download routes — verify with `curl -I` shows correct headers
- [ ] **Memory limits:** Often not enforced — verify container OOM kills on memory exhaustion
- [ ] **Cleanup on error:** Often skips cleanup — test with intentional failures, verify files removed
- [ ] **Signal handling:** Often missing SIGTERM/SIGINT handlers — test `docker stop`, verify cleanup
- [ ] **Library vulnerabilities:** Often outdated versions — run `npm audit`, check CVE databases

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Data logged accidentally | HIGH | Rotate logs, purge log storage, audit for exposure |
| Files persisted to disk | MEDIUM | Identify files, secure delete, audit access |
| Docker volume created | LOW | `docker volume rm`, verify no data remains |
| Memory exhaustion event | LOW | Container restarts automatically, add limits |
| Cache headers missing | LOW | Deploy fix, users must clear browser cache |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| PDF library vulnerabilities | Phase 1 (Core) | Run `npm audit`, test with malformed PDFs |
| Memory exhaustion | Phase 1 (Core) | Test with compression bombs, verify OOM kills container |
| Temporary file leakage | Phase 1 (Core) | Process files, verify `/tmp` empty, test error paths |
| Browser caching | Phase 1 (Core) | `curl -I` on download endpoint, verify headers |
| Docker volume persistence | Phase 1 (Core) | `docker volume ls`, `docker inspect` for mounts |
| Logging user data | Phase 1 (Core) | Process files, grep logs for content, verify empty |
| LibreOffice vulnerabilities | Phase 2 (Conversion) | Check LibreOffice version, test with malicious docs |
| UX feedback issues | Phase 3 (Polish) | User testing, measure time-to-feedback |

---

## Sources

- CVE-2025-68428: jsPDF Path Traversal — https://github.com/parallax/jsPDF/security/advisories/GHSA-cxh5-xvwc-h4q9
- CVE-2025-54869: FPDI Memory Exhaustion — https://github.com/Setasign/FPDI/security/advisories/GHSA-jxhh-4648-vpp3
- CVE-2025-62708: pypdf LZWDecode RAM Exhaustion — https://github.com/py-pdf/pypdf/security/advisories/GHSA-jfx9-29x2-rv3j
- CVE-2024-12425/12426: LibreOffice File Write/Read — https://codeanlabs.com/2025/02/exploiting-libreoffice-cve-2024-12425-and-cve-2024-12426/
- OWASP Testing Guide: Browser Cache Weaknesses — https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses
- CWE-525: Browser Cache with Sensitive Info — https://cwe.mitre.org/data/definitions/525.html
- Docker Resource Constraints — https://docs.docker.com/engine/containers/resource_constraints/
- Docker Volumes Documentation — https://docs.docker.com/engine/storage/volumes
- OWASP Top 10 2025: Security Logging Failures — https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/
- OpenTelemetry Sensitive Data Handling — https://opentelemetry.io/docs/security/handling-sensitive-data
- OWASP Insecure Temporary File — https://owasp.org/www-community/vulnerabilities/Insecure_Temporary_File
- OpenStack Secure Tempfile Guidelines — https://security.openstack.org/guidelines/dg_using-temporary-files-securely.html

---
*Pitfalls research for: Privacy-focused PDF processing, ephemeral file handling, self-hosted web applications*
*Researched: 2026-02-19*
