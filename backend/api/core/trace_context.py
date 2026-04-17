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
