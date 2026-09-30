# Module 10: pytest Fixtures, conftest.py & Dependency Injection

## 1. What It Is
A **pytest fixture** is a modular, reusable function decorated with `@pytest.fixture` that prepares a baseline environment, data, or state before a test executes, and optionally cleans up resources after the test completes.

## 2. Why It Exists
Before fixtures, developers had to manually write setup boilerplate at the top of every test function:
```python
def test_something():
    db = create_test_db()
    user = create_test_user(db)
    # test logic...
    cleanup_db(db)
```
If you had 100 tests, this boilerplate was duplicated 100 times. If the database initialization logic changed, you had to edit 100 files. Fixtures eliminate this duplication through **Dependency Injection**.

## 3. Why Backend Engineers Use It
- **Declarative Dependency Management**: A test function simply declares what it needs in its argument list:
  ```python
  def test_get_case(client, sample_case):  # pytest injects these automatically!
  ```
- **Automated Teardown**: Using the `yield` statement guarantees that database tables, files, or network sockets are safely closed, even if the test crashes mid-execution.
- **Hierarchical Fixture Chaining**: Fixtures can depend on other fixtures. In our project:
  ```mermaid
  graph TD
      DBSession[db_session fixture: creates in-memory DB tables] --> SampleUser[sample_user fixture: inserts User record]
      SampleUser --> SampleCase[sample_case fixture: inserts Case record]
      DBSession --> Client[client fixture: overrides FastAPI get_db]
      
      SampleCase --> Test[test_get_case_existing test function]
      Client --> Test
  ```

## 4. Understanding Fixture Scopes
The `scope` parameter controls how often pytest instantiates and tears down a fixture:

| Scope | Lifetime | Ideal Use Case |
|---|---|---|
| `scope="function"` *(default)* | Created once per test function; destroyed after test completes | Isolated database transactions, mutable test objects |
| `scope="class"` | Created once per test class | Shared read-only fixtures across methods in a class |
| `scope="module"` | Created once per test file (`test_*.py`) | Heavy read-only data, file parsing |
| `scope="session"` | Created once per test run across the whole suite | Docker container spinning, expensive network setups |

## 5. The Magic of `conftest.py`
In pytest, any fixture defined in a file named `conftest.py` is automatically visible to all tests in that directory and its subdirectories. **No import statement is needed!**
Our project's [tests/conftest.py](file:///d:/week1_kpmg/case-management-backend/tests/conftest.py) defines the test infrastructure:

```python
@pytest.fixture(scope="function")
def db_session():
    # Setup: Create fresh SQLite database tables
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session  # Hand execution to test function
    finally:
        # Teardown: Drop all tables so next test has a clean slate
        session.close()
        Base.metadata.drop_all(bind=test_engine)
```

## 6. Overriding FastAPI Dependencies for Testing
FastAPI's dependency injection system pairs seamlessly with pytest fixtures. In production, routes call `Depends(get_db)` to talk to the real database. In tests, our `client` fixture overrides this dependency:

```python
@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Swap out production get_db with our in-memory test database session:
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides so subsequent tests aren't polluted:
    app.dependency_overrides.clear()
```
**This is the ultimate expression of test isolation**: production code remains 100% untouched, yet runs against an isolated, lightning-fast test database during testing!

## 7. Common Mistakes
1. **Forgetting teardown after `yield`**: Failing to close sessions or drop tables leads to database lock errors (`database is locked` in SQLite).
2. **Using mutable session-scoped fixtures**: If a test modifies a record in a session-scoped database fixture, subsequent tests see the modified data and fail unpredictably.
3. **Circular fixture dependencies**: Fixture A requests Fixture B, and Fixture B requests Fixture A. pytest detects this and throws a collection error.

## 8. Practical Exercises
1. Open [tests/conftest.py](file:///d:/week1_kpmg/case-management-backend/tests/conftest.py). Trace how `sample_case` requests `sample_user`, and how `sample_user` requests `db_session`.
2. Add a new fixture `admin_user` in `conftest.py` that creates a user with `role="admin"`. Use it in a new test in `tests/api/test_user_and_error_handlers.py`.

## 9. Interview Questions & Model Answers
**Q: How does pytest's fixture mechanism implement the Dependency Injection (DI) design pattern?**
*Answer:* In standard programming, a function instantiates its own dependencies. Under Dependency Injection, the dependencies are supplied ("injected") from the outside. Pytest implements DI by inspecting the parameter names of test functions at collection time. If a parameter name matches a registered fixture name, pytest resolves the fixture dependency graph, instantiates the fixtures in topological order, and passes the resulting objects into the test function.

## 10. Short Self-Test
1. What code executes after the `yield` statement inside a pytest fixture? *(Answer: Teardown / cleanup code).*
2. Where should shared fixtures be placed so they are available to all test files without explicit imports? *(Answer: In `conftest.py`).*
