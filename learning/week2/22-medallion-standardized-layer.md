# Medallion Architecture: The Standardized (Silver) Layer

The **Standardized Layer** (also termed the **Silver Layer** or **Cleaned Layer**) is the bridge between raw bronze storage and consumable gold marts. Its mission is to transform messy, unvalidated data into a clean, queryable, typed dataset where all domain rules are satisfied and defects have been diverted to quarantine.

---

## 1. Principles of the Standardized Layer

1. **Schema Enforcement**: All columns match declared types (`Int64`, `string`, `datetime64[ns, UTC]`).
2. **Quality Isolation**: Only records that passed all critical data quality rules are present. All non-compliant records have been sent to the quarantine dead-letter store.
3. **Canonical Enums**: Categorical fields (`status`, `priority`, `case_type`) are trimmed and uppercased to prevent fragmented groupings in SQL queries.
4. **Cleaned Text**: Whitespace is trimmed, and null descriptions are imputed with default strings.

---

## 2. Directory Layout & Persistence

```
data/standardized/
└── cases/
    └── std_cases.parquet
```

Silver tables are persisted as compressed columnar Parquet files. Because schema enforcement and type coercion have already occurred, queries against the Silver layer are fast, reliable, and type-safe.

---

## 3. Production Implementation in `StandardizedLayerManager`

In `pipeline/layers/standardized.py`, our `StandardizedLayerManager` handles saving and loading Silver datasets:

```python
from pathlib import Path
import pandas as pd

class StandardizedLayerManager:
    """Manages the Standardized (Silver) Cleansed Tier."""

    def __init__(self, standardized_dir: Path):
        self.standardized_dir = Path(standardized_dir)
        self.standardized_dir.mkdir(parents=True, exist_ok=True)

    def save_standardized(self, df: pd.DataFrame, dataset_name: str) -> Path:
        out_dir = self.standardized_dir / dataset_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"std_{dataset_name}.parquet"
        df.to_parquet(out_file, engine="pyarrow", compression="snappy", index=False)
        return out_file

    def load_standardized(self, dataset_name: str) -> pd.DataFrame:
        target_file = self.standardized_dir / dataset_name / f"std_{dataset_name}.parquet"
        if not target_file.exists():
            return pd.DataFrame()
        return pd.read_parquet(target_file)
```

The Silver layer serves as the single source of truth from which multiple downstream Gold marts (e.g. Executive Dashboards, Audit Logs, ML Feature Stores) can be built.
