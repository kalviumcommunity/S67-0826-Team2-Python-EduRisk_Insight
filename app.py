"""
StudentPulse AI - Academic Engagement & Early-Risk Platform
Authoritative Streamlit Entry Point.
Faithful implementation of Stitch visual design system and decoupled architecture.
"""

from pathlib import Path
import sys
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.reporting import ReportingService
from src.database import DatabaseManager
from ui.theme import apply_theme
from ui.components.navigation import render_sidebar_nav, render_top_header

# Import all page renderers
from ui.pages.welcome import render_welcome_page
from ui.pages.overview import render_overview_page
from ui.pages.risk_explorer import render_risk_explorer_page
from ui.pages.student_detail import render_student_detail_page
from ui.pages.data_quality import render_data_quality_page
from ui.pages.academic_reports import render_academic_reports_page


# 1. Page Configuration
st.set_page_config(
    page_title="StudentPulse AI — Academic Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Authoritative Stitch Design System Theme
apply_theme()


# 3. Singleton Database & Reporting Service Setup
@st.cache_resource
def get_reporting_service() -> ReportingService:
    """Initialize cached ReportingService."""
    db = DatabaseManager(db_path=Path("data/studentpulse.db"))
    return ReportingService(db_manager=db)


def main():
    service = get_reporting_service()

    # Session State Initialization
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Overview"

    # Render Sidebar Navigation
    current_page = render_sidebar_nav()

    # Render Top Context Header (except on Welcome page)
    if current_page != "Sign In / Welcome":
        render_top_header(current_course="Intro to Data Analytics", current_term="Fall 2026")

    # Multi-Page Routing
    if current_page == "Overview":
        render_overview_page(service)
    elif current_page == "Risk Explorer":
        render_risk_explorer_page(service)
    elif current_page == "Student Detail":
        render_student_detail_page(service)
    elif current_page == "Data Quality":
        render_data_quality_page(service)
    elif current_page == "Academic Reports":
        render_academic_reports_page(service)
    elif current_page == "Sign In / Welcome":
        render_welcome_page()
    else:
        render_overview_page(service)


if __name__ == "__main__":
    main()
