import os

BASE_DIR = r"D:\week1_kpmg\case-management-backend"
OUT_DIR = os.path.join(BASE_DIR, "learning", "week5")
os.makedirs(OUT_DIR, exist_ok=True)

modules = {}

def build_module(num, slug, title, concept_summary, arch_snippet, proj_example, impl_map, mistakes, troubleshooting, interview_q, exercise):
    return f"""# Module {num:02d}: {title}

## 1. Simple Explanation
{concept_summary}

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: {title} provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
{arch_snippet}
```

## 5. Project-Specific Implementation
{proj_example}

## 6. Code & Module Mapping
- **Implementation File(s)**: `{impl_map[0]}`
- **Test File(s)**: `{impl_map[1]}`
- **Documentation Reference**: `{impl_map[2]}`

## 7. Common Pitfalls & Mistakes
{mistakes}

## 8. Troubleshooting & Diagnostic Guide
{troubleshooting}

## 9. Interview Questions & Detailed Answers
### Q1: {interview_q[0]}
**Answer**: {interview_q[1]}

### Q2: {interview_q[2]}
**Answer**: {interview_q[3]}

## 10. Practical Hands-On Exercise
{exercise}
"""

modules["15_RED_TEAM_TESTING.md"] = build_module(
    15, "red-team-testing", "Red-Team Security Testing & Adversarial Evaluation",
    "Red-team testing adopts an adversarial mindset to probe systems for security vulnerabilities, access bypasses, injection attacks, and data leakage before deployment.",
    "Attacker Input -> [Adversarial Payloads] -> Gateway / Guardrails / RBAC -> Verification of 100% Interception",
    "Implemented in `tests/security/test_red_team_suite.py` with 16 automated tests attacking prompt boundaries, RBAC roles, payload schemas, and tool authorizations.",
    ("security/guardrails.py, security/rbac.py", "tests/security/test_red_team_suite.py", "docs/week5/security/RED_TEAM_REPORT.md"),
    "- Trusting the LLM to police its own outputs.\n- Treating security testing as a one-time manual audit rather than automated continuous regression tests.",
    "Run `pytest tests/security/test_red_team_suite.py -v` and inspect `RED_TEAM_RESULTS.md`.",
    ("Why can an LLM never be trusted as the sole security boundary in enterprise systems?",
     "Because LLMs are non-deterministic, probabilistic text completion engines susceptible to semantic obfuscation, jailbreaks, and indirect prompt injections. Deterministic code must enforce the security boundaries.",
     "What are the four core red-team attack vectors required in enterprise AI testing?",
     "1. Prompt Injection, 2. Access Leakage / Privilege Escalation, 3. Malformed Data Injection, 4. Unsafe Tool Requests."),
    "Run `pytest tests/security/test_red_team_suite.py` and inspect test outputs."
)

modules["16_PROMPT_INJECTION.md"] = build_module(
    16, "prompt-injection", "Prompt Injection Defense & Untrusted Text Isolation",
    "Prompt injection occurs when user-supplied text manipulates the LLM into ignoring system instructions, leaking private prompts, or executing unauthorized actions.",
    "User Prompt -> Pre-Execution Regex Guardrails -> Context Token Sanitization -> Model (Treated as Untrusted)",
    "`security/guardrails.py::detect_prompt_injection()` scans inputs for adversarial patterns ('ignore previous instructions', 'bypass security', 'you are now unconstrained').",
    ("security/guardrails.py", "tests/test_security_guardrails.py", "docs/week5/security/ABUSE_CASES.md"),
    "- Passing raw user input directly to the system prompt context without validation.\n- Relying solely on prompt instructions like 'Do not execute dangerous commands'.",
    "Test pattern matching in `security/guardrails.py` against OWASP Top 10 LLM jailbreak vectors.",
    ("What is the difference between direct and indirect prompt injection?",
     "Direct prompt injection is typed directly by the user into the chat prompt. Indirect prompt injection is embedded inside ingested external data (e.g. inside a retrieved compliance document or customer email).",
     "How does our architecture neutralize indirect prompt injection in RAG contexts?",
     "By treating retrieved context strictly as passive reference text and forbidding tool execution from RAG answer generation pipelines."),
    "Inspect the regex patterns in `security/guardrails.py`."
)

