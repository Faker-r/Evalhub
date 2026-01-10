import tempfile
from pathlib import Path
from lighteval.tasks.lighteval_task import LightevalTaskConfig, LightevalTask
from lighteval.tasks.requests import Doc
from lighteval.metrics import Metric


class DatasetTask:
    def __init__(self, dataset_name: str, dataset_content: str, metrics: list[Metric]):
        self.dataset_name = dataset_name
        self.dataset_content = dataset_content
        self.metrics = metrics
        self.temp_file = None

    def _create_prompt_function(self):
        """Create prompt function that converts dataset lines to Doc objects."""

        def line_to_prompt(line, _doc):
            return Doc(
                task_name=self.dataset_name,
                query=line["input"],
                choices=[],
                gold_index=0,
            )

        return line_to_prompt

    def build_lighteval_task(self) -> LightevalTask:
        """Build a LightevalTask from the dataset and metrics."""
        # Write dataset content to a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        )
        self.temp_file.write(self.dataset_content)
        self.temp_file.close()

        task_config = LightevalTaskConfig(
            name=self.dataset_name,
            prompt_function=self._create_prompt_function(),
            hf_repo="json",
            hf_subset=None,
            hf_avail_splits=["test"],
            evaluation_splits=["test"],
            hf_data_files={"test": self.temp_file.name},
            metrics=self.metrics,
            stop_sequence=["\n\n\n"],
        )

        return LightevalTask(task_config)

    def cleanup(self):
        """Remove temporary file."""
        if self.temp_file:
            Path(self.temp_file.name).unlink(missing_ok=True)
