"""
Test script to verify the flexible evaluation service works end-to-end.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from api.core.database import get_session
from api.evaluations.service import EvaluationService
from api.evaluations.schemas import (
    FlexibleEvaluationRequest,
    ModelConfig,
    MultipleChoiceConfig,
    OutputType,
    JudgeType,
    TextOutputConfig,
)

# Test user ID - replace with your own
USER_ID = "e01da140-64b2-4ab9-b379-4f55dcaf0b22"


async def test_text_exact_match():
    """Test text output with exact match scoring."""
    print("\n" + "=" * 60)
    print("TEST 1: Text Output with Exact Match")
    print("=" * 60)

    request = FlexibleEvaluationRequest(
        dataset_name="mmlu_college_chem_test",  # Uses "question" field from mtbench
        input_field="question",  # Use first turn as input
        output_type=OutputType.MULTIPLE_CHOICE,
        mc_config=MultipleChoiceConfig(choices_field="choices", gold_answer_field="answer"),
        judge_type=JudgeType.EXACT_MATCH,
        model_completion_config=ModelConfig(
            model_name="gpt-5.1",
            model_id="gpt-5.1",
            model_slug="gpt-5.1",
            model_provider="openai",
            model_provider_slug="openai",
            model_provider_id=0,
        ),
    )

    await run_evaluation(request, "Text + Exact Match")


async def test_text_f1_score():
    """Test text output with F1 score."""
    print("\n" + "=" * 60)
    print("TEST 2: Text Output with F1 Score")
    print("=" * 60)

    request = FlexibleEvaluationRequest(
        dataset_name="mmlu_college_chem_test_sample_text",
        input_field="question",
        output_type=OutputType.TEXT,
        text_config=TextOutputConfig(gold_answer_field="answer"),
        judge_type=JudgeType.F1_SCORE,
        model_completion_config=ModelConfig(
            model_name="gpt-5.1",
            model_id="gpt-5.1",
            model_slug="gpt-5.1",
            model_provider="openai",
            model_provider_slug="openai",
            model_provider_id=0,
        ),
    )

    await run_evaluation(request, "Text + F1 Score")


async def test_text_llm_judge():
    """Test text output with LLM as judge."""
    print("\n" + "=" * 60)
    print("TEST 3: Text Output with LLM as Judge")
    print("=" * 60)

    request = FlexibleEvaluationRequest(
        dataset_name="joke_fruits.jsonl",
        input_field="input",
        output_type=OutputType.TEXT,
        text_config=TextOutputConfig(gold_answer_field=None),
        judge_type=JudgeType.LLM_AS_JUDGE,
        guideline_names=["humor"],
        model_completion_config=ModelConfig(
            model_name="gpt-4o-mini",
            model_id="gpt-4o-mini",
            model_slug="gpt-4o-mini",
            model_provider="openai",
            model_provider_slug="openai",
            model_provider_id=0,
        ),
        judge_config=ModelConfig(
            model_name="gpt-4o",
            model_id="gpt-4o",
            model_slug="gpt-4o",
            model_provider="openai",
            model_provider_slug="openai",
            model_provider_id=0,
        ),
    )

    await run_evaluation(request, "Text + LLM as Judge")


async def run_evaluation(request: FlexibleEvaluationRequest, test_name: str):
    """Run a flexible evaluation and display results."""
    print(f"\nStarting {test_name} test...")
    print(f"  Dataset: {request.dataset_name}")
    print(f"  Input field: {request.input_field}")
    print(f"  Output type: {request.output_type}")
    print(f"  Judge type: {request.judge_type}")

    async for session in get_session():
        service = EvaluationService(session, USER_ID)

        try:
            response = await service.run_flexible_evaluation(request)
            print("\n✓ Evaluation started successfully")
            print(f"  Trace ID: {response.trace_id}")
            print(f"  Status: {response.status}")
            print(f"  Task Name: {response.task_name}")
            print(f"  Guideline Names: {response.guideline_names}")
            print(f"  Completion Model: {response.completion_model}")
            print(f"  Model Provider: {response.model_provider}")
            print(f"  Judge Model: {response.judge_model}")
            print(f"  Created At: {response.created_at}")

            # Wait for background task to complete
            print("\n  Waiting for evaluation to complete...")
            await wait_for_completion(service, response.trace_id)

        except Exception as e:
            print(f"\n✗ Evaluation failed: {e}")
            import traceback
            traceback.print_exc()

        break


async def wait_for_completion(service: EvaluationService, trace_id: int, timeout: int = 300):
    """Wait for evaluation to complete and display final results."""
    import time
    start_time = time.time()

    while time.time() - start_time < timeout:
        trace = await service.get_trace(trace_id)

        if trace.status == "completed":
            print("\n✓ Evaluation completed!")
            print(f"  Final Status: {trace.status}")
            if trace.summary:
                print("  Summary:")
                for key, value in trace.summary.get("scores", {}).items():
                    print(f"    {key}: {value}")
            return

        if trace.status == "failed":
            print("\n✗ Evaluation failed!")
            if trace.summary:
                print(f"  Error: {trace.summary.get('error', 'Unknown error')}")
            return

        await asyncio.sleep(5)

    print(f"\n⚠ Timeout waiting for evaluation to complete (>{timeout}s)")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("FLEXIBLE EVALUATION TEST SUITE")
    print("=" * 60)

    if not USER_ID:
        print("⚠ Please set USER_ID in the script")
        return

    print(f"User ID: {USER_ID}")

    # Run tests - comment out tests you don't want to run
    # await test_text_exact_match()
    await test_text_f1_score()
    # await test_text_llm_judge()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
