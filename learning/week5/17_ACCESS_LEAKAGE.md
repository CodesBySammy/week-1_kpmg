# Module 17: Access Leakage Prevention & Multi-Tenant Data Isolation

## 1. Simple Explanation
Access leakage occurs when a user or role gains unauthorized visibility into confidential data belonging to another department, tenant, or user.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Access Leakage Prevention & Multi-Tenant Data Isolation provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
User Request (JWT Claims: Dept=Retail) -> Repository SQL Query -> Filter: WHERE department == 'Retail' -> Prevent Cross-Tenant Leakage
```

## 5. Project-Specific Implementation
Implemented in `security/rbac.py::check_department_access()` and query filters in `app/repositories/case_repository.py`, preventing `Retail Banking` users from viewing `Wealth Management` cases.

## 6. Code & Module Mapping
- **Implementation File(s)**: `security/rbac.py, app/repositories/case_repository.py`
- **Test File(s)**: `tests/security/test_red_team_suite.py`
- **Documentation Reference**: `docs/week5/security/THREAT_MODEL.md`

## 7. Common Pitfalls & Mistakes
- Filtering data at the API/presentation layer rather than at the database query level.
- Allowing LLMs to search an unpartitioned vector database containing multiple tenants' confidential data.

## 8. Troubleshooting & Diagnostic Guide
Verify that attempting cross-department access returns HTTP 403 Forbidden.

## 9. Interview Questions & Detailed Answers
### Q1: Why must tenant/department isolation be enforced at the SQL/vector store query level?
**Answer**: If records are filtered after retrieval, sensitive data enters application memory and token contexts, risking exposure through logs, stack traces, or model hallucinations.

### Q2: How does the platform verify that an investigator cannot access an auditor-restricted case?
**Answer**: Via `UserPrincipal.role` checks inside deterministic FastAPI dependency functions (`require_roles(...)`).

## 10. Practical Hands-On Exercise
Run `pytest tests/security/test_red_team_suite.py -k access_leakage`.
