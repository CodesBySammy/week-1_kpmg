# Lab 02: Ingesting Semi-Structured JSON & Record Path Extraction

## Objective
Extract separate entity tables from a single nested JSON document using targeted record paths.

---

## Exercise

1. Inspect `data/input/reference.json`:
   Notice it contains top-level keys `"users"` and `"departments"`.

2. Use `JSONSource` to extract both arrays into independent DataFrames:
```python
from pathlib import Path
from pipeline.sources.json_source import JSONSource

ref_path = Path("data/input/reference.json")

# Ingest Users
user_source = JSONSource(file_path=ref_path, record_path="users", source_name="users_json")
users_df = user_source.read()
print(f"Users extracted: {len(users_df)} rows")
print(users_df.head(2))

# Ingest Departments
dept_source = JSONSource(file_path=ref_path, record_path="departments", source_name="depts_json")
depts_df = dept_source.read()
print(f"Departments extracted: {len(depts_df)} rows")
print(depts_df.head(2))
```

---

## Verification
- Assert that `users_df` has 10 rows with columns `['user_id', 'username', 'department_id', 'tier', 'region']`.
- Assert that `depts_df` has 3 rows with columns `['department_id', 'department_name', 'lead_user_id']`.
