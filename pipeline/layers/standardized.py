"""
Standardized Data Layer Manager

Persists cleaned, type-cast, schema-conformant datasets.
"""

from pathlib import Path
import pandas as pd


class StandardizedLayerManager:
    """Manages persistence of standardized records."""

    def __init__(self, standardized_dir: Path):
        self.standardized_dir = Path(standardized_dir)
        self.standardized_dir.mkdir(parents=True, exist_ok=True)

    def save_standardized(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        run_id: str,
    ) -> Path:
        """
        Saves standardized records in columnar Parquet format for fast querying.
        """
        output_file = self.standardized_dir / f"{dataset_name}_standardized_{run_id}.parquet"
        df.to_parquet(output_file, engine="pyarrow", index=False)
        return output_file
