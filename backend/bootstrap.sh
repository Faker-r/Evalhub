#!/usr/bin/env bash
set -e

poetry lock
poetry install
poetry run python scripts/setup_lighteval.py
