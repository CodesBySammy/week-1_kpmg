# Lab 10: Relational Joins, Reference Enrichment, and SLA Breach Calculation

## Objective
Join case records with reference users, department lookups, and regulatory policy metadata to compute resolution times and SLA breaches.

---

## Exercise

1. Execute `join_case_reference_and_policies`:
```python
import pandas as pd
from pipeline.transformations.joins import join_case_reference_and_policies

cases = pd.DataFrame([
    {
        "case_id": 101,
        "priority": "HIGH",
        "case_type": "SECURITY",
        "assigned_to": 1,
        "created_at": pd.to_datetime("2026-03-01T08:00:00Z"),
        "resolved_at": pd.to_datetime("2026-03-01T15:00:00Z"),  # 7.0 hours
    }
])

users = pd.DataFrame([
    {"user_id": 1, "department_id": 2, "tier": "L3", "region": "APAC"}
])

depts = pd.DataFrame([
    {"department_id": 2, "department_name": "Cybersecurity"}
])

policies = pd.DataFrame([
    {
        "policy_id": "POL-CYBER-01",
        "case_type": "SECURITY",
        "priority": "HIGH",
        "sla_target_hours": 4.0,  # SLA is 4.0 hours!
        "compliance_framework": "ISO27001",
    }
])

enriched = join_case_reference_and_policies(cases, users, depts, policies)

row = enriched.iloc[0]
print("Assignee Dept:", row["assignee_department"])
print("Resolution Hours:", row["resolution_time_hours"])
print("SLA Target Hours:", row["sla_target_hours"])
print("SLA Breached?:", row["sla_breached"])
```

---

## Verification
- Confirm that `resolution_time_hours` is 7.0 and `sla_breached` is `True` because 7.0 > 4.0.
