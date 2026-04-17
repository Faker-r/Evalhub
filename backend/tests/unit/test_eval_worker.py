"""Unit tests for eval_worker._create_model_config."""

from unittest.mock import MagicMock, patch

import pytest

from api.evaluations.eval_worker import _create_model_config


class TestCreateModelConfig:
    @patch("api.evaluations.eval_worker.OpenAICompatibleModelConfig")
    def test_standard_config(self, MockConfig):
        data = {
            "model_name": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-abc123",
        }
        _create_model_config(data)
        MockConfig.assert_called_once_with(
            model_name="gpt-4o",
            base_url="https://api.openai.com/v1",
            api_key="sk-abc123",
        )

    @patch("api.evaluations.eval_worker.GenerationParameters")
    @patch("api.evaluations.eval_worker.OpenAICompatibleModelConfig")
    def test_config_with_extra_body(self, MockConfig, MockGenParams):
        data = {
            "model_name": "anthropic/claude-3",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": "or-key",
            "extra_body": {"provider": {"order": ["anthropic"]}},
        }
        _create_model_config(data)
        MockGenParams.assert_called_once_with(
            extra_body={"provider": {"order": ["anthropic"]}}
        )
        assert MockConfig.call_count == 1
        call_kwargs = MockConfig.call_args.kwargs
        assert call_kwargs["model_name"] == "anthropic/claude-3"

    @patch("api.evaluations.eval_worker.OpenAICompatibleModelConfig")
    def test_empty_extra_body(self, MockConfig):
        data = {
            "model_name": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-key",
            "extra_body": {},
        }
        _create_model_config(data)
        # empty dict is falsy so standard path
        MockConfig.assert_called_once_with(
            model_name="gpt-4o",
            base_url="https://api.openai.com/v1",
            api_key="sk-key",
        )
