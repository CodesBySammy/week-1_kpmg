# Week 2 Architecture Decision Records (ADR)

This document records the architectural decisions made during Week 2 data pipeline development.

---

## ADR-008: Medallion Architecture (Bronze -> Silver -> Gold)
* **Status**: ACCEPTED
* **Context**: Need a structured data tiering strategy that preserves unadulterated source history while providing clean, typed tables for analysts and AI models.
* **Decision**: Implement a 3-tier Medallion architecture: Raw Bronze (`data/raw/` date-partitioned Parquet), Standardized Silver (`data/standardized/` cleansed Parquet), and Curated Gold (`data/curated/` Parquet, CSV, and SQLite).
* **Consequences**: Enables historical re-processing from Bronze without querying operational databases.

---

## ADR-009: Strict Two-Stage Source-to-Target Reconciliation
* **Status**: ACCEPTED
* **Context**: Need mathematical proof of zero data loss across transformations and filtering.
* **Decision**: Enforce two balancing equations on every execution:
  1. $\text{Source} = \text{Valid} + \text{Quarantined}$
  2. $\text{Curated} = \text{Valid} - \text{Duplicates Removed}$
  If either equation yields variance $\neq 0$, the run fails immediately.
* **Consequences**: Guarantees non-repudiation and immediate alerting upon data leakage.

---

## ADR-010: Dead-Letter Quarantine Sink over Fail-Stop
* **Status**: ACCEPTED
* **Context**: Ingesting operational data with minor human input defects shouldn't crash processing for 100,000 valid records.
* **Decision**: Implement a non-blocking quarantine sink (`data/rejected/rejected_<run_id>.json`). Corrupted rows are diverted with rule ID and failure reason metadata, while valid rows proceed.
* **Consequences**: Non-blocking pipeline resilience with zero data loss.

---

## ADR-011: High-Watermark Incremental Processing with Two-Phase Commit
* **Status**: ACCEPTED
* **Context**: Processing full historical reloads daily is unsustainable as data volume grows.
* **Decision**: Implement `WatermarkTracker` tracking $\max(\text{updated\_at})$ in `audit/watermark.json`. Crucially, the watermark is committed *only after* curated data has landed and reconciliation has passed.
* **Consequences**: Bounded compute cost with zero risk of skipping uncommitted records during mid-run failures.

---

## ADR-012: Multi-Stage Docker Build with Non-Root User
* **Status**: ACCEPTED
* **Context**: Need containerized execution that runs identically across local dev and cloud clusters without security risks.
* **Decision**: Use a multi-stage Docker build targeting `python:3.11-slim` with an unprivileged `appuser` (UID non-root) and host bind mounts for persistent data outputs.
* **Consequences**: Secure, lightweight container image compliant with enterprise security policies.
