"""
Unit Tests for Week 4 Observability, Correlation, Tracing, and Metrics.

Verifies:
  1. Correlation ID propagation.
  2. EventLogger structured event emission.
  3. Distributed tracer span lifecycle and attributes.
  4. MetricsCollector latency calculation and counter updates.
"""

import time
import pytest

from observability.correlation import get_correlation_id, set_correlation_id
from observability.events import EventLogger, EventType
from observability.metrics import MetricsCollector
from observability.tracer import Tracer


def test_correlation_id_context():
    """Verify correlation ID can be set and retrieved in async context."""
    token = set_correlation_id("test-corr-abc-123")
    assert get_correlation_id() == "test-corr-abc-123"


def test_event_logger_records_events():
    """Verify EventLogger collects events with correlation ID."""
    logger = EventLogger()
    event = logger.record(
        event_type=EventType.TOOL_STARTED,
        correlation_id="corr-999",
        username="agent_sam",
        payload={"tool": "retrieve_case_details"},
    )

    assert event.event_type == EventType.TOOL_STARTED
    assert event.correlation_id == "corr-999"

    logged = logger.get_events_for_correlation("corr-999")
    assert len(logged) == 1
    assert logged[0].payload["tool"] == "retrieve_case_details"


def test_tracer_span_lifecycle():
    """Verify tracer span records start, end, attributes, and duration."""
    tracer = Tracer()
    with tracer.trace(trace_id="trace-xyz", name="orchestration_test", tags={"intent": "retrieve_case"}) as span:
        time.sleep(0.01)  # small duration

    assert span.duration_ms is not None
    assert span.duration_ms > 0
    assert span.tags["intent"] == "retrieve_case"
    assert span.status == "OK"


def test_metrics_collector():
    """Verify latency percentiles and counters in MetricsCollector."""
    metrics = MetricsCollector()

    # Record some latencies
    metrics.record_latency("workflow_total", 10.0)
    metrics.record_latency("workflow_total", 20.0)
    metrics.record_ai_usage(prompt_tokens=50, completion_tokens=25)
    metrics.record_error("tool_failures")
    metrics.increment_request_count()

    stats = metrics.get_summary()
    assert stats["total_requests"] == 1
    assert stats["latency_metrics"]["workflow_total"]["count"] == 2
    assert stats["latency_metrics"]["workflow_total"]["avg_ms"] == 15.0
    assert stats["token_usage"]["total_tokens"] == 75
    assert stats["error_metrics"]["tool_failures"] == 1
