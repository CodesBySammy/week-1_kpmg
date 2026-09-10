# Week 1 Comprehensive Self-Assessment Exam

## Exam Instructions
- This exam covers all Week 1 technical learning objectives: Python modular architecture, Git workflows, Relational SQL, FastAPI, pytest testing, exception handling, and structured logging.
- **Do not look at the answer key** until you have written out your answers completely.
- Time Limit: 60 minutes.
- Passing Score: 80% (32 / 40 points).

---

## SECTION 1: MULTIPLE CHOICE QUESTIONS (10 Points)

1. In a multi-tier enterprise backend architecture, which layer is responsible for enforcing that a ticket description cannot exceed 5,000 characters?
   - A) Database Storage Engine
   - B) API / Pydantic Schema Validation Layer
   - C) UI Presentation Layer
   - D) Operating System Shell

2. What is the fundamental difference between `git merge` and `git rebase`?
   - A) `git merge` deletes the feature branch, while `git rebase` preserves it.
   - B) `git merge` creates a new merge commit preserving historical topology; `git rebase` replays commits linearly on top of another branch.
   - C) `git rebase` is used exclusively for remote repositories.
   - D) `git merge` requires internet connectivity.

3. Which of the following is an example of an IDEMPOTENT HTTP operation?
   - A) `POST /api/v1/cases`
   - B) `PUT /api/v1/cases/42`
   - C) Sending a payment processing request via `POST /charge`
   - D) Appending an audit log entry via `POST /logs`

4. When SQLite is used as an embedded relational database engine, what command must be executed on each new connection to enforce foreign key referential integrity?
   - A) `ENABLE FOREIGN KEYS;`
   - B) `SET FOREIGN_KEYS = 1;`
   - C) `PRAGMA foreign_keys = ON;`
   - D) `ALTER DATABASE ENFORCE KEYS;`

5. What does the `@lru_cache()` decorator do when applied to our `get_settings()` configuration function in `app/config.py`?
   - A) Encrypts the database password in memory.
   - B) Caches the returned `Settings` instance so environment variables and `.env` files are only read from disk once.
   - C) Clears the cache on every HTTP request.
   - D) Generates a random session token.

6. Which SQL window function calculates values based on the immediately preceding row within a partition?
   - A) `LEAD()`
   - B) `ROW_NUMBER()`
   - C) `LAG()`
   - D) `DENSE_RANK()`

7. In pytest, what scope should a test database fixture use if each test function requires a completely clean, isolated database state?
   - A) `scope="session"`
   - B) `scope="module"`
   - C) `scope="function"`
   - D) `scope="package"`

8. If an API endpoint catches an unexpected `sqlalchemy.exc.OperationalError` (database failure), what should it return to the external client?
   - A) HTTP 200 with `{"error": "Database error"}`
   - B) HTTP 500 with the full Python stack trace and database credentials
   - C) HTTP 500 with a sanitized, generic error code (e.g. `INTERNAL_ERROR`) masking the internal traceback
   - D) The client should receive no response and time out

9. What does the `fail_under = 70` setting in `pyproject.toml` enforce?
   - A) The maximum latency of the API must be under 70ms.
   - B) If test statement coverage falls below 70%, pytest fails the run with exit code 1.
   - C) At most 70 tests can be run in parallel.
   - D) The database connection pool size cannot exceed 70.

10. In Third Normal Form (3NF), which type of dependency is strictly prohibited?
    - A) Functional dependencies on the primary key
    - B) Transitive dependencies (non-key columns depending on other non-key columns)
    - C) Foreign key references to parent tables
    - D) Composite primary keys

---

## SECTION 2: SHORT ANSWER & CONCEPTUAL QUESTIONS (10 Points)

11. Why is writing `except Exception: pass` considered an unacceptable anti-pattern in production backend code?
12. Explain the purpose of `conftest.py` in pytest and how it enables dependency injection.
13. Why should application secrets (API keys, database passwords) never be committed to Git, and how does `.env.example` help?
14. What is the difference between a Safe HTTP method and an Idempotent HTTP method?
15. Explain why structured JSON logging is preferred over `print()` statements in containerized and cloud architectures.

---

## SECTION 3: SQL CODING CHALLENGES (8 Points)

16. **Joins Challenge**: Write a SQL query against our project schema that returns the `title` and `status` of all cases, along with the `full_name` of the assignee. Crucially, unassigned cases must still appear in the results with the assignee name displaying `'UNASSIGNED'`.

17. **CTE & Window Function Challenge**: Using a Common Table Expression (`WITH ...`) and the `ROW_NUMBER()` window function, write a query that returns the single most recently created case for each `status` category.

---

## SECTION 4: PYTHON & FASTAPI ARCHITECTURE CHALLENGES (6 Points)

18. Look at the following buggy route handler. Identify three severe architectural or design flaws:
    ```python
    @app.get("/update_case")
    def update_case(id, title):
        conn = sqlite3.connect("prod.db")
        conn.execute(f"UPDATE cases SET title = '{title}' WHERE id = {id}")
        conn.commit()
        return "OK"
    ```

19. Explain how Pydantic's `ConfigDict(from_attributes=True)` enables seamless interoperability between SQLAlchemy ORM models and API response schemas.

---

## SECTION 5: DEBUGGING SCENARIOS (6 Points)

20. **Scenario**: When running `python -m pytest`, the test suite fails with:
    ```text
    E   AssertionError: assert 422 == 201
    E    +  where 422 = <Response [422 Unprocessable Entity]>.status_code
    ```
    The test was attempting to create a case with `{"title": "Bug", "created_by": 0}`.
    Diagnose why the endpoint returned 422 rather than 201.
