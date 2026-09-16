"""
Master Data Pipeline Orchestration Engine

Coordinates the end-to-end data pipeline lifecycle across all 10 stages:
1. Source Ingestion (Heterogeneous Sources: CSV, JSON, Parquet, Relational DB, REST API)
2. Raw Layer Ingestion & Lineage Persistence
3. Statistical Data Profiling (Completeness, Uniqueness, Validity, Distribution, Referential Integrity)
4. Data Standardization & Type Coercion
5. Automated Data Quality Rule Evaluation
6. Quarantine Management for Rejected Records
7. Deduplication & Relational Joins (Enrichment)
8. Window Analytical Ranking
9. Curated Layer Publishing (Parquet & CSV)
10. Source-to-Target Mathematical Reconciliation & Audit Manifest Generation
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

from pipeline.audit.audit_manager import AuditManager
from pipeline.config import PipelineSettings, settings
from pipeline.layers.curated import CuratedLayerManager
from pipeline.layers.raw import RawLayerManager
from pipeline.layers.standardized import StandardizedLayerManager
from pipeline.orchestration.incremental import WatermarkTracker
from pipeline.profiling.profiler import DataProfiler
from pipeline.quarantine.quarantine_manager import QuarantineManager
from pipeline.reconciliation.reconciler import ReconciliationEngine
from pipeline.schemas.case_schema import (
    ALLOWED_CASE_TYPES,
    ALLOWED_PRIORITIES,
    ALLOWED_STATUSES,
)
from pipeline.sources.api_source import APISource
from pipeline.sources.csv_source import CSVSource
from pipeline.sources.database_source import DatabaseSource
from pipeline.sources.json_source import JSONSource
from pipeline.sources.parquet_source import ParquetSource
from pipeline.transformations.deduplication import deduplicate_cases
from pipeline.transformations.joins import join_case_reference_and_policies
from pipeline.transformations.standardization import (
    standardize_case_records,
    standardize_departments,
    standardize_policy_metadata,
    standardize_reference_users,
)
from pipeline.transformations.windowing import apply_window_metrics
from pipeline.validation.quality_rules import QualityRulesEvaluator


class CaseManagementPipeline:
    """Enterprise Data Pipeline Orchestrator."""

    def __init__(self, config: Optional[PipelineSettings] = None):
        self.config = config or settings
        self.config.ensure_directories()

        # Component Initializations
        self.raw_manager = RawLayerManager(self.config.raw_dir)
        self.standardized_manager = StandardizedLayerManager(self.config.standardized_dir)
        self.curated_manager = CuratedLayerManager(
            self.config.curated_dir,
            database_url=self.config.database_url,
        )
        self.quarantine_manager = QuarantineManager(self.config.rejected_dir)
        self.reconciliation_engine = ReconciliationEngine(self.config.reconciliation_dir)
        self.audit_manager = AuditManager(self.config.audit_dir)
        self.watermark_tracker = WatermarkTracker(self.config.watermark_file)
        self.profiler = DataProfiler(dataset_name="cases")

    def run(
        self,
        mode: Optional[str] = None,
        run_id: Optional[str] = None,
        cases_file: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Executes the full pipeline workflow.
        """
        start_time = datetime.now(timezone.utc)
        execution_mode = mode or self.config.run_mode
        active_run_id = run_id or self.config.get_run_id()
        batch_id = f"BATCH_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        cases_input_path = cases_file or (self.config.input_dir / "cases.csv")

        # ── STAGE 1: Heterogeneous Source Ingestion ──────────────────────
        sources_meta = []

        # Ingestion 1: Cases (CSV)
        csv_source = CSVSource(cases_input_path, source_name="cases_csv")
        raw_cases_df = csv_source.read()
        sources_meta.append({"source": "cases_csv", "format": "CSV", "path": str(cases_input_path), "count": len(raw_cases_df)})

        # Ingestion 2: Reference Lookup (JSON)
        ref_path = self.config.input_dir / "reference.json"
        json_users_source = JSONSource(ref_path, record_path="users", source_name="reference_users_json")
        json_depts_source = JSONSource(ref_path, record_path="departments", source_name="reference_depts_json")
        raw_users_df = json_users_source.read()
        raw_depts_df = json_depts_source.read()
        sources_meta.append({"source": "reference_json", "format": "JSON", "count": len(raw_users_df) + len(raw_depts_df)})

        # Ingestion 3: Policy Metadata (Parquet)
        parquet_path = self.config.input_dir / "policy_metadata.parquet"
        parquet_source = ParquetSource(parquet_path, source_name="policy_parquet")
        raw_policies_df = parquet_source.read()
        sources_meta.append({"source": "policy_parquet", "format": "PARQUET", "count": len(raw_policies_df)})

        # Ingestion 4: REST API (Mock Policy API with deterministic fallback)
        api_fallback = raw_policies_df.to_dict(orient="records")
        api_source = APISource(
            endpoint_url=self.config.mock_api_url,
            timeout_seconds=self.config.mock_api_timeout_seconds,
            fallback_data=api_fallback,
            source_name="mock_rest_api",
        )
        api_policies_df = api_source.read()
        sources_meta.append({"source": "mock_rest_api", "format": "REST_API", "count": len(api_policies_df)})

        # Ingestion 5: Relational Database Source (SQLite cases table from Week 1)
        try:
            db_source = DatabaseSource(
                connection_url=self.config.database_url,
                table_name="cases",
                source_name="sqlite_cases",
            )
            db_cases_df = db_source.read()
            sources_meta.append({"source": "sqlite_cases", "format": "RELATIONAL_SQLITE", "count": len(db_cases_df)})
        except Exception:
            sources_meta.append({"source": "sqlite_cases", "format": "RELATIONAL_SQLITE", "count": 0, "status": "DB_OFFLINE"})

        # Handle incremental mode filtering on cases
        if execution_mode == "incremental":
            raw_cases_df, new_watermark = self.watermark_tracker.filter_incremental_records(raw_cases_df)
        else:
            new_watermark = datetime.now(timezone.utc)

        source_count = len(raw_cases_df)

        # ── STAGE 2: Raw Layer Persistence ───────────────────────────────
        raw_case_file = self.raw_manager.save_raw(
            raw_cases_df,
            dataset_name="cases",
            run_id=active_run_id,
            source_name="cases_csv",
        )

        # ── STAGE 3: Statistical Data Profiling ───────────────────────────
        valid_user_ids = raw_users_df["user_id"].tolist() if "user_id" in raw_users_df.columns else []
        profile_results = self.profiler.profile_cases(
            raw_cases_df,
            reference_user_ids=valid_user_ids,
        )
        prof_json, prof_md = self.profiler.save_reports(
            profile_results,
            output_dir=self.config.profiling_dir,
            run_id=active_run_id,
        )

        # ── STAGE 4: Data Standardization ────────────────────────────────
        std_cases_df = standardize_case_records(raw_cases_df)
        std_users_df = standardize_reference_users(raw_users_df)
        std_depts_df = standardize_departments(raw_depts_df)
        std_policies_df = standardize_policy_metadata(raw_policies_df)

        std_cases_file = self.standardized_manager.save_standardized(
            std_cases_df,
            dataset_name="cases",
            run_id=active_run_id,
        )

        # ── STAGE 5: Quality Rule Evaluation & Partitioning ─────────────
        quality_evaluator = QualityRulesEvaluator(
            context={"valid_user_ids": valid_user_ids}
        )
        valid_cases_df, rejected_records = quality_evaluator.evaluate(
            std_cases_df,
            run_id=active_run_id,
            source_name="cases_csv",
        )
        valid_count = len(valid_cases_df)
        quarantined_count = len(rejected_records)

        # ── STAGE 6: Quarantine Invalid Records ──────────────────────────
        rejected_file = None
        if quarantined_count > 0:
            rejected_file = self.quarantine_manager.quarantine_records(
                rejected_records=rejected_records,
                run_id=active_run_id,
                batch_id=batch_id,
            )

        # ── STAGE 7: Deduplication & Relational Joins ────────────────────
        deduped_cases_df, duplicates_removed = deduplicate_cases(
            valid_cases_df,
            primary_key="case_id",
            order_by_col="updated_at",
        )

        enriched_cases_df = join_case_reference_and_policies(
            cases_df=deduped_cases_df,
            users_df=std_users_df,
            depts_df=std_depts_df,
            policies_df=std_policies_df,
        )

        # ── STAGE 8: Analytical Window Operations ────────────────────────
        curated_df = apply_window_metrics(enriched_cases_df)
        curated_count = len(curated_df)

        # ── STAGE 9: Curated Layer Publishing ────────────────────────────
        curated_file = self.curated_manager.publish_curated(
            curated_df,
            dataset_name="curated_cases",
            run_id=active_run_id,
        )

        # ── STAGE 10: Reconciliation & Audit Manifest ────────────────────
        recon_report = self.reconciliation_engine.reconcile(
            run_id=active_run_id,
            source_name="cases_csv",
            source_count=source_count,
            quarantined_count=quarantined_count,
            valid_count=valid_count,
            duplicates_removed=duplicates_removed,
            curated_count=curated_count,
        )
        recon_json, recon_md = self.reconciliation_engine.save_reports(
            recon_report,
            run_id=active_run_id,
        )

        end_time = datetime.now(timezone.utc)
        counts_summary = {
            "source_count": source_count,
            "quarantined_count": quarantined_count,
            "valid_count": valid_count,
            "duplicates_removed": duplicates_removed,
            "curated_count": curated_count,
        }
        output_locations = {
            "raw_file": str(raw_case_file),
            "standardized_file": str(std_cases_file),
            "curated_file": str(curated_file),
            "rejected_file": str(rejected_file) if rejected_file else "None",
            "profiling_report": str(prof_md),
            "reconciliation_report": str(recon_md),
        }

        manifest_file = self.audit_manager.create_manifest(
            run_id=active_run_id,
            batch_id=batch_id,
            start_time=start_time,
            end_time=end_time,
            status=recon_report["overall_status"],
            sources_ingested=sources_meta,
            counts=counts_summary,
            output_locations=output_locations,
        )

        # Update high-watermark state if incremental run
        if execution_mode == "incremental" and new_watermark:
            self.watermark_tracker.update_watermark(new_watermark, batch_id=batch_id)

        return {
            "run_id": active_run_id,
            "batch_id": batch_id,
            "status": recon_report["overall_status"],
            "mode": execution_mode,
            "source_count": source_count,
            "quarantined_count": quarantined_count,
            "valid_count": valid_count,
            "duplicates_removed": duplicates_removed,
            "curated_count": curated_count,
            "counts": counts_summary,
            "manifest_file": str(manifest_file),
            "curated_records": curated_count,
            "quarantined_records": quarantined_count,
            "reconciliation_status": recon_report["overall_status"],
        }
