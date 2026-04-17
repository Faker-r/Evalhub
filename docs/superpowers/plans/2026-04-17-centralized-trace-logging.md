# Centralized Trace Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add request-scoped trace IDs and structured JSON logging to correlate logs across FastAPI requests and Celery worker tasks.

**Architecture:** A `contextvars.ContextVar` holds a per-request trace ID set by FastAPI middleware. A custom `JSONFormatter` reads the context var and emits structured JSON on every log call. Celery tasks receive the trace ID as an explicit parameter and set the context var before doing work.

**Tech Stack:** Python stdlib only (`contextvars`, `logging`, `json`, `uuid`). No new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-17-centralized-trace-logging-design.md`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `backend/api/core/trace_context.py` | **New.** `ContextVar` for trace ID + `TraceIDMiddleware` |
| `backend/api/core/logging.py` | **Modify.** Replace plain-text formatter with `JSONFormatter` that reads trace ID from context var |
| `backend/api/main.py` | **Modify.** Register `TraceIDMiddleware` |
| `backend/api/evaluations/service.py` | **Modify.** Pass `request_trace_id` when dispatching Celery tasks |
| `backend/api/evaluations/tasks.py` | **Modify.** Accept `request_trace_id` param, set context var at task start |
| `backend/tests/unit/test_trace_context.py` | **New.** Unit tests for trace context module |
| `backend/tests/unit/test_logging.py` | **New.** Unit tests for JSON formatter |
| `backend/tests/test_main.py` | **Modify.** Add test for trace ID in response headers |

---

### Task 1: Trace Context Module — ContextVar + Middleware

**Files:**
- Create: `backend/api/core/trace_context.py`
- Test: `backend/tests/unit/test_trace_context.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/unit/test_trace_context.py`:

```python
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.core.trace_context import TraceIDMiddleware, trace_id_var


def _make_app():
    app = FastAPI()
    app.add_middleware(TraceIDMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"trace_id": trace_id_var.get("")}

    return app


class TestTraceIDVar:
    def test_default_is_empty_string(self):
        assert trace_id_var.get("") == ""

    def test_set_and_get(self):
        token = trace_id_var.set("abc-123")
        assert trace_id_var.get("") == "abc-123"
        trace_id_var.reset(token)


