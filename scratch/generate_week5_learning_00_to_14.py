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

modules["00_WEEK5_OVERVIEW.md"] = build_module(
    0, "overview", "Week 5 Capstone: Integration, Hardening & Production Handover",
    "Week 5 is the final capstone phase of the FDE Fresher Readiness Program. It integrates the Week 1 CRUD backend, Week 2 data pipeline, Week 3 grounded RAG engine, and Week 4 agentic workflow into a unified, hardened, production-ready enterprise system capable of surviving scope shifts, attacks, and outages.",
    "Client Request -> API Gateway (Auth & RBAC) -> Guardrails -> Workflow Orchestrator -> [RAG Engine | Agentic Tools] -> Approval Layer -> Database & Audit",
    "In this project, Week 5 exercises the entire repository (`app/`, `pipeline/`, `rag/`, `workflow/`, `tools/`, `security/`) under 221 automated tests, validating that every component operates seamlessly without regressions.",
    ("app/main.py, workflow/orchestrator.py", "tests/regression/test_regression_suite.py", "docs/week5/WEEK5_BASELINE.md"),
    "- Treating Week 5 as a disconnected prototype rather than extending the existing codebase.\n- Relying on manual UI testing instead of automated regression test suites.\n- Fabricating metrics or test logs rather than measuring actual runtime performance.",
    "Check system baseline with `pytest tests/` and verify that all 221 tests execute in under 30 seconds with zero failures.",
    ("What differentiates an FDE deliverable from a typical software prototype?",
     "An FDE deliverable includes end-to-end integration, deterministic authorization, automated recovery from failures, structured audit trails, comprehensive performance benchmarks, and a formal handover package for client engineering teams.",
     "How does the Week 5 architecture enforce defense-in-depth?",
     "By decoupling untrusted AI model suggestions from deterministic application execution; all database writes and state transitions require code-level RBAC checks and cryptographic HMAC approval tokens."),
    "Run `pytest tests/` and inspect `docs/week5/WEEK5_TRACEABILITY_MATRIX.md` to trace curriculum requirements to code."
)

modules["01_TECHNICAL_DISCOVERY.md"] = build_module(
    1, "technical-discovery", "Technical Discovery in Client Engagements",
    "Technical discovery is the structured process of interviewing client stakeholders, analyzing existing legacy systems, cataloging data sources, uncovering hidden constraints, and establishing the technical reality before writing production code.",
    "Discovery Phase: Business Pain Points -> Legacy Data & API Audits -> Security/Auth Boundaries -> Baseline Architecture Definition",
    "Documented in `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md` for the simulated Global Bank case management engagement, analyzing legacy CSV data dumps and strict regulatory audit requirements.",
    ("docs/week5/client-engagement/TECHNICAL_DISCOVERY.md", "tests/api/test_cases_api.py", "docs/week5/client-engagement/CLIENT_PROCESS_BRIEF.md"),
    "- Assuming the client's documented process matches what their legacy systems actually do.\n- Skipping non-functional requirements such as compliance audit retention or p95 latency targets.",
    "Compare client data schemas against real database records using schema profiling scripts (`pipeline/profiler.py`).",
    ("Why must technical discovery precede architecture design in an FDE engagement?",
     "Discovery identifies real enterprise constraints (e.g. data silos, air-gapped environments, regulatory compliance requirements) that dictate architecture choices, avoiding expensive late-stage redesigns.",
     "What is the difference between a functional requirement and an architectural constraint?",
     "A functional requirement defines what the system should do (e.g., query case details), while a constraint defines limitations within which the system must operate (e.g., must run on-premise without public cloud egress)."),
    "Review `docs/week5/client-engagement/CONSTRAINTS.md` and identify 3 architectural trade-offs."
)

