# Incident Report: INC-06 - Upstream Model Provider Failure

## 1. Symptom & Description
The external or local LLM inference endpoint experiences high latency, connection reset, or returns an HTTP 503 Service Unavailable.

## 2. Expected Behavior
- Circuit breaker / timeout interceptor trips after bounded duration (e.g., 5.0 seconds).
- The orchestrator falls back to a graceful degraded response without crashing the request thread.
- Emits structured error log with trace ID.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_model_failure_llm_down_fallback`.

## 4. Root Cause Analysis
Direct unbounded network calls to LLM APIs can cause worker thread exhaustion and cascading failures.

## 5. Remediation & Hardening
- Configured bounded timeout on LLM provider client.
- Added try/except fallback returning deterministic policy message: `"Service temporarily degraded: LLM inference unavailable. Please retry shortly."`
