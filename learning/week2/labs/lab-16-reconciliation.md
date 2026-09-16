# Lab 16: Source-to-Target Mathematical Reconciliation & Variance Alerts

## Objective
Balance record counts across ingestion, quarantine, validation, deduplication, and curated tiers to verify zero data loss.

---

## Exercise

1. Execute `ReconciliationEngine`:
```python
from pathlib import Path
from pipeline.reconciliation.reconciler import ReconciliationEngine

engine = ReconciliationEngine(reports_dir=Path("reports/reconciliation"))

# Balanced Run
report_pass = engine.reconcile(
    run_id="LAB_16_PASS",
    source_name="cases.csv",
    source_count=100,
    quarantined_count=10,
    valid_count=90,
    duplicates_removed=5,
    curated_count=85,
)
print("Balanced run status:", report_pass["overall_status"])

# Unbalanced Run (10 records leaked!)
report_fail = engine.reconcile(
    run_id="LAB_16_FAIL",
    source_name="cases.csv",
    source_count=100,
    quarantined_count=10,
    valid_count=80,  # 10 records missing!
    duplicates_removed=5,
    curated_count=75,
)
print("Unbalanced run status:", report_fail["overall_status"])
print("Source variance:", report_fail["variance"]["source_variance"])

# Generate Reports
json_path, md_path = engine.save_reports(report_pass, run_id="LAB_16_PASS")
print(f"Generated Markdown reconciliation report at: {md_path}")
```

---

## Verification
- Confirm that `report_pass` yields `overall_status == "PASS"`.
- Confirm that `report_fail` yields `overall_status == "FAIL"` and `source_variance == 10`.
