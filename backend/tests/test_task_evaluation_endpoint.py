"""
Test script to verify the task evaluation service works end-to-end.
"""

import asyncio
import os

import pytest
from dotenv import load_dotenv

pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Manual integration — set RUN_INTEGRATION_TESTS=1",
)

from api.core.database import get_session
from api.evaluations.schemas import (
    DatasetConfig,
    StandardEvaluationModelConfig,
    TaskEvaluationRequest,
)
from api.evaluations.service import EvaluationService
from api.models_and_providers.schemas import ModelResponse, ProviderResponse

load_dotenv()


def _std_model_config(
    *,
    model_id: str,
    display_name: str,
    api_name: str,
    provider_name: str,
) -> StandardEvaluationModelConfig:
    prov = ProviderResponse(
        id=f"p-{provider_name}",
        name=provider_name,
        slug=provider_name,
        base_url="https://api.example.com/v1",
    )
    model = ModelResponse(
        id=model_id,
        display_name=display_name,
        developer=provider_name,
        api_name=api_name,
        providers=[prov],
    )
    return StandardEvaluationModelConfig(
        api_source="standard",
        model=model,
        provider=prov,
    )


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
        model_completion_config=_std_model_config(
            model_id="deepseek-ai/DeepSeek-V3.2",
            display_name="deepseek-ai/DeepSeek-V3.2",
            api_name="deepseek-ai/DeepSeek-V3.2",
            provider_name="baseten",
        ),
        judge_config=_std_model_config(
            model_id="gpt-4o",
            display_name="gpt-4o",
            api_name="gpt-4o",
            provider_name="openai",
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
            assert trace.id is not None

            print("✓ Trace created in database")

            # Step 5: Display results
            print("\n5. Results:")
            print(f"   Trace ID: {trace.id}")

            print("\n✓ Test completed successfully!")

        except Exception as e:
            print(f"✗ Evaluation failed: {e}")
            raise

        break


if __name__ == "__main__":
    asyncio.run(test_task_evaluation_service())
