# Enterprise Regression Testing Strategy

## Purpose & Scope
Ensures that all capabilities built during Weeks 1, 2, 3, and 4 continue to function without degradation following Week 5 integration, scope expansion, and failure hardening.

## Regression Guard Hierarchy
1. **Week 1 Core Backend (`tests/api/`, `tests/unit/`)**: REST CRUD operations, repository persistence, relational schemas, database rollback.
2. **Week 2 Data Engineering (`tests/pipeline/`)**: Bronze/Silver/Gold ingestion, schema validation, quarantine routing, financial reconciliation.
3. **Week 3 Grounded RAG (`tests/test_rag_*.py`)**: Token-budgeted chunking, hybrid retrieval (dense + sparse), reranking, grounded generation with citations, policy refusal.
4. **Week 4 Controlled Workflow (`tests/test_workflow_*.py`, `tests/test_human_approval.py`)**: Intent detection, tool execution contracts, approval manager, OpenTelemetry tracing.
5. **Week 5 Integration Suite (`tests/regression/test_regression_suite.py`)**: 17 dedicated end-to-end regression tests validating cross-module compatibility.

## Execution Matrix
- **Command**: `pytest tests/regression/test_regression_suite.py -v`
- **Result**: 17 passed, 0 failed.
- **Overall Suite**: 221 passed, 0 failed.
