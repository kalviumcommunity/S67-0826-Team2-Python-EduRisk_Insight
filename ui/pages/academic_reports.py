"""
StudentPulse AI - Academic Reports & Cohort Disparity Page
Faithful implementation of Stitch academic_reports screen.
Provides cross-course risk disparity analysis, dynamic cohort findings,
and exportable analytical reports.
"""

from typing import Dict, Optional
import streamlit as st
import pandas as pd

from src.reporting import ReportingService
from analytics.cohort_analysis import analyze_cohort_disparities
from ui.charts.plotly_charts import create_course_comparison_bar
from ui.components.cards import render_disclaimer


def render_academic_reports_page(service: ReportingService):
    """
    Renders the Academic Reports & Disparity Analytics screen.
    
    Args:
        service: ReportingService instance.
    """
    # -------------------------------------------------------------
    # Page Header
    # -------------------------------------------------------------
    st.markdown("""<div style="margin-bottom: 24px;">
<h2 style="font-family: 'Geist', sans-serif; font-size: 28px; font-weight: 700; color: #181d1a; margin-bottom: 4px;">Academic Reports</h2>
<p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #5f5e5e; margin: 0;">
Generate evidence-backed cohort insights, cross-sectional disparities, and executive summaries.
</p>
</div>""", unsafe_allow_html=True)

    # Filter Bar
    filter_opts = service.get_filter_options()
    col_f1, col_f2 = st.columns([3, 3])
    with col_f1:
        sel_term = st.selectbox("Select Academic Term", filter_opts["terms"], index=0, key="rep_term_sel")
    with col_f2:
        sel_course = st.selectbox("Select Course Scope", filter_opts["courses"], index=0, key="rep_course_sel")

    filters = {}
    if sel_term != "All":
        filters["term"] = sel_term
    if sel_course != "All":
        filters["course_id"] = sel_course

    course_summary_df = service.get_course_summary(filters)
    insights = service.get_top_insights(filters)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2-Column Main Layout: 7 Cols Left, 5 Cols Right
    # -------------------------------------------------------------
    col_left, col_right = st.columns([7, 5])

    with col_left:
        # Report Card 1: Weekly Engagement Summary
        st.markdown("""<div class="sp-card" style="border: 2px solid #516600; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
<div>
<h3 style="font-family: 'Geist', sans-serif; font-size: 18px; font-weight: 600; color: #181d1a; margin: 0 0 4px 0;">
Weekly Engagement & Risk Summary
</h3>
<p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; margin: 0; line-height: 1.4;">
Aggregated LMS activity, attendance trends, assignment submissions, and student support flags across all active course sections.
</p>
</div>
<span class="material-symbols-outlined" style="color: #516600; font-size: 32px;">analytics</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #ebefea; padding-top: 14px; margin-top: 14px;">
<span style="font-family: 'Geist', sans-serif; font-size: 11px; text-transform: uppercase; color: #5f5e5e;">
Last Generated: Today at 09:14 AM
</span>
<div style="display: flex; gap: 8px;">
<span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> Ready for Download</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # Download actions for Report 1
        students_df = service.get_risk_students(filters)
        if not students_df.empty:
            csv_data = students_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Download Summary Report (CSV)",
                data=csv_data,
                file_name=f"studentpulse_engagement_summary_{sel_term}_{sel_course}.csv",
                mime="text/csv",
                type="primary",
                key="download_rep1_csv"
            )

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Report Card 2: Course Disparity & Risk Review
        st.markdown("""<div class="sp-card" style="margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
<div>
<h3 style="font-family: 'Geist', sans-serif; font-size: 18px; font-weight: 600; color: #181d1a; margin: 0 0 4px 0;">
Course & Section Disparity Review
</h3>
<p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; margin: 0; line-height: 1.4;">
Evaluates systemic engagement and score differences across departmental offerings and course sections.
</p>
</div>
<span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 32px;">health_and_safety</span>
</div>
</div>""", unsafe_allow_html=True)

        # Interactive Plotly Disparity Bar Chart
        if not course_summary_df.empty:
            fig_disp = create_course_comparison_bar(course_summary_df)
            st.plotly_chart(fig_disp, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        # Report Preview / Dynamic Cohort Findings Box (Matches Stitch design)
        findings_html = ""
        if insights:
            for item in insights:
                icon_color = "#ba1a1a" if item.severity == "High" else ("#d97706" if item.severity == "Medium" else "#516600")
                bg_card = "#ffdad6" if item.severity == "High" else ("#fef0c7" if item.severity == "Medium" else "#ffffff")
                border_card = "#ffb4ab" if item.severity == "High" else ("#fde68a" if item.severity == "Medium" else "#ebefea")

                findings_html += f"""<div style="background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
<span class="material-symbols-outlined" style="color: {icon_color}; font-size: 20px;">{item.icon}</span>
<strong style="font-family: 'Geist', sans-serif; font-size: 13px; color: #181d1a;">{item.title}</strong>
</div>
<div style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #181d1a; margin-bottom: 4px; line-height: 1.3;">
{item.headline}
</div>
<div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #5f5e5e; line-height: 1.4;">
{item.description}
</div>
</div>"""
        else:
            findings_html = "<div style='font-size: 13px; color: #5f5e5e; padding: 8px 0;'>No cohort findings generated for the current filter criteria.</div>"

        preview_card_html = f"""<div class="sp-card" style="background-color: #f1f5ef; border: 1px solid #c4c9ac; margin-bottom: 16px;">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
<span class="material-symbols-outlined" style="color: #516600;">visibility</span>
<h3 style="font-family: 'Geist', sans-serif; font-size: 16px; font-weight: 600; color: #181d1a; margin: 0;">
Dynamic Cohort Findings Preview
</h3>
</div>
{findings_html}
</div>"""
        st.markdown(preview_card_html, unsafe_allow_html=True)

        if st.button("Generate Fresh Report", key="gen_fresh_rep_btn", type="primary", use_container_width=True):
            st.success("✓ Fresh cohort analysis report generated.")
            st.rerun()

    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Bottom Section: Section Breakdown & Disparity Table
    # -------------------------------------------------------------
    st.markdown("""<div class="sp-card" style="margin-bottom: 16px;">
<div class="sp-card-header" style="margin-bottom: 0;">
<span>Course Section Performance & Risk Breakdown</span>
</div>
</div>""", unsafe_allow_html=True)

    try:
        features_all = service.db.query_dataframe("SELECT * FROM student_course_features")
        risk_all = service.db.query_dataframe("SELECT * FROM risk_assessments")
        disparity_df = analyze_cohort_disparities(features_all, risk_all)

        if not disparity_df.empty:
            if sel_course != "All":
                disparity_df = disparity_df[disparity_df["course_id"] == sel_course]
            
            disparity_df.columns = [
                "Course Code", "Section", "Enrolled Students", "Needs Review",
                "Watch", "On Track", "Avg Attendance (%)", "Avg Submission (%)",
                "Avg Assessment (%)", "High Risk Rate (%)"
            ]
            st.dataframe(disparity_df, use_container_width=True, hide_index=True)
        else:
            st.info("No section comparison data available.")
    except Exception as e:
        st.error(f"Could not compute section breakdown: {str(e)}")

    render_disclaimer()
