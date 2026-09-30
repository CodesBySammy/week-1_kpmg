# Week 1 Capstone Mastery & Oral Defense Checklist

Use this checklist to prepare for your final Week 1 oral technical review with your engineering mentor. You must be prepared to demonstrate, code, or verbally explain each item without reading from notes.

---

## 1. Architectural & Domain Mastery
- [ ] **I can explain the architecture**: I can draw the 5-layer FDE solution anatomy on a whiteboard and explain where this backend lives.
- [ ] **I can explain the Python project structure**: I can explain the responsibility of `api/`, `services/`, `repositories/`, `models/`, `schemas/`, `database/`, and `exceptions/` without hesitating.
- [ ] **I can explain the project without reading code**: I can deliver the 2-minute elevator pitch describing what the Case Management service does, why it was built, and how it handles state transitions.

---

## 2. Source Control & Workflow
- [ ] **I can explain the Git workflow**: I can explain the difference between `main` and feature branches, and write a conventional commit message.
- [ ] **I can resolve merge conflicts**: I can explain what `<<<<<<< HEAD` means and demonstrate manual conflict resolution using the command line.

---

## 3. Database & Relational SQL
- [ ] **I can explain the database schema**: I can explain why `users`, `cases`, and `case_history` are separated into distinct tables (3NF normalization) to prevent update anomalies.
- [ ] **I can write joins**: I can explain the critical difference between `INNER JOIN` and `LEFT JOIN` when querying cases with nullable assignees.
- [ ] **I can write a Common Table Expression (CTE)**: I can write a `WITH ... AS (...)` query to modularize complex multi-step aggregations.
- [ ] **I can use a Window Function**: I can write a query using `ROW_NUMBER()`, `RANK()`, or `LAG()` with an `OVER (PARTITION BY ... ORDER BY ...)` clause and explain why window functions do not collapse rows like `GROUP BY`.
- [ ] **I understand transactions & ACID**: I can explain Atomicity, Consistency, Isolation, and Durability, and describe how `BEGIN`, `COMMIT`, `ROLLBACK`, and `SAVEPOINT` guarantee data integrity.

---

## 4. REST APIs, Validation & Contracts
- [ ] **I can explain REST methods**: I can explain why `GET` is safe and idempotent, why `PUT` is idempotent, and why `POST` is non-idempotent.
- [ ] **I can explain status codes**: I can explain the exact distinction between `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, and `422 Unprocessable Entity`.
- [ ] **I understand request validation**: I can explain how Pydantic's `Field(min_length=1, gt=0)` enforces validation at the API boundary before code hits the database.
- [ ] **I understand OpenAPI**: I can explain how FastAPI automatically generates the OpenAPI specification from Python type hints and how clients consume Swagger UI at `/docs`.
- [ ] **I understand API error contracts**: I can explain the structure of our `{ "error": { "code", "message", "details" } }` envelope and why internal database stack traces must never leak to API consumers.

---

## 5. Testing & Observability
- [ ] **I can explain pytest**: I can write an automated test function using Python's native `assert` keyword.
- [ ] **I can explain fixtures**: I can explain how `conftest.py` provides dependency injection and how `yield` handles setup and teardown for in-memory test databases.
- [ ] **I can explain mocks**: I can explain when to use `unittest.mock.MagicMock` to isolate business logic, and why we do NOT mock the database in repository or API tests.
- [ ] **I understand code coverage**: I can run `pytest --cov` and explain why 100% line coverage does not guarantee 0% bugs.
- [ ] **I can interpret structured logs**: I can explain the difference between unstructured `print()` and machine-readable JSON logs with `case_id` metadata.
- [ ] **I can diagnose a failing test**: I can read a Python traceback from the bottom up, formulate a hypothesis, and apply a targeted fix using the 9-step debugging methodology.
- [ ] **I can run the project from scratch**: I can clone the repository onto a brand-new laptop, follow the README, and have the backend and test suite running in under 2 minutes.
