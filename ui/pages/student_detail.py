"""
StudentPulse AI - Student Detail Profile Page
Faithful implementation of Stitch student_profile_detail screen.
Provides deep-dive individual engagement analysis, explainable risk factors,
and interactive staff intervention recording.
"""

import datetime
from typing import Dict, Optional
import streamlit as st
import pandas as pd

from src.reporting import ReportingService
from src.risk_explanations import format_support_badge, get_recommended_action
from ui.components.cards import render_disclaimer


def render_student_detail_page(service: ReportingService):
    """
    Renders the comprehensive Student Profile Detail view.
    
    Args:
        service: ReportingService instance.
    """
    # 1. Determine Selected Student ID and Course Context
    sel_id = st.session_state.get("selected_student_id")
    sel_course = st.session_state.get("selected_student_course")

    # If no student is currently selected in session state, fetch first available
    if not sel_id:
        risk_df = service.get_risk_students()
        if not risk_df.empty:
            sel_id = str(risk_df.iloc[0]["student_id"])
            sel_course = str(risk_df.iloc[0]["course_id"])
            st.session_state["selected_student_id"] = sel_id
            st.session_state["selected_student_course"] = sel_course
        else:
            st.warning("No student records found in database. Please run the pipeline first.")
            return

    # Student switcher bar
    col_nav_left, col_nav_right = st.columns([2, 4])
    with col_nav_left:
        if st.button("← Back to Risk Explorer", key="back_to_explorer_btn", type="secondary"):
            st.session_state["current_page"] = "Risk Explorer"
            st.rerun()
    with col_nav_right:
        # Quick Switcher for convenience
        all_students_df = service.get_risk_students({"course_id": sel_course} if sel_course else None)
        if not all_students_df.empty:
            s_list = all_students_df["student_id"].tolist()
            cur_idx = s_list.index(sel_id) if sel_id in s_list else 0
            new_s_id = st.selectbox("Quick Switch Student", s_list, index=cur_idx, key="student_detail_quick_switch")
            if new_s_id != sel_id:
                st.session_state["selected_student_id"] = new_s_id
                st.rerun()

    profile = service.get_student_detail(sel_id, sel_course)
    if not profile:
        st.error(f"Could not load detailed profile for student {sel_id}.")
        return

    badge_info = format_support_badge(profile.get("risk_level", "Low"))
    reasons = profile.get("parsed_reasons", [])
    action_info = get_recommended_action(profile.get("risk_level", "Low"), reasons)

    # -------------------------------------------------------------
    # Profile Header matching Stitch design
    # -------------------------------------------------------------
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; gap: 8px; border-bottom: 1px solid #c4c9ac; padding-bottom: 18px; margin-bottom: 24px; margin-top: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                    <h1 style="font-family: 'Geist', sans-serif; font-size: 32px; font-weight: 700; color: #181d1a; margin: 0; letter-spacing: -0.02em;">
                        {profile['student_id']}
                    </h1>
                    <span class="sp-badge {('sp-badge-high' if profile['risk_level'] == 'High' else ('sp-badge-medium' if profile['risk_level'] == 'Medium' else 'sp-badge-low'))}">
                        <span class="sp-badge-dot"></span> {badge_info['label']}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e;">
                    <span><strong>Program:</strong> {profile.get('program', 'Data Analytics')}</span>
                    <span>•</span>
                    <span><strong>Course:</strong> {profile.get('course_id', 'DATA-101')} ({profile.get('term', 'Fall 2026')})</span>
                    <span>•</span>
                    <span><strong>Section:</strong> {profile.get('section', 'A')}</span>
                    <span>•</span>
                    <span><strong>Cohort:</strong> Class of {profile.get('cohort_year', 2026)}</span>
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="material-symbols-outlined" style="color: #516600; font-size: 18px;">schedule</span>
                <span style="font-size: 12px; color: #5f5e5e;">Risk Score: <strong style="color: #181d1a;">{profile.get('risk_score', 0)} pts</strong></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2-Column Main Layout: 7 Cols Left, 5 Cols Right
    # -------------------------------------------------------------
    col_left, col_right = st.columns([7, 5])

    with col_left:
        # 1. Assessment & Performance Progress Card
        asg_avg = float(profile.get("assignment_average", 75.0))
        asm_avg = float(profile.get("assessment_average", 75.0))
        composite_avg = round((asg_avg + asm_avg) / 2.0, 1)

        asg_color = "#ba1a1a" if asg_avg < 50 else ("#d97706" if asg_avg < 70 else "#516600")
        asm_color = "#ba1a1a" if asm_avg < 50 else ("#d97706" if asm_avg < 70 else "#516600")
        comp_color = "#ba1a1a" if composite_avg < 50 else ("#d97706" if composite_avg < 70 else "#516600")

        st.markdown(f"""
        <div class="sp-card">
            <div class="sp-card-header">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e;">monitoring</span>
                    Assessment & Performance Progress
                </span>
                <span style="font-size: 12px; color: #5f5e5e;">Composite: <strong style="color: {comp_color};">{composite_avg:.1f}%</strong></span>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                        <span style="font-weight: 500; color: #181d1a;">Examination / Assessment Average</span>
                        <strong style="color: {asm_color}; font-family: monospace;">{asm_avg:.1f}%</strong>
                    </div>
                    <div style="width: 100%; height: 8px; background-color: #ebefea; border-radius: 9999px; overflow: hidden;">
                        <div style="width: {min(max(asm_avg, 0), 100)}%; height: 100%; background-color: {asm_color}; border-radius: 9999px;"></div>
                    </div>
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                        <span style="font-weight: 500; color: #181d1a;">Assignment Submission Average</span>
                        <strong style="color: {asg_color}; font-family: monospace;">{asg_avg:.1f}%</strong>
                    </div>
                    <div style="width: 100%; height: 8px; background-color: #ebefea; border-radius: 9999px; overflow: hidden;">
                        <div style="width: {min(max(asg_avg, 0), 100)}%; height: 100%; background-color: {asg_color}; border-radius: 9999px;"></div>
                    </div>
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                        <span style="font-weight: 500; color: #181d1a;">Submission Completion Rate</span>
                        <strong style="color: {'#ba1a1a' if profile.get('submission_completion_rate', 100) < 80 else '#516600'}; font-family: monospace;">
                            {profile.get('submission_completion_rate', 100):.1f}%
                        </strong>
                    </div>
                    <div style="width: 100%; height: 8px; background-color: #ebefea; border-radius: 9999px; overflow: hidden;">
                        <div style="width: {min(max(float(profile.get('submission_completion_rate', 100)), 0), 100)}%; height: 100%; background-color: {'#ba1a1a' if profile.get('submission_completion_rate', 100) < 80 else '#516600'}; border-radius: 9999px;"></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Recent Engagement & Attendance Timeline
        att_rate = float(profile.get("attendance_rate", 100.0))
        rec_att = float(profile.get("recent_attendance_rate", att_rate))
        att_history = profile.get("attendance_history", [])

        st.markdown(f"""
        <div class="sp-card">
            <div class="sp-card-header">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e;">calendar_today</span>
                    Recent Engagement & Attendance Breakdown
                </span>
                <span style="font-size: 12px; color: #5f5e5e;">Term Attendance: <strong style="color: {'#ba1a1a' if att_rate < 70 else '#516600'};">{att_rate:.1f}%</strong></span>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #5f5e5e; font-family: 'Geist', sans-serif;">
                        Recent 14-Day Trajectory
                    </span>
                    <span style="font-size: 12px; font-weight: 600; color: {'#ba1a1a' if rec_att < 70 else '#516600'};">
                        {rec_att:.1f}% (Recent 2-Week Window)
                    </span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #ebefea; border-radius: 9999px; overflow: hidden;">
                    <div style="width: {min(max(rec_att, 0), 100)}%; height: 100%; background-color: {'#ba1a1a' if rec_att < 70 else '#516600'}; border-radius: 9999px;"></div>
                </div>
            </div>

            <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #5f5e5e; font-family: 'Geist', sans-serif; margin-bottom: 8px;">
                Recent Session Log (Latest 10 Sessions)
            </div>
        """, unsafe_allow_html=True)

        if att_history:
            log_cols = st.columns(min(len(att_history[:10]), 10))
            for idx, item in enumerate(att_history[:10]):
                status = item.get("attendance_status", "Present")
                dt = str(item.get("session_date", ""))[-5:]  # MM-DD
                bg = "#dcfce7" if status == "Present" else ("#fef0c7" if status == "Late" else ("#ffdad6" if status == "Absent" else "#e5e9e4"))
                fg = "#14532d" if status == "Present" else ("#93370d" if status == "Late" else ("#93000a" if status == "Absent" else "#474746"))
                with log_cols[idx]:
                    st.markdown(f"""
                    <div style="text-align: center; background-color: {bg}; color: {fg}; border-radius: 6px; padding: 6px 2px; font-size: 11px; font-weight: 600; border: 1px solid rgba(0,0,0,0.05);">
                        <div>{dt}</div>
                        <div style="font-size: 9px; text-transform: uppercase;">{status[:3]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No session attendance logs recorded for this course.")

        st.markdown("</div>", unsafe_allow_html=True)

        # 3. Assignment Status Checklist
        asg_history = profile.get("assignment_history", [])
        st.markdown("""
        <div class="sp-card">
            <div class="sp-card-header">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e;">assignment</span>
                    Course Assignment Submissions
                </span>
            </div>
        """, unsafe_allow_html=True)

        if asg_history:
            for asg in asg_history:
                asg_id = asg.get("assignment_id", "Assignment")
                due = str(asg.get("due_date", ""))[:10]
                sub = asg.get("submitted_at")
                score = asg.get("score")
                max_s = asg.get("max_score", 100.0)

                is_missing = sub is None
                is_late = sub is not None and str(sub) > str(asg.get("due_date", ""))

                if is_missing:
                    status_badge = "<span class='sp-badge sp-badge-high'><span class='sp-badge-dot'></span> Missing (Past Due)</span>"
                    score_display = "<span style='color: #ba1a1a; font-weight: 600;'>0.0 / 100.0</span>"
                    bg_style = "background-color: #fffbfa; border: 1px solid #ffdad6;"
                elif is_late:
                    status_badge = "<span class='sp-badge sp-badge-medium'><span class='sp-badge-dot'></span> Late Submission</span>"
                    score_display = f"<span style='font-family: monospace; font-weight: 600;'>{score:.1f} / {max_s:.0f}</span>" if score is not None else "Pending Grading"
                    bg_style = "background-color: #ffffff; border: 1px solid #ebefea;"
                else:
                    status_badge = "<span class='sp-badge sp-badge-low'><span class='sp-badge-dot'></span> Submitted on Time</span>"
                    score_display = f"<span style='font-family: monospace; font-weight: 600; color: #516600;'>{score:.1f} / {max_s:.0f}</span>" if score is not None else "Pending Grading"
                    bg_style = "background-color: #ffffff; border: 1px solid #ebefea;"

                st.markdown(f"""
                <div style="{bg_style} border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div style="font-weight: 600; font-size: 13px; color: #181d1a;">{asg_id}</div>
                        <div style="font-size: 11px; color: #5f5e5e;">Due: {due} {f'• Submitted: {str(sub)[:16]}' if sub else ''}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        {score_display}
                        {status_badge}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No assignments recorded for this course.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # 1. Why this student was flagged Card (Matches Stitch design)
        st.markdown(f"""
        <div class="sp-card" style="border-top: 4px solid {badge_info['dot']};">
            <h3 style="font-family: 'Geist', sans-serif; font-size: 17px; font-weight: 600; color: #181d1a; margin: 0 0 16px 0;">
                Why this student was flagged
            </h3>
        """, unsafe_allow_html=True)

        if reasons:
            for r in reasons:
                pts = r.get("points", 2)
                lbl = r.get("label", "Engagement indicator")
                desc = r.get("description", "")
                st.markdown(f"""
                <div style="border-bottom: 1px solid #ebefea; padding-bottom: 12px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 13px; font-weight: 600; color: #181d1a;">{lbl}</span>
                        <span class="sp-points-pill">+{pts} pts</span>
                    </div>
                    <p style="font-size: 12px; color: #5f5e5e; margin: 0; line-height: 1.4;">
                        {desc}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #dcfce7; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; color: #14532d; font-size: 13px;">
                ✓ No active risk thresholds triggered. All engagement indicators remain on track.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 2. Suggested Next Step & Support Action Form
        st.markdown(f"""
        <div class="sp-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: #516600;">
                <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">lightbulb</span>
                <h3 style="font-family: 'Geist', sans-serif; font-size: 16px; font-weight: 600; color: #181d1a; margin: 0;">
                    Suggested Next Step
                </h3>
            </div>
            
            <div style="background-color: #f7faf5; border: 1px solid #c4c9ac; border-radius: 8px; padding: 14px; margin-bottom: 16px;">
                <div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #181d1a; line-height: 1.5;">
                    {action_info['description']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Support Action Logging Form
        with st.form(key=f"support_action_form_{sel_id}"):
            st.markdown("<strong style='font-size: 12px; text-transform: uppercase; color: #5f5e5e; font-family: Geist;'>Log Advisor Support Action</strong>", unsafe_allow_html=True)
            action_type_sel = st.selectbox(
                "Action Type",
                [
                    "1:1 Advisor Check-in",
                    "Attendance Nudge Email",
                    "Tutoring Center Referral",
                    "Office Hours Meeting",
                    "Academic Progress Note",
                    "Dean/Department Escalation",
                ],
                index=0,
                key=f"action_type_{sel_id}"
            )
            staff_note_input = st.text_area(
                "Private Staff Note",
                placeholder="Enter confidential advisory notes, next steps, or student discussion outcomes...",
                height=100,
                key=f"staff_note_{sel_id}"
            )
            submit_btn = st.form_submit_button("Add Support Action", type="primary", use_container_width=True)

            if submit_btn:
                if staff_note_input and staff_note_input.strip():
                    success = service.add_intervention_note(
                        student_id=sel_id,
                        course_id=profile.get("course_id", "DATA-101"),
                        action_type=action_type_sel,
                        note=staff_note_input.strip(),
                        staff_user="Dr. Maya"
                    )
                    if success:
                        st.success("✓ Support action logged successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to persist intervention note.")
                else:
                    st.warning("Please enter a note before submitting.")

        # 3. Historical Actions Timeline
        interventions = profile.get("interventions", [])
        st.markdown("""
        <div class="sp-card" style="margin-top: 20px;">
            <div class="sp-card-header" style="margin-bottom: 12px;">
                <span style="font-size: 13px; text-transform: uppercase; color: #5f5e5e; font-family: 'Geist', sans-serif;">
                    Historical Actions & Notes
                </span>
            </div>
        """, unsafe_allow_html=True)

        if interventions:
            for item in interventions:
                act_date = str(item.get("action_date", ""))[:16]
                act_type = item.get("action_type", "Advisory Note")
                note_txt = item.get("outcome_note", "")
                staff = item.get("staff_user", "Advisor")
                st.markdown(f"""
                <div style="background-color: #f7faf5; border: 1px solid #ebefea; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #5f5e5e; margin-bottom: 4px;">
                        <strong>{act_type}</strong>
                        <span>{act_date} ({staff})</span>
                    </div>
                    <p style="font-size: 12px; color: #181d1a; margin: 0; line-height: 1.4;">
                        "{note_txt}"
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-size: 12px; color: #5f5e5e; font-style: italic;">
                No historical support actions logged for this student yet.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    render_disclaimer()
