"""Unit tests for S3Storage with mocked boto3 client."""

import os
from unittest.mock import MagicMock, call, patch

import pytest
from botocore.exceptions import ClientError

from api.core.s3 import (
    API_KEYS_PREFIX,
    DATASETS_PREFIX,
    EVAL_RESULTS_PREFIX,
    TRACES_PREFIX,
    S3Storage,
    get_s3_client,
)


@pytest.fixture
def mock_s3_client():
    with patch("api.core.s3.get_s3_client") as mock_factory:
        client = MagicMock()
        mock_factory.return_value = client
        yield client


@pytest.fixture
def storage(mock_s3_client):
    s = S3Storage()
    return s


def _client_error(code="InternalError"):
    return ClientError(
        {"Error": {"Code": code, "Message": "test"}}, "operation"
    )


# ==================== Dataset Methods ====================


class TestUploadDataset:
    def test_upload_dataset_string(self, storage, mock_s3_client):
        storage.upload_dataset("my_data", '{"input": "hello"}')
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=storage.bucket,
            Key=f"{DATASETS_PREFIX}/my_data.jsonl",
            Body=b'{"input": "hello"}',
            ContentType="application/jsonl",
        )

    def test_upload_dataset_with_extension(self, storage, mock_s3_client):
        storage.upload_dataset("my_data.jsonl", "content")
        mock_s3_client.put_object.assert_called_once()
        key = mock_s3_client.put_object.call_args.kwargs["Key"]
        assert key == f"{DATASETS_PREFIX}/my_data.jsonl"

    def test_upload_dataset_error(self, storage, mock_s3_client):
        mock_s3_client.put_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.upload_dataset("test", "content")


class TestUploadDatasetFile:
    def test_upload_dataset_file(self, storage, mock_s3_client):
        file_obj = MagicMock()
        storage.upload_dataset_file("data", file_obj)
        mock_s3_client.upload_fileobj.assert_called_once_with(
            file_obj,
            storage.bucket,
            f"{DATASETS_PREFIX}/data.jsonl",
            ExtraArgs={"ContentType": "application/jsonl"},
        )

    def test_upload_dataset_file_error(self, storage, mock_s3_client):
        mock_s3_client.upload_fileobj.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.upload_dataset_file("data", MagicMock())


class TestDownloadDataset:
    def test_download_dataset(self, storage, mock_s3_client):
        body = MagicMock()
        body.read.return_value = b'{"input": "test"}'
        mock_s3_client.get_object.return_value = {"Body": body}

        result = storage.download_dataset("my_data")
        assert result == '{"input": "test"}'

    def test_download_dataset_not_found(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("NoSuchKey")
        with pytest.raises(FileNotFoundError, match="Dataset not found"):
            storage.download_dataset("missing")

    def test_download_dataset_other_error(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("AccessDenied")
        with pytest.raises(ClientError):
            storage.download_dataset("test")


class TestDeleteDataset:
    def test_delete_dataset(self, storage, mock_s3_client):
        storage.delete_dataset("my_data")
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=storage.bucket,
            Key=f"{DATASETS_PREFIX}/my_data.jsonl",
        )

    def test_delete_dataset_error(self, storage, mock_s3_client):
        mock_s3_client.delete_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.delete_dataset("test")


# ==================== API Key Methods ====================


class TestUploadApiKey:
    def test_upload_api_key(self, storage, mock_s3_client):
        storage.upload_api_key("user-123", "openai", "sk-abc")
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=storage.bucket,
            Key=f"{API_KEYS_PREFIX}/user-123/openai.txt",
            Body=b"sk-abc",
            ContentType="text/plain",
        )

    def test_upload_api_key_error(self, storage, mock_s3_client):
        mock_s3_client.put_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.upload_api_key("user", "provider", "key")


