"""
StudentPulse AI - Temporal Trend Analysis Module
Computes longitudinal engagement trends, weekly dynamics, and trajectory velocity.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def compute_weekly_trends(
    attendance_df: Optional[pd.DataFrame] = None,
    assignments_df: Optional[pd.DataFrame] = None,
    course_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Aggregates weekly attendance and assignment submission metrics across the cohort.
    
    Args:
        attendance_df: DataFrame of cleaned attendance logs.
        assignments_df: DataFrame of cleaned assignment records.
        course_id: Optional course_id filter.
        
    Returns:
        DataFrame with weekly attendance rates, submission rates, and week-over-week deltas.
    """
    att = attendance_df.copy() if attendance_df is not None and not attendance_df.empty else pd.DataFrame()
    asg = assignments_df.copy() if assignments_df is not None and not assignments_df.empty else pd.DataFrame()

    if course_id and course_id != "All":
        if not att.empty and "course_id" in att.columns:
            att = att[att["course_id"] == course_id]
        if not asg.empty and "course_id" in asg.columns:
            asg = asg[asg["course_id"] == course_id]

    # Weekly attendance aggregation
    weekly_att = pd.DataFrame()
    if not att.empty and "session_date" in att.columns:
        att["session_date"] = pd.to_datetime(att["session_date"])
        att["week_start"] = att["session_date"].dt.to_period("W").apply(lambda r: r.start_time)
        att["is_present"] = (att["attendance_status"] == "Present").astype(int)
        att["is_late"] = (att["attendance_status"] == "Late").astype(int)
        att["is_excused"] = (att["attendance_status"] == "Excused").astype(int)

        att_grouped = att.groupby("week_start").agg(
            total_records=("session_date", "count"),
            present_records=("is_present", "sum"),
            late_records=("is_late", "sum"),
            excused_records=("is_excused", "sum"),
        ).reset_index()

        eff_records = np.maximum(att_grouped["total_records"] - att_grouped["excused_records"], 0)
        att_grouped["attendance_rate"] = np.where(
            eff_records > 0,
            ((att_grouped["present_records"] + 0.5 * att_grouped["late_records"]) / eff_records * 100.0).round(1),
            100.0,
        )
        weekly_att = att_grouped[["week_start", "total_records", "attendance_rate"]]

    # Weekly assignment submission aggregation
    weekly_asg = pd.DataFrame()
    if not asg.empty and "due_date" in asg.columns:
        asg["due_date"] = pd.to_datetime(asg["due_date"])
        asg["week_start"] = asg["due_date"].dt.to_period("W").apply(lambda r: r.start_time)
        asg["is_submitted"] = asg["submitted_at"].notna().astype(int)

        asg_grouped = asg.groupby("week_start").agg(
            due_count=("assignment_id", "count"),
            submitted_count=("is_submitted", "sum"),
        ).reset_index()

        asg_grouped["submission_rate"] = np.where(
            asg_grouped["due_count"] > 0,
            (asg_grouped["submitted_count"] / asg_grouped["due_count"] * 100.0).round(1),
            100.0,
        )
        weekly_asg = asg_grouped[["week_start", "due_count", "submission_rate"]]

    # Merge attendance and assignment trends
    if weekly_att.empty and weekly_asg.empty:
        return pd.DataFrame(columns=[
            "week", "week_start", "attendance_rate", "submission_rate",
            "attendance_delta", "submission_delta"
        ])

    if not weekly_att.empty and not weekly_asg.empty:
        merged = pd.merge(weekly_att, weekly_asg, on="week_start", how="outer").sort_values(by="week_start")
    elif not weekly_att.empty:
        merged = weekly_att.sort_values(by="week_start")
        merged["due_count"] = 0
        merged["submission_rate"] = 100.0
    else:
        merged = weekly_asg.sort_values(by="week_start")
        merged["total_records"] = 0
        merged["attendance_rate"] = 100.0

    merged["attendance_rate"] = merged["attendance_rate"].ffill().bfill().fillna(100.0)
    merged["submission_rate"] = merged["submission_rate"].ffill().bfill().fillna(100.0)

    # Week label formatting
    merged["week"] = [f"Week {i+1}" for i in range(len(merged))]

    # Week-over-week deltas
    merged["attendance_delta"] = merged["attendance_rate"].diff().fillna(0.0).round(1)
    merged["submission_delta"] = merged["submission_rate"].diff().fillna(0.0).round(1)

    return merged.reset_index(drop=True)


