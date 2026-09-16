# Lab 01: Ingesting CSV with Resilient Parsing & Bad Line Handling

## Objective
Build and test a resilient CSV source reader that handles raw strings, checks file existence, and protects against corrupted delimiters.

---

## Exercise

1. Create a script or run in Python REPL:
```python
from pathlib import Path
import pandas as pd
from pipeline.sources.csv_source import CSVSource

# Point to sample cases
csv_path = Path("data/input/cases.csv")
source = CSVSource(file_path=csv_path, source_name="lab_csv")

df = source.read()
print(f"Ingested {len(df)} rows from {csv_path.name}")
print(f"Columns: {list(df.columns)}")
print(df.head(2))
```

2. Test failure handling on a non-existent file:
```python
try:
    bad_source = CSVSource(file_path=Path("non_existent.csv"))
    bad_source.read()
except FileNotFoundError as e:
    print(f"Successfully caught expected error: {e}")
```

---

## Verification
- Confirm that 20 rows are ingested.
- Confirm all values are ingested as strings to avoid premature type inference before profiling.