class TestTraceIDMiddleware:
    def test_generates_trace_id_when_no_header(self):
        client = TestClient(_make_app())
        response = client.get("/test")
        assert response.status_code == 200
        trace_id = response.headers.get("x-trace-id")
        assert trace_id is not None
        uuid.UUID(trace_id)

    def test_uses_provided_trace_id_header(self):
        client = TestClient(_make_app())
        response = client.get("/test", headers={"x-trace-id": "my-custom-id"})
        assert response.headers.get("x-trace-id") == "my-custom-id"
        assert response.json()["trace_id"] == "my-custom-id"

    def test_trace_id_available_in_endpoint(self):
        client = TestClient(_make_app())
        response = client.get("/test")
        body = response.json()
        assert body["trace_id"] == response.headers["x-trace-id"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/test_trace_context.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.core.trace_context'`

- [ ] **Step 3: Write the implementation**

Create `backend/api/core/trace_context.py`:

```python
import contextvars
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tid = request.headers.get("x-trace-id") or str(uuid.uuid4())
        trace_id_var.set(tid)
        response = await call_next(request)
        response.headers["x-trace-id"] = tid
        return response
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/test_trace_context.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd backend
git add api/core/trace_context.py tests/unit/test_trace_context.py
git commit -m "feat: add trace ID context var and middleware"
```

---

### Task 2: Structured JSON Logging

**Files:**
- Modify: `backend/api/core/logging.py` (lines 1-21)
- Test: `backend/tests/unit/test_logging.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/unit/test_logging.py`:

```python
import json
import logging

from api.core.logging import JSONFormatter, get_logger, setup_logging
from api.core.trace_context import trace_id_var


class TestJSONFormatter:
    def test_output_is_valid_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "hello"
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"

    def test_includes_trace_id_from_context(self):
        formatter = JSONFormatter()
        token = trace_id_var.set("test-trace-123")
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="with trace", args=(), exc_info=None,
            )
            output = formatter.format(record)
            parsed = json.loads(output)
            assert parsed["trace_id"] == "test-trace-123"
        finally:
            trace_id_var.reset(token)

    def test_trace_id_empty_when_no_context(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="no trace", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["trace_id"] == ""

    def test_has_all_required_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="api.core.test", level=logging.WARNING, pathname="test.py",
            lineno=42, msg="check fields", args=(), exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_func"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert set(parsed.keys()) == {
            "timestamp", "level", "logger", "message",
            "trace_id", "module", "func",
        }


class TestGetLogger:
    def test_returns_named_logger(self):
        log = get_logger("my.module")
        assert log.name == "my.module"


class TestSetupLogging:
    def test_root_logger_has_json_formatter(self):
        setup_logging()
        root = logging.getLogger()
        has_json = any(
            isinstance(h.formatter, JSONFormatter)
            for h in root.handlers
        )
        assert has_json
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/test_logging.py -v`
Expected: FAIL with `ImportError: cannot import name 'JSONFormatter' from 'api.core.logging'`

- [ ] **Step 3: Write the implementation**

Replace the contents of `backend/api/core/logging.py` with:

```python
import json
import logging
import sys

from api.core.config import settings
from api.core.trace_context import trace_id_var


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id_var.get(""),
            "module": record.module,
            "func": record.funcName,
        })


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if not any(isinstance(h.formatter, JSONFormatter) for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "celery", "celery.worker"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/test_logging.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Run existing tests to check for regressions**

Run: `cd backend && python -m pytest tests/test_main.py -v`
Expected: PASS (existing health check and root endpoint tests still work)

- [ ] **Step 6: Commit**

```bash
cd backend
git add api/core/logging.py tests/unit/test_logging.py
git commit -m "feat: replace plain-text logging with JSON formatter and trace ID injection"
```

---

### Task 3: Register Middleware in FastAPI App

**Files:**
- Modify: `backend/api/main.py` (lines 1-49)
- Modify: `backend/tests/test_main.py`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_main.py`:

```python
import uuid


def test_response_contains_trace_id_header():
    response = client.get("/api/health")
    trace_id = response.headers.get("x-trace-id")
    assert trace_id is not None
    uuid.UUID(trace_id)


def test_request_trace_id_is_echoed_back():
    response = client.get("/api/health", headers={"x-trace-id": "custom-trace-abc"})
    assert response.headers.get("x-trace-id") == "custom-trace-abc"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_main.py::test_response_contains_trace_id_header tests/test_main.py::test_request_trace_id_is_echoed_back -v`
Expected: FAIL (no `x-trace-id` header in response yet)

- [ ] **Step 3: Register the middleware**

In `backend/api/main.py`, add the import at the top (after the existing imports from `api.core`):

```python
from api.core.trace_context import TraceIDMiddleware
```

Then add the middleware registration right after the existing `app.add_middleware(SlowAPIASGIMiddleware)` line (line 49):

```python
app.add_middleware(TraceIDMiddleware)
```

The full middleware section should read:

```python
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIASGIMiddleware)
app.add_middleware(TraceIDMiddleware)
```

Note: Starlette processes middleware in reverse order of `add_middleware` calls. `TraceIDMiddleware` is added last so it runs **first** (outermost), ensuring the trace ID is available before rate limiting runs.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_main.py -v`
Expected: All 4 tests PASS (2 existing + 2 new)

- [ ] **Step 5: Commit**

```bash
cd backend
git add api/main.py tests/test_main.py
git commit -m "feat: register TraceIDMiddleware in FastAPI app"
```

---

### Task 4: Celery Trace ID Propagation

**Files:**
- Modify: `backend/api/evaluations/service.py` (lines 68-77, 146-161)
- Modify: `backend/api/evaluations/tasks.py` (lines 570-579, 658-673)

This task modifies Celery task signatures and dispatch calls. No unit test is practical here since these tasks require database, Redis, S3, and LLM provider connections. Verification is done by inspecting the code changes and running existing tests for regressions.

- [ ] **Step 1: Add trace ID propagation to `service.py`**

In `backend/api/evaluations/service.py`, add the import at the top (after the existing `from api.core.logging import get_logger` line):

```python
from api.core.trace_context import trace_id_var
```

Then modify the `run_task_evaluation_task.delay()` call (lines 69-77) to pass `request_trace_id`:

```python
        run_task_evaluation_task.delay(
            trace_id=trace.id,
            user_id=self.user_id,
            task_name=task_name,
            n_samples=request.dataset_config.n_samples,
            n_fewshots=request.dataset_config.n_fewshots,
            model_config_data=model_config_data,
            request_data=request_data,
            request_trace_id=trace_id_var.get(""),
        )
```

And modify the `run_flexible_evaluation_task.delay()` call (lines 147-161) to pass `request_trace_id`:

```python
        run_flexible_evaluation_task.delay(
            trace_id=trace.id,
            user_id=self.user_id,
            dataset_name=request.dataset_name,
            dataset_content=dataset_content,
            input_field=request.input_field,
            output_type=request.output_type.value,
            judge_type=request.judge_type.value,
            text_config=text_config_data,
            mc_config=mc_config_data,
            guidelines_data=guidelines_data,
            model_config_data=model_config_data,
            judge_config_data=judge_config_data,
            request_data=request_data,
            request_trace_id=trace_id_var.get(""),
        )
```

- [ ] **Step 2: Add trace ID acceptance to `tasks.py`**

In `backend/api/evaluations/tasks.py`, add two imports. Add `uuid` to the stdlib imports at the top of the file (after `import traceback` on line 7):

```python
import uuid
```

And add the trace context import after the existing `from api.core.logging import get_logger` line:

```python
from api.core.trace_context import trace_id_var
```

Then modify `run_task_evaluation_task` (lines 570-579) to accept and set the trace ID:

```python
def run_task_evaluation_task(
    self,
    trace_id: int,
    user_id: str,
    task_name: str,
    n_samples: int | None,
    n_fewshots: int | None,
    model_config_data: dict,
    request_data: dict,
    request_trace_id: str = "",
) -> None:
    """Celery task: run a task evaluation pipeline, post-process results, handle errors."""
    trace_id_var.set(request_trace_id or str(uuid.uuid4()))
    try:
```

And modify `run_flexible_evaluation_task` (lines 658-673) similarly:

```python
def run_flexible_evaluation_task(
    self,
    trace_id: int,
    user_id: str,
    dataset_name: str,
    dataset_content: str,
    input_field: str,
    output_type: str,
    judge_type: str,
    text_config: dict | None,
    mc_config: dict | None,
    guidelines_data: list[dict],
    model_config_data: dict,
    judge_config_data: dict | None,
    request_data: dict,
    request_trace_id: str = "",
) -> None:
    """Celery task: run a flexible evaluation pipeline, post-process results, handle errors."""
    trace_id_var.set(request_trace_id or str(uuid.uuid4()))
    try:
```

- [ ] **Step 3: Run existing tests for regressions**

Run: `cd backend && python -m pytest tests/test_main.py tests/unit/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
cd backend
git add api/evaluations/service.py api/evaluations/tasks.py
git commit -m "feat: propagate trace ID from API requests to Celery tasks"
```

---

### Task 5: Smoke Test — End-to-End Verification

This is a manual verification step, not an automated test. It confirms that the full chain works with the running app.

- [ ] **Step 1: Start the backend**

Run: `cd backend && python -m api`

- [ ] **Step 2: Make a request and verify JSON logs with trace ID**

In another terminal:
```bash
curl -s http://localhost:8001/api/health -v 2>&1 | grep -i x-trace-id
```

Expected: Response includes `x-trace-id: <some-uuid>` header.

Check the backend terminal output — logs should be JSON lines like:
```json
{"timestamp": "...", "level": "INFO", "logger": "api.main", "message": "Starting Evalhub application", "trace_id": "", "module": "main", "func": "lifespan"}
```

- [ ] **Step 3: Verify custom trace ID is echoed**

```bash
curl -s http://localhost:8001/api/health -H "x-trace-id: test-123" -v 2>&1 | grep -i x-trace-id
```

Expected: `x-trace-id: test-123`

- [ ] **Step 4: Commit final state (if any adjustments were needed)**

Only if changes were made during smoke testing:
```bash
git add -u
git commit -m "fix: adjustments from smoke testing"
```
