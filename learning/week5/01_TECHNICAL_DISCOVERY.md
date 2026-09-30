# Module 01: Technical Discovery in Client Engagements

## 1. Simple Explanation
Technical discovery is the structured process of interviewing client stakeholders, analyzing existing legacy systems, cataloging data sources, uncovering hidden constraints, and establishing the technical reality before writing production code.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Technical Discovery in Client Engagements provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Discovery Phase: Business Pain Points -> Legacy Data & API Audits -> Security/Auth Boundaries -> Baseline Architecture Definition
```

## 5. Project-Specific Implementation
Documented in `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md` for the simulated Global Bank case management engagement, analyzing legacy CSV data dumps and strict regulatory audit requirements.

## 6. Code & Module Mapping
- **Implementation File(s)**: `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md`
- **Test File(s)**: `tests/api/test_cases_api.py`
- **Documentation Reference**: `docs/week5/client-engagement/CLIENT_PROCESS_BRIEF.md`

## 7. Common Pitfalls & Mistakes
- Assuming the client's documented process matches what their legacy systems actually do.
- Skipping non-functional requirements such as compliance audit retention or p95 latency targets.

## 8. Troubleshooting & Diagnostic Guide
Compare client data schemas against real database records using schema profiling scripts (`pipeline/profiler.py`).

## 9. Interview Questions & Detailed Answers
### Q1: Why must technical discovery precede architecture design in an FDE engagement?
**Answer**: Discovery identifies real enterprise constraints (e.g. data silos, air-gapped environments, regulatory compliance requirements) that dictate architecture choices, avoiding expensive late-stage redesigns.

### Q2: What is the difference between a functional requirement and an architectural constraint?
**Answer**: A functional requirement defines what the system should do (e.g., query case details), while a constraint defines limitations within which the system must operate (e.g., must run on-premise without public cloud egress).

## 10. Practical Hands-On Exercise
Review `docs/week5/client-engagement/CONSTRAINTS.md` and identify 3 architectural trade-offs.
