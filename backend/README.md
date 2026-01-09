# Evalhub
Infra for LLM evaluations

## Backend setup

From `backend/`, run:

```bash
./bootstrap.sh
```

This will:

- install backend dependencies with `poetry install`
- clone `huggingface/lighteval` into `backend/lighteval` if it does not exist
- install lighteval in editable mode using `scripts/setup_lighteval.py`

Note: We're using an unreleased version of `lighteval`, therefore we build from the latest changes to their github repo.