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
