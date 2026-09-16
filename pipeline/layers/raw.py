"""
Raw Data Layer Manager

Preserves source fidelity with minimal modification and explicit lineage metadata.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import pandas as pd


class RawLayerManager:
    """Manages persistence of raw, ingested datasets."""

    def __init__(self, raw_dir: Path):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        run_id: str,
        source_name: str,
    ) -> Path:
        """
        Saves raw records with system audit metadata columns:
        - _ingested_at
        - _source_name
        - _run_id
        """
        raw_df = df.copy()
        raw_df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
        raw_df["_source_name"] = source_name
        raw_df["_run_id"] = run_id

        output_file = self.raw_dir / f"{dataset_name}_raw_{run_id}.csv"
        raw_df.to_csv(output_file, index=False)
        return output_file
