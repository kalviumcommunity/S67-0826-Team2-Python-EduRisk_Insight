"""
StudentPulse AI - Overview Dashboard Page
Faithful implementation of Stitch overview_dashboard screen.
"""

from typing import Dict, Optional
import pandas as pd
import streamlit as st

from src.reporting import ReportingService
from ui.components.cards import render_metric_card, render_signal_callout, render_disclaimer
from ui.charts.plotly_charts import create_engagement_trend_chart, create_risk_distribution_bar


def render_overview_page(service: ReportingService):
    """
    Renders the executive Overview Dashboard.
    
    Args:
        service: ReportingService instance.
    """
    # Top Course Selector
    filters_opt = service.get_filter_options()
    selected_course = st.selectbox("Select Course Context", filters_opt["courses"], index=0, key="overview_course_sel")

    filters = {"course_id": selected_course} if selected_course != "All" else {}
    metrics = service.get_overview_metrics(filters)
    insights = service.get_top_insights(filters)
    weekly_df = service.get_weekly_trends(filters)

    course_display = selected_course if selected_course != "All" else "All Enrolled Offerings"

    # Page Header
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Geist', sans-serif; font-size: 28px; font-weight: 700; color: #181d1a; margin-bottom: 4px;">Good morning, Dr. Maya.</h2>
        <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #5f5e5e; margin: 0;">Here is the current engagement picture for {course_display}.</p>
    </div>
    """, unsafe_allow_html=True)

    # Empty State Quick-Start Banner
    if metrics.total_enrolled == 0:
        st.markdown("""
        <div class="sp-card" style="background: linear-gradient(135deg, #f8faf6 0%, #eef3ea 100%); border-left: 4px solid #516600; padding: 20px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h3 style="font-family: 'Geist', sans-serif; font-size: 18px; font-weight: 700; color: #181d1a; margin: 0 0 4px 0;">
                        🚀 No Active Dataset Loaded
                    </h3>
                    <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; margin: 0;">
                        Upload your real institutional CSV files (students, enrolments, attendance, assignments, assessments) in the <strong>Data Quality Studio</strong> to generate real-time risk analytics.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📂 Open CSV Dataset Ingestion Studio", key="empty_overview_goto_upload", type="primary"):
            st.session_state["current_page"] = "Data Quality"
            st.rerun()
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # PRD Section 10: six headline KPI cards
    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Enrolled Students", f"{metrics.total_enrolled:,}", "group")
    with k2:
        render_metric_card("Need Review", f"{metrics.high_risk_count:,}", "warning", is_alert=(metrics.high_risk_count > 0))
    with k3:
        render_metric_card("Watch", f"{metrics.medium_risk_count:,}", "visibility")
    k4, k5, k6 = st.columns(3)
    with k4:
        render_metric_card("Avg Attendance", f"{metrics.avg_attendance_rate:.0f}%", "event_available")
    with k5:
        render_metric_card("Assignment Comp.", f"{metrics.avg_submission_completion:.0f}%", "task_alt")
    with k6:
        render_metric_card("Assessment Avg.", f"{metrics.avg_assessment_score:.0f}%", "school")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Middle Section: Grid (2 cols)
    grid_left, grid_right = st.columns([2, 1])

    with grid_left:
        st.markdown("""
        <div class="sp-card" style="margin-bottom: 0;">
            <div class="sp-card-header">
                <span>Engagement Trend</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        fig_trend = create_engagement_trend_chart(weekly_df)
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    with grid_right:
        # Support Level Distribution
        st.markdown("""
        <div class="sp-card" style="margin-bottom: 16px;">
            <div style="font-family: 'Geist', sans-serif; font-size: 15px; font-weight: 600; color: #181d1a; margin-bottom: 12px;">Students by support level</div>
        </div>
        """, unsafe_allow_html=True)
        fig_dist = create_risk_distribution_bar(
            low_count=metrics.low_risk_count,
            med_count=metrics.medium_risk_count,
            high_count=metrics.high_risk_count
        )
        st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})

        # Dynamic Top Signal
        top_signal = insights[0] if insights else None
        signal_headline = top_signal.headline if top_signal else "Attendance remains steady across active sections."
        render_signal_callout(
            title="This week's signal",
            text=signal_headline,
            icon="campaign",
            is_alert=(top_signal.severity == "High" if top_signal else False)
        )

    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)

    # Bottom Section: Priority Review List Table
    st.markdown("""
    <div class="sp-card">
        <div class="sp-card-header">
            <span>Priority review list</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch top 10 highest-risk students
    risk_students_df = service.get_risk_students(filters)
    if not risk_students_df.empty:
        high_priority = risk_students_df[risk_students_df["risk_level"] == "High"].head(8)
        if high_priority.empty:
            high_priority = risk_students_df.head(8)

        # Render custom interactive rows
        for _, row in high_priority.iterrows():
            s_id = str(row["student_id"])
            att_val = f"{row['attendance_rate']:.0f}%"
            missing_val = str(row["missing_assignments"])
            avg_val = f"{row['current_composite_avg']:.0f}%"
            reasons = row.get("primary_signal_labels", [])
            flag_text = reasons[0] if reasons else "Multiple risk indicators"
            lvl = row["risk_level"]
            badge_class = "sp-badge-high" if lvl == "High" else ("sp-badge-medium" if lvl == "Medium" else "sp-badge-low")
            badge_label = "Needs Review" if lvl == "High" else ("Watch" if lvl == "Medium" else "On Track")

            row_c1, row_c2, row_c3, row_c4, row_c5, row_c6, row_c7 = st.columns([2, 2, 1.5, 1.5, 1.5, 3, 1.5])
            with row_c1:
                st.markdown(f"<strong style='font-family: monospace; font-size: 13px;'>{s_id}</strong>", unsafe_allow_html=True)
            with row_c2:
                st.markdown(f"<span class='sp-badge {badge_class}'><span class='sp-badge-dot'></span> {badge_label}</span>", unsafe_allow_html=True)
            with row_c3:
                st.markdown(f"<span style='font-size: 13px;'>{att_val}</span>", unsafe_allow_html=True)
            with row_c4:
                st.markdown(f"<span style='font-size: 13px;'>{missing_val} missing</span>", unsafe_allow_html=True)
            with row_c5:
                st.markdown(f"<span style='font-size: 13px;'>{avg_val}</span>", unsafe_allow_html=True)
            with row_c6:
                st.markdown(f"<span style='font-size: 12px; color: #5f5e5e;'>{flag_text}</span>", unsafe_allow_html=True)
            with row_c7:
                if st.button("Review", key=f"rev_btn_{s_id}_{row['course_id']}", type="primary", use_container_width=True):
                    st.session_state["selected_student_id"] = s_id
                    st.session_state["selected_student_course"] = str(row["course_id"])
                    st.session_state["current_page"] = "Student Detail"
                    st.rerun()
            st.markdown("<hr style='margin: 4px 0 12px 0; border: none; border-top: 1px solid #ebefea;'>", unsafe_allow_html=True)
    else:
        st.info("No students currently flagged in this course view.")

    render_disclaimer()
