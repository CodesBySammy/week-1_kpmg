# Week 2 Enterprise Data Engineering Interview Questions & Master Solutions

This guide contains **50 top enterprise data engineering interview questions** covering architecture, formats, data quality, reconciliation, idempotency, streaming vs batch, Spark, and Docker.

---

### Ingestion & Data Formats (Q1 - Q10)

#### Q1: Why is Apache Parquet preferred over CSV and JSON for analytical data warehouses?
**Answer:** 
1. **Columnar Projection Pruning**: Parquet stores data column-by-column rather than row-by-row. When queries request 3 columns out of 50, only those 3 column chunks are read from disk, saving 90%+ I/O bandwidth.
2. **High Compression Ratios**: Homogeneous data types stored contiguously compress drastically better using run-length and dictionary encoding with Snappy/Zstandard (70-85% size reduction vs CSV).
3. **Embedded Schema Metadata**: Parquet files embed strongly-typed Apache Arrow/Thrift schemas in their footers, eliminating type inference guessing.
4. **Predicate Pushdown (Statistics)**: Parquet footers store `min`/`max`/`null_count` per row group, allowing engines to skip entire row groups without reading them.

#### Q2: What is RFC 4180, and what are the most common failure modes when ingesting CSV files in production?
**Answer:** RFC 4180 is the standard specification for CSV format. Common production failures include:
- Unescaped delimiters inside text columns (e.g. `"San Francisco, CA"` without quotes splitting into two columns).
- Embedded line breaks (`\n` or `\r\n`) within user comments splitting single logical records into multiple erroneous lines.
- Unhandled null representations (`"NA"`, `"null"`, `""`, `"-999"`).
- Leading zero truncation (zip codes `'01234'` coerced into integer `1234`).
- Ambiguous date formats (e.g., `'03/04/2026'` representing March 4 vs April 3).

#### Q3: How do you prevent Out-Of-Memory (OOM) errors when ingesting a 50 GB CSV on a 16 GB RAM server?
**Answer:** Ingest in bounded chunks using streaming iterators (`pd.read_csv(..., chunksize=10000)` or PySpark/DuckDB streaming cursors). Each chunk is read, validated, standardized, and immediately appended to partitioned Parquet files before processing the next chunk, keeping memory consumption strictly $O(\text{chunksize})$.

#### Q4: What is the difference between standard JSON and JSON Lines (NDJSON), and when should you use each?
**Answer:** Standard JSON encapsulates an entire dataset in a single root array or object (`[...]`), requiring the entire file to be loaded and parsed in memory at once. JSON Lines (`.jsonl` or `.ndjson`) stores each record as a standalone, valid JSON string on a single line separated by newline characters. JSON Lines is preferred for logs, streaming queues, and large datasets because it can be read and written line-by-line in constant memory $O(1)$.

#### Q5: How do you ingest data from a production OLTP database without degrading application performance?
**Answer:**
1. Query a **Read Replica** rather than the primary master database.
2. Use **server-side cursors** (`execution_options(stream_results=True)` in SQLAlchemy) to stream rows in batches rather than buffering all rows in client memory.
3. Constrain extracts with indexed timestamp boundaries (`WHERE updated_at > :watermark`).
4. Set transaction isolation to `READ COMMITTED` or `REPEATABLE READ` to avoid locking rows.

#### Q6: How do you handle transient network failures and HTTP 429 errors when ingesting from REST APIs?
**Answer:** Implement **Exponential Backoff with Random Jitter**:
$$\text{delay} = 2^{\text{attempt}} + \text{uniform}(0, 1)$$
Set explicit connection and read timeouts on every request. On non-retryable 4xx client errors (400, 401, 403), fail immediately. On retryable 5xx server errors or 429 rate limits, back off and retry up to $N$ times. For resilient batch pipelines, provide a local cached fallback dataset for critical reference metadata.

#### Q7: What is Cursor-Based Pagination, and why is it superior to Offset/Limit pagination in real-time databases?
**Answer:** Offset pagination (`LIMIT 50 OFFSET 1000`) forces the database to scan and discard 1,000 index rows before returning 50 rows. Furthermore, if new records are inserted while a client paginates, records shift, causing the client to read duplicate rows or skip rows entirely. Cursor-based pagination uses an indexed unique value (`WHERE id > :last_seen_id ORDER BY id LIMIT 50`), executing in $O(1)$ index time with zero risk of missed or duplicated rows.

