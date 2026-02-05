"""
Example of how to evaluate a task using a model and a metric.
"""

import logging
import os
from dataclasses import dataclass

import litellm
from dotenv import load_dotenv

from api.evaluations.eval_pipeline.guideline_judge import (
    GuidelineJudgeMetric,
    GuidelineScoringScale,
)
from lighteval.metrics import apply_metric
from lighteval.models.abstract_model import LightevalModel
from lighteval.models.model_output import ModelResponse
from lighteval.tasks.requests import Doc

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASETEN_API_KEY = os.getenv("BASETEN_API_KEY")

logger = logging.getLogger(__name__)


litellm._turn_on_debug()

dataset_file = "/Users/pjavanrood/Code/Evalhub/backend/samples/samples_from_openai_evals/sample_datasets/joke_fruits.jsonl"

"""
The file format is:
{"input": "write a 1-2 funny lines about apple"}
{"input": "write a 1-2 boring lines about apple"}
{"input": "write a 1-2 funny lines about pineapple"}
{"input": "write a 1-2 boring lines about pineapple"}
{"input": "write a 1-2 funny lines about watermelon"}
{"input": "write a 1-2 boring lines about watermelon"}
{"input": "write a 1-2 funny lines about grapefruit"}
{"input": "write a 1-2 boring lines about grapefruit"}
{"input": "write a 1-2 funny lines about mango"}
{"input": "write a 1-2 boring lines about mango"}
"""

humor_guideline = {
    "name": "humor_score",
    "prompt": """You are an expert judge evaluating the humor quality of jokes. Your task is to rate how funny a joke is on a scale from 0 to 10, where:
- 0-2: Not funny at all, no humor detected
- 3-4: Slightly amusing, minimal humor
- 5-6: Moderately funny, decent humor
- 7-8: Quite funny, good humor
- 9-10: Extremely funny, excellent humor

Consider factors such as:
- Originality and creativity
- Timing and delivery
- Cleverness and wit
- Appropriateness of the humor
- Overall comedic effect""",
    "scoring_scale": {
        "type": GuidelineScoringScale.NUMERIC,
        "min_score": 0,
        "max_score": 10,
    },
}

from lighteval.tasks.lighteval_task import LightevalTask, LightevalTaskConfig
from lighteval.tasks.registry import Registry


def line_to_prompt(line, doc):
    return Doc(
        task_name="joke_fruits",
        query=line["input"],
        choices=[],
        gold_index=0,
    )


judge_llm_metric = GuidelineJudgeMetric(
    guideline=humor_guideline,
    model="gpt-4o-2024-08-06",
    url=None,
    api_key=OPENAI_API_KEY,
)

task_config = LightevalTaskConfig(
    name="joke_fruits",
    prompt_function=line_to_prompt,
    hf_repo="json",
    hf_subset=None,
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    hf_data_files={"test": dataset_file},
    metrics=[judge_llm_metric],
    stop_sequence=["\n\n\n"],
)
task = LightevalTask(task_config)
task.get_docs(10)

# Create a registry with the custom task for proper cache hashing
registry = Registry(tasks=None)
registry._task_registry["joke_fruits"] = task_config
registry.task_to_configs = {"joke_fruits": [task_config]}
from lighteval.logging.evaluation_tracker import EvaluationTracker

evaluation_tracker = EvaluationTracker(
    output_dir="/Users/pjavanrood/Code/Evalhub/backend/experiments/results_joke_fruits",
    save_details=True,
    push_to_hub=False,
)
from lighteval.models.endpoints.litellm_model import LiteLLMClient, LiteLLMModelConfig

model_config = LiteLLMModelConfig(
    model_name="baseten/deepseek-ai/DeepSeek-V3.2",
    base_url="https://inference.baseten.co/v1",
    api_key=BASETEN_API_KEY,
)

model = LiteLLMClient(model_config)

# Initialize the registry on the model's cache to avoid the warning
if hasattr(model, "_cache") and model._cache is not None:
    model._cache._init_registry(registry)


@dataclass
class EvaluationPipelineParameters:
    max_samples: int | None = None
    save_details: bool = True
    use_cache: bool = True


class EvaluationPipeline:
    def __init__(
        self,
        task: LightevalTask,
        evaluation_tracker: EvaluationTracker,
        model: LightevalModel,
        params: EvaluationPipelineParameters | None = None,
    ):
        self.task = task
        self.evaluation_tracker = evaluation_tracker
        self.model = model
        self.params = params or EvaluationPipelineParameters()
        if not self.params.use_cache and hasattr(self.model, "_cache"):
            self.model._cache = None

    def _run_model(self, docs: list[Doc]) -> list[ModelResponse]:
        return self.model.greedy_until(docs)

    def _compute_metrics(
        self, responses: list[ModelResponse], docs: list[Doc]
    ) -> list[dict]:
        metrics = self.task.metrics
        if not metrics:
            return [{} for _ in docs]

        outputs = [{} for _ in docs]
        metrics_with_compute = [
            m
            for m in metrics
            if hasattr(m, "compute") and callable(getattr(m, "compute"))
        ]
        metrics_without_compute = [m for m in metrics if m not in metrics_with_compute]

        if metrics_without_compute:
            metric_outputs = apply_metric(responses, docs, metrics_without_compute)
            for i, item in enumerate(metric_outputs):
                outputs[i].update(item)

        for metric in metrics_with_compute:
            metric_outputs = metric.compute(responses=responses, docs=docs)
            for i, item in enumerate(metric_outputs):
                outputs[i].update(item)

        return outputs

    def _aggregate_metrics(self, sample_metrics: list[dict]) -> dict:
        aggregated = {}
        aggregations = self.task.aggregation()
        for metric_name, agg_fn in aggregations.items():
            values = [
                item[metric_name] for item in sample_metrics if metric_name in item
            ]
            if values:
                aggregated[metric_name] = agg_fn(values)
        return aggregated

    def evaluate(self) -> dict:
        self.evaluation_tracker.general_config_logger.log_model_info(
            model_config=model.config
        )
        docs = self.task.get_docs(self.params.max_samples)
        responses = self._run_model(docs)
        sample_metrics = self._compute_metrics(responses, docs)
        aggregated = self._aggregate_metrics(sample_metrics)

        task_name = self.task.full_name
        for doc, response, metrics in zip(docs, responses, sample_metrics):
            numeric_metrics = {
                k: v for k, v in metrics.items() if isinstance(v, (int, float))
            }
            if numeric_metrics:
                self.evaluation_tracker.metrics_logger.log(task_name, numeric_metrics)
            if self.params.save_details:
                self.evaluation_tracker.details_logger.log(
                    task_name, doc, response, metrics
                )

        self.evaluation_tracker.metrics_logger.aggregate(
            task_dict={task.full_name: task}, bootstrap_iters=0
        )
        self.evaluation_tracker.details_logger.aggregate()
        return {
            "task": task_name,
            "samples": sample_metrics,
            "summary": aggregated,
        }

    def save_and_push_results(self):
        self.evaluation_tracker.save()

    def show_results(self):
        return self.evaluation_tracker.generate_final_dict()


evaluation_pipeline = EvaluationPipeline(task, evaluation_tracker, model)
_ = evaluation_pipeline.evaluate()
evaluation_pipeline.save_and_push_results()
results = evaluation_pipeline.show_results()
