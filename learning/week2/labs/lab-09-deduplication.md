# Lab 09: Primary Key Deduplication Preserving Latest Timestamp

## Objective
Implement deterministic deduplication that keeps the freshest record when duplicate natural keys arrive.

---

## Exercise

1. Execute `deduplicate_cases`:
```python
import pandas as pd
from pipeline.transformations.deduplication import deduplicate_cases

df = pd.DataFrame([
    {"case_id": 1, "title": "Old status", "status": "OPEN", "updated_at": "2026-03-01T10:00:00Z"},
    {"case_id": 1, "title": "New status", "status": "RESOLVED", "updated_at": "2026-03-01T14:00:00Z"},
    {"case_id": 2, "title": "Unique case", "status": "OPEN", "updated_at": "2026-03-01T11:00:00Z"},
])

deduped_df, duplicates_removed = deduplicate_cases(df, primary_key="case_id", order_by_col="updated_at")

print(f"Duplicates removed: {duplicates_removed}")
print(f"Remaining records: {len(deduped_df)}")
case1 = deduped_df[deduped_df["case_id"] == 1].iloc[0]
print(f"Case 1 Title: {case1['title']}, Status: {case1['status']}")
```

---

## Verification
- Confirm that exactly 1 duplicate was removed.
- Confirm Case 1 kept the `"New status"` record with status `"RESOLVED"`.
