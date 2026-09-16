# Week 2 Enterprise Data Pipeline: Architecture Specification

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Sources ["1. Heterogeneous Sources"]
        S1["cases.csv<br>(Operational Logs)"]
        S2["reference.json<br>(Users & Depts)"]
        S3["policy_metadata.parquet<br>(SLA Targets)"]
        S4["REST API<br>(GET /mock/policies)"]
        S5["SQLite / PostgreSQL<br>(OLTP cases.db)"]
    end

    subgraph Bronze ["2. Raw Layer (Bronze)"]
        R1["data/raw/cases/ingest_date=YYYY-MM-DD/<br>raw_cases.parquet"]
        R2["Lineage: _ingested_at, _source_name, _run_id"]
    end

    subgraph Profile ["3. Statistical Profiling"]
        P1["DataProfiler Engine<br>• Completeness (Null rates)<br>• Uniqueness (Cardinality)<br>• Validity (Enums & types)<br>• Distribution (Percentiles)<br>• Referential Integrity (Orphans)"]
        P2["reports/profiling/<br>profiling_RUN_*.md & .json"]
    end

    subgraph Silver ["4. Quality & Standardized Layer (Silver)"]
        Q1{"QualityRulesEvaluator<br>(8 Critical Domain Rules)"}
        Q2["data/rejected/<br>rejected_RUN_*.json<br>(Quarantine Dead-Letter)"]
        Q3["data/standardized/cases/<br>std_cases.parquet<br>(Cleansed & Enforced)"]
    end

    subgraph Transform ["5. Transformation Engine"]
        T1["Deduplication (PK + Latest TS)"]
        T2["Relational Joins (Users, Depts, Policies)"]
        T3["Window Analytics (Dense Rank & Sequences)"]
        T4["Summary Aggregations (SLA KPIs)"]
    end

    subgraph Gold ["6. Curated Layer (Gold)"]
        C1["data/curated/cases/curated_cases.parquet<br>(High-Speed Columnar)"]
        C2["data/curated/cases/curated_cases.csv<br>(Business Export)"]
        C3["SQLite Table: curated_cases<br>(Sub-Second SQL Queries)"]
    end

    subgraph Control ["7. Integrity, Lineage & Reconciliation"]
        M1["ReconciliationEngine<br>Source == Valid + Quarantined<br>Curated == Valid - Duplicates"]
        M2["reports/reconciliation/<br>reconciliation_RUN_*.md & .json"]
        M3["AuditManager<br>manifest_RUN_*.json & execution_ledger.jsonl"]
        M4["WatermarkTracker<br>audit/watermark.json (Incremental Delta State)"]
    end

    Sources --> Bronze
    Bronze --> Profile
    Profile --> Q1
    Q1 -->|Corrupted / Non-Compliant| Q2
    Q1 -->|100% Clean Records| Q3
    Q3 --> Transform
    Transform --> Gold

    Bronze -.-> M1
    Q2 -.-> M1
    Gold -.-> M1
    M1 --> M2
    M1 --> M3
    M1 --> M4
```

---

## 2. Component Responsibility Matrix

| Component | Module | Responsibility | Key Classes & Functions |
|---|---|---|---|
| **Sources** | `pipeline/sources/` | Ingestion from CSV, JSON, Parquet, SQLite, REST API with fallback | `CSVSource`, `JSONSource`, `ParquetSource`, `DatabaseSource`, `APISource` |
| **Contracts** | `pipeline/schemas/` | Schema validation, contract declarations, enum constraints | `DataContract`, `SchemaValidator`, `CASE_SOURCE_CONTRACT` |
| **Profiler** | `pipeline/profiling/` | Vectorized 5-pillar statistical profiling and reporting | `DataProfiler` |
| **Quality Engine** | `pipeline/validation/` | Evaluating 8 domain rules, partitioning valid vs invalid | `QualityRulesEvaluator`, `QualityRule`, `CASE_QUALITY_RULES` |
| **Quarantine** | `pipeline/quarantine/` | Persisting dead-letter payloads with root-cause failure metadata | `QuarantineManager` |
| **Transformations** | `pipeline/transformations/` | Type standardization, timestamp parsing, deduplication, joins, windowing, rollups | `standardize_case_records`, `deduplicate_cases`, `join_case_reference_and_policies`, `apply_window_metrics`, `aggregate_department_sla_summary` |
| **Medallion Layers** | `pipeline/layers/` | Managing Raw Bronze, Standardized Silver, and Curated Gold tiers | `RawLayerManager`, `StandardizedLayerManager`, `CuratedLayerManager` |
| **Reconciliation** | `pipeline/reconciliation/` | Mathematical balancing, variance alerts, Markdown reports | `ReconciliationEngine` |
| **Audit & State** | `pipeline/audit/`, `pipeline/orchestration/` | Run manifests, JSONL execution ledgers, high-watermark delta state | `AuditManager`, `WatermarkTracker` |
| **Orchestrator** | `pipeline/orchestration/` | Master 10-stage execution DAG and state machine | `CaseManagementPipeline` |
| **CLI Runner** | `pipeline/cli.py` | Command-line interface with flags (`--mode full/incremental`, `--file`) | `main` CLI runner |
