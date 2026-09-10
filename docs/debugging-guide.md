# Operational Debugging & Troubleshooting Guide

## 1. Quick Diagnostic Checklist
When an incident or failure is observed in the service, follow this rapid triage checklist:

- [ ] **Step 1: Check Health Endpoint**: Run `curl http://127.0.0.1:8000/health`. Is the server responding with `200 OK`?
- [ ] **Step 2: Inspect Ingress Logs**: Search console or terminal logs for lines with `"level": "ERROR"` or `"level": "WARNING"`.
- [ ] **Step 3: Run Automated Test Suite**: Run `python -m pytest -v`. Do tests pass locally?
- [ ] **Step 4: Verify Database State**: Does `case_management.db` exist? Can you run `SELECT COUNT(*) FROM cases;`?

---

## 2. Common Failures & Immediate Fixes

### Issue 1: `Port 8000 is already in use` (`OSError: [Errno 10048]`)
- **Symptom**: Uvicorn fails to bind at startup with `Address already in use`.
- **Cause**: A previous Uvicorn instance was left running in the background or another application is occupying port 8000.
- **Resolution (PowerShell)**:
  ```powershell
  # Find process ID using port 8000
  netstat -ano | findstr :8000
  # Terminate the process (replace PID with actual number)
  Stop-Process -Id <PID> -Force
  ```
  Or change the port in `.env` or CLI: `uvicorn app.main:app --port 8001`.

---

### Issue 2: `sqlite3.OperationalError: database is locked`
- **Symptom**: API requests freeze or throw `database is locked`.
- **Cause**: SQLite allows multiple concurrent readers, but only **one single writer** at a time. An uncommitted transaction or unclosed database cursor held a write lock on the database file.
- **Diagnosis**: Look for repository code where `db.commit()` or `db.rollback()` was skipped in an exception block.
- **Resolution**:
  1. Ensure `db.close()` is executed in the `get_db()` generator `finally` block (see `app/database/session.py`).
  2. Verify all write operations in `app/repositories/case_repository.py` call `db.rollback()` inside their `except` blocks.

---

### Issue 3: `Request validation failed (HTTP 422)`
- **Symptom**: POST or PUT requests return 422 Unprocessable Entity.
- **Diagnosis**: Look at the `"details"` array in the JSON response:
  ```json
  {
    "error": {
      "code": "REQUEST_VALIDATION_ERROR",
      "details": [{"field": "body -> title", "message": "Field required"}]
    }
  }
  ```
- **Resolution**:
  - The client omitted a mandatory field or provided an invalid type (e.g. string for integer ID).
  - Cross-reference the payload against [docs/api-specification.md](file:///d:/week1_kpmg/case-management-backend/docs/api-specification.md) or Swagger UI at `/docs`.

---

### Issue 4: `IntegrityError: FOREIGN KEY constraint failed`
- **Symptom**: Database insert fails with a foreign key violation.
- **Diagnosis**: A case was submitted with `created_by = 999`, but no user with `id = 999` exists in the `users` table.
- **Resolution**:
  - Pre-validate existence in the Service layer (`self.user_repo.get_by_id(db, user_id)`) before attempting the insert.
  - This translates low-level SQLite constraint crashes into user-friendly `HTTP 404 USER_NOT_FOUND` errors.

---

### Issue 5: `PendingRollbackError: This Session's transaction has been rolled back due to a previous exception during flush.`
- **Symptom**: A route handler throws `PendingRollbackError` on subsequent queries.
- **Cause**: An earlier database query failed, but the session was not rolled back before being used again.
- **Resolution**: Always wrap database mutations in `try: ... except: db.rollback(); raise`.

---

## 3. Running with Live Debug Logging
To increase log verbosity during active troubleshooting:

1. **Option A: Via `.env` File**:
   Set `LOG_LEVEL=DEBUG` in your local `.env` file.
2. **Option B: Via Environment Variable (PowerShell)**:
   ```powershell
   $env:LOG_LEVEL="DEBUG"
   uvicorn app.main:app --reload
   ```
3. **Option C: Inspecting SQL Statements**:
   In `app/database/session.py`, temporarily set `echo=True` on `create_engine()` to see raw SQL queries emitted to the console in real-time.
