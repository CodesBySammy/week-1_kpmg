# LAB-04: Negative-Path & Boundary Condition Testing

## 1. Objective
Implement and execute negative-path tests targeting malformed payloads, invalid IDs, and boundary violations.

## 2. Prerequisites
Pytest, FastAPI TestClient, and HTTP status code standards.

## 3. Practical Task
Author test cases asserting HTTP 422, 401, and 403 on corrupted requests.

## 4. Step-by-Step Instructions
1. Open `tests/negative/test_negative_paths.py`.
2. Execute the test suite using `pytest tests/negative/ -v`.
3. Observe assertions on RFC 7807 problem details.
4. Add a test asserting negative transaction amounts return validation errors.

## 5. Expected Result
All 18 negative test cases passing with zero unhandled exceptions.

## 6. Verification & Automated Validation
Run `pytest tests/negative/test_negative_paths.py`.

## 7. Challenge Questions
Why should a server never return a raw stack trace to an external client?
