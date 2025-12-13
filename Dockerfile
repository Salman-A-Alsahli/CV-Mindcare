# Dockerfile for CV-Mindcare
# Multi-stage build for optimized production image

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .[ml]

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libsndfile1 \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY backend/ /app/backend/
COPY launcher/ /app/launcher/
COPY config/ /app/config/

# Create directory for database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/app/data/cv_mindcare.db \
    LOG_LEVEL=INFO

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Create non-root user
RUN useradd -m -u 1000 cvmindcare && \
    chown -R cvmindcare:cvmindcare /app
USER cvmindcare

# Default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
