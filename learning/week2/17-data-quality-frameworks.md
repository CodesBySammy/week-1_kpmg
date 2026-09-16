# Data Quality Frameworks: Great Expectations, Soda, Deequ, and Custom Engines

In software engineering, you write unit tests for your code (`pytest`). In data engineering, you must write tests for your **data**.

Data pipelines process dynamic, constantly changing data produced by humans and third-party systems. Code tests pass 100% of the time, yet a pipeline can still corrupt business metrics if the underlying data quality is violated.

---

## 1. Major Industry Data Quality Frameworks

| Framework | Ecosystem | Key Features | Best Used For |
|---|---|---|---|
| **Great Expectations (GX)** | Python / SQL / Spark | Declarative "Expectations" JSON/YAML, automated HTML documentation suites | Comprehensive enterprise data testing & team collaboration |
| **Soda Core** | Python / CLI / Cloud | Human-readable SodaCL YAML checks, SQL integration | Lightweight CLI data verification in CI/CD |
| **AWS Deequ** | Scala / Apache Spark | Unit tests for data on distributed Spark clusters | Big Data pipelines at petabyte scale |
| **Custom Rule Engines** | Python / Pydantic | Embedded directly into pipeline DAGs, ultra-low latency, tailored quarantine sinks | Micro-batch pipelines requiring custom isolation logic |

---

## 2. Declarative Assertions: The Great Expectations Model

In Great Expectations, assertions are phrased as human-readable declarative "expectations":
```python
# Expect column values to never be null
validator.expect_column_values_to_not_be_null(column="case_id")

# Expect column values to match allowed enum set
validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
)

# Expect referential foreign key integrity
validator.expect_column_values_to_be_in_set(
    column="created_by",
    value_set=valid_user_ids,
)
```

---

## 3. Severity Levels & Failure Behaviors

A mature data quality framework categorizes violations by severity:

```mermaid
graph TD
    RuleEval{"Quality Rule Evaluation"}
    RuleEval -->|Pass| Clean["Proceed to Standardized Layer"]
    RuleEval -->|Warning Rule Failed| LogWarn["Log Warning & Allow Record to Pass"]
    RuleEval -->|Critical Rule Failed| Quarantine["Divert to Quarantine Dead-Letter Sink"]
    RuleEval -->|Fatal Anomaly (> 10% Failed)| Halt["Halt Pipeline Immediately (Fail-Stop)"]
```

1. **`WARNING` (Warn and Pass)**:
   - Example: Missing non-essential description or uncommon user agent.
   - Action: Log warning, allow record to proceed through transformations.
2. **`CRITICAL` (Quarantine)**:
   - Example: Null title, unparseable timestamp, or invalid status enum.
   - Action: Do not let record into curated storage; divert to quarantine sink with error payload metadata.
3. **`FATAL` (Halt Pipeline)**:
   - Example: More than 10% of total records failed validation (indicating an upstream schema breakage or corrupted file).
   - Action: Abort pipeline execution immediately to prevent poisoning downstream data marts.
