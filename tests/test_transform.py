"""
Unit tests for StudentPulse AI Data Transformation & Cleaning Module (src/transform.py).
Tests deduplication, normalization, date parsing, score bounds clipping, and foreign key filtering.
"""

import pandas as pd
import pytest

from src.transform import CleanedDatasets, clean_and_transform_data


@pytest.fixture
def raw_sample_data():
    """Provides raw messy sample data dictionary for transformation testing."""
    students = pd.DataFrame([
        {"student_id": " STU-001 ", "program": " Data Science ", "cohort_year": "2026"},
        {"student_id": "STU-002", "program": "Computer Science", "cohort_year": None},
        {"student_id": "STU-001", "program": "Data Science", "cohort_year": 2026},  # Duplicate student
    ])
    enrolments = pd.DataFrame([
        {"student_id": "STU-001 ", "course_id": " DATA-101 ", "term": " Fall 2026 ", "section": " A "},
        {"student_id": "STU-001", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},  # Duplicate
        {"student_id": "STU-999", "course_id": "DATA-101", "term": "Fall 2026", "section": "A"},  # Invalid FK
    ])
    attendance = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "present"},
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-02", "attendance_status": "LATE"},
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "invalid-date", "attendance_status": "Present"},
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-03", "attendance_status": "InvalidStatus"},
        {"student_id": "STU-999", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "Present"},  # Invalid FK
        {"student_id": "STU-001", "course_id": "DATA-101", "session_date": "2026-09-01", "attendance_status": "Present"},  # Duplicate session
    ])
    assignments = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10 23:59:00", "submitted_at": "2026-09-09 10:00:00", "score": "-10.0", "max_score": "100.0"},  # Negative score
        {"student_id": "STU-001", "course_id": "DATA-101", "assignment_id": "A2", "due_date": "2026-09-20 23:59:00", "submitted_at": "2026-09-19 10:00:00", "score": "120.0", "max_score": "100.0"},  # Score > max
        {"student_id": "STU-999", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10", "submitted_at": "2026-09-09", "score": "80", "max_score": "100"},  # Invalid FK
        {"student_id": "STU-001", "course_id": "DATA-101", "assignment_id": "A1", "due_date": "2026-09-10", "submitted_at": "2026-09-09", "score": "95", "max_score": "100"},  # Duplicate assignment
    ])
    assessments = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "assessment_date": "2026-10-01", "assessment_type": "Quiz 1", "score": "-5.0", "max_score": "100.0"},
        {"student_id": "STU-001", "course_id": "DATA-101", "assessment_date": "2026-10-15", "assessment_type": "Midterm", "score": "110.0", "max_score": "100.0"},
        {"student_id": "STU-002", "course_id": "DATA-101", "assessment_date": "2026-10-01", "assessment_type": "Quiz 1", "score": None, "max_score": "100.0"},
        {"student_id": "STU-999", "course_id": "DATA-101", "assessment_date": "2026-10-01", "assessment_type": "Quiz 1", "score": "80", "max_score": "100"},
    ])
    interventions = pd.DataFrame([
        {"student_id": "STU-001", "course_id": "DATA-101", "action_date": "2026-09-15", "action_type": "Email Reminder", "outcome_note": "Sent reminder"},
        {"student_id": "STU-999", "course_id": "DATA-101", "action_date": "2026-09-15", "action_type": "Call", "outcome_note": "No answer"},
    ])
    return {
        "students": students,
        "enrolments": enrolments,
        "attendance": attendance,
        "assignments": assignments,
        "assessments": assessments,
        "interventions": interventions,
    }


def test_clean_and_transform_students(raw_sample_data):
    """Verifies whitespace stripping, cohort fallback, and deduplication for students."""
    cleaned = clean_and_transform_data(raw_sample_data)
    students = cleaned.students

    assert len(students) == 2
    assert set(students["student_id"]) == {"STU-001", "STU-002"}
    assert students.loc[students["student_id"] == "STU-001", "program"].iloc[0] == "Data Science"
    assert students.loc[students["student_id"] == "STU-002", "cohort_year"].iloc[0] == 2026


def test_clean_and_transform_enrolments(raw_sample_data):
    """Verifies foreign key filtering and deduplication for enrolments."""
    cleaned = clean_and_transform_data(raw_sample_data)
    enrolments = cleaned.enrolments

    assert len(enrolments) == 1
    assert enrolments.iloc[0]["student_id"] == "STU-001"
    assert enrolments.iloc[0]["course_id"] == "DATA-101"
    assert enrolments.iloc[0]["term"] == "Fall 2026"
    assert enrolments.iloc[0]["section"] == "A"


def test_clean_and_transform_attendance(raw_sample_data):
    """Verifies attendance date parsing, status capitalization, invalid enum dropping, and deduplication."""
    cleaned = clean_and_transform_data(raw_sample_data)
    attendance = cleaned.attendance

    assert len(attendance) == 2
    statuses = set(attendance["attendance_status"])
    assert statuses == {"Present", "Late"}
    assert all(attendance["student_id"] == "STU-001")


def test_clean_and_transform_assignments(raw_sample_data):
    """Verifies score bounding [0, max_score] and deduplication for assignments."""
    cleaned = clean_and_transform_data(raw_sample_data)
    assignments = cleaned.assignments

    assert len(assignments) == 2
    a1 = assignments[assignments["assignment_id"] == "A1"].iloc[0]
    a2 = assignments[assignments["assignment_id"] == "A2"].iloc[0]

    assert a1["score"] == 0.0  # Clipped from -10.0
    assert a2["score"] == 100.0  # Clipped from 120.0 to max_score (100.0)


def test_clean_and_transform_assessments(raw_sample_data):
    """Verifies assessment score bounds, null filling to 0.0, and foreign key filtering."""
    cleaned = clean_and_transform_data(raw_sample_data)
    assessments = cleaned.assessments

    assert len(assessments) == 3
    q1_stu1 = assessments[(assessments["student_id"] == "STU-001") & (assessments["assessment_type"] == "Quiz 1")].iloc[0]
    mid_stu1 = assessments[(assessments["student_id"] == "STU-001") & (assessments["assessment_type"] == "Midterm")].iloc[0]
    q1_stu2 = assessments[(assessments["student_id"] == "STU-002") & (assessments["assessment_type"] == "Quiz 1")].iloc[0]

    assert q1_stu1["score"] == 0.0
    assert mid_stu1["score"] == 100.0
    assert q1_stu2["score"] == 0.0


def test_clean_and_transform_interventions(raw_sample_data):
    """Verifies foreign key filtering and default staff_user assignment."""
    cleaned = clean_and_transform_data(raw_sample_data)
    interventions = cleaned.interventions

    assert len(interventions) == 1
    assert interventions.iloc[0]["student_id"] == "STU-001"
    assert interventions.iloc[0]["staff_user"] == "academic_advisor"


def test_clean_and_transform_empty_data():
    """Verifies transformation handles empty dictionaries without error."""
    cleaned = clean_and_transform_data({})
    assert isinstance(cleaned, CleanedDatasets)
    assert cleaned.students.empty
    assert cleaned.enrolments.empty
    assert cleaned.attendance.empty
    assert cleaned.assignments.empty
    assert cleaned.assessments.empty
    assert cleaned.interventions.empty
