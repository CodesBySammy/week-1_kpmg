# Lab 03: Reading Columnar Parquet & Inspecting Schema Metadata

## Objective
Ingest columnar Parquet files using `pyarrow` and inspect the embedded Thrift metadata and statistics.

---

## Exercise

1. Read and inspect `data/input/policy_metadata.parquet`:
```python
from pathlib import Path
import pyarrow.parquet as pq
from pipeline.sources.parquet_source import ParquetSource

parquet_path = Path("data/input/policy_metadata.parquet")

# Method 1: Via ParquetSource
source = ParquetSource(file_path=parquet_path, source_name="policy_parquet")
df = source.read()
print(f"Ingested {len(df)} policy rows")
print(df.info())

# Method 2: Inspect Low-Level Parquet File Metadata
parquet_file = pq.ParquetFile(parquet_path)
print("=== Parquet Schema ===")
print(parquet_file.schema)
print("=== Number of Row Groups ===")
print(parquet_file.num_row_groups)
print("=== Row Group 0 Statistics ===")
rg = parquet_file.metadata.row_group(0)
for col_idx in range(rg.num_columns):
    col = rg.column(col_idx)
    print(f"Column: {col.path_in_schema}, Enc: {col.encodings}, Total Size: {col.total_compressed_size} bytes")
```

---

## Verification
- Notice how Parquet metadata explicitly stores data types and compression schemes (Snappy).
