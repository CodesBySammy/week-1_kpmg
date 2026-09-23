"""
Tracing Module.
Provides lightweight, OpenTelemetry-compatible span and trace tracking
to reconstruct call hierarchies: request -> workflow -> RAG/tool -> database.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import time
import uuid
import contextlib
from pydantic import BaseModel, Field


class Span(BaseModel):
    span_id: str = Field(default_factory=lambda: f"spn_{uuid.uuid4().hex[:10]}")
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "OK"  # "OK" or "ERROR"
    tags: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class Tracer:
    """Manages creation, nesting, and querying of execution spans."""

    def __init__(self):
        self._spans: List[Span] = []

    def start_span(
        self,
        trace_id: str,
        name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Span:
        span = Span(
            trace_id=trace_id,
            name=name,
            parent_span_id=parent_span_id,
            start_time=time.perf_counter(),
            tags=tags or {},
        )
        self._spans.append(span)
        return span

    def end_span(self, span: Span, status: str = "OK", error: Optional[str] = None) -> Span:
        span.end_time = time.perf_counter()
        span.duration_ms = round((span.end_time - span.start_time) * 1000.0, 2)
        span.status = status
        span.error_message = error
        return span

    @contextlib.contextmanager
    def trace(
        self,
        trace_id: str,
        name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ):
        span = self.start_span(trace_id, name, parent_span_id, tags)
        try:
            yield span
            self.end_span(span, status="OK")
        except Exception as ex:
            self.end_span(span, status="ERROR", error=str(ex))
            raise

    def get_spans_for_trace(self, trace_id: str) -> List[Span]:
        return [s for s in self._spans if s.trace_id == trace_id]

    def export_trace_tree(self, trace_id: str) -> List[Dict[str, Any]]:
        """Formats the trace into an indented hierarchical tree for debugging."""
        spans = self.get_spans_for_trace(trace_id)
        return [
            {
                "span_id": s.span_id,
                "name": s.name,
                "parent_id": s.parent_span_id,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "tags": s.tags,
            }
            for s in spans
        ]


trace_collector = Tracer()
