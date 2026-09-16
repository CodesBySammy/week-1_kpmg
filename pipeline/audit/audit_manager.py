"""
Audit Metadata & Run Manifest Manager

Maintains complete traceability, operational batch metadata, and execution lineage.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditManager:
    """Records pipeline execution manifests and batch audit metadata."""

    def __init__(self, audit_dir: Path):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def create_manifest(
        self,
        run_id: str,
        batch_id: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        sources_ingested: List[Dict[str, Any]],
        counts: Dict[str, int],
        output_locations: Dict[str, str],
        errors: Optional[List[str]] = None,
    ) -> Path:
        """
        Creates and persists a comprehensive run manifest JSON artifact.
        """
        duration_seconds = round((end_time - start_time).total_seconds(), 3)
        manifest_file = self.audit_dir / f"manifest_{run_id}.json"

        manifest_data = {
            "run_id": run_id,
            "batch_id": batch_id,
            "pipeline_version": "2.0.0",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "status": status,
            "sources_ingested": sources_ingested,
            "record_counts": counts,
            "output_locations": output_locations,
            "errors": errors or [],
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, default=str)

        # Also maintain a rolling master audit ledger file
        ledger_file = self.audit_dir / "execution_ledger.jsonl"
        summary_line = {
            "run_id": run_id,
            "batch_id": batch_id,
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "status": status,
            "source_count": counts.get("source_count", 0),
            "curated_count": counts.get("curated_count", 0),
            "rejected_count": counts.get("quarantined_count", 0),
        }
        with open(ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary_line, default=str) + "\n")

        return manifest_file
