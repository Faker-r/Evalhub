"""
Test script to verify lighteval integration works end-to-end.
This mimics what the evaluation service does.
"""

import os
import tempfile

from dotenv import load_dotenv

from api.evaluations.eval_pipeline.dataset_task import DatasetTask
from api.evaluations.eval_pipeline.eval_pipeline import (
    CustomTaskEvaluationPipeline,
    CustomTaskEvaluationPipelineParameters,
)
from api.evaluations.eval_pipeline.guideline_judge import GuidelineJudgeMetric
from api.guidelines.schemas import GuidelineScoringScale
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.endpoints.litellm_model import LiteLLMClient, LiteLLMModelConfig
from lighteval.tasks.registry import Registry

load_dotenv()

# Test dataset (simple joke evaluation)
dataset_content = """{"input": "write a 1-2 funny lines about apple"}
{"input": "write a 1-2 funny lines about banana"}"""

# Test guideline
guideline = {
    "name": "humor_score",
    "prompt": """You are an expert judge evaluating the humor quality of jokes. Rate how funny the response is on a scale from 0 to 5, where:
- 0-1: Not funny at all
- 2-3: Moderately funny
- 4-5: Very funny""",
    "scoring_scale": GuidelineScoringScale.NUMERIC,
    "scoring_scale_config": {
        "min_value": 0,
        "max_value": 5,
    },
}


def test_lighteval_integration():
    """Test the lighteval integration."""
    print("Starting lighteval integration test...")

    # Step 1: Create judge metric
    print("\n1. Creating judge metric...")
    metric = GuidelineJudgeMetric(
        guideline=guideline,
        model="gpt-4o-mini",
        url="https://api.openai.com/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    print("✓ Judge metric created")

    # Step 2: Create dataset task
    print("\n2. Creating dataset task...")
    dataset_task = DatasetTask(
        dataset_name="test_jokes",
        dataset_content=dataset_content,
        metrics=[metric],
    )
    task = dataset_task.build_lighteval_task()
    print(f"✓ Dataset task created with {len(task.get_docs(None))} samples")

    # Step 3: Create registry
    print("\n3. Creating registry...")
    registry = Registry(tasks=None)
    registry._task_registry["test_jokes"] = task.config
    registry.task_to_configs = {"test_jokes": [task.config]}
    print("✓ Registry created")

    # Step 4: Create model
    print("\n4. Creating model...")
    model_config = LiteLLMModelConfig(
        model_name="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    model = LiteLLMClient(model_config)

    # Initialize registry on model cache
    if hasattr(model, "_cache") and model._cache is not None:
        model._cache._init_registry(registry)
    print("✓ Model created")

    # Step 5: Create evaluation tracker
    print("\n5. Creating evaluation tracker...")
    temp_dir = tempfile.mkdtemp()
    evaluation_tracker = EvaluationTracker(
        output_dir=temp_dir,
        save_details=True,
        push_to_hub=False,
    )
    print(f"✓ Evaluation tracker created (output dir: {temp_dir})")

    # Step 6: Run evaluation pipeline
    print("\n6. Running evaluation pipeline...")
    pipeline = CustomTaskEvaluationPipeline(
        task=task,
        evaluation_tracker=evaluation_tracker,
        model=model,
        params=CustomTaskEvaluationPipelineParameters(
            max_samples=2, save_details=True, use_cache=True  # Only test with 2 samples
        ),
    )

    results = pipeline.evaluate()
    pipeline.save_and_push_results()
    print("✓ Evaluation completed")

    # Step 7: Display results
    print("\n7. Results:")
    print(f"   Task: {results['task']}")
    print(f"   Samples evaluated: {len(results['samples'])}")
    print(f"   Summary: {results['summary']}")

    for i, sample in enumerate(results["samples"]):
        print(f"\n   Sample {i}:")
        print(f"     Score: {sample.get('humor_score', 'N/A')}")

    # Cleanup
    dataset_task.cleanup()
    print("\n✓ Test completed successfully!")


if __name__ == "__main__":
    test_lighteval_integration()
