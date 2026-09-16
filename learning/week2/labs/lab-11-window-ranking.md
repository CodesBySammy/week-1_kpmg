# Lab 11: Window Functions and Analytical Rankings

## Objective
Apply partitioned window functions over case records to generate dense duration rankings and department sequence numbers.

---

## Exercise

1. Execute `apply_window_metrics`:
```python
import pandas as pd
from pipeline.transformations.windowing import apply_window_metrics

df = pd.DataFrame([
    {"case_id": 1, "priority": "CRITICAL", "assignee_department": "Engineering", "resolution_time_hours": 12.0},
    {"case_id": 2, "priority": "CRITICAL", "assignee_department": "Engineering", "resolution_time_hours": 3.5},
    {"case_id": 3, "priority": "CRITICAL", "assignee_department": "Cybersecurity", "resolution_time_hours": 1.2},
    {"case_id": 4, "priority": "LOW", "assignee_department": "Engineering", "resolution_time_hours": 48.0},
])

windowed = apply_window_metrics(df)

print(windowed[["case_id", "priority", "assignee_department", "resolution_time_hours", "priority_duration_rank", "department_case_seq"]])
```

---

## Verification
- Notice that Case #3 has `priority_duration_rank = 1` among CRITICAL priority cases.
- Notice `department_case_seq` increments within Engineering (1, 2, 3) and resets for Cybersecurity (1).
