# Comprehensive Testing Strategy

## 1. Test Organization
- `tests/test_tools_contracts.py`: Input/output schema validation, ToolError models, safe read and write tools.
- `tests/test_workflow_orchestration.py`: Intent routing, FSM transitions, and orchestrator execution.
- `tests/test_human_approval.py`: Approval token generation, reviewer approval, rejection, and expiration.
- `tests/test_security_guardrails.py`: Input length bounds, character cleaning, and prompt injection attacks.
- `tests/test_security_rbac.py`: JWT issuance, tampering prevention, and role permission enforcement.
- `tests/test_observability.py`: Correlation ID propagation, event logging, tracer spans, and metrics.
- `tests/test_workflow_api.py`: FastAPI end-to-end integration tests for `/execute`, `/auth/token`, `/ready`, etc.
