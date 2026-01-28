"""Script to populate benchmarks table with lighteval tasks.

This script:
1. Loads all generative tasks from lighteval Registry
2. Fetches metadata from HuggingFace API for each task
3. Estimates input tokens by tokenizing dataset samples
4. Stores all information in the benchmarks table

NOTES:
- SORTED BY DOWNLOAD COUNT (most popular first)
- GATED AND DEPRECATED DATASETS CANNOT ESTIMATE INPUT TOKENS

Usage:
    python -m scripts.populate_benchmarks [--limit N] [--hf-token TOKEN]
    
    The script will automatically use HF_TOKEN from .env if available.
    Use --hf-token to override the .env token.
"""

import argparse
import asyncio
import re
from datetime import datetime
from typing import Optional
from collections import defaultdict

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
from lighteval.tasks.registry import Registry
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from transformers import AutoTokenizer

from api.benchmarks.repository import BenchmarkRepository
from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from scripts.benchmark_utils import (
    clean_description,
    filter_benchmark_tags,
    infer_tags_from_task_info
)

setup_logging()
logger = get_logger(__name__)

# Global args for accessing CLI flags
args = None

# Minimum downloads required to include a dataset (0 = no limit)
MIN_DOWNLOADS = 0

# Correction map for known incomplete/incorrect repo names in lighteval registry
# These are popular datasets that lighteval stores with wrong names
# Keys should be lowercase for case-insensitive matching
# This is a lighteval issue though
REPO_NAME_CORRECTIONS = {
    "emotion": "dair-ai/emotion",
    "pubmed_qa": "qiaojin/PubMedQA",
    "pubmedqa": "qiaojin/PubMedQA",
    "parquet": None,  # Invalid repo, skip entirely
}


def normalize_repo_name(hf_repo: str) -> Optional[str]:
    """
    Normalize and validate a HuggingFace repo name.

    Returns the corrected repo name, or None if the repo should be skipped.
    """
    # Check if we have a correction for this repo (case-insensitive)
    hf_repo_lower = hf_repo.lower()
    if hf_repo_lower in REPO_NAME_CORRECTIONS:
        corrected = REPO_NAME_CORRECTIONS[hf_repo_lower]
        if corrected is None:
            logger.warning(f"Skipping invalid repo: {hf_repo}")
            return None
        logger.info(f"Correcting repo name: {hf_repo} -> {corrected}")
        return corrected

    # Valid repo names should have author/name format
    if "/" not in hf_repo:
        logger.warning(f"Skipping repo with invalid format (missing author): {hf_repo}")
        return None

    return hf_repo


def get_dataset_info(hf_repo: str, token: Optional[str] = None) -> dict:
    """
    Query Hugging Face API to get information about a dataset given its hf_repo.

    Args:
        hf_repo: Hugging Face repository identifier
        token: Optional Hugging Face API token for authenticated requests

    Returns:
        dict: Dictionary containing dataset information
    """
    api = HfApi(token=token)

    result = {
        "repo_id": hf_repo,
        "repo_info": None,
        "error": None,
    }

    # Try to find the repository by trying different repo types
    repo_info = None
    repo_type = None

    # First, try to auto-detect the repo type
    try:
        repo_info = api.repo_info(repo_id=hf_repo, repo_type=None)
        repo_type = getattr(repo_info, "type", "dataset")
    except HfHubHTTPError:
        # If auto-detection fails, try dataset first (most common for benchmarks)
        for rt in ["dataset", "model", "space"]:
            try:
                repo_info = api.repo_info(repo_id=hf_repo, repo_type=rt)
                repo_type = rt
                break
            except HfHubHTTPError:
                continue

    if not repo_info:
        result["error"] = f"Repository '{hf_repo}' not found"
        return result

    try:
        # Extract repository information
        result["repo_info"] = {
            "id": repo_info.id,
            "type": repo_type,
            "author": getattr(repo_info, "author", None),
            "created_at": (
                repo_info.created_at.isoformat() if hasattr(repo_info, "created_at") and repo_info.created_at else None
            ),
            "private": getattr(repo_info, "private", None),
            "gated": getattr(repo_info, "gated", None),
            "downloads": getattr(repo_info, "downloads", None),
            "tags": getattr(repo_info, "tags", []),
            "description": getattr(repo_info, "description", None),
            "card_data": getattr(repo_info, "card_data", None),
            "siblings": (
                [sibling.rfilename for sibling in repo_info.siblings]
                if hasattr(repo_info, "siblings")
                else []
            ),
        }

    except Exception as e:
        result["error"] = f"Error: {str(e)}"

    return result


