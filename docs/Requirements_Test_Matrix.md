# EvalHub Requirements → Test Traceability Matrix

**Version:** 1.0  
**Date:** February 4, 2026  
**Purpose:** Quick reference for requirement-to-test mapping

---

## Functional Requirements (FR)

### FR-1.0: Benchmark Dataset & Guidelines

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-1.1 | List benchmarks with pagination | FR-1.1-INT-001 | `test_benchmarks_list_returns_paginated_response` | `test_api_endpoints.py` | 47 |
| FR-1.1 | List benchmarks with pagination | FR-1.1-INT-002 | `test_benchmarks_list_pagination_parameters` | `test_api_endpoints.py` | 67 |
| FR-1.2 | Sort benchmarks by downloads | FR-1.2-INT-001 | `test_benchmarks_list_sorting_by_downloads` | `test_api_endpoints.py` | 82 |
| FR-1.2 | Filter benchmarks by search | FR-1.2-INT-002 | `test_benchmarks_list_search_filter` | `test_api_endpoints.py` | 100 |
| FR-1.3 | Get benchmark by ID | FR-1.3-INT-001 | `test_benchmark_get_by_id` | `test_api_endpoints.py` | 113 |
| FR-1.4 | 404 for missing benchmark | FR-1.4-INT-001 | `test_benchmark_not_found_returns_404` | `test_api_endpoints.py` | 133 |
| FR-1.5 | Get benchmark tasks | FR-1.5-INT-001 | `test_benchmark_tasks_endpoint` | `test_api_endpoints.py` | 146 |
| FR-1.6 | Benchmark schema validation | FR-1.6-UNIT-001 | `test_benchmark_response_schema_valid` | `test_schemas.py` | 41 |
| FR-1.7 | Dataset schema validation | FR-1.7-UNIT-001 | `test_dataset_response_schema_valid` | `test_schemas.py` | 86 |
| FR-1.8 | Guideline boolean scale | FR-1.8-UNIT-001 | `test_guideline_boolean_scoring_scale` | `test_schemas.py` | 113 |
| FR-1.9 | Guideline numeric scale | FR-1.9-UNIT-001 | `test_guideline_numeric_scoring_scale` | `test_schemas.py` | 127 |
| FR-1.10 | Guideline custom category | FR-1.10-UNIT-001 | `test_guideline_custom_category_scoring_scale` | `test_schemas.py` | 143 |
| FR-1.11 | Reject mismatched config | FR-1.11-UNIT-001 | `test_guideline_mismatched_config_rejected` | `test_schemas.py` | 173 |

### FR-2.0: User Custom Evaluation Submission Portal

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-2.1 | Valid ModelConfig | FR-2.1-UNIT-001 | `test_model_config_valid` | `test_schemas.py` | 196 |
| FR-2.2 | OpenRouter api_source | FR-2.2-UNIT-001 | `test_model_config_openrouter_source` | `test_schemas.py` | 214 |
| FR-2.3 | Reject invalid api_source | FR-2.3-UNIT-001 | `test_model_config_invalid_api_source` | `test_schemas.py` | 230 |
| FR-2.4 | Valid DatasetConfig | FR-2.4-UNIT-001 | `test_dataset_config_valid` | `test_schemas.py` | 246 |
| FR-2.5 | Task evaluation request | FR-2.5-UNIT-001 | `test_task_evaluation_request_valid` | `test_schemas.py` | 268 |
| FR-2.6 | Flexible eval - text | FR-2.6-UNIT-001 | `test_flexible_evaluation_request_text_output` | `test_schemas.py` | 292 |
| FR-2.7 | Flexible eval - MC | FR-2.7-UNIT-001 | `test_flexible_evaluation_request_multiple_choice` | `test_schemas.py` | 319 |
| FR-2.8 | List evaluation traces | FR-2.8-INT-001 | `test_evaluation_traces_authenticated` | `test_api_endpoints.py` | 217 |

### FR-3.0: Admin Evaluation API

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-3.1 | List providers | FR-3.1-INT-001 | `test_providers_list` | `test_api_endpoints.py` | 268 |
| FR-3.2 | List models | FR-3.2-INT-001 | `test_models_list` | `test_api_endpoints.py` | 281 |

### FR-4.0: Filterable Leaderboard

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-4.1 | Require dataset_name param | FR-4.1-INT-001 | `test_leaderboard_requires_dataset_parameter` | `test_api_endpoints.py` | 234 |
| FR-4.2 | Return leaderboard data | FR-4.2-INT-001 | `test_leaderboard_with_dataset_parameter` | `test_api_endpoints.py` | 245 |
| FR-4.3 | Leaderboard entry fields | FR-4.3-INT-001 | `test_leaderboard_entry_has_required_fields` | `test_api_endpoints.py` | 326 |

### FR-5.0: Side-by-Side Comparison

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-5.1 | Overlapping datasets | FR-5.1-INT-001 | `test_overlapping_datasets_endpoint` | `test_api_endpoints.py` | 263 |
| FR-5.2 | Side-by-side report | FR-5.2-INT-001 | `test_side_by_side_report_endpoint` | `test_api_endpoints.py` | 277 |

### FR-6.0: Login & Authentication

