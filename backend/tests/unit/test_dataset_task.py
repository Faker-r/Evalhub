"""Unit tests for DatasetTask."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.evaluations.eval_pipeline.dataset_task import DatasetTask


class TestDatasetTask:
    def test_create_prompt_function(self):
        task = DatasetTask("test_ds", "", [])
        fn = task._create_prompt_function()

        line = {"input": "What is AI?"}
        doc = fn(line, None)
        assert doc.query == "What is AI?"
        assert doc.task_name == "test_ds"
        assert doc.choices == []
        assert doc.gold_index == 0

    @patch("api.evaluations.eval_pipeline.dataset_task.LightevalTask")
    def test_build_lighteval_task(self, MockTask):
        content = '{"input": "hello"}\n{"input": "world"}\n'
        task = DatasetTask("ds", content, [MagicMock()])
        MockTask.return_value = MagicMock()

        result = task.build_lighteval_task()
        MockTask.assert_called_once()
        assert task.temp_file is not None

        config_call = MockTask.call_args[0][0]
        assert config_call.name == "ds"
        task.cleanup()

    def test_cleanup_removes_file(self):
        task = DatasetTask("ds", "", [])
        task.temp_file = MagicMock()
        path = tempfile.mktemp(suffix=".jsonl")
        Path(path).write_text("test")
        task.temp_file.name = path

        task.cleanup()
        assert not Path(path).exists()

    def test_cleanup_no_file(self):
        task = DatasetTask("ds", "", [])
        task.cleanup()  # should not raise