modules["02_REQUIREMENTS_ENGINEERING.md"] = build_module(
    2, "requirements-engineering", "Structured Requirements Engineering & Acceptance Criteria",
    "Requirements engineering translates ambiguous client briefs into measurable, testable, and unambiguous technical specifications categorized into functional, non-functional, security, and operational streams.",
    "Business Brief -> Functional & Non-Functional Requirements -> RFC 2119 Normative Statements -> Testable Acceptance Criteria",
    "Every requirement in `docs/week5/client-engagement/REQUIREMENTS.md` (e.g., REQ-001 to REQ-010) is linked to Pydantic validation schemas in `app/schemas/case.py` and automated tests.",
    ("app/schemas/case.py, tools/contracts.py", "tests/test_tools_contracts.py", "docs/week5/client-engagement/REQUIREMENTS.md"),
    "- Writing unverifiable criteria such as 'The system should be fast and secure'.\n- Failing to specify error codes and response schemas for negative paths.",
    "Verify that each requirement has an associated automated test that asserts specific HTTP status codes and response bodies.",
    ("How do you make an acceptance criterion measurable and testable?",
     "Use observable outputs: exact HTTP response codes (e.g. 422 Unprocessable Entity), RFC 7807 problem fields, p95 latency thresholds (e.g. < 50ms), or deterministic database state changes.",
     "What role do Pydantic models play in requirements enforcement?",
     "Pydantic contracts act as executable boundary specifications, enforcing data types, mandatory fields, regex patterns, and range constraints at the API threshold."),
    "Inspect `app/schemas/case.py` and observe how `CaseUpdate` enforces field constraints."
)

modules["03_CURRENT_STATE_ANALYSIS.md"] = build_module(
    3, "current-state-analysis", "Current-State System Analysis & Baseline Establishing",
    "Current-state analysis evaluates existing codebases, architectures, and data flows before applying enhancements. It identifies baseline test metrics, technical debt, and architectural dependencies.",
    "Existing Code Inspection -> Baseline Test Execution (143 Tests) -> Debt & Limitations Cataloging -> Extension Plan",
    "Documented in `docs/week5/WEEK5_BASELINE.md`, recording the 143 passed tests, 90.63% test coverage, and known limitations of the Weeks 1–4 system before introducing Week 5 modifications.",
    ("docs/week5/WEEK5_BASELINE.md", "tests/api/test_cases_api.py", "docs/week5/architecture/CURRENT_STATE_ARCHITECTURE.md"),
    "- Modifying working legacy code without first capturing an authoritative test baseline.\n- Hiding known technical debt or fragile workarounds from project documentation.",
    "Execute `pytest` on the clean baseline branch and pipe test output to an immutable baseline artifact.",
    ("Why is an authoritative baseline report essential before beginning major refactoring?",
     "It proves whether subsequent failures were introduced by new changes or pre-existed, and provides objective evidence of non-regression to client stakeholders.",
     "How do you document technical debt responsibly in an enterprise project?",
     "In a dedicated Known Limitations Register detailing the debt item, root cause, production impact, and recommended remediation."),
    "Read `docs/week5/WEEK5_BASELINE.md` and verify all baseline test suites."
)

modules["04_SYSTEM_ARCHITECTURE.md"] = build_module(
    4, "system-architecture", "System Architecture & Cross-Layer Integration",
    "System architecture defines how decoupled subsystems (web gateway, lakehouse data pipeline, grounded RAG, agentic workflows, persistence, and observability) interact coherently under unified contracts.",
    "Gateway <-> Security & RBAC <-> Workflow Orchestrator <-> [RAG Engine | Tool Registry] <-> Database & Storage",
    "Our platform integrates FastAPI routers (`app/api`), SQLAlchemy ORM (`app/models`), Parquet medallion pipelines (`pipeline/`), hybrid search (`rag/`), and LangGraph state machines (`workflow/`).",
    ("app/main.py, workflow/orchestrator.py", "tests/test_workflow_orchestration.py", "docs/week5/architecture/CURRENT_STATE_ARCHITECTURE.md"),
    "- Tight coupling between the presentation layer and persistence models.\n- Allowing AI components to directly execute database mutations without an intermediate service layer.",
    "Verify layer decoupling by asserting that tools only communicate through domain repository contracts, never raw SQL queries.",
    ("What are the key architectural layers of the Week 1–5 platform?",
     "1. Presentation/API Gateway Layer, 2. Security & Guardrail Interceptor, 3. Workflow & RAG Orchestration Layer, 4. Domain & Tool Integration Layer, 5. Lakehouse & Relational Persistence Layer.",
     "How does the architecture prevent AI hallucinations from affecting persistent data?",
     "By strictly isolating the LLM: the model can only generate structured tool proposals, which are validated against Pydantic contracts and evaluated by deterministic RBAC and approval guards before execution."),
    "Review `docs/week5/architecture/CURRENT_STATE_ARCHITECTURE.md`."
)

