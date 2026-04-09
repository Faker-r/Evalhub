# Codacy Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Codacy GitHub App to automatically review Python backend code for quality and security issues on PRs.

**Architecture:** Add a `.codacy.yml` configuration file to the repository root that tells Codacy which files to analyze, which to exclude, and which analysis tools to enable. The GitHub App handles all analysis — no CI workflow changes needed.

**Tech Stack:** Codacy, GitHub App, Python linting tools (Pylint, Bandit, Ruff)

**Spec:** [docs/superpowers/specs/2026-03-23-codacy-integration-design.md](../specs/2026-03-23-codacy-integration-design.md)

**Branch:** `feat/codacy-integration`

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `.codacy.yml` | Create | Codacy analysis configuration |
| `docs/codacy-setup.md` | Create | Manual setup instructions for GitHub App |

---

## Task 1: Create Feature Branch

**Files:** None (git operation only)

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b feat/codacy-integration
```

Expected: Switched to new branch 'feat/codacy-integration'

---

## Task 2: Create Codacy Configuration File

**Files:**
- Create: `.codacy.yml`

- [ ] **Step 1: Create `.codacy.yml` with analysis configuration**

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

- [ ] **Step 2: Verify YAML syntax is valid**

Run: `python -c "import yaml; yaml.safe_load(open('.codacy.yml'))"`

Expected: No output (valid YAML)

- [ ] **Step 3: Commit the configuration file**

```bash
git add .codacy.yml
git commit -m "feat: add Codacy configuration for Python backend analysis

Enables Pylint, Bandit (security), and Ruff for code quality checks.
Excludes virtual envs, lighteval, and generated files."
```

---

## Task 3: Create Setup Documentation

**Files:**
- Create: `docs/codacy-setup.md`

- [ ] **Step 1: Create setup guide for manual Codacy configuration**

```markdown
# Codacy Setup Guide

This guide covers the manual steps to complete Codacy integration.

## Prerequisites

- GitHub account with admin access to the repository
- Codacy account (free tier available)

## Setup Steps

### 1. Create Codacy Account

1. Go to [https://app.codacy.com](https://app.codacy.com)
2. Click "Sign up" and select "Sign up with GitHub"
3. Authorize Codacy to access your GitHub account

### 2. Add Repository to Codacy

1. In Codacy dashboard, click "Add repository"
2. Select the Evalhub repository from the list
3. Click "Add" to start the initial analysis

### 3. Configure Quality Settings

1. Go to Repository Settings > Quality Settings
2. Set "Issues are new if" to "Not found in default branch"
3. Under "Quality gates", ensure all gates are set to "Not blocking"

### 4. Verify Integration

1. Create a test PR with a minor change
2. Wait 2-5 minutes for Codacy analysis
3. Verify Codacy comments appear on the PR

## Configuration

The repository includes a `.codacy.yml` file that configures:

- **Enabled tools:** Pylint, Bandit (security), Ruff
- **Excluded paths:** Virtual environments, generated files, frontend code
- **Scope:** Backend Python code only

## Troubleshooting

### Codacy not analyzing PRs

1. Check GitHub App is installed: Settings > Integrations > GitHub Apps
2. Verify repository permissions in Codacy dashboard
3. Check `.codacy.yml` syntax is valid

### Too many false positives

1. Go to Codacy > Code Patterns
2. Disable specific rules causing noise
3. Or add inline `# noqa` comments for one-off suppressions

## Next Steps

- [ ] Frontend integration (planned separately)
- [ ] Coverage report upload
- [ ] Quality gate enforcement (when ready)
```

- [ ] **Step 2: Commit the documentation**

```bash
git add docs/codacy-setup.md
git commit -m "docs: add Codacy setup guide

Documents manual steps for GitHub App installation,
quality settings, and troubleshooting."
```

---

## Task 4: Final Verification and Push

**Files:** None (verification only)

- [ ] **Step 1: Verify all files are committed**

Run: `git status`

Expected: "nothing to commit, working tree clean"

- [ ] **Step 2: Review commit history**

Run: `git log --oneline -3`

Expected: Two commits for Codacy config and docs

- [ ] **Step 3: Push branch to remote**

```bash
git push -u origin feat/codacy-integration
```

- [ ] **Step 4: Report completion**

Notify user that:
1. Branch `feat/codacy-integration` is ready
2. Next step: Follow `docs/codacy-setup.md` to install GitHub App
3. After GitHub App installed, create PR to trigger first Codacy analysis
