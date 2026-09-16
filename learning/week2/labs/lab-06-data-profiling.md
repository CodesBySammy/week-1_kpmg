# Lab 06: Executing the 5-Pillar Statistical Data Profiler

## Objective
Run statistical profiling across completeness, uniqueness, validity, distributions, and referential integrity on raw cases.

---

## Exercise

1. Execute the `DataProfiler` on `cases.csv`:
```python
from pathlib import Path
import pandas as pd
from pipeline.profiling.profiler import DataProfiler

raw_cases = pd.read_csv("data/input/cases.csv", dtype=str)

profiler = DataProfiler(dataset_name="cases")
report = profiler.profile(
    df=raw_cases,
    primary_keys=["case_id"],
    enum_validations={
        "status": ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
        "priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    },
    foreign_keys={
        "created_by": {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    },
)

# Inspect statistical summary
print("Total rows:", report["total_rows"])
print("Uniqueness:", report["uniqueness"])
print("Validity breaches:", report["validity"]["invalid_counts"])
print("Referential orphans:", report["referential_integrity"]["orphan_counts"])

# Save reports
json_path, md_path = profiler.save_reports(report, output_dir=Path("reports/profiling"), run_id="LAB_06")
print(f"Generated Markdown report at: {md_path}")
```

2. Open `reports/profiling/profiling_LAB_06.md` and review the formatted tables.
