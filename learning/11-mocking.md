# Module 11: Mocking, Test Doubles & Isolation Boundaries

## 1. What It Is
**Mocking** is the practice of replacing real software components, services, or dependencies with simulated objects (**test doubles**) that mimic the behavior of the real objects in a controlled, deterministic way. In Python, this is provided by the built-in `unittest.mock` module (`MagicMock`, `patch`).

## 2. Why It Exists
Real systems have dependencies that are unsuitable for fast, deterministic unit testing:
- **Network calls & Third-party APIs**: Third-party APIs (Stripe, Twilio, external CRM) have rate limits, cost money per call, and can experience downtime.
- **Side Effects**: You do not want a test to send real SMS messages, bill customer credit cards, or format a production disk.
- **Hard-to-Reproduce Failures**: How do you test how your application behaves when a database disk runs out of space, or a network socket abruptly times out? You cannot easily trigger a physical disk crash during every test run — but you can mock one in a single line of code!

## 3. Taxonomy of Test Doubles
The testing literature defines five distinct types of test doubles:

| Double Type | Definition | Example in Our Project |
|---|---|---|
| **Dummy** | Objects passed around but never actually used | Passing an empty dict or string just to satisfy a required parameter |
| **Fake** | Working implementation, but with a shortcut unsuitable for production | Using an in-memory SQLite database instead of a multi-node PostgreSQL cluster |
| **Stub** | Provides canned answers to calls made during the test | `service.user_repo.get_by_id = MagicMock(return_value=mock_user)` |
| **Spy** | Records information about how it was called (arguments, call count) | `service.case_repo.create.assert_called_once()` |
| **Mock** | Pre-programmed with expectations which form a specification of the calls they receive | A `MagicMock` with `side_effect=UserNotFoundError` |

## 4. Why We Do NOT Mock Everything (The Mocking Trap)
A critical rule of professional backend engineering: **DO NOT MOCK EVERYTHING.**
- If you mock the database, mock the repository, mock the models, and mock the schemas, you are no longer testing your code — you are testing your mocks!
- When you refactor internal functions, over-mocked test suites break even though the application's actual behavior is completely fine.
- **Guideline**:
  - In **Unit Tests** (`tests/unit/test_case_service.py`), we mock the *Repository* to verify pure business logic without database overhead.
  - In **Repository Tests** (`tests/unit/test_case_repository.py`), we **DO NOT MOCK** — we test against a real SQLite database session.
  - In **API Tests** (`tests/api/test_cases_api.py`), we **DO NOT MOCK** — we test the entire HTTP-to-Database flow end-to-end.

## 5. Mocking in Action: Project Examples

### Example 1: Isolating Business Logic in Service Layer
In [tests/unit/test_case_service.py](file:///d:/week1_kpmg/case-management-backend/tests/unit/test_case_service.py):
```python
def test_create_case_fails_when_creator_not_found(self):
    service = CaseService()
    mock_db = MagicMock()
    
    # STUB: Tell the mock repository to pretend the user does not exist
    service.user_repo.get_by_id = MagicMock(side_effect=UserNotFoundError(user_id=999))

    case_input = CaseCreate(title="Some Bug", created_by=999)

    # Verify that the Service catches this and propagates the domain error
    with pytest.raises(UserNotFoundError) as exc_info:
        service.create_case(mock_db, case_input)

    assert exc_info.value.user_id == 999
    # SPY: Verify that the service actually called get_by_id with the right arguments
    service.user_repo.get_by_id.assert_called_once_with(mock_db, 999)
```

### Example 2: Simulating Unhandled Database Catastrophe
In [tests/api/test_user_and_error_handlers.py](file:///d:/week1_kpmg/case-management-backend/tests/api/test_user_and_error_handlers.py):
```python
def test_database_error_handler(client, sample_user):
    # PATCH: Temporarily hijack CaseRepository.create during this test block
    with patch("app.services.case_service.CaseRepository.create") as mock_create:
        mock_create.side_effect = DatabaseError("Fatal disk write failure")

        response = client.post("/api/v1/cases", json={"title": "Trigger Error", "created_by": sample_user.id})
        
        # Verify HTTP status is 500
        assert response.status_code == 500
        data = response.json()
        # Verify error details are masked from client
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "Fatal disk write failure" not in data["error"]["message"]
```

## 6. Common Mistakes
1. **Mocking the wrong import path**:
   - When using `patch("module.Class")`, you must patch where the object is **looked up / used**, not where it is defined!
   - Example: To patch `CaseRepository` in `CaseService`, patch `"app.services.case_service.CaseRepository"`, not `"app.repositories.case_repository.CaseRepository"`.
2. **Forgetting to unpatch**:
   - Always use `with patch(...)` as a context manager or `@patch` as a decorator. Never call `mock.patch()` manually without `start()` and `stop()`.

## 7. Practical Exercises
1. Open [tests/unit/test_case_service.py](file:///d:/week1_kpmg/case-management-backend/tests/unit/test_case_service.py) and identify every instance of `MagicMock`. Write a 1-sentence explanation of why each mock exists.
2. Modify `test_create_case_success` to verify that `service.case_repo.create` was called with a `Case` object having `status == CaseStatus.OPEN`.

## 8. Interview Questions & Model Answers
**Q: What is the risk of excessive mocking in an automated test suite?**
*Answer:* Excessive mocking tightly couples test code to internal implementation details rather than external behavior. If a developer refactors an internal helper method or renames a private variable, the test suite will fail even though the software works perfectly (false positives). Furthermore, if mocks return unrealistic data structures, tests can pass with 100% green checkmarks while the production code crashes in real deployments because the mock did not match real-world API responses.

## 9. Short Self-Test
1. What is the difference between `return_value` and `side_effect` on a `MagicMock`? *(Answer: `return_value` returns a fixed value when the mock is called; `side_effect` raises an exception or dynamically computes a return value based on inputs).*
2. Where should you target `patch()`: where the symbol is imported, or where it is defined? *(Answer: Where it is imported/used).*
