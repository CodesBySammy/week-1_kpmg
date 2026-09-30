# Enterprise Incident & Failure Catalog (Week 5)

## Overview
This catalog indexes all 8 seeded, cross-layer failure scenarios implemented in `tests/failure-scenarios/test_failure_scenarios.py` and validated under Python 3.14.7. Each scenario verifies that the Enterprise Case Management Platform handles failures deterministically, emitting structured audit logs, maintaining state integrity, and preventing unhandled crashes.

## Incident Inventory

| Incident ID | Category | Subsystem | Symptom / Injection Vector | Expected Deterministic Response | Automated Test |
|---|---|---|---|---|---|
| **INC-01** | Data Failure | Ingestion Pipeline | Malformed schema, missing mandatory field `client_id`, negative amount | Quarantine isolation, error logged, pipeline survives | `test_data_failure_quarantine_malformed_case` |
| **INC-02** | API Failure | Gateway / HTTP | Corrupted JSON payload, missing auth header, timeout | HTTP 422 / 401 with standardized RFC 7807 error schema | `test_api_failure_malformed_json_returns_422` |
| **INC-03** | RAG Failure | Retrieval Engine | Empty retrieval, out-of-domain knowledge query | Controlled refusal string, `is_grounded=False`, no hallucination | `test_rag_failure_empty_retrieval_refuses_gracefully` |
| **INC-04** | Tool Failure | Agentic Tools | Upstream tool failure, invalid ticket ID in `update_ticket` | `ToolError` returned, workflow stays deterministic | `test_tool_failure_invalid_ticket_id` |
| **INC-05** | Auth Failure | Security / RBAC | User with role `auditor` or `investigator` executing `CRITICAL_ESC` | Access denied (403 / UNAUTHORIZED), audit record emitted | `test_auth_failure_unauthorized_escalation_tier` |
| **INC-06** | Model Failure | LLM Provider | Upstream LLM exception / timeout | Graceful fallback to canned policy refusal, error logged | `test_model_failure_llm_down_fallback` |
| **INC-07** | Workflow Failure | State Machine | Expired or mismatched cryptographic approval token | Rejection transition to `APPROVAL_REJECTED`, no execution | `test_workflow_failure_invalid_approval_token` |
| **INC-08** | Deployment Failure | Deployment / SRE | Missing mandatory env var (`DATABASE_URL`, `JWT_SECRET_KEY`) | Immediate startup assertion fail with actionable log | `test_deployment_failure_missing_env_var` |

Refer to individual incident runbooks (`INCIDENT_01_DATA_FAILURE.md` through `INCIDENT_08_DEPLOYMENT_FAILURE.md`) for detailed reproduction logs, root-cause analyses, and mitigation strategies.
