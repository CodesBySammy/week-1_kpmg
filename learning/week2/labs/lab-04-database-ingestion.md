# Lab 04: Relational Extraction from SQLite via SQLAlchemy

## Objective
Extract operational case records directly from an existing SQLite database using table reflection and SQL queries.

---

## Exercise

1. Execute direct database ingestion:
```python
from pipeline.sources.database_source import DatabaseSource

db_url = "sqlite:///data/cases.db"

# Ingest entire cases table
source = DatabaseSource(connection_url=db_url, query_or_table="cases")
df = source.read()
print(f"Extracted {len(df)} records from cases table")

# Ingest with filtered SQL query
query = "SELECT case_id, title, status, priority FROM cases WHERE status = 'OPEN'"
filtered_source = DatabaseSource(connection_url=db_url, query_or_table=query, is_query=True)
open_df = filtered_source.read()
print(f"Extracted {len(open_df)} OPEN cases")
```

---

## Verification
- Confirm that records are returned as a clean pandas DataFrame ready for pipeline transformation.
