# Week 2 Enterprise Data Engineering Self-Assessment: Answer Key & Rubric

Use this document to score your responses to `week2-self-assessment.md`.

---

## Part 1: Multiple Choice Answers

| Question | Correct Option | Explanation |
|:---:|:---:|---|
| **Q1** | **C** | Apache Parquet is a columnar format supporting predicate pushdown, dictionary encoding, and embedded Arrow schemas. |
| **Q2** | **B** | The Bronze layer stores an immutable, append-only copy of source data verbatim with ingestion timestamps and lineage. |
| **Q3** | **B** | The core balancing equation is $\text{Source Count} = \text{Valid Count} + \text{Quarantined Count}$. |
| **Q4** | **B** | Reading as raw strings preserves defect strings so profilers and rule evaluators can inspect and quarantine them without silent truncation. |
| **Q5** | **B** | JSON Lines can be parsed line-by-line using streaming iterators in constant $O(1)$ memory. |
| **Q6** | **C** | Pandas `Int64` (capital 'I') supports nullable integer representations using an internal boolean bitmask. |
| **Q7** | **B** | Forward compatibility allows old consumers to safely read data produced by newer schemas by ignoring newly added optional fields. |
| **Q8** | **B** | A broadcast hash join copies the small lookup table to all worker nodes, eliminating network shuffle of the large fact table. |
| **Q9** | **C** | `DENSE_RANK()` does not skip rank numbers after ties: `[10, 10, 25]` becomes `[1, 1, 2]`. |
| **Q10** | **B** | A quarantine sink isolates defective records into a dead-letter location with root-cause failure metadata without halting clean processing. |
| **Q11** | **B** | A circuit breaker trips and halts processing when the failure rate exceeds a critical threshold (e.g. > 10%), indicating systemic corruption. |
| **Q12** | **C** | The high-watermark must only be committed at the end of the run after curated data has landed and reconciliation has passed. |
| **Q13** | **B** | Idempotency means executing an operation multiple times produces the exact same system state as executing it once ($f(f(x)) = f(x)$). |
| **Q14** | **B** | A positive source variance indicates data leakage where records disappeared inside transformation logic without being counted in quarantine. |
| **Q15** | **B** | Storing UTC timestamps eliminates timezone ambiguity across global regions, server clocks, and Daylight Saving Time shifts. |
| **Q16** | **B** | The Catalyst Optimizer analyzes query ASTs, pushes down predicates, prunes columns, and generates optimized physical execution plans. |
| **Q17** | **B** | Multi-stage builds strip compilers and build caches from the final container, drastically reducing image size and attack surface. |
| **Q18** | **B** | Running as an unprivileged user (`appuser`) prevents attackers who compromise container processes from escalating to host root privileges. |
| **Q19** | **B** | The manifest is a single-run execution snapshot; the ledger is an append-only JSONL stream tracking all past pipeline executions. |
| **Q20** | **A** | Sorting by `case_id` and `updated_at` ascending and keeping the `last` record deterministically preserves the latest state of each case. |

---

## Part 2: System Design & Scenario Solutions

### Q21: Handling String User IDs (`"USR-101"`)
**Solution**: 
1. In `standardize_case_records`, the coercion `pd.to_numeric(df["created_by"], errors="coerce")` converts `"USR-101"` into `<NA>`.
2. In `QualityRulesEvaluator`, `RULE-CASE-006` (`check_referential_creator`) checks if `created_by` is a valid positive integer in the reference set.
3. The rule evaluator flags the row as invalid with reason: `"created_by 'USR-101' is not a valid integer"`.
4. The record is diverted to `data/rejected/rejected_<run_id>.json`, while clean records continue to Curated storage.

### Q22: Handling Late-Arriving Data
**Solution**:
1. Implement a **Sliding Lookback Window**: subtract a safety buffer (e.g. 2 hours) from the committed watermark: $\text{query\_ts} = \text{watermark} - \text{buffer}$.
2. Ingest all records where `updated_at > query_ts`.
3. In Stage 7, execute deterministic deduplication (`deduplicate_cases`) by sorting on `case_id` and `updated_at` ascending and keeping the `last` record.
4. This seamlessly updates existing records with fresher data while absorbing duplicate overlap.