#### Q8: What is PyArrow, and how does it relate to Apache Arrow and Pandas?
**Answer:** Apache Arrow is an open-source, language-independent columnar memory specification designed for zero-copy data sharing between systems (Python, C++, Java, R). PyArrow is the official Python binding for Apache Arrow. Pandas 2.0+ can use PyArrow as its underlying memory engine (`string[pyarrow]`, `int64[pyarrow]`), providing drastic RAM savings, SIMD vectorization, and instant zero-copy conversions between Pandas, Parquet, and Spark.

#### Q9: What happens when an ingestion pipeline encounters schema drift (e.g. an extra column is added upstream)?
**Answer:** Under **tolerant schema evolution**, non-breaking additive changes (extra optional columns) are accepted, passed through to the Bronze raw layer, and stored without breaking the pipeline. Under strict contracts, schema drift triggers an alert. Breaking changes (e.g. missing required columns or altered data types) cause the contract validator to reject the batch and alert engineers.

#### Q10: Why should raw ingestion readers initially read text fields with `dtype=str`?
**Answer:** If an automated parser attempts to infer types prematurely, corrupted records (e.g., `'N/A'` or `'ERR-500'` in an integer column) are either coerced into `NaN` (silently losing the defect string) or cause the entire file read to crash. Ingesting as raw strings preserves the exact dirty input, allowing the Data Profiler and Quality Rules Engine to inspect the defect, capture root cause, and quarantine the record.

---

### Data Profiling & Quality Engineering (Q11 - Q20)

#### Q11: What are the 5 fundamental pillars of data profiling?
**Answer:**
1. **Completeness**: Null ratios, missing value percentages, empty string counts.
2. **Uniqueness**: Cardinality, distinct counts, primary key duplicate detection.
3. **Validity**: Conformance to business enums, regex patterns, boundary limits.
4. **Distribution**: Minimum, maximum, mean, median, IQR percentiles, standard deviation.
5. **Referential Integrity**: Foreign key orphans, unmatched parent entity IDs.

#### Q12: Why is data testing in data engineering different from code testing in software engineering?
**Answer:** Code testing (`pytest`) tests deterministic algorithms against static, controlled inputs written by developers. Data testing tests non-deterministic, dynamic inputs generated by millions of external users, third-party APIs, and distributed microservices. Passing 100% of unit tests does not prevent bad data from corrupting reports; continuous, runtime data quality testing is required.

#### Q13: What is a Quarantine Dead-Letter Sink, and why is it superior to failing the pipeline?
**Answer:** A Quarantine Sink diverts non-compliant or corrupted records into a dedicated storage location (`data/rejected/rejected_<run_id>.json`) along with root-cause failure metadata (rule ID, explanation, timestamp), while allowing valid records to continue processing. This guarantees **non-blocking pipeline resilience** while achieving **zero data loss** and complete auditability.

#### Q14: When should a data pipeline choose Fail-Stop over Fail-Continue?
**Answer:** 
- **Fail-Continue (Quarantine)**: For isolated, record-level defects (e.g., 5 invalid records out of 10,000).
- **Fail-Stop (Abort)**: For systemic or structural failures (missing source file, database connection lost, broken data contract missing a core column, or when quarantine rate exceeds a circuit breaker threshold such as > 10% of total volume).

#### Q15: How does Great Expectations differ from custom rule-based evaluators?
**Answer:** Great Expectations provides declarative, pre-built assertions ("Expectations"), an automated HTML data doc generator, and integration with data orchestration tools. Custom rule evaluators (like our `QualityRulesEvaluator`) are lightweight, have zero external dependencies, embed directly inside micro-batch DAGs, and provide instant custom quarantine payloads.

#### Q16: How do you detect and handle outliers in pipeline metrics like resolution time?
**Answer:** Calculate the Interquartile Range ($IQR = Q3 - Q1$). Any data point where $X < Q1 - 1.5 \times IQR$ or $X > Q3 + 1.5 \times IQR$ is classified as a statistical outlier. Outliers should be flagged for investigation rather than blindly deleted, as they often represent genuine operational incidents (e.g., a case stuck in triage for 3 months).

#### Q17: What is referential integrity checking in a data pipeline?
**Answer:** Verifying that foreign key references in a fact dataset resolve to existing primary keys in a lookup or dimension dataset. For example, verifying that every case's `created_by` user ID exists in the employee reference table. If it does not exist, the record is flagged as an orphan and quarantined.

