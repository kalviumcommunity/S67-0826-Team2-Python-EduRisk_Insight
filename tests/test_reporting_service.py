"""
Unit tests for StudentPulse AI Reporting Service Layer.
Tests decoupling between UI components, database queries, and insights.
"""

from pathlib import Path
import pytest
import pandas as pd

from src.database import DatabaseManager
from src.reporting import ReportingService, OverviewMetrics


@pytest.fixture
def service(tmp_path):
    """Initializes ReportingService with an active SQLite test database."""
    test_db = tmp_path / "test_reporting.db"
    raw_source = tmp_path / "raw"
    from scripts.generate_data import generate_synthetic_academic_dataset
    generate_synthetic_academic_dataset(target_enrolments=30, output_dir=raw_source, fixtures_dir=tmp_path / "fixtures")
    from src.pipeline import run_pipeline
    run_pipeline(raw_dir=raw_source, db_path=test_db, processed_dir=tmp_path / "processed")
    db = DatabaseManager(db_path=test_db)
    return ReportingService(db_manager=db)


def test_reporting_service_filter_options(service):
    """Verifies that filter dropdown options are correctly loaded from DB."""
    opts = service.get_filter_options()
    
    assert isinstance(opts, dict)
    assert "courses" in opts
    assert "terms" in opts
    assert "sections" in opts
    assert "risk_levels" in opts
    assert "All" in opts["courses"]
    assert len(opts["courses"]) > 1


def test_reporting_service_overview_metrics(service):
    """Verifies retrieval of aggregate KPI metrics."""
    metrics = service.get_overview_metrics()
    
    assert isinstance(metrics, OverviewMetrics)
    assert metrics.total_enrolled > 0
    assert metrics.avg_attendance_rate >= 0.0
    assert metrics.avg_submission_completion >= 0.0
    assert metrics.avg_assessment_score >= 0.0


def test_reporting_service_get_risk_students(service):
    """Verifies retrieval and filtering of risk explorer student table."""
    # Test all students
    df_all = service.get_risk_students()
    assert isinstance(df_all, pd.DataFrame)
    assert not df_all.empty
    assert "student_id" in df_all.columns
    assert "risk_score" in df_all.columns
    assert "parsed_reasons" in df_all.columns

    # Test filtering by risk_level
    df_high = service.get_risk_students({"risk_level": "Needs Review"})
    assert not df_high.empty
    assert (df_high["risk_level"] == "High").all()


def test_reporting_service_get_student_detail(service):
    """Verifies fetching student profile and sub-table activity."""
    students = service.get_risk_students()
    assert not students.empty
    s_id = str(students.iloc[0]["student_id"])
    c_id = str(students.iloc[0]["course_id"])

    profile = service.get_student_detail(s_id, c_id)
    assert profile is not None
    assert profile["student_id"] == s_id
    assert "attendance_history" in profile
    assert "assignment_history" in profile
    assert "assessment_history" in profile
    assert "interventions" in profile


def test_reporting_service_add_intervention_note(service):
    """Verifies persisting a new advisor support note."""
    students = service.get_risk_students()
    s_id = str(students.iloc[0]["student_id"])
    c_id = str(students.iloc[0]["course_id"])

    success = service.add_intervention_note(
        student_id=s_id,
        course_id=c_id,
        action_type="1:1 Advisor Check-in",
        note="Automated unit test intervention note.",
        staff_user="Dr. Maya"
    )
    assert success is True

    # Verify that note appears in student detail
    profile = service.get_student_detail(s_id, c_id)
    notes = [i["outcome_note"] for i in profile["interventions"]]
    assert "Automated unit test intervention note." in notes


def test_reporting_service_top_insights(service):
    """Verifies dynamic derivation of top 3 cohort findings."""
    insights = service.get_top_insights()
    assert isinstance(insights, list)
    assert len(insights) == 3
    assert all(hasattr(i, "headline") for i in insights)
    assert all(hasattr(i, "severity") for i in insights)
