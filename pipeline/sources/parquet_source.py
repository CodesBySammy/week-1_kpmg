"""
Parquet Source Ingestion Component

Reads columnar policy metadata from Apache Parquet files.
"""

from pathlib import Path
from typing import Union
import pandas as pd
from pipeline.sources.base_source import BaseSource


class ParquetSource(BaseSource):
    """Ingests policy metadata from Apache Parquet columnar files."""

    def __init__(self, file_path: Union[str, Path], source_name: str = "policy_parquet"):
        super().__init__(source_name=source_name)
        self.file_path = Path(file_path)

    def read(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Parquet source file not found at: {self.file_path}")

        try:
            df = pd.read_parquet(self.file_path, engine="pyarrow")
            return df
        except Exception as exc:
            raise RuntimeError(f"Failed to read Parquet source from {self.file_path}: {exc}") from exc
