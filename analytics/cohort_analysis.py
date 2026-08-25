"""
StudentPulse AI - Cohort Analysis Module
Compares cross-sectional performance across departments, programs, courses, and sections.
"""

from typing import Dict
import pandas as pd


def analyze_cohort_disparities(features_df: pd.DataFrame, risk_df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs cross-course and cross-section comparative risk rate breakdown.
    
    Args:
        features_df: Features table.
        risk_df: Risk table.
        
    Returns:
        Summary DataFrame aggregated by course_id and section.
    """
    if features_df.empty or risk_df.empty:
        return pd.DataFrame()

    join_keys = ["student_id", "course_id", "term"]
    if "section" in features_df.columns and "section" in risk_df.columns:
        join_keys.append("section")

    merged = pd.merge(features_df, risk_df, on=join_keys, how="inner")

    if "section" not in merged.columns:
        if "section_x" in merged.columns:
            merged["section"] = merged["section_x"]
        elif "section_y" in merged.columns:
            merged["section"] = merged["section_y"]
        else:
            merged["section"] = "Default"
    
    grouped = merged.groupby(["course_id", "section"]).agg(
        total_students=("student_id", "nunique"),
        high_risk_count=("risk_level", lambda x: (x == "High").sum()),
        medium_risk_count=("risk_level", lambda x: (x == "Medium").sum()),
        low_risk_count=("risk_level", lambda x: (x == "Low").sum()),
        avg_attendance=("attendance_rate", "mean"),
        avg_submission_completion=("submission_completion_rate", "mean"),
        avg_assessment=("assessment_average", "mean"),
    ).reset_index()

    grouped["high_risk_pct"] = (grouped["high_risk_count"] / grouped["total_students"] * 100.0).round(1)
    grouped["avg_attendance"] = grouped["avg_attendance"].round(1)
    grouped["avg_submission_completion"] = grouped["avg_submission_completion"].round(1)
    grouped["avg_assessment"] = grouped["avg_assessment"].round(1)

    return grouped.sort_values(by="high_risk_pct", ascending=False)
