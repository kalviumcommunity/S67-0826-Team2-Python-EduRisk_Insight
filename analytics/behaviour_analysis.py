"""
StudentPulse AI - Student Behaviour & Anomaly Analysis Module
Detects submission turnaround behaviors, chronic absence streaks, and disengagement signals.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def analyze_submission_behaviour(assignments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates assignment submission timeliness, turnaround delay, and behavioural flags per student.
    
    Args:
        assignments_df: DataFrame of student assignment records with submitted_at and due_date.
        
    Returns:
        DataFrame with per-student submission behavior metrics and risk category.
    """
    if assignments_df.empty or "due_date" not in assignments_df.columns:
        return pd.DataFrame(columns=[
            "student_id", "course_id", "total_assignments", "on_time_count", "late_count",
            "missing_count", "on_time_rate", "late_rate", "avg_delay_days", "behaviour_flag"
        ])

    asg = assignments_df.copy()
    asg["due_date"] = pd.to_datetime(asg["due_date"])
    asg["submitted_at"] = pd.to_datetime(asg["submitted_at"])

    asg["is_submitted"] = asg["submitted_at"].notna().astype(int)
    asg["is_late"] = (asg["is_submitted"] & (asg["submitted_at"] > asg["due_date"])).astype(int)
    asg["is_on_time"] = (asg["is_submitted"] & (asg["submitted_at"] <= asg["due_date"])).astype(int)
    asg["is_missing"] = asg["submitted_at"].isna().astype(int)

    # Delay in days (positive = late, negative = early)
    asg["delay_days"] = np.where(
        asg["is_submitted"] == 1,
        (asg["submitted_at"] - asg["due_date"]).dt.total_seconds() / 86400.0,
        np.nan,
    )

    grouped = asg.groupby(["student_id", "course_id"]).agg(
        total_assignments=("assignment_id", "count"),
        on_time_count=("is_on_time", "sum"),
        late_count=("is_late", "sum"),
        missing_count=("is_missing", "sum"),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index()

    grouped["avg_delay_days"] = grouped["avg_delay_days"].fillna(0.0).round(1)

    grouped["on_time_rate"] = np.where(
        grouped["total_assignments"] > 0,
        (grouped["on_time_count"] / grouped["total_assignments"] * 100.0).round(1),
        100.0,
    )
    grouped["late_rate"] = np.where(
        grouped["total_assignments"] > 0,
        (grouped["late_count"] / grouped["total_assignments"] * 100.0).round(1),
        0.0,
    )

    # Behaviour classification
    conditions = [
        grouped["missing_count"] >= 2,
        grouped["late_rate"] >= 50.0,
        grouped["late_rate"] > 0.0,
    ]
    choices = ["High Missing Risk", "Habitual Late", "Occasional Delay"]
    grouped["behaviour_flag"] = np.select(conditions, choices, default="Punctual")

    cols = [
        "student_id", "course_id", "total_assignments", "on_time_count", "late_count",
        "missing_count", "on_time_rate", "late_rate", "avg_delay_days", "behaviour_flag"
    ]
    return grouped[cols]


def detect_consecutive_absence_streaks(
    attendance_df: pd.DataFrame,
    threshold: int = 3,
) -> pd.DataFrame:
    """
    Identifies maximum and current consecutive absence streaks per student.
    
    Args:
        attendance_df: DataFrame of attendance records with session_date and attendance_status.
        threshold: Threshold for flagging critical absence streaks (default: 3).
        
    Returns:
        DataFrame with absence streak statistics per student-course.
    """
    if attendance_df.empty or "session_date" not in attendance_df.columns:
        return pd.DataFrame(columns=[
            "student_id", "course_id", "max_consecutive_absences",
            "current_absence_streak", "is_streak_critical"
        ])

    att = attendance_df.copy()
    att["session_date"] = pd.to_datetime(att["session_date"])
    att = att.sort_values(by=["student_id", "course_id", "session_date"])

    records = []
    for (s_id, c_id), group in att.groupby(["student_id", "course_id"]):
        max_streak = 0
        current_streak = 0
        running_streak = 0

        for status in group["attendance_status"]:
            if status == "Absent":
                running_streak += 1
                if running_streak > max_streak:
                    max_streak = running_streak
            elif status == "Excused":
                # Excused does not break streak but does not increment
                pass
            else:
                running_streak = 0

        # Current streak looks at trailing sessions
        trailing_statuses = group["attendance_status"].tolist()
        current_streak = 0
        for status in reversed(trailing_statuses):
            if status == "Absent":
                current_streak += 1
            elif status == "Excused":
                continue
            else:
                break

        records.append({
            "student_id": s_id,
            "course_id": c_id,
            "max_consecutive_absences": max_streak,
            "current_absence_streak": current_streak,
            "is_streak_critical": bool(max_streak >= threshold),
        })

    return pd.DataFrame(records)


def generate_behavioural_profile(
    features_df: pd.DataFrame,
    behaviour_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Computes cohort-level summary profile of behavioural indicators and submission habits.
    
    Args:
        features_df: DataFrame of student-course features.
        behaviour_df: Optional DataFrame of output from analyze_submission_behaviour.
        
    Returns:
        Dictionary with behavioural distribution metrics and anomaly rates.
    """
    if features_df.empty:
        return {}

    total = len(features_df)
    chronic_absent_count = int((features_df["attendance_rate"] < 70.0).sum())
    missing_work_count = int((features_df["missing_assignments"] >= 2).sum())
    late_submission_habit_count = int((features_df["late_submission_rate"] >= 30.0).sum())

    profile: Dict[str, Any] = {
        "cohort_size": total,
        "chronic_absenteeism_rate": round(chronic_absent_count / total * 100.0, 1) if total else 0.0,
        "missing_work_risk_rate": round(missing_work_count / total * 100.0, 1) if total else 0.0,
        "habitual_late_rate": round(late_submission_habit_count / total * 100.0, 1) if total else 0.0,
        "engagement_trend_counts": features_df["engagement_trend"].value_counts().to_dict(),
    }

    if behaviour_df is not None and not behaviour_df.empty and "behaviour_flag" in behaviour_df.columns:
        profile["behaviour_flag_distribution"] = behaviour_df["behaviour_flag"].value_counts().to_dict()

    return profile