modules["05_COMPONENT_DIAGRAMS.md"] = build_module(
    5, "component-diagrams", "Component Diagrams & Interface Specifications",
    "Component diagrams visualize the software modules, their internal structures, interfaces, and interdependencies using standard notations like UML or Mermaid, providing an architectural blueprint.",
    "Mermaid Component Diagram: UI/Client -> [Gateway] -> [RBAC Guard] -> [Workflow Orchestrator] -> [RAG Engine] & [Tools]",
    "`docs/week5/architecture/COMPONENT_DIAGRAM.md` provides an exact Mermaid rendering matching our active codebase modules: `APIGateway`, `CorrMiddleware`, `AuthGuard`, `Router`, `RAGService`, `ToolExecutor`, and `CaseRepo`.",
    ("docs/week5/architecture/COMPONENT_DIAGRAM.md", "tests/test_tools_contracts.py", "docs/week5/architecture/COMPONENT_DIAGRAM.md"),
    "- Creating fictional diagrams that depict aspirational components not present in the code.\n- Failing to document external system interfaces and communication protocols.",
    "Cross-reference every node in the Mermaid diagram against actual Python file paths.",
    ("Why are version-controlled text diagrams (Mermaid) preferred over binary image files in FDE deliverables?",
     "Text-based diagrams live in git, participate in code reviews, show line-by-line diffs during refactoring, and cannot become disconnected from repository versions.",
     "What information should an enterprise component diagram convey?",
     "Component boundaries, exposed interfaces, consumed dependencies, communication protocols (HTTP, gRPC, IPC), and trust boundaries."),
    "Open `docs/week5/architecture/COMPONENT_DIAGRAM.md` and trace the path of an `update_ticket` request."
)

modules["06_SEQUENCE_DIAGRAMS.md"] = build_module(
    6, "sequence-diagrams", "Sequence Diagrams for Complex Distributed Workflows",
    "Sequence diagrams model dynamic runtime interactions between components over time, capturing message exchanges, conditional branches, async responses, and state machine transitions.",
    "Client -> API -> Guardrails -> Orchestrator -> Tool -> Approval Manager -> Supervisor -> Database -> Client",
    "`docs/week5/architecture/SEQUENCE_DIAGRAMS.md` specifies 4 core lifecycles: End-to-End Case Resolution, Grounded RAG Query, Consequential Tool Execution with Human Approval, and Escalation Tier Update.",
    ("docs/week5/architecture/SEQUENCE_DIAGRAMS.md", "tests/test_human_approval.py", "docs/week5/architecture/SEQUENCE_DIAGRAMS.md"),
    "- Omitting error and failure paths from sequence diagrams.\n- Failing to show asynchronous boundaries and human-in-the-loop waiting states.",
    "Validate sequence diagrams against test executions using OpenTelemetry trace logs.",
    ("Why is modeling human-in-the-loop interactions challenging in sequence diagrams?",
     "Because human approval is asynchronous and stateful: the initial request transitions the workflow to a paused state (`WAITING_FOR_APPROVAL`) and releases the worker thread until an out-of-band approval token is supplied.",
     "How do sequence diagrams aid incident troubleshooting?",
     "They provide support engineers with the exact expected order of messages and logs, allowing rapid identification of where a stalled transaction broke."),
    "Trace the approval sequence diagram in `docs/week5/architecture/SEQUENCE_DIAGRAMS.md`."
)

