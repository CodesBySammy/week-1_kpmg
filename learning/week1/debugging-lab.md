# Debugging Lab: Practical Failure Diagnosis with Logs & Test Evidence

## Lab Overview
In this lab, you will act as the on-call QA and Backend Engineer. You will diagnose six realistic production defects using real evidence: structured JSON logs, pytest assertion failures, and SQL traces.

**Rules**:
1. Read each Scenario and Evidence carefully.
2. Formulate your own hypothesis and fix BEFORE scrolling down to the Solution Section!

---

## PART I: THE EXERCISES

### Exercise 1: The Missing Unassigned Cases (SQL Query Defect)
- **Symptom**: The customer support director complains: *"Our database has 8 cases total, but when I view the team workload dashboard, only 6 cases appear! Two cases have completely vanished!"*
- **Evidence**:
  - Direct SQL count: `SELECT COUNT(*) FROM cases;` returns `8`.
  - Dashboard Query being run:
    ```sql
    SELECT c.id, c.title, c.status, u.full_name AS assignee
    FROM cases c
    INNER JOIN users u ON c.assigned_to = u.id;
    ```
    Returns only `6` rows!
- **Your Task**:
  1. What is the root cause?
  2. How would you fix the SQL query so all 8 cases are returned?

---

### Exercise 2: The Mysterious 422 Rejection (Validation Defect)
- **Symptom**: An external integration client reports that their script cannot create new tickets. Every call fails with HTTP 422.
- **Evidence (Captured Ingress JSON Log)**:
  ```json
  {
    "timestamp": "2026-09-10T12:15:00Z",
    "level": "WARNING",
    "logger": "app.exceptions.handlers",
    "message": "Request validation failed",
    "path": "/api/v1/cases",
    "errors": [
      {
        "field": "body -> title",
        "message": "String should have at least 1 character",
        "type": "string_too_short"
      },
      {
        "field": "body -> created_by",
        "message": "Input should be a valid integer, unable to parse string as an integer",
        "type": "int_parsing"
      }
    ]
  }
  ```
- **Incoming Request Payload Sent by Client**:
  ```json
  {
    "title": "",
    "description": "Payment webhook timeout",
    "priority": "HIGH",
    "created_by": "user_42"
  }
  ```
- **Your Task**:
  1. Identify the two distinct validation errors in the client payload.
  2. Explain which lines of `app/schemas/case.py` rejected these values.

---

### Exercise 3: The Ghost Status Code (HTTP Status Contract Violation)
- **Symptom**: The automated frontend test suite is failing on ticket creation.
- **Evidence (pytest test failure)**:
  ```text
  tests/api/test_cases_api.py:38: in test_create_case_valid
      assert response.status_code == 201
  E   AssertionError: assert 200 == 201
  E    +  where 200 = <Response [200 OK]>.status_code
  ```
- **Code in Question**:
  ```python
  @router.post("/cases", response_model=CaseResponse)
  def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
      return case_service.create_case(db, case_data)
  ```
- **Your Task**:
  1. Why did FastAPI return status code 200 by default?
  2. What line of code is required to fix this to return the standard 201 Created?

---

### Exercise 4: The Silent Status Transition Failure (Business Rule Defect)
- **Symptom**: A user closed a ticket (`status = 'CLOSED'`). Later, an automated script tried to update the title, and the application crashed or permitted illegal state changes.
- **Evidence**:
  A test fails with:
  ```text
  app.exceptions.ValidationError: Cannot change the status of a CLOSED case
  ```
  However, when updating only the `description` without touching `status`, the server also rejected the update!
- **Code in Service Layer**:
  ```python
  if case.status == CaseStatus.CLOSED:
      raise ValidationError("Cannot update a CLOSED case")
  ```