| Req ID | Requirement | Test ID | Test Name | File | Line |
|--------|-------------|---------|-----------|------|------|
| FR-6.1 | Datasets require auth | FR-6.1-INT-001 | `test_datasets_list_requires_authentication` | `test_api_endpoints.py` | 162 |
| FR-6.2 | Guidelines require auth | FR-6.2-INT-001 | `test_guidelines_list_requires_authentication` | `test_api_endpoints.py` | 172 |
| FR-6.3 | Traces require auth | FR-6.3-INT-001 | `test_evaluation_traces_requires_authentication` | `test_api_endpoints.py` | 182 |
| FR-6.4 | Profile requires auth | FR-6.4-INT-001 | `test_user_profile_requires_authentication` | `test_api_endpoints.py` | 192 |
| FR-6.5 | Invalid token rejected | FR-6.5-INT-001 | `test_invalid_token_rejected` | `test_api_endpoints.py` | 202 |
| FR-6.6 | UserCreate validation | FR-6.6-UNIT-001 | `test_user_create_valid` | `test_schemas.py` | 348 |
| FR-6.7 | Invalid email rejected | FR-6.7-UNIT-001 | `test_user_create_invalid_email` | `test_schemas.py` | 359 |
| FR-6.8 | AuthResponse schema | FR-6.8-UNIT-001 | `test_auth_response_valid` | `test_schemas.py` | 385 |

---

## Non-Functional Requirements (NFR)

### NFR-1.0: Performance

| Req ID | Requirement | Test ID | Test Name | File | Target |
|--------|-------------|---------|-----------|------|--------|
| NFR-1.1 | Health endpoint < 100ms | NFR-1.1-PERF-001 | `test_health_endpoint_performance` | `test_evaluation_flow.py` | < 100ms avg |
| NFR-1.2 | Benchmark list < 500ms | NFR-1.2-PERF-001 | `test_benchmark_list_performance` | `test_evaluation_flow.py` | < 500ms avg |

### NFR-2.0: Security

| Req ID | Requirement | Test ID | Test Name | File | Target |
|--------|-------------|---------|-----------|------|--------|
| NFR-2.1 | Protected routes | NFR-2.1-SEC-001 | `TestAuthenticationProtection` (class) | `test_api_endpoints.py` | 401/403 |
| NFR-2.2 | JWT verification | NFR-2.2-SEC-001 | `test_invalid_token_rejected` | `test_api_endpoints.py` | Reject invalid |

### NFR-3.0: Reliability

| Req ID | Requirement | Test ID | Test Name | File | Target |
|--------|-------------|---------|-----------|------|--------|
| NFR-3.1 | Consistent errors | NFR-3.1-REL-001 | `test_error_handling_workflow` | `test_evaluation_flow.py` | No 500 errors |
| NFR-3.2 | Proper 404s | NFR-3.2-REL-001 | `test_benchmark_not_found_returns_404` | `test_api_endpoints.py` | 404 format |
| NFR-3.3 | Validation errors | NFR-3.3-REL-001 | `test_leaderboard_requires_dataset_parameter` | `test_api_endpoints.py` | 422 format |

---

## End-to-End Tests

| Test ID | Test Name | Covers | File |
|---------|-----------|--------|------|
| E2E-001 | `test_complete_benchmark_browsing_flow` | FR-1.1, FR-1.3, FR-1.5 | `test_evaluation_flow.py` |
| E2E-002 | `test_authenticated_user_workflow` | FR-1.7, FR-2.8, FR-6.x | `test_evaluation_flow.py` |
| E2E-003 | `test_leaderboard_data_retrieval` | FR-4.1, FR-4.2 | `test_evaluation_flow.py` |
| E2E-004 | `test_error_handling_workflow` | NFR-3.1, NFR-3.2, NFR-3.3 | `test_evaluation_flow.py` |

---

## Test Coverage Summary

| Category | Total Tests | Unit | Integration | E2E |
|----------|-------------|------|-------------|-----|
| FR-1.0 Benchmarks | 13 | 6 | 7 | 0 |
| FR-2.0 Evaluations | 8 | 7 | 1 | 0 |
| FR-3.0 Admin | 2 | 0 | 2 | 0 |
| FR-4.0 Leaderboard | 3 | 0 | 3 | 0 |
| FR-5.0 Comparison | 2 | 0 | 2 | 0 |
| FR-6.0 Auth | 8 | 3 | 5 | 0 |
| NFR-1.0 Performance | 2 | 0 | 0 | 2 |
| NFR-2.0 Security | 2 | 0 | 2 | 0 |
| NFR-3.0 Reliability | 3 | 0 | 2 | 1 |
| **Total** | **43** | **16** | **24** | **3** |

---

## Quick Reference: Running Tests

```bash
# All tests
poetry run pytest tests/ -v

# By requirement area
poetry run pytest tests/ -k "benchmark" -v    # FR-1.0
poetry run pytest tests/ -k "evaluation" -v   # FR-2.0
poetry run pytest tests/ -k "leaderboard" -v  # FR-4.0
poetry run pytest tests/ -k "auth" -v         # FR-6.0

# By test type
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v
poetry run pytest tests/e2e/ -v
```

---

## Evidence Locations

| Evidence Type | File Pattern | Location |
|---------------|--------------|----------|
| E2E Results | `e2e_evidence_*.json` | `tests/evidence/` |
| Performance | `performance_evidence_*.json` | `tests/evidence/` |
| Coverage | `index.html` | `tests/evidence/coverage_report/` |
| Benchmark Report | `benchmark_test_report.md` | Repository root |
