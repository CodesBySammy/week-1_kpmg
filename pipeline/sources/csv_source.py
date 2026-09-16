"""
CSV Source Ingestion Component

Reads delimited case records from CSV files with type safety and error handling.
"""

from pathlib import Path
from typing import Union
import pandas as pd
from pipeline.sources.base_source import BaseSource


class CSVSource(BaseSource):
    """Ingests case records from CSV files."""

    def __init__(self, file_path: Union[str, Path], source_name: str = "cases_csv"):
        super().__init__(source_name=source_name)
        self.file_path = Path(file_path)

    def read(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV source file not found at: {self.file_path}")

        try:
            # Read CSV with string retention for IDs to prevent floating point conversion
            df = pd.read_csv(
                self.file_path,
                dtype=str,
                keep_default_na=False,  # Treat empty string as empty string initially
            )
            return df
        except Exception as exc:
            raise RuntimeError(f"Failed to read CSV source from {self.file_path}: {exc}") from exc
