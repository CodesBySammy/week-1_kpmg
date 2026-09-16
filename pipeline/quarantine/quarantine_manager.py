"""
Quarantine & Rejected-Record Handling Component

Persists invalid and non-compliant records into a dedicated quarantine area
with rich audit metadata for operational inspection and root-cause analysis.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


class QuarantineManager:
    """Manages the lifecycle and persistence of quarantined/rejected records."""

    def __init__(self, quarantine_dir: Path):
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def quarantine_records(
        self,
        rejected_records: List[Dict[str, Any]],
        run_id: str,
        batch_id: str,
    ) -> Path:
        """
        Persists rejected records to a structured JSON file in the quarantine directory.
        """
        output_file = self.quarantine_dir / f"rejected_{run_id}.json"
        
        payload = {
            "run_id": run_id,
            "batch_id": batch_id,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "total_quarantined": len(rejected_records),
            "rejected_records": rejected_records,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

        return output_file

    def get_quarantined_count(self, run_id: str) -> int:
        """Retrieves count of quarantined records for a given run ID."""
        file_path = self.quarantine_dir / f"rejected_{run_id}.json"
        if not file_path.exists():
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("total_quarantined", 0)