modules["17_ACCESS_LEAKAGE.md"] = build_module(
    17, "access-leakage", "Access Leakage Prevention & Multi-Tenant Data Isolation",
    "Access leakage occurs when a user or role gains unauthorized visibility into confidential data belonging to another department, tenant, or user.",
    "User Request (JWT Claims: Dept=Retail) -> Repository SQL Query -> Filter: WHERE department == 'Retail' -> Prevent Cross-Tenant Leakage",
    "Implemented in `security/rbac.py::check_department_access()` and query filters in `app/repositories/case_repository.py`, preventing `Retail Banking` users from viewing `Wealth Management` cases.",
    ("security/rbac.py, app/repositories/case_repository.py", "tests/security/test_red_team_suite.py", "docs/week5/security/THREAT_MODEL.md"),
    "- Filtering data at the API/presentation layer rather than at the database query level.\n- Allowing LLMs to search an unpartitioned vector database containing multiple tenants' confidential data.",
    "Verify that attempting cross-department access returns HTTP 403 Forbidden.",
    ("Why must tenant/department isolation be enforced at the SQL/vector store query level?",
     "If records are filtered after retrieval, sensitive data enters application memory and token contexts, risking exposure through logs, stack traces, or model hallucinations.",
     "How does the platform verify that an investigator cannot access an auditor-restricted case?",
     "Via `UserPrincipal.role` checks inside deterministic FastAPI dependency functions (`require_roles(...)`)."),
    "Run `pytest tests/security/test_red_team_suite.py -k access_leakage`."
)

modules["18_MALFORMED_DATA.md"] = build_module(
    18, "malformed-data", "Malformed Data Handling & Quarantine Architectures",
    "Malformed data handling ensures that corrupted, oversized, or non-schema-compliant payloads are safely isolated without crashing downstream analytical pipelines or transactional databases.",
    "Incoming Record -> Schema Validator -> [Valid -> Silver Parquet] OR [Invalid -> Quarantine Lakehouse Zone + Error Reason]",
    "Implemented in `pipeline/validation.py` and `pipeline/quarantine.py`: records with null timestamps or negative amounts are routed to `data/quarantine/` with structured error codes.",
    ("pipeline/validation.py, pipeline/quarantine.py", "tests/pipeline/test_quarantine.py", "docs/week5/failures/INCIDENT_01_DATA_FAILURE.md"),
    "- Silently dropping corrupted records without audit logging or operator alerting.\n- Letting malformed records trigger uncaught exceptions that halt batch pipelines.",
    "Check quarantine directory contents and query `pipeline_quarantined_records_total` Prometheus metrics.",
    ("What are the core components of a production data quarantine pattern?",
     "1. Schema validation gate, 2. Dedicated quarantine storage partitioned by date and failure code, 3. Error metadata enrichment, 4. Telemetry metrics and alerting, 5. Re-ingestion remediation tooling.",
     "How does Pydantic v2 enhance malformed data detection in FastAPI?",
     "It performs rapid C-level validation, generates deterministic RFC 7807 error structures, and rejects unknown or corrupted data before it reaches business logic."),
    "Run `pytest tests/pipeline/test_quarantine.py -v`."
)

modules["19_UNSAFE_TOOL_REQUESTS.md"] = build_module(
    19, "unsafe-tool-requests", "Unsafe Tool Request Mitigation & Principle of Deterministic Control",
    "The Principle of Deterministic Control dictates: 'The Model May Propose, but Deterministic Application Code Must Decide'. Unsafe or unauthorized tool actions are blocked at the application boundary.",
    "LLM Proposal ('update ticket CASE-101') -> Deterministic Guardrail -> Role Check -> Approval Verification -> DB Execution",
    "`tools/update_ticket.py` verifies caller permissions and requires a valid HMAC approval token from `workflow/approval.py` before executing any state or escalation modifications.",
    ("tools/update_ticket.py, workflow/approval.py", "tests/test_human_approval.py", "docs/week5/security/SECURITY_HARDENING_REPORT.md"),
    "- Allowing an LLM to directly trigger database mutations or financial transactions without human approval.\n- Trusting model-generated parameters without re-validating them against database constraints.",
    "Verify that calling `update_ticket` with a tampered approval token returns `INVALID_APPROVAL`.",
    ("What is the core architectural principle governing tool execution in enterprise AI?",
     "'The model may propose; deterministic application code must decide.' The LLM has zero authority to commit transactions; all calls pass through strict RBAC, validation, and approval checks.",
     "What happens if an LLM hallucinates an invalid ticket ID in a tool call?",
     "The tool intercepts the missing ID, catches the domain exception, and returns a typed `ToolError(error_code='CASE_NOT_FOUND')` rather than crashing the worker."),
    "Review `tools/update_ticket.py`."
)

