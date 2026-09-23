"""
Correlation ID Management and Propagation.
Propagates X-Correlation-ID across HTTP headers, workflow contexts, tool calls, and logs.
"""
from typing import Optional
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_CORRELATION_ID_CTX: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Returns the current request's correlation ID or generates a new one."""
    cid = _CORRELATION_ID_CTX.get()
    if not cid:
        cid = f"corr_{uuid.uuid4().hex[:12]}"
        _CORRELATION_ID_CTX.set(cid)
    return cid


def set_correlation_id(correlation_id: str) -> None:
    """Explicitly sets the correlation ID in the current async context."""
    _CORRELATION_ID_CTX.set(correlation_id)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware that extracts X-Correlation-ID from incoming HTTP headers
    or generates a new UUID, binds it to the async context, and sets it on the response.
    """

    HEADER_NAME = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        cid = request.headers.get(self.HEADER_NAME)
        if not cid:
            cid = f"corr_{uuid.uuid4().hex[:12]}"

        token = _CORRELATION_ID_CTX.set(cid)
        try:
            response: Response = await call_next(request)
            response.headers[self.HEADER_NAME] = cid
            return response
        finally:
            _CORRELATION_ID_CTX.reset(token)