# Global tokenizer cache to avoid reloading
_tokenizer_cache = None

def get_tokenizer():
    """Get cached tokenizer instance."""
    global _tokenizer_cache
    if _tokenizer_cache is None:
        from transformers import AutoTokenizer
        _tokenizer_cache = AutoTokenizer.from_pretrained("gpt2")
    return _tokenizer_cache


def cancel_alarm():
    """Cancel alarm if on Unix system."""
    import signal
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)


def get_dataset_size(
    hf_repo: str,
    hf_subset: Optional[str],
    evaluation_splits: list[str],
    token: Optional[str] = None
) -> Optional[int]:
    """
    Get the total number of samples in the evaluation splits of a dataset.

    Args:
        hf_repo: HuggingFace repository identifier
        hf_subset: Dataset subset/config name (from task_config.hf_subset)
        evaluation_splits: List of splits to count (from task_config.evaluation_splits)
        token: Optional HuggingFace API token for authenticated requests

    Returns:
        Optional[int]: Total number of samples across evaluation splits, or None if unavailable
    """
    try:
        from datasets import load_dataset_builder

        # Load the dataset builder to get info without downloading data
        builder = None
        try:
            builder = load_dataset_builder(hf_repo, hf_subset, token=token)
        except Exception as e:
            # If it fails, try with trust_remote_code for datasets that require it
            error_msg = str(e).lower()
            if "trust_remote_code" in error_msg or "custom code" in error_msg:
                builder = load_dataset_builder(hf_repo, hf_subset, token=token, trust_remote_code=True)
            else:
                raise

        if not builder or not builder.info or not builder.info.splits:
            logger.warning(f"No split info available for {hf_repo} (subset: {hf_subset})")
            return None

        # Sum up only the evaluation splits
        total_size = 0
        splits_found = []
        for split_name in evaluation_splits:
            if split_name in builder.info.splits:
                split_info = builder.info.splits[split_name]
                if split_info.num_examples is not None:
                    total_size += split_info.num_examples
                    splits_found.append(split_name)

        if total_size > 0:
            logger.info(f"Dataset size for {hf_repo}: {total_size} samples (splits: {', '.join(splits_found)})")
            return total_size

        logger.warning(f"No evaluation splits found for {hf_repo}. Requested: {evaluation_splits}, Available: {list(builder.info.splits.keys())}")
        return None
    except Exception as e:
        logger.warning(f"Could not get dataset size for {hf_repo}: {e}")
        return None


