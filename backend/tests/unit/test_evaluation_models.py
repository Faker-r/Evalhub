"""Unit tests for Trace model properties."""

from unittest.mock import MagicMock


class TestTraceProperties:
    def _make_trace(self, completion_config=None, judge_config=None):
        from api.evaluations.models import Trace

        trace = MagicMock(spec=Trace)
        trace.completion_model_config = completion_config
        trace.judge_model_config = judge_config
        trace.completion_model = Trace.completion_model.fget(trace)
        trace.model_provider = Trace.model_provider.fget(trace)
        trace.judge_model = Trace.judge_model.fget(trace)
        trace.judge_model_provider = Trace.judge_model_provider.fget(trace)
        return trace

    def test_completion_model(self):
        trace = self._make_trace(
            completion_config={"api_name": "gpt-4o", "provider_slug": "openai"}
        )
        assert trace.completion_model == "gpt-4o"

    def test_completion_model_none_config(self):
        trace = self._make_trace(completion_config=None)
        assert trace.completion_model == ""

    def test_model_provider(self):
        trace = self._make_trace(
            completion_config={"api_name": "gpt-4o", "provider_slug": "openai"}
        )
        assert trace.model_provider == "openai"

    def test_model_provider_none_config(self):
        trace = self._make_trace(completion_config=None)
        assert trace.model_provider == ""

    def test_judge_model(self):
        trace = self._make_trace(
            judge_config={"api_name": "gpt-4o", "provider_slug": "openai"}
        )
        assert trace.judge_model == "gpt-4o"

    def test_judge_model_none_config(self):
        trace = self._make_trace(judge_config=None)
        assert trace.judge_model == ""

    def test_judge_model_provider(self):
        trace = self._make_trace(
            judge_config={"api_name": "gpt-4o", "provider_slug": "openai"}
        )
        assert trace.judge_model_provider == "openai"

    def test_judge_model_provider_none_config(self):
        trace = self._make_trace(judge_config=None)
        assert trace.judge_model_provider == ""
