"""
Operational Metrics Collector.
Measures latency, AI token usage, and system error rates.
"""
from typing import Dict, Any, List
import threading
from pydantic import BaseModel, Field


class MetricsCollector:
    """Thread-safe collector for real-time operational telemetry."""

    def __init__(self):
        self._lock = threading.Lock()
        
        # Latencies: dict of list of float ms
        self._latencies: Dict[str, List[float]] = {
            "workflow_total": [],
            "rag_retrieval": [],
            "tool_execution": [],
            "approval_wait": [],
        }

        # Token usage
        self._token_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "calls_count": 0,
        }

        # Error counts
        self._error_counts: Dict[str, int] = {
            "guardrail_violations": 0,
            "authentication_failures": 0,
            "authorization_failures": 0,
            "tool_failures": 0,
            "timeouts": 0,
            "retry_exhausted": 0,
            "approval_rejections": 0,
            "unhandled_exceptions": 0,
        }

        # Request counter
        self._total_requests = 0

    def record_latency(self, metric_name: str, duration_ms: float):
        with self._lock:
            if metric_name not in self._latencies:
                self._latencies[metric_name] = []
            self._latencies[metric_name].append(duration_ms)
            if len(self._latencies[metric_name]) > 500:
                self._latencies[metric_name].pop(0)

    def record_ai_usage(self, prompt_tokens: int, completion_tokens: int):
        with self._lock:
            self._token_usage["total_prompt_tokens"] += prompt_tokens
            self._token_usage["total_completion_tokens"] += completion_tokens
            self._token_usage["total_tokens"] += (prompt_tokens + completion_tokens)
            self._token_usage["calls_count"] += 1

    def record_error(self, error_type: str):
        with self._lock:
            self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1

    def increment_request_count(self):
        with self._lock:
            self._total_requests += 1

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            latency_summary = {}
            for k, v in self._latencies.items():
                if v:
                    latency_summary[k] = {
                        "count": len(v),
                        "avg_ms": round(sum(v) / len(v), 2),
                        "min_ms": round(min(v), 2),
                        "max_ms": round(max(v), 2),
                    }
                else:
                    latency_summary[k] = {"count": 0, "avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}

            return {
                "total_requests": self._total_requests,
                "latency_metrics": latency_summary,
                "token_usage": dict(self._token_usage),
                "error_metrics": dict(self._error_counts),
            }


metrics_collector = MetricsCollector()