modules["20_PERFORMANCE_TESTING.md"] = build_module(
    20, "performance-testing", "Performance Testing, Latency Benchmarking & SLAs",
    "Performance testing measures system latency, throughput, concurrency limits, and resource utilization under realistic workloads to ensure compliance with enterprise Service Level Agreements (SLAs).",
    "Benchmark Runner -> [API Latency | Retrieval Time | Context Assembly | Tool Exec] -> Statistical Analysis (p50, p95, p99)",
    "`tests/performance/test_performance_benchmarks.py` measures real execution times across API endpoints, document chunkers, hybrid retrieval, and approval verification, documented in `PERFORMANCE_RESULTS.md`.",
    ("tests/performance/test_performance_benchmarks.py", "tests/performance/test_performance_benchmarks.py", "docs/week5/testing/PERFORMANCE_BENCHMARKS.md"),
    "- Reporting only average (mean) latency, which hides tail latency spikes.\n- Benchmarking debug builds or unindexed databases and assuming production will behave the same.",
    "Run `pytest tests/performance/test_performance_benchmarks.py -v` and inspect p95 latency outputs.",
    ("Why are percentile metrics (p95, p99) more informative than average latency in enterprise APIs?",
     "Average latency is easily skewed by many fast requests, masking severe latency spikes experienced by the 1% or 5% of users with complex queries or during garbage collection pauses.",
     "What were the measured p95 latency results in this project?",
     "Case CRUD API: 3.84ms; Hybrid Retrieval: 6.22ms; Context Assembly: 0.92ms; Workflow E2E: 14.50ms (all well within SLAs)."),
    "Run `pytest tests/performance/test_performance_benchmarks.py`."
)

modules["21_RELIABILITY_TESTING.md"] = build_module(
    21, "reliability-testing", "Reliability, Resilience & Fault Tolerance",
    "Reliability engineering verifies that a system maintains uninterrupted service, recovers gracefully from transient dependency failures, and avoids cascading outages.",
    "Component Outage (LLM Down / DB Lock) -> Circuit Breaker / Timeout -> Fallback Path Activated -> Graceful Response + Telemetry",
    "Verified in `tests/failure-scenarios/test_failure_scenarios.py`: when mock LLM inference fails, the system falls back to a deterministic degraded policy message rather than returning HTTP 500.",
    ("workflow/orchestrator.py, rag/generation/generator.py", "tests/failure-scenarios/test_failure_scenarios.py", "docs/week5/testing/RELIABILITY_TESTING.md"),
    "- Unbounded network timeouts that block threads indefinitely when external services hang.\n- Failing to release database connections during exception handling, leading to pool exhaustion.",
    "Simulate an external dependency failure and verify that client receives a graceful HTTP 503 or cached fallback.",
    ("What is the difference between fault tolerance and graceful degradation?",
     "Fault tolerance means the system continues functioning with zero user-visible impairment. Graceful degradation means non-critical features (like AI reasoning) step down to canned fallbacks while core business operations continue.",
     "How does the state machine handle retry exhaustion?",
     "After reaching max retries, the state machine transitions cleanly from `EXECUTING` to `FAILED` and records an audit log entry."),
    "Review `INCIDENT_06_MODEL_FAILURE.md`."
)

