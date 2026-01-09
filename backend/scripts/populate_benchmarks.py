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


def estimate_input_tokens(hf_repo: str, max_samples: int = 50, timeout: int = 10) -> Optional[int]:
    """
    Estimate the number of input tokens in a dataset by tokenizing samples.
    
    Handles multiple configs and splits automatically.
    Optimized for speed with caching and reduced samples.

    Args:
        hf_repo: HuggingFace repository identifier
        max_samples: Maximum number of samples to analyze (default: 50, reduced for speed)
        timeout: Maximum seconds to spend on this dataset (default: 10)

    Returns:
        Optional[int]: Average number of tokens per sample, or None if estimation fails
    """
    try:
        import signal
        from datasets import load_dataset, get_dataset_config_names
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Token estimation timed out after {timeout}s")
        
        # Only set alarm on Unix systems
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        dataset = None
        config_used = None
        split_used = None
        
        # Try different splits in order of preference (reduced to speed up)
        splits_to_try = ["test", "validation"]  # Skip train (usually largest)
        
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
            cancel_alarm()
            return None

        # Use cached tokenizer
        tokenizer = get_tokenizer()

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

        # Cancel alarm
        cancel_alarm()

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

    # Group tasks by repository
    repo_to_tasks = defaultdict(list)
    for task_name, task_config in generative_tasks.items():
        repo_to_tasks[task_config.hf_repo].append((task_name, task_config))
    
    logger.info(f"Grouped into {len(repo_to_tasks)} unique repositories")

    # Get download counts for each unique repo to sort by popularity
    logger.info("Fetching download counts to prioritize popular datasets...")
    repo_downloads = {}
    
    for repo in repo_to_tasks.keys():
        dataset_info = get_dataset_info(repo, hf_token)
        downloads = dataset_info.get("repo_info", {}).get("downloads", 0) if not dataset_info.get("error") else 0
        repo_downloads[repo] = downloads or 0  # Treat None as 0
    
    # Sort repositories by download count (descending)
    sorted_repos = sorted(
        repo_to_tasks.items(),
        key=lambda item: repo_downloads.get(item[0], 0),
        reverse=True
    )
    
    logger.info(f"Sorted repositories by download count (most popular first)")

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

            # Estimate input tokens (skip if --skip-tokens flag is set)
            estimated_tokens = None if (args and args.skip_tokens) else estimate_input_tokens(hf_repo)

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
                "estimated_input_tokens": estimated_tokens,
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
                await repository.upsert(dataset_name, benchmark_data)
            
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

    asyncio.run(populate_benchmarks(limit=args.limit, hf_token=hf_token))


if __name__ == "__main__":
    main()
