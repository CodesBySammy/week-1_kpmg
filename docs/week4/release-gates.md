# Production Release Gates & Canary Verification

## 1. Overview
In a controlled AI workflow system handling enterprise case updates and sensitive retrieval, automated software release gates ensure that no model hallucinations, unauthorized mutation paths, or untested prompt regressions reach production.

Every release candidate must satisfy all five automated gates before progressive rollouts.

---

## 2. Release Gate Matrix

| Gate | Category | Threshold / Acceptance Criteria | Automated Verification Mechanism | Failure Impact |
|---|---|---|---|---|
| **Gate 1: Zero Regressions** | Functional | 100% of legacy Week 1, 2, 3 tests pass (100+ tests). | `pytest tests/test_*.py` in CI | Immediate block; build halted. |
| **Gate 2: Coverage Target** | Quality | Overall repository test coverage >= 70% (target >= 85%). | `pytest --cov --cov-fail-under=70` | Pipeline rejects PR. |
| **Gate 3: Security & RBAC Enforcement** | Security | 0 unauthenticated access to workflow endpoints; 0 privilege escalations (viewers forbidden from write mutations). | `pytest tests/test_security_rbac.py` | Strict deployment veto. |
| **Gate 4: Consequential Action Gating** | Safety | 100% of `update_ticket` tool calls require valid, signed human approval tokens before persistence. | `pytest tests/test_human_approval.py` | Hard stop; manual audit. |
| **Gate 5: Liveness & Readiness Probes** | Operational | `/health` returns 200 OK within 50ms; `/ready` verifies SQLite session, vector index, and workflow engine within 200ms. | Smoke test step in CD pipeline | Rollback initiated. |

---

## 3. Canary Deployment Strategy

```mermaid
graph TD
    A[Build Docker / Python Artifact] --> B[Run Automated Release Gates 1-5]
    B -->|Pass| C[Deploy to Sandbox / Staging]
    B -->|Fail| Z[Halt & Notify On-Call]
    C --> D[Run Synthetic Health & Readiness Check]
    D --> E[Route 5% Traffic to Canary Node]
    E --> F{Evaluate Metrics (5 min)}
    F -->|Error Rate < 0.1% & P95 < 500ms| G[Route 25% Traffic]
    F -->|Anomalies Detected| R[Trigger Automated Rollback]
    G --> H{Evaluate Metrics (10 min)}
    H -->|Healthy| I[Route 100% Production Traffic]
    H -->|Degraded| R
```

### Canary Evaluation Metrics
1. **HTTP Status Code Ratio:** $5xx$ responses must remain $< 0.1\%$.
2. **Workflow Error Counter:** `observability.metrics.error_count` must not exceed baseline by $> 2\%$.
3. **P95 Latency:** Endpoint `/api/v1/workflow/execute` P95 latency must be $< 1.2\text{s}$.
4. **Approval Rejection Rate:** Rejections due to malformed payload or timeout must be $< 1\%$.