def estimate_avg_tokens_per_sample(
    hf_repo: str,
    hf_subset: Optional[str],
    evaluation_splits: list[str],
    token: Optional[str] = None,
    max_samples: int = 50,
    timeout: int = 30
) -> Optional[int]:
    """
    Estimate the average number of input tokens per sample by tokenizing samples
    from the evaluation splits.

    Args:
        hf_repo: HuggingFace repository identifier
        hf_subset: Dataset subset/config name (from task_config.hf_subset)
        evaluation_splits: List of splits to sample from (from task_config.evaluation_splits)
        token: Optional HuggingFace API token for authenticated requests
        max_samples: Maximum number of samples to analyze (default: 50)
        timeout: Maximum seconds to spend on this dataset (default: 30)

    Returns:
        Optional[int]: Average number of tokens per sample, or None if estimation fails
    """
    try:
        import signal
        from datasets import load_dataset

        # Set up timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Token estimation timed out after {timeout}s")

        # Only set alarm on Unix systems
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        dataset = None
        split_used = None

        # Try each evaluation split until one works
        for split in evaluation_splits:
            try:
                dataset = load_dataset(hf_repo, hf_subset, split=split, streaming=True, token=token)
                split_used = split
                break
            except Exception as e:
                error_msg = str(e).lower()
                # If split doesn't exist, try next one
                if "split" in error_msg:
                    continue
                # Other errors, also try next split
                continue

        # If no evaluation split worked, give up
        if dataset is None:
            logger.warning(f"Could not load dataset {hf_repo} (subset: {hf_subset}): no evaluation splits available")
            cancel_alarm()
            return None

        # Use cached tokenizer
        tokenizer = get_tokenizer()

        def value_to_text(value) -> str:
            """Recursively convert any value to text for token counting."""
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            if isinstance(value, (int, float, bool)):
                return str(value)
            if isinstance(value, list):
                return " ".join(value_to_text(item) for item in value)
            if isinstance(value, dict):
                return " ".join(value_to_text(v) for v in value.values())
            return str(value)

        token_counts = []
        for i, sample in enumerate(dataset):
            if i >= max_samples:
                break

            # Concatenate ALL text content from the sample
            text_parts = []
            if isinstance(sample, dict):
                for key, value in sample.items():
                    part = value_to_text(value)
                    if part:
                        text_parts.append(part)

            text = " ".join(text_parts)

            if text:
                tokens = tokenizer.encode(text)
                token_counts.append(len(tokens))

        # Cancel alarm
        cancel_alarm()

        if token_counts:
            avg_tokens = sum(token_counts) // len(token_counts)
            subset_info = f" (subset: {hf_subset})" if hf_subset else ""
            logger.info(
                f"Estimated {avg_tokens} avg tokens/sample for {hf_repo}{subset_info} "
                f"(from {len(token_counts)} samples in '{split_used}' split)"
            )
            return avg_tokens
        else:
            logger.warning(f"Could not estimate tokens for {hf_repo}: no text content found")
            return None

    except TimeoutError as e:
        logger.warning(f"Token estimation timeout for {hf_repo}: {e}")
        cancel_alarm()
        return None
    except Exception as e:
        logger.warning(f"Failed to estimate tokens for {hf_repo}: {e}")
        cancel_alarm()
        return None


