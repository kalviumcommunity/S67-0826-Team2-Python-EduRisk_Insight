"""
StudentPulse AI - High-Performance Feature Engineering Engine
Vectorized computation of student-course engagement metrics, submission rates, performance, and trends.
"""

from dataclasses import dataclass
import datetime
import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.transform import CleanedDatasets

logger = logging.getLogger(__name__)


def compute_student_course_features(
    cleaned_data: CleanedDatasets,
    as_of_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Vectorized computation of all standard student-course feature metrics.
    
    Args:
        cleaned_data: CleanedDatasets containing cleaned tables.
        as_of_date: Reference date for recency calculations (defaults to max date in data).
        
    Returns:
        DataFrame with one row per student-course-term.
    """
    enrolments = cleaned_data.enrolments.copy()
    if enrolments.empty:
        return pd.DataFrame()

    attendance = cleaned_data.attendance.copy()
    assignments = cleaned_data.assignments.copy()
    assessments = cleaned_data.assessments.copy()

    # Determine reference date
    if as_of_date is None:
        dates = []
        if not attendance.empty and "session_date" in attendance.columns:
            dates.extend(attendance["session_date"].dropna().tolist())
        if not assignments.empty and "due_date" in assignments.columns:
            dates.extend(assignments["due_date"].dropna().tolist())
        if dates:
            as_of_date = pd.to_datetime(max(dates))
        else:
            as_of_date = pd.to_datetime(datetime.datetime.now(datetime.timezone.utc))

    recent_cutoff_date = as_of_date - pd.Timedelta(days=14)

    # -----------------------------------------------------------------
    # 1. Vectorized Attendance Aggregations
    # -----------------------------------------------------------------
    if not attendance.empty:
        attendance["is_present"] = (attendance["attendance_status"] == "Present").astype(int)
        attendance["is_late"] = (attendance["attendance_status"] == "Late").astype(int)
        attendance["is_absent"] = (attendance["attendance_status"] == "Absent").astype(int)
        attendance["is_excused"] = (attendance["attendance_status"] == "Excused").astype(int)
        attendance["is_recent"] = (attendance["session_date"] >= recent_cutoff_date).astype(int)
        attendance["is_prior"] = (attendance["session_date"] < recent_cutoff_date).astype(int)

        att_agg = attendance.groupby(["student_id", "course_id"]).agg(
            total_sessions=("session_date", "count"),
            present_sessions=("is_present", "sum"),
            late_sessions=("is_late", "sum"),
            absent_sessions=("is_absent", "sum"),
            excused_sessions=("is_excused", "sum"),
            recent_total=("is_recent", "sum"),
            recent_present=("is_present", lambda x: (x * attendance.loc[x.index, "is_recent"]).sum()),
            recent_late=("is_late", lambda x: (x * attendance.loc[x.index, "is_recent"]).sum()),
            recent_excused=("is_excused", lambda x: (x * attendance.loc[x.index, "is_recent"]).sum()),
            prior_total=("is_prior", "sum"),
            prior_present=("is_present", lambda x: (x * attendance.loc[x.index, "is_prior"]).sum()),
            prior_late=("is_late", lambda x: (x * attendance.loc[x.index, "is_prior"]).sum()),
            prior_excused=("is_excused", lambda x: (x * attendance.loc[x.index, "is_prior"]).sum()),
        ).reset_index()
    else:
        att_agg = pd.DataFrame(columns=[
            "student_id", "course_id", "total_sessions", "present_sessions", "late_sessions",
            "absent_sessions", "excused_sessions", "recent_total", "recent_present", "recent_late",
            "recent_excused", "prior_total", "prior_present", "prior_late", "prior_excused"
        ])

    # -----------------------------------------------------------------
    # 2. Vectorized Assignment Aggregations
    # -----------------------------------------------------------------
    if not assignments.empty:
        assignments["is_submitted"] = assignments["submitted_at"].notna().astype(int)
        assignments["is_due"] = (assignments["due_date"] <= as_of_date).astype(int)
        assignments["is_missing"] = ((assignments["due_date"] <= as_of_date) & assignments["submitted_at"].isna()).astype(int)
        assignments["is_late"] = (assignments["submitted_at"].notna() & (assignments["submitted_at"] > assignments["due_date"])).astype(int)
        assignments["valid_score"] = assignments["score"].fillna(0.0)
        assignments["valid_max"] = assignments["max_score"].fillna(100.0)

        asg_agg = assignments.groupby(["student_id", "course_id"]).agg(
            total_assignments=("assignment_id", "count"),
            submitted_assignments=("is_submitted", "sum"),
            due_assignments=("is_due", "sum"),
            missing_assignments=("is_missing", "sum"),
            late_assignments=("is_late", "sum"),
            sum_score=("valid_score", "sum"),
            sum_max_score=("valid_max", "sum"),
        ).reset_index()
    else:
        asg_agg = pd.DataFrame(columns=[
            "student_id", "course_id", "total_assignments", "submitted_assignments",
            "due_assignments", "missing_assignments", "late_assignments", "sum_score", "sum_max_score"
        ])

    # -----------------------------------------------------------------
    # 3. Vectorized Assessment Aggregations
    # -----------------------------------------------------------------
    if not assessments.empty:
        assessments["valid_score"] = assessments["score"].fillna(0.0)
        assessments["valid_max"] = assessments["max_score"].fillna(100.0)
        asm_agg = assessments.groupby(["student_id", "course_id"]).agg(
            total_assessments=("assessment_type", "count"),
            asm_sum_score=("valid_score", "sum"),
            asm_sum_max=("valid_max", "sum"),
        ).reset_index()
    else:
        asm_agg = pd.DataFrame(columns=["student_id", "course_id", "total_assessments", "asm_sum_score", "asm_sum_max"])

    # -----------------------------------------------------------------
    # 4. Merge onto Enrolments
    # -----------------------------------------------------------------
    merged = pd.merge(enrolments, att_agg, on=["student_id", "course_id"], how="left").fillna(0)
    merged = pd.merge(merged, asg_agg, on=["student_id", "course_id"], how="left").fillna(0)
    merged = pd.merge(merged, asm_agg, on=["student_id", "course_id"], how="left").fillna(0)

    # Compute Rates
    eff_sched = np.maximum(merged["total_sessions"] - merged["excused_sessions"], 0)
    merged["attendance_rate"] = np.where(
        eff_sched > 0,
        ((merged["present_sessions"] + (0.5 * merged["late_sessions"])) / eff_sched * 100.0).round(1),
        100.0
    )

    rec_eff = np.maximum(merged["recent_total"] - merged["recent_excused"], 0)
    merged["recent_attendance_rate"] = np.where(
        rec_eff > 0,
        ((merged["recent_present"] + (0.5 * merged["recent_late"])) / rec_eff * 100.0).round(1),
        merged["attendance_rate"]
    )

    prior_eff = np.maximum(merged["prior_total"] - merged["prior_excused"], 0)
    prior_att = np.where(
        prior_eff > 0,
        ((merged["prior_present"] + (0.5 * merged["prior_late"])) / prior_eff * 100.0),
        merged["attendance_rate"]
    )

    due_count = np.maximum(merged["due_assignments"], 0)
    merged["submission_completion_rate"] = np.where(
        due_count > 0,
        np.minimum((merged["submitted_assignments"] / due_count * 100.0).round(1), 100.0),
        100.0
    )

    sub_count = np.maximum(merged["submitted_assignments"], 0)
    merged["late_submission_rate"] = np.where(
        sub_count > 0,
        (merged["late_assignments"] / sub_count * 100.0).round(1),
        0.0
    )

    asg_max = np.maximum(merged["sum_max_score"], 0)
    merged["assignment_average"] = np.where(
        asg_max > 0,
        (merged["sum_score"] / asg_max * 100.0).round(1),
        75.0
    )

    asm_max = np.maximum(merged["asm_sum_max"], 0)
    merged["assessment_average"] = np.where(
        asm_max > 0,
        (merged["asm_sum_score"] / asm_max * 100.0).round(1),
        merged["assignment_average"]
    )

    # Engagement Trend
    att_diff = merged["recent_attendance_rate"] - prior_att
    conditions = [
        (merged["total_sessions"] < 3) & (merged["total_assignments"] < 2),
        (att_diff <= -15.0) | (merged["missing_assignments"] >= 2),
        (att_diff >= 10.0) & (merged["missing_assignments"] == 0),
    ]
    choices = ["insufficient_data", "declining", "improving"]
    merged["engagement_trend"] = np.select(conditions, choices, default="stable")

    merged["calculated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    final_cols = [
        "student_id", "course_id", "term", "section", "attendance_rate", "recent_attendance_rate",
        "submission_completion_rate", "late_submission_rate", "assignment_average", "assessment_average",
        "missing_assignments", "engagement_trend", "total_sessions", "present_sessions", "excused_sessions",
        "absent_sessions", "total_assignments", "submitted_assignments", "late_assignments", "calculated_at"
    ]

    return merged[final_cols]
