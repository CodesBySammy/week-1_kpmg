# Lab 18: Incremental Delta Ingestion & Watermark State Management

## Objective
Execute delta filtering using `WatermarkTracker` and observe high-watermark state updates.

---

## Exercise

1. Execute watermark tracking:
```python
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from pipeline.orchestration.incremental import WatermarkTracker

tracker = WatermarkTracker(watermark_path=Path("audit/test_watermark.json"))

# 1. First run: No prior watermark exists (processes all)
df = pd.DataFrame([
    {"case_id": 1, "title": "Case 1", "updated_at": "2026-03-01T10:00:00Z"},
    {"case_id": 2, "title": "Case 2", "updated_at": "2026-03-01T12:00:00Z"},
])

delta_df, new_max = tracker.filter_incremental_records(df)
print(f"Initial run processed: {len(delta_df)} records. New max: {new_max}")
tracker.update_watermark(new_max, batch_id="BATCH_1")

# 2. Second run: New batch arrives with 1 old and 1 new record
new_batch = pd.DataFrame([
    {"case_id": 2, "title": "Case 2 unchanged", "updated_at": "2026-03-01T12:00:00Z"},
    {"case_id": 3, "title": "Case 3 NEW", "updated_at": "2026-03-01T15:00:00Z"},
])

delta_df2, new_max2 = tracker.filter_incremental_records(new_batch)
print(f"Incremental run processed: {len(delta_df2)} records (Only Case 3!)")
print(delta_df2[["case_id", "title", "updated_at"]])
```

---

## Verification
- Notice how Case #2 was filtered out because its timestamp did not exceed the committed watermark.
