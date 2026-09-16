# Medallion Architecture: The Raw (Bronze) Layer

The **Raw Layer** (also termed the **Bronze Layer** or **Landing Zone**) is the initial ingestion tier of an enterprise data platform. Its mission is to store an exact, immutable copy of incoming raw data with lineage metadata.

---

## 1. Principles of the Raw Layer

1. **Append-Only & Immutable**: Never update, edit, or delete records in the Raw layer.
2. **Lossless Verbatim Storage**: Do not filter invalid records, do not standardize casings, and do not drop unmapped columns. If the upstream source sent corrupted JSON or malformed strings, land it exactly as received.
3. **Partitioning by Ingestion Date**: Organize files into date-partitioned folder hierarchies (e.g. `raw/cases/ingest_date=2026-09-16/`).
4. **Lineage Metadata Columns**: Append metadata columns to every landed record:
   - `_ingested_at`: UTC timestamp when the pipeline landed the file.
   - `_source_file`: Path or URL of the upstream file or API endpoint.
   - `_run_id`: Unique pipeline run identifier.

---

## 2. Directory Layout & Partitioning

```
data/raw/
└── cases/
    ├── ingest_date=2026-09-15/
    │   └── raw_cases.parquet
    └── ingest_date=2026-09-16/
        └── raw_cases.parquet
```

Organizing by `ingest_date=YYYY-MM-DD` enables **Partition Pruning** in analytics engines (Athena, Spark, DuckDB). When querying data ingested today, the engine skips scanning past dates entirely.

---

## 3. Production Implementation in `RawLayerManager`

In `pipeline/layers/raw.py`, our `RawLayerManager` lands ingested DataFrames into Parquet with lineage columns:

```python
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

class RawLayerManager:
    """Manages the Raw (Bronze) Ingestion Tier."""

    def __init__(self, raw_dir: Path):
        self.raw_dir = Path(raw_dir)

    def land_raw_data(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        run_id: str,
        source_name: str,
    ) -> Path:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        partition_dir = self.raw_dir / dataset_name / f"ingest_date={today_str}"
        partition_dir.mkdir(parents=True, exist_ok=True)

        landing_df = df.copy()
        landing_df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
        landing_df["_source_name"] = source_name
        landing_df["_run_id"] = run_id

        output_file = partition_dir / f"raw_{dataset_name}.parquet"
        landing_df.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
        return output_file
```

This guarantees that data engineers can always trace any curated record back to its exact raw bronze origin.
