"""
StudentPulse AI - Risk Explorer Page
Faithful implementation of Stitch risk_explorer and risk_explorer_empty_state screens.
"""

from typing import Dict
import pandas as pd
import streamlit as st

from src.reporting import ReportingService
from src.risk_explanations import format_support_badge, get_recommended_action
from ui.components.filters import render_filter_rail
from ui.components.cards import render_disclaimer


def render_risk_explorer_page(service: ReportingService):
    """
    Renders the interactive Risk Explorer interface with multi-criteria filtering,
    contextual slide-out student drawer, CSV export, and empty states.
    
    Args:
        service: ReportingService instance.
    """
    # Header & Export Action
    head_left, head_right = st.columns([3, 1])
    with head_left:
        st.markdown("""
        <h2 style="font-family: 'Geist', sans-serif; font-size: 28px; font-weight: 700; color: #181d1a; margin-bottom: 4px;">Risk Explorer</h2>
        <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #5f5e5e; margin: 0 0 16px 0;">
            Review students by the signals that need a conversation — not by a black-box score.
        </p>
        """, unsafe_allow_html=True)

    # Filter Rail
    filters = render_filter_rail(service)
    students_df = service.get_risk_students(filters)

    with head_right:
        if not students_df.empty:
            # Prepare exportable dataframe
            export_cols = [
                "student_id", "course_id", "section", "term", "risk_level", "risk_score",
                "attendance_rate", "recent_attendance_rate", "submission_completion_rate",
                "late_submission_rate", "missing_assignments", "assignment_average",
                "assessment_average", "engagement_trend"
            ]
            valid_exp_cols = [c for c in export_cols if c in students_df.columns]
            csv_data = students_df[valid_exp_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Export CSV",
                data=csv_data,
                file_name=f"studentpulse_risk_export_{filters.get('course_id', 'all')}.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True,
            )

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # Check for empty state
    if students_df.empty:
        st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #c4c9ac; border-radius: 16px; padding: 48px 24px; text-align: center; margin: 24px 0;">
            <div style="width: 64px; height: 64px; border-radius: 50%; background-color: #ebefea; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 32px;">search_off</span>
            </div>
            <h3 style="font-family: 'Geist', sans-serif; font-size: 20px; font-weight: 600; color: #181d1a; margin-bottom: 8px;">No students match these filters</h3>
            <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #5f5e5e; max-width: 420px; margin: 0 auto 24px auto;">
                Try adjusting your search criteria, clearing the filter selections, or broadening the support level filter.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Clear all filters", type="secondary"):
            st.session_state["filter_course"] = "All"
            st.session_state["filter_term"] = "All"
            st.session_state["filter_section"] = "All"
            st.session_state["filter_risk_level"] = "All"
            st.session_state["filter_search"] = ""
            st.rerun()
        render_disclaimer()
        return

    # Selected student in session state for sidebar context
    if "selected_student_id" not in st.session_state or not st.session_state["selected_student_id"]:
        st.session_state["selected_student_id"] = str(students_df.iloc[0]["student_id"])
        st.session_state["selected_student_course"] = str(students_df.iloc[0]["course_id"])

    # 2-Column Split: Left = Table, Right = Detail Drawer
    col_table, col_detail = st.columns([7, 5])

    with col_table:
        st.markdown(f"""
        <div style="font-family: 'Geist', sans-serif; font-size: 13px; font-weight: 600; color: #5f5e5e; margin-bottom: 8px;">
            SHOWING {len(students_df)} STUDENTS
        </div>
        """, unsafe_allow_html=True)

        # Render Table Header
        t_c1, t_c2, t_c3, t_c4 = st.columns([2.5, 2.5, 4.5, 2])
        with t_c1:
            st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>STUDENT ID</strong>", unsafe_allow_html=True)
        with t_c2:
            st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>SUPPORT LEVEL</strong>", unsafe_allow_html=True)
        with t_c3:
            st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>PRIMARY SIGNALS</strong>", unsafe_allow_html=True)
        with t_c4:
            st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>ACTION</strong>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #c4c9ac;'>", unsafe_allow_html=True)

        # Render first 25 students with pagination support
        for _, row in students_df.head(25).iterrows():
            s_id = str(row["student_id"])
            c_id = str(row["course_id"])
            lvl = row["risk_level"]
            badge_info = format_support_badge(lvl)
            badge_class = "sp-badge-high" if lvl == "High" else ("sp-badge-medium" if lvl == "Medium" else "sp-badge-low")

            is_selected = (st.session_state.get("selected_student_id") == s_id)
            highlight_border = "border-left: 3px solid #516600; background-color: #f7faf5;" if is_selected else ""

            row_1, row_2, row_3, row_4 = st.columns([2.5, 2.5, 4.5, 2])
            with row_1:
                st.markdown(f"<span style='font-family: monospace; font-weight: 600; font-size: 13px;'>{s_id}</span>", unsafe_allow_html=True)
            with row_2:
                st.markdown(f"<span class='sp-badge {badge_class}'><span class='sp-badge-dot'></span> {badge_info['label']}</span>", unsafe_allow_html=True)
            with row_3:
                reasons = row.get("primary_signal_labels", [])
                chips_html = "".join([f"<span class='sp-chip'>{r}</span>" for r in reasons[:2]])
                st.markdown(chips_html or "<span style='font-size: 11px; color: #5f5e5e;'>On track</span>", unsafe_allow_html=True)
            with row_4:
                if st.button("Inspect", key=f"inspect_{s_id}_{c_id}", use_container_width=True):
                    st.session_state["selected_student_id"] = s_id
                    st.session_state["selected_student_course"] = c_id
                    st.rerun()

            st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #ebefea;'>", unsafe_allow_html=True)

    # Right Column: Contextual Student Detail Sidebar
    with col_detail:
        sel_id = st.session_state.get("selected_student_id")
        sel_course = st.session_state.get("selected_student_course")
        profile = service.get_student_detail(sel_id, sel_course)

        if profile:
            badge_info = format_support_badge(profile["risk_level"])
            reasons = profile.get("parsed_reasons", [])
            action_info = get_recommended_action(profile["risk_level"], reasons)

            st.markdown(f"""
            <div class="sp-card" style="border-top: 4px solid {badge_info['dot']};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                    <div>
                        <h3 style="font-family: monospace; font-size: 22px; font-weight: 700; color: #181d1a; margin: 0;">{sel_id}</h3>
                        <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; margin: 2px 0 0 0;">
                            {profile.get('program', 'Data Analytics')} — Section {profile.get('section', 'A')}
                        </p>
                    </div>
                    <span class="sp-badge {('sp-badge-high' if profile['risk_level'] == 'High' else ('sp-badge-medium' if profile['risk_level'] == 'Medium' else 'sp-badge-low'))}">
                        <span class="sp-badge-dot"></span> {badge_info['label']}
                    </span>
                </div>

                <!-- Status Alert Box -->
                <div style="background-color: {badge_info['bg']}; border: 1px solid {badge_info['border']}; border-radius: 8px; padding: 12px; margin-bottom: 20px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: {badge_info['text']};">
                        Risk Score: {profile['risk_score']} pts
                    </div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: {badge_info['text']}; margin-top: 2px;">
                        {len(reasons)} active indicator(s) triggered for qualified advisor review.
                    </div>
                </div>

                <!-- Signal Breakdown -->
                <div style="font-family: 'Geist', sans-serif; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #5f5e5e; margin-bottom: 12px; border-bottom: 1px solid #ebefea; padding-bottom: 4px;">
                    Signal Breakdown
                </div>
            """, unsafe_allow_html=True)

            # Signal Item 1: Attendance
            att_val = profile.get("attendance_rate", 100.0)
            att_color = "#ba1a1a" if att_val < 70 else "#516600"
            st.markdown(f"""
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span class="material-symbols-outlined" style="font-size: 16px; color: #5f5e5e;">calendar_today</span> Attendance
                    </span>
                    <strong style="color: {att_color}; font-family: monospace;">{att_val:.0f}%</strong>
                </div>
                <div style="width: 100%; height: 6px; background-color: #ebefea; border-radius: 9999px; overflow: hidden;">
                    <div style="width: {min(att_val, 100.0)}%; height: 100%; background-color: {att_color}; border-radius: 9999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Signal Item 2: Submissions
            missing_val = profile.get("missing_assignments", 0)
            miss_color = "#ba1a1a" if missing_val >= 2 else "#5f5e5e"
            st.markdown(f"""
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span class="material-symbols-outlined" style="font-size: 16px; color: #5f5e5e;">assignment_late</span> Missing Work
                    </span>
                    <strong style="color: {miss_color}; font-family: monospace;">{missing_val} Missing</strong>
                </div>
                <div style="font-size: 11px; color: #5f5e5e;">Completion rate: {profile.get('submission_completion_rate', 100):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

            # Recommended Action Section
            st.markdown(f"""
                <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #ebefea;">
                    <div style="font-family: 'Geist', sans-serif; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #5f5e5e; margin-bottom: 8px;">
                        Recommended Action
                    </div>
                    <p style="font-family: 'Inter', sans-serif; font-size: 12px; color: #181d1a; margin-bottom: 12px;">
                        {action_info['description']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Full Profile →", key="view_profile_drawer_btn", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Student Detail"
                st.rerun()

    render_disclaimer()
