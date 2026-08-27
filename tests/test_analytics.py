"""
Unit tests for StudentPulse AI Analytics Engine.
Tests statistical profiling (LU 2.28, LU 2.32), cohort disparity analysis (LU 2.6, LU 2.30),
temporal trend analysis (LU 2.29), and student behaviour analytics (LU 2.31, LU 2.32).
"""

import pandas as pd
import pytest

from analytics.behaviour_analysis import (
    analyze_submission_behaviour,
    detect_consecutive_absence_streaks,
    generate_behavioural_profile,
)
from analytics.cohort_analysis import analyze_cohort_disparities
from analytics.profiling import generate_cohort_profile
from analytics.trend_analysis import (
    compute_student_trend_trajectories,
    compute_weekly_trends,
)


@pytest.fixture
def sample_features_df():
    """Provides a sample student features DataFrame."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004", "S005"],
        "course_id": ["CS101", "CS101", "CS101", "MATH201", "MATH201"],
        "term": ["Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026", "Fall 2026"],
        "attendance_rate": [90.0, 70.0, 50.0, 85.0, 60.0],
        "submission_completion_rate": [100.0, 75.0, 40.0, 90.0, 50.0],
        "late_submission_rate": [0.0, 35.0, 60.0, 0.0, 40.0],
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


@pytest.fixture
def sample_attendance_df():
    """Provides longitudinal attendance records for trend and streak testing."""
    return pd.DataFrame({
        "student_id": [
            "S001", "S001", "S001", "S001",
            "S002", "S002", "S002", "S002",
            "S003", "S003", "S003", "S003",
        ],
        "course_id": ["CS101"] * 12,
        "session_date": [
            "2026-09-01", "2026-09-08", "2026-09-15", "2026-09-22",
            "2026-09-01", "2026-09-08", "2026-09-15", "2026-09-22",
            "2026-09-01", "2026-09-08", "2026-09-15", "2026-09-22",
        ],
        "attendance_status": [
            "Present", "Present", "Present", "Present",
            "Present", "Absent", "Absent", "Absent",
            "Absent", "Late", "Present", "Present",
        ],
    })


@pytest.fixture
def sample_assignments_df():
    """Provides assignment submission records for behavior testing."""
    return pd.DataFrame({
        "assignment_id": [1, 2, 3, 4, 5, 6],
        "student_id": ["S001", "S001", "S002", "S002", "S003", "S003"],
        "course_id": ["CS101"] * 6,
        "due_date": [
            "2026-09-05", "2026-09-12",
            "2026-09-05", "2026-09-12",
            "2026-09-05", "2026-09-12",
        ],
        "submitted_at": [
            "2026-09-04 10:00:00", "2026-09-11 15:00:00",  # On-time
            "2026-09-07 10:00:00", "2026-09-14 10:00:00",  # Late
            None, None,                                    # Missing
        ],
        "score": [95.0, 90.0, 70.0, 65.0, None, None],
        "max_score": [100.0] * 6,
    })


# -------------------------------------------------------------
# Profiling & Disparity Tests (LU 2.28, 2.30, 2.32)
# -------------------------------------------------------------

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
    features_with_section = sample_features_df.copy()
    features_with_section["section"] = ["A", "A", "B", "A", "A"]

    disparities = analyze_cohort_disparities(features_with_section, sample_risk_df)

    assert isinstance(disparities, pd.DataFrame)
    assert not disparities.empty
    assert len(disparities) == 3

    cols = disparities.columns.tolist()
    assert "course_id" in cols
    assert "section" in cols
    assert "total_students" in cols
    assert "high_risk_count" in cols
    assert "high_risk_pct" in cols
    assert "avg_attendance" in cols

    cs101_b = disparities[(disparities["course_id"] == "CS101") & (disparities["section"] == "B")].iloc[0]
    assert cs101_b["total_students"] == 1
    assert cs101_b["high_risk_count"] == 1
    assert cs101_b["high_risk_pct"] == 100.0


def test_analyze_cohort_disparities_empty():
    """Verifies disparity analysis handles empty inputs."""
    res = analyze_cohort_disparities(pd.DataFrame(), pd.DataFrame())
    assert isinstance(res, pd.DataFrame)
    assert res.empty


# -------------------------------------------------------------
# Trend Analysis Tests (LU 2.29, LU 2.32)
# -------------------------------------------------------------

def test_compute_weekly_trends_valid(sample_attendance_df, sample_assignments_df):
    """Verifies weekly attendance and submission aggregation with week-over-week deltas."""
    trends = compute_weekly_trends(sample_attendance_df, sample_assignments_df)

    assert isinstance(trends, pd.DataFrame)
    assert not trends.empty
    assert "week" in trends.columns
    assert "attendance_rate" in trends.columns
    assert "submission_rate" in trends.columns
    assert "attendance_delta" in trends.columns
    assert "submission_delta" in trends.columns
    assert trends.iloc[0]["week"] == "Week 1"


def test_compute_weekly_trends_course_filter(sample_attendance_df, sample_assignments_df):
    """Verifies course filtering in weekly trend computation."""
    trends_cs = compute_weekly_trends(sample_attendance_df, sample_assignments_df, course_id="CS101")
    assert not trends_cs.empty

    trends_other = compute_weekly_trends(sample_attendance_df, sample_assignments_df, course_id="NONEXISTENT")
    assert trends_other.empty


def test_compute_weekly_trends_empty():
    """Verifies weekly trends handles empty data gracefully."""
    trends = compute_weekly_trends(pd.DataFrame(), pd.DataFrame())
    assert isinstance(trends, pd.DataFrame)
    assert trends.empty


def test_compute_student_trend_trajectories_valid(sample_attendance_df):
    """Verifies student velocity and trajectory classification."""
    as_of = pd.to_datetime("2026-09-23")
    trajectories = compute_student_trend_trajectories(sample_attendance_df, as_of_date=as_of, window_days=14)

    assert isinstance(trajectories, pd.DataFrame)
    assert len(trajectories) == 3
    assert "trajectory" in trajectories.columns
    assert "net_change" in trajectories.columns

    s001 = trajectories[trajectories["student_id"] == "S001"].iloc[0]
    assert s001["recent_rate"] == 100.0


def test_compute_student_trend_trajectories_empty():
    """Verifies trajectory analysis handles empty input."""
    res = compute_student_trend_trajectories(pd.DataFrame())
    assert isinstance(res, pd.DataFrame)
    assert res.empty


# -------------------------------------------------------------
# Behaviour Analysis Tests (LU 2.31, LU 2.32)
# -------------------------------------------------------------

def test_analyze_submission_behaviour_valid(sample_assignments_df):
    """Verifies student submission turnaround and punctuality profiling."""
    behaviour = analyze_submission_behaviour(sample_assignments_df)

    assert isinstance(behaviour, pd.DataFrame)
    assert len(behaviour) == 3

    s001 = behaviour[behaviour["student_id"] == "S001"].iloc[0]
    assert s001["on_time_rate"] == 100.0
    assert s001["behaviour_flag"] == "Punctual"

    s002 = behaviour[behaviour["student_id"] == "S002"].iloc[0]
    assert s002["late_rate"] == 100.0
    assert s002["behaviour_flag"] == "Habitual Late"

    s003 = behaviour[behaviour["student_id"] == "S003"].iloc[0]
    assert s003["missing_count"] == 2
    assert s003["behaviour_flag"] == "High Missing Risk"


def test_analyze_submission_behaviour_empty():
    """Verifies behaviour analysis handles empty DataFrame."""
    res = analyze_submission_behaviour(pd.DataFrame())
    assert isinstance(res, pd.DataFrame)
    assert res.empty


def test_detect_consecutive_absence_streaks(sample_attendance_df):
    """Verifies consecutive unexcused absence streak detection."""
    streaks = detect_consecutive_absence_streaks(sample_attendance_df, threshold=3)

    assert isinstance(streaks, pd.DataFrame)
    assert len(streaks) == 3

    # S002 had 3 consecutive absences
    s002 = streaks[streaks["student_id"] == "S002"].iloc[0]
    assert s002["max_consecutive_absences"] == 3
    assert bool(s002["is_streak_critical"]) is True

    # S001 had 0 absences
    s001 = streaks[streaks["student_id"] == "S001"].iloc[0]
    assert s001["max_consecutive_absences"] == 0
    assert bool(s001["is_streak_critical"]) is False


def test_detect_consecutive_absence_streaks_empty():
    """Verifies streak detection handles empty input."""
    res = detect_consecutive_absence_streaks(pd.DataFrame())
    assert isinstance(res, pd.DataFrame)
    assert res.empty


def test_generate_behavioural_profile(sample_features_df, sample_assignments_df):
    """Verifies generation of cohort behavioural summary profile."""
    behaviour_df = analyze_submission_behaviour(sample_assignments_df)
    profile = generate_behavioural_profile(sample_features_df, behaviour_df)

    assert isinstance(profile, dict)
    assert profile["cohort_size"] == 5
    assert "chronic_absenteeism_rate" in profile
    assert "missing_work_risk_rate" in profile
    assert "habitual_late_rate" in profile
    assert "behaviour_flag_distribution" in profile


def test_generate_behavioural_profile_empty():
    """Verifies profile generation handles empty input."""
    profile = generate_behavioural_profile(pd.DataFrame())
    assert profile == {}
