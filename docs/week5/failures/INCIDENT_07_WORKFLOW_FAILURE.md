# Incident Report: INC-07 - Workflow State Mismatch & Approval Failure

## 1. Symptom & Description
A consequential write request (`update_ticket`) is submitted with an expired, forged, or mismatched HMAC approval token.

## 2. Expected Behavior
- Cryptographic verification via `approval_manager.verify_approval(approval_id, expected_ticket_id)` fails.
- Workflow transitions state from `APPROVAL_REQUIRED` to `APPROVAL_REJECTED` or halts.
- Write operation is blocked; database record remains unaltered.
- Security audit event recorded.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_workflow_failure_invalid_approval_token`.

## 4. Root Cause Analysis
Static approval IDs or non-cryptographic tokens could allow replay attacks or approval token reuse across cases.

## 5. Remediation & Hardening
- Implemented HMAC-SHA256 tokens binding ticket ID, proposed status, timestamp, and approver user ID.
- TTL enforced on approval tokens (max 30 minutes).
- Verified single-use token invalidation upon execution.
