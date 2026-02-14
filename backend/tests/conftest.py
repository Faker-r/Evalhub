"""
Pytest configuration and fixtures for EvalHub backend tests.

This module provides:
- Test database session fixtures
- Mock user authentication fixtures
- Test client for API endpoint testing
- Common test data factories
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Load environment variables for testing
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

from api.core.database import get_session
from api.core.security import CurrentUser, get_current_user
from api.main import app

# =============================================================================
# Event Loop Configuration
# =============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Test Client Fixtures
# =============================================================================


@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    """Provide a synchronous test client for simple API tests."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client for async API tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# =============================================================================
# Mock Authentication Fixtures
# =============================================================================

TEST_USER_ID = "e01da140-64b2-4ab9-b379-4f55dcaf0b22"
TEST_USER_EMAIL = "test@evalhub.com"


@pytest.fixture
def mock_current_user() -> CurrentUser:
    """Create a mock authenticated user."""
    return CurrentUser(id=TEST_USER_ID, email=TEST_USER_EMAIL)


@pytest.fixture
def authenticated_client(
    sync_client: TestClient, mock_current_user: CurrentUser
) -> TestClient:
    """Provide a test client with mocked authentication."""
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield sync_client
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_async_client(
    async_client: AsyncClient, mock_current_user: CurrentUser
) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with mocked authentication."""
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield async_client
    app.dependency_overrides.clear()


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_benchmark_data() -> dict:
    """Provide sample benchmark data for testing."""
    return {
        "id": 1,
        "dataset_name": "test_benchmark",
        "hf_repo": "test/benchmark",
        "tasks": ["test_task"],
        "description": "A test benchmark for unit testing",
        "author": "test_author",
        "downloads": 1000,
        "tags": ["test", "benchmark"],
    }


@pytest.fixture
def sample_dataset_upload() -> dict:
    """Provide sample dataset upload data."""
    return {
        "name": "test_dataset",
        "category": "testing",
        "samples": [
            {"input": "What is 2+2?", "expected": "4"},
            {"input": "What is 3+3?", "expected": "6"},
            {"input": "What is 4+4?", "expected": "8"},
        ],
    }


@pytest.fixture
def sample_guideline_data() -> dict:
    """Provide sample guideline creation data."""
    return {
        "name": "test_guideline",
        "prompt": "Evaluate if the response is helpful and accurate.",
        "category": "quality",
        "scoring_scale": "numeric",
        "scoring_scale_config": {"min_value": 1, "max_value": 5},
    }


@pytest.fixture
def sample_evaluation_request() -> dict:
    """Provide sample evaluation request data."""
    return {
        "dataset_name": "test_dataset",
        "guideline_names": ["test_guideline"],
        "model_completion_config": {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        },
        "judge_config": {
            "api_source": "standard",
            "model_name": "gpt-4o",
            "model_id": "2",
            "api_name": "gpt-4o",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        },
    }


@pytest.fixture
def sample_task_evaluation_request() -> dict:
    """Provide sample task evaluation request data."""
    return {
        "task_name": "gsm8k",
        "dataset_config": {"dataset_name": "gsm8k", "n_samples": 5, "n_fewshots": 0},
        "model_completion_config": {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        },
    }


@pytest.fixture
def sample_flexible_evaluation_request() -> dict:
    """Provide sample flexible evaluation request data."""
    return {
        "dataset_name": "test_dataset",
        "input_field": "question",
        "output_type": "text",
        "text_config": {"gold_answer_field": "answer"},
        "judge_type": "exact_match",
        "model_completion_config": {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        },
    }


# =============================================================================
# Validation Helpers
# =============================================================================


def assert_valid_json_response(response, expected_status: int = 200):
    """Assert that a response is valid JSON with expected status."""
    assert (
        response.status_code == expected_status
    ), f"Expected {expected_status}, got {response.status_code}: {response.text}"
    return response.json()


def assert_error_response(response, expected_status: int, error_contains: str = None):
    """Assert that a response is an error with expected status."""
    assert (
        response.status_code == expected_status
    ), f"Expected {expected_status}, got {response.status_code}"
    if error_contains:
        data = response.json()
        assert "detail" in data
        assert error_contains.lower() in data["detail"].lower()


# =============================================================================
# Test Evidence Collection
# =============================================================================


class TestEvidence:
    """Utility class for collecting test evidence for documentation."""

    def __init__(self):
        self.evidence = []

    def record(
        self,
        test_name: str,
        endpoint: str,
        request_data: dict,
        response_status: int,
        response_data: dict,
        notes: str = "",
    ):
        """Record test evidence."""
        self.evidence.append(
            {
                "test_name": test_name,
                "endpoint": endpoint,
                "request": request_data,
                "response_status": response_status,
                "response": response_data,
                "notes": notes,
            }
        )

    def save(self, filepath: str):
        """Save evidence to a JSON file."""
        import json

        with open(filepath, "w") as f:
            json.dump(self.evidence, f, indent=2, default=str)


@pytest.fixture
def test_evidence() -> TestEvidence:
    """Provide a test evidence collector."""
    return TestEvidence()
