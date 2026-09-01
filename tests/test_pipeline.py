"""
Integration tests for StudentPulse AI End-to-End Pipeline.
Verifies the complete execution from CSV ingestion to SQLite schema creation.
"""

from pathlib import Path
import tempfile
import pytest

from src.pipeline import run_pipeline, PipelineRunResult
from src.database import DatabaseManager


def test_end_to_end_pipeline_execution():
    """Executes the full pipeline on a temporary database and verifies all artifacts."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_db = tmp_path / "test_studentpulse.db"
        test_processed = tmp_path / "processed"

        raw_source = tmp_path / "raw"
        from scripts.generate_data import generate_synthetic_academic_dataset
        generate_synthetic_academic_dataset(target_enrolments=30, output_dir=raw_source, fixtures_dir=tmp_path / "fixtures")
        result = run_pipeline(
            raw_dir=raw_source,
            db_path=test_db,
            config_path=Path("config/risk_thresholds.yaml"),
            processed_dir=test_processed,
        )

        assert isinstance(result, PipelineRunResult)
        assert result.status in ("SUCCESS", "WARNING")
        assert result.total_students > 0
        assert result.total_enrolments > 0
        assert (result.high_risk_count + result.medium_risk_count + result.low_risk_count) > 0
        assert result.validation_health_pct > 90.0

        # Verify SQLite tables exist and contain records
        db = DatabaseManager(db_path=test_db)
        tables = [r["name"] for r in db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")]
        
        expected_tables = [
            "students", "enrolments", "attendance", "assignments",
            "assessments", "student_course_features", "risk_assessments",
            "data_quality_reports", "pipeline_runs"
        ]
        for tbl in expected_tables:
            assert tbl in tables, f"Expected table {tbl} was not created in database."

        # Verify processed CSV snapshots
        assert (test_processed / "student_course_features.csv").exists()
        assert (test_processed / "risk_assessments.csv").exists()
        assert (test_processed / "latest_quality_report.csv").exists()
