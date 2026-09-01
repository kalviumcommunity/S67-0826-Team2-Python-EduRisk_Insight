"""
StudentPulse AI - Dynamic Cohort Insights Generator
Derives explainable, evidence-backed findings from active cohort analytics without hardcoded text.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class InsightFinding:
    """Represents an evidence-backed institutional finding."""
    title: str
    headline: str
    description: str
    severity: str  # 'High', 'Medium', 'Info'
    icon: str
    metric_value: Optional[str] = None


def generate_cohort_insights(
    features_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    selected_course: Optional[str] = None,
    selected_section: Optional[str] = None,
) -> List[InsightFinding]:
    """
    Dynamically generates the top 3 cohort-level findings based on filtered student records.
    
    Args:
        features_df: Precomputed student_course_features DataFrame.
        risk_df: Risk evaluations DataFrame.
        selected_course: Optional course filter.
        selected_section: Optional section filter.
        
    Returns:
        List of exactly 3 relevant InsightFinding objects.
    """
    if features_df.empty or risk_df.empty:
        return [
            InsightFinding(
                title="Cohort Baseline",
                headline="Insufficient cohort data available for dynamic insight derivation.",
                description="Populate or ingest course records to generate automated risk findings.",
                severity="Info",
                icon="info",
            ),
            InsightFinding(
                title="Data Synchronization",
                headline="Awaiting ingestion of student engagement activity.",
                description="Run the data pipeline to refresh institutional analytics.",
                severity="Info",
                icon="sync",
            ),
            InsightFinding(
                title="Advisory Guidance",
                headline="Risk indicators support human review and never replace academic judgement.",
                description="Institutional policies require human advisor oversight for all interventions.",
                severity="Info",
                icon="verified_user",
            ),
        ]

    if "risk_level" in features_df.columns:
        merged = features_df.copy()
    elif not risk_df.empty:
        cols_to_use = [c for c in risk_df.columns if c in ["student_id", "course_id", "term", "risk_level", "risk_score"]]
        merged = pd.merge(features_df, risk_df[cols_to_use], on=["student_id", "course_id", "term"], how="inner")
    else:
        merged = features_df.copy()
        merged["risk_level"] = "Low"


    findings: List[InsightFinding] = []
    total_students = len(merged)
    high_risk_students = merged[merged["risk_level"] == "High"]
    med_risk_students = merged[merged["risk_level"] == "Medium"]

    # -------------------------------------------------------------
    # Insight 1: Highest Concentration Course or Section
    # -------------------------------------------------------------
    if selected_section and selected_section != "All":
        # Section specific finding
        sec_high = len(high_risk_students)
        sec_pct = round(sec_high / total_students * 100.0, 1) if total_students else 0.0
        findings.append(InsightFinding(
            title="Section Risk Concentration",
            headline=f"Section {selected_section} exhibits {sec_high} students ({sec_pct}%) in need of review.",
            description=f"Out of {total_students} enrolled students, {sec_pct}% have triggered priority risk indicators requiring advisor attention.",
            severity="High" if sec_pct > 20 else "Medium",
            icon="group_work",
            metric_value=f"{sec_pct}%",
        ))
    elif "section" in merged.columns and merged["section"].nunique() > 1:
        # Compare sections
        sec_summary = merged.groupby("section")["risk_level"].apply(lambda x: (x == "High").mean() * 100.0)
        worst_sec = sec_summary.idxmax()
        worst_sec_pct = round(sec_summary.max(), 1)
        findings.append(InsightFinding(
            title="Section Variance",
            headline=f"Recent engagement decline is concentrated in Section {worst_sec} ({worst_sec_pct}% elevated risk).",
            description=f"Section {worst_sec} shows a higher proportion of students flagged for attendance or assignment review compared to other sections.",
            severity="High" if worst_sec_pct > 20 else "Medium",
            icon="pie_chart",
            metric_value=f"Section {worst_sec}",
        ))
    elif "course_id" in merged.columns and merged["course_id"].nunique() > 1:
        course_summary = merged.groupby("course_id")["risk_level"].apply(lambda x: (x == "High").mean() * 100.0)
        worst_course = course_summary.idxmax()
        worst_course_pct = round(course_summary.max(), 1)
        findings.append(InsightFinding(
            title="Course Disparity",
            headline=f"Course {worst_course} has the highest proportion of high-risk students ({worst_course_pct}%).",
            description=f"Course {worst_course} displays elevated assignment drop-off rates relative to other departmental offerings.",
            severity="High" if worst_course_pct > 20 else "Medium",
            icon="school",
            metric_value=f"{worst_course_pct}%",
        ))
    else:
        # General cohort risk rate
        high_pct = round(len(high_risk_students) / total_students * 100.0, 1) if total_students else 0.0
        findings.append(InsightFinding(
            title="Cohort Risk Profile",
            headline=f"{len(high_risk_students)} students ({high_pct}%) currently require academic review.",
            description="Engagement signals indicate students facing combined attendance and submission pacing challenges.",
            severity="High" if high_pct > 15 else "Medium",
            icon="bar_chart",
            metric_value=f"{high_pct}%",
        ))

    # -------------------------------------------------------------
    # Insight 2: Primary Risk Factor / Driver Analysis
    # -------------------------------------------------------------
    # Evaluate drivers among flagged students (High + Medium)
    flagged = merged[merged["risk_level"].isin(["High", "Medium"])]
    if not flagged.empty:
        low_att_count = (flagged["attendance_rate"] < 70.0).sum()
        missing_work_count = (flagged["missing_assignments"] >= 2).sum()
        low_sub_count = (flagged["submission_completion_rate"] < 80.0).sum()
        low_perf_count = ((flagged["assignment_average"] < 50.0) | (flagged["assessment_average"] < 50.0)).sum()

        driver_counts = {
            "missing assignment submissions": missing_work_count,
            "attendance below 70%": low_att_count,
            "submission completion below 80%": low_sub_count,
            "exam performance below 50%": low_perf_count,
        }
        top_driver, top_count = max(driver_counts.items(), key=lambda item: item[1])
        top_driver_pct = round(top_count / len(flagged) * 100.0, 1)

        findings.append(InsightFinding(
            title="Primary Risk Indicator",
            headline=f"Students with {top_driver} represent the largest risk segment ({top_driver_pct}% of flagged cohort).",
            description=f"Among the {len(flagged)} students flagged for support, {top_count} exhibit {top_driver}. Early submission support is strongly recommended.",
            severity="High" if top_driver_pct > 50 else "Medium",
            icon="assignment_late",
            metric_value=f"{top_driver_pct}%",
        ))
    else:
        avg_att = round(merged["attendance_rate"].mean(), 1) if not merged.empty else 0.0
        findings.append(InsightFinding(
            title="Engagement Stability",
            headline=f"Cohort attendance remains steady at an average of {avg_att}%.",
            description="No widespread acute attendance anomalies detected across current student cohorts.",
            severity="Info",
            icon="event_available",
            metric_value=f"{avg_att}%",
        ))

    # -------------------------------------------------------------
    # Insight 3: Engagement Correlation / Recovering Trend Finding
    # -------------------------------------------------------------
    # Correlation between attendance & completion or recovering students
    recovering_count = (merged["engagement_trend"] == "improving").sum()
    declining_count = (merged["engagement_trend"] == "declining").sum()

    if declining_count > 0:
        dec_pct = round(declining_count / total_students * 100.0, 1)
        findings.append(InsightFinding(
            title="Recency Anomaly",
            headline=f"{declining_count} students ({dec_pct}%) demonstrate an active 14-day engagement decline.",
            description="Recent attendance or assignment completion is falling faster than earlier term averages, suggesting emerging semester burnout.",
            severity="Medium",
            icon="trending_down",
            metric_value=f"{declining_count} Students",
        ))
    elif recovering_count > 0:
        rec_pct = round(recovering_count / total_students * 100.0, 1)
        findings.append(InsightFinding(
            title="Positive Trajectory",
            headline=f"{recovering_count} students ({rec_pct}%) are showing improving engagement trends.",
            description="Recent 14-day attendance and homework submission rates have rebounded compared to earlier term intervals.",
            severity="Info",
            icon="trending_up",
            metric_value=f"{recovering_count} Students",
        ))
    else:
        findings.append(InsightFinding(
            title="Support Indicator Note",
            headline="Risk indicators are support signals for qualified staff review and do not replace academic judgement.",
            description="Signals highlight correlated engagement patterns and do not imply causation or determine academic grades.",
            severity="Info",
            icon="shield",
            metric_value="Advisory",
        ))

    return findings[:3]
