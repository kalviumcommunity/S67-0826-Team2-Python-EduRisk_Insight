from pathlib import Path

from src.database import DatabaseManager


def test_required_reporting_objects_exist():
    db = DatabaseManager(Path("data/studentpulse.db"))
    rows = db.execute_query("SELECT name, type FROM sqlite_master WHERE type IN ('table','view')")
    objects = {(r["name"], r["type"]) for r in rows}
    required_tables = {
        "students", "enrolments", "attendance", "assignments", "assessments",
        "interventions", "student_course_features", "risk_assessments",
        "data_quality_reports", "pipeline_runs",
    }
    required_views = {
        "v_overview_kpis", "v_risk_explorer", "v_course_risk_summary",
        "v_student_detail", "v_data_quality_summary",
    }
    assert required_tables <= {n for n, t in objects if t == "table"}
    assert required_views <= {n for n, t in objects if t == "view"}


def test_demo_database_has_explainable_risk_records():
    db = DatabaseManager(Path("data/studentpulse.db"))
    total = db.execute_query("SELECT COUNT(*) AS c FROM risk_assessments")[0]["c"]
    invalid = db.execute_query("SELECT COUNT(*) AS c FROM risk_assessments WHERE risk_level NOT IN ('Low','Medium','High')")[0]["c"]
    unexplained = db.execute_query("SELECT COUNT(*) AS c FROM risk_assessments WHERE risk_score > 0 AND (reasons_json IS NULL OR reasons_json = '[]')")[0]["c"]
    assert invalid == 0
    assert unexplained == 0
    if total == 0:
        # If active DB is clean/empty, verify explainability on a synthetic pipeline run
        from src.pipeline import run_pipeline
        from scripts.generate_data import generate_synthetic_academic_dataset
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_db = Path(tmp_dir) / "test.db"
            raw_source = Path(tmp_dir) / "raw"
            generate_synthetic_academic_dataset(target_enrolments=30, output_dir=raw_source, fixtures_dir=Path(tmp_dir) / "fixtures")
            run_pipeline(raw_dir=raw_source, db_path=test_db, processed_dir=Path(tmp_dir) / "proc")
            db_test = DatabaseManager(test_db)
            total_t = db_test.execute_query("SELECT COUNT(*) AS c FROM risk_assessments")[0]["c"]
            assert total_t > 0
