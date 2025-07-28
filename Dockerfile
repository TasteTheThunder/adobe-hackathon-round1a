# Multi-stage build for minimal image size
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    g++ \
    make \
    musl-dev \
    linux-headers \
    freetype-dev \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    gzip

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.10-alpine

# Install only runtime dependencies (minimal)
RUN apk add --no-cache \
    freetype \
    jpeg \
    zlib \
    libstdc++ \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Create non-root user first
RUN addgroup -g 1001 -S appgroup && \
    adduser -S -D -G appgroup -u 1001 appuser

# Copy installed packages from builder stage to user directory
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy application code (only necessary files)
COPY --chown=appuser:appgroup app.py .
COPY --chown=appuser:appgroup input/ ./input/
COPY --chown=appuser:appgroup output/ ./output/

# Switch to non-root user
USER appuser

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

# Command to run the app
CMD ["python", "app.py"]
