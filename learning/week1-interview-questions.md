# Week 1 Technical Interview Questions & Architectural Pitch Guide

## PART I: THE 2-MINUTE ELEVATOR PITCHES

### 1. "Explain your Week 1 project in 2 minutes."
> **Model Answer**:
> "In Week 1, I engineered an enterprise Case Management Backend using Python, FastAPI, and a normalized relational SQLite database via SQLAlchemy. The service manages the full lifecycle of customer issues and system defects with strict domain validation, auditability, and observability.
> 
> Architecturally, it follows a clean multi-tiered design with complete separation of concerns: thin FastAPI route controllers, Pydantic schemas for request validation, a domain service layer for business rules, and a repository layer for isolated data access and transactions. 
> 
> The database schema is normalized to Third Normal Form with users, cases, and an append-only audit log that records every field change to enable SLA tracking and historical analysis. 
> 
> Reliability is guaranteed through a comprehensive test suite of 30 unit and integration tests using pytest, test fixtures, and in-memory test databases, achieving over 95% statement coverage. Finally, the service implements structured JSON logging and a predictable error contract that masks internal database stack traces while providing fine-grained error codes to API consumers."

---

### 2. "Explain your architecture and dependency flow."
> **Model Answer**:
> "Our architecture enforces a strict unidirectional dependency rule: **Routes → Services → Repositories → Database**. 
> - The **API layer** (`app/api/routes/`) handles HTTP semantics, routing, and status codes (such as returning 201 for case creation).
> - The **Schema layer** (`app/schemas/`) uses Pydantic DTOs to validate input types, string lengths, and enums at the boundary.
> - The **Service layer** (`app/services/`) encapsulates core business logic — for example, verifying user existence and forbidding status changes on closed cases.
> - The **Repository layer** (`app/repositories/`) isolates all SQLAlchemy ORM operations and transaction rollbacks.
> 
> Dependencies never point backwards. Routes never write SQL, and repositories know nothing about HTTP status codes. This ensures business logic can be unit-tested with mocks without starting a server or database."

---

### 3. "Why did you choose SQLite over PostgreSQL for this implementation?"
> **Model Answer**:
> "We selected SQLite as our primary implementation for three practical reasons:
> 1. **Zero-Friction Local Reproducibility**: SQLite is built into Python's standard library. Any engineer or CI/CD runner can clone the repository, run `pytest`, and start the service with zero Docker daemon dependencies or external network services.
> 2. **Full Relational & ANSI SQL Capabilities**: SQLite fully supports the advanced relational features required by our curriculum, including foreign key constraints, multi-table JOINs, Common Table Expressions (CTEs), and Window Functions (`ROW_NUMBER`, `RANK`, `LAG`).
> 3. **Clean Migration Path**: Because our application abstracts all database interactions through SQLAlchemy ORM and the Repository pattern, switching to PostgreSQL in a later enterprise phase requires changing exactly one environment variable (`DATABASE_URL=postgresql://...`) in `.env` without modifying a single line of business logic."

---

### 4. "How do your API error contracts work?"
> **Model Answer**:
> "All API errors adhere to a standardized, machine-readable envelope: `{ "error": { "code": "...", "message": "...", "details": ... } }`.
> 
> In `app/exceptions/`, we created a custom domain exception hierarchy inheriting from `AppError` — such as `CaseNotFoundError`, `UserNotFoundError`, and `ValidationError`. Global FastAPI exception handlers intercept these domain exceptions and translate them into their corresponding HTTP status codes: 404 for missing entities and 422 for domain validation failures.
> 
> Crucially, for unexpected database or internal errors, our global handler logs the complete stack trace and query internally for engineering diagnostics, but returns a generic `500 INTERNAL_ERROR` to the client. This prevents information leakage of server paths, library versions, or database credentials."

---

### 5. "How do you test the API?"
> **Model Answer**:
> "We follow the Testing Pyramid across two layers in `tests/`:
> 1. **Unit Tests (`tests/unit/`)**: We test the `CaseService` in pure isolation using `unittest.mock.MagicMock` to stub out repositories and verify business rules (e.g. verifying that creating a case with a non-existent creator ID raises `UserNotFoundError`).
> 2. **API Integration Tests (`tests/api/`)**: We use FastAPI's `TestClient` paired with a custom pytest fixture in `conftest.py`. The fixture uses FastAPI's `dependency_overrides` mechanism to redirect `get_db` to a fresh, isolated in-memory SQLite database for every test function. This exercises the entire HTTP request/response cycle, Pydantic validation, and real database writes without cross-test data pollution.
> 
> Our automated suite runs 30 tests in approximately 1.3 seconds and achieves 95.1% code coverage."

---

### 6. "How would you debug a failing production endpoint?"
> **Model Answer**:
> "I follow a systematic 9-step hypothesis-driven approach:
> 1. **Inspect Structured Logs**: I query our log aggregation platform for `level == 'ERROR'` or `WARNING` and locate the event by endpoint path or timestamp. Because we use structured JSON logging, I immediately inspect metadata fields like `case_id`, `operation`, and error stack traces.
> 2. **Isolate and Reproduce**: Using the logged payload, I attempt to reproduce the failure locally via a minimal API call or directly in `pytest`.
> 3. **Write a Failing Test**: Before writing any code, I write an automated test in `tests/api/` that captures the failing condition.
> 4. **Apply Targeted Fix**: I correct the root cause in the service or repository.
> 5. **Verify and Audit**: I rerun the focused test to see it turn green, then run the full suite to verify zero regressions before committing with a conventional commit."

---

## PART II: TOPIC-BY-TOPIC TECHNICAL INTERVIEW QUESTIONS

### Category 1: Git & Version Control
**Q1 (Beginner): What is the staging area in Git and why do we need it?**
*Answer:* The staging area (or index) is an intermediate buffer between your local working tree and the permanent Git commit history. It allows you to selectively stage specific files or individual lines (`git add -p`) to craft clean, atomic commits representing a single logical change rather than dumping every modified file into one messy commit.

**Q2 (Intermediate): How do you resolve a Git merge conflict?**
*Answer:* When Git cannot automatically reconcile concurrent modifications to the same lines, it halts the merge and inserts conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>> branch_name`). To resolve it: (1) open the conflicted file, (2) analyze both versions and manually reconcile the intended code, (3) delete the conflict markers, (4) stage the resolved file with `git add`, and (5) finalize the merge commit with `git commit`.

---

### Category 2: Python & Object-Oriented Engineering
**Q3 (Intermediate): What is the difference between a class attribute and an instance attribute in Python?**
*Answer:* A class attribute is defined directly inside the class body and is shared across all instances of that class (e.g. `__tablename__ = "cases"` in a SQLAlchemy model). An instance attribute is bound to a specific instance (typically inside `__init__` via `self.title = title`), so each object maintains its own independent copy.

**Q4 (Intermediate): Why should you avoid mutable default arguments like `def func(items=[])` in Python?**
*Answer:* In Python, default parameter expressions are evaluated once when the function is defined, not each time it is called. If a mutable object (like a list or dictionary) is used as a default, all subsequent calls to the function that omit the parameter will mutate and share the exact same underlying object. The safe pattern is `def func(items: list | None = None): items = items if items is not None else []`.

---

### Category 3: SQL & Relational Databases
**Q5 (Beginner): Why is a surrogate primary key preferred over a natural primary key?**
*Answer:* Natural keys (such as email addresses or phone numbers) have real-world business meaning and are subject to change. If an email is used as a primary key and referenced by hundreds of foreign key rows, changing the user's email requires cascading updates across every referencing table. A surrogate key (like an auto-incrementing integer) has no business meaning, is immutable, and ensures permanent referential stability.

**Q6 (Intermediate): Explain the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()`.**
*Answer:* All three are SQL window functions that assign integer rankings within a partition based on an order. They differ in tie handling: `ROW_NUMBER()` assigns distinct consecutive numbers (1, 2, 3) arbitrarily breaking ties. `RANK()` assigns identical numbers to ties and skips subsequent numbers (1, 1, 3). `DENSE_RANK()` assigns identical numbers to ties without skipping subsequent numbers (1, 1, 2).

**Q7 (Advanced): What is a Common Table Expression (CTE) and when would you use it instead of a subquery?**
*Answer:* A CTE is a temporary named result set defined using the `WITH` clause before a primary SQL statement. CTEs are preferred over subqueries because they break complex data transformations into sequential, readable steps, eliminate duplicate subquery execution, and support recursive graph/hierarchy traversals.

---

### Category 4: FastAPI & REST APIs
**Q8 (Intermediate): How does FastAPI implement Dependency Injection, and how does it benefit testing?**
*Answer:* FastAPI uses the `Depends()` marker in route parameter lists to declare dependencies (such as database sessions or authentication providers). At runtime, FastAPI resolves and executes the dependency before invoking the route. In tests, dependencies can be swapped without modifying application code using `app.dependency_overrides[get_db] = override_func`, allowing tests to run against in-memory databases or mock services seamlessly.

**Q9 (Intermediate): What is the difference between HTTP 400, 404, and 422?**
*Answer:* HTTP 400 (Bad Request) means the request was syntactically invalid (e.g. corrupted JSON or malformed headers). HTTP 404 (Not Found) means the requested URI path or entity identifier does not exist. HTTP 422 (Unprocessable Entity) means the request was syntactically valid JSON, but violated semantic domain or schema validation rules (e.g. missing required fields, strings failing length limits).
