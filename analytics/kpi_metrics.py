"""
StudentPulse AI - Institutional KPI & Business Metrics Engine
Calculates executive headline KPIs, course-level performance aggregates,
disengagement risk indices, and dual-engine SQL/Python parity validation.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def compute_executive_kpis(
    features_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computes institutional headline academic KPIs for a filtered student cohort.
    
    Args:
        features_df: DataFrame containing student course features.
        risk_df: DataFrame containing student risk assessments.
        filters: Optional dict containing filter keys: 'term', 'course_id', 'section'.
        
    Returns:
        Dictionary containing counts, percentages, and performance averages.
    """
    if features_df.empty or risk_df.empty:
        return {
            "total_enrolled_students": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "high_risk_rate": 0.0,
            "medium_risk_rate": 0.0,
            "low_risk_rate": 0.0,
            "avg_attendance_rate": 0.0,
            "avg_submission_completion_rate": 0.0,
            "avg_assessment_score": 0.0,
            "avg_assignment_score": 0.0,
            "on_track_rate": 0.0,
        }

    join_keys = ["student_id", "course_id", "term"]
    if "section" in features_df.columns and "section" in risk_df.columns:
        join_keys.append("section")

    merged = pd.merge(features_df, risk_df, on=join_keys, how="inner")

    # Apply filters if provided
    if filters:
        if filters.get("term") and filters["term"] != "All" and "term" in merged.columns:
            merged = merged[merged["term"] == filters["term"]]
        if filters.get("course_id") and filters["course_id"] != "All" and "course_id" in merged.columns:
            merged = merged[merged["course_id"] == filters["course_id"]]
        if filters.get("section") and filters["section"] != "All" and "section" in merged.columns:
            merged = merged[merged["section"] == filters["section"]]

    if merged.empty:
        return {
            "total_enrolled_students": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "high_risk_rate": 0.0,
            "medium_risk_rate": 0.0,
            "low_risk_rate": 0.0,
            "avg_attendance_rate": 0.0,
            "avg_submission_completion_rate": 0.0,
            "avg_assessment_score": 0.0,
            "avg_assignment_score": 0.0,
            "on_track_rate": 0.0,
        }

    total_students = int(merged["student_id"].nunique())
    high_count = int((merged["risk_level"] == "High").sum())
    med_count = int((merged["risk_level"] == "Medium").sum())
    low_count = int((merged["risk_level"] == "Low").sum())
    record_count = len(merged)

    avg_att = float(merged["attendance_rate"].mean()) if "attendance_rate" in merged.columns and not merged["attendance_rate"].isna().all() else 0.0
    avg_sub = float(merged["submission_completion_rate"].mean()) if "submission_completion_rate" in merged.columns and not merged["submission_completion_rate"].isna().all() else 0.0
    avg_asm = float(merged["assessment_average"].mean()) if "assessment_average" in merged.columns and not merged["assessment_average"].isna().all() else 0.0
    avg_asg = float(merged["assignment_average"].mean()) if "assignment_average" in merged.columns and not merged["assignment_average"].isna().all() else 0.0

    return {
        "total_enrolled_students": total_students,
        "high_risk_count": high_count,
        "medium_risk_count": med_count,
        "low_risk_count": low_count,
        "high_risk_rate": round(high_count / record_count * 100.0, 1) if record_count else 0.0,
        "medium_risk_rate": round(med_count / record_count * 100.0, 1) if record_count else 0.0,
        "low_risk_rate": round(low_count / record_count * 100.0, 1) if record_count else 0.0,
        "avg_attendance_rate": round(avg_att, 2),
        "avg_submission_completion_rate": round(avg_sub, 2),
        "avg_assessment_score": round(avg_asm, 2),
        "avg_assignment_score": round(avg_asg, 2),
        "on_track_rate": round(low_count / record_count * 100.0, 1) if record_count else 0.0,
    }


