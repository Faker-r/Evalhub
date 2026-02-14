"""
Unit tests for Pydantic schemas.

Tests validation logic for request/response schemas across:
- FR-1.0: Benchmark and dataset schemas
- FR-2.0: Evaluation request schemas
- FR-6.0: Authentication schemas

Test Matrix:
| Test Name                              | FR   | Schema              | Validates                    |
|----------------------------------------|------|---------------------|------------------------------|
| test_benchmark_response_schema         | FR-1 | BenchmarkResponse   | Valid benchmark data         |
| test_dataset_response_schema           | FR-1 | DatasetResponse     | Valid dataset data           |
| test_guideline_schema_boolean          | FR-1 | GuidelineCreate     | Boolean scoring scale        |
| test_guideline_schema_numeric          | FR-1 | GuidelineCreate     | Numeric scoring scale        |
| test_guideline_schema_custom_category  | FR-1 | GuidelineCreate     | Custom category scale        |
| test_guideline_schema_invalid_config   | FR-1 | GuidelineCreate     | Mismatched config rejection  |
| test_flexible_eval_request_valid       | FR-2 | FlexibleEvalRequest | Valid flexible eval request  |
| test_auth_response_schema              | FR-6 | AuthResponse        | Valid auth response          |
| test_login_data_invalid_email          | FR-6 | LoginData           | Email validation             |
"""

import pytest
from pydantic import ValidationError

from api.auth.schemas import AuthResponse, LoginData, UserCreate
from api.benchmarks.schemas import BenchmarkListResponse, BenchmarkResponse
from api.datasets.schemas import DatasetListResponse, DatasetResponse
from api.evaluations.schemas import (
    DatasetConfig,
    FlexibleEvaluationRequest,
    JudgeType,
    ModelConfig,
    MultipleChoiceConfig,
    OutputType,
    TaskEvaluationRequest,
    TextOutputConfig,
    TraceResponse,
)
from api.guidelines.schemas import (
    BooleanScaleConfig,
    CustomCategoryScaleConfig,
    GuidelineCreate,
    GuidelineResponse,
    GuidelineScoringScale,
    NumericScaleConfig,
    PercentageScaleConfig,
)

# =============================================================================
# FR-1.0: Benchmark & Dataset Schema Tests
# =============================================================================

