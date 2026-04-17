# Centralized Trace Logging Design

## Problem

When a request hits the API, triggers a Celery task, and that task calls external services (LLM providers, S3, DB), there is no way to correlate logs across those boundaries. All logging is plain-text to stdout with no request IDs or structured format.

## Scope

- Backend only (no frontend changes)
- No new dependencies (pure stdlib)
- No infrastructure changes (Docker compose, AWS unchanged)

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trace ID field name | `trace_id` | Context makes meaning clear vs. the evaluation `Trace` model |
| Log format | Always JSON | Consistent everywhere; use `jq` locally |
| Frontend propagation | Deferred | Keep scope tight; middleware generates IDs for all requests |
| CloudWatch log shipping for Celery | Deferred | Separate concern; requires IAM policy review |
| Middleware approach | `BaseHTTPMiddleware` | Simplest; body-buffering limitation irrelevant for JSON API responses |

## Architecture

Three layers, five files (one new, four modified):

```
Request → TraceIDMiddleware → ContextVar → JSONFormatter → stdout (JSON)
                                  ↓
                          Celery .delay(request_trace_id=...)
                                  ↓
                          Task sets ContextVar → JSONFormatter → stdout (JSON)
```

### Layer 1: Trace Context Module

**New file: `backend/api/core/trace_context.py`**

- A `contextvars.ContextVar[str]` named `trace_id_var` holds the current request's trace ID. This is async-safe and works across `await` boundaries.
- A `TraceIDMiddleware` (Starlette `BaseHTTPMiddleware`) runs on every request:
  1. Reads `X-Trace-ID` header if present, otherwise generates a `uuid4`
  2. Sets `trace_id_var` so all downstream code can read it
  3. Adds `X-Trace-ID` to the response headers
- Registered in `main.py` alongside the existing SlowAPI middleware.

### Layer 2: Structured JSON Logging

**Modified file: `backend/api/core/logging.py`**

- Replace the `logging.basicConfig` plain-text formatter with a `JSONFormatter` subclass of `logging.Formatter`.
- Each log entry is a single JSON line with fields: `timestamp`, `level`, `logger`, `message`, `trace_id`, `module`, `func`.
- `trace_id` is read from `trace_id_var.get("")` — zero changes to existing log call sites. Every `logger.info(...)` throughout the codebase automatically includes the trace ID.
- `get_logger()` function signature unchanged — callers are unaffected.
- `setup_logging()` configures a `StreamHandler` with the `JSONFormatter` on the root logger.

### Layer 3: Celery Trace Propagation

**Modified files: `backend/api/evaluations/service.py` and `backend/api/evaluations/tasks.py`**

- **Service layer** (`service.py`): When dispatching via `.delay()`, read the current trace ID from `trace_id_var` and pass it as `request_trace_id` kwarg.
- **Task functions** (`tasks.py`): Both `run_task_evaluation_task` and `run_flexible_evaluation_task` accept a new `request_trace_id: str = ""` parameter. First action in each task: `trace_id_var.set(request_trace_id or str(uuid.uuid4()))`. If triggered without a trace ID (e.g., manual Celery invocation), a new one is generated.
- All `logger.*()` calls within tasks automatically include the trace ID via the JSONFormatter.

## Files Changed

| File | Change |
|------|--------|
| `backend/api/core/trace_context.py` | **New** — `ContextVar` + `TraceIDMiddleware` |
| `backend/api/core/logging.py` | Replace formatter with `JSONFormatter` + trace ID injection |
| `backend/api/main.py` | Register `TraceIDMiddleware` |
| `backend/api/evaluations/service.py` | Pass `request_trace_id` when dispatching Celery tasks |
| `backend/api/evaluations/tasks.py` | Accept + set `request_trace_id` param in both tasks |

## Log Output Example

```json
{"timestamp": "2026-04-17 14:30:01", "level": "INFO", "logger": "api.evaluations.service", "message": "Starting task evaluation", "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "module": "service", "func": "create_task_evaluation"}
```

## What This Enables

- Search all logs for a single request: `grep "a1b2c3d4" logs.json` or CloudWatch Logs Insights `filter trace_id = "a1b2c3d4-..."`
- Correlate API request logs with the Celery worker logs that processed the evaluation
- Structured JSON format enables programmatic log parsing and future integration with log aggregation tools

## Future Extensions (Not In Scope)

- Frontend `X-Trace-ID` propagation from React `ApiClient`
- Switch Celery Docker log driver to `awslogs` for unified CloudWatch querying
- OpenTelemetry integration (trace ID foundation makes migration straightforward)
