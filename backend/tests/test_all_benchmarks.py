"""
Benchmark Compatibility Test Script

This script tests all supported benchmarks from the Evalhub database to verify
that the evaluation system can run end-to-end evaluations without breaking.

It generates a markdown report showing:
- Which benchmarks succeeded
- Which benchmarks failed and their error traces
- Summary statistics

Usage:
    poetry run python -m tests.test_all_benchmarks                     # Run all benchmarks with baseten
    poetry run python -m tests.test_all_benchmarks --limit 5           # Run first 5 benchmarks
    poetry run python -m tests.test_all_benchmarks --provider openai   # Use OpenAI instead of baseten
    poetry run python -m tests.test_all_benchmarks --from-json         # Load from JSON file instead of Supabase
"""

import os
import sys
import json
import asyncio
import argparse
import traceback
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from api.core.database import get_session
from api.core.supabase import get_supabase_client
from api.evaluations.service import EvaluationService
from api.evaluations.repository import EvaluationRepository
from api.evaluations.schemas import TaskEvaluationRequest, DatasetConfig, ModelConfig


# Polling configuration
POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 600  # 10 minutes max per benchmark

# Provider configurations
PROVIDER_CONFIGS = {
    "baseten": {
        "model_name": "deepseek-ai/DeepSeek-V3.2",
        "model_provider": "baseten",
    },
    "openai": {
        "model_name": "gpt-4o-mini",
        "model_provider": "openai",
    },
}


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""
    dataset_name: str
    task_name: str
    status: str  # "success", "error", "silent_failure", "timeout"
    trace_id: Optional[int] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    scores: Optional[dict] = None
    duration_seconds: float = 0.0


