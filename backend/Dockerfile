# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Copy application code
COPY . .

# Install all dependencies (--no-root skips installing the project itself)
RUN poetry install --no-interaction --no-root

# Install lighteval into system Python (cloned outside /app to avoid volume mount conflict)
RUN git clone https://github.com/pjavanrood/lighteval.git /opt/lighteval && \
    pip install --no-build-isolation -e "/opt/lighteval[extended_tasks]" && \
    pip install "setuptools<82"

# Create a non-root user for security and set git safe directory for all users
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /opt/lighteval && \
    git config --system --add safe.directory /opt/lighteval

USER appuser

# Also set for appuser's global config
RUN git config --global --add safe.directory /opt/lighteval

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "api"]
