# Analytical Aggregations: Rollups, SLAs, and Compliance Reporting

While row-level curated tables (`curated_cases.parquet`) provide granular data for deep-dive investigation, executives, managers, and operational dashboards require **pre-aggregated summary rollups**.

---

## 1. Why Compute Aggregations in the Pipeline?

If a BI dashboard (PowerBI, Tableau, Looker) queries a raw 50-million-row table to calculate the daily SLA compliance rate across 10 departments, it forces the database to scan millions of rows on every dashboard refresh.

By computing **Curated Summary Rollups** inside the pipeline:
1. **Instantaneous Dashboard Response**: Dashboard queries scan a 10-row summary table rather than millions of rows.
2. **Unified Business Definitions**: The formula for `sla_compliance_pct` is codified once in version-controlled data pipeline code, preventing discrepancies where different analysts write slightly different SQL queries.

---

## 2. Department SLA Compliance Summary

In `pipeline/transformations/aggregation.py`, `aggregate_department_sla_summary` computes key performance indicators (KPIs) per department:

```python
def aggregate_department_sla_summary(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame()

    dept_col = "assignee_department" if "assignee_department" in df.columns else "department"

    summary = (
        df.groupby(dept_col)
        .agg(
            total_cases=("case_id", "count"),
            sla_breaches=("sla_breached", lambda s: int(s.sum()) if "sla_breached" in df.columns else 0),
            avg_resolution_hours=(
                "resolution_time_hours",
                lambda s: round(float(s.mean()), 2) if "resolution_time_hours" in df.columns else 0.0,
            ),
        )
        .reset_index()
    )

    # Calculate SLA Compliance Percentage
    summary["sla_compliance_pct"] = round(
        ((summary["total_cases"] - summary["sla_breaches"]) / summary["total_cases"]) * 100.0,
        2,
    )
    return summary
```

### Resulting Operational Mart:
| Assignee Department | Total Cases | SLA Breaches | Avg Resolution (Hrs) | SLA Compliance % |
|---|:---:|:---:|:---:|:---:|
| **Cybersecurity** | 6 | 0 | 3.25 | **100.0%** |
| **Engineering** | 5 | 1 | 9.40 | **80.0%** |
| **Customer Support** | 3 | 0 | 1.80 | **100.0%** |

---

## 3. Priority Summary Aggregations

Similarly, `aggregate_priority_summary` breaks down workload and resolution speed by case urgency (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), exposing bottlenecks where high-severity tickets take disproportionately long to resolve.
