# Lab 17: Inspecting Medallion Storage: Bronze, Silver, and Gold Parquet

## Objective
Trace a case record as it moves from Raw Bronze landing, through Standardized Silver, to Curated Gold Parquet and SQL tables.

---

## Exercise

1. Inspect the 3 tiers using pandas:
```python
import pandas as pd
from pathlib import Path

# 1. Bronze Raw Landing
raw_files = list(Path("data/raw/cases").glob("**/*.parquet"))
if raw_files:
    raw_df = pd.read_parquet(raw_files[0])
    print("=== Bronze Raw Layer ===")
    print(f"File: {raw_files[0]}")
    print(f"Columns: {list(raw_df.columns)}")
    print(raw_df[["case_id", "_ingested_at", "_run_id"]].head(2))

# 2. Silver Standardized Layer
std_file = Path("data/standardized/cases/std_cases.parquet")
if std_file.exists():
    std_df = pd.read_parquet(std_file)
    print("\n=== Silver Standardized Layer ===")
    print(f"Columns: {list(std_df.columns)}")
    print(std_df[["case_id", "title", "status", "priority"]].head(2))

# 3. Gold Curated Layer
curated_file = Path("data/curated/cases/curated_cases.parquet")
if curated_file.exists():
    curated_df = pd.read_parquet(curated_file)
    print("\n=== Gold Curated Layer ===")
    print(f"Columns: {list(curated_df.columns)}")
    print(curated_df[["case_id", "assignee_department", "resolution_time_hours", "sla_breached"]].head(2))
```

---

## Verification
- Notice the progressive enrichment from raw string values to standardized enums to business metrics (`sla_breached`).
