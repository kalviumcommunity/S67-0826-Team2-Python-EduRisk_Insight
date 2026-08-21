"""
Unit tests for StudentPulse AI Feature Engineering Module.
Tests rate calculations, boundary conditions, and engagement trend classification.
"""

from pathlib import Path
import pandas as pd
import pytest

from src.transform import CleanedDatasets, clean_and_transform_data
from src.features import compute_student_course_features


@pytest.fixture
def clean_test_dataset():
    """Provides cleaned test datasets with known metric values."""
    students = pd.DataFrame([
        {"student_id": "STU-100", "program": "Analytics", "cohort_year": 2026},
        {"student_id": "STU-200", "program": "CS", "cohort_year": 2026},
    ])
    enrolments = pd.DataFrame([
        {"student_id": "STU-100", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},
        {"student_id": "STU-200", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},
    ])
    # STU-100: 4 Present, 1 Late, 1 Absent (Total=6, Attendance = (4 + 0.5)/6 = 75.0%)
    # STU-200: 1 Present, 5 Absent (Total=6, Attendance = 1/6 = 16.7%)
    attendance = pd.DataFrame([
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-01"), "attendance_status": "Present"},
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-03"), "attendance_status": "Present"},
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-08"), "attendance_status": "Present"},
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-10"), "attendance_status": "Present"},
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-15"), "attendance_status": "Late"},
        {"student_id": "STU-100", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-17"), "attendance_status": "Absent"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-01"), "attendance_status": "Present"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-03"), "attendance_status": "Absent"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-08"), "attendance_status": "Absent"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-10"), "attendance_status": "Absent"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-15"), "attendance_status": "Absent"},
        {"student_id": "STU-200", "course_id": "DATA-101", "session_date": pd.Timestamp("2026-09-17"), "attendance_status": "Absent"},
    ])
    # STU-100: 2 assignments, 2 submitted on time, score 90 and 80 -> avg 85.0%, completion 100%
    # STU-200: 2 assignments, 0 submitted -> missing 2, avg 75.0% (default), completion 0%
    assignments = pd.DataFrame([
        {"student_id": "STU-100", "course_id": "DATA-101", "assignment_id": "A1", "due_date": pd.Timestamp("2026-09-05"), "submitted_at": pd.Timestamp("2026-09-04"), "score": 90.0, "max_score": 100.0},
        {"student_id": "STU-100", "course_id": "DATA-101", "assignment_id": "A2", "due_date": pd.Timestamp("2026-09-12"), "submitted_at": pd.Timestamp("2026-09-11"), "score": 80.0, "max_score": 100.0},
        {"student_id": "STU-200", "course_id": "DATA-101", "assignment_id": "A1", "due_date": pd.Timestamp("2026-09-05"), "submitted_at": None, "score": None, "max_score": 100.0},
        {"student_id": "STU-200", "course_id": "DATA-101", "assignment_id": "A2", "due_date": pd.Timestamp("2026-09-12"), "submitted_at": None, "score": None, "max_score": 100.0},
    ])
    assessments = pd.DataFrame([
        {"student_id": "STU-100", "course_id": "DATA-101", "assessment_date": pd.Timestamp("2026-09-14"), "assessment_type": "Quiz 1", "score": 88.0, "max_score": 100.0},
        {"student_id": "STU-200", "course_id": "DATA-101", "assessment_date": pd.Timestamp("2026-09-14"), "assessment_type": "Quiz 1", "score": 35.0, "max_score": 100.0},
    ])
    interventions = pd.DataFrame(columns=["student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"])

    return CleanedDatasets(
        students=students,
        enrolments=enrolments,
        attendance=attendance,
        assignments=assignments,
        assessments=assessments,
        interventions=interventions,
    )


def test_feature_computation_attendance_rate(clean_test_dataset):
    """Verifies precision of attendance rate computation."""
    features_df = compute_student_course_features(clean_test_dataset, as_of_date=pd.Timestamp("2026-09-20"))
    
    assert len(features_df) == 2
    row_100 = features_df[features_df["student_id"] == "STU-100"].iloc[0]
    row_200 = features_df[features_df["student_id"] == "STU-200"].iloc[0]

    # STU-100: (4 + 0.5) / 6 * 100 = 75.0%
    assert abs(row_100["attendance_rate"] - 75.0) < 0.1
    # STU-200: 1 / 6 * 100 = 16.7%
    assert abs(row_200["attendance_rate"] - 16.7) < 0.2


def test_feature_computation_submission_completion(clean_test_dataset):
    """Verifies submission completion rates and missing assignment counts."""
    features_df = compute_student_course_features(clean_test_dataset, as_of_date=pd.Timestamp("2026-09-20"))
    
    row_100 = features_df[features_df["student_id"] == "STU-100"].iloc[0]
    row_200 = features_df[features_df["student_id"] == "STU-200"].iloc[0]

    assert row_100["submission_completion_rate"] == 100.0
    assert row_100["missing_assignments"] == 0

    assert row_200["submission_completion_rate"] == 0.0
    assert row_200["missing_assignments"] == 2


def test_feature_computation_assessment_average(clean_test_dataset):
    """Verifies calculation of assessment score averages."""
    features_df = compute_student_course_features(clean_test_dataset, as_of_date=pd.Timestamp("2026-09-20"))
    
    row_100 = features_df[features_df["student_id"] == "STU-100"].iloc[0]
    row_200 = features_df[features_df["student_id"] == "STU-200"].iloc[0]

    assert row_100["assessment_average"] == 88.0
    assert row_200["assessment_average"] == 35.0


def test_feature_computation_handles_empty_dataset():
    """Verifies that empty datasets return an empty DataFrame without raising exceptions."""
    empty_clean = CleanedDatasets(
        students=pd.DataFrame(),
        enrolments=pd.DataFrame(),
        attendance=pd.DataFrame(),
        assignments=pd.DataFrame(),
        assessments=pd.DataFrame(),
        interventions=pd.DataFrame(),
    )
    features_df = compute_student_course_features(empty_clean)
    assert features_df.empty
