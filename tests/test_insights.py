"""
Unit tests for Dynamic Cohort Insights Generator.
Tests data-driven finding derivation, fallback states, and ranking.
"""

import pandas as pd
import pytest
from src.insights import generate_cohort_insights, InsightFinding


def test_generate_cohort_insights_empty():
    """Verifies that empty DataFrames return informative fallback insights."""
    empty_features = pd.DataFrame()
    empty_risk = pd.DataFrame()
    findings = generate_cohort_insights(empty_features, empty_risk)

    assert isinstance(findings, list)
    assert len(findings) == 3
    assert all(isinstance(f, InsightFinding) for f in findings)
    assert findings[0].title == "Cohort Baseline"
    assert findings[1].title == "Data Synchronization"
    assert findings[2].title == "Advisory Guidance"


def test_generate_cohort_insights_valid():
    """Verifies dynamic insight generation from synthetic student metrics."""
    features_df = pd.DataFrame({
        "student_id": ["STU-1", "STU-2", "STU-3", "STU-4", "STU-5"],
        "course_id": ["CS-101", "CS-101", "CS-101", "CS-101", "CS-101"],
        "term": ["Fall 2026"] * 5,
        "section": ["Section A", "Section A", "Section B", "Section B", "Section B"],
        "attendance_rate": [45.0, 55.0, 95.0, 90.0, 88.0],
        "submission_completion_rate": [50.0, 60.0, 100.0, 95.0, 90.0],
        "missing_assignments": [3, 2, 0, 0, 0],
        "assignment_average": [40.0, 48.0, 90.0, 85.0, 82.0],
        "assessment_average": [35.0, 45.0, 92.0, 88.0, 80.0],
        "engagement_trend": ["declining", "declining", "stable", "stable", "improving"],
        "risk_level": ["High", "High", "Low", "Low", "Low"],
        "risk_score": [80, 75, 0, 5, 0],
    })
    risk_df = features_df[["student_id", "course_id", "term", "risk_level", "risk_score"]].copy()

    findings = generate_cohort_insights(features_df, risk_df)

    assert len(findings) == 3
    assert any(f.title in ["Section Variance", "Course Disparity", "Cohort Risk Profile", "Section Risk Concentration"] for f in findings)
    assert any(f.title == "Primary Risk Indicator" for f in findings)
    assert any(f.title in ["Recency Anomaly", "Positive Trajectory", "Support Indicator Note", "Engagement Stability"] for f in findings)


def test_generate_cohort_insights_section_filter():
    """Verifies section-specific insights when filtered by section."""
    features_df = pd.DataFrame({
        "student_id": ["STU-1", "STU-2"],
        "course_id": ["CS-101", "CS-101"],
        "term": ["Fall 2026"] * 2,
        "section": ["Section A", "Section A"],
        "attendance_rate": [45.0, 55.0],
        "submission_completion_rate": [50.0, 60.0],
        "missing_assignments": [3, 2],
        "assignment_average": [40.0, 48.0],
        "assessment_average": [35.0, 45.0],
        "engagement_trend": ["declining", "declining"],
        "risk_level": ["High", "High"],
        "risk_score": [80, 75],
    })
    risk_df = features_df[["student_id", "course_id", "term", "risk_level", "risk_score"]].copy()

    findings = generate_cohort_insights(features_df, risk_df, selected_section="Section A")

    assert len(findings) == 3
    assert findings[0].title == "Section Risk Concentration"
    assert "Section Section A" in findings[0].headline
