# Codacy Integration Design Spec

**Date:** 2026-03-23
**Status:** Approved
**Scope:** Backend (Python) only

## Overview

Integrate Codacy into the Evalhub repository to automatically review Python backend code for standards compliance, security vulnerabilities, and code quality issues. Codacy will analyze PRs and commits via their GitHub App, providing feedback as PR comments without blocking merges.

## Goals

- Provide early feedback on code quality during development
- Identify security vulnerabilities before they reach production
- Maintain consistent code standards across the backend codebase
- Non-blocking integration that reports issues without preventing merges

## Approach

**Codacy GitHub App Integration** — Install the Codacy GitHub App which automatically analyzes PRs and commits without modifying the existing CI workflow.

### Why This Approach

- Zero CI configuration needed — Codacy handles analysis on their infrastructure
- Automatic PR comments with inline annotations
- Doesn't add to CI build time
- Simple setup and maintenance

## Components

### 1. Codacy Account & Repository Setup (Manual)

- Create Codacy organization at https://app.codacy.com
- Connect GitHub account via OAuth
- Authorize the Evalhub repository
- Install Codacy GitHub App on the repository

### 2. Codacy Configuration File

Add `.codacy.yml` to repository root with:

- Analysis scope limited to `backend/` directory
- Exclusions for virtual environments, test fixtures, generated files
- Python-specific tools enabled: Pylint, Bandit (security), Prospector, Ruff

### 3. Quality Settings (Configured in Codacy Dashboard)

- Mode: Report only (no PR blocking)
- Issue categories: All enabled (security, code patterns, duplication, complexity)
- Languages: Python

## File Changes

| File | Purpose |
|------|---------|
| `.codacy.yml` | Analysis configuration — scope, excluded paths, enabled tools |

## Configuration Details

### Complete `.codacy.yml` Configuration

```yaml
---
engines:
  pylint:
    enabled: true
  bandit:
    enabled: true
  ruff:
    enabled: true

exclude_paths:
  - "frontend/**"
  - "backend/.venv/**"
  - "backend/venv/**"
  - "backend/lighteval/**"
  - "backend/**/__pycache__/**"
  - "backend/alembic/versions/**"
  - "backend/alembic/env.py"
  - "**/*.pyc"
  - "**/node_modules/**"
```

### Excluded Paths

| Path | Rationale |
|------|-----------|
| `frontend/**` | Out of scope (frontend integration planned separately) |
| `backend/.venv/**`, `backend/venv/**` | Virtual environment dependencies (third-party code) |
| `backend/lighteval/**` | Vendored/external library |
| `backend/**/__pycache__/**` | Python bytecode cache |
| `backend/alembic/versions/**` | Auto-generated Alembic migration files |
| `backend/alembic/env.py` | Boilerplate Alembic configuration |

### Enabled Tools

| Tool | Purpose |
|------|---------|
| Pylint | Code quality, style, error detection |
| Bandit | Security vulnerability scanning |
| Ruff | Fast Python linter (complements existing black/isort) |

**Note:** Prospector was removed to avoid duplicate findings since it runs Pylint internally. Ruff is configured to complement (not duplicate) the existing pre-commit hooks which handle formatting via black/isort.

## Implementation Notes

- Changes will be made on a new branch: `feat/codacy-integration`
- Subagents will be used for parallel implementation tasks
- Manual setup steps (account creation, GitHub App installation) will be documented in a separate guide

## Future Enhancements (Out of Scope)

- Frontend (TypeScript/React) integration — planned as follow-up
- Coverage report upload to Codacy
- Stricter quality gates (blocking PRs on issues)

## Pre-commit Hook Compatibility

The existing pre-commit configuration runs:
- **black** — Code formatting
- **isort** — Import sorting
- **autoflake** — Unused import removal

Codacy's analysis complements these tools:
- Codacy runs on PRs (remote), pre-commit runs locally
- Codacy adds security scanning (Bandit) and deeper code quality analysis (Pylint)
- Ruff in Codacy focuses on error detection, not formatting (which black handles)

No rule conflicts expected since formatting is handled locally via pre-commit.

## Verification

To verify the integration is working:
1. Create a test PR with an intentional security issue (e.g., hardcoded password)
2. Confirm Codacy comments appear on the PR within 5 minutes
3. Verify findings are categorized correctly (security vs code quality)

## Initial Baseline

On first scan, Codacy may flag existing issues in the codebase. The approach:
- Accept initial findings as informational
- Address critical/security issues promptly
- Use Codacy's "ignore" feature for false positives
- No immediate cleanup sprint required

## Success Criteria

1. `.codacy.yml` configuration file committed to repository
2. Codacy GitHub App installed and analyzing PRs
3. PR comments showing code quality and security findings
4. No impact on existing CI workflow or build times
