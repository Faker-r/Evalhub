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
from datetime import datetime
from typing import Optional

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
from lighteval.tasks.registry import Registry
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from transformers import AutoTokenizer

from api.benchmarks.repository import BenchmarkRepository
from api.core.config import settings
from api.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


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
            "siblings": (
                [sibling.rfilename for sibling in repo_info.siblings]
                if hasattr(repo_info, "siblings")
                else []
            ),
        }

    except Exception as e:
        result["error"] = f"Error: {str(e)}"

    return result


def estimate_input_tokens(hf_repo: str, max_samples: int = 100) -> Optional[int]:
    """
    Estimate the number of input tokens in a dataset by tokenizing samples.
    
    Handles multiple configs and splits automatically.

    Args:
        hf_repo: HuggingFace repository identifier
        max_samples: Maximum number of samples to analyze

    Returns:
        Optional[int]: Average number of tokens per sample, or None if estimation fails
    """
    try:
        from datasets import load_dataset, get_dataset_config_names
        
        dataset = None
        config_used = None
        split_used = None
        
        # Try different splits in order of preference
        splits_to_try = ["train", "test", "validation", "dev"]
        
        # First, try without config
        for split in splits_to_try:
            try:
                dataset = load_dataset(hf_repo, split=split, streaming=True)
                split_used = split
                break
            except Exception as e:
                error_msg = str(e).lower()
                
                # If it's a config issue, try with configs
                if "config" in error_msg or "subset" in error_msg:
                    try:
                        configs = get_dataset_config_names(hf_repo)
                        if configs:
                            # Try first config with this split
                            dataset = load_dataset(hf_repo, configs[0], split=split, streaming=True)
                            config_used = configs[0]
                            split_used = split
                            break
                    except:
                        continue
                # If it's a split issue, try next split
                elif "split" in error_msg:
                    continue
                # Other errors, try next split
                else:
                    continue
        
        # If still no dataset, give up
        if dataset is None:
            logger.warning(f"Could not load dataset {hf_repo}: tried all splits and configs")
            return None

        # Use a standard tokenizer (GPT-2 as a common baseline)
        tokenizer = AutoTokenizer.from_pretrained("gpt2")

        token_counts = []
        for i, sample in enumerate(dataset):
            if i >= max_samples:
                break

            # Try to find text content in the sample
            text = ""
            if isinstance(sample, dict):
                # Common field names for input text
                for field in ["input", "text", "prompt", "question", "query", "context"]:
                    if field in sample:
                        text = str(sample[field])
                        break
                # If no common field found, concatenate all string values
                if not text:
                    text = " ".join(str(v) for v in sample.values() if isinstance(v, str))

            if text:
                tokens = tokenizer.encode(text)
                token_counts.append(len(tokens))

        if token_counts:
            avg_tokens = sum(token_counts) // len(token_counts)
            config_info = f" (config: {config_used})" if config_used else ""
            logger.info(
                f"Estimated {avg_tokens} tokens for {hf_repo}{config_info} "
                f"(from {len(token_counts)} samples in '{split_used}' split)"
            )
            return avg_tokens
        else:
            logger.warning(f"Could not estimate tokens for {hf_repo}: no text content found")
            return None

    except Exception as e:
        logger.warning(f"Failed to estimate tokens for {hf_repo}: {e}")
        return None


async def populate_benchmarks(limit: Optional[int] = None, hf_token: Optional[str] = None):
    """
    Populate the benchmarks table with lighteval tasks.

    Args:
        limit: Optional limit on number of tasks to process
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

    # Get download counts for each unique repo to sort by popularity
    logger.info("Fetching download counts to prioritize popular datasets...")
    repo_downloads = {}
    unique_repos = {task_config.hf_repo for task_config in generative_tasks.values()}
    
    for repo in unique_repos:
        dataset_info = get_dataset_info(repo, hf_token)
        downloads = dataset_info.get("repo_info", {}).get("downloads", 0) if not dataset_info.get("error") else 0
        repo_downloads[repo] = downloads or 0  # Treat None as 0
    
    # Sort tasks by their repo's download count (descending)
    sorted_tasks = sorted(
        generative_tasks.items(),
        key=lambda item: repo_downloads.get(item[1].hf_repo, 0),
        reverse=True
    )
    generative_tasks = dict(sorted_tasks)
    
    logger.info(f"Sorted tasks by download count (most popular first)")

    if limit:
        generative_tasks = dict(list(generative_tasks.items())[:limit])
        logger.info(f"Limited to {limit} tasks")

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
    failed_tasks = []

    for i, (task_name, task_config) in enumerate(generative_tasks.items(), 1):
        logger.info(f"Processing {i}/{len(generative_tasks)}: {task_name}")

        try:
            hf_repo = task_config.hf_repo

            # Get dataset info from HF
            dataset_info = get_dataset_info(hf_repo, hf_token)

            if dataset_info.get("error"):
                logger.warning(f"Error fetching info for {task_name}: {dataset_info['error']}")
                repo_info = {}
            else:
                repo_info = dataset_info.get("repo_info", {})

            # Estimate input tokens
            estimated_tokens = estimate_input_tokens(hf_repo)

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
            
            benchmark_data = {
                "dataset_name": task_config.name or task_name,
                "hf_repo": hf_repo,
                "author": repo_info.get("author"),
                "downloads": repo_info.get("downloads"),
                "tags": repo_info.get("tags", []),
                "estimated_input_tokens": estimated_tokens,
                "repo_type": repo_info.get("type"),
                "created_at_hf": created_at_hf.replace(tzinfo=None) if created_at_hf else None,
                "private": repo_info.get("private"),
                "gated": gated,
                "files": repo_info.get("siblings", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            # Create a new session for each task to avoid rollback cascade
            async with async_session() as session:
                repository = BenchmarkRepository(session)
                await repository.upsert(task_name, benchmark_data)
            
            logger.info(f"Successfully processed {task_name}")
            success_count += 1

        except Exception as e:
            logger.error(f"Error processing {task_name}: {e}")
            failure_count += 1
            failed_tasks.append(task_name)
            continue

    await engine.dispose()
    
    # Log summary
    logger.info("=" * 60)
    logger.info("Finished populating benchmarks")
    logger.info(f"Total processed: {success_count + failure_count}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {failure_count}")
    if failed_tasks:
        logger.info(f"Failed tasks: {', '.join(failed_tasks[:10])}")
        if len(failed_tasks) > 10:
            logger.info(f"... and {len(failed_tasks) - 10} more")
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

    args = parser.parse_args()

    # Use command line token if provided, otherwise use token from .env
    hf_token = args.hf_token or settings.HF_TOKEN
    
    if hf_token:
        logger.info("Using HuggingFace token for authenticated requests (higher rate limits)")
    else:
        logger.info("No HuggingFace token provided - using unauthenticated requests (lower rate limits)")

    asyncio.run(populate_benchmarks(limit=args.limit, hf_token=hf_token))


if __name__ == "__main__":
    main()
