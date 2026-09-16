# Lab 15: Isolating Rejected Records in the Quarantine Dead-Letter Sink

## Objective
Persist rejected records to the quarantine storage directory and verify payload JSON structure.

---

## Exercise

1. Execute `QuarantineManager`:
```python
from pathlib import Path
import json
from pipeline.quarantine.quarantine_manager import QuarantineManager

manager = QuarantineManager(quarantine_dir=Path("data/rejected"))

rejected_payloads = [
    {
        "original_record": {"case_id": "99", "status": "UNKNOWN"},
        "source": "cases.csv",
        "run_id": "LAB_15",
        "rule_id": "RULE-CASE-002",
        "rule_description": "Valid status enum",
        "reason": "Status 'UNKNOWN' not allowed",
        "severity": "CRITICAL",
        "rejected_at": "2026-09-16T12:00:00Z"
    }
]

out_file = manager.quarantine_records(
    rejected_records=rejected_payloads,
    run_id="LAB_15",
    batch_id="BATCH_LAB_15",
)

print(f"Quarantined payload saved to: {out_file}")

with open(out_file, "r", encoding="utf-8") as f:
    saved_data = json.load(f)
print("Total Quarantined:", saved_data["total_quarantined"])
```

---

## Verification
- Inspect the generated JSON file at `data/rejected/rejected_LAB_15.json` and verify all failure context is captured.
