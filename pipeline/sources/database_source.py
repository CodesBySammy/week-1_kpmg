"""
Relational Database Source Ingestion Component

Ingests case and user records directly from the Week 1 SQLite relational database.
"""

from typing import Optional
import pandas as pd
from sqlalchemy import create_engine
from pipeline.sources.base_source import BaseSource


class DatabaseSource(BaseSource):
    """Ingests records from relational database tables."""

    def __init__(
        self,
        connection_url: str,
        table_name: str = "cases",
        query: Optional[str] = None,
        source_name: str = "database_sqlite",
    ):
        super().__init__(source_name=source_name)
        self.connection_url = connection_url
        self.table_name = table_name
        self.query = query or f"SELECT * FROM {table_name}"

    def read(self) -> pd.DataFrame:
        try:
            engine = create_engine(self.connection_url)
            with engine.connect() as conn:
                df = pd.read_sql_query(self.query, conn)
            return df
        except Exception as exc:
            raise RuntimeError(
                f"Failed to query relational database source ({self.connection_url}): {exc}"
            ) from exc
