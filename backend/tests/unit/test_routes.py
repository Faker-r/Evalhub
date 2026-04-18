"""Unit tests for all route handlers via TestClient with dependency overrides."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.core.database import get_session
from api.core.security import CurrentUser, get_current_user
from api.datasets.schemas import DatasetVisibility
from api.guidelines.schemas import GuidelineScoringScale, GuidelineVisibility
from api.main import app

_PROVIDER_ID = "11111111-1111-1111-1111-111111111111"
_MODEL_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def _std_eval_model_config() -> dict:
    """Minimal valid EvaluationModelConfig (standard) payload for route tests."""
    return {
        "api_source": "standard",
        "model": {
            "id": "m-1",
            "display_name": "GPT-4o",
            "developer": "OpenAI",
            "api_name": "gpt-4o",
            "providers": [
                {
                    "id": "p-1",
                    "name": "openai",
                    "slug": "openai",
                    "base_url": "https://api.openai.com/v1",
                }
            ],
        },
        "provider": {
            "id": "p-1",
            "name": "openai",
            "slug": "openai",
            "base_url": "https://api.openai.com/v1",
        },
    }


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_user():
    return CurrentUser(id="user-uuid-123", email="test@evalhub.com")


@pytest.fixture
def client(mock_session, mock_user):
    async def override_session():
        yield mock_session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ==================== Auth Routes ====================


class TestAuthRoutes:
    @patch("api.auth.routes.AuthService")
    def test_register(self, MockService, client):
        from api.auth.schemas import AuthResponse

        mock_svc = MockService.return_value
        mock_svc.register = AsyncMock(
            return_value=AuthResponse(
                access_token="access",
                refresh_token="refresh",
                expires_in=3600,
                user_id="uid",
                email="test@test.com",
            )
        )
        resp = client.post(
            "/api/auth/register", json={"email": "test@test.com", "password": "pw123"}
        )
        assert resp.status_code == 201

    @patch("api.auth.routes.AuthService")
    def test_login(self, MockService, client):
        from api.auth.schemas import AuthResponse

        mock_svc = MockService.return_value
        mock_svc.login = AsyncMock(
            return_value=AuthResponse(
                access_token="access",
                refresh_token="refresh",
                expires_in=3600,
                user_id="uid",
                email="test@test.com",
            )
        )
        resp = client.post(
            "/api/auth/login", json={"email": "test@test.com", "password": "pw123"}
        )
        assert resp.status_code == 200

    @patch("api.auth.routes.AuthService")
    def test_refresh(self, MockService, client):
        from api.auth.schemas import AuthResponse

        mock_svc = MockService.return_value
        mock_svc.refresh_token = AsyncMock(
            return_value=AuthResponse(
                access_token="new_access",
                refresh_token="new_refresh",
                expires_in=3600,
                user_id="uid",
                email="test@test.com",
            )
        )
        resp = client.post("/api/auth/refresh", json={"refresh_token": "old_token"})
        assert resp.status_code == 200

    @patch("api.auth.routes.AuthService")
    def test_logout(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.logout = AsyncMock(return_value=None)
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 204


# ==================== Users Routes ====================


class TestUsersRoutes:
    def test_get_me(self, client):
        resp = client.get("/api/users/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@evalhub.com"

    @patch("api.users.routes.UserService")
    def test_add_api_key(self, MockService, client):
        from api.users.schemas import ApiKeyResponse

        mock_svc = MockService.return_value
        mock_svc.create_api_key = AsyncMock(
            return_value=ApiKeyResponse(
                provider_id=_PROVIDER_ID,
                provider_name="openai",
            )
        )
        resp = client.post(
            "/api/users/api-keys",
            json={"provider_id": _PROVIDER_ID, "api_key": "sk-abc"},
        )
        assert resp.status_code == 201

    @patch("api.users.routes.UserService")
    def test_list_api_keys(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.list_api_keys = AsyncMock(return_value=[])
        resp = client.get("/api/users/api-keys")
        assert resp.status_code == 200

    @patch("api.users.routes.UserService")
    def test_delete_api_key(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.delete_api_key = AsyncMock(return_value=None)
        resp = client.delete("/api/users/api-keys/1")
        assert resp.status_code == 204


# ==================== Guidelines Routes ====================


class TestGuidelinesRoutes:
    @patch("api.guidelines.routes.GuidelineService")
    def test_add_guideline(self, MockService, client):
        from api.guidelines.schemas import GuidelineResponse

        mock_svc = MockService.return_value
        mock_svc.create_guideline = AsyncMock(
            return_value=GuidelineResponse(
                id=1,
                name="test_g",
                prompt="Is it good?",
                category="quality",
                scoring_scale=GuidelineScoringScale.BOOLEAN,
                scoring_scale_config={},
                visibility=GuidelineVisibility.PUBLIC,
                user_id=None,
            )
        )
        resp = client.post(
            "/api/guidelines",
            json={
                "name": "test_g",
                "prompt": "Is it good?",
                "category": "quality",
                "scoring_scale": "boolean",
                "scoring_scale_config": {},
            },
        )
        assert resp.status_code == 201

    @patch("api.guidelines.routes.GuidelineService")
    def test_get_guidelines(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.get_all_guidelines = AsyncMock(return_value=[])
        resp = client.get("/api/guidelines")
        assert resp.status_code == 200


# ==================== Datasets Routes ====================


class TestDatasetsRoutes:
    @patch("api.datasets.routes.DatasetService")
    def test_get_datasets(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.get_all_datasets = AsyncMock(return_value=[])
        resp = client.get("/api/datasets")
        assert resp.status_code == 200

    @patch("api.datasets.routes.DatasetService")
    def test_get_dataset_preview(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.get_dataset_preview = AsyncMock(return_value=[])
        resp = client.get("/api/datasets/1/preview")
        assert resp.status_code == 200

    @patch("api.datasets.routes.DatasetService")
    def test_add_dataset(self, MockService, client):
        from api.datasets.schemas import DatasetResponse

        mock_svc = MockService.return_value
        mock_svc.create_dataset = AsyncMock(
            return_value=DatasetResponse(
                id=1,
                name="test_ds",
                category="general",
                sample_count=10,
                visibility=DatasetVisibility.PUBLIC,
                user_id=None,
            )
        )
        import io

        file_content = b'{"input": "hello"}\n'
        resp = client.post(
            "/api/datasets",
            data={"name": "test_ds", "category": "general"},
            files={
                "file": ("test.jsonl", io.BytesIO(file_content), "application/jsonl")
            },
        )
        assert resp.status_code == 201


# ==================== Models and Providers Routes ====================


class TestModelsAndProvidersRoutes:
    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_create_provider(self, MockService, client):
        from api.models_and_providers.schemas import ProviderResponse

        mock_svc = MockService.return_value
        mock_svc.create_provider = AsyncMock(
            return_value=ProviderResponse(
                id=_PROVIDER_ID,
                name="openai",
                slug="openai",
                base_url="https://api.openai.com/v1",
            )
        )
        resp = client.post(
            "/api/models-and-providers/providers",
            json={
                "name": "openai",
                "slug": "openai",
                "base_url": "https://api.openai.com/v1",
            },
        )
        assert resp.status_code == 201

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_list_providers(self, MockService, client):
        from api.models_and_providers.schemas import ProviderListResponse

        mock_svc = MockService.return_value
        mock_svc.list_providers = AsyncMock(
            return_value=ProviderListResponse(
                providers=[], total=0, page=1, page_size=50
            )
        )
        resp = client.get("/api/models-and-providers/providers")
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_get_provider(self, MockService, client):
        from api.models_and_providers.schemas import ProviderResponse

        mock_svc = MockService.return_value
        mock_svc.get_provider = AsyncMock(
            return_value=ProviderResponse(
                id=_PROVIDER_ID,
                name="openai",
                slug="openai",
                base_url="https://api.openai.com/v1",
            )
        )
        resp = client.get(f"/api/models-and-providers/providers/{_PROVIDER_ID}")
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_get_provider_by_name(self, MockService, client):
        from api.models_and_providers.schemas import ProviderResponse

        mock_svc = MockService.return_value
        mock_svc.get_provider_by_name = AsyncMock(
            return_value=ProviderResponse(
                id=_PROVIDER_ID,
                name="openai",
                slug="openai",
                base_url="https://api.openai.com/v1",
            )
        )
        resp = client.get("/api/models-and-providers/providers/by-name/openai")
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_update_provider(self, MockService, client):
        from api.models_and_providers.schemas import ProviderResponse

        mock_svc = MockService.return_value
        mock_svc.update_provider = AsyncMock(
            return_value=ProviderResponse(
                id=_PROVIDER_ID,
                name="updated",
                slug="openai",
                base_url="https://api.openai.com/v1",
            )
        )
        resp = client.put(
            f"/api/models-and-providers/providers/{_PROVIDER_ID}",
            json={"name": "updated"},
        )
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_delete_provider(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.delete_provider = AsyncMock(return_value=None)
        resp = client.delete(f"/api/models-and-providers/providers/{_PROVIDER_ID}")
        assert resp.status_code == 204

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_create_model(self, MockService, client):
        from api.models_and_providers.schemas import ModelResponse

        mock_svc = MockService.return_value
        mock_svc.create_model = AsyncMock(
            return_value=ModelResponse(
                id=_MODEL_ID,
                display_name="GPT-4o",
                developer="OpenAI",
                api_name="gpt-4o",
                providers=[],
            )
        )
        resp = client.post(
            "/api/models-and-providers/models",
            json={
                "display_name": "GPT-4o",
                "developer": "OpenAI",
                "api_name": "gpt-4o",
                "provider_ids": [_PROVIDER_ID],
            },
        )
        assert resp.status_code == 201

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_list_models(self, MockService, client):
        from api.models_and_providers.schemas import ModelListResponse

        mock_svc = MockService.return_value
        mock_svc.list_models = AsyncMock(
            return_value=ModelListResponse(models=[], total=0, page=1, page_size=50)
        )
        resp = client.get("/api/models-and-providers/models")
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_get_model(self, MockService, client):
        from api.models_and_providers.schemas import ModelResponse

        mock_svc = MockService.return_value
        mock_svc.get_model = AsyncMock(
            return_value=ModelResponse(
                id=_MODEL_ID,
                display_name="GPT-4o",
                developer="OpenAI",
                api_name="gpt-4o",
                providers=[],
            )
        )
        resp = client.get(f"/api/models-and-providers/models/{_MODEL_ID}")
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_update_model(self, MockService, client):
        from api.models_and_providers.schemas import ModelResponse

        mock_svc = MockService.return_value
        mock_svc.update_model = AsyncMock(
            return_value=ModelResponse(
                id=_MODEL_ID,
                display_name="Updated",
                developer="OpenAI",
                api_name="gpt-4o",
                providers=[],
            )
        )
        resp = client.put(
            f"/api/models-and-providers/models/{_MODEL_ID}",
            json={"display_name": "Updated"},
        )
        assert resp.status_code == 200

    @patch("api.models_and_providers.routes.ModelsAndProvidersService")
    def test_delete_model(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.delete_model = AsyncMock(return_value=None)
        resp = client.delete(f"/api/models-and-providers/models/{_MODEL_ID}")
        assert resp.status_code == 204


# ==================== Evaluations Routes ====================


class TestEvaluationsRoutes:
    @patch("api.evaluations.routes.EvaluationService")
    def test_run_task_evaluation(self, MockService, client):
        from api.evaluations.schemas import TaskEvaluationResponse

        mock_svc = MockService.return_value
        mock_svc.run_task_evaluation = AsyncMock(
            return_value=TaskEvaluationResponse(
                trace_id=1,
                status="running",
                task_name="gsm8k",
                sample_count=0,
                guideline_names=[],
                completion_model="gpt-4o",
                model_provider="openai",
                judge_model="",
                created_at=datetime(2025, 1, 1),
            )
        )
        resp = client.post(
            "/api/evaluations/tasks",
            json={
                "task_name": "gsm8k",
                "dataset_config": {"dataset_name": "gsm8k", "n_samples": 5},
                "model_completion_config": _std_eval_model_config(),
            },
        )
        assert resp.status_code == 201

    @patch("api.evaluations.routes.EvaluationService")
    def test_run_flexible_evaluation(self, MockService, client):
        from api.evaluations.schemas import TaskEvaluationResponse

        mock_svc = MockService.return_value
        mock_svc.run_flexible_evaluation = AsyncMock(
            return_value=TaskEvaluationResponse(
                trace_id=1,
                status="running",
                task_name="ds",
                sample_count=0,
                guideline_names=["exact_match"],
                completion_model="gpt-4o",
                model_provider="openai",
                judge_model="",
                created_at=datetime(2025, 1, 1),
            )
        )
        resp = client.post(
            "/api/evaluations/flexible",
            json={
                "dataset_name": "ds",
                "input_field": "question",
                "output_type": "text",
                "judge_type": "exact_match",
                "model_completion_config": _std_eval_model_config(),
            },
        )
        assert resp.status_code == 201

    @patch("api.evaluations.routes.EvaluationService")
    def test_get_traces(self, MockService, client):
        mock_svc = MockService.return_value
        mock_svc.get_traces = AsyncMock(return_value=([], 0, {}))
        resp = client.get("/api/evaluations/traces")
        assert resp.status_code == 200

    @patch("api.evaluations.routes.EvaluationService")
    def test_get_trace(self, MockService, client):
        from api.evaluations.schemas import TraceResponse

        mock_svc = MockService.return_value
        mock_svc.get_trace = AsyncMock(
            return_value=TraceResponse(
                id=1,
                user_id="user-uuid-123",
                dataset_name="ds",
                guideline_names=["g1"],
                completion_model="gpt-4o",
                model_provider="openai",
                judge_model="gpt-4o",
                judge_model_provider="openai",
                status="completed",
                summary=None,
                created_at=datetime(2025, 1, 1),
            )
        )
        resp = client.get("/api/evaluations/traces/1")
        assert resp.status_code == 200

    @patch("api.evaluations.routes.EvaluationService")
    def test_get_trace_details(self, MockService, client):
        from api.evaluations.schemas import TraceDetailsResponse

        mock_svc = MockService.return_value
        mock_svc.get_trace_details = AsyncMock(
            return_value=TraceDetailsResponse(
                trace_id=1,
                status="completed",
                created_at=datetime(2025, 1, 1),
                judge_model_provider="openai",
                spec={"dataset_name": "ds"},
            )
        )
        resp = client.get("/api/evaluations/trace-details/1")
        assert resp.status_code == 200

    @patch("api.evaluations.routes.EvaluationService")
    def test_get_trace_samples(self, MockService, client):
        from api.evaluations.schemas import TraceSamplesResponse

        mock_svc = MockService.return_value
        mock_svc.get_trace_samples = AsyncMock(
            return_value=TraceSamplesResponse(samples=[])
        )
        resp = client.get("/api/evaluations/traces/1/samples?n_samples=3")
        assert resp.status_code == 200


# ==================== Benchmarks Routes ====================


class TestBenchmarksRoutes:
    @patch("api.benchmarks.routes.BenchmarkService")
    def test_get_benchmarks(self, MockService, client):
        from api.benchmarks.schemas import BenchmarkListResponse

        mock_svc = MockService.return_value
        mock_svc.get_all_benchmarks = AsyncMock(
            return_value=BenchmarkListResponse(
                benchmarks=[], total=0, page=1, page_size=50, total_pages=0
            )
        )
        resp = client.get("/api/benchmarks")
        assert resp.status_code == 200

    @patch("api.benchmarks.routes.BenchmarkService")
    def test_get_task_details(self, MockService, client):
        from api.benchmarks.schemas import TaskDetailsResponse

        mock_svc = MockService.return_value
        mock_svc.get_task_details = AsyncMock(
            return_value=TaskDetailsResponse(
                task_name="gsm8k", task_details_nested_dict={"name": "gsm8k"}
            )
        )
        resp = client.get("/api/benchmarks/task-details/gsm8k")
        assert resp.status_code == 200

    @patch("api.benchmarks.routes.BenchmarkService")
    def test_get_benchmark(self, MockService, client):
        from api.benchmarks.schemas import BenchmarkResponse

        mock_svc = MockService.return_value
        mock_svc.get_benchmark = AsyncMock(
            return_value=BenchmarkResponse(
                id=1,
                dataset_name="bench",
                hf_repo="test/repo",
                tasks=["t1"],
                repo_type="dataset",
                description="test",
                author="author",
                created_at=datetime(2025, 1, 1),
                updated_at=datetime(2025, 1, 1),
            )
        )
        resp = client.get("/api/benchmarks/1")
        assert resp.status_code == 200

    @patch("api.benchmarks.routes.BenchmarkService")
    def test_get_benchmark_tasks(self, MockService, client):
        from api.benchmarks.schemas import BenchmarkTasksListResponse

        mock_svc = MockService.return_value
        mock_svc.get_benchmark_tasks = AsyncMock(
            return_value=BenchmarkTasksListResponse(tasks=[])
        )
        resp = client.get("/api/benchmarks/1/tasks")
        assert resp.status_code == 200


# ==================== Leaderboard Routes ====================


class TestLeaderboardRoutes:
    @patch("api.leaderboard.routes.LeaderboardService")
    def test_get_leaderboard(self, MockService, client):
        from api.leaderboard.schemas import LeaderboardResponse

        mock_svc = MockService.return_value
        mock_svc.get_leaderboard = AsyncMock(
            return_value=LeaderboardResponse(datasets=[])
        )
        resp = client.get("/api/leaderboard")
        assert resp.status_code == 200


# ==================== Evaluation Comparison Routes ====================


class TestEvaluationComparisonRoutes:
    @patch("api.evaluation_comparison.routes.EvaluationComparisonService")
    def test_overlapping_datasets(self, MockService, client):
        from api.evaluation_comparison.schemas import OverlappingDatasetsResult

        mock_svc = MockService.return_value
        mock_svc.get_overlapping_datasets = AsyncMock(
            return_value=OverlappingDatasetsResult(count=0, dataset_names=[])
        )
        resp = client.post(
            "/api/evaluation-comparison/overlapping-datasets",
            json={"model_provider_pairs": [{"model": "gpt-4o", "provider": "openai"}]},
        )
        assert resp.status_code == 200

    @patch("api.evaluation_comparison.routes.EvaluationComparisonService")
    def test_side_by_side_report(self, MockService, client):
        from api.evaluation_comparison.schemas import SideBySideReportResult

        mock_svc = MockService.return_value
        mock_svc.generate_side_by_side_report = AsyncMock(
            return_value=SideBySideReportResult(entries=[], spec_by_trace={})
        )
        resp = client.post(
            "/api/evaluation-comparison/side-by-side-report",
            json={"model_provider_pairs": [{"model": "gpt-4o", "provider": "openai"}]},
        )
        assert resp.status_code == 200