def compute_course_level_kpis(
    features_df: pd.DataFrame,
    risk_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculates course and section comparative KPI scorecard.
    
    Args:
        features_df: DataFrame of student-course feature records.
        risk_df: DataFrame of risk assessment evaluations.
        
    Returns:
        DataFrame aggregated by course and section with health metrics.
    """
    if features_df.empty or risk_df.empty:
        return pd.DataFrame(columns=[
            "course_id", "term", "section", "total_students", "high_risk_count",
            "medium_risk_count", "low_risk_count", "high_risk_pct", "avg_attendance_rate",
            "avg_submission_rate", "avg_assessment_score", "academic_health_score"
        ])

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

    group_cols = ["course_id"]
    if "term" in merged.columns:
        group_cols.append("term")
    if "section" in merged.columns:
        group_cols.append("section")

    grouped = merged.groupby(group_cols).agg(
        total_students=("student_id", "nunique"),
        high_risk_count=("risk_level", lambda x: (x == "High").sum()),
        medium_risk_count=("risk_level", lambda x: (x == "Medium").sum()),
        low_risk_count=("risk_level", lambda x: (x == "Low").sum()),
        avg_attendance_rate=("attendance_rate", "mean"),
        avg_submission_rate=("submission_completion_rate", "mean"),
        avg_assessment_score=("assessment_average", "mean"),
    ).reset_index()

    grouped["high_risk_pct"] = (grouped["high_risk_count"] / grouped["total_students"] * 100.0).round(1)
    grouped["avg_attendance_rate"] = grouped["avg_attendance_rate"].round(1)
    grouped["avg_submission_rate"] = grouped["avg_submission_rate"].round(1)
    grouped["avg_assessment_score"] = grouped["avg_assessment_score"].round(1)

    # Weighted Academic Health Score (0-100 index)
    grouped["academic_health_score"] = (
        0.30 * grouped["avg_attendance_rate"] +
        0.35 * grouped["avg_submission_rate"] +
        0.35 * grouped["avg_assessment_score"]
    ).round(1)

    return grouped.sort_values(by="high_risk_pct", ascending=False).reset_index(drop=True)


def compute_disengagement_kpi_indicators(
    features_df: pd.DataFrame,
    risk_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Quantifies leading disengagement indicators across institutional cohorts.
    
    Args:
        features_df: DataFrame of student-course feature records.
        risk_df: Optional DataFrame of risk assessments.
        
    Returns:
        Dictionary of disengagement metrics, counts, and percentages.
    """
    if features_df.empty:
        return {}

    total = len(features_df)
    chronic_absent_mask = features_df["attendance_rate"] < 70.0
    backlog_mask = features_df["missing_assignments"] >= 2
    low_assess_mask = features_df["assessment_average"] < 60.0
    declining_mask = features_df["engagement_trend"] == "declining"

    # Multi-risk triggers (students meeting >= 2 warning criteria)
    multi_trigger_count = int(
        (chronic_absent_mask.astype(int) +
         backlog_mask.astype(int) +
         low_assess_mask.astype(int) +
         declining_mask.astype(int) >= 2).sum()
    )

    chronic_count = int(chronic_absent_mask.sum())
    backlog_count = int(backlog_mask.sum())
    low_assess_count = int(low_assess_mask.sum())
    declining_count = int(declining_mask.sum())

    return {
        "cohort_size": total,
        "chronic_absenteeism_count": chronic_count,
        "chronic_absenteeism_pct": round(chronic_count / total * 100.0, 1) if total else 0.0,
        "critical_backlog_count": backlog_count,
        "critical_backlog_pct": round(backlog_count / total * 100.0, 1) if total else 0.0,
        "low_assessment_count": low_assess_count,
        "low_assessment_pct": round(low_assess_count / total * 100.0, 1) if total else 0.0,
        "declining_engagement_count": declining_count,
        "declining_engagement_pct": round(declining_count / total * 100.0, 1) if total else 0.0,
        "multi_risk_student_count": multi_trigger_count,
        "multi_risk_student_pct": round(multi_trigger_count / total * 100.0, 1) if total else 0.0,
    }


def validate_sql_vs_python_kpis(
    py_kpis: Dict[str, Any],
    sql_kpis: Dict[str, Any],
    tolerance: float = 0.05,
) -> Dict[str, Any]:
    """
    Performs dual-engine consistency audit between Python and SQL computed metrics.
    
    Args:
        py_kpis: KPI dictionary computed in Python.
        sql_kpis: KPI dictionary retrieved from SQL view.
        tolerance: Maximum acceptable absolute difference for float metrics.
        
    Returns:
        Audit report dictionary with overall status and metric-level breakdown.
    """
    comparisons = []
    all_passed = True

    metrics_to_check = [
        ("total_enrolled_students", "count"),
        ("high_risk_count", "count"),
        ("medium_risk_count", "count"),
        ("low_risk_count", "count"),
        ("avg_attendance_rate", "float"),
        ("avg_submission_completion_rate", "float"),
        ("avg_assessment_score", "float"),
    ]

    for metric_name, m_type in metrics_to_check:
        py_val = py_kpis.get(metric_name, 0)
        # SQL might use slightly different column name variations
        sql_val = sql_kpis.get(metric_name, sql_kpis.get(metric_name.replace("_rate", ""), 0))

        if py_val is None:
            py_val = 0
        if sql_val is None:
            sql_val = 0

        diff = abs(float(py_val) - float(sql_val))
        passed = diff <= (0.0 if m_type == "count" else tolerance)
        if not passed:
            all_passed = False

        comparisons.append({
            "metric": metric_name,
            "python_value": py_val,
            "sql_value": sql_val,
            "difference": round(diff, 4),
            "passed": passed,
        })

    return {
        "overall_status": "PASS" if all_passed else "FAIL",
        "all_passed": all_passed,
        "metrics": comparisons,
    }
