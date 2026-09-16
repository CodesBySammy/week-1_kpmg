"""
Incremental Load & Watermark Management Component

Enables delta processing by maintaining high-watermark state across runs.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd


class WatermarkTracker:
    """Tracks and persists the high-watermark timestamp for incremental delta processing."""

    def __init__(self, watermark_path: Path):
        self.watermark_path = Path(watermark_path)
        self.watermark_path.parent.mkdir(parents=True, exist_ok=True)

    def get_watermark(self) -> Optional[datetime]:
        """Reads the latest committed high-watermark timestamp."""
        if not self.watermark_path.exists():
            return None
        try:
            with open(self.watermark_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                ts_str = data.get("high_watermark")
                if ts_str:
                    return datetime.fromisoformat(ts_str)
        except Exception:
            return None
        return None

    def update_watermark(self, new_watermark: datetime, batch_id: str) -> None:
        """Persists updated high-watermark timestamp after successful run."""
        payload = {
            "high_watermark": new_watermark.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_batch_id": batch_id,
        }
        with open(self.watermark_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def filter_incremental_records(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "updated_at",
    ) -> Tuple[pd.DataFrame, Optional[datetime]]:
        """
        Filters DataFrame to keep only records newer than the high-watermark.
        Returns (delta_df, new_max_watermark).
        """
        watermark = self.get_watermark()
        if watermark is None or len(df) == 0:
            # Full load: compute initial max watermark
            ts_series = pd.to_datetime(df[timestamp_col], errors="coerce", utc=True).dropna()
            max_ts = ts_series.max().to_pydatetime() if not ts_series.empty else datetime.now(timezone.utc)
            return df.copy(), max_ts

        # Convert column to comparable UTC datetime
        dt_col = pd.to_datetime(df[timestamp_col], errors="coerce", utc=True)
        # Ensure watermark has tzinfo
        if watermark.tzinfo is None:
            watermark = watermark.replace(tzinfo=timezone.utc)

        delta_mask = dt_col > watermark
        delta_df = df[delta_mask].copy()

        ts_series = pd.to_datetime(delta_df[timestamp_col], errors="coerce", utc=True).dropna()
        new_max = ts_series.max().to_pydatetime() if not ts_series.empty else watermark

        return delta_df, new_max
