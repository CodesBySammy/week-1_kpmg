"""
Observability Subsystem for Week 4 Controlled AI Workflows.
Implements correlation IDs, structured lifecycle events, distributed-style tracing, and metric collection.
"""

from .correlation import get_correlation_id, set_correlation_id, CorrelationMiddleware
from .events import WorkflowEvent, EventType, event_logger
from .tracer import Tracer, Span, trace_collector
from .metrics import MetricsCollector, metrics_collector

__all__ = [
    "get_correlation_id",
    "set_correlation_id",
    "CorrelationMiddleware",
    "WorkflowEvent",
    "EventType",
    "event_logger",
    "Tracer",
    "Span",
    "trace_collector",
    "MetricsCollector",
    "metrics_collector",
]
