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
