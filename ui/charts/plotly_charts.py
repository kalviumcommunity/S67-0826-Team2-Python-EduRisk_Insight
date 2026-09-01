"""
StudentPulse AI - Plotly Chart Components
Renders authoritative academic charts strictly styled to the Stitch visual language.
"""

from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go


def get_stitch_layout(title: str = "", height: int = 320) -> dict:
    """Returns standard Plotly layout configuration enforcing the Stitch design system."""
    return dict(
        title=dict(
            text=title,
            font=dict(family="Geist, sans-serif", size=16, color="#181d1a"),
            x=0.0,
            y=0.96,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        margin=dict(l=40, r=20, t=40, b=40),
        height=height,
        font=dict(family="Inter, sans-serif", size=12, color="#5f5e5e"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#ebefea",
            gridwidth=1,
            linecolor="#c4c9ac",
            tickfont=dict(family="Geist, monospace", size=11, color="#5f5e5e"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#ebefea",
            gridwidth=1,
            linecolor="#c4c9ac",
            tickfont=dict(family="Geist, monospace", size=11, color="#5f5e5e"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Inter, sans-serif", size=11, color="#181d1a"),
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#c4c9ac",
            font=dict(family="Inter, sans-serif", size=12, color="#181d1a"),
        ),
    )


def create_engagement_trend_chart(weekly_df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Render weekly attendance and submission-completion trends."""
    fig = go.Figure()

    if weekly_df is not None and not weekly_df.empty and "week" in weekly_df.columns:
        x_vals = weekly_df["week"].tolist()
        att_vals = weekly_df.get("attendance_rate", pd.Series(dtype=float)).tolist()
        sub_vals = weekly_df.get("submission_completion_rate", pd.Series(dtype=float)).tolist()
    else:
        x_vals = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"]
        att_vals = [92.4, 91.0, 88.5, 89.2, 85.0, 84.1, 82.5, 80.2, 79.4, 81.2]
        sub_vals = [96, 95, 94, 92, 90, 88, 87, 84, 82, 85]

    if any(v is not None for v in att_vals):
        fig.add_trace(go.Scatter(
            x=x_vals, y=att_vals, mode="lines+markers", name="Attendance",
            line=dict(color="#516600", width=3, shape="spline"),
            marker=dict(size=6, color="#516600"),
            hovertemplate="Week %{x}<br>Attendance: <b>%{y:.1f}%</b><extra></extra>",
        ))
    if any(v is not None for v in sub_vals):
        fig.add_trace(go.Scatter(
            x=x_vals, y=sub_vals, mode="lines+markers", name="Submission completion",
            line=dict(color="#49657a", width=2.5, shape="spline"),
            marker=dict(size=5, color="#49657a"),
            hovertemplate="Week %{x}<br>Submission completion: <b>%{y:.1f}%</b><extra></extra>",
        ))

    fig.add_hline(
        y=70.0, line_dash="dash", line_color="#ba1a1a", line_width=1.5,
        annotation_text="Institutional Baseline (70%)", annotation_position="bottom right",
        annotation_font=dict(family="Geist, sans-serif", size=10, color="#ba1a1a"),
    )
    layout = get_stitch_layout("", height=280)
    layout["yaxis"]["range"] = [40, 100]
    layout["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**layout)
    return fig

def create_risk_distribution_bar(low_count: int, med_count: int, high_count: int) -> go.Figure:
    """
    Renders the Support Level Distribution horizontal progress bar.
    
    Args:
        low_count: Count of On Track students.
        med_count: Count of Watch students.
        high_count: Count of Needs Review students.
        
    Returns:
        Plotly Figure.
    """
    total = max(low_count + med_count + high_count, 1)
    p_low = round(low_count / total * 100.0, 1)
    p_med = round(med_count / total * 100.0, 1)
    p_high = round(high_count / total * 100.0, 1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=["Cohort"],
        x=[p_low],
        name=f"On Track ({low_count})",
        orientation="h",
        marker=dict(color="#516600"),
        text=[f"{p_low}%"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", family="Geist", size=11, weight="bold"),
        hovertemplate="On Track: %{x}% (" + str(low_count) + " students)<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        y=["Cohort"],
        x=[p_med],
        name=f"Watch ({med_count})",
        orientation="h",
        marker=dict(color="#d97706"),
        text=[f"{p_med}%" if p_med > 5 else ""],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", family="Geist", size=11, weight="bold"),
        hovertemplate="Watch: %{x}% (" + str(med_count) + " students)<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        y=["Cohort"],
        x=[p_high],
        name=f"Needs Review ({high_count})",
        orientation="h",
        marker=dict(color="#ba1a1a"),
        text=[f"{p_high}%" if p_high > 5 else ""],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", family="Geist", size=11, weight="bold"),
        hovertemplate="Needs Review: %{x}% (" + str(high_count) + " students)<extra></extra>",
    ))

    layout = get_stitch_layout("", height=100)
    layout["barmode"] = "stack"
    layout["showlegend"] = True
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    layout["xaxis"] = dict(showgrid=False, showticklabels=False, range=[0, 100])
    layout["yaxis"] = dict(showgrid=False, showticklabels=False)
    fig.update_layout(**layout)
    return fig


def create_course_comparison_bar(course_summary_df: pd.DataFrame) -> go.Figure:
    """
    Renders Course Disparity Comparison Chart for Academic Reports.
    
    Args:
        course_summary_df: DataFrame with course comparison metrics.
        
    Returns:
        Plotly Figure.
    """
    fig = go.Figure()
    if course_summary_df.empty:
        return fig

    # Group by course_id
    grouped = course_summary_df.groupby("course_id").agg({
        "enrolled_count": "sum",
        "high_risk_count": "sum",
        "medium_risk_count": "sum",
        "low_risk_count": "sum",
    }).reset_index()

    grouped["high_risk_pct"] = (grouped["high_risk_count"] / grouped["enrolled_count"] * 100.0).round(1)
    grouped["med_risk_pct"] = (grouped["medium_risk_count"] / grouped["enrolled_count"] * 100.0).round(1)

    courses = grouped["course_id"].tolist()

    fig.add_trace(go.Bar(
        x=courses,
        y=grouped["high_risk_pct"],
        name="Needs Review %",
        marker=dict(color="#ba1a1a"),
        hovertemplate="%{x}<br>Needs Review: <b>%{y:.1f}%</b><extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=courses,
        y=grouped["med_risk_pct"],
        name="Watch %",
        marker=dict(color="#d97706"),
        hovertemplate="%{x}<br>Watch: <b>%{y:.1f}%</b><extra></extra>",
    ))

    layout = get_stitch_layout("Risk Disparity by Academic Course", height=320)
    layout["barmode"] = "group"
    layout["yaxis"]["ticksuffix"] = "%"
    layout["yaxis"]["title"] = "Proportion of Enrolled Cohort (%)"
    fig.update_layout(**layout)
    return fig