@dataclass
class TestReport:
    """Full test report for all benchmarks."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_benchmarks: int = 0
    successful: list[BenchmarkResult] = field(default_factory=list)
    failed: list[BenchmarkResult] = field(default_factory=list)
    silent_failures: list[BenchmarkResult] = field(default_factory=list)
    timeouts: list[BenchmarkResult] = field(default_factory=list)


def fetch_benchmarks_from_supabase() -> list[dict]:
    """Fetch all benchmarks from the Supabase benchmarks table, sorted by downloads descending."""
    print("Fetching benchmarks from Supabase...")
    client = get_supabase_client()
    response = client.table("benchmarks").select("*").order("downloads", desc=True).execute()
    benchmarks = response.data
    print(f"Found {len(benchmarks)} benchmarks in Supabase (sorted by downloads)")
    return benchmarks


def fetch_benchmarks_by_names(names: list[str]) -> list[dict]:
    """Fetch specific benchmarks from Supabase by dataset_name."""
    print(f"Fetching specific benchmarks: {names}")
    client = get_supabase_client()
    response = client.table("benchmarks").select("*").in_("dataset_name", names).execute()
    benchmarks = response.data
    # Sort by downloads like the main fetcher
    benchmarks.sort(key=lambda x: x.get("downloads", 0), reverse=True)
    print(f"Found {len(benchmarks)} benchmarks matching the provided names")
    return benchmarks


def fetch_benchmarks_from_json(filepath: str = "benchmarks_rows.json") -> list[dict]:
    """Fetch benchmarks from local JSON file, sorted by downloads descending."""
    print(f"Looking for {filepath}...")

    # Try multiple possible locations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        filepath,  # Current working directory
        os.path.join(script_dir, filepath),  # Same directory as script (backend/tests/)
        os.path.join(script_dir, "..", filepath),  # backend/
        os.path.join(script_dir, "..", "..", filepath),  # repo root
    ]

    resolved_path = None
    for path in possible_paths:
        if os.path.exists(path):
            resolved_path = path
            break

    if not resolved_path:
        raise FileNotFoundError(
            f"Could not find {filepath}. Tried:\n" + "\n".join(f"  - {p}" for p in possible_paths)
        )

    print(f"Found file at: {resolved_path}")
    with open(resolved_path, encoding="utf-8") as f:
        benchmarks = json.load(f)

    # Sort by downloads descending
    benchmarks.sort(key=lambda x: x.get("downloads", 0), reverse=True)
    print(f"Loaded {len(benchmarks)} benchmarks (sorted by downloads)")
    return benchmarks


def extract_task_name(benchmark: dict) -> str:
    """Extract the task name from a benchmark entry.

    The 'tasks' field is a JSON string like '["gsm8k"]' or '["mmlu_pro"]'.
    We extract the first task name.
    """
    tasks_str = benchmark.get("tasks", "[]")
    if isinstance(tasks_str, str):
        tasks = json.loads(tasks_str)
    else:
        tasks = tasks_str

    if tasks and len(tasks) > 0:
        return tasks[0]

    # Fallback to dataset_name if tasks is empty
    return benchmark.get("dataset_name", "unknown")


def create_evaluation_request(
    task_name: str,
    dataset_name: str,
    n_samples: int = 5,
    n_fewshots: int = 0,
    model_name: str = "deepseek-ai/DeepSeek-V3.2",
    model_provider: str = "baseten",
) -> TaskEvaluationRequest:
    """Create a TaskEvaluationRequest for testing a benchmark."""
    return TaskEvaluationRequest(
        task_name=task_name,
        dataset_config=DatasetConfig(
            dataset_name=dataset_name,
            n_samples=n_samples,
            n_fewshots=n_fewshots,
        ),
        model_completion_config=ModelConfig(
            model_name=model_name,
            model_provider=model_provider,
        ),
        judge_config=None,  # Use default metrics, no judge needed for lighteval tasks
    )


def check_for_silent_failure(scores: dict) -> tuple[bool, str]:
    """Check if scores indicate a silent failure (e.g., all zeros).

    Returns (is_silent_failure, reason)
    """
    if not scores:
        return True, "No scores returned"

    # Check if all numeric scores are zero
    all_zeros = True
    for metric_name, value in scores.items():
        if isinstance(value, (int, float)):
            if value != 0:
                all_zeros = False
                break
        elif isinstance(value, dict):
            # Handle nested score structures
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (int, float)) and sub_value != 0:
                    all_zeros = False
                    break

    if all_zeros:
        return True, f"All scores are zero: {scores}"

    return False, ""


async def poll_trace_completion(
    trace_id: int,
    timeout_seconds: int = POLL_TIMEOUT_SECONDS,
    poll_interval: int = POLL_INTERVAL_SECONDS,
) -> tuple[str, Optional[dict], Optional[str], Optional[str]]:
    """Poll the database until trace completes or times out.

    Returns: (status, summary, error_message, error_traceback)
    """
    start_time = datetime.now()

    while True:
        elapsed = (datetime.now() - start_time).total_seconds()
        if elapsed > timeout_seconds:
            return "timeout", None, f"Timed out after {timeout_seconds} seconds", None

        async for session in get_session():
            repository = EvaluationRepository(session)
            try:
                trace = await repository.get_trace_by_id(trace_id)

                if trace.status == "completed":
                    return "completed", trace.summary, None, None
                elif trace.status == "failed":
                    # Extract error and traceback from summary
                    error_msg = None
                    error_tb = None
                    if trace.summary:
                        error_msg = trace.summary.get("error")
                        error_tb = trace.summary.get("traceback")
                    return "failed", trace.summary, error_msg, error_tb
                # Still running, continue polling
            finally:
                await session.close()
            break

        print(f"    ... still running ({int(elapsed)}s elapsed)")
        await asyncio.sleep(poll_interval)


async def get_trace_error_events(trace_id: int) -> list[dict]:
    """Fetch any error events associated with a trace."""
    async for session in get_session():
        repository = EvaluationRepository(session)
        try:
            events = await repository.get_events_by_trace(trace_id)
            error_events = [
                {
                    "event_type": e.event_type,
                    "data": e.data,
                    "sample_id": e.sample_id,
                    "guideline_name": e.guideline_name,
                }
                for e in events
                if e.event_type == "error"
            ]
            return error_events
        finally:
            await session.close()
        break
    return []


async def run_single_benchmark(
    benchmark: dict,
    user_id: str,
    n_samples: int = 5,
    model_name: str = "deepseek-ai/DeepSeek-V3.2",
    model_provider: str = "baseten",
) -> BenchmarkResult:
    """Run a single benchmark and return the result."""
    dataset_name = benchmark.get("dataset_name", "unknown")
    task_name = extract_task_name(benchmark)

    print(f"\n{'='*60}")
    print(f"Testing: {dataset_name} (task: {task_name})")
    print(f"{'='*60}")

    start_time = datetime.now()
    trace_id = None

    try:
        request = create_evaluation_request(
            task_name=task_name,
            dataset_name=dataset_name,
            n_samples=n_samples,
            model_name=model_name,
            model_provider=model_provider,
        )

        # Step 1: Start the evaluation
        async for session in get_session():
            service = EvaluationService(session, user_id)
            response = await service.run_task_evaluation(request)
            trace_id = response.trace_id
            print(f"  Started evaluation (trace_id: {trace_id})")
            break

        # Step 2: Poll for completion
        print(f"  Polling for completion...")
        final_status, summary, error_msg, error_tb = await poll_trace_completion(trace_id)

        duration = (datetime.now() - start_time).total_seconds()

        # Step 3: Analyze the result
        if final_status == "timeout":
            print(f"⏱ {dataset_name}: TIMEOUT")
            return BenchmarkResult(
                dataset_name=dataset_name,
                task_name=task_name,
                status="timeout",
                trace_id=trace_id,
                error_message=error_msg,
                duration_seconds=duration,
            )

        elif final_status == "failed":
            # Fetch additional error details from trace events
            error_events = await get_trace_error_events(trace_id)

            full_error = error_msg or "Unknown error"
            if error_events:
                event_errors = "\n".join([
                    f"  - {e['event_type']}: {e['data']}"
                    for e in error_events
                ])
                full_error = f"{full_error}\n\nTrace Events:\n{event_errors}"

            print(f"✗ {dataset_name}: FAILED")
            print(f"  Error: {error_msg}")

            return BenchmarkResult(
                dataset_name=dataset_name,
                task_name=task_name,
                status="error",
                trace_id=trace_id,
                error_message=full_error,
                error_traceback=error_tb,  # Full traceback from background task
                duration_seconds=duration,
            )

        elif final_status == "completed":
            # Check for silent failures
            scores = summary.get("scores", {}) if summary else {}
            is_silent_failure, failure_reason = check_for_silent_failure(scores)

            if is_silent_failure:
                print(f"⚠ {dataset_name}: SILENT FAILURE")
                print(f"  Reason: {failure_reason}")

                return BenchmarkResult(
                    dataset_name=dataset_name,
                    task_name=task_name,
                    status="silent_failure",
                    trace_id=trace_id,
                    error_message=failure_reason,
                    scores=scores,
                    duration_seconds=duration,
                )

            print(f"✓ {dataset_name}: SUCCESS")
            print(f"  Scores: {scores}")

            return BenchmarkResult(
                dataset_name=dataset_name,
                task_name=task_name,
                status="success",
                trace_id=trace_id,
                scores=scores,
                duration_seconds=duration,
            )

        else:
            # Unexpected status
            print(f"? {dataset_name}: UNEXPECTED STATUS ({final_status})")
            return BenchmarkResult(
                dataset_name=dataset_name,
                task_name=task_name,
                status="error",
                trace_id=trace_id,
                error_message=f"Unexpected final status: {final_status}",
                duration_seconds=duration,
            )

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        error_tb = traceback.format_exc()
        print(f"✗ {dataset_name}: FAILED (exception during submission)")
        print(f"  Error: {str(e)}")

        return BenchmarkResult(
            dataset_name=dataset_name,
            task_name=task_name,
            status="error",
            trace_id=trace_id,
            error_message=str(e),
            error_traceback=error_tb,
            duration_seconds=duration,
        )


async def run_all_benchmarks(
    benchmarks: list[dict],
    user_id: str,
    limit: Optional[int] = None,
    n_samples: int = 5,
    model_name: str = "deepseek-ai/DeepSeek-V3.2",
    model_provider: str = "baseten",
) -> TestReport:
    """Run all benchmarks and generate a report."""
    report = TestReport(
        started_at=datetime.now(),
        total_benchmarks=len(benchmarks) if limit is None else min(limit, len(benchmarks)),
    )

    benchmarks_to_test = benchmarks[:limit] if limit else benchmarks

    print(f"\n{'#'*60}")
    print(f"# Running {len(benchmarks_to_test)} benchmark tests")
    print(f"# Samples per benchmark: {n_samples}")
    print(f"# Provider: {model_provider} ({model_name})")
    print(f"# Started at: {report.started_at.isoformat()}")
    print(f"{'#'*60}")

    for i, benchmark in enumerate(benchmarks_to_test, 1):
        print(f"\n[{i}/{len(benchmarks_to_test)}]", end="")

        result = await run_single_benchmark(
            benchmark=benchmark,
            user_id=user_id,
            n_samples=n_samples,
            model_name=model_name,
            model_provider=model_provider,
        )

        if result.status == "success":
            report.successful.append(result)
        elif result.status == "silent_failure":
            report.silent_failures.append(result)
        elif result.status == "timeout":
            report.timeouts.append(result)
        else:
            report.failed.append(result)

    report.completed_at = datetime.now()
    return report


def generate_markdown_report(report: TestReport, output_path: str = "benchmark_test_report.md"):
    """Generate a markdown report from the test results."""

    duration = (report.completed_at - report.started_at).total_seconds() if report.completed_at else 0

    lines = [
        "# Benchmark Compatibility Test Report",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Test Duration:** {duration:.1f} seconds",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Benchmarks Tested | {report.total_benchmarks} |",
        f"| ✓ Successful | {len(report.successful)} |",
        f"| ✗ Failed | {len(report.failed)} |",
        f"| ⚠ Silent Failures | {len(report.silent_failures)} |",
        f"| ⏱ Timeouts | {len(report.timeouts)} |",
        "",
    ]

    # Success rate
    if report.total_benchmarks > 0:
        success_rate = (len(report.successful) / report.total_benchmarks) * 100
        lines.append(f"**Success Rate:** {success_rate:.1f}%")
        lines.append("")

    # Successful benchmarks
    lines.extend([
        "## ✓ Successful Benchmarks",
        "",
    ])

    if report.successful:
        lines.append("| Dataset | Task | Trace ID | Duration (s) | Scores |")
        lines.append("|---------|------|----------|--------------|--------|")
        for result in report.successful:
            scores_summary = _format_scores_summary(result.scores)
            lines.append(f"| {result.dataset_name} | {result.task_name} | {result.trace_id or 'N/A'} | {result.duration_seconds:.1f} | {scores_summary} |")
    else:
        lines.append("_No successful benchmarks_")
    lines.append("")

    # Failed benchmarks with error traces
    lines.extend([
        "## ✗ Failed Benchmarks",
        "",
    ])

    if report.failed:
        for result in report.failed:
            lines.extend([
                f"### {result.dataset_name}",
                "",
                f"**Task:** `{result.task_name}`",
                f"**Trace ID:** {result.trace_id or 'N/A'}",
                f"**Duration:** {result.duration_seconds:.1f}s",
                "",
                "**Error Message:**",
                "```",
                result.error_message or "No error message",
                "```",
                "",
            ])
            if result.error_traceback:
                lines.extend([
                    "**Full Traceback:**",
                    "```python",
                    result.error_traceback,
                    "```",
                    "",
                ])
    else:
        lines.append("_No failed benchmarks_")
    lines.append("")

    # Timeouts
    lines.extend([
        "## ⏱ Timeouts",
        "",
    ])

    if report.timeouts:
        lines.append("| Dataset | Task | Trace ID | Duration (s) |")
        lines.append("|---------|------|----------|--------------|")
        for result in report.timeouts:
            lines.append(f"| {result.dataset_name} | {result.task_name} | {result.trace_id or 'N/A'} | {result.duration_seconds:.1f} |")
    else:
        lines.append("_No timeouts_")
    lines.append("")

    # Silent failures
    lines.extend([
        "## ⚠ Silent Failures",
        "",
        "_These benchmarks completed but returned suspicious results (e.g., all zeros)_",
        "",
    ])

    if report.silent_failures:
        for result in report.silent_failures:
            lines.extend([
                f"### {result.dataset_name}",
                "",
                f"**Task:** `{result.task_name}`",
                f"**Trace ID:** {result.trace_id or 'N/A'}",
                f"**Issue:** {result.error_message or 'Unknown issue'}",
                "",
            ])
            if result.scores:
                lines.extend([
                    "**Scores:**",
                    "```json",
                    json.dumps(result.scores, indent=2),
                    "```",
                    "",
                ])
            if result.warnings:
                lines.append("**Warnings:**")
                for warning in result.warnings:
                    lines.append(f"- {warning}")
                lines.append("")
    else:
        lines.append("_No silent failures detected_")
    lines.append("")

    # Full Error Details section - all tracebacks in one place for easy debugging
    failed_with_tracebacks = [r for r in report.failed if r.error_traceback]
    if failed_with_tracebacks:
        lines.extend([
            "---",
            "",
            "## 📋 Full Error Tracebacks",
            "",
            "_Complete stack traces for all failed benchmarks for debugging purposes._",
            "",
        ])

        for result in failed_with_tracebacks:
            lines.extend([
                f"### {result.dataset_name} (`{result.task_name}`)",
                "",
                "```python",
                result.error_traceback,
                "```",
                "",
            ])

    # Write report
    report_content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n{'='*60}")
    print(f"Report saved to: {output_path}")
    print(f"{'='*60}")

    return report_content


def _format_scores_summary(scores: Optional[dict]) -> str:
    """Format scores dict into a brief summary string."""
    if not scores:
        return "N/A"

    # Take first few metrics
    items = list(scores.items())[:3]
    parts = []
    for key, value in items:
        if isinstance(value, float):
            parts.append(f"{key}: {value:.3f}")
        else:
            parts.append(f"{key}: {value}")

    summary = ", ".join(parts)
    if len(scores) > 3:
        summary += f" (+{len(scores) - 3} more)"

    return summary


def print_summary(report: TestReport):
    """Print a quick summary to console."""
    print(f"\n{'#'*60}")
    print("# TEST SUMMARY")
    print(f"{'#'*60}")
    print(f"Total tested:    {report.total_benchmarks}")
    print(f"✓ Successful:    {len(report.successful)}")
    print(f"✗ Failed:        {len(report.failed)}")
    print(f"⚠ Silent fails:  {len(report.silent_failures)}")
    print(f"⏱ Timeouts:      {len(report.timeouts)}")

    if report.total_benchmarks > 0:
        success_rate = (len(report.successful) / report.total_benchmarks) * 100
        print(f"Success rate:    {success_rate:.1f}%")

    if report.failed:
        print(f"\nFailed benchmarks:")
        for result in report.failed:
            error_preview = (result.error_message[:80] + "...") if result.error_message and len(result.error_message) > 80 else (result.error_message or "Unknown error")
            print(f"  - {result.dataset_name}: {error_preview}")

    if report.timeouts:
        print(f"\nTimed out benchmarks:")
        for result in report.timeouts:
            print(f"  - {result.dataset_name}")


async def main():
    parser = argparse.ArgumentParser(
        description="Test all supported benchmarks for compatibility with the evaluation system."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of benchmarks to test. If not specified, all benchmarks are tested.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["baseten", "openai"],
        default="baseten",
        help="Model provider to use for evaluations (default: baseten)",
    )
    parser.add_argument(
        "--from-json",
        action="store_true",
        help="Load benchmarks from benchmarks_rows.json instead of Supabase",
    )
    parser.add_argument(
        "--datasets",
        type=str,
        help="Comma-separated list of dataset names to run (e.g. 'gsm8k,mmlu'). Supersedes --limit.",
    )

    args = parser.parse_args()

    # Configuration
    user_id = "e01da140-64b2-4ab9-b379-4f55dcaf0b22"
    n_samples = 5
    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    output_path = f"./tests/benchmark_test_report_{timestamp}.md"

    # Get provider config
    provider_config = PROVIDER_CONFIGS[args.provider]
    model_name = provider_config["model_name"]
    model_provider = provider_config["model_provider"]

    # Fetch benchmarks
    # Fetch benchmarks
    if args.datasets:
        dataset_names = [d.strip() for d in args.datasets.split(",") if d.strip()]
        
        if args.from_json:
            all_benchmarks = fetch_benchmarks_from_json()
            # Filter locally
            benchmarks = [b for b in all_benchmarks if b.get("dataset_name") in dataset_names]
            print(f"Filtered to {len(benchmarks)} benchmarks from JSON")
        else:
            try:
                benchmarks = fetch_benchmarks_by_names(dataset_names)
            except Exception as e:
                print(f"Failed to fetch specific benchmarks from Supabase: {e}")
                print("Falling back to JSON file...")
                all_benchmarks = fetch_benchmarks_from_json()
                benchmarks = [b for b in all_benchmarks if b.get("dataset_name") in dataset_names]

    elif args.from_json:
        benchmarks = fetch_benchmarks_from_json()
    else:
        try:
            benchmarks = fetch_benchmarks_from_supabase()
        except Exception as e:
            print(f"Failed to fetch from Supabase: {e}")
            print("Falling back to JSON file...")
            benchmarks = fetch_benchmarks_from_json()

    if not benchmarks:
        print("No benchmarks found!")
        sys.exit(1)

    # Run tests
    # Run tests
    # If datasets are specified, ignore limit unless explicitly desired? 
    # Usually valid to just run what was requested. args.limit applies if set.
    report = await run_all_benchmarks(
        benchmarks=benchmarks,
        user_id=user_id,
        limit=args.limit,
        n_samples=n_samples,
        model_name=model_name,
        model_provider=model_provider,
    )

    # Generate report
    generate_markdown_report(report, output_path)

    # Print summary
    print_summary(report)

    # Exit with error code if there were failures
    if report.failed or report.timeouts:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
