# Week 2 Enterprise Data Engineering Self-Assessment

Test your understanding of enterprise data pipelines, schemas, profiling, medallion architecture, reconciliation, idempotency, and containerization.

---

## Part 1: Multiple Choice Questions (20 Questions)

### Q1. Which file format provides columnar storage, predicate pushdown, and dictionary encoding?
- A) CSV
- B) JSON Lines
- C) Apache Parquet
- D) XML

### Q2. In the Medallion Architecture, what is the primary purpose of the Bronze (Raw) layer?
- A) To hold aggregated business metrics for executive dashboards
- B) To store an immutable, unadulterated copy of source data with ingestion metadata
- C) To filter out bad records before landing
- D) To maintain third normal form relational tables

### Q3. What is the fundamental mathematical equation for Stage 1 Source-to-Target Reconciliation?
- A) $\text{Source Count} = \text{Curated Count} - \text{Quarantined Count}$
- B) $\text{Source Count} = \text{Valid Count} + \text{Quarantined Count}$
- C) $\text{Curated Count} = \text{Source Count} \times 2$
- D) $\text{Source Count} = \text{Duplicates Removed} + \text{Valid Count}$

### Q4. Why is reading large CSV files with `dtype=str` recommended for raw ingestion?
- A) Strings consume less memory than numeric types
- B) It prevents premature type coercion from silently masking or discarding defective data
- C) CSV files cannot store numbers
- D) It speeds up PyArrow compression

### Q5. What is the key advantage of JSON Lines (NDJSON) over standard JSON for large data pipelines?
- A) JSON Lines supports binary encryption natively
- B) JSON Lines can be streamed line-by-line in $O(1)$ constant memory
- C) JSON Lines is smaller than Parquet
- D) Standard JSON cannot store nested dictionaries

### Q6. Which pandas data type represents nullable integers without forcing the column to `float64`?
- A) `int32`
- B) `int64`
- C) `Int64` (Capital 'I')
- D) `numpy.int_`

### Q7. If an upstream producer adds a new optional column to an API response, which schema evolution guarantee ensures old consumers do not crash?
- A) Backward Compatibility
- B) Forward Compatibility
- C) Full Compatibility
- D) Strict Locking

### Q8. What happens during a Broadcast Hash Join in distributed data systems?
- A) Both large tables are shuffled across all network nodes
- B) The small dimension table is copied to all worker nodes, eliminating fact table network shuffle
- C) The database locks both tables during execution
- D) All records are converted into JSON strings

### Q9. What does `DENSE_RANK()` produce for values `[10, 10, 25]`?
- A) `1, 1, 3`
- B) `1, 2, 3`
- C) `1, 1, 2`
- D) `0, 0, 1`

### Q10. What is a Quarantine Dead-Letter Sink?
- A) A trash bin where bad records are permanently deleted
- B) A dedicated storage location where non-compliant records are diverted with failure metadata without halting the pipeline
- C) A firewall that blocks external IP addresses
- D) A temporary cache for database connection pools

### Q11. When should a data pipeline trigger a Circuit Breaker (Fail-Stop)?
- A) When a single row has an invalid status enum
- B) When the quarantine failure rate exceeds an unacceptable threshold (e.g. > 10%)
- C) When any warning rule is triggered
- D) When a user updates a ticket description

### Q12. In the High-Watermark incremental processing pattern, when should the watermark be committed?
- A) At the start of the pipeline run before reading data
- B) Immediately after reading the source files
- C) Strictly after curated data has landed, reconciliation has passed, and the manifest is written
- D) Watermarks do not need to be persisted

### Q13. An operation is defined as Idempotent if:
- A) It runs in under 1 second
- B) Executing it multiple times produces the exact same system state as executing it once
- C) It never encounters a network error
- D) It uses multi-threading

### Q14. What does a positive source variance (`Source - (Valid + Quarantined) > 0`) signify?
- A) Phantom data insertion
- B) Data leakage (records lost inside the processing engine)
- C) 100% data completeness
- D) Schema evolution success

### Q15. Why should pipeline timestamps always be stored in UTC?
- A) UTC timestamps require fewer bytes
- B) Local timezones create ambiguity across Daylight Saving Time changes and multi-region users
- C) SQLite cannot store timezones
- D) UTC is required by the Python interpreter

### Q16. What is the role of the Catalyst Optimizer in Apache Spark?
- A) To manage JVM garbage collection
- B) To analyze, optimize, and generate efficient physical execution plans for DataFrame queries
- C) To serialize Python objects to disk
- D) To host the web UI dashboard

### Q17. In a multi-stage Docker build, why are build tools compiled in an initial builder stage?
- A) To make the build run faster on the first try
- B) To strip compilers and temporary build artifacts out of the final runtime image, minimizing size and vulnerabilities
- C) To bypass Docker layer caching
- D) Because Python requires GCC in production

### Q18. Why should a production Docker container avoid running as the `root` user?
- A) Root users cannot execute Python scripts
- B) To prevent an attacker who compromises the container process from gaining root access to the host kernel
- C) To avoid paying Docker enterprise licensing fees
- D) Because Linux disallows writing to `/app` as root

### Q19. What is the difference between an Audit Manifest and an Execution Ledger?
- A) The manifest is for databases, the ledger is for files
- B) The manifest is a single-run snapshot; the ledger is an append-only historic log of all runs
- C) There is no difference
- D) The ledger only records errors

### Q20. In our Case Management pipeline, what ensures duplicate cases are resolved deterministically?
- A) Sorting by `case_id` and `updated_at` ascending and keeping the `last` record
- B) Randomly picking one record
- C) Keeping the record with the shortest title
- D) Dropping all records that share a `case_id`

---

## Part 2: System Design & Scenario Questions (10 Questions)

- **Q21**: An upstream service accidentally starts sending user IDs as strings prefixed with `"USR-"` (e.g. `"USR-101"`). Describe how our pipeline's contract and quarantine engine handles this.
- **Q22**: How would you design a pipeline to handle late-arriving data from offline mobile devices?
- **Q23**: Explain why `LEFT JOIN` without deduplicated dimension keys causes reconciliation failures.
- **Q24**: Why is storing raw data as immutable files in Bronze safer than transforming data in-place?
- **Q25**: How does projection pruning in Parquet reduce cloud computing costs?
- **Q26**: If the pipeline crashes while writing to the Curated tier, how does idempotency prevent data corruption on rerun?
- **Q27**: Explain the difference between eager actions and lazy transformations in PySpark.
- **Q28**: What 4 metrics would you place on a PagerDuty alert dashboard for pipeline health?
- **Q29**: Why do we use host bind mounts (`-v $(pwd)/data:/app/data`) when executing our containerized pipeline?
- **Q30**: Walk through the 6 steps you would take to debug a reconciliation status `FAIL`.
