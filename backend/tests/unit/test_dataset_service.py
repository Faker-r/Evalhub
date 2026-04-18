"""Unit tests for DatasetService, focusing on _validate_and_count logic."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from api.datasets.service import VALIDATION_SAMPLE_SIZE, DatasetService


@pytest.fixture
def service():
    mock_session = AsyncMock()
    with patch("api.datasets.service.S3Storage"):
        svc = DatasetService(mock_session)
    return svc


class TestValidateAndCount:
    def test_valid_jsonl_single_line(self, service):
        content = b'{"input": "hello", "expected": "world"}\n'
        count = service._validate_and_count(content)
        assert count == 1

    def test_valid_jsonl_multiple_lines(self, service):
        lines = [json.dumps({"input": f"q{i}"}) for i in range(5)]
        content = "\n".join(lines).encode("utf-8")
        count = service._validate_and_count(content)
        assert count == 5

    def test_skips_blank_lines(self, service):
        content = b'{"input": "a"}\n\n{"input": "b"}\n\n\n'
        count = service._validate_and_count(content)
        assert count == 2

    def test_empty_file_raises(self, service):
        with pytest.raises(HTTPException) as exc_info:
            service._validate_and_count(b"")
        assert exc_info.value.status_code == 400
        assert "no valid data" in exc_info.value.detail.lower()

    def test_only_blank_lines_raises(self, service):
        with pytest.raises(HTTPException) as exc_info:
            service._validate_and_count(b"\n\n  \n")
        assert exc_info.value.status_code == 400

    def test_non_utf8_raises(self, service):
        content = b"\xff\xfe"
        with pytest.raises(HTTPException) as exc_info:
            service._validate_and_count(content)
        assert exc_info.value.status_code == 400
        assert "utf-8" in exc_info.value.detail.lower()

    def test_invalid_json_raises(self, service):
        content = b"not json at all\n"
        with pytest.raises(HTTPException) as exc_info:
            service._validate_and_count(content)
        assert exc_info.value.status_code == 400
        assert "invalid json" in exc_info.value.detail.lower()

    def test_non_object_json_raises(self, service):
        content = b'["this", "is", "an", "array"]\n'
        with pytest.raises(HTTPException) as exc_info:
            service._validate_and_count(content)
        assert exc_info.value.status_code == 400
        assert "json object" in exc_info.value.detail.lower()

    def test_beyond_validation_sample_size(self, service):
        lines = []
        for i in range(VALIDATION_SAMPLE_SIZE + 50):
            lines.append(json.dumps({"input": f"question {i}"}))
        content = "\n".join(lines).encode("utf-8")
        count = service._validate_and_count(content)
        assert count == VALIDATION_SAMPLE_SIZE + 50

    def test_missing_input_field_still_passes(self, service):
        content = b'{"text": "no input field"}\n'
        count = service._validate_and_count(content)
        assert count == 1


class TestGetDatasetByName:
    async def test_returns_dataset(self, service):
        mock_dataset = MagicMock()
        service.repository = AsyncMock()
        service.repository.get_by_name.return_value = mock_dataset

        result = await service.get_dataset_by_name("test_ds")
        assert result == mock_dataset

    async def test_not_found_raises(self, service):
        service.repository = AsyncMock()
        service.repository.get_by_name.return_value = None

        from api.core.exceptions import NotFoundException

        with pytest.raises(NotFoundException):
            await service.get_dataset_by_name("missing_ds")


class TestGetDatasetContent:
    async def test_returns_content(self, service):
        mock_dataset = MagicMock()
        mock_dataset.name = "test_ds"
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = mock_dataset
        service.s3.download_dataset.return_value = '{"input": "hello"}'

        result = await service.get_dataset_content(1)
        assert result == '{"input": "hello"}'

    async def test_file_not_found_raises(self, service):
        mock_dataset = MagicMock()
        mock_dataset.name = "test_ds"
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = mock_dataset
        service.s3.download_dataset.side_effect = FileNotFoundError("not found")

        from api.core.exceptions import NotFoundException

        with pytest.raises(NotFoundException):
            await service.get_dataset_content(1)


class TestGetDatasetPreview:
    async def test_returns_preview(self, service):
        mock_dataset = MagicMock()
        mock_dataset.name = "test_ds"
        mock_dataset.visibility = "public"
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = mock_dataset
        service.s3.download_dataset.return_value = '{"input": "q1"}\n{"input": "q2"}\n'

        result = await service.get_dataset_preview(1)
        assert len(result) == 2
        assert result[0]["input"] == "q1"

    async def test_skips_invalid_json_lines(self, service):
        mock_dataset = MagicMock()
        mock_dataset.name = "test_ds"
        mock_dataset.visibility = "public"
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = mock_dataset
        service.s3.download_dataset.return_value = (
            '{"input": "q1"}\nnot_json\n{"input": "q2"}\n'
        )

        result = await service.get_dataset_preview(1)
        assert len(result) == 2

    async def test_error_raises_500(self, service):
        mock_dataset = MagicMock()
        mock_dataset.name = "test_ds"
        mock_dataset.visibility = "public"
        service.repository = AsyncMock()
        service.repository.get_by_id.return_value = mock_dataset
        service.s3.download_dataset.side_effect = RuntimeError("S3 down")

        with pytest.raises(HTTPException) as exc_info:
            await service.get_dataset_preview(1)
        assert exc_info.value.status_code == 500
