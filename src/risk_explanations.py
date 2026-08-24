"""
StudentPulse AI - Risk Explanation Helper
Provides structured presentation utilities for human-readable risk signals and advisory recommendations.
"""

import json
from typing import Any, Dict, List, Optional


def parse_reasons_json(reasons_raw: Any) -> List[Dict[str, Any]]:
    """
    Safely parses JSON or list representation of triggered risk signals.
    
    Args:
        reasons_raw: JSON string, Python list, or null value.
        
    Returns:
        List of reason dictionaries with code, label, points, and description.
    """
    if not reasons_raw:
        return []
    if isinstance(reasons_raw, list):
        return reasons_raw
    if isinstance(reasons_raw, str):
        try:
            parsed = json.loads(reasons_raw)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    return []


def format_support_badge(risk_level: str) -> Dict[str, str]:
    """
    Returns the visual style attributes (label, bg color, text color, dot color) matching the Stitch design system.
    
    Args:
        risk_level: 'Low', 'Medium', or 'High'
        
    Returns:
        Dictionary with badge styling properties.
    """
    level_lower = str(risk_level).strip().lower()
    if level_lower in ("high", "needs review"):
        return {
            "label": "Needs Review",
            "bg": "#ffdad6",
            "text": "#93000a",
            "dot": "#ba1a1a",
            "border": "#ffb4ab",
            "icon": "warning",
        }
    elif level_lower in ("medium", "watch"):
        return {
            "label": "Watch",
            "bg": "#fef0c7",
            "text": "#93370d",
            "dot": "#d97706",
            "border": "#fde68a",
            "icon": "visibility",
        }
    else:
        return {
            "label": "On Track",
            "bg": "#dcfce7",
            "text": "#14532d",
            "dot": "#16a34a",
            "border": "#bbf7d0",
            "icon": "check_circle",
        }


def get_recommended_action(risk_level: str, reasons: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Generates actionable, ethical academic advisor recommendations based on triggered signals.
    
    Args:
        risk_level: 'Low', 'Medium', or 'High'
        reasons: List of active risk reasons.
        
    Returns:
        Dictionary with action title, description, and primary button CTA.
    """
    codes = {r.get("code") for r in reasons}

    if "LOW_ATTENDANCE" in codes and "MISSING_ASSIGNMENTS" in codes:
        return {
            "title": "Comprehensive Support Check-In",
            "description": "Student is experiencing concurrent attendance and assignment completion signals. Recommend a holistic 1:1 conversation to discuss pacing and campus academic tutoring resources.",
            "cta": "Schedule 1:1 Check-in",
            "secondary_cta": "Send Supportive Nudge",
        }
    elif "MISSING_ASSIGNMENTS" in codes or "LOW_SUBMISSION_COMPLETION" in codes:
        return {
            "title": "Assignment Completion Review",
            "description": "Multiple past-due submissions detected. Review missing items with student and offer office hours support or assignment submission guidance.",
            "cta": "Review Missing Work",
            "secondary_cta": "Message Student",
        }
    elif "RECENT_ATTENDANCE_DROP" in codes or "LOW_ATTENDANCE" in codes:
        return {
            "title": "Attendance & Engagement Inquiry",
            "description": "Recent attendance drop identified over the last two weeks. Send a friendly check-in email to inquire if any schedule conflicts or support needs have arisen.",
            "cta": "Send Attendance Nudge",
            "secondary_cta": "Review Lecture Logs",
        }
    elif "LOW_ACADEMIC_PERFORMANCE" in codes:
        return {
            "title": "Subject-Matter Tutoring Referral",
            "description": "Assessment scores indicate conceptual difficulty. Recommend connecting student with peer tutoring or supplementary review sessions.",
            "cta": "Refer to Tutoring",
            "secondary_cta": "Review Grade Breakdown",
        }
    else:
        return {
            "title": "Positive Reinforcement",
            "description": "Student engagement and performance metrics are on track. Continue standard curriculum pacing and positive reinforcement.",
            "cta": "View Full Profile",
            "secondary_cta": "Add Note",
        }
