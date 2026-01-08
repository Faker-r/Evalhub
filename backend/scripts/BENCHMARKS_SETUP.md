# Benchmarks Population Script

```bash
# Populate all tasks (may take a while - 646 tasks)
python -m scripts.populate_benchmarks

# Or limit for testing
python -m scripts.populate_benchmarks --limit 10

# With HuggingFace token for higher rate limits
python -m scripts.populate_benchmarks --hf-token YOUR_HF_TOKEN
```

**Note**: The script filters for generative tasks only (those using `SamplingMethod.GENERATIVE`).
