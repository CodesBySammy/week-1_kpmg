# Multi-Stage Production Dockerfile for Case Management Platform
# Supports both Week 1 FastAPI backend and Week 2 Data Pipeline execution

FROM python:3.11-slim as base

# Set environment variables for Python runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (build essentials, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project specification files first for Docker layer caching
COPY pyproject.toml .
COPY .env.example .env

# Install dependencies including pipeline and RAG packages
RUN pip install --upgrade pip && \
    pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "sqlalchemy>=2.0.0" \
    "pydantic>=2.0.0" "pydantic-settings>=2.0.0" "python-dotenv>=1.0.0" \
    "python-json-logger>=2.0.0" "pandas>=2.2.0" "pyarrow>=15.0.0" \
    "requests>=2.31.0" "pytest>=8.0.0" "pytest-cov>=5.0.0" "httpx>=0.27.0" \
    "rank-bm25>=0.2.2" "pypdf>=5.0.0" "pyyaml>=6.0.0"

# Copy source code and artifacts
COPY app/ ./app/
COPY pipeline/ ./pipeline/
COPY rag/ ./rag/
COPY sql/ ./sql/
COPY data/ ./data/

# Install the editable project packages
RUN pip install -e .

# Create non-root operational user for enterprise container security
RUN useradd -m -u 1000 appuser && \
    mkdir -p data/raw data/standardized data/curated data/rejected reports audit && \
    chown -R appuser:appuser /app
USER appuser

# Expose FastAPI backend port
EXPOSE 8000

# Default entrypoint runs the Week 2 Data Pipeline CLI
# Can be overridden:
# - Run backend: docker run -p 8000:8000 <image> uvicorn app.main:app --host 0.0.0.0 --port 8000
# - Run pipeline: docker run <image> python -m pipeline.cli --mode full
# - Run RAG assistant: docker run <image> python -m rag.cli query "What is the password policy?"
# - Run RAG evaluation: docker run <image> python -m rag.cli evaluate
CMD ["python", "-m", "pipeline.cli", "--mode", "full"]
