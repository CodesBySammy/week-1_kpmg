"""
Command Line Interface (CLI) for Case Management Data Pipeline

Usage Examples:
    python -m pipeline.cli --mode full
    python -m pipeline.cli --mode incremental
    python -m pipeline.cli --run-id RUN_TEST_001 --input data/input/cases.csv
"""

import argparse
import json
import sys
from pathlib import Path

from pipeline.config import settings
from pipeline.orchestration.pipeline import CaseManagementPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Case Management Enterprise Data Pipeline CLI (Week 2)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="Pipeline execution mode: 'full' reloads all data; 'incremental' processes delta since last watermark.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Explicit identifier for this execution run (default: auto-generated timestamped ID).",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Custom path to input cases file (CSV format).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom directory path for publishing curated outputs.",
    )
    parser.add_argument(
        "--rerun",
        type=str,
        default=None,
        help="Rerun an existing historical batch ID.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    active_run_id = args.rerun or args.run_id
    custom_input = Path(args.input) if args.input else None

    if args.output_dir:
        settings.curated_dir = Path(args.output_dir)

    print("=" * 65)
    print(">>> STARTING CASE MANAGEMENT ENTERPRISE DATA PIPELINE (WEEK 2)")
    print(f"   Execution Mode: {args.mode.upper()}")
    if active_run_id:
        print(f"   Active Run ID:  {active_run_id}")
    print("=" * 65)

    pipeline = CaseManagementPipeline(config=settings)

    try:
        result = pipeline.run(
            mode=args.mode,
            run_id=active_run_id,
            cases_file=custom_input,
        )

        print("\n" + "=" * 65)
        print("[SUCCESS] PIPELINE EXECUTION COMPLETED")
        print("=" * 65)
        print(f"  * Run ID:                {result['run_id']}")
        print(f"  * Batch ID:              {result['batch_id']}")
        print(f"  * Status:                {result['status']}")
        print(f"  * Ingested Source Rows:  {result['counts']['source_count']}")
        print(f"  * Valid Rows:            {result['counts']['valid_count']}")
        print(f"  * Quarantined Rows:      {result['quarantined_records']}")
        print(f"  * Duplicates Removed:    {result['counts']['duplicates_removed']}")
        print(f"  * Curated Rows:          {result['curated_records']}")
        print(f"  * Reconciliation Check:  {result['reconciliation_status']}")
        print(f"  * Run Manifest:          {result['manifest_file']}")
        print("=" * 65)

        if result["status"] != "PASS":
            print("[WARNING] Reconciliation failed balance check!")
            return 1

        return 0

    except Exception as exc:
        print(f"\n[ERROR] PIPELINE EXECUTION FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
