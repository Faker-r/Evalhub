#!/usr/bin/env bash
set -e

poetry lock
poetry install --no-root
poetry run python scripts/setup_lighteval.py
