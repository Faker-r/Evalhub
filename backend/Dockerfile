# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ARG VERSION=unknown

LABEL org.opencontainers.image.title="Evalhub Backend"
LABEL org.opencontainers.image.description="Evalhub FastAPI backend service"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="https://github.com/Faker-r/Evalhub"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-root --only main

COPY . .

RUN git clone https://github.com/pjavanrood/lighteval.git /opt/lighteval && \
    pip install --no-build-isolation -e "/opt/lighteval[extended_tasks]" && \
    pip install "setuptools<82"

RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /opt/lighteval && \
    git config --system --add safe.directory /opt/lighteval

USER appuser

RUN git config --global --add safe.directory /opt/lighteval

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

EXPOSE 8000

STOPSIGNAL SIGTERM

CMD ["python", "-m", "api"]