modules["07_DATA_FLOW.md"] = build_module(
    7, "data-flow", "Data Flow & Medallion Pipeline Architecture",
    "Data flow architecture describes how data moves, transforms, and persists from ingestion to consumption across storage tiers, such as raw Bronze, cleansed Silver, and curated Gold layers.",
    "Raw Ingestion (CSV/JSON) -> Bronze Storage -> Validation & Profiling -> Silver Parquet -> Curated Gold & RAG Index",
    "Implemented in `pipeline/`: raw data is validated against `SOURCE_CASE_SCHEMA`, invalid rows route to `quarantine`, valid data writes to Silver Parquet, and audited aggregations write to Gold.",
    ("pipeline/orchestrator.py, pipeline/validation.py", "tests/pipeline/test_orchestration.py", "docs/week5/architecture/DATA_FLOW_DIAGRAM.md"),
    "- Mutating raw data in place rather than preserving immutable Bronze snapshots.\n- Mixing analytical data pipeline logic with online transaction processing (OLTP) tables.",
    "Inspect pipeline test runs in `tests/pipeline/test_quarantine.py` to verify corrupted records are quarantined.",
    ("What is the purpose of the Medallion Architecture in enterprise data systems?",
     "It enforces progressive data quality: Bronze preserves raw unvalidated source records, Silver validates and standardizes data structures, and Gold models domain-specific analytical aggregations.",
     "How does the data pipeline interact with the Grounded RAG subsystem?",
     "Gold compliance documents and resolved case summaries are ingested by the RAG chunker and indexer to create searchable knowledge bases."),
    "Review `pipeline/validation.py` and see how quarantine schemas are structured."
)

modules["08_BACKLOG_DECOMPOSITION.md"] = build_module(
    8, "backlog-decomposition", "Backlog Decomposition & Engineering Estimation",
    "Backlog decomposition breaks down high-level business epics into structured, bite-sized, independently testable engineering work items prioritized by risk, dependencies, and value delivery.",
    "Client Epic -> Feature Themes -> Engineering Stories -> Vertical Slices -> Technical Acceptance Tasks",
    "`docs/week5/backlog/TECHNICAL_BACKLOG.md` decomposes the system into 6 vertical slices (SLICE-001 through SLICE-006) covering API, RAG, tools, approval, escalation, and audit.",
    ("docs/week5/backlog/TECHNICAL_BACKLOG.md", "tests/e2e/test_scope_change_escalation.py", "docs/week5/backlog/TECHNICAL_BACKLOG.md"),
    "- Horizontal slicing (e.g. 'Build all DB tables' then 'Build all APIs'), which delays end-to-end testing.\n- Decomposing tasks without defining verifiable completion criteria.",
    "Verify that each backlog item has an associated slice ID, acceptance criteria, and automated test suite.",
    ("Why does FDE favor vertical slicing over horizontal layer-by-layer development?",
     "Vertical slices deliver end-to-end demonstrable value early, allowing validation of cross-layer integration, security, and performance from day one.",
     "How are dependencies managed between backlog slices?",
     "By establishing core data contracts and schemas first (Week 1), enabling subsequent slices to build upon stable foundation interfaces."),
    "Inspect `docs/week5/backlog/TECHNICAL_BACKLOG.md`."
)

modules["09_VERTICAL_SLICES.md"] = build_module(
    9, "vertical-slices", "Vertical Slices Architecture & Implementation",
    "A vertical slice implements a thin, fully functional slice across all architectural tiers: client input -> gateway -> security -> domain logic -> external tools/AI -> persistence -> telemetry.",
    "Request -> Auth Middleware -> Intent Router -> Domain Service / Tool -> Persistence -> Audit Log -> Telemetry",
    "SLICE-005 in our project: User requests case escalation -> JWT checked -> RBAC validates role -> Model checks justification -> DB updates escalation_tier -> Audit log recorded.",
    ("tools/update_ticket.py, security/rbac.py", "tests/e2e/test_scope_change_escalation.py", "docs/week5/backlog/TECHNICAL_BACKLOG.md"),
    "- Leaving stubs or mock data in the middle of a slice during final integration.\n- Skipping observability or audit logging within vertical slices.",
    "Run `tests/e2e/test_scope_change_escalation.py` to observe end-to-end execution across all tiers.",
    ("What constitutes a complete vertical slice in an enterprise AI platform?",
     "It must include input validation, authentication, authorization, domain logic, data persistence, audit logging, error handling, and distributed tracing.",
     "How do vertical slices simplify regression testing?",
     "Each slice maps directly to an automated end-to-end test that verifies the full integration path in a single execution."),
    "Run `pytest tests/e2e/test_scope_change_escalation.py -v`."
)

