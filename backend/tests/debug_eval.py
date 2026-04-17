import asyncio

from api.core.database import get_session
from api.evaluations.schemas import TaskEvaluationRequest
from api.evaluations.service import EvaluationService
from tests.utils import get_test_user_id


async def debug_task_evaluation():
    request = {
        "task_name": "aime24",
        "dataset_config": {"dataset_name": "aime24", "n_fewshots": 1, "n_samples": 5},
        "model_completion_config": {
            "model_name": "deepseek-ai/DeepSeek-V3.2",
            "model_id": "deepseek-ai/DeepSeek-V3.2",
            "model_slug": "deepseek-ai/DeepSeek-V3.2",
            "model_provider": "baseten",
            "model_provider_slug": "baseten",
            "model_provider_id": "0",
            # "model_name":"openai/gpt-4.1",
            # "model_provider":"openai"
        },
    }

    task_evaluation_request = TaskEvaluationRequest(**request)

    async for session in get_session():
        eval_service = EvaluationService(session, get_test_user_id())
        pipeline_output = eval_service._run_lighteval_task_pipeline(
            task_evaluation_request
        )
        print(pipeline_output)
        break


if __name__ == "__main__":
    asyncio.run(debug_task_evaluation())
