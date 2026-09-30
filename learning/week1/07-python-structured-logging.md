# Module 07: Python Structured Logging & Observability

## 1. What It Is
**Structured Logging** is the practice of emitting application logs as standardized, machine-readable data structures (typically JSON) rather than unstructured free-form text strings. Each log entry contains standardized key-value pairs (`timestamp`, `level`, `logger`, `operation`, `case_id`, `duration_ms`).

## 2. Why It Exists
In high-throughput enterprise systems processing thousands of requests per second:
- Unstructured `print()` statements or plain strings like `"User 14 updated case 22"` require fragile, slow regular expressions to parse.
- When an outage occurs, operators cannot filter logs by `case_id == 42` or alert on `level == 'ERROR' and operation == 'database_commit'`.
- Plain text strings cannot be indexed efficiently by modern log aggregation platforms (e.g. Datadog, Elasticsearch, Splunk, AWS CloudWatch).

## 3. Why Backend Engineers Use It
- **Instant Queryability & Alerting**: Query logs like a database table in cloud monitoring tools (`SELECT count(*) WHERE error.code = 'DATABASE_ERROR'`).
- **Distributed Tracing & Correlation**: Attaching a unique `request_id` or `correlation_id` to every log line allows an engineer to trace an HTTP request as it flows across multiple services.
- **Root Cause Isolation**: When a test or production request fails, structured metadata immediately identifies the exact parameters, user, and module responsible.

## 4. Comparison: Plain Text vs. Structured JSON

### Plain Text Logging (Primitive)
```text
2026-09-10 12:00:00 - INFO - Case created with id 101 by user 4
```
*Disadvantage*: To extract the case ID, you must write a regex pattern. If someone changes the phrasing to `"Created case #101"`, all alerting dashboards break.

### Structured JSON Logging (Enterprise Standard)
```json
{
  "timestamp": "2026-09-10T12:00:00+00:00",
  "level": "INFO",
  "logger": "app.services.case_service",
  "message": "Case created successfully",
  "case_id": 101,
  "status": "OPEN",
  "operation": "create_case"
}
```
*Advantage*: Every field is a direct, indexed JSON key. Any log ingestion tool can parse it natively without custom parsing scripts.

## 5. Implementation in Our Project: `app/logging_config.py`
In [app/logging_config.py](file:///d:/week1_kpmg/case-management-backend/app/logging_config.py), we configure Python's standard `logging` library using `python-json-logger`:

```python
from pythonjsonlogger import json as json_logger

def setup_logging(log_level: Optional[str] = None) -> None:
    settings = get_settings()
    level = log_level or settings.log_level

    formatter = json_logger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
```

### Emitting Logs with Context:
Throughout our codebase, we pass structured contextual metadata using the `extra={...}` dictionary:
```python
logger.info(
    "Case updated successfully",
    extra={
        "case_id": case_id,
        "updated_fields": list(updates.keys()),
        "operation": "update_case",
    },
)
```

## 6. What NOT to Log (Security & Privacy Boundaries)
Enterprise compliance policies (GDPR, HIPAA, PCI-DSS, SOC 2) strictly prohibit logging sensitive data:

| Sensitive Category | Examples | Correct Action |
|---|---|---|
| **Credentials** | Passwords, API tokens, JWT secrets, private keys | **NEVER log under any circumstances** |
| **Financial / Payment** | Credit card numbers (PAN), CVVs, bank account numbers | **NEVER log**; mask or redact if necessary |
| **Personal Identifiable Info (PII)** | Social security numbers, national IDs, health records | Mask (`user_id=14` instead of `ssn=***`) |
| **Large Payloads** | Full 50MB file uploads, multi-megabyte base64 strings | Log only metadata (byte size, MIME type, filename) |

## 7. Common Mistakes
1. **Using `print()`**: `print()` lacks log levels (DEBUG/INFO/WARN/ERROR), timestamps, module origin, and cannot be directed to log collectors without ugly stdout hijacking.
2. **String Interpolation in Log Calls**:
   - BAD: `logger.info(f"Case {case_id} updated")` (Forces string formatting even if log level is disabled!).
   - GOOD: `logger.info("Case updated", extra={"case_id": case_id})`.
3. **Logging Sensitive Passwords or Tokens**:
   - Logging the entire incoming request body without sanitizing auth headers or password fields.

## 8. Practical Exercises
1. Run this Python snippet in your terminal to see our project's JSON logger in action:
   ```bash
   python -c "from app.logging_config import setup_logging, get_logger; setup_logging(); logger = get_logger('demo'); logger.info('Test log event', extra={'case_id': 42, 'status': 'OPEN'})"
   ```
   Inspect the JSON output printed to the console.
2. Search through `app/` and locate 3 places where `extra={...}` is used to attach structured metadata to a log event.

## 9. Interview Questions & Model Answers
**Q: What is the difference between structured logging and standard text logging, and why is it preferred in microservice and cloud architectures?**
*Answer:* Standard text logging produces arbitrary human-readable strings that require complex, brittle regex parsing to extract metrics or query events. Structured logging outputs machine-readable JSON key-value pairs with consistent schemas (timestamp, level, service, trace_id, event). In distributed architectures, structured logs can be ingested directly into search and analytics platforms like Elasticsearch or CloudWatch, allowing engineers to filter millions of logs instantaneously by specific customer IDs or error codes.

## 10. Short Self-Test
1. What argument in Python's standard `logger.info(...)` method is used to pass custom structured JSON keys? *(Answer: `extra={...}`)*
2. Name two pieces of data that should NEVER appear in application logs. *(Answer: Passwords and API tokens/secrets).*
