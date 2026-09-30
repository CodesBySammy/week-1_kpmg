# Incident Report: INC-02 - Gateway API Failure

## 1. Symptom & Description
Client applications occasionally emit truncated or malformed HTTP POST bodies (`Content-Type: application/json` with trailing syntax errors or missing closing braces) or invoke endpoints with upstream timeout conditions.

## 2. Expected Behavior
- The FastAPI gateway must catch parser exceptions before routing to domain handlers.
- Return HTTP 422 Unprocessable Entity with deterministic RFC 7807 problem details.
- Provide a unique `correlation_id` header in the response for tracing.
- Never leak Python stack traces or internal server structure to callers.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_api_failure_malformed_json_returns_422`.

```python
def test_api_failure_malformed_json_returns_422(client):
    response = client.post(
        "/api/v1/cases/",
        data="{truncated_json: true",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert "correlation_id" in response.headers
```

## 4. Root Cause Analysis
Default exception handlers in vanilla frameworks sometimes expose traceback details or drop correlation headers on early parsing errors.

## 5. Remediation & Hardening
- Registered custom `RequestValidationError` handler in `app/api/middleware.py`.
- Ensured `CorrelationIdMiddleware` runs as outermost ASGI middleware layer.
- Bound correlation IDs to all error responses.
