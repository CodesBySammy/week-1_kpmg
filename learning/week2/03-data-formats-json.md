# Data Formats Deep Dive: JSON, JSON Lines, and Semi-Structured Normalization

JavaScript Object Notation (**JSON**) is the standard format for web service responses, event streams, and document databases. Unlike CSV, JSON is hierarchical and self-describing, but it introduces distinct challenges in relational data engineering.

---

## 1. JSON vs JSON Lines (JSONL / NDJSON)

There are two primary JSON structures in data engineering:

### A. Standard JSON (Document Array)
```json
{
  "users": [
    {"user_id": 1, "username": "alice", "tier": "L1"},
    {"user_id": 2, "username": "bob", "tier": "L2"}
  ]
}
```
- **Limitation**: The entire file must be parsed into memory as a single object before individual records can be read. A 5 GB JSON file cannot easily be streamed.

### B. JSON Lines (`.jsonl` or `.ndjson`)
```json
{"event_id": 101, "timestamp": "2026-03-01T10:00:00Z", "action": "CREATE"}
{"event_id": 102, "timestamp": "2026-03-01T10:01:00Z", "action": "UPDATE"}
```
- **Advantage**: Each line is an independent, valid JSON document. Files can be read line-by-line using streaming buffers, split across worker threads, and processed in constant memory $O(1)$.
- In Week 2, our **Execution Ledger** (`audit/execution_ledger.jsonl`) uses JSONL for append-only audit tracking.

---

## 2. Flattening Nested JSON Objects (`pd.json_normalize`)

Real-world API payloads often contain nested sub-objects and arrays:

```json
{
  "case_id": 101,
  "creator": {
    "user_id": 5,
    "contact": {
      "email": "sarah@example.com",
      "phone": "+1-555-0199"
    }
  },
  "tags": ["security", "p1"]
}
```

To transform this into tabular columns for SQL/analytical queries, use `pd.json_normalize`:

```python
import pandas as pd

raw_data = [
    {
        "case_id": 101,
        "creator": {"user_id": 5, "contact": {"email": "sarah@example.com"}},
        "tags": ["security", "p1"],
    }
]

# Flatten nested sub-objects with dot separator
flat_df = pd.json_normalize(raw_data, sep="_")
print(flat_df.columns.tolist())
# Output: ['case_id', 'tags', 'creator_user_id', 'creator_contact_email']
```

---

## 3. Production JSON Ingestion in Our Pipeline

In `pipeline/sources/json_source.py`, our `JSONSource` supports both top-level record arrays and targeted record paths:

```python
import json
from pathlib import Path
from typing import Optional
import pandas as pd
from pipeline.sources.base_source import BaseSource

class JSONSource(BaseSource):
    """Production JSON Ingestion Component supporting targeted record paths."""

    def __init__(
        self,
        file_path: Path,
        record_path: Optional[str] = None,
        source_name: str = "json_source",
    ):
        super().__init__(source_name=source_name)
        self.file_path = Path(file_path)
        self.record_path = record_path

    def read(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if self.record_path and isinstance(data, dict):
            # Extract nested array (e.g. data["users"] or data["departments"])
            records = data.get(self.record_path, [])
        elif isinstance(data, list):
            records = data
        else:
            records = [data]

        return pd.json_normalize(records)
```

In our Week 2 pipeline, `data/input/reference.json` contains two distinct record paths (`users` and `departments`), which are ingested cleanly as separate reference DataFrames without duplicating disk files.
