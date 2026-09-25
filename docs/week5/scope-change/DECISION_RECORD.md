# Decision Record: Scope Change SCR-2026-05

- **Decision**: Adopt non-breaking schema extension for `escalation_tier` and `department`.
- **Rationale**: Adding nullable/defaulted columns preserves full compatibility with existing database rows while fulfilling client compliance requirements.
- **Alternatives Considered**:
  1. *Separate Escalation Table*: Rejected due to unnecessary relational join overhead and complexity.
  2. *Free-form Tagging*: Rejected because unstructured tags do not allow deterministic RBAC enforcement or SLA validation.
- **Status**: Implemented and Verified in CI test suite.
