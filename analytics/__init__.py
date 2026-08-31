"""
StudentPulse AI - Analytics Engine Package
Exposes cohort profiling, disparity analysis, longitudinal trends, behavioural metrics, and KPI aggregations.
"""

from analytics.behaviour_analysis import (
    analyze_submission_behaviour,
    detect_consecutive_absence_streaks,
    generate_behavioural_profile,
)
from analytics.cohort_analysis import analyze_cohort_disparities
from analytics.kpi_metrics import (
    compute_course_level_kpis,
    compute_disengagement_kpi_indicators,
    compute_executive_kpis,
    validate_sql_vs_python_kpis,
)
from analytics.profiling import generate_cohort_profile
from analytics.trend_analysis import (
    compute_student_trend_trajectories,
    compute_weekly_trends,
)

__all__ = [
    "analyze_cohort_disparities",
    "analyze_submission_behaviour",
    "compute_course_level_kpis",
    "compute_disengagement_kpi_indicators",
    "compute_executive_kpis",
    "compute_student_trend_trajectories",
    "compute_weekly_trends",
    "detect_consecutive_absence_streaks",
    "generate_behavioural_profile",
    "generate_cohort_profile",
    "validate_sql_vs_python_kpis",
]

