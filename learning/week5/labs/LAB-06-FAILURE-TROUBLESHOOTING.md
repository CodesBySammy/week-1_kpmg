# LAB-06: Seeded Failure Injection & Incident Troubleshooting

## 1. Objective
Inject cross-layer system failures and follow incident runbooks to troubleshoot root causes using correlation IDs.

## 2. Prerequisites
Familiarity with structured logging, correlation IDs, and exception handling.

## 3. Practical Task
Trigger an invalid approval token failure, extract trace ID, and diagnose root cause.

## 4. Step-by-Step Instructions
1. Run `pytest tests/failure-scenarios/test_failure_scenarios.py -k test_workflow_failure_invalid_approval_token -v -s`.
2. Capture correlation ID and structured error log.
3. Trace failure in `docs/week5/failures/INCIDENT_07_WORKFLOW_FAILURE.md`.
4. Verify state machine transitioned to `APPROVAL_REJECTED`.

## 5. Expected Result
Successful diagnosis and verification of deterministic state recovery.

## 6. Verification & Automated Validation
Run `pytest tests/failure-scenarios/test_failure_scenarios.py` (15/15 passed).

## 7. Challenge Questions
How does a correlation ID link an API gateway request to an internal database rollback?
