# Client Process Brief: Global Corporate Services Inc. (GCSI)

## 1. Engagement Overview
- **Client Organization**: Global Corporate Services Inc. (GCSI) — Enterprise Support Operations
- **Business Unit**: Customer Operations & Tier-2 Support Escalations
- **Simulated Engagement**: FDE Capstone Pilot — Enterprise Case Management & Controlled AI Workflow Platform
- **Date**: September 2026

## 2. Business Problem & Opportunity
GCSI handles over 45,000 corporate support cases monthly across multiple operating departments (Billing, Technical Services, Legal & Compliance). The current workflow is plagued by:
1. Fragmented data silos between relational case databases, unstructured SLA policies, and legacy ticketing endpoints.
2. Inconsistent policy compliance: agents struggle to quickly locate authoritative escalation rules, leading to missed SLA commitments.
3. Lack of safety controls in automated tools: past attempts at generative AI bots led to hallucinated ticket updates and uncontrolled database writes.
4. Absence of auditability: manual overrides occur without immutable cryptographic records or reviewer signoffs.

## 3. Users and Personas
1. **Support Agent (nalyst / iewer)**:
   - Queries case details, reads status updates, and asks policy questions.
   - Restricted to read-only operations and permitted department data.
2. **Support Lead (operator)**:
   - Updates ticket priority, reassigns owners, and submits escalation requests.
   - May request consequential actions but requires formal approval.
3. **Operations Manager / Supervisor (supervisor / dmin)**:
   - Reviews and signs off on high-impact actions (priority escalation, ticket status changes).
   - Generates and signs HMAC approval tokens.
4. **Platform Auditor / SRE (dmin)**:
   - Monitors system metrics, audit event logs, correlation ID traces, and data reconciliation reports.

## 4. Current Process & Interfaces
- Case records are stored in a relational store (cases, users, udit_logs).
- Document ingestion receives regulatory compliance policies in Markdown/PDF formats.
- Batch analytics pipelines process raw ingestion dumps into curated lakehouse tables.
- The AI assistant must interact via structured REST APIs, supporting natural-language questions, structured tool invocations, and strict human approvals.

## 5. Security & Operational Expectations
- Zero unauthenticated access: all workflows require valid JWT tokens.
- Deterministic guardrails: all user queries must be filtered for prompt injections and jailbreak attacks before processing.
- Human-in-the-Loop (HITL): consequential database mutations require an explicit, cryptographic approval signature.
- Strict Observability: every request must carry a X-Correlation-ID propagated through logs, traces, and metrics.