modules["10_ACCEPTANCE_CRITERIA.md"] = build_module(
    10, "acceptance-criteria", "Codifying Technical Acceptance Criteria",
    "Technical acceptance criteria are unambiguous, observable conditions that a software deliverable must satisfy to be accepted by client stakeholders, QA, and security auditors.",
    "Requirement Statement -> GIVEN / WHEN / THEN Format -> Assertions on HTTP Status, JSON Fields, DB Rows & Logs",
    "Defined in `docs/week5/backlog/ACCEPTANCE_CRITERIA.md`. For example, AC-005.1 asserts: GIVEN an investigator user, WHEN they set `escalation_tier=CRITICAL_ESC`, THEN return HTTP 403 / UNAUTHORIZED_ESCALATION.",
    ("docs/week5/backlog/ACCEPTANCE_CRITERIA.md", "tests/security/test_red_team_suite.py", "docs/week5/backlog/ACCEPTANCE_CRITERIA.md"),
    "- Using subjective words like 'intuitive', 'fast', or 'robust'.\n- Omitting negative paths, error handling, and authorization boundary criteria.",
    "Check that every acceptance criterion has a matching assert statement in pytest.",
    ("Why should acceptance criteria be written before implementation begins?",
     "It establishes a shared definition of success between client and engineering, guides test-driven development (TDD), and prevents scope creep.",
     "How do you test acceptance criteria for non-deterministic AI generation?",
     "By testing deterministic constraints around the AI: token budget bounds, citation presence, groundedness score thresholds, and exact refusal strings on empty context."),
    "Review `docs/week5/backlog/ACCEPTANCE_CRITERIA.md`."
)

modules["11_END_TO_END_TESTING.md"] = build_module(
    11, "end-to-end-testing", "End-to-End (E2E) Testing in Enterprise Systems",
    "E2E testing validates complete application flows from initial request entry to final state persistence and external telemetry, ensuring that all integrated components collaborate correctly.",
    "E2E Test: HTTP Request -> Gateway Auth -> Workflow Router -> RAG / Tool -> State Machine -> DB Commit -> Response Verification",
    "`tests/e2e/test_scope_change_escalation.py` tests complete user journeys: escalation request, supervisor approval token issuance, token verification, ticket update, and audit log generation.",
    ("tests/e2e/test_scope_change_escalation.py", "tests/e2e/test_scope_change_escalation.py", "docs/week5/testing/REGRESSION_STRATEGY.md"),
    "- Relying on brittle external network dependencies during automated E2E runs.\n- Not resetting database state between test cases, causing flaky test pollution.",
    "Run `pytest tests/e2e/` with SQLAlchemy session rollback fixtures to guarantee state isolation.",
    ("What is the primary objective of E2E testing compared to unit testing?",
     "Unit tests verify individual functions in isolation; E2E tests verify cross-component contracts, serialization, state transitions, security boundaries, and database persistence under realistic workflows.",
     "How do we prevent E2E tests from being slow and flaky in AI applications?",
     "Use fast in-memory database instances, mock external LLM network latency with deterministic providers, and isolate state using transactional test fixtures."),
    "Execute `pytest tests/e2e/test_scope_change_escalation.py -v`."
)

modules["12_INTEGRATION_TESTING.md"] = build_module(
    12, "integration-testing", "Cross-Layer Integration Testing",
    "Integration testing focuses on the interfaces and interactions between adjacent modules (e.g., API router to domain service, domain service to repository, workflow to tool contract).",
    "Module A (API) <-> Interface Contract <-> Module B (Service) <-> Persistence Contract <-> Module C (Database)",
    "`tests/api/test_cases_api.py` and `tests/test_tools_contracts.py` test integration between FastAPI request bodies, Pydantic tool schemas, and SQLAlchemy case models.",
    ("app/api/cases.py, tools/update_ticket.py", "tests/api/test_cases_api.py", "docs/week5/testing/REGRESSION_STRATEGY.md"),
    "- Over-mocking: mocking the database, the repository, and the schema until no real integration is actually tested.\n- Ignoring serialization edge cases such as datetime timezone handling.",
    "Execute tests with real SQLite test databases and verify actual table writes.",
    ("What distinguishes integration testing from E2E testing?",
     "Integration tests verify specific pairwise component contracts (e.g. service + database), while E2E tests exercise the complete path from the public API entry point through all subsystems.",
     "Why must tool contracts be rigorously integration-tested in agentic AI architectures?",
     "Because LLM tool-calling engines produce structured JSON; if the tool contract validation is loose, malformed arguments could corrupt the database or trigger unhandled server exceptions."),
    "Run `pytest tests/test_tools_contracts.py -v`."
)

