# Module 04: System Architecture & Cross-Layer Integration

## 1. Simple Explanation
System architecture defines how decoupled subsystems (web gateway, lakehouse data pipeline, grounded RAG, agentic workflows, persistence, and observability) interact coherently under unified contracts.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: System Architecture & Cross-Layer Integration provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Gateway <-> Security & RBAC <-> Workflow Orchestrator <-> [RAG Engine | Tool Registry] <-> Database & Storage
```

## 5. Project-Specific Implementation
Our platform integrates FastAPI routers (`app/api`), SQLAlchemy ORM (`app/models`), Parquet medallion pipelines (`pipeline/`), hybrid search (`rag/`), and LangGraph state machines (`workflow/`).

## 6. Code & Module Mapping
- **Implementation File(s)**: `app/main.py, workflow/orchestrator.py`
- **Test File(s)**: `tests/test_workflow_orchestration.py`
- **Documentation Reference**: `docs/week5/architecture/CURRENT_STATE_ARCHITECTURE.md`

## 7. Common Pitfalls & Mistakes
- Tight coupling between the presentation layer and persistence models.
- Allowing AI components to directly execute database mutations without an intermediate service layer.

## 8. Troubleshooting & Diagnostic Guide
Verify layer decoupling by asserting that tools only communicate through domain repository contracts, never raw SQL queries.

## 9. Interview Questions & Detailed Answers
### Q1: What are the key architectural layers of the Week 1–5 platform?
**Answer**: 1. Presentation/API Gateway Layer, 2. Security & Guardrail Interceptor, 3. Workflow & RAG Orchestration Layer, 4. Domain & Tool Integration Layer, 5. Lakehouse & Relational Persistence Layer.

### Q2: How does the architecture prevent AI hallucinations from affecting persistent data?
**Answer**: By strictly isolating the LLM: the model can only generate structured tool proposals, which are validated against Pydantic contracts and evaluated by deterministic RBAC and approval guards before execution.

## 10. Practical Hands-On Exercise
Review `docs/week5/architecture/CURRENT_STATE_ARCHITECTURE.md`.
