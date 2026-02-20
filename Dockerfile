# NoTracePDF Dockerfile
# Self-hosted, zero-trace PDF processing toolkit
#
# Key privacy features:
# - NO VOLUME instruction (zero persistent storage)
# - Runs as non-root user
# - Debian slim for better pre-built wheel support

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# - poppler-utils: PDF to image conversion
# - libqpdf-dev: pikepdf dependency
# - LibreOffice: Office document conversions
# - Pango/GDK: WeasyPrint dependencies for HTML to PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    poppler-utils \
    libqpdf-dev \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libreoffice-impress-nogui \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --group appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create upload directory (will be tmpfs-mounted at runtime)
RUN mkdir -p /app/uploads && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn + uvicorn workers
# Timeout increased to 120s for Office conversions
ENTRYPOINT ["gunicorn", "app.main:app", \
    "-w", "2", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "-b", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--graceful-timeout", "30", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
