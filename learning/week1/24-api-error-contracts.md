# Module 24: API Error Contracts & Predictable Client Failure Handling

## 1. What It Is
An **API Error Contract** is a formalized, immutable specification governing the exact JSON structure and semantic codes returned by an API whenever a request fails (HTTP 4xx or 5xx).

## 2. Why It Exists
In undisciplined backend services, errors are returned haphazardly:
- Route A returns: `{"error": "Case not found"}` (string)
- Route B returns: `{"errors": ["Invalid priority", "Missing title"]}` (list)
- Route C returns: `{"message": "Internal failure", "code": 104}` (integer code)
- Route D returns an unhandled 500 HTML error page from the web server!

**The Result**: Frontend and client engineers must write convoluted, fragile `try/catch` logic with dozens of `if/else` checks to figure out what went wrong. An Error Contract guarantees that *every single failure* conforms to one predictable envelope.

## 3. Why Backend Engineers Use It
- **Deterministic Client Parsing**: Frontends can write a single global interceptor (in Axios or Fetch) that unwraps errors, displays toast notifications, and highlights invalid input fields automatically.
- **Machine-Parseable Error Codes**: Instead of parsing natural language English strings (`if (msg.includes("not found"))`), clients switch on stable, enum-like error codes (`CASE_NOT_FOUND`).
- **Security by Default**: Enforces that internal stack traces, SQL queries, and server file paths are stripped before reaching the outside world.

## 4. The Standard Error Envelope Architecture

```json
{
  "error": {
    "code": "STRING_ENUM_IDENTIFIER",
    "message": "Human-readable summary of the failure",
    "details": null | [ "Array of specific field validation errors" ]
  }
}
```

```mermaid
graph TD
    Client[Client App] -->|Sends Bad Request| API[FastAPI Ingress]
    API --> Handlers[app/exceptions/handlers.py]
    Handlers --> F1[404: CASE_NOT_FOUND]
    Handlers --> F2[422: REQUEST_VALIDATION_ERROR]
    Handlers --> F3[422: VALIDATION_ERROR]
    Handlers --> F4[500: INTERNAL_ERROR]
    
    F1 --> Envelope[Universal JSON Envelope]
    F2 --> Envelope
    F3 --> Envelope
    F4 --> Envelope
    Envelope --> Client
```

## 5. Specification of System Error Codes

| Error Code | HTTP Status | Description | Example Scenario |
|---|---|---|---|
| `CASE_NOT_FOUND` | **404** | The requested case identifier does not exist | `GET /api/v1/cases/999` |
| `USER_NOT_FOUND` | **404** | The referenced creator or assignee user does not exist | Creating a case with `created_by: 888` |
| `REQUEST_VALIDATION_ERROR` | **422** | Incoming JSON failed Pydantic schema or type validation | Sending an empty string for `title` |
| `VALIDATION_ERROR` | **422** | Domain business rule violation | Attempting to mutate a `CLOSED` case |
| `INTERNAL_ERROR` | **500** | Unexpected server-side bug or persistence failure | Database disk failure or unhandled exception |

## 6. Concrete Contract Examples from Our Project

### Example 1: Resource Not Found (HTTP 404)
```json
{
  "error": {
    "code": "CASE_NOT_FOUND",
    "message": "Case with id 9999 not found",
    "details": null
  }
}
```

### Example 2: Schema Validation Failure with Field Details (HTTP 422)
When Pydantic rejects a payload, our handler transforms the raw validation errors into a clean, field-by-field breakdown:
```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "body -> title",
        "message": "String should have at least 1 character",
        "type": "string_too_short"
      },
      {
        "field": "body -> priority",
        "message": "Input should be 'LOW', 'MEDIUM', 'HIGH' or 'CRITICAL'",
        "type": "enum"
      }
    ]
  }
}
```

### Example 3: Masked Internal Server Error (HTTP 500)
Even if Python crashed with a 40-line `sqlalchemy.exc.OperationalError`, the client receives only a safe, sanitized envelope:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": null
  }
}
```

## 7. Common Mistakes
1. **Returning Error Strings Instead of Objects**:
   - `{"detail": "Not found"}` leaves no room for error codes or metadata.
2. **Changing Error Formats per Endpoint**:
   - Every single endpoint in the service must share the exact same top-level `"error"` key.
3. **Leaking Secrets in Error Messages**:
   - E.g. Returning `"Connection failed to postgresql://admin:secret123@db.prod:5432"`. Never pass raw driver exceptions to the client.

## 8. Practical Exercises
1. Inspect the implementation of `_error_response()` in [app/exceptions/handlers.py](file:///d:/week1_kpmg/case-management-backend/app/exceptions/handlers.py). Trace how status code, code string, and details are assembled.
2. Write a test asserting that an unhandled 500 error does NOT leak the word "Exception" or Python file paths in the response body. (See [tests/api/test_user_and_error_handlers.py](file:///d:/week1_kpmg/case-management-backend/tests/api/test_user_and_error_handlers.py)).

## 9. Interview Questions & Model Answers
**Q: Why is an explicit error code (like `CASE_NOT_FOUND`) superior to relying solely on the human-readable error message or HTTP status code?**
*Answer:* Human-readable error messages are intended for display, change frequently (e.g. for internationalization/translations or copy edits), and require brittle regex parsing if used in code. Meanwhile, HTTP status codes are coarse-grained: a 404 could mean the route was wrong, the case was missing, or the user was missing. An explicit machine-readable error code provides an immutable, fine-grained semantic enum that client code can safely switch on to trigger specific UI workflows without parsing English text.

## 10. Short Self-Test
1. What three standard keys are contained inside our project's `error` envelope? *(Answer: `code`, `message`, and `details`).*
2. Why should the `details` field be populated for validation errors, but set to `null` for 404 or 500 errors? *(Answer: Validation errors need field-level feedback so the user knows which form field to fix; 404 and 500 errors have no individual field errors to report).*
