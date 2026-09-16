# Lab 12: Pre-Aggregated Summary Rollups & SLA Compliance Metrics

## Objective
Compute executive department summary tables with total volume, SLA breaches, average resolution time, and compliance percentages.

---

## Exercise

1. Execute `aggregate_department_sla_summary`:
```python
import pandas as pd
from pipeline.transformations.aggregation import aggregate_department_sla_summary

curated_df = pd.DataFrame([
    {"case_id": 1, "assignee_department": "Engineering", "sla_breached": False, "resolution_time_hours": 4.0},
    {"case_id": 2, "assignee_department": "Engineering", "sla_breached": True, "resolution_time_hours": 24.0},
    {"case_id": 3, "assignee_department": "Engineering", "sla_breached": False, "resolution_time_hours": 6.0},
    {"case_id": 4, "assignee_department": "Cybersecurity", "sla_breached": False, "resolution_time_hours": 1.5},
])

summary = aggregate_department_sla_summary(curated_df)
print(summary.to_string(index=False))
```

---

## Verification
- Notice Engineering has 3 cases, 1 breach, and `sla_compliance_pct = 66.67%`.
- Notice Cybersecurity has 1 case, 0 breaches, and `sla_compliance_pct = 100.0%`.
