"""
Unit tests for StudentPulse AI Analytics Engine.
Tests statistical profiling (LU 2.28, LU 2.32) and cohort disparity analysis (LU 2.6, LU 2.30).
"""

import pandas as pd
import pytest
from analytics.cohort_analysis import analyze_cohort_disparities
from analytics.profiling import generate_cohort_profile


@pytest.fixture
def sample_features_df():
    """Provides a sample student features DataFrame."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004", "S005"],
        "course_id": ["CS101", "CS101", "CS101", "MATH201", "MATH201"],
        "term": ["Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026"],
        "attendance_rate": [90.0, 70.0, 50.0, 85.0, 60.0],
        "submission_completion_rate": [100.0, 75.0, 40.0, 90.0, 50.0],
        "assessment_average": [88.5, 72.0, 45.0, 82.0, 58.0],
        "missing_assignments": [0, 1, 3, 0, 2],
        "engagement_trend": ["improving", "stable", "declining", "stable", "declining"]
    })


@pytest.fixture
def sample_risk_df():
    """Provides a sample student risk evaluations DataFrame."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004", "S005"],
        "course_id": ["CS101", "CS101", "CS101", "MATH201", "MATH201"],
        "term": ["Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026"],
        "section": ["A", "A", "B", "A", "A"],
        "risk_score": [10, 45, 80, 20, 75],
        "risk_level": ["Low", "Medium", "High", "Low", "High"]
    })


def test_generate_cohort_profile_valid(sample_features_df):
    """Verifies statistical profiling calculations across cohorts."""
    profile = generate_cohort_profile(sample_features_df)

    assert profile["record_count"] == 5
    assert profile["unique_students"] == 5
    assert profile["unique_courses"] == 2

    # Attendance stats
    attendance = profile["attendance"]
    assert attendance["mean"] == pytest.approx(71.0, 0.1)
    assert attendance["min"] == 50.0
    assert attendance["max"] == 90.0
    assert attendance["median"] == 70.0

    # Submission stats
    submissions = profile["submission_completion"]
    assert submissions["mean"] == pytest.approx(71.0, 0.1)
    assert "p25" in submissions
    assert "p75" in submissions

    # Distributions
    assert profile["missing_assignments_distribution"][0] == 2
    assert profile["missing_assignments_distribution"][3] == 1
    assert profile["engagement_trend_distribution"]["declining"] == 2


def test_generate_cohort_profile_empty():
    """Verifies profiling gracefully handles empty DataFrames."""
    profile = generate_cohort_profile(pd.DataFrame())
    assert profile == {}


def test_generate_cohort_profile_single_row():
    """Verifies profiling handles single-row DataFrames without std errors."""
    single_df = pd.DataFrame({
        "student_id": ["S001"],
        "course_id": ["CS101"],
        "term": ["Fall 2026"],
        "attendance_rate": [85.0],
        "submission_completion_rate": [90.0],
        "assessment_average": [80.0],
        "missing_assignments": [0],
        "engagement_trend": ["stable"]
    })
    profile = generate_cohort_profile(single_df)
    assert profile["record_count"] == 1
    assert profile["attendance"]["std"] == 0.0


def test_analyze_cohort_disparities_valid(sample_features_df, sample_risk_df):
    """Verifies cross-sectional cohort disparity aggregation."""
    # Add section to sample_features_df as expected in merge
    features_with_section = sample_features_df.copy()
    features_with_section["section"] = ["A", "A", "B", "A", "A"]

    disparities = analyze_cohort_disparities(features_with_section, sample_risk_df)

    assert isinstance(disparities, pd.DataFrame)
    assert not disparities.empty
    assert len(disparities) == 3  # (CS101, A), (CS101, B), (MATH201, A)

    cols = disparities.columns.tolist()
    assert "course_id" in cols
    assert "section" in cols
    assert "total_students" in cols
    assert "high_risk_count" in cols
    assert "high_risk_pct" in cols
    assert "avg_attendance" in cols

    # High risk pct checks
    cs101_b = disparities[(disparities["course_id"] == "CS101") & (disparities["section"] == "B")].iloc[0]
    assert cs101_b["total_students"] == 1
    assert cs101_b["high_risk_count"] == 1
    assert cs101_b["high_risk_pct"] == 100.0

    # Top entry should be sorted descending by high_risk_pct
    assert disparities.iloc[0]["high_risk_pct"] >= disparities.iloc[-1]["high_risk_pct"]


def test_analyze_cohort_disparities_empty():
    """Verifies disparity analysis handles empty inputs."""
    res = analyze_cohort_disparities(pd.DataFrame(), pd.DataFrame())
    assert isinstance(res, pd.DataFrame)
    assert res.empty