def compute_student_trend_trajectories(
    attendance_df: pd.DataFrame,
    as_of_date: Optional[pd.Timestamp] = None,
    window_days: int = 14,
) -> pd.DataFrame:
    """
    Computes individual student velocity and trajectory category (improving, stable, declining).
    
    Args:
        attendance_df: DataFrame of attendance records with session_date.
        as_of_date: Reference date for trajectory calculation.
        window_days: Number of recent days to define the recent window.
        
    Returns:
        DataFrame containing student-course prior rate, recent rate, net change, and trajectory label.
    """
    if attendance_df.empty or "session_date" not in attendance_df.columns:
        return pd.DataFrame(columns=[
            "student_id", "course_id", "prior_rate", "recent_rate", "net_change", "trajectory"
        ])

    att = attendance_df.copy()
    att["session_date"] = pd.to_datetime(att["session_date"])

    if as_of_date is None:
        as_of_date = att["session_date"].max()

    recent_cutoff = as_of_date - pd.Timedelta(days=window_days)

    att["is_present"] = (att["attendance_status"] == "Present").astype(int)
    att["is_late"] = (att["attendance_status"] == "Late").astype(int)
    att["is_excused"] = (att["attendance_status"] == "Excused").astype(int)
    att["is_recent"] = (att["session_date"] >= recent_cutoff).astype(int)
    att["is_prior"] = (att["session_date"] < recent_cutoff).astype(int)

    grouped = att.groupby(["student_id", "course_id"]).agg(
        recent_total=("is_recent", "sum"),
        recent_present=("is_present", lambda x: (x * att.loc[x.index, "is_recent"]).sum()),
        recent_late=("is_late", lambda x: (x * att.loc[x.index, "is_recent"]).sum()),
        recent_excused=("is_excused", lambda x: (x * att.loc[x.index, "is_recent"]).sum()),
        prior_total=("is_prior", "sum"),
        prior_present=("is_present", lambda x: (x * att.loc[x.index, "is_prior"]).sum()),
        prior_late=("is_late", lambda x: (x * att.loc[x.index, "is_prior"]).sum()),
        prior_excused=("is_excused", lambda x: (x * att.loc[x.index, "is_prior"]).sum()),
    ).reset_index()

    rec_eff = np.maximum(grouped["recent_total"] - grouped["recent_excused"], 0)
    grouped["recent_rate"] = np.where(
        rec_eff > 0,
        ((grouped["recent_present"] + 0.5 * grouped["recent_late"]) / rec_eff * 100.0).round(1),
        100.0,
    )

    prior_eff = np.maximum(grouped["prior_total"] - grouped["prior_excused"], 0)
    grouped["prior_rate"] = np.where(
        prior_eff > 0,
        ((grouped["prior_present"] + 0.5 * grouped["prior_late"]) / prior_eff * 100.0).round(1),
        grouped["recent_rate"],
    )

    grouped["net_change"] = (grouped["recent_rate"] - grouped["prior_rate"]).round(1)

    conditions = [
        (grouped["recent_total"] < 2) & (grouped["prior_total"] < 2),
        grouped["net_change"] <= -15.0,
        grouped["net_change"] >= 10.0,
    ]
    choices = ["insufficient_data", "declining", "improving"]
    grouped["trajectory"] = np.select(conditions, choices, default="stable")

    cols = ["student_id", "course_id", "prior_rate", "recent_rate", "net_change", "trajectory"]
    return grouped[cols]
