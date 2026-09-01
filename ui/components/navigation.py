"""
StudentPulse AI - Navigation Component
Renders the Stitch-styled sidebar navigation, top bar, and breadcrumb header.
"""

from typing import Dict, Tuple
import streamlit as st


def render_sidebar_nav() -> str:
    """
    Renders the custom Stitch sidebar with brand header, navigation links, and advisor profile.
    
    Returns:
        The selected page name.
    """
    with st.sidebar:
        # Brand Header
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 4px 8px;">
            <div style="background-color: #516600; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <span class="material-symbols-outlined" style="color: #c6f500; font-size: 22px;">pulse_alert</span>
            </div>
            <div>
                <h1 style="font-family: 'Geist', sans-serif; font-size: 18px; font-weight: 700; color: #516600; margin: 0; line-height: 1.2;">StudentPulse</h1>
                <p style="font-family: 'Inter', sans-serif; font-size: 11px; color: #5f5e5e; margin: 0;">Academic Intelligence</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Options
        pages = [
            ("Overview", "dashboard"),
            ("Risk Explorer", "warning"),
            ("Student Detail", "group"),
            ("Data Quality", "database"),
            ("Academic Reports", "assessment"),
            ("Sign In / Welcome", "lock_open"),
        ]

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Overview"

        for page_name, icon in pages:
            is_active = st.session_state["current_page"] == page_name
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{page_name}", key=f"nav_{page_name}", use_container_width=True, type=btn_style):
                st.session_state["current_page"] = page_name
                st.rerun()

        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)

        # Advisor Profile Footer
        st.markdown("""
        <div style="margin-top: auto; padding: 12px; background-color: #ffffff; border: 1px solid #c4c9ac; border-radius: 10px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background-color: #ebefea; display: flex; align-items: center; justify-content: center; font-family: 'Geist', sans-serif; font-weight: 600; color: #516600; font-size: 12px;">
                DM
            </div>
            <div style="flex: 1; overflow: hidden;">
                <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #181d1a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Dr. Maya</div>
                <div style="font-family: 'Inter', sans-serif; font-size: 10px; color: #5f5e5e;">Senior Academic Advisor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("current_page", "Overview")


def render_top_header(current_course: str = "Intro to Data Analytics", current_term: str = "Fall 2026"):
    """Renders the top header bar with term indicator and search context."""
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0 16px 0; border-bottom: 1px solid #c4c9ac; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e;">{current_term}</span>
            <span style="color: #c4c9ac;">|</span>
            <span style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #516600; border-bottom: 2px solid #516600; padding-bottom: 2px;">{current_course}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> System Live</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
