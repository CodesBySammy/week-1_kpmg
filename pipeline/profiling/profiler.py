"""
Data Profiling Engine

Computes 5-pillar statistical profiles of unfamiliar datasets:
1. Completeness (Null counts & percentages)
2. Uniqueness (Duplicate counts & cardinality ratios)
3. Validity (Domain rule, format & range violations)
4. Distribution (Frequency distributions & numerical metrics)
5. Referential Integrity (Foreign key presence and orphan detection)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from pipeline.schemas.case_schema import (
    ALLOWED_CASE_TYPES,
    ALLOWED_PRIORITIES,
    ALLOWED_STATUSES,
)


class DataProfiler:
    """Calculates comprehensive statistical and structural data profiles."""

    def __init__(self, dataset_name: str = "cases"):
        self.dataset_name = dataset_name

    def profile_cases(
        self,
        df: pd.DataFrame,
        reference_user_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Profiles a cases dataset across all 5 dimensions required by the curriculum.
        """
        total_records = len(df)
        if total_records == 0:
            return {"error": "Dataset is empty", "total_records": 0}

        profile: Dict[str, Any] = {
            "dataset_name": self.dataset_name,
            "profiled_at": datetime.now(timezone.utc).isoformat(),
            "total_records": total_records,
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "completeness": {},
            "uniqueness": {},
            "validity": {},
            "distribution": {},
            "referential_integrity": {},
        }

        # ── 1. Completeness: Null Counts & Null Percentages ──────────────
        for col in df.columns:
            # Count both explicit NaNs and empty string representations
            is_empty_str = (df[col].astype(str).str.strip() == "")
            is_na = df[col].isna()
            missing_count = int((is_na | is_empty_str).sum())
            missing_pct = round((missing_count / total_records) * 100, 2)
            profile["completeness"][col] = {
                "missing_count": missing_count,
                "missing_percentage": missing_pct,
                "present_count": total_records - missing_count,
                "present_percentage": round(100.0 - missing_pct, 2),
            }

        # ── 2. Uniqueness: Duplicate Counts & Cardinality ────────────────
        if "case_id" in df.columns:
            pk_series = df["case_id"].dropna()
            total_pk = len(pk_series)
            unique_pk = int(pk_series.nunique())
            duplicate_pk_count = total_pk - unique_pk
            profile["uniqueness"]["case_id"] = {
                "unique_count": unique_pk,
                "duplicate_count": duplicate_pk_count,
                "uniqueness_ratio": round(unique_pk / total_pk if total_pk else 0.0, 4),
            }

        full_row_duplicates = int(df.duplicated().sum())
        profile["uniqueness"]["full_row_duplicates"] = full_row_duplicates

        # ── 3. Validity: Domain & Format Conformance ────────────────────
        validity: Dict[str, Any] = {}

        if "status" in df.columns:
            statuses = df["status"].dropna().astype(str).str.strip().str.upper()
            invalid_statuses = statuses[~statuses.isin(ALLOWED_STATUSES)]
            validity["status"] = {
                "valid_count": int(statuses.isin(ALLOWED_STATUSES).sum()),
                "invalid_count": int(len(invalid_statuses)),
                "invalid_samples": list(invalid_statuses.unique()[:5]),
            }

        if "priority" in df.columns:
            priorities = df["priority"].dropna().astype(str).str.strip().str.upper()
            invalid_priorities = priorities[~priorities.isin(ALLOWED_PRIORITIES)]
            validity["priority"] = {
                "valid_count": int(priorities.isin(ALLOWED_PRIORITIES).sum()),
                "invalid_count": int(len(invalid_priorities)),
                "invalid_samples": list(invalid_priorities.unique()[:5]),
            }

        if "case_type" in df.columns:
            types = df["case_type"].dropna().astype(str).str.strip().str.upper()
            invalid_types = types[~types.isin(ALLOWED_CASE_TYPES)]
            validity["case_type"] = {
                "valid_count": int(types.isin(ALLOWED_CASE_TYPES).sum()),
                "invalid_count": int(len(invalid_types)),
                "invalid_samples": list(invalid_types.unique()[:5]),
            }

        if "case_id" in df.columns:
            try:
                numeric_ids = pd.to_numeric(df["case_id"], errors="coerce")
                negative_ids = int((numeric_ids < 0).sum())
                validity["numeric_case_id"] = {
                    "negative_count": negative_ids,
                    "non_numeric_count": int(numeric_ids.isna().sum()),
                }
            except Exception:
                pass

        profile["validity"] = validity

        # ── 4. Distribution: Categorical Frequencies ────────────────────
        distribution: Dict[str, Any] = {}
        for cat_col in ["status", "priority", "case_type"]:
            if cat_col in df.columns:
                counts = df[cat_col].value_counts(dropna=False).to_dict()
                distribution[cat_col] = {str(k): int(v) for k, v in counts.items()}
        profile["distribution"] = distribution

        # ── 5. Referential Integrity ─────────────────────────────────────
        if reference_user_ids is not None:
            ref_int: Dict[str, Any] = {}
            for user_col in ["created_by", "assigned_to"]:
                if user_col in df.columns:
                    # Clean and parse user IDs
                    series = pd.to_numeric(df[user_col], errors="coerce").dropna().astype(int)
                    orphans = series[~series.isin(reference_user_ids)]
                    ref_int[user_col] = {
                        "total_referenced": len(series),
                        "valid_references": int(series.isin(reference_user_ids).sum()),
                        "orphan_count": int(len(orphans)),
                        "orphan_samples": list(orphans.unique()[:5]),
                    }
            profile["referential_integrity"] = ref_int

        return profile

    def save_reports(
        self,
        profile_dict: Dict[str, Any],
        output_dir: Path,
        run_id: str,
    ) -> Tuple[Path, Path]:
        """
        Saves both machine-readable JSON and human-readable Markdown profile reports.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{self.dataset_name}_profile_{run_id}.json"
        md_path = output_dir / f"{self.dataset_name}_profile_{run_id}.md"

        # 1. Write JSON Report
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(profile_dict, f, indent=2, default=str)

        # 2. Write Markdown Report
        md_lines = [
            f"# Data Profiling Report: {self.dataset_name.upper()}",
            f"**Run ID:** `{run_id}`  ",
            f"**Profiled At:** {profile_dict.get('profiled_at')}  ",
            f"**Total Records:** {profile_dict.get('total_records')} | **Columns:** {profile_dict.get('total_columns')}  ",
            "\n---\n",
            "## 1. Completeness Metrics (Null Analysis)",
            "| Column | Missing Count | Missing % | Present Count | Present % |",
            "|---|---|---|---|---|",
        ]
        for col, stats in profile_dict.get("completeness", {}).items():
            md_lines.append(
                f"| `{col}` | {stats['missing_count']} | {stats['missing_percentage']}% | {stats['present_count']} | {stats['present_percentage']}% |"
            )

        md_lines.extend([
            "\n---\n",
            "## 2. Uniqueness Metrics",
        ])
        for key, val in profile_dict.get("uniqueness", {}).items():
            md_lines.append(f"- **{key}:** `{val}`")

        md_lines.extend([
            "\n---\n",
            "## 3. Validity Metrics",
        ])
        for col, val in profile_dict.get("validity", {}).items():
            md_lines.append(f"### Column: `{col}`")
            for k, v in val.items():
                md_lines.append(f"- {k}: `{v}`")

        md_lines.extend([
            "\n---\n",
            "## 4. Categorical Distributions",
        ])
        for col, dist in profile_dict.get("distribution", {}).items():
            md_lines.append(f"### Distribution of `{col}`:")
            for k, v in dist.items():
                md_lines.append(f"- **{k}**: {v}")

        md_lines.extend([
            "\n---\n",
            "## 5. Referential Integrity",
        ])
        for col, val in profile_dict.get("referential_integrity", {}).items():
            md_lines.append(f"- **{col}**: {val['orphan_count']} orphan records found (samples: `{val['orphan_samples']}`)")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return json_path, md_path