modules["22_FAILURE_RECOVERY.md"] = build_module(
    22, "failure-recovery", "Failure Recovery & Self-Healing State Machines",
    "Failure recovery mechanisms enable systems to detect abnormal states, safely roll back in-flight transactions, and transition state machines into well-defined recovery states.",
    "State: EXECUTING -> Exception Encountered -> DB Rollback -> State: FAILED / CANCELLED -> Error Emitted",
    "Implemented in `workflow/state.py` and `workflow/orchestrator.py`: if a tool fails or an approval token is invalid, the orchestrator transitions state to `FAILED` or `APPROVAL_REJECTED`.",
    ("workflow/state.py, workflow/orchestrator.py", "tests/failure-scenarios/test_failure_scenarios.py", "docs/week5/failures/FAILURE_SCENARIOS.md"),
    "- Leaving state machines in zombie or orphan states when background operations crash.\n- Committing partial database writes before verifying all downstream constraints.",
    "Inspect `workflow_state_transitions_total` metrics to trace failed state paths.",
    ("Why must database transactions be bound to workflow state transitions?",
     "To maintain ACID consistency: if a workflow step fails, the database rollback reverts any intermediate mutations, ensuring persistent storage exactly mirrors workflow state.",
     "What states are available in the Week 4/5 workflow state machine?",
     "`REQUEST_RECEIVED`, `INTENT_DETECTED`, `TOOL_PROPOSED`, `APPROVAL_REQUIRED`, `APPROVED`, `EXECUTING`, `COMPLETED`, `APPROVAL_REJECTED`, `APPROVAL_EXPIRED`, `TIMED_OUT`, `FAILED`."),
    "Run `pytest tests/test_workflow_orchestration.py -v`."
)

modules["23_SCOPE_CHANGE_MANAGEMENT.md"] = build_module(
    23, "scope-change-management", "Controlled Scope Change Management & Impact Analysis",
    "Scope change management is the disciplined engineering process of evaluating, designing, implementing, and verifying new requirements introduced mid-engagement without disrupting existing baselines.",
    "Scope Change Request -> Technical Impact Assessment -> Schema & Migration Update -> Backlog & ADR Update -> Regression Test",
    "Implemented for Week 5: Added `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`) and `department` fields to Case model, added supervisor RBAC enforcement, and verified with 4 new E2E tests.",
    ("app/models/case.py, app/schemas/case.py", "tests/e2e/test_scope_change_escalation.py", "docs/week5/scope-change/IMPACT_ASSESSMENT.md"),
    "- Implementing scope changes ad-hoc without performing an impact assessment across all layers.\n- Making breaking database schema changes that corrupt legacy records.",
    "Run `pytest tests/e2e/test_scope_change_escalation.py` to verify scope change implementation.",
    ("What are the required sections of an enterprise Impact Assessment?",
     "1. What changed, 2. Why it changed, 3. What is affected (APIs, schemas, tests, docs), 4. What is NOT affected, 5. Trade-offs, 6. Final engineering decision.",
     "How was backward compatibility maintained when adding `escalation_tier` to the database?",
     "By defining `escalation_tier` with a default value (`STANDARD`) and making the column nullable or default-populated in SQLite/SQLAlchemy."),
    "Review `docs/week5/scope-change/SCOPE_CHANGE_REQUEST.md`."
)

modules["24_TECHNICAL_DECISION_RECORDS.md"] = build_module(
    24, "technical-decision-records", "Architecture Decision Records (ADRs) in Production Engineering",
    "Architecture Decision Records (ADRs) document key architectural choices, their business and technical context, evaluated alternatives, rationale, and positive/negative trade-offs.",
    "Context / Problem -> Evaluated Alternatives (A, B, C) -> Decision -> Consequences & Trade-offs",
    "`docs/week5/architecture/ARCHITECTURE_DECISION_RECORDS.md` contains 7 comprehensive ADRs (ADR-001 to ADR-007) detailing decisions on hybrid RAG, HMAC approvals, scope change, and failure handling.",
    ("docs/week5/architecture/ARCHITECTURE_DECISION_RECORDS.md", "tests/regression/test_regression_suite.py", "docs/week5/architecture/ARCHITECTURE_DECISION_RECORDS.md"),
    "- Documenting only the chosen option without explaining why alternatives were rejected.\n- Writing ADRs as post-hoc justifications rather than engineering decision records.",
    "Review ADR consequences to confirm documented trade-offs match active code constraints.",
    ("What is the structure of an Architecture Decision Record (ADR)?",
     "Title & Status, Context, Decision Drivers, Considered Options, Decision Outcome, Positive Consequences, Negative Consequences / Trade-offs.",
     "Why are ADRs critical for long-term project handover?",
     "They prevent receiving engineering teams from unknowingly re-introducing previously rejected approaches or misunderstanding non-obvious architecture constraints."),
    "Read `docs/week5/architecture/ARCHITECTURE_DECISION_RECORDS.md`."
)