modules["13_REGRESSION_TESTING.md"] = build_module(
    13, "regression-testing", "Regression Testing Strategies for Cumulative Codebases",
    "Regression testing ensures that new features, bug fixes, or architectural refactorings in current weeks do not break or degrade previously working functionality from earlier weeks.",
    "Cumulative Test Suite: [Week 1 API & DB] + [Week 2 Pipeline] + [Week 3 RAG] + [Week 4 Workflows] + [Week 5 Hardening] = 221 Tests",
    "`tests/regression/test_regression_suite.py` executes 17 targeted regression checks across all 5 weeks, confirming that core CRUD, parquet pipelines, RAG citations, and HMAC approvals remain 100% operational.",
    ("tests/regression/test_regression_suite.py", "tests/regression/test_regression_suite.py", "docs/week5/testing/REGRESSION_STRATEGY.md"),
    "- Only running tests for the newly written module and skipping previous weeks' test suites.\n- Silently modifying old test assertions when code breaks rather than fixing the underlying regression.",
    "Run `pytest tests/` in CI/CD pipeline before every merge; enforce 100% pass requirement.",
    ("How does an FDE prevent regressions when adding new client requirements?",
     "By establishing an automated regression test baseline, practicing backward-compatible schema evolutions (e.g., nullable default columns in migrations), and enforcing automated test runs on all pull requests.",
     "What should an engineer do if a legacy test fails after adding a new feature?",
     "Investigate whether the failure represents a true functional regression or a deliberate, agreed-upon behavioral change. If regression, fix the new code immediately."),
    "Execute `pytest tests/regression/test_regression_suite.py -v`."
)

modules["14_NEGATIVE_PATH_TESTING.md"] = build_module(
    14, "negative-path-testing", "Negative-Path & Boundary Condition Testing",
    "Negative-path testing systematically subjects the system to invalid, malformed, unexpected, and boundary-exceeding inputs to verify that it fails safely and deterministically without crashing.",
    "Input -> [Malformed JSON / Missing Fields / Giant Strings / Null Bytes] -> Gateway Validation -> HTTP 422 / 400 + Structured Error",
    "`tests/negative/test_negative_paths.py` contains 18 tests evaluating missing mandatory fields, negative amounts, oversized strings, expired tokens, duplicate IDs, and invalid status transitions.",
    ("tests/negative/test_negative_paths.py", "tests/negative/test_negative_paths.py", "docs/week5/testing/REGRESSION_STRATEGY.md"),
    "- Only testing happy-path valid data and assuming client applications will always send conformant payloads.\n- Allowing uncaught 500 Internal Server Errors on malformed client requests.",
    "Ensure all negative test cases assert structured error models (RFC 7807) and specific status codes (400, 401, 403, 422).",
    ("Why is negative-path testing crucial in production AI applications?",
     "AI models and external web clients regularly generate unpredictable, truncated, or malformed inputs. Deterministic validation layers ensure these anomalies never cause crashes or undefined database states.",
     "What status code should a FastAPI endpoint return for a body with syntax errors versus business rule violations?",
     "HTTP 422 Unprocessable Entity for schema/syntax validation errors; HTTP 400 Bad Request or HTTP 403 Forbidden for semantic business rule or authorization violations."),
    "Run `pytest tests/negative/test_negative_paths.py -v`."
)

# Write all files to disk
for filename, content in modules.items():
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {filename}")

print("Learning modules 00-14 created successfully.")
