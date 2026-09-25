# Scope Change Impact Assessment: SCR-2026-05

## 1. What Changed?
Introduction of `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`) and `department` fields across data models, REST endpoints, agentic tool schemas, and access controls.

## 2. Why Did It Change?
Client GCSI mandated formal SLA escalation governance to prevent SLA breaches on enterprise accounts and isolate sensitive billing/legal cases from generic tier-1 support visibility.

## 3. What Is Affected?
- **Data Layer (`app/models/case.py`)**: Added `EscalationTier` enum and `escalation_tier`, `department` columns with default values.
- **API Schemas (`app/schemas/case.py`)**: Added `escalation_tier` and `department` fields to request and response DTOs.
- **Case Service (`app/services/case_service.py`)**: Propagates `escalation_tier` and `department` during creation and updates.
- **Tool Layer (`tools/schemas.py`, `tools/update_ticket.py`)**: Supports escalation parameters in tool input/output contracts.
- **Security (`security/rbac.py`)**: Added `verify_department_access` utility to prevent unauthorized cross-department data leaks.
- **Testing (`tests/e2e/test_scope_change_escalation.py`)**: Added test suite validating escalation workflows, RBAC rejections, and approval tokens.

## 4. What Is NOT Affected?
- **Medallion Data Pipeline**: Raw, Standardized, and Curated lakehouse layers remain intact.
- **RAG Subsystem**: Document chunking, hybrid indexing, and cross-score reranking function identically.
- **Authentication**: JWT token format and claims structure remain unchanged.
- **Week 1–4 Baseline Tests**: All 143 baseline tests remain 100% passing.

## 5. What Trade-offs Exist?
- **Enum vs String**: Used Python enum with SQLAlchemy `Enum` for strict type safety.
- **Default Fallback**: Used `STANDARD` and `SUPPORT` as sensible defaults to guarantee 100% backward compatibility without requiring destructive data migrations.

## 6. Final Decision & Signoff
Approved by Architecture & Engineering Lead for immediate integration into Release Candidate v1.0.0-rc1.
