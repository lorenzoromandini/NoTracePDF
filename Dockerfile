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
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    poppler-utils \
    libqpdf-dev \
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
# Timeout: 30s to prevent slow upload DoS
# Graceful timeout: 10s for clean shutdown
ENTRYPOINT ["gunicorn", "app.main:app", \
    "-w", "2", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "-b", "0.0.0.0:8000", \
    "--timeout", "30", \
    "--graceful-timeout", "10", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