#### Q18: What is the difference between a Warning rule and a Critical rule in data quality?
**Answer:**
- **Critical Rule**: Breaching it invalidates core business logic or downstream reporting (e.g., null primary key, negative price, invalid status). Action: Divert record to quarantine.
- **Warning Rule**: Breaching it indicates an anomaly or minor imperfection that does not invalidate the record (e.g., missing non-critical description, unusual text length). Action: Log warning, allow record to proceed.

#### Q19: Why should data quality rules return both a boolean and an explanatory reason string?
**Answer:** Simply knowing that a record failed (`passed = False`) is useless to an on-call engineer or data steward. Returning `(False, "Status 'CANCEL' not in allowed enum ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']")` provides immediate, actionable root-cause intelligence in the quarantine payload.

#### Q20: What is a Circuit Breaker in data engineering pipelines?
**Answer:** A safety threshold that halts the pipeline if the percentage of quarantined records exceeds an acceptable limit (e.g., > 5% or > 10%). If 2,000 out of 10,000 records fail validation, it indicates a major upstream breaking change or file corruption; halting prevents polluting quarantine storage and alert systems.

---

### Transformations, Deduplication & Medallion Architecture (Q21 - Q30)

#### Q21: What are the three tiers of the Medallion Architecture, and what is the responsibility of each?
**Answer:**
1. **Raw (Bronze)**: Immutable, append-only landing of raw data verbatim, with ingestion timestamp and source lineage metadata.
2. **Standardized (Silver)**: Cleansed, schema-enforced, normalized single source of truth; corrupted rows diverted to quarantine; primary keys deduplicated.
3. **Curated (Gold)**: Business-ready, dimensional models enriched with reference lookups, pre-computed aggregations, and business KPIs for BI and AI consumption.

#### Q22: Why should data never be transformed or cleaned in the Bronze/Raw layer?
**Answer:** The Bronze layer serves as the ultimate historical truth. If business transformation logic changes 6 months later, or if a bug is discovered in cleansing code, having an unadulterated raw copy allows engineers to re-run transformations from Bronze without requesting re-exports from operational source systems.

#### Q23: How do you achieve deterministic primary key deduplication when duplicate natural keys arrive?
**Answer:** Sort by primary key and the record mutation timestamp (`updated_at`) ascending, then keep the `last` record (`df.sort_values([pk, ts]).drop_duplicates(subset=[pk], keep="last")`). This guarantees that the most recent state of the entity is preserved.

#### Q24: What is the difference between a Broadcast Hash Join and a Shuffle Sort-Merge Join in distributed systems?
**Answer:**
- **Broadcast Hash Join**: The small reference table (< 100 MB) is copied in its entirety to all worker nodes. The large fact table never moves across the network. Zero network shuffling makes it $O(N)$ and ultra-fast.
- **Shuffle Sort-Merge Join**: Both large tables are hashed by join key, shuffled across the network to corresponding partition nodes, sorted, and merged. Used when both tables are massive.

#### Q25: How do you prevent join cardinality explosions (Cartesian multiplications) during enrichment?
**Answer:** Ensure the dimension/lookup dataset is strictly deduplicated on the join keys before executing the merge (`policies_df.drop_duplicates(subset=['case_type', 'priority'])`). If join keys are not unique in the lookup table, a `LEFT JOIN` duplicates fact records, causing reconciliation count balancing to fail.

#### Q26: What is the difference between SQL `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`?
**Answer:** For values `[10, 10, 20]`:
- `ROW_NUMBER()`: Assigns sequential numbers without ties (`1, 2, 3`).
- `RANK()`: Assigns identical numbers for ties, but skips subsequent numbers (`1, 1, 3`).
- `DENSE_RANK()`: Assigns identical numbers for ties, but does NOT skip subsequent numbers (`1, 1, 2`).

#### Q27: When should you use a window function instead of a `GROUP BY` aggregation?
**Answer:** Use `GROUP BY` when you want to reduce multiple rows into a single summary rollup row per group. Use `WINDOW` functions when you need to calculate group-level metrics (rankings, running totals, lead/lag intervals) while **retaining every individual row's identity and attributes**.

