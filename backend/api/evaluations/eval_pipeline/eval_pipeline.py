"""Module for custom task evaluation pipeline."""

from dataclasses import dataclass

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.metrics import apply_metric
from lighteval.models.abstract_model import LightevalModel
from lighteval.models.model_output import ModelResponse
from lighteval.tasks.lighteval_task import LightevalTask
from lighteval.tasks.requests import Doc


@dataclass
class CustomTaskEvaluationPipelineParameters:
    """Parameters for custom task evaluation pipeline."""

    max_samples: int | None = None
    save_details: bool = True
    use_cache: bool = True


class CustomTaskEvaluationPipeline:
    """Evaluation pipeline for running tasks with lighteval."""

    def __init__(
        self,
        task: LightevalTask,
        evaluation_tracker: EvaluationTracker,
        model: LightevalModel,
        params: CustomTaskEvaluationPipelineParameters | None = None,
    ):
        self.task = task
        self.evaluation_tracker = evaluation_tracker
        self.model = model
        self.params = params or CustomTaskEvaluationPipelineParameters()
        if not self.params.use_cache and hasattr(self.model, "_cache"):
            self.model._cache = None

    def _run_model(self, docs: list[Doc]) -> list[ModelResponse]:
        """Run model on documents."""
        return self.model.greedy_until(docs)

    def _compute_metrics(
        self, responses: list[ModelResponse], docs: list[Doc]
    ) -> list[dict]:
        """Compute metrics on model responses."""
        metrics = self.task.metrics
        if not metrics:
            return [{} for _ in docs]

        metrics_with_compute = [
            m
            for m in metrics
            if hasattr(m, "compute") and callable(getattr(m, "compute"))
        ]
        metrics_without_compute = [m for m in metrics if m not in metrics_with_compute]

        outputs = (
            apply_metric(responses, docs, metrics_without_compute)
            if metrics_without_compute
            else [{} for _ in docs]
        )

        for metric in metrics_with_compute:
            metric_outputs = metric.compute(responses=responses, docs=docs)
            for i, item in enumerate(metric_outputs):
                outputs[i].update(item)

        return outputs

    def _aggregate_metrics(self, sample_metrics: list[dict]) -> dict:
        """Aggregate sample-level metrics."""
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
        """Run evaluation pipeline."""
        self.evaluation_tracker.general_config_logger.log_model_info(
            model_config=self.model.config
        )

        docs = self.task.get_docs(self.params.max_samples)
        responses = self._run_model(docs)
        outputs = self._compute_metrics(responses, docs)

        task_name = self.task.full_name
        for output, doc, response in zip(outputs, docs, responses):
            # Only log metrics that have aggregation functions to metrics_logger
            aggregation_keys = set(self.task.aggregation().keys())
            metrics_only = {k: v for k, v in output.items() if k in aggregation_keys}

            self.evaluation_tracker.metrics_logger.log(task_name, metrics_only)
            if self.params.save_details:
                # Details logger gets the full output including metadata
                self.evaluation_tracker.details_logger.log(
                    task_name, doc, response, output
                )

        self.evaluation_tracker.metrics_logger.aggregate(
            task_dict={self.task.full_name: self.task}, bootstrap_iters=0
        )
        self.evaluation_tracker.details_logger.aggregate()

        aggregated = self._aggregate_metrics(outputs)
        scores_by_metric = {}
        for metric_name in aggregated.keys():
            scores_by_metric[metric_name] = [
                sample[metric_name] for sample in outputs if metric_name in sample
            ]

        return {
            "summary": aggregated,
            "scores": scores_by_metric,
            "sample_count": len(docs),
        }

    def save_and_push_results(self):
        """Save and push results."""
        self.evaluation_tracker.save()

    def show_results(self):
        """Show final results."""
        return self.evaluation_tracker.generate_final_dict()
