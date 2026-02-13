"""Module for custom task evaluation pipeline."""

from collections.abc import Callable
from dataclasses import dataclass

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.metrics import apply_metric
from lighteval.models.abstract_model import LightevalModel
from lighteval.models.model_output import ModelResponse
from lighteval.tasks.lighteval_task import LightevalTask
from lighteval.tasks.requests import Doc

# Type alias: callback(stage, percent, detail)
ProgressCallback = Callable[[str, int | None, str], None]

# The pipeline reports 0–85%; the remaining 15% is reserved for
# post-pipeline work (S3 upload, DB writes) handled in the Celery task.
_PIPELINE_MAX_PCT = 85


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
        progress_callback: ProgressCallback | None = None,
    ):
        self.task = task
        self.evaluation_tracker = evaluation_tracker
        self.model = model
        self.params = params or CustomTaskEvaluationPipelineParameters()
        self.progress_callback = progress_callback
        if not self.params.use_cache and hasattr(self.model, "_cache"):
            self.model._cache = None

        # Work-unit tracking (set in evaluate())
        self._total_work = 1
        self._completed_work = 0

    def _pct(self) -> int:
        """Current progress mapped to 0–_PIPELINE_MAX_PCT range."""
        return int(self._completed_work / self._total_work * _PIPELINE_MAX_PCT)

    def _report(self, stage: str, detail: str = "") -> None:
        if self.progress_callback:
            self.progress_callback(stage, self._pct(), detail)

    def _run_model(self, docs: list[Doc]) -> list[ModelResponse]:
        """Run model on documents.

        When a progress_callback is set, processes docs one-by-one to report
        per-sample progress.  OpenAI API requests are sequential anyway, so
        there is no performance penalty.
        """
        if not self.progress_callback or not docs:
            return self.model.greedy_until(docs)

        total = len(docs)
        responses: list[ModelResponse] = []
        for i, doc in enumerate(docs):
            resp = self.model.greedy_until([doc])
            responses.extend(resp)
            self._completed_work = i + 1
            self._report("model_inference", f"Sample {i + 1}/{total}")
        return responses

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

        n_samples = len(docs)
        for j, metric in enumerate(metrics_with_compute):
            metric_outputs = metric.compute(responses=responses, docs=docs)
            for i, item in enumerate(metric_outputs):
                outputs[i].update(item)
            # Each compute-metric is weighted as N work units (≈ N API calls)
            self._completed_work = n_samples + (j + 1) * n_samples
            self._report(
                "computing_metrics",
                f"Metric {j + 1}/{len(metrics_with_compute)}",
            )

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
        n_samples = len(docs)

        # Estimate total work units so percentages are proportional to real work.
        # Inference = N units (one API call per sample).
        # Each compute-metric (e.g. LLM-as-judge) ≈ N units.
        # +1 unit for aggregation/logging overhead.
        metrics = self.task.metrics or []
        n_compute = len(
            [m for m in metrics if hasattr(m, "compute") and callable(getattr(m, "compute"))]
        )
        self._total_work = n_samples * (1 + n_compute) + 1
        self._completed_work = 0

        self._report("model_inference", "Starting inference...")
        responses = self._run_model(docs)

        self._report("computing_metrics", "Computing metrics...")
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

        self._completed_work = self._total_work
        self._report("aggregating", "Aggregating results...")

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