async def populate_benchmarks(limit: Optional[int] = None, hf_token: Optional[str] = None):
    """
    Populate the benchmarks table with lighteval tasks.
    
    Tasks are grouped by their HuggingFace repository, so multiple task variants
    (e.g., gpqa:diamond, gpqa:extended) are stored as a single benchmark entry
    with all tasks in the tasks array.

    Args:
        limit: Optional limit on number of repositories to process
        hf_token: Optional HuggingFace API token
    """
    logger.info("Loading lighteval tasks...")

    # Load all task configs
    all_tasks = Registry().load_all_task_configs()

    # Filter to only generative tasks
    generative_tasks = {
        task: task_config
        for task, task_config in all_tasks.items()
        if all(str(m.category) == "SamplingMethod.GENERATIVE" for m in task_config.metrics)
    }

    logger.info(f"Found {len(generative_tasks)} generative tasks out of {len(all_tasks)} total tasks")

    # Group tasks by repository (normalize repo names and skip invalid ones)
    repo_to_tasks = defaultdict(list)
    skipped_repos = set()
    for task_name, task_config in generative_tasks.items():
        normalized_repo = normalize_repo_name(task_config.hf_repo)
        if normalized_repo is None:
            skipped_repos.add(task_config.hf_repo)
            continue
        repo_to_tasks[normalized_repo].append((task_name, task_config))

    if skipped_repos:
        logger.info(f"Skipped {len(skipped_repos)} repos with invalid names: {', '.join(skipped_repos)}")
    logger.info(f"Grouped into {len(repo_to_tasks)} unique repositories")

    # Get download counts for each unique repo to sort by popularity
    logger.info("Fetching download counts to prioritize popular datasets...")
    repo_downloads = {}
    
    for repo in repo_to_tasks.keys():
        dataset_info = get_dataset_info(repo, hf_token)
        downloads = dataset_info.get("repo_info", {}).get("downloads", 0) if not dataset_info.get("error") else 0
        repo_downloads[repo] = downloads or 0  # Treat None as 0
    
    # Filter out repos with too few downloads
    filtered_repos = {
        repo: tasks for repo, tasks in repo_to_tasks.items()
        if repo_downloads.get(repo, 0) >= MIN_DOWNLOADS
    }
    low_download_repos = len(repo_to_tasks) - len(filtered_repos)
    if low_download_repos > 0:
        logger.info(f"Filtered out {low_download_repos} repos with < {MIN_DOWNLOADS} downloads")

    # Sort repositories by download count (descending)
    sorted_repos = sorted(
        filtered_repos.items(),
        key=lambda item: repo_downloads.get(item[0], 0),
        reverse=True
    )

    logger.info(f"Processing {len(sorted_repos)} repositories (sorted by download count)")

    if limit:
        sorted_repos = sorted_repos[:limit]
        logger.info(f"Limited to {limit} repositories")

    # Create async engine and session
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"ssl": "require", "statement_cache_size": 0},
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Track success/failure stats
    success_count = 0
    failure_count = 0
    failed_repos = []

    for i, (hf_repo, tasks) in enumerate(sorted_repos, 1):
        # Use the first task as the primary task
        primary_task_name, primary_task_config = tasks[0]
        
        # Collect all task names for this repo (sorted alphabetically)
        all_task_names = sorted([task_name for task_name, _ in tasks])
        
        logger.info(f"Processing {i}/{len(sorted_repos)}: {hf_repo} ({len(tasks)} tasks: {', '.join(all_task_names)})")

        try:
            # Get dataset info from HF (once per repo, not per task)
            dataset_info = get_dataset_info(hf_repo, hf_token)

            if dataset_info.get("error"):
                logger.warning(f"Error fetching info for {hf_repo}: {dataset_info['error']}")
                repo_info = {}
            else:
                repo_info = dataset_info.get("repo_info", {})

            # Parse created_at
            created_at_hf = None
            if repo_info.get("created_at"):
                try:
                    created_at_hf = datetime.fromisoformat(repo_info["created_at"])
                except Exception:
                    pass

            # Prepare benchmark data
            # Convert gated to boolean (HuggingFace returns 'auto', True, False, or None)
            gated_value = repo_info.get("gated")
            if isinstance(gated_value, bool):
                gated = gated_value
            elif gated_value == "auto" or gated_value is True:
                gated = True
            else:
                gated = False
            
            # Get HuggingFace tags and filter to only benchmark type tags
            raw_tags = repo_info.get("tags", [])
            hf_tags = filter_benchmark_tags(raw_tags)
            
            # Get description from HuggingFace or card data and clean it
            raw_description = repo_info.get("description")
            if not raw_description and repo_info.get("card_data"):
                # Try to extract description from card_data if available
                card_data = repo_info.get("card_data")
                if isinstance(card_data, dict):
                    raw_description = card_data.get("description") or card_data.get("summary")
            
            # Clean the description to remove markdown formatting and extract summary
            description = clean_description(raw_description)

            # Infer additional tags from task name/description
            inferred_tags = infer_tags_from_task_info(primary_task_name or hf_repo, description)
            if inferred_tags:
                logger.debug(f"Inferred tags for {hf_repo}: {inferred_tags}")
                for tag in inferred_tags:
                    if tag not in hf_tags:
                        hf_tags.append(tag)
            
            
            dataset_name = hf_repo.split('/')[-1] if '/' in hf_repo else hf_repo
            
            benchmark_data = {
                "dataset_name": dataset_name,  # Use repo name as title
                "hf_repo": hf_repo,
                "description": description,
                "author": repo_info.get("author"),
                "downloads": repo_info.get("downloads"),
                "tags": hf_tags,
                "repo_type": repo_info.get("type"),
                "created_at_hf": created_at_hf.replace(tzinfo=None) if created_at_hf else None,
                "private": repo_info.get("private"),
                "gated": gated,
                "files": repo_info.get("siblings", []),
                "tasks": all_task_names,  # Store all task names
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            # Create a new session for each repo to avoid rollback cascade
            async with async_session() as session:
                repository = BenchmarkRepository(session)
                # Use dataset name for upsert
                benchmark = await repository.upsert(dataset_name, benchmark_data)

                # Process tasks - calculate size and tokens for each task variant
                if not (args and args.skip_task_details):
                    if len(tasks) > 1:
                        logger.info(f"Processing {len(tasks)} tasks for {hf_repo}")

                    # Cache to avoid redundant API calls for same subset+splits combo
                    task_cache = {}  # key: (subset, tuple(splits)) -> (size, tokens)

                    for task_name, task_config in tasks:
                        # Get this task's specific subset and evaluation splits
                        task_subset = task_config.hf_subset
                        if task_config.evaluation_splits:
                            task_eval_splits = list(task_config.evaluation_splits)
                        elif task_config.hf_avail_splits:
                            task_eval_splits = list(task_config.hf_avail_splits)
                        else:
                            task_eval_splits = ["train", "validation", "test"]

                        # Check cache first
                        cache_key = (task_subset, tuple(sorted(task_eval_splits)))
                        if cache_key in task_cache:
                            task_size, task_tokens = task_cache[cache_key]
                        else:
                            # Calculate size and tokens for this specific task
                            task_size = get_dataset_size(hf_repo, task_subset, task_eval_splits, token=hf_token)

                            task_tokens = None
                            if not (args and args.skip_tokens):
                                task_avg_tokens = estimate_avg_tokens_per_sample(
                                    hf_repo, task_subset, task_eval_splits, token=hf_token
                                )
                                if task_avg_tokens and task_size:
                                    task_tokens = task_avg_tokens * task_size

                            # Store in cache
                            task_cache[cache_key] = (task_size, task_tokens)

                        task_data = {
                            "task_name": task_name,
                            "hf_subset": task_subset,
                            "evaluation_splits": task_eval_splits,
                            "dataset_size": task_size,
                            "estimated_input_tokens": task_tokens,
                            "updated_at": datetime.now(),
                        }
                        await repository.upsert_task(benchmark.id, task_data)

            logger.info(f"Successfully processed {hf_repo}")
            success_count += 1

        except Exception as e:
            logger.error(f"Error processing {hf_repo}: {e}")
            failure_count += 1
            failed_repos.append(hf_repo)
            continue

    await engine.dispose()
    
    # Log summary
    logger.info("=" * 60)
    logger.info("Finished populating benchmarks")
    logger.info(f"Total processed: {success_count + failure_count}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {failure_count}")
    if failed_repos:
        logger.info(f"Failed repos: {', '.join(failed_repos[:10])}")
        if len(failed_repos) > 10:
            logger.info(f"... and {len(failed_repos) - 10} more")
    logger.info("=" * 60)



def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Populate benchmarks table with lighteval tasks")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of tasks to process (for testing)",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="HuggingFace API token for higher rate limits (overrides HF_TOKEN from .env)",
    )
    parser.add_argument(
        "--skip-tokens",
        action="store_true",
        help="Skip token estimation for faster processing (tokens will be None)",
    )
    parser.add_argument(
        "--skip-task-details",
        action="store_true",
        help="Skip per-task size/token calculation for faster processing",
    )

    # Store args globally so estimate_input_tokens can access skip_tokens flag
    global args
    args = parser.parse_args()

    # Use command line token if provided, otherwise use token from .env
    hf_token = args.hf_token or settings.HF_TOKEN
    
    if hf_token:
        logger.info("Using HuggingFace token for authenticated requests (higher rate limits)")
    else:
        logger.info("No HuggingFace token provided - using unauthenticated requests (lower rate limits)")
    
    if args.skip_tokens:
        logger.info("⚡ FAST MODE: Skipping token estimation")

    if args.skip_task_details:
        logger.info("⚡ FAST MODE: Skipping per-task details")

    asyncio.run(populate_benchmarks(limit=args.limit, hf_token=hf_token))


if __name__ == "__main__":
    main()