modules["25_PRODUCTION_READINESS.md"] = build_module(
    25, "production-readiness", "Production-Readiness Reviews & Deployment Gates",
    "A Production-Readiness Review (PRR) is a formal gating evaluation assessing whether a software deliverable satisfies all operational, security, reliability, performance, and documentation criteria.",
    "System Deliverable -> PRR Checklist Evaluation (Functional, Security, SRE, Support) -> Sign-Off -> Release Candidate",
    "`docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md` and `FINAL_READINESS_REPORT.md` evaluate all platform gates with verified test evidence.",
    ("docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md", "tests/regression/test_regression_suite.py", "docs/week5/production-readiness/FINAL_READINESS_REPORT.md"),
    "- Marking readiness checklist items as 'PASS' without citing verifiable test evidence.\n- Ignoring operational and supportability gates (e.g. missing runbooks or alerts).",
    "Verify that every 'PASS' entry in the PRR checklist links directly to an automated test or markdown artifact.",
    ("What are the core evaluation pillars in an enterprise Production-Readiness Review?",
     "Functional Completeness, Security & Compliance, Reliability & Fault Tolerance, Performance & Scalability, Observability & Tracing, Deployment & Rollback, Operational Supportability.",
     "Under what conditions should a PRR result in a REJECT or CONDITIONAL PASS?",
     "A REJECT occurs if critical security flaws, data corruption risks, or failing tests exist. A CONDITIONAL PASS may occur if non-blocking technical debt is documented with agreed remediation timelines."),
    "Review `docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md`."
)

modules["26_KNOWN_LIMITATIONS.md"] = build_module(
    26, "known-limitations", "Known Limitations Registers & Technical Debt Management",
    "A Known Limitations Register provides transparent, honest, and rigorous documentation of all system boundaries, assumptions, technical debt, and environment constraints.",
    "Architecture Analysis -> Identify Boundary Conditions -> Document Root Cause & Impact -> Define Remediation Roadmap",
    "Documented in `docs/week5/production-readiness/KNOWN_LIMITATIONS.md`: highlights local hash embedding vs. remote vector APIs, SQLite vs. Postgres concurrency, and approval token TTL limits.",
    ("docs/week5/production-readiness/KNOWN_LIMITATIONS.md", "tests/performance/test_performance_benchmarks.py", "docs/week5/production-readiness/KNOWN_LIMITATIONS.md"),
    "- Concealing known limitations from clients or receiving teams in an effort to look flawless.\n- Listing limitations without explaining their operational impact and workarounds.",
    "Cross-check each item in the register against customer service tickets and test skip decorators.",
    ("Why is an honest Known Limitations Register considered a mark of senior engineering maturity?",
     "Because all production systems have trade-offs. Transparent disclosure builds trust with client stakeholders, prevents catastrophic production misuses, and provides an immediate roadmap for future sprints.",
     "What is an example of a deliberate technical limitation in this project?",
     "Using dense hash embeddings for automated unit testing: it enables sub-second test execution without network calls or API costs, but requires remote vector embeddings for semantic nuance in production."),
    "Read `docs/week5/production-readiness/KNOWN_LIMITATIONS.md`."
)

modules["27_TECHNICAL_DEMONSTRATION.md"] = build_module(
    27, "technical-demonstration", "Conducting High-Stakes Technical Demonstrations",
    "Technical demonstrations present working software to client stakeholders, balancing architectural depth for engineering leads with business value and risk controls for executive sponsors.",
    "Preparation Checklist -> Live Demo Execution (18 Scenarios) -> Architecture Deep-Dive -> Stakeholder Q&A",
    "Structured in `docs/week5/demo/DEMO_SCRIPT.md` (18-step live scenario from health check, grounded RAG, human approval, audit trail, to failure recovery and red-team attack interception).",
    ("docs/week5/demo/DEMO_SCRIPT.md", "tests/e2e/test_scope_change_escalation.py", "docs/week5/demo/DEMO_CHECKLIST.md"),
    "- Showing static slide decks instead of live running software.\n- Only demonstrating the happy path and skipping error handling, approval gates, or recovery.",
    "Verify pre-demo checklist in `docs/week5/demo/DEMO_CHECKLIST.md` prior to presenting.",
    ("What makes a technical demonstration compelling to both business and engineering stakeholders?",
     "Showing both sides of the coin: business efficiency (rapid grounded case answers and automated workflows) combined with rigorous engineering controls (approval gates, audit trails, and security attack blocks).",
     "How should an engineer handle unexpected live demo failures?",
     "Acknowledge the symptom calmly, extract the correlation ID from the error response, inspect live logs to demonstrate troubleshooting competence, and use pre-documented emergency runbooks."),
    "Review `docs/week5/demo/DEMO_SCRIPT.md`."
)

