# Module 07: Data Flow & Medallion Pipeline Architecture

## 1. Simple Explanation
Data flow architecture describes how data moves, transforms, and persists from ingestion to consumption across storage tiers, such as raw Bronze, cleansed Silver, and curated Gold layers.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Data Flow & Medallion Pipeline Architecture provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Raw Ingestion (CSV/JSON) -> Bronze Storage -> Validation & Profiling -> Silver Parquet -> Curated Gold & RAG Index
```

## 5. Project-Specific Implementation
Implemented in `pipeline/`: raw data is validated against `SOURCE_CASE_SCHEMA`, invalid rows route to `quarantine`, valid data writes to Silver Parquet, and audited aggregations write to Gold.

## 6. Code & Module Mapping
- **Implementation File(s)**: `pipeline/orchestrator.py, pipeline/validation.py`
- **Test File(s)**: `tests/pipeline/test_orchestration.py`
- **Documentation Reference**: `docs/week5/architecture/DATA_FLOW_DIAGRAM.md`

## 7. Common Pitfalls & Mistakes
- Mutating raw data in place rather than preserving immutable Bronze snapshots.
- Mixing analytical data pipeline logic with online transaction processing (OLTP) tables.

## 8. Troubleshooting & Diagnostic Guide
Inspect pipeline test runs in `tests/pipeline/test_quarantine.py` to verify corrupted records are quarantined.

## 9. Interview Questions & Detailed Answers
### Q1: What is the purpose of the Medallion Architecture in enterprise data systems?
**Answer**: It enforces progressive data quality: Bronze preserves raw unvalidated source records, Silver validates and standardizes data structures, and Gold models domain-specific analytical aggregations.

### Q2: How does the data pipeline interact with the Grounded RAG subsystem?
**Answer**: Gold compliance documents and resolved case summaries are ingested by the RAG chunker and indexer to create searchable knowledge bases.

## 10. Practical Hands-On Exercise
Review `pipeline/validation.py` and see how quarantine schemas are structured.
