"""
Test script to verify the task evaluation service works end-to-end.
"""

import asyncio
import os

from dotenv import load_dotenv

from api.core.database import get_session
from api.evaluations.schemas import DatasetConfig, ModelConfig, TaskEvaluationRequest
from api.evaluations.service import EvaluationService

load_dotenv()


async def test_task_evaluation_service():
    """Test the task evaluation service."""
    print("Starting task evaluation service test...")

    # Step 1: Get user ID
    print("\n1. Loading user ID...")
    user_id = "e01da140-64b2-4ab9-b379-4f55dcaf0b22"
    if not user_id:
        print("⚠ No USER_ID found in environment. Please set it to test the service.")
        return
    print(f"✓ User ID loaded: {user_id}")

    # Step 2: Prepare request
    print("\n2. Preparing evaluation request...")
    request = TaskEvaluationRequest(
        task_name="gsm8k|5",
        dataset_config=DatasetConfig(
            dataset_name="gsm8k",
            n_samples=5,
        ),
        model_completion_config=ModelConfig(
            model_name="deepseek-ai/DeepSeek-V3.2",
            model_id="deepseek-ai/DeepSeek-V3.2",
            model_slug="deepseek-ai/DeepSeek-V3.2",
            model_provider="baseten",
            model_provider_slug="baseten",
            model_provider_id="0",
        ),
        judge_config=ModelConfig(
            model_name="gpt-4o",
            model_id="gpt-4o",
            model_slug="gpt-4o",
            model_provider="openai",
            model_provider_slug="openai",
            model_provider_id="0",
        ),
    )
    print(
        f"✓ Request prepared: task={request.task_name}, samples={request.dataset_config.n_samples}"
    )

    # Step 3: Create database session
    print("\n3. Creating database session...")
    async for session in get_session():
        print("✓ Database session created")

        # Step 4: Run evaluation
        print("\n4. Running task evaluation...")
        service = EvaluationService(session, user_id)

        try:
            trace = await service._create_task_trace(request)

            await EvaluationService._run_task_evaluation_background(trace.id, request)

            print("✓ Evaluation started")

            # Step 5: Display results
            print("\n5. Results:")
            print(f"   Trace ID: {trace.id}")
            print("   Status: running")

            print("\n✓ Test completed successfully!")

        except Exception as e:
            print(f"✗ Evaluation failed: {e}")
            raise

        break


if __name__ == "__main__":
    asyncio.run(test_task_evaluation_service())
