# Incident Report: INC-05 - RBAC Authorization & Escalation Failure

## 1. Symptom & Description
A user with an unauthorized role (e.g., `investigator` or `auditor`) attempts to modify the case `escalation_tier` to `CRITICAL_ESC` or update ticket status without required administrative permissions.

## 2. Expected Behavior
- Deterministic application-level RBAC interceptor validates `UserPrincipal.role`.
- Only `supervisor` or `admin` roles are permitted to assign `CRITICAL_ESC`.
- Rejects request with error code `UNAUTHORIZED_ESCALATION` or HTTP 403 Forbidden.
- Logs a security audit event `UNAUTHORIZED_ACCESS_ATTEMPT`.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_auth_failure_unauthorized_escalation_tier`.

## 4. Root Cause Analysis
Relying on model intent detection alone to gate permissions allows model manipulation to bypass business rules.

## 5. Remediation & Hardening
- Deterministic role validation enforced in `tools/update_ticket.py` and `security/rbac.py`.
- Model output is treated strictly as an untrusted proposal. Deterministic code enforces the final gate.
