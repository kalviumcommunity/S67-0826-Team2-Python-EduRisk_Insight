"""
Unit tests for StudentPulse AI Risk Engine & Scoring Rules.
Tests transparent point accumulation, risk band classification, and explainability.
"""

from pathlib import Path
import json
import pandas as pd
import pytest

from src.risk_rules import RiskEngine, StudentRiskEvaluation


@pytest.fixture
def risk_engine():
    """Initializes a RiskEngine instance with default threshold configurations."""
    return RiskEngine(config_path=Path("config/risk_thresholds.yaml"))


def test_risk_engine_evaluates_on_track_student(risk_engine):
    """Tests evaluation of an engaged student (100% attendance, no missing work, high grades)."""
    student_row = pd.Series({
        "student_id": "STU-GOOD",
        "course_id": "DATA-101",
        "term": "Fall 2026",
        "attendance_rate": 95.0,
        "recent_attendance_rate": 95.0,
        "submission_completion_rate": 100.0,
        "missing_assignments": 0,
        "late_submission_rate": 0.0,
        "assignment_average": 88.0,
        "assessment_average": 90.0,
    })
    eval_res = risk_engine.evaluate_student(student_row)
    
    assert isinstance(eval_res, StudentRiskEvaluation)
    assert eval_res.risk_score == 0
    assert eval_res.risk_level == "Low"
    assert eval_res.support_level_name == "On Track"
    assert len(eval_res.reasons) == 0


def test_risk_engine_evaluates_high_risk_student(risk_engine):
    """Tests evaluation of a student with concurrent attendance and submission drop-off."""
    student_row = pd.Series({
        "student_id": "STU-CRITICAL",
        "course_id": "DATA-101",
        "term": "Fall 2026",
        "attendance_rate": 55.0,            # +3 pts (Attendance below 70%)
        "recent_attendance_rate": 40.0,     # +2 pts (Drop >= 15 pts)
        "submission_completion_rate": 60.0, # +3 pts (Completion below 80%)
        "missing_assignments": 2,           # +3 pts (Missing >= 2)
        "late_submission_rate": 50.0,       # +1 pt  (Late > 30%)
        "assignment_average": 45.0,         # +3 pts (Performance below 50%)
        "assessment_average": 40.0,
    })
    eval_res = risk_engine.evaluate_student(student_row)
    
    assert eval_res.risk_score >= 6
    assert eval_res.risk_level == "High"
    assert eval_res.support_level_name == "Needs Review"
    assert len(eval_res.reasons) >= 4

    reason_codes = {r.code for r in eval_res.reasons}
    assert "LOW_ATTENDANCE" in reason_codes
    assert "MISSING_ASSIGNMENTS" in reason_codes
    assert "LOW_ACADEMIC_PERFORMANCE" in reason_codes


def test_risk_engine_evaluates_watch_student(risk_engine):
    """Tests evaluation of a medium-risk student (score 3-5 pts)."""
    student_row = pd.Series({
        "student_id": "STU-WATCH",
        "course_id": "DATA-101",
        "term": "Fall 2026",
        "attendance_rate": 65.0,            # +3 pts
        "recent_attendance_rate": 65.0,
        "submission_completion_rate": 90.0,
        "missing_assignments": 0,
        "late_submission_rate": 0.0,
        "assignment_average": 75.0,
        "assessment_average": 75.0,
    })
    eval_res = risk_engine.evaluate_student(student_row)
    
    assert eval_res.risk_score == 3
    assert eval_res.risk_level == "Medium"
    assert eval_res.support_level_name == "Watch"


def test_risk_engine_evaluates_dataframe(risk_engine):
    """Tests batch DataFrame evaluation producing serialized reasons_json."""
    features_df = pd.DataFrame([
        {
            "student_id": "STU-001",
            "course_id": "DATA-101",
            "term": "Fall 2026",
            "attendance_rate": 95.0,
            "recent_attendance_rate": 95.0,
            "submission_completion_rate": 100.0,
            "missing_assignments": 0,
            "late_submission_rate": 0.0,
            "assignment_average": 85.0,
            "assessment_average": 85.0,
        },
        {
            "student_id": "STU-002",
            "course_id": "DATA-101",
            "term": "Fall 2026",
            "attendance_rate": 50.0,
            "recent_attendance_rate": 50.0,
            "submission_completion_rate": 50.0,
            "missing_assignments": 3,
            "late_submission_rate": 40.0,
            "assignment_average": 40.0,
            "assessment_average": 40.0,
        }
    ])
    risk_df = risk_engine.evaluate_features_dataframe(features_df)
    
    assert len(risk_df) == 2
    assert "reasons_json" in risk_df.columns
    assert "risk_score" in risk_df.columns
    assert "risk_level" in risk_df.columns
    
    # Check JSON deserializability
    reasons_stu2 = json.loads(risk_df.iloc[1]["reasons_json"])
    assert isinstance(reasons_stu2, list)
    assert len(reasons_stu2) > 0
