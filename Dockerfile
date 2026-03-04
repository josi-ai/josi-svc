# Production Dockerfile for Josi API - Google Cloud Optimized
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    git \
    curl \
    # Swiss Ephemeris dependencies
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Create directory for Swiss Ephemeris data
RUN mkdir -p /usr/share/swisseph

# Install Poetry
RUN pip install poetry==1.7.1

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (including dev for CI testing)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY alembic.ini pytest.ini ./

# Copy and set up alembic
COPY src/alembic ./src/alembic/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=8000

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Expose port (Google Cloud Run uses PORT env var)
EXPOSE 8000

# Run the application with dynamic port binding for Cloud Run
CMD exec uvicorn josi.main:app --host 0.0.0.0 --port ${PORT:-8000}