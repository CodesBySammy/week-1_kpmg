# Week 1 Self-Assessment Examination — Answer Key & Solutions

## SCORING GUIDE
- Total Points: 40 Points
- 36 – 40 Points (90%+): Excellent / Senior-Ready Freshness
- 32 – 35 Points (80%+): Pass / Ready for Week 2
- < 32 Points: Review the corresponding modules before proceeding.

---

## SECTION 1: MULTIPLE CHOICE ANSWERS (10 Points)

1. **B — API / Pydantic Schema Validation Layer**
   - *Explanation*: Pydantic schemas (such as `CaseCreate` in `app/schemas/case.py`) validate string bounds (`max_length=5000`) before any controller or database logic runs.
2. **B — `git merge` creates a new merge commit preserving historical topology; `git rebase` replays commits linearly on top of another branch.**
   - *Explanation*: Merge preserves the full non-linear DAG structure; rebase rewrites commit hashes to form a straight line.
3. **B — `PUT /api/v1/cases/42`**
   - *Explanation*: Replacing a resource with `PUT` produces the identical server state whether called once or ten times. `POST` appends new state every time.
4. **C — `PRAGMA foreign_keys = ON;`**
   - *Explanation*: For legacy compatibility, SQLite disables foreign key enforcement by default on new connections unless explicitly activated via this pragma.
5. **B — Caches the returned `Settings` instance so environment variables and `.env` files are only read from disk once.**
   - *Explanation*: `lru_cache` memoizes the parsed object in memory to prevent repeated disk I/O on every incoming request.
6. **C — `LAG()`**
   - *Explanation*: `LAG()` accesses attributes from a previous row at a specified offset within a partition; `LEAD()` looks ahead.
7. **C — `scope="function"`**
   - *Explanation*: Function scope runs fixture setup and teardown for each individual test function, ensuring 100% test isolation.
8. **C — HTTP 500 with a sanitized, generic error code (e.g. `INTERNAL_ERROR`) masking the internal traceback**
   - *Explanation*: Exposing stack traces or database driver errors leaks sensitive paths, versions, and credentials to potential attackers.
9. **B — If test statement coverage falls below 70%, pytest fails the run with exit code 1.**
   - *Explanation*: `fail_under` in `pyproject.toml` sets an automated quality gate for CI/CD test coverage.
10. **B — Transitive dependencies (non-key columns depending on other non-key columns)**
    - *Explanation*: In 3NF, every non-key column must depend directly and only on the primary key, eliminating transitive relationships.

---

## SECTION 2: SHORT ANSWER SOLUTIONS (10 Points)

11. **Why is `except Exception: pass` an unacceptable anti-pattern?**
    - *Model Answer*: Silently catching and passing all exceptions masks catastrophic runtime failures (such as disk write errors, database disconnections, or memory exhaustion). The application continues running in an inconsistent or corrupted state, returns a false 200 OK to the user, writes no log message, and makes diagnosing the root cause nearly impossible.

12. **Explain the purpose of `conftest.py` in pytest and how it enables dependency injection.**
    - *Model Answer*: `conftest.py` is pytest's centralized configuration and shared fixture registry. Fixtures defined in `conftest.py` are automatically discovered across all test files in the directory tree without requiring imports. It enables dependency injection by allowing test functions to declare fixture names as parameters; pytest resolves the dependency graph and injects the instantiated resources (e.g. test client, database session) into the test.

13. **Why should application secrets never be committed to Git, and how does `.env.example` help?**
    - *Model Answer*: Secrets committed to version control are permanently recorded in Git history, exposing systems to credential theft even if deleted in a later commit. Committing an `.env.example` template provides a safe blueprint showing which environment variables are required, with dummy placeholder values, allowing new developers to configure their local `.env` securely.

14. **What is the difference between a Safe HTTP method and an Idempotent HTTP method?**
    - *Model Answer*: A safe method (`GET`, `HEAD`) is strictly read-only and does not modify server resource state. An idempotent method (`PUT`, `DELETE`, `GET`) can modify server state, but calling it multiple times with the same input produces the exact same server state as calling it once. All safe methods are idempotent, but not all idempotent methods are safe.

15. **Why is structured JSON logging preferred over `print()` statements?**
    - *Model Answer*: `print()` writes unstructured, unformatted text to standard output without severity levels, timestamps, or source context. Structured JSON logging outputs machine-readable key-value pairs with consistent schemas (`timestamp`, `level`, `operation`, `case_id`). In cloud environments, these JSON logs can be ingested directly into search and indexing systems (Datadog, CloudWatch, Elasticsearch) for instantaneous filtering and automated alerting.

---

## SECTION 3: SQL CODING SOLUTIONS (8 Points)

16. **Joins Solution**:
    ```sql
    SELECT
        c.title,
        c.status,
        COALESCE(u.full_name, 'UNASSIGNED') AS assignee_name
    FROM cases c
    LEFT JOIN users u ON c.assigned_to = u.id;
    ```
    - *Grading*: Must use `LEFT JOIN` (using `INNER JOIN` drops unassigned cases). Must use `COALESCE` or `CASE` to handle the `NULL` display.

17. **CTE & Window Function Solution**:
    ```sql
    WITH ranked_cases AS (
        SELECT
            id,
            title,
            status,
            created_at,
            ROW_NUMBER() OVER (
                PARTITION BY status
                ORDER BY created_at DESC
            ) AS rn
        FROM cases
    )
    SELECT id, title, status, created_at
    FROM ranked_cases
    WHERE rn = 1;
    ```
    - *Grading*: Must define a CTE via `WITH`. Must use `ROW_NUMBER()` with `PARTITION BY status` and `ORDER BY created_at DESC`. Must filter `WHERE rn = 1` in the outer query.

---

## SECTION 4: PYTHON & FASTAPI SOLUTIONS (6 Points)

18. **Flaws in the Buggy Route Handler**:
    1. **SQL Injection Vulnerability**: String formatting (`f"UPDATE ... {title}"`) allows malicious users to inject raw SQL commands.
    2. **Wrong HTTP Method**: Used `@app.get` for a state mutation (updating a record). Updates must use `PUT` or `PATCH`.
    3. **Missing Resource Routing & Validation**: The URI `/update_case` is RPC-style rather than RESTful (`PUT /cases/{id}`). There are no type hints or Pydantic validation schemas on `id` or `title`.
    4. **Direct Connection in Route**: Opens a raw SQLite connection directly inside the controller instead of using dependency injection and repository abstraction.

19. **Pydantic's `from_attributes=True`**:
    - *Model Answer*: By default, Pydantic expects inputs to be Python dictionaries (`data["title"]`). In SQLAlchemy, query results are ORM class instances whose data is accessed via object attributes (`case.title`). Setting `from_attributes=True` instructs Pydantic to read values from object attributes, enabling direct serialization of SQLAlchemy models into API response schemas without manual dict conversion.

---

## SECTION 5: DEBUGGING SCENARIO (6 Points)

20. **Diagnosis**:
    - In [app/schemas/case.py](file:///d:/week1_kpmg/case-management-backend/app/schemas/case.py), the `created_by` field is declared with the constraint:
      ```python
      created_by: int = Field(..., gt=0)
      ```
    - `gt=0` requires the value to be strictly greater than zero.
    - Passing `created_by: 0` violates this rule, causing Pydantic to automatically reject the request at the boundary and return HTTP 422 Unprocessable Entity with a validation error indicating that the value must be greater than 0.
