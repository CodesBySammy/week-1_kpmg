"""
JSON Source Ingestion Component

Reads structured reference data from JSON files with schema support.
"""

import json
from pathlib import Path
from typing import Optional, Union
import pandas as pd
from pipeline.sources.base_source import BaseSource


class JSONSource(BaseSource):
    """Ingests reference data from JSON files."""

    def __init__(
        self,
        file_path: Union[str, Path],
        record_path: Optional[str] = None,
        source_name: str = "reference_json",
    ):
        super().__init__(source_name=source_name)
        self.file_path = Path(file_path)
        self.record_path = record_path

    def read(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON source file not found at: {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if self.record_path and isinstance(data, dict):
                if self.record_path not in data:
                    raise KeyError(f"Key '{self.record_path}' not found in JSON source file")
                records = data[self.record_path]
                df = pd.DataFrame(records)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                # Flat dictionary
                df = pd.json_normalize(data)

            return df
        except Exception as exc:
            raise RuntimeError(f"Failed to read JSON source from {self.file_path}: {exc}") from exc