class TestBenchmarkSchemas:
    """Tests for benchmark-related schemas (FR-1.0)."""
    
    def test_benchmark_response_schema_valid(self):
        """Test valid BenchmarkResponse creation."""
        from datetime import datetime
        
        data = {
            "id": 1,
            "tasks": ["gsm8k"],
            "dataset_name": "gsm8k",
            "hf_repo": "openai/gsm8k",
            "description": "Grade school math benchmark",
            "author": "openai",
            "downloads": 50000,
            "tags": ["math", "reasoning"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        response = BenchmarkResponse(**data)
        
        assert response.id == 1
        assert response.dataset_name == "gsm8k"
        assert response.hf_repo == "openai/gsm8k"
        assert response.tasks == ["gsm8k"]
        assert response.downloads == 50000
    
    def test_benchmark_response_optional_fields(self):
        """Test BenchmarkResponse with minimal required fields."""
        from datetime import datetime
        
        data = {
            "id": 1,
            "dataset_name": "minimal_benchmark",
            "hf_repo": "test/minimal",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        response = BenchmarkResponse(**data)
        
        assert response.id == 1
        assert response.tasks is None
        assert response.description is None
        assert response.author is None
    
    def test_benchmark_list_response_pagination(self):
        """Test BenchmarkListResponse pagination fields."""
        from datetime import datetime
        
        benchmark = {
            "id": 1,
            "dataset_name": "test",
            "hf_repo": "test/repo",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        data = {
            "benchmarks": [BenchmarkResponse(**benchmark)],
            "total": 100,
            "page": 1,
            "page_size": 10,
            "total_pages": 10,
        }
        
        response = BenchmarkListResponse(**data)
        
        assert len(response.benchmarks) == 1
        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 10
        assert response.total_pages == 10


class TestDatasetSchemas:
    """Tests for dataset-related schemas (FR-1.0)."""
    
    def test_dataset_response_schema_valid(self):
        """Test valid DatasetResponse creation."""
        data = {
            "id": 1,
            "name": "test_dataset",
            "category": "question_answering",
            "sample_count": 100,
        }
        
        response = DatasetResponse(**data)
        
        assert response.id == 1
        assert response.name == "test_dataset"
        assert response.category == "question_answering"
        assert response.sample_count == 100
    
    def test_dataset_list_response(self):
        """Test DatasetListResponse schema."""
        datasets = [
            DatasetResponse(id=1, name="ds1", category="qa", sample_count=100),
            DatasetResponse(id=2, name="ds2", category="math", sample_count=200),
        ]
        
        response = DatasetListResponse(datasets=datasets)
        
        assert len(response.datasets) == 2
        assert response.datasets[0].name == "ds1"
        assert response.datasets[1].sample_count == 200


class TestGuidelineSchemas:
    """Tests for guideline-related schemas (FR-1.0)."""
    
    def test_guideline_boolean_scoring_scale(self):
        """Test guideline with boolean scoring scale."""
        data = {
            "name": "is_helpful",
            "prompt": "Is the response helpful?",
            "category": "quality",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": BooleanScaleConfig(),
        }
        
        guideline = GuidelineCreate(**data)
        
        assert guideline.name == "is_helpful"
        assert guideline.scoring_scale == GuidelineScoringScale.BOOLEAN
        assert isinstance(guideline.scoring_scale_config, BooleanScaleConfig)
    
    def test_guideline_numeric_scoring_scale(self):
        """Test guideline with numeric scoring scale (1-5)."""
        data = {
            "name": "quality_score",
            "prompt": "Rate the quality of the response from 1 to 5.",
            "category": "quality",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": NumericScaleConfig(min_value=1, max_value=5),
        }
        
        guideline = GuidelineCreate(**data)
        
        assert guideline.scoring_scale == GuidelineScoringScale.NUMERIC
        assert guideline.scoring_scale_config.min_value == 1
        assert guideline.scoring_scale_config.max_value == 5
    
    def test_guideline_custom_category_scoring_scale(self):
        """Test guideline with custom category scoring scale."""
        data = {
            "name": "sentiment",
            "prompt": "Classify the sentiment of the response.",
            "category": "analysis",
            "scoring_scale": GuidelineScoringScale.CUSTOM_CATEGORY,
            "scoring_scale_config": CustomCategoryScaleConfig(
                categories=["positive", "neutral", "negative"]
            ),
        }
        
        guideline = GuidelineCreate(**data)
        
        assert guideline.scoring_scale == GuidelineScoringScale.CUSTOM_CATEGORY
        assert guideline.scoring_scale_config.categories == ["positive", "neutral", "negative"]
    
    def test_guideline_percentage_scoring_scale(self):
        """Test guideline with percentage scoring scale."""
        data = {
            "name": "accuracy_percentage",
            "prompt": "What percentage of the response is accurate?",
            "category": "accuracy",
            "scoring_scale": GuidelineScoringScale.PERCENTAGE,
            "scoring_scale_config": PercentageScaleConfig(),
        }
        
        guideline = GuidelineCreate(**data)
        
        assert guideline.scoring_scale == GuidelineScoringScale.PERCENTAGE
    
    def test_guideline_mismatched_config_rejected(self):
        """Test that mismatched scoring scale and config is rejected."""
        data = {
            "name": "invalid_guideline",
            "prompt": "Test prompt",
            "category": "test",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": BooleanScaleConfig(),  # Wrong config type
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GuidelineCreate(**data)
        
        assert "Numeric scale requires NumericScaleConfig" in str(exc_info.value)


# =============================================================================
# FR-2.0: Evaluation Request Schema Tests
# =============================================================================

class TestEvaluationSchemas:
    """Tests for evaluation-related schemas (FR-2.0)."""
    
    def test_model_config_valid(self):
        """Test valid ModelConfig creation."""
        data = {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        }
        
        config = ModelConfig(**data)
        
        assert config.model_name == "gpt-4o-mini"
        assert config.api_source == "standard"
        assert config.model_provider == "openai"
    
    def test_model_config_openrouter_source(self):
        """Test ModelConfig with openrouter api_source."""
        data = {
            "api_source": "openrouter",
            "model_name": "anthropic/claude-3-opus",
            "model_id": "2",
            "api_name": "anthropic/claude-3-opus",
            "model_provider": "anthropic",
            "model_provider_slug": "anthropic",
            "model_provider_id": "2",
        }
        
        config = ModelConfig(**data)
        
        assert config.api_source == "openrouter"
    
    def test_model_config_invalid_api_source(self):
        """Test that invalid api_source is rejected."""
        data = {
            "api_source": "invalid_source",  # Invalid
            "model_name": "test",
            "model_id": "1",
            "api_name": "test",
            "model_provider": "test",
            "model_provider_slug": "test",
            "model_provider_id": "1",
        }
        
        with pytest.raises(ValidationError):
            ModelConfig(**data)
    
    def test_dataset_config_valid(self):
        """Test valid DatasetConfig creation."""
        data = {
            "dataset_name": "gsm8k",
            "n_samples": 100,
            "n_fewshots": 5,
        }
        
        config = DatasetConfig(**data)
        
        assert config.dataset_name == "gsm8k"
        assert config.n_samples == 100
        assert config.n_fewshots == 5
    
    def test_dataset_config_defaults(self):
        """Test DatasetConfig with default values."""
        data = {"dataset_name": "test_dataset"}
        
        config = DatasetConfig(**data)
        
        assert config.dataset_name == "test_dataset"
        assert config.n_samples is None
        assert config.n_fewshots is None
    
    def test_task_evaluation_request_valid(self):
        """Test valid TaskEvaluationRequest creation."""
        model_config = {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        }
        
        data = {
            "task_name": "gsm8k",
            "dataset_config": {"dataset_name": "gsm8k", "n_samples": 10},
            "model_completion_config": model_config,
        }
        
        request = TaskEvaluationRequest(**data)
        
        assert request.task_name == "gsm8k"
        assert request.dataset_config.n_samples == 10
        assert request.judge_config is None  # Optional
    
    def test_flexible_evaluation_request_text_output(self):
        """Test FlexibleEvaluationRequest with text output type."""
        model_config = {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        }
        
        data = {
            "dataset_name": "custom_dataset",
            "input_field": "question",
            "output_type": OutputType.TEXT,
            "text_config": {"gold_answer_field": "answer"},
            "judge_type": JudgeType.F1_SCORE,
            "model_completion_config": model_config,
        }
        
        request = FlexibleEvaluationRequest(**data)
        
        assert request.output_type == OutputType.TEXT
        assert request.judge_type == JudgeType.F1_SCORE
        assert request.text_config.gold_answer_field == "answer"
    
    def test_flexible_evaluation_request_multiple_choice(self):
        """Test FlexibleEvaluationRequest with multiple choice output type."""
        model_config = {
            "api_source": "standard",
            "model_name": "gpt-4o-mini",
            "model_id": "1",
            "api_name": "gpt-4o-mini",
            "model_provider": "openai",
            "model_provider_slug": "openai",
            "model_provider_id": "1",
        }
        
        data = {
            "dataset_name": "mmlu",
            "input_field": "question",
            "output_type": OutputType.MULTIPLE_CHOICE,
            "mc_config": {
                "choices_field": "choices",
                "gold_answer_field": "answer"
            },
            "judge_type": JudgeType.EXACT_MATCH,
            "model_completion_config": model_config,
        }
        
        request = FlexibleEvaluationRequest(**data)
        
        assert request.output_type == OutputType.MULTIPLE_CHOICE
        assert request.mc_config.choices_field == "choices"
        assert request.judge_type == JudgeType.EXACT_MATCH


# =============================================================================
# FR-6.0: Authentication Schema Tests
# =============================================================================

class TestAuthSchemas:
    """Tests for authentication-related schemas (FR-6.0)."""
    
    def test_user_create_valid(self):
        """Test valid UserCreate schema."""
        data = {
            "email": "test@example.com",
            "password": "secure_password_123",
        }
        
        user = UserCreate(**data)
        
        assert user.email == "test@example.com"
        assert user.password == "secure_password_123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email is rejected."""
        data = {
            "email": "invalid-email",  # Not a valid email
            "password": "password123",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        # Should fail email validation
        assert "email" in str(exc_info.value).lower()
    
    def test_login_data_valid(self):
        """Test valid LoginData schema."""
        data = {
            "email": "user@test.com",
            "password": "mypassword",
        }
        
        login = LoginData(**data)
        
        assert login.email == "user@test.com"
        assert login.password == "mypassword"
    
    def test_auth_response_valid(self):
        """Test valid AuthResponse schema."""
        data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "refresh_token_value",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@test.com",
        }
        
        response = AuthResponse(**data)
        
        assert response.access_token.startswith("eyJ")
        assert response.token_type == "bearer"
        assert response.expires_in == 3600
        assert response.user_id == "550e8400-e29b-41d4-a716-446655440000"
    
    def test_auth_response_default_token_type(self):
        """Test AuthResponse default token_type."""
        data = {
            "access_token": "token",
            "refresh_token": "refresh",
            "expires_in": 3600,
            "user_id": "user-id",
            "email": "test@test.com",
        }
        
        response = AuthResponse(**data)
        
        assert response.token_type == "bearer"  # Default value


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_dataset_config_zero_samples(self):
        """Test DatasetConfig accepts zero samples."""
        config = DatasetConfig(dataset_name="test", n_samples=0)
        assert config.n_samples == 0
    
    def test_dataset_config_large_samples(self):
        """Test DatasetConfig with large sample count."""
        config = DatasetConfig(dataset_name="test", n_samples=1_000_000)
        assert config.n_samples == 1_000_000
    
    def test_numeric_scale_min_equals_max(self):
        """Test NumericScaleConfig where min equals max."""
        config = NumericScaleConfig(min_value=5, max_value=5)
        assert config.min_value == config.max_value
    
    def test_empty_guideline_categories(self):
        """Test CustomCategoryScaleConfig with empty categories list."""
        # This should be allowed by the schema (validation may happen elsewhere)
        config = CustomCategoryScaleConfig(categories=[])
        assert config.categories == []
    
    def test_benchmark_response_empty_tasks(self):
        """Test BenchmarkResponse with empty tasks list."""
        from datetime import datetime
        
        data = {
            "id": 1,
            "dataset_name": "test",
            "hf_repo": "test/repo",
            "tasks": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        response = BenchmarkResponse(**data)
        assert response.tasks == []