### Q23: Why Non-Unique Join Keys Cause Reconciliation Failure
**Solution**:
If a dimension lookup table has duplicate entries for a join key (e.g. two rows for `priority='HIGH', case_type='BUG'`), a `LEFT JOIN` duplicates every matching fact row. 
If 100 valid cases are joined, the output becomes 150 rows. 
Equation 2 states: $\text{Curated} = \text{Valid} - \text{Duplicates}$. 
$150 \neq 100 - 0$, causing a **curated variance of $+50$**, tripping an immediate reconciliation failure alert.

### Q24: Why Immutable Bronze is Safer than In-Place Mutation
**Solution**:
In-place mutations destroy historical state. If an upstream bug sends corrupt data for a week, or if a newly deployed cleansing script has a regex bug that truncates case titles, in-place systems irreversibly destroy historical data. With an immutable Bronze layer, you can fix the script, wipe Silver/Gold, and re-execute the entire pipeline from historical Bronze Parquet without requesting backups.

### Q25: Projection Pruning and Cloud Costs
**Solution**:
Cloud data warehouses (AWS Athena, BigQuery, Snowflake) charge based on the number of bytes scanned from storage. If a table has 50 columns totaling 1 TB, but a daily report only queries `case_id`, `status`, and `priority` (50 GB of columnar Parquet), projection pruning scans only 50 GB, cutting query processing costs and execution time by **95%**.

### Q26: Crash Recovery via Idempotency
**Solution**:
Because Curated publishing uses atomic file overwrites (`mode="overwrite"`) and SQL replacement (`if_exists="replace"` or `MERGE INTO`), rerunning the failed pipeline cleanly replaces partial or incomplete writes from the crashed run. It does not append duplicate rows or leave orphaned records.

### Q27: Lazy Transformations vs Eager Actions in Spark
**Solution**:
- **Lazy Transformations** (`select`, `filter`, `join`, `groupBy`) do not compute immediately; they append logical operations to an execution DAG.
- **Eager Actions** (`count`, `show`, `write.parquet`) trigger actual physical cluster execution.
- Lazy evaluation enables Catalyst to optimize the entire query end-to-end (e.g. merging two filters into one and pushing them down to Parquet) before reading any data from disk.

### Q28: The 4 Golden PagerDuty Alert Metrics
**Solution**:
1. **Reconciliation Status**: Fire `CRITICAL` alert if `reconciliation_status == "FAIL"`.
2. **Quarantine Rate**: Fire `CRITICAL` alert if $\frac{\text{quarantined\_records}}{\text{source\_records}} > 0.10$ (Circuit Breaker).
3. **Data Freshness SLA**: Fire `WARNING` alert if $\text{current\_time} - \max(\text{curated\_updated\_at}) > 24 \text{ hours}$.
4. **Execution Duration**: Fire `WARNING` alert if pipeline runtime exceeds $3\times$ the historical moving average.

### Q29: Host Bind Mounts in Docker Data Pipelines
**Solution**:
Docker containers have ephemeral filesystems; files written inside a container are destroyed when the container terminates. By mounting host folders (`-v $(pwd)/data:/app/data`), the container writes directly to host storage, allowing developers, CI/CD artifacts, and host databases to immediately access the generated Parquet files, reports, and manifests.

### Q30: 6 Steps to Debug Reconciliation Failure
**Solution**:
1. **Triage**: Inspect `audit/manifest_<run_id>.json` to identify the failing run and duration.
2. **Isolate Variance**: Compare `source_count`, `valid_count`, `quarantined_count`, `duplicates_removed`, and `curated_count` in `reports/reconciliation/reconciliation_<run_id>.json`.
3. **Inspect Quarantine**: Read `data/rejected/rejected_<run_id>.json` to review the rule IDs and rejection reasons for all quarantined records.
4. **Reproduce**: Extract the problematic input rows into `tests/pipeline/` and run `pytest -k test_failures`.
5. **Fix & Verify**: Correct the rule evaluator or join logic, re-run `pytest`, and verify 100% test pass rate and zero variance.
6. **Prevent**: Update data contract tests to assert the edge case is permanently defended against.
