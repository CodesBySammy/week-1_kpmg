# Implementing a Production 5-Pillar Data Profiler in Python

In this module, we inspect how the 5 pillars of data profiling are implemented using vectorized pandas operations in `pipeline/profiling/profiler.py`.

---

## 1. Vectorized Vector Profiling vs Row Loops

When profiling millions of rows, iterating with `for row in df.iterrows():` is up to **100x slower** than vectorized operations. Vectorized operations execute in compiled C/C++ backends.

### Computing Completeness & Uniqueness Vectorially:
```python
def profile_column_basics(series: pd.Series, total_rows: int) -> dict:
    null_count = int(series.isna().sum())
    # Count empty strings as missing if string column
    if series.dtype == "object":
        null_count += int((series.astype(str).str.strip() == "").sum())

    non_null_series = series.dropna()
    distinct_count = int(non_null_series.nunique())

    return {
        "null_count": null_count,
        "completeness_pct": round(((total_rows - null_count) / total_rows) * 100.0, 2),
        "distinct_count": distinct_count,
        "uniqueness_pct": round((distinct_count / total_rows) * 100.0, 2),
    }
```

### Computing Statistical Distribution:
```python
def profile_numeric_distribution(series: pd.Series) -> dict:
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        return {}

    return {
        "min": float(numeric_series.min()),
        "max": float(numeric_series.max()),
        "mean": round(float(numeric_series.mean()), 2),
        "median": round(float(numeric_series.median()), 2),
        "p25": round(float(numeric_series.quantile(0.25)), 2),
        "p75": round(float(numeric_series.quantile(0.75)), 2),
    }
```

---

## 2. Our Production `DataProfiler` Architecture

In `pipeline/profiling/profiler.py`, the `DataProfiler` class synthesizes all 5 pillars into a structured report:

```python
class DataProfiler:
    def __init__(self, dataset_name: str = "dataset"):
        self.dataset_name = dataset_name

    def profile(
        self,
        df: pd.DataFrame,
        primary_keys: Optional[List[str]] = None,
        enum_validations: Optional[Dict[str, List[Any]]] = None,
        foreign_keys: Optional[Dict[str, Set[Any]]] = None,
    ) -> Dict[str, Any]:
        total_rows = len(df)
        total_columns = len(df.columns)

        # 1. Completeness & Uniqueness
        completeness = self._profile_completeness(df, total_rows)
        uniqueness = self._profile_uniqueness(df, primary_keys or [])

        # 2. Validity
        validity = self._profile_validity(df, enum_validations or {})

        # 3. Distribution
        distributions = self._profile_distributions(df)

        # 4. Referential Integrity
        referential = self._profile_referential_integrity(df, foreign_keys or {})

        return {
            "dataset_name": self.dataset_name,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "completeness": completeness,
            "uniqueness": uniqueness,
            "validity": validity,
            "distributions": distributions,
            "referential_integrity": referential,
        }
```

---

## 3. Automated Markdown & JSON Reporting

In enterprise environments, profiling metrics must be published in two formats:
1. **JSON (`reports/profiling/profiling_<run_id>.json`)**: Ingested by automated monitoring agents, Prometheus exporters, and metadata catalogs (DataHub, Amundsen).
2. **Markdown (`reports/profiling/profiling_<run_id>.md`)**: Human-readable tables rendered on GitHub PRs, Jenkins build logs, or email digests.

Our profiler automatically renders clean GitHub Flavored Markdown:
```markdown
| Column Name | Null Count | Completeness % | Status |
|---|:---:|:---:|:---:|
| `case_id` | 0 | 100.0% | 🟢 OK |
| `title` | 1 | 95.0% | 🟡 Review |
| `description` | 2 | 90.0% | 🟡 Review |
```
