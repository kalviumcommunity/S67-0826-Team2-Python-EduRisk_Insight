"""
StudentPulse AI - Welcome & Sign-In Page
Landing portal matching Stitch welcome_sign_in screen.
"""

import streamlit as st
from ui.components.cards import render_disclaimer


def render_welcome_page():
    """Renders the clean institutional welcome and prototype sign-in screen."""
    st.markdown("""
    <div style="max-width: 480px; margin: 40px auto; background-color: #ffffff; border: 1px solid #c4c9ac; border-radius: 16px; padding: 40px; box-shadow: 0px 4px 20px rgba(0,0,0,0.03);">
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="width: 56px; height: 56px; border-radius: 12px; background-color: #516600; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                <span class="material-symbols-outlined" style="color: #c6f500; font-size: 32px;">pulse_alert</span>
            </div>
            <h1 style="font-family: 'Geist', sans-serif; font-size: 26px; font-weight: 700; color: #181d1a; margin-bottom: 6px;">StudentPulse AI</h1>
            <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #5f5e5e; margin: 0;">Academic Engagement & Early-Risk Insights</p>
        </div>

        <div style="background-color: #f7faf5; border: 1px solid #c4c9ac; border-radius: 10px; padding: 16px; margin-bottom: 24px;">
            <div style="font-family: 'Geist', sans-serif; font-size: 12px; font-weight: 600; text-transform: uppercase; color: #516600; margin-bottom: 4px;">Verified Advisor Role</div>
            <div style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #181d1a;">Dr. Maya</div>
            <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #5f5e5e;">Faculty of Computing & Data Sciences</div>
        </div>

        <div style="margin-bottom: 24px;">
            <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; line-height: 1.5;">
                Welcome to the institutional early-warning analytics portal. Access real-time student engagement signals, submission trends, and rule-based risk indicators.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Launch Advisor Dashboard →", type="primary", use_container_width=True, key="launch_dash_btn"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    render_disclaimer()
