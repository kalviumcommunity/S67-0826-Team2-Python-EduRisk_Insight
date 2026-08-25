"""
StudentPulse AI - UI Theme & Design System
Applies the authoritative Stitch design specifications: warm off-white surface, chartreuse primary,
refined typography (Geist + Inter), restrained borders, and accessible high-contrast indicators.
"""

import streamlit as st

STITCH_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
    --sp-surface: #f7faf5;
    --sp-surface-card: #ffffff;
    --sp-surface-container: #ebefea;
    --sp-surface-container-low: #f1f5ef;
    --sp-surface-container-high: #e5e9e4;
    --sp-on-surface: #181d1a;
    --sp-on-surface-variant: #444933;
    --sp-secondary: #5f5e5e;
    --sp-outline: #747a61;
    --sp-outline-variant: #c4c9ac;
    --sp-border-subtle: #d9ddd8;
    
    --sp-primary: #516600;
    --sp-primary-container: #c6f500;
    --sp-on-primary-container: #161e00;
    
    --sp-error: #ba1a1a;
    --sp-error-container: #ffdad6;
    --sp-on-error-container: #93000a;
    
    --sp-warning: #d97706;
    --sp-warning-container: #fef0c7;
    --sp-on-warning-container: #93370d;
    
    --sp-success: #16a34a;
    --sp-success-container: #dcfce7;
    --sp-on-success-container: #14532d;
}

/* Global Application Typography & Background */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--sp-surface) !important;
    color: var(--sp-on-surface) !important;
}

/* Clean Header & Navigation Overrides */
header[data-testid="stHeader"] {
    background-color: var(--sp-surface) !important;
    border-bottom: 1px solid var(--sp-outline-variant) !important;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: var(--sp-surface) !important;
    border-right: 1px solid var(--sp-outline-variant) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
}

/* Headings */
h1, h2, h3, h4, .font-geist {
    font-family: 'Geist', sans-serif !important;
    font-weight: 600 !important;
    color: var(--sp-on-surface) !important;
    letter-spacing: -0.01em !important;
}

/* Tabular Numerals */
.tabular-nums, .font-mono, td, th {
    font-variant-numeric: tabular-nums !important;
}

/* Material Symbols Helper */
.material-symbols-outlined {
    font-family: 'Material Symbols Outlined' !important;
    font-weight: normal;
    font-style: normal;
    font-size: 20px;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    vertical-align: middle;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.material-symbols-outlined.filled {
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* Stitch Metric Card */
.sp-metric-card {
    background-color: #ffffff;
    border: 1px solid var(--sp-outline-variant);
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.02);
    transition: box-shadow 0.2s ease, transform 0.1s ease;
    height: 100%;
}

.sp-metric-card:hover {
    box-shadow: 0px 4px 12px rgba(23, 23, 23, 0.06);
}

.sp-metric-label {
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--sp-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.sp-metric-value {
    font-family: 'Geist', sans-serif;
    font-size: 36px;
    font-weight: 700;
    line-height: 1.1;
    color: var(--sp-on-surface);
}

.sp-metric-value.alert {
    color: var(--sp-error);
}

/* Stitch Card Container */
.sp-card {
    background-color: #ffffff;
    border: 1px solid var(--sp-outline-variant);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.02);
    margin-bottom: 24px;
}

.sp-card-header {
    font-family: 'Geist', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: var(--sp-on-surface);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Status Badges & Pills */
.sp-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
}

.sp-badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 9999px;
}

.sp-badge-high {
    background-color: var(--sp-error-container);
    color: var(--sp-on-error-container);
    border: 1px solid #ffb4ab;
}
.sp-badge-high .sp-badge-dot { background-color: var(--sp-error); }

.sp-badge-medium {
    background-color: var(--sp-warning-container);
    color: var(--sp-on-warning-container);
    border: 1px solid #fde68a;
}
.sp-badge-medium .sp-badge-dot { background-color: var(--sp-warning); }

.sp-badge-low {
    background-color: var(--sp-success-container);
    color: var(--sp-on-success-container);
    border: 1px solid #bbf7d0;
}
.sp-badge-low .sp-badge-dot { background-color: var(--sp-success); }

/* Reason Tag Chip */
.sp-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid var(--sp-outline-variant);
    background-color: var(--sp-surface-container-low);
    font-size: 11px;
    color: var(--sp-on-surface);
    margin: 2px 4px 2px 0;
}

/* Points Pill (+3 pts) */
.sp-points-pill {
    background-color: var(--sp-surface-container-high);
    color: var(--sp-secondary);
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
}

/* Signal Callout Box */
.sp-signal-callout {
    background-color: #ffffff;
    border: 1px solid var(--sp-outline-variant);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

.sp-signal-callout::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background-color: var(--sp-primary);
}

.sp-signal-callout.alert::before {
    background-color: var(--sp-error);
}

/* Disclaimer Banner */
.sp-disclaimer {
    background-color: var(--sp-surface-container-low);
    border: 1px solid var(--sp-outline-variant);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 12px;
    color: var(--sp-secondary);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 24px;
}

/* Primary Button Styling */
button[kind="primary"], .stButton > button[kind="primary"] {
    background-color: var(--sp-primary-container) !important;
    color: var(--sp-on-primary-container) !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
}

button[kind="primary"]:hover {
    background-color: var(--sp-primary) !important;
    color: #ffffff !important;
}

/* Secondary Button */
button[kind="secondary"], .stButton > button {
    background-color: #ffffff !important;
    color: var(--sp-on-surface) !important;
    border: 1px solid var(--sp-outline-variant) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

button[kind="secondary"]:hover, .stButton > button:hover {
    background-color: var(--sp-surface-container-low) !important;
    border-color: var(--sp-outline) !important;
}

/* Form input fields */
.stSelectbox > div > div, .stTextInput > div > div {
    background-color: #ffffff !important;
    border: 1px solid var(--sp-outline-variant) !important;
    border-radius: 8px !important;
}

/* Progress bar overrides */
.stProgress > div > div > div > div {
    background-color: var(--sp-primary) !important;
}

/* Custom Table Styles */
.sp-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.sp-table th {
    background-color: var(--sp-surface-container-low);
    color: var(--sp-secondary);
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 12px 16px;
    border-bottom: 1px solid var(--sp-outline-variant);
    text-align: left;
}

.sp-table td {
    padding: 14px 16px;
    border-bottom: 1px solid var(--sp-outline-variant);
    color: var(--sp-on-surface);
}

.sp-table tr:hover td {
    background-color: var(--sp-surface-container-low);
}

/* Streamlit dataframe/table borders */
[data-testid="stDataFrame"] {
    border: 1px solid var(--sp-outline-variant);
    border-radius: 12px;
    overflow: hidden;
}
</style>
"""


def apply_theme():
    """Applies the Stitch design CSS system into the Streamlit session."""
    st.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)
