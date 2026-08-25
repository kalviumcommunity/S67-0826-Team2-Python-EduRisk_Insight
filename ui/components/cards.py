"""
StudentPulse AI - UI Card Components
Reusable card elements styled to the Stitch design specifications.
"""

from typing import Optional
import streamlit as st


def render_metric_card(label: str, value: str, icon: str, is_alert: bool = False, subtitle: Optional[str] = None):
    """
    Renders a Stitch-styled headline KPI card.
    
    Args:
        label: Uppercase metadata label.
        value: Tabular metric value.
        icon: Material Symbol icon name.
        is_alert: True if value should be highlighted in error red.
        subtitle: Optional contextual subtext.
    """
    val_class = "sp-metric-value alert" if is_alert else "sp-metric-value"
    icon_color = "#ba1a1a" if is_alert else "#5f5e5e"
    sub_html = f"<div style='font-size: 11px; color: #5f5e5e; margin-top: 4px;'>{subtitle}</div>" if subtitle else ""

    st.markdown(f"""
    <div class="sp-metric-card">
        <div class="sp-metric-label">
            <span>{label}</span>
            <span class="material-symbols-outlined" style="color: {icon_color};">{icon}</span>
        </div>
        <div class="{val_class}">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_signal_callout(title: str, text: str, icon: str = "campaign", is_alert: bool = False):
    """Renders the 'This week's signal' callout card."""
    alert_class = "sp-signal-callout alert" if is_alert else "sp-signal-callout"
    st.markdown(f"""
    <div class="{alert_class}">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">{icon}</span>
            <span style="font-family: 'Geist', sans-serif; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #5f5e5e;">{title}</span>
        </div>
        <p style="font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 500; color: #181d1a; margin: 0; line-height: 1.4;">
            "{text}"
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer():
    """Renders the required institutional ethical disclaimer."""
    st.markdown("""
    <div class="sp-disclaimer">
        <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">verified_user</span>
        <span>
            <strong>Institutional Advisory Note:</strong> StudentPulse provides explainable engagement signals to support qualified staff review. It does not calculate academic grades or make automated disciplinary decisions.
        </span>
    </div>
    """, unsafe_allow_html=True)
