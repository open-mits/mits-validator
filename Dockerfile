# Multi-stage build for production-ready MITS Validator
# Stage 1: Builder
FROM python:3.12-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim as runtime

# Set labels for metadata
LABEL org.opencontainers.image.title="MITS Validator"
LABEL org.opencontainers.image.description="Production-ready MITS XML validation service"
LABEL org.opencontainers.image.url="https://github.com/open-mits/mits-validator"
LABEL org.opencontainers.image.source="https://github.com/open-mits/mits-validator"
LABEL org.opencontainers.image.license="Apache-2.0"
LABEL org.opencontainers.image.vendor="Open MITS"

# Create non-root user for security
RUN groupadd --gid 1000 mits && \
    useradd --uid 1000 --gid mits --shell /bin/bash --create-home mits

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mits:mits src/ ./src/
COPY --chown=mits:mits rules/ ./rules/
COPY --chown=mits:mits schemas/ ./schemas/

# Create directories for runtime data
RUN mkdir -p /app/data /app/logs && \
    chown -R mits:mits /app

# Switch to non-root user
USER mits

# Set environment variables with secure defaults
ENV PORT=8000
ENV MAX_UPLOAD_BYTES=10485760
ENV REQUEST_TIMEOUT=30
ENV ALLOWED_CONTENT_TYPES="application/xml,text/xml,application/octet-stream"
ENV DEFAULT_PROFILE="default"
ENV LOG_LEVEL="INFO"
ENV CORS_ORIGINS="*"
ENV CORS_METHODS="GET,POST,OPTIONS"
ENV CORS_HEADERS="*"
ENV UMASK=022

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start command with production settings
CMD ["uvicorn", "src.mits_validator.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
