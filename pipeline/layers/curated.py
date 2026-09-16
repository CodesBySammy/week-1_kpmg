"""
Curated Data Layer Manager

Publishes business-ready, enriched, joined, quality-verified datasets.
Supports Parquet, CSV, and relational table exports for downstream consumption.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine


class CuratedLayerManager:
    """Manages publishing of curated analytical datasets."""

    def __init__(self, curated_dir: Path, database_url: Optional[str] = None):
        self.curated_dir = Path(curated_dir)
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        self.database_url = database_url

    def publish_curated(
        self,
        df: pd.DataFrame,
        dataset_name: str = "curated_cases",
        run_id: Optional[str] = None,
    ) -> Path:
        """
        Publishes curated data to:
        1. Current latest Parquet: data/curated/{dataset_name}.parquet
        2. Timestamped Parquet: data/curated/{dataset_name}_{run_id}.parquet
        3. CSV for easy spreadsheet inspection: data/curated/{dataset_name}.csv
        4. Relational table in database if connection configured.
        """
        # 1. Primary latest Parquet
        parquet_path = self.curated_dir / f"{dataset_name}.parquet"
        df.to_parquet(parquet_path, engine="pyarrow", index=False)

        # 2. Timestamped version for historical lineage
        if run_id:
            versioned_path = self.curated_dir / f"{dataset_name}_{run_id}.parquet"
            df.to_parquet(versioned_path, engine="pyarrow", index=False)

        # 3. CSV export
        csv_path = self.curated_dir / f"{dataset_name}.csv"
        df.to_csv(csv_path, index=False)

        # 4. Optional relational export for downstream SQL querying
        if self.database_url:
            try:
                engine = create_engine(self.database_url)
                # Ensure SQLite doesn't fail on complex timestamp objects
                db_df = df.copy()
                for col in db_df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
                    db_df[col] = db_df[col].astype(str)
                with engine.connect() as conn:
                    db_df.to_sql(dataset_name, conn, if_exists="replace", index=False)
            except Exception:
                pass  # Non-fatal if relational export fails

        return parquet_path
