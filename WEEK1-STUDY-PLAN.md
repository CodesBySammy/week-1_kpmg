# Week 1 Structured Study Plan: From Fresher to Backend Engineer

## 1. Study Philosophy: Learn by Building
> **Core Rule**: Do NOT merely read documentation passively. The project drives the learning!  
> For every single module, follow the cycle:  
> **LEARN → PRACTICE → BUILD → TEST → DEBUG → DOCUMENT → REVIEW**

This 5-day structured plan is designed for an intensive 40-hour learning sprint, moving systematically from foundational architecture to production-grade deployment and testing.

---

## Day 1: System Anatomy, Git Discipline & Modular Python

### Session 1.1: FDE Architecture & Solution Anatomy
- **Topics**: The 5 enterprise tiers (UI, API, Data, AI, Integration), layer boundaries, and where Week 1 fits.
- **Files to Read**: [learning/00-week1-overview.md](file:///d:/week1_kpmg/case-management-backend/learning/00-week1-overview.md), [learning/01-fde-solution-anatomy.md](file:///d:/week1_kpmg/case-management-backend/learning/01-fde-solution-anatomy.md), [docs/architecture.md](file:///d:/week1_kpmg/case-management-backend/docs/architecture.md)
- **Hands-on Practice**: Draw the 5 layers on paper. Map each folder in `app/` to its corresponding architectural tier.
- **Estimated Difficulty**: Beginner (2 Hours)
- **Oral Defense**: "Explain why the UI must never connect directly to the database."

### Session 1.2: Git Version Control, Feature Branching & Merge Conflicts
- **Topics**: Working tree, staging area, commits, feature branches, pull requests, merge conflict mechanics.
- **Files to Read**: [learning/02-git.md](file:///d:/week1_kpmg/case-management-backend/learning/02-git.md), [docs/git-workflow.md](file:///d:/week1_kpmg/case-management-backend/docs/git-workflow.md)
- **Hands-on Practice**: Complete the hands-on lab in [learning/git-lab.md](file:///d:/week1_kpmg/case-management-backend/learning/git-lab.md). Intentionally create a merge conflict, resolve it manually, and inspect the Git graph with `git log --graph --oneline`.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "What is the difference between `git merge` and `git rebase`?"

### Session 1.3: Python Modular Architecture & Separation of Concerns
- **Topics**: Modules, packages (`__init__.py`), classes, functions, unidirectional dependency direction, avoiding the monolithic `main.py` anti-pattern.
- **Files to Read**: [learning/03-python-modular-engineering.md](file:///d:/week1_kpmg/case-management-backend/learning/03-python-modular-engineering.md)
- **Project Code to Inspect**: [app/main.py](file:///d:/week1_kpmg/case-management-backend/app/main.py), [app/services/case_service.py](file:///d:/week1_kpmg/case-management-backend/app/services/case_service.py), [app/repositories/case_repository.py](file:///d:/week1_kpmg/case-management-backend/app/repositories/case_repository.py)
- **Hands-on Practice**: Add a helper method to `CaseService` that calculates days elapsed since creation. Verify that it requires zero changes to the database repository.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "Why must the repository layer never import from the API routes layer?"

---

## Day 2: Relational Databases, Normalization & Advanced SQL

### Session 2.1: Relational Modeling & 3NF Schema Design
- **Topics**: Primary keys, surrogate vs. natural keys, foreign keys, cascade rules, 1NF/2NF/3NF normalization.
- **Files to Read**: [learning/13-relational-databases.md](file:///d:/week1_kpmg/case-management-backend/learning/13-relational-databases.md), [learning/14-sql-schema-design.md](file:///d:/week1_kpmg/case-management-backend/learning/14-sql-schema-design.md), [docs/database-design.md](file:///d:/week1_kpmg/case-management-backend/docs/database-design.md)
- **Project Code to Inspect**: [sql/schema.sql](file:///d:/week1_kpmg/case-management-backend/sql/schema.sql), [app/models/case.py](file:///d:/week1_kpmg/case-management-backend/app/models/case.py)
- **Hands-on Practice**: Initialize SQLite and load `schema.sql` and `seed.sql`. Inspect constraints using SQLite CLI.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "Why do we store the ticket audit history in a separate append-only table (`case_history`)?"

### Session 2.2: SQL JOINs & The N+1 Query Problem
- **Topics**: INNER JOIN, LEFT JOIN, multiple joins, table aliases, aggregation with joins, preventing N+1 queries.
- **Files to Read**: [learning/15-sql-joins.md](file:///d:/week1_kpmg/case-management-backend/learning/15-sql-joins.md)
- **Project Code to Inspect**: [sql/queries.sql](file:///d:/week1_kpmg/case-management-backend/sql/queries.sql) (Section 1)
- **Hands-on Practice**: Execute Section 1 queries. Write a query returning all users who have never opened a case.
- **Estimated Difficulty**: Intermediate (2 Hours)
- **Oral Defense**: "Why does an INNER JOIN drop unassigned tickets, and why is LEFT JOIN mandatory?"

### Session 2.3: CTEs, Window Functions & ACID Transactions
- **Topics**: Common Table Expressions (`WITH`), ranking window functions (`ROW_NUMBER`, `RANK`), offset functions (`LAG`), running totals, ACID guarantees, rollback mechanics.
- **Files to Read**: [learning/16-sql-ctes.md](file:///d:/week1_kpmg/case-management-backend/learning/16-sql-ctes.md), [learning/17-sql-window-functions.md](file:///d:/week1_kpmg/case-management-backend/learning/17-sql-window-functions.md), [learning/18-sql-transactions.md](file:///d:/week1_kpmg/case-management-backend/learning/18-sql-transactions.md)
- **Project Code to Inspect**: [sql/queries.sql](file:///d:/week1_kpmg/case-management-backend/sql/queries.sql) (Sections 2 & 3), [sql/transaction_examples.sql](file:///d:/week1_kpmg/case-management-backend/sql/transaction_examples.sql)
- **Hands-on Practice**: Execute transaction examples with `ROLLBACK` and verify that no changes persist.
- **Estimated Difficulty**: Advanced (3 Hours)
- **Oral Defense**: "How does a window function differ fundamentally from a `GROUP BY` aggregation?"

---

## Day 3: RESTful APIs, Pydantic Validation & FastAPI

### Session 3.1: REST Fundamentals & HTTP Methods
- **Topics**: Resource-oriented URIs (nouns, not verbs), statelessness, safety and idempotency, GET/POST/PUT/DELETE.
- **Files to Read**: [learning/19-rest-api-fundamentals.md](file:///d:/week1_kpmg/case-management-backend/learning/19-rest-api-fundamentals.md), [learning/20-http-methods.md](file:///d:/week1_kpmg/case-management-backend/learning/20-http-methods.md)
- **Project Code to Inspect**: [app/api/routes/cases.py](file:///d:/week1_kpmg/case-management-backend/app/api/routes/cases.py)
- **Hands-on Practice**: Use `curl` or PowerShell to send GET, POST, and PUT requests to the local server.
- **Estimated Difficulty**: Beginner to Intermediate (2 Hours)
- **Oral Defense**: "Why is PUT idempotent while POST is non-idempotent?"

### Session 3.2: Request Validation with Pydantic & Status Codes
- **Topics**: Pydantic schemas, `Field()` constraints, enums, automatic 422 generation, semantic HTTP status codes (200, 201, 404, 422, 500).
- **Files to Read**: [learning/21-request-validation.md](file:///d:/week1_kpmg/case-management-backend/learning/21-request-validation.md), [learning/22-http-status-codes.md](file:///d:/week1_kpmg/case-management-backend/learning/22-http-status-codes.md)
- **Project Code to Inspect**: [app/schemas/case.py](file:///d:/week1_kpmg/case-management-backend/app/schemas/case.py)
- **Hands-on Practice**: Send malformed payloads (empty title, negative ID) and inspect the structured 422 error response.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "What is the difference between HTTP 400 Bad Request and HTTP 422 Unprocessable Entity?"

### Session 3.3: OpenAPI Specification & API Error Contracts
- **Topics**: OpenAPI 3.1, Swagger UI (`/docs`), ReDoc (`/redoc`), standardized error envelope, zero-traceback policy.
- **Files to Read**: [learning/23-openapi.md](file:///d:/week1_kpmg/case-management-backend/learning/23-openapi.md), [learning/24-api-error-contracts.md](file:///d:/week1_kpmg/case-management-backend/learning/24-api-error-contracts.md), [docs/api-specification.md](file:///d:/week1_kpmg/case-management-backend/docs/api-specification.md)
- **Project Code to Inspect**: [docs/openapi.json](file:///d:/week1_kpmg/case-management-backend/docs/openapi.json), [app/exceptions/handlers.py](file:///d:/week1_kpmg/case-management-backend/app/exceptions/handlers.py)
- **Hands-on Practice**: Open `http://127.0.0.1:8000/docs` in your browser. Test creating and updating a case directly in the interactive UI.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "Why should an API never return a raw Python stack trace to an external client?"

---

## Day 4: Automated Testing, Fixtures, Mocks & Observability

### Session 4.1: pytest & The Testing Pyramid
- **Topics**: Unit tests, integration tests, native assertions, test discovery conventions, AAA pattern.
- **Files to Read**: [learning/08-pytest.md](file:///d:/week1_kpmg/case-management-backend/learning/08-pytest.md), [learning/09-unit-testing.md](file:///d:/week1_kpmg/case-management-backend/learning/09-unit-testing.md)
- **Project Code to Inspect**: [tests/unit/test_case_service.py](file:///d:/week1_kpmg/case-management-backend/tests/unit/test_case_service.py)
- **Hands-on Practice**: Run `python -m pytest -v`. Inspect test collection and execution timing.
- **Estimated Difficulty**: Intermediate (2 Hours)
- **Oral Defense**: "What are the three steps in the AAA testing pattern?"

### Session 4.2: pytest Fixtures, conftest.py & Rational Mocking
- **Topics**: `conftest.py`, fixture scopes, `yield` setup/teardown, dependency injection overrides, `unittest.mock.MagicMock`, when NOT to mock.
- **Files to Read**: [learning/10-pytest-fixtures.md](file:///d:/week1_kpmg/case-management-backend/learning/10-pytest-fixtures.md), [learning/11-mocking.md](file:///d:/week1_kpmg/case-management-backend/learning/11-mocking.md), [docs/testing-strategy.md](file:///d:/week1_kpmg/case-management-backend/docs/testing-strategy.md)
- **Project Code to Inspect**: [tests/conftest.py](file:///d:/week1_kpmg/case-management-backend/tests/conftest.py)
- **Hands-on Practice**: Trace how `client` overrides `get_db` to point to in-memory SQLite. Write a new unit test with a mocked repository method.
- **Estimated Difficulty**: Advanced (3 Hours)
- **Oral Defense**: "Why do we mock the repository in service tests, but use a real SQLite database in API integration tests?"

### Session 4.3: Test Coverage & Structured JSON Logging
- **Topics**: Statement and branch coverage, `pytest-cov`, `fail_under = 70`, machine-readable JSON logging, logging security (PII redaction).
- **Files to Read**: [learning/07-python-structured-logging.md](file:///d:/week1_kpmg/case-management-backend/learning/07-python-structured-logging.md), [learning/12-test-coverage.md](file:///d:/week1_kpmg/case-management-backend/learning/12-test-coverage.md), [docs/logging-and-error-handling.md](file:///d:/week1_kpmg/case-management-backend/docs/logging-and-error-handling.md)
- **Project Code to Inspect**: [app/logging_config.py](file:///d:/week1_kpmg/case-management-backend/app/logging_config.py)
- **Hands-on Practice**: Run `python -m pytest --cov=app --cov-report=html`. Open `htmlcov/index.html` and review line coverage.
- **Estimated Difficulty**: Intermediate (3 Hours)
- **Oral Defense**: "Why does 100% line coverage NOT mean zero bugs?"

---

## Day 5: Forensic Debugging, Code Review & Capstone Defense

### Session 5.1: Forensic Debugging Lab
- **Topics**: The 9-step hypothesis-driven debugging process, reading tracebacks from the bottom up, log analysis.
- **Files to Read**: [learning/26-debugging-methodology.md](file:///d:/week1_kpmg/case-management-backend/learning/26-debugging-methodology.md), [docs/debugging-guide.md](file:///d:/week1_kpmg/case-management-backend/docs/debugging-guide.md)
- **Hands-on Practice**: Complete all 6 scenarios in [learning/debugging-lab.md](file:///d:/week1_kpmg/case-management-backend/learning/debugging-lab.md). Diagnose each defect from evidence before looking at solutions.
- **Estimated Difficulty**: Advanced (3 Hours)
- **Oral Defense**: "Walk me through your troubleshooting steps when a production endpoint returns 500 errors."

### Session 5.2: Self-Assessment Exam & Interview Preparation
- **Topics**: Comprehensive review of all Week 1 knowledge areas.
- **Files to Read**: [learning/week1-interview-questions.md](file:///d:/week1_kpmg/case-management-backend/learning/week1-interview-questions.md)
- **Hands-on Practice**: Take the 40-point exam in [learning/week1-self-assessment.md](file:///d:/week1_kpmg/case-management-backend/learning/week1-self-assessment.md) in exam conditions. Grade yourself using [learning/week1-self-assessment-answers.md](file:///d:/week1_kpmg/case-management-backend/learning/week1-self-assessment-answers.md).
- **Estimated Difficulty**: Advanced (3 Hours)
- **Target Score**: >= 32 / 40 Points (80%).

### Session 5.3: Oral Defense & Capstone Sign-off
- **Topics**: Defense of architecture, ADRs, and live system demonstration.
- **Files to Read**: [docs/decisions.md](file:///d:/week1_kpmg/case-management-backend/docs/decisions.md), [docs/final-code-review.md](file:///d:/week1_kpmg/case-management-backend/docs/final-code-review.md), [docs/final-capstone-check.md](file:///d:/week1_kpmg/case-management-backend/docs/final-capstone-check.md)
- **Hands-on Practice**: Perform a clean installation from scratch following [README.md](file:///d:/week1_kpmg/case-management-backend/README.md). Verify all 30 tests pass.
- **Estimated Difficulty**: Intermediate (2 Hours)
- **Final Outcome**: Sign off on all items in `docs/final-capstone-check.md`. Ready for Week 2!