#### Q28: What is Lead/Lag in window operations, and how is it used in operational pipelines?
**Answer:** `LAG(col, 1)` accesses the value of a column from the previous row in the ordered partition; `LEAD(col, 1)` accesses the value from the next row. In case management, `LAG(status_changed_at)` computes the dwell time a ticket spent in a specific state before being transitioned.

#### Q29: Why should all pipeline timestamps be converted to UTC with explicit timezone metadata?
**Answer:** Ambiguous local timestamps (e.g. `'2026-03-01 10:00:00'`) cause catastrophic errors when calculating resolution intervals across globally distributed users or across Daylight Saving Time (DST) transitions. UTC provides a continuous, monotonically increasing universal timeline.

#### Q30: What is nullable integer type `Int64` in Pandas, and why is it preferred over `int64` or `float64`?
**Answer:** Standard NumPy `int64` does not support `NaN` or missing values; if an integer column has a single null, NumPy forces the entire column to `float64`, converting ID `5` into `5.0`. Pandas nullable `Int64` uses an internal boolean bitmask to represent nulls while preserving pure integer representations.

---

### Reconciliation, Incremental Watermarks & Idempotency (Q31 - Q40)

#### Q31: What is Source-to-Target Reconciliation, and what mathematical equations govern it?
**Answer:** The automated audit process that mathematically balances record counts across all processing stages to verify zero data loss:
$$\text{Source Count} = \text{Valid Count} + \text{Quarantined Count}$$
$$\text{Curated Count} = \text{Valid Count} - \text{Duplicates Removed}$$

#### Q32: What does a non-zero source variance indicate during pipeline reconciliation?
**Answer:** Data leakage or phantom insertion. If `Source - (Valid + Quarantined) > 0`, records were lost inside the validation engine without being quarantined. If negative, rows were counted multiple times.

#### Q33: What is the High-Watermark pattern in incremental data pipelines?
**Answer:** Persisting the maximum timestamp ($\max(\text{updated\_at})$) of successfully processed records. On the subsequent run, the pipeline extracts only records where $\text{updated\_at} > \text{high\_watermark}$, keeping processing volume and run times constant regardless of total historical data size.

#### Q34: What is Late-Arriving Data, and how do you prevent losing it in a watermark pipeline?
**Answer:** Data generated in the past that arrives at the pipeline after the watermark has already advanced (e.g. mobile devices syncing after offline mode). It is handled using a **Sliding Lookback Window** ($\text{query\_watermark} = \text{current\_watermark} - \text{buffer}$), followed by primary key deduplication to absorb duplicate records.

#### Q35: When should the high-watermark state be committed to persistent storage?
**Answer:** Strictly at the very end of the pipeline execution, **only after** all records have landed in curated storage, reconciliation has passed (`status == 'PASS'`), and the audit manifest has been written. Committing before success causes uncommitted delta records to be skipped on rerun.

#### Q36: Define Idempotency in data engineering and provide two real-world implementations.
**Answer:** An operation is idempotent if executing it multiple times produces the exact same system state as executing it once ($f(f(x)) = f(x)$).
- **Implementation 1 (File Storage)**: Atomic partition overwrite (`df.to_parquet(target_partition, mode='overwrite')`).
- **Implementation 2 (SQL Table)**: Primary key upsert (`MERGE INTO target USING source ON target.id = source.id ...`).

#### Q37: What is an Audit Manifest, and what metadata must it contain?
**Answer:** A machine-readable JSON snapshot generated for every execution run recording:
- `run_id`, `batch_id`, UTC start and end timestamps, and duration.
- Execution status (`PASS`/`FAIL`) and error messages if any.
- Sources ingested (names, formats, paths, row counts).
- Exact mathematical counts breakdown (source, quarantined, valid, duplicates, curated).
- Output file paths and report locations.

#### Q38: What is an Execution Ledger, and how does it differ from a Run Manifest?
**Answer:** While a Run Manifest is a detailed snapshot of a single execution, an Execution Ledger (`execution_ledger.jsonl`) is an append-only line-delimited JSON stream capturing a one-line summary of every past run. It provides a longitudinal audit trail for monitoring trends in duration, record volume, and failure rates over time.

#### Q39: What is Data Lineage, and why is it legally mandated in banking and healthcare?
**Answer:** Data Lineage is the complete provenance map detailing every source, transformation, filter, and join that contributed to a specific data point. Regulations like BCBS 239 (banking) and HIPAA (healthcare) legally mandate that financial institutions prove the mathematical accuracy and origin of risk figures.