class TestDownloadApiKey:
    def test_download_api_key(self, storage, mock_s3_client):
        body = MagicMock()
        body.read.return_value = b"sk-secret"
        mock_s3_client.get_object.return_value = {"Body": body}

        result = storage.download_api_key("user-123", "openai")
        assert result == "sk-secret"

    def test_download_api_key_not_found(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("NoSuchKey")
        with pytest.raises(FileNotFoundError, match="API key not found"):
            storage.download_api_key("user", "openai")

    def test_download_api_key_other_error(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("AccessDenied")
        with pytest.raises(ClientError):
            storage.download_api_key("user", "openai")


class TestDeleteApiKey:
    def test_delete_api_key(self, storage, mock_s3_client):
        storage.delete_api_key("user-123", "openai")
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=storage.bucket,
            Key=f"{API_KEYS_PREFIX}/user-123/openai.txt",
        )

    def test_delete_api_key_error(self, storage, mock_s3_client):
        mock_s3_client.delete_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.delete_api_key("user", "openai")


class TestApiKeyExists:
    def test_api_key_exists_true(self, storage, mock_s3_client):
        mock_s3_client.head_object.return_value = {}
        assert storage.api_key_exists("user-123", "openai") is True

    def test_api_key_exists_false(self, storage, mock_s3_client):
        mock_s3_client.head_object.side_effect = _client_error("404")
        assert storage.api_key_exists("user-123", "openai") is False


class TestListUserApiKeys:
    def test_list_user_api_keys(self, storage, mock_s3_client):
        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": f"{API_KEYS_PREFIX}/user-123/openai.txt"},
                {"Key": f"{API_KEYS_PREFIX}/user-123/anthropic.txt"},
            ]
        }
        result = storage.list_user_api_keys("user-123")
        assert result == ["openai", "anthropic"]

    def test_list_user_api_keys_empty(self, storage, mock_s3_client):
        mock_s3_client.list_objects_v2.return_value = {}
        result = storage.list_user_api_keys("user-123")
        assert result == []

    def test_list_user_api_keys_error(self, storage, mock_s3_client):
        mock_s3_client.list_objects_v2.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.list_user_api_keys("user-123")


# ==================== Trace Methods ====================


class TestUploadTrace:
    def test_upload_trace(self, storage, mock_s3_client):
        storage.upload_trace("trace-001", '{"event": "start"}')
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=storage.bucket,
            Key=f"{TRACES_PREFIX}/trace-001.jsonl",
            Body=b'{"event": "start"}',
            ContentType="application/jsonl",
        )

    def test_upload_trace_error(self, storage, mock_s3_client):
        mock_s3_client.put_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.upload_trace("trace", "content")


class TestDownloadTrace:
    def test_download_trace(self, storage, mock_s3_client):
        body = MagicMock()
        body.read.return_value = b'{"event": "done"}'
        mock_s3_client.get_object.return_value = {"Body": body}

        result = storage.download_trace("trace-001")
        assert result == '{"event": "done"}'

    def test_download_trace_not_found(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("NoSuchKey")
        with pytest.raises(FileNotFoundError, match="Trace not found"):
            storage.download_trace("missing")

    def test_download_trace_other_error(self, storage, mock_s3_client):
        mock_s3_client.get_object.side_effect = _client_error("AccessDenied")
        with pytest.raises(ClientError):
            storage.download_trace("trace")


# ==================== Eval Results Methods ====================


class TestUploadEvalResults:
    def test_upload_eval_results(self, storage, mock_s3_client, tmp_path):
        subdir = tmp_path / "results"
        subdir.mkdir()
        (subdir / "file1.json").write_text('{"result": 1}')
        (subdir / "file2.json").write_text('{"result": 2}')

        result = storage.upload_eval_results(42, str(subdir))
        assert result == f"{EVAL_RESULTS_PREFIX}/42"
        assert mock_s3_client.put_object.call_count == 2

    def test_upload_eval_results_error(self, storage, mock_s3_client, tmp_path):
        subdir = tmp_path / "results"
        subdir.mkdir()
        (subdir / "file.json").write_text("{}")
        mock_s3_client.put_object.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.upload_eval_results(1, str(subdir))


class TestListFiles:
    def test_list_files(self, storage, mock_s3_client):
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Contents": [{"Key": "file1.json"}, {"Key": "file2.json"}]},
            {"Contents": [{"Key": "file3.json"}]},
        ]
        mock_s3_client.get_paginator.return_value = paginator

        result = storage.list_files("prefix/")
        assert result == ["file1.json", "file2.json", "file3.json"]

    def test_list_files_empty(self, storage, mock_s3_client):
        paginator = MagicMock()
        paginator.paginate.return_value = [{}]
        mock_s3_client.get_paginator.return_value = paginator

        result = storage.list_files("prefix/")
        assert result == []

    def test_list_files_error(self, storage, mock_s3_client):
        paginator = MagicMock()
        paginator.paginate.side_effect = _client_error()
        mock_s3_client.get_paginator.return_value = paginator
        with pytest.raises(ClientError):
            storage.list_files("prefix/")


class TestDownloadFile:
    def test_download_file(self, storage, mock_s3_client):
        storage.download_file("key.json", "/tmp/local.json")
        mock_s3_client.download_file.assert_called_once_with(
            storage.bucket, "key.json", "/tmp/local.json"
        )

    def test_download_file_error(self, storage, mock_s3_client):
        mock_s3_client.download_file.side_effect = _client_error()
        with pytest.raises(ClientError):
            storage.download_file("key.json", "/tmp/local.json")
