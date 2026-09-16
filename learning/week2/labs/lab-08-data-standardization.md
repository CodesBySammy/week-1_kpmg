# Lab 08: Data Standardization & Timestamp Normalization

## Objective
Standardize unformatted raw inputs into clean types, uppercase enums, and ISO-8601 UTC datetimes.

---

## Exercise

1. Execute `standardize_case_records`:
```python
import pandas as pd
from pipeline.transformations.standardization import standardize_case_records

raw_data = pd.DataFrame([
    {
        "case_id": "42",
        "title": "  Slow API latency  ",
        "description": None,
        "status": "in_progress",
        "priority": "high",
        "case_type": "bug",
        "created_by": "3",
        "assigned_to": None,
        "created_at": "2026-03-01 08:30:00",
        "updated_at": "2026-03-01 09:15:00",
        "resolved_at": None,
    }
])

cleaned = standardize_case_records(raw_data)
print("Title trimmed:", repr(cleaned.loc[0, "title"]))
print("Description imputed:", repr(cleaned.loc[0, "description"]))
print("Status uppercase:", repr(cleaned.loc[0, "status"]))
print("Assigned to dtype:", cleaned["assigned_to"].dtype)
print("Created_at timezone:", cleaned.loc[0, "created_at"].tzinfo)
```

---

## Verification
- Notice that `assigned_to` uses nullable integer `Int64`, preserving `<NA>` without forcing the column to float.
- Notice `created_at` has `tzinfo=datetime.timezone.utc`.