#### Q40: How do you verify idempotency in automated test suites?
**Answer:** Run the pipeline once with a fixed input dataset and record output counts and hashes. Immediately run the pipeline a second time with the exact same input. Assert that the second run yields identical output counts, identical reconciliation status, and introduces zero duplicate rows into the target database.

---

### PySpark, Orchestration & Docker (Q41 - Q50)

#### Q41: What is a Directed Acyclic Graph (DAG) in workflow orchestration?
**Answer:** A finite directed graph with no directed cycles. In orchestration (Airflow, Dagster), vertices represent discrete computational tasks, and edges represent execution dependencies ($A \rightarrow B$). Acyclicity guarantees that workflows never enter infinite execution loops.

#### Q42: What is Lazy Evaluation in Apache Spark, and why is it beneficial?
**Answer:** Transformations (`select`, `filter`, `join`) are not executed when called; Spark records them into a logical plan. Execution occurs only when an action (`count`, `write`) is called. This enables the **Catalyst Optimizer** to inspect the entire DAG, push down filters, eliminate unused columns, and optimize join strategies before executing any physical computation.

#### Q43: What is the Catalyst Optimizer in Apache Spark?
**Answer:** Spark SQL's query optimization engine. It transforms user code through 4 phases:
1. Analysis (resolving column names and types).
2. Logical Optimization (predicate pushdown, projection pruning, constant folding).
3. Physical Planning (selecting between broadcast hash join vs sort-merge join).
4. Code Generation (compiling query fragments into optimized Java bytecode via Tungsten).

#### Q44: What is Data Shuffling in Spark, and why is it considered the primary performance bottleneck?
**Answer:** Shuffling is the redistribution of data across cluster worker nodes (e.g. during wide transformations like `groupByKey`, `distinct`, or wide `join`). It requires serializing data to disk, transmitting over network cables, and deserializing on receiving nodes. Minimizing shuffles (e.g. using Broadcast Joins) is the primary goal of Spark optimization.

#### Q45: Why should Docker containers for data pipelines use Multi-Stage builds?
**Answer:** Multi-stage builds compile dependencies and wheels in a temporary "builder" stage, then copy only the compiled artifacts into a lean "runtime" container. This strips out compilers, build tools, and temporary caches, reducing container image size by up to 80% and shrinking the attack surface.

#### Q46: Why should a production data pipeline container never run as the `root` user?
**Answer:** If an attacker exploits a vulnerability in a third-party Python package or framework running as `root` (UID 0), they can break out of container isolation and gain superuser control over the host operating system. Creating an unprivileged `appuser` limits the potential blast radius.

#### Q47: What is the difference between Docker Volumes and Host Bind Mounts?
**Answer:**
- **Named Volumes**: Managed entirely by Docker inside `/var/lib/docker/volumes/`. High performance, best for persistent databases.
- **Host Bind Mounts**: Direct mapping of a specific host folder into the container (`-v $(pwd)/data:/app/data`). Best for data pipelines where input datasets and output reports must be directly accessible to developers and host scripts.

#### Q48: How do 12-Factor App principles apply to data pipelines?
**Answer:**
- Store configuration (database URLs, storage paths, API endpoints) in environment variables.
- Treat backing services (databases, object stores) as attached resources.
- Strict separation of build, release, and run phases.
- Stateless batch execution processes that persist state externally.
- Structured logging as event streams to `stdout`.

#### Q49: What is the difference between unit testing, integration testing, and reconciliation testing in data pipelines?
**Answer:**
- **Unit Testing**: Tests pure transformation functions (standardization, date parsing, string trimming) in isolation with zero I/O.
- **Integration Testing**: Tests component interaction with real or mocked external systems (reading CSVs, querying databases, calling APIs).
- **Reconciliation Testing**: End-to-end mathematical verification asserting that $100\%$ of source records are accounted for across all output layers with zero variance.

#### Q50: How do you design a data pipeline to be cloud-agnostic?
**Answer:**
- Abstract storage paths behind standard URI schemes (`s3://`, `gs://`, `file://`) using tools like PyArrow, fsspec, or Apache Iceberg.
- Decouple compute from storage.
- Package the pipeline in standardized Docker containers configured entirely via environment variables.
- Avoid proprietary cloud-vendor database dialects in core transformation logic.