- **Your Task**:
  1. What is the business logic requirement? Should closed cases be completely immutable, or only prohibit status changes?
  2. Inspect how [app/services/case_service.py](file:///d:/week1_kpmg/case-management-backend/app/services/case_service.py) handles this distinction.

---

### Exercise 5: The Leaked Traceback Security Finding (Error Handling Defect)
- **Symptom**: A security penetration tester flags a high-severity finding: *"API exposes database internal path and schema during simulated disk failure."*
- **Evidence (Client Response Captured by Pentester)**:
  ```json
  {
    "detail": "OperationalError: (sqlite3.OperationalError) disk I/O error\n[SQL: INSERT INTO cases ...] (Background on this error at: https://sqlalche.me/e/20/e3q8)"
  }
  ```
- **Your Task**:
  1. Why did this information leak to the client?
  2. What global exception handler is required to mask this with a safe `500 INTERNAL_ERROR`?

---

### Exercise 6: Broken Circular Import at Startup
- **Symptom**: You start the server using `uvicorn app.main:app` and it immediately crashes before listening on port 8000.
- **Evidence (Terminal Output)**:
  ```text
  ImportError: cannot import name 'CaseService' from partially initialized module 'app.services.case_service' (most likely due to a circular import)
  ```
- **Your Task**:
  1. What causes a circular import in Python?
  2. How do you diagnose and break the circular dependency?

---

## PART II: SOLUTIONS & DETAILED DIAGNOSIS

### Solution 1: SQL Join Defect
- **Diagnosis**: The query used `INNER JOIN users u ON c.assigned_to = u.id`. Cases 4 and 6 have `assigned_to = NULL` (unassigned). Because `NULL` does not match any user ID, the `INNER JOIN` dropped those two rows.
- **Fix**: Replace `INNER JOIN` with `LEFT JOIN` and use `COALESCE`:
  ```sql
  SELECT c.id, c.title, c.status, COALESCE(u.full_name, 'UNASSIGNED') AS assignee
  FROM cases c
  LEFT JOIN users u ON c.assigned_to = u.id;
  ```
- **Verification**: Query returns all 8 rows.

---

### Solution 2: Validation Defect
- **Diagnosis**:
  1. `title: ""` failed `Field(..., min_length=1)` in `CaseCreate`. Empty strings are rejected.
  2. `created_by: "user_42"` passed a string containing characters instead of an integer. `created_by: int` requires a numeric integer (e.g. `42`).
- **Fix**: Client must supply:
  ```json
  {
    "title": "Payment webhook timeout",
    "created_by": 42
  }
  ```

---

### Solution 3: Status Code Violation
- **Diagnosis**: FastAPI defaults all route decorators to `status_code=200 OK` unless explicitly overridden.
- **Fix**: Add `status_code=201` directly to the `@router.post` decorator:
  ```python
  @router.post("/cases", response_model=CaseResponse, status_code=201)
  ```
- **Verification**: Rerun `pytest tests/api/test_cases_api.py` — assertion `assert response.status_code == 201` passes.

---

### Solution 4: Business Rule Defect
- **Diagnosis**: The check was overly aggressive or placed incorrectly. If the rule is "cannot change status of a closed case", check if `"status" in updates and case.status == CaseStatus.CLOSED`.
- **Fix** (as implemented in `app/services/case_service.py`):
  ```python
  if "status" in updates and case.status == CaseStatus.CLOSED:
      raise ValidationError("Cannot change the status of a CLOSED case")
  ```

---

### Solution 5: Error Handling & Masking
- **Diagnosis**: The application lacked a global exception handler for `DatabaseError` or generic `Exception`, so FastAPI's default handler dumped the raw exception details.
- **Fix**: In `app/exceptions/handlers.py`:
  ```python
  @app.exception_handler(DatabaseError)
  async def database_error_handler(request: Request, exc: DatabaseError):
      logger.error("Database error", extra={"detail": exc.message})
      return JSONResponse(
          status_code=500,
          content={"error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred", "details": None}}
      )
  ```

---

### Solution 6: Circular Import
- **Diagnosis**: Module A imported Module B at the top level, and Module B imported Module A at the top level. When Python loads Module A, it pauses to load Module B, which tries to import Module A before Module A is finished loading!
- **Fix**:
  1. Move shared types/schemas into a dedicated neutral file (`app/schemas/` or `app/models/`).
  2. Or, move the import statement inside the specific function that uses it (local import).
