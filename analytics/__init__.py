"""
StudentPulse AI - Analytics Engine Package
Exposes cohort profiling, disparity analysis, longitudinal trends, and behavioural metrics.
"""

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

__all__ = [
    "analyze_cohort_disparities",
    "analyze_submission_behaviour",
    "compute_student_trend_trajectories",
    "compute_weekly_trends",
    "detect_consecutive_absence_streaks",
    "generate_behavioural_profile",
    "generate_cohort_profile",
]
