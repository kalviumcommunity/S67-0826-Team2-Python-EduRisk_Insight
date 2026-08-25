"""
StudentPulse AI - Dataset Profiling Module
Computes summary distributions, null profiles, and statistical metrics across cohorts.
"""

from typing import Any, Dict
import pandas as pd


def generate_cohort_profile(features_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes summary statistical profile across student-course feature metrics.
    
    Args:
        features_df: DataFrame of student-course features.
        
    Returns:
        Dictionary with quantiles, averages, and distributions.
    """
    if features_df.empty:
        return {}

    return {
        "record_count": len(features_df),
        "unique_students": int(features_df["student_id"].nunique()),
        "unique_courses": int(features_df["course_id"].nunique()),
        "attendance": {
            "mean": round(float(features_df["attendance_rate"].mean()), 1),
            "median": round(float(features_df["attendance_rate"].median()), 1),
            "std": round(float(features_df["attendance_rate"].std()), 1) if len(features_df) > 1 else 0.0,
            "min": round(float(features_df["attendance_rate"].min()), 1),
            "max": round(float(features_df["attendance_rate"].max()), 1),
        },
        "submission_completion": {
            "mean": round(float(features_df["submission_completion_rate"].mean()), 1),
            "median": round(float(features_df["submission_completion_rate"].median()), 1),
            "p25": round(float(features_df["submission_completion_rate"].quantile(0.25)), 1),
            "p75": round(float(features_df["submission_completion_rate"].quantile(0.75)), 1),
        },
        "missing_assignments_distribution": features_df["missing_assignments"].value_counts().to_dict(),
        "engagement_trend_distribution": features_df["engagement_trend"].value_counts().to_dict(),
    }
