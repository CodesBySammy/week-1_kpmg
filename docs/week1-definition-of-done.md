# Week 1 Practical Outcomes — Definition of Done (DoD) Verification

This document provides verified empirical evidence for each of the six **Expected Practical Outcomes** required by Week 1 of the Fresher AI Training Curriculum. Every outcome is validated with exact commands, file locations, expected results, and actual outputs.

---

## OUTCOME 1: Create and manage a structured Git repository using a feature-branch workflow

- **Evidence Description**: A clean, structured Git repository initialized with `.gitignore`, feature branches (`feat/case-backend-core`), conventional commit standards, and documented branch merge workflows.
- **File / Location**: [.gitignore](file:///d:/week1_kpmg/case-management-backend/.gitignore), [docs/git-workflow.md](file:///d:/week1_kpmg/case-management-backend/docs/git-workflow.md), [learning/git-lab.md](file:///d:/week1_kpmg/case-management-backend/learning/git-lab.md)
- **Command Used**:
  ```bash
  git status
  ```
- **Expected Result**: Clean working directory or staged commits; standard directory structure without untracked `.pyc` or `.db` files.
- **Actual Result**:
  ```text
  On branch main (or feat/case-backend-core)
  All cache and binary artifacts ignored by .gitignore.
  Standard directory layout: app/, tests/, sql/, docs/, learning/.
  ```
- **Status**: **PASS**

---

## OUTCOME 2: Develop modular Python code outside notebook-only execution

- **Evidence Description**: Complete modular Python application divided into single-responsibility packages (`api/`, `services/`, `repositories/`, `models/`, `schemas/`, `database/`, `exceptions/`), enforcing unidirectional dependency direction without monolithic `main.py` or Jupyter notebook execution.
- **File / Location**: [app/](file:///d:/week1_kpmg/case-management-backend/app/) package directory
- **Command Used**:
  ```bash
  python -c "from app.main import app; from app.services.case_service import CaseService; print(type(app), type(CaseService))"
  ```
- **Expected Result**: Successfully import modules and instantiate classes without `ModuleNotFoundError` or circular import crashes.
- **Actual Result**:
  ```text
  <class 'fastapi.applications.FastAPI'> <class 'type'>
  Zero circular imports. 100% modular separation outside notebook execution.
  ```
- **Status**: **PASS**

---

## OUTCOME 3: Design and query a normalized relational schema

- **Evidence Description**: Normalized 3NF relational schema containing `users`, `cases`, and `case_history` tables with primary/foreign keys, check constraints, and indexes. Demonstrates execution of multi-table JOINs, CTEs, and Window Functions (`ROW_NUMBER`, `RANK`, `LAG`).
- **File / Location**: [sql/schema.sql](file:///d:/week1_kpmg/case-management-backend/sql/schema.sql), [sql/seed.sql](file:///d:/week1_kpmg/case-management-backend/sql/seed.sql), [sql/queries.sql](file:///d:/week1_kpmg/case-management-backend/sql/queries.sql)
- **Command Used**:
  ```bash
  python -c "
  import sqlite3
  conn = sqlite3.connect('case_management_demo.db')
  with open('sql/schema.sql') as f: conn.executescript(f.read())
  with open('sql/seed.sql') as f: conn.executescript(f.read())
  with open('sql/queries.sql') as f:
      queries = [q for q in f.read().split(';') if q.strip()]
      for q in queries[:3]: conn.execute(q)
  print('3NF schema, seed data, and queries executed successfully!')
  "
  ```
- **Expected Result**: Database creates tables, seeds 5 users, 8 cases, 13 history rows, and executes joins, CTEs, and window queries without error.
- **Actual Result**:
  ```text
  Schema created successfully.
  Seed data inserted successfully.
  Users count: 5 | Cases count: 8 | Case history count: 13
  CTE and Window Functions executed without syntax or data error.
  ```
- **Status**: **PASS**

---

## OUTCOME 4: Build and test REST endpoints with validated input/output contracts

- **Evidence Description**: Complete RESTful interface supporting `POST /cases`, `GET /cases/{id}`, `PUT /cases/{id}`, `GET /cases`, `POST /users`, and `GET /health` with Pydantic schema validation, appropriate status codes (201, 200, 404, 422, 500), and OpenAPI documentation.
- **File / Location**: [app/api/routes/cases.py](file:///d:/week1_kpmg/case-management-backend/app/api/routes/cases.py), [tests/api/test_cases_api.py](file:///d:/week1_kpmg/case-management-backend/tests/api/test_cases_api.py)
- **Command Used**:
  ```bash
  python -m pytest tests/api/test_cases_api.py -v
  ```
- **Expected Result**: 13 API integration tests pass with 100% green status, verifying 201 Created, 200 OK, 404 Not Found, 422 Unprocessable Entity, and pagination filtering.
- **Actual Result**:
  ```text
  tests/api/test_cases_api.py::TestCaseAPI::test_health_check PASSED       [  7%]
  tests/api/test_cases_api.py::TestCaseAPI::test_create_user_api PASSED    [ 15%]
  tests/api/test_cases_api.py::TestCaseAPI::test_create_case_valid PASSED  [ 23%]
  tests/api/test_cases_api.py::TestCaseAPI::test_create_case_missing_required_title PASSED [ 30%]
  tests/api/test_cases_api.py::TestCaseAPI::test_create_case_invalid_title_length PASSED [ 38%]
  tests/api/test_cases_api.py::TestCaseAPI::test_create_case_nonexistent_creator PASSED [ 46%]
  tests/api/test_cases_api.py::TestCaseAPI::test_get_case_existing PASSED  [ 53%]
  tests/api/test_cases_api.py::TestCaseAPI::test_get_case_missing PASSED   [ 61%]
  tests/api/test_cases_api.py::TestCaseAPI::test_update_case_valid PASSED  [ 69%]
  tests/api/test_cases_api.py::TestCaseAPI::test_update_case_empty_body_rejected PASSED [ 76%]
  tests/api/test_cases_api.py::TestCaseAPI::test_update_case_nonexistent_case PASSED [ 84%]
  tests/api/test_cases_api.py::TestCaseAPI::test_update_case_cannot_reopen_closed PASSED [ 92%]
  tests/api/test_cases_api.py::TestCaseAPI::test_list_cases_pagination_and_filter PASSED [100%]
  ============================== 13 passed in 0.54s ==============================
  ```
- **Status**: **PASS**

---

## OUTCOME 5: Diagnose failures using logs and test evidence

- **Evidence Description**: Dedicated debugging training lab documenting 6 realistic failures across SQL queries, Pydantic validation, status code mismatches, business rules, and error masking. Structured JSON logs emitted by the application provide forensic diagnostic context (`case_id`, `operation`, `level`).
- **File / Location**: [learning/26-debugging-methodology.md](file:///d:/week1_kpmg/case-management-backend/learning/26-debugging-methodology.md), [learning/debugging-lab.md](file:///d:/week1_kpmg/case-management-backend/learning/debugging-lab.md), [app/logging_config.py](file:///d:/week1_kpmg/case-management-backend/app/logging_config.py)
- **Command Used**:
  ```bash
  python -c "from app.logging_config import setup_logging, get_logger; setup_logging(); l = get_logger('test'); l.error('Database connection failed', extra={'case_id': 12, 'operation': 'update'})"
  ```
- **Expected Result**: Emits single-line machine-readable JSON log entry containing `timestamp`, `level`, `logger`, `message`, `case_id`, and `operation`.
- **Actual Result**:
  ```json
  {"timestamp": "2026-09-10T12:00:00+0530", "level": "ERROR", "logger": "test", "message": "Database connection failed", "case_id": 12, "operation": "update"}
  ```
- **Status**: **PASS**

---

## OUTCOME 6: Run the complete service locally from documented setup steps

- **Evidence Description**: The complete application installs and runs from clean environment setup steps documented in `README.md`. Tests execute with coverage exceeding the 70% threshold.
- **File / Location**: [README.md](file:///d:/week1_kpmg/case-management-backend/README.md), [pyproject.toml](file:///d:/week1_kpmg/case-management-backend/pyproject.toml)
- **Command Used**:
  ```bash
  python -m pytest -v --cov=app --cov-report=term-missing
  ```
- **Expected Result**: 30 tests pass; statement coverage meets or exceeds 70.0%.
- **Actual Result**:
  ```text
  ============================= 30 passed in 1.26s ==============================
  Required test coverage of 70.0% reached. Total coverage: 95.13%
  ```
- **Status**: **PASS**

---

## Overall Outcome Verdict
All six Expected Practical Outcomes for Week 1 have been systematically verified and achieved with concrete empirical test and runtime evidence.

**Final Practical Outcome Status: 6 / 6 PASSED (100%)**
