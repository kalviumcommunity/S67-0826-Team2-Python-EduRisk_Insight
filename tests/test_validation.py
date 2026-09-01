"""
Unit tests for StudentPulse AI Data Quality & Validation Engine.
Tests all institutional rules and controlled invalid fixtures.
"""

from pathlib import Path
import pytest
import pandas as pd

from src.validate import DataQualityValidator, QualityRuleResult, ValidationReport
from src.ingest import ingest_raw_data


@pytest.fixture
def sample_valid_data():
    """Provides a valid synthetic data payload."""
    students = pd.DataFrame([
        {"student_id": "STU-001", "program": "Data Science", "cohort_year": 2026},
        {"student_id": "STU-002", "program": "Computer Science", "cohort_year": 2026},
    ])
    enrolments = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},
        {"student_id": "STU-002", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},
    ])
    attendance = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "Present"},
        {"student_id": "STU-002", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "Absent"},
    ])
    assignments = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10 23:59:00", "submitted_at": "2026-09-09 10:00:00", "score": 90.0, "max_score": 100.0},
        {"student_id": "STU-002", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10 23:59:00", "submitted_at": None, "score": None, "max_score": 100.0},
    ])
    assessments = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "assessment_date": "2026-10-01", "assessment_type": "Quiz 1", "score": 85.0, "max_score": 100.0},
    ])
    return {
        "students": students,
        "enrolments": enrolments,
        "attendance": attendance,
        "assignments": assignments,
        "assessments": assessments,
    }


def test_validator_passes_valid_data(sample_valid_data):
    """Verifies that 100% valid data passes all checks without errors."""
    validator = DataQualityValidator(run_id="test_run_valid")
    report = validator.validate_all(sample_valid_data)
    
    assert isinstance(report, ValidationReport)
    assert report.failed_rules == 0
    assert report.has_blocking_errors is False
    assert report.overall_health_pct == 100.0
    assert len(report.rule_results) > 0


def test_validator_detects_duplicate_students(sample_valid_data):
    """Verifies detection of duplicate student IDs."""
    data = sample_valid_data.copy()
    data["students"] = pd.DataFrame([
        {"student_id": "STU-001", "program": "Data Science", "cohort_year": 2026},
        {"student_id": "STU-001", "program": "Data Science", "cohort_year": 2026},  # Duplicate
    ])
    validator = DataQualityValidator()
    report = validator.validate_all(data)
    
    dup_rules = [r for r in report.rule_results if r.rule_code == "STUDENTS_DUP_ID"]
    assert len(dup_rules) == 1
    assert dup_rules[0].status == "FAIL"
    assert dup_rules[0].records_failed == 1


def test_validator_detects_unmatched_student_foreign_key(sample_valid_data):
    """Verifies foreign key failure when enrollment refers to non-existent student."""
    data = sample_valid_data.copy()
    data["enrolments"] = pd.DataFrame([
        {"student_id": "STU-UNKNOWN-999", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},
    ])
    validator = DataQualityValidator()
    report = validator.validate_all(data)
    
    fk_rules = [r for r in report.rule_results if r.rule_code == "ENROLMENTS_FK_STUDENT"]
    assert len(fk_rules) == 1
    assert fk_rules[0].status == "FAIL"
    assert fk_rules[0].records_failed == 1


def test_validator_detects_invalid_attendance_status(sample_valid_data):
    """Verifies enum validation on attendance status."""
    data = sample_valid_data.copy()
    data["attendance"] = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "InvalidStatus"},
    ])
    validator = DataQualityValidator()
    report = validator.validate_all(data)
    
    enum_rules = [r for r in report.rule_results if r.rule_code == "ATTENDANCE_STATUS_ENUM"]
    assert len(enum_rules) == 1
    assert enum_rules[0].status == "FAIL"


def test_validator_detects_invalid_assignment_scores(sample_valid_data):
    """Verifies assignment score bounds check ([0, max_score])."""
    data = sample_valid_data.copy()
    data["assignments"] = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10", "score": -10.0, "max_score": 100.0},
        {"student_id": "STU-002", "course_id": "DATA-101", "assignment_id": "A2", "due_date": "2026-09-10", "score": 150.0, "max_score": 100.0},
    ])
    validator = DataQualityValidator()
    report = validator.validate_all(data)
    
    score_rules = [r for r in report.rule_results if r.rule_code == "ASSIGNMENT_SCORE_RANGE"]
    assert len(score_rules) == 1
    assert score_rules[0].status == "FAIL"
    assert score_rules[0].records_failed == 2


def test_validator_detects_empty_students_table():
    """Verifies failure on empty students dimension."""
    validator = DataQualityValidator()
    report = validator.validate_all({"students": pd.DataFrame()})
    
    empty_rules = [r for r in report.rule_results if r.rule_code == "STUDENTS_EMPTY"]
    assert len(empty_rules) == 1
    assert empty_rules[0].status == "FAIL"
    assert report.has_blocking_errors is True


def test_validator_converts_to_dataframe(sample_valid_data):
    """Verifies conversion of ValidationReport to DataFrame for SQL storage."""
    validator = DataQualityValidator()
    report = validator.validate_all(sample_valid_data)
    df = report.to_dataframe()
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "rule_code" in df.columns
    assert "status" in df.columns
    assert "severity" in df.columns
