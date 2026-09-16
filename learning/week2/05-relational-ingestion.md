# Relational Database Ingestion: Cursors, Connection Pooling, and Transaction Isolation

In enterprise environments, data pipelines frequently ingest records directly from operational Online Transaction Processing (OLTP) databases such as PostgreSQL, MySQL, SQL Server, or SQLite.

---

## 1. The Challenges of Ingesting from OLTP Systems

Operational databases are actively serving user requests, API traffic, and business workflows. If a data pipeline runs an unconstrained `SELECT * FROM cases` on a 50-million-row production table:
1. **Table Locking**: Shared read locks can block writes, causing API requests to timeout (504 Gateway Timeout).
2. **Buffer Pool Eviction**: The massive full table scan evicts frequently accessed index pages from database RAM, degrading overall application responsiveness.
3. **Driver Memory Exhaustion**: Fetching millions of rows into Python memory at once causes `MemoryError`.

---

## 2. Best Practices for Production DB Extraction

### 1. Server-Side Cursors & Chunked Streaming
Rather than buffering the entire result set in memory, use server-side streaming cursors to stream rows in fixed batches (e.g. 5,000 rows at a time):

```python
from sqlalchemy import create_engine, text
import pandas as pd

def stream_database_table(connection_url: str, query: str, chunk_size: int = 5000):
    """Streams data from an OLTP database in bounded chunks using server-side execution."""
    engine = create_engine(connection_url)
    with engine.connect().execution_options(stream_results=True) as conn:
        for chunk_df in pd.read_sql_query(text(query), conn, chunksize=chunk_size):
            yield chunk_df
```

### 2. Transaction Isolation & Read Replicas
- **Never query the primary master database for large ETL extracts**: In production, route pipeline queries to a dedicated **Read Replica** (asynchronously replicated slave).
- **Isolation Level**: Set the transaction isolation to `READ COMMITTED` or `REPEATABLE READ` to avoid locking rows or seeing uncommitted dirty data.

### 3. Incremental Timestamp Predicates
Always bound database queries with timestamp boundaries rather than running full table scans:
```sql
SELECT case_id, title, status, priority, created_by, assigned_to, created_at, updated_at
FROM cases
WHERE updated_at > :high_watermark
ORDER BY updated_at ASC;
```

---

## 3. Production Implementation in Our Pipeline

In `pipeline/sources/database_source.py`, we implement `DatabaseSource`:

```python
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from pipeline.sources.base_source import BaseSource

class DatabaseSource(BaseSource):
    """Production Ingestion Component for Relational Databases via SQLAlchemy."""

    def __init__(
        self,
        connection_url: str,
        query_or_table: str,
        is_query: bool = False,
        source_name: str = "database_source",
    ):
        super().__init__(source_name=source_name)
        self.connection_url = connection_url
        self.query_or_table = query_or_table
        self.is_query = is_query

    def read(self) -> pd.DataFrame:
        engine = create_engine(self.connection_url)
        with engine.connect() as conn:
            if self.is_query:
                query = text(self.query_or_table)
            else:
                query = text(f"SELECT * FROM {self.query_or_table}")
            df = pd.read_sql(query, conn)
        return df
```

This component allows our pipeline to extract directly from the Week 1 SQLite database (`cases.db`) or any enterprise SQL database.