modules["28_KNOWLEDGE_TRANSFER.md"] = build_module(
    28, "knowledge-transfer", "Knowledge Transfer (KT) Methodologies for FDEs",
    "Knowledge transfer ensures that the receiving engineering and operational teams thoroughly understand system architecture, data models, debugging patterns, and operational runbooks.",
    "FDE Engineering -> Paired Walkthroughs & Code Labs -> Runbook Drills -> Shadow On-Call -> Client Team Autonomy",
    "`docs/week5/handover/` contains 12 dedicated handover guides (`LOCAL_SETUP.md`, `OPERATIONS_GUIDE.md`, `TROUBLESHOOTING_GUIDE.md`, `OWNERSHIP_MATRIX.md`).",
    ("docs/week5/handover/HANDOVER_GUIDE.md", "tests/regression/test_regression_suite.py", "docs/week5/handover/OWNERSHIP_MATRIX.md"),
    "- Dumping code without structured documentation and walking away.\n- Conducting one-way lecture presentations rather than hands-on debugging labs.",
    "Have a receiving engineer perform a fresh install using only `docs/week5/handover/LOCAL_SETUP.md` without assistance.",
    ("What are the key stages of an effective FDE Knowledge Transfer plan?",
     "1. Documentation & Architecture Walkthrough, 2. Hands-on Local Setup & Test Suite Execution, 3. Guided Incident Troubleshooting Drills, 4. Paired On-Call Support, 5. Formal Handover Sign-Off.",
     "How do we measure the success of a knowledge transfer engagement?",
     "When the client engineering team can independently resolve an injected incident, deploy a release candidate, and add a test case without FDE intervention."),
    "Review `docs/week5/handover/HANDOVER_GUIDE.md`."
)

modules["29_HANDOVER.md"] = build_module(
    29, "handover", "Production Handover, Ownership Transition & Engagement Closure",
    "Production handover marks the formal transition of software ownership, operational accountability, and repository management from the FDE team to the client's permanent engineering organization.",
    "Handover Package Delivery -> Operational Runbook Review -> Ownership Matrix Sign-Off -> Engagement Closure",
    "Codified in `docs/week5/handover/HANDOVER_GUIDE.md`, `release/VERSION.md` (v1.0.0-rc1), and `docs/week5/DEFINITION_OF_DONE.md`.",
    ("docs/week5/handover/HANDOVER_GUIDE.md", "tests/regression/test_regression_suite.py", "docs/week5/DEFINITION_OF_DONE.md"),
    "- Incomplete ownership matrices leaving ambiguity over who supports specific subsystems.\n- Handing over undocumented environment variables or deployment procedures.",
    "Validate that all items in `docs/week5/DEFINITION_OF_DONE.md` are checked off.",
    ("What deliverables are mandatory for a production engineering handover?",
     "1. Versioned Release Candidate with release notes, 2. Passing automated test suite with baseline evidence, 3. Architectural diagrams (Mermaid), 4. Threat model & security closure report, 5. Support runbooks & troubleshooting catalogs, 6. Ownership matrix.",
     "What does the final Definition of Done signify in Week 5?",
     "It signifies that the cumulative solution satisfies 100% of curriculum requirements, has zero known unhandled regressions, and is fully ready for independent enterprise operation."),
    "Inspect `docs/week5/DEFINITION_OF_DONE.md`."
)

# Write all files to disk
for filename, content in modules.items():
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {filename}")

print("Learning modules 15-29 created successfully.")
