"""StudentPulse AI filter rail component."""

from typing import Any, Dict
import streamlit as st
from src.reporting import ReportingService


def render_filter_rail(service: ReportingService) -> Dict[str, Any]:
    """Render PRD-aligned Risk Explorer filters and return normalized selections."""
    options = service.get_filter_options()

    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        course = st.selectbox("Course", options["courses"], index=0, key="filter_course")
    with c2:
        term = st.selectbox("Term", options["terms"], index=0, key="filter_term")
    with c3:
        section = st.selectbox("Section", options["sections"], index=0, key="filter_section")
    with c4:
        risk_level = st.selectbox("Support Level", options["risk_levels"], index=0, key="filter_risk_level")

    c5, c6, c7 = st.columns([2, 2, 2])
    with c5:
        search = st.text_input("Search Student ID", placeholder="e.g. STU-1045", key="filter_search")
    with c6:
        attendance_min, attendance_max = st.slider(
            "Attendance range (%)", 0, 100, (0, 100), key="filter_attendance_range"
        )
    with c7:
        submission_status = st.selectbox(
            "Submission Status", ["All", "Complete", "Incomplete"], index=0, key="filter_submission_status"
        )

    return {
        "course_id": course,
        "term": term,
        "section": section,
        "risk_level": risk_level,
        "search": search.strip() if search else None,
        "attendance_min": attendance_min,
        "attendance_max": attendance_max,
        "submission_status": submission_status,
    }
