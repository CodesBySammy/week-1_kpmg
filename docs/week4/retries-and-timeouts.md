# Retries, Timeouts, and Exponential Backoff

## 1. Retry Strategy
- **Retryable Errors:** Downstream network timeouts, transient database connection lockups, temporary rate limits.
- **Non-Retryable Errors:** Schema validation failures, authentication errors, authorization rejections, human approval rejections, missing resources (404/Case Not Found).
- **Backoff Algorithm:** Exponential backoff with jitter:
  Delay = base_delay * (2 ** attempt) + jitter

## 2. Timeouts
- Tool execution timeout: **5.0 seconds**
- Workflow overall timeout: **10.0 seconds**
- Exceeding the timeout transitions the workflow to `WorkflowState.TIMED_OUT` and emits a structured failure event.
