"""
StudentPulse AI - Configurable Risk Scoring Engine
Evaluates transparent, explainable academic early-warning rules loaded from YAML configuration.
"""

from dataclasses import dataclass, field
import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config/risk_thresholds.yaml")


@dataclass
class TriggeredReason:
    """Structured human-readable explanation for a triggered risk rule."""
    code: str
    label: str
    points: int
    description: str


@dataclass
class StudentRiskEvaluation:
    """Complete explainable risk assessment for a student-course record."""
    student_id: str
    course_id: str
    term: str
    risk_score: int
    risk_level: str  # 'Low', 'Medium', 'High'
    support_level_name: str  # 'On Track', 'Watch', 'Needs Review'
    reasons: List[TriggeredReason] = field(default_factory=list)
    suggested_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation to serializable dict for JSON/database storage."""
        return {
            "student_id": self.student_id,
            "course_id": self.course_id,
            "term": self.term,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "support_level_name": self.support_level_name,
            "reasons": [
                {
                    "code": r.code,
                    "label": r.label,
                    "points": r.points,
                    "description": r.description,
                }
                for r in self.reasons
            ],
            "suggested_action": self.suggested_action,
        }


class RiskEngine:
    """Evaluates student features against institutional threshold rules."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load risk threshold config from YAML file with safe fallback."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error("Failed to parse risk thresholds config: %s", str(e))
                
        # Default fallback config if file missing
        return {
            "risk_rules": {
                "attendance_below": {"threshold_pct": 70.0, "points": 3, "code": "LOW_ATTENDANCE", "label": "Attendance rate below 70%"},
                "recent_attendance_drop": {"threshold_pts": 15.0, "points": 2, "code": "RECENT_ATTENDANCE_DROP", "label": "Recent attendance decline (>=15% drop)"},
                "submission_completion_below": {"threshold_pct": 80.0, "points": 3, "code": "LOW_SUBMISSION_COMPLETION", "label": "Submission completion below 80%"},
                "missing_assignments_min": {"threshold_count": 2, "points": 3, "code": "MISSING_ASSIGNMENTS", "label": "2 or more missing assignments"},
                "late_submission_rate_above": {"threshold_pct": 30.0, "points": 1, "code": "HIGH_LATE_SUBMISSION_RATE", "label": "Late submission rate > 30%"},
                "performance_below": {"threshold_pct": 50.0, "points": 3, "code": "LOW_ACADEMIC_PERFORMANCE", "label": "Assignment or assessment average below 50%"},
            },
            "risk_bands": {
                "low": {"name": "On Track", "key": "Low", "min_score": 0, "max_score": 2},
                "medium": {"name": "Watch", "key": "Medium", "min_score": 3, "max_score": 5},
                "high": {"name": "Needs Review", "key": "High", "min_score": 6, "max_score": 99},
            }
        }

    def evaluate_student(self, row: pd.Series) -> StudentRiskEvaluation:
        """
        Evaluate a single student-course feature row and return transparent score and reasons.
        
        Args:
            row: Series containing student-course engineered features.
            
        Returns:
            StudentRiskEvaluation object with exact points and human-readable signals.
        """
        rules = self.config.get("risk_rules", {})
        reasons: List[TriggeredReason] = []
        total_score = 0

        # Rule 1: Attendance Rate < threshold (default 70%)
        r1 = rules.get("attendance_below", {})
        thresh_att = float(r1.get("threshold_pct", 70.0))
        att_rate = float(row.get("attendance_rate", 100.0))
        if att_rate < thresh_att:
            pts = int(r1.get("points", 3))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r1.get("code", "LOW_ATTENDANCE"),
                label=r1.get("label", f"Attendance rate below {thresh_att:.0f}%"),
                points=pts,
                description=f"Current attendance of {att_rate:.1f}% is below institutional baseline of {thresh_att:.0f}%.",
            ))

        # Rule 2: Recent Attendance Drop >= threshold (default 15 pts)
        r2 = rules.get("recent_attendance_drop", {})
        thresh_drop = float(r2.get("threshold_pts", 15.0))
        recent_att = float(row.get("recent_attendance_rate", att_rate))
        # Drop is measured as term attendance - recent attendance or relative decline
        att_drop = att_rate - recent_att
        if att_drop >= thresh_drop:
            pts = int(r2.get("points", 2))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r2.get("code", "RECENT_ATTENDANCE_DROP"),
                label=r2.get("label", f"Recent attendance decline (>={thresh_drop:.0f}% drop)"),
                points=pts,
                description=f"Recent 14-day attendance ({recent_att:.1f}%) dropped by {att_drop:.1f} percentage points.",
            ))

        # Rule 3: Submission Completion < threshold (default 80%)
        r3 = rules.get("submission_completion_below", {})
        thresh_sub = float(r3.get("threshold_pct", 80.0))
        sub_rate = float(row.get("submission_completion_rate", 100.0))
        if sub_rate < thresh_sub:
            pts = int(r3.get("points", 3))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r3.get("code", "LOW_SUBMISSION_COMPLETION"),
                label=r3.get("label", f"Submission completion below {thresh_sub:.0f}%"),
                points=pts,
                description=f"Completed {sub_rate:.1f}% of scheduled assignments (target: {thresh_sub:.0f}%).",
            ))

        # Rule 4: Missing Assignments >= threshold (default 2)
        r4 = rules.get("missing_assignments_min", {})
        thresh_missing = int(r4.get("threshold_count", 2))
        missing_count = int(row.get("missing_assignments", 0))
        if missing_count >= thresh_missing:
            pts = int(r4.get("points", 3))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r4.get("code", "MISSING_ASSIGNMENTS"),
                label=r4.get("label", f"{thresh_missing} or more missing assignments"),
                points=pts,
                description=f"Student has {missing_count} unsubmitted past-due assignments.",
            ))

        # Rule 5: Late Submission Rate > threshold (default 30%)
        r5 = rules.get("late_submission_rate_above", {})
        thresh_late = float(r5.get("late_submission_rate_above", {}).get("threshold_pct", 30.0) if isinstance(r5.get("late_submission_rate_above"), dict) else r5.get("threshold_pct", 30.0))
        late_rate = float(row.get("late_submission_rate", 0.0))
        if late_rate > thresh_late:
            pts = int(r5.get("points", 1))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r5.get("code", "HIGH_LATE_SUBMISSION_RATE"),
                label=r5.get("label", f"Late submission rate > {thresh_late:.0f}%"),
                points=pts,
                description=f"{late_rate:.1f}% of submissions occurred after the designated deadline.",
            ))

        # Rule 6: Assignment OR Assessment Average < threshold (default 50%)
        r6 = rules.get("performance_below", {})
        thresh_perf = float(r6.get("threshold_pct", 50.0))
        asg_avg = float(row.get("assignment_average", 75.0))
        asm_avg = float(row.get("assessment_average", 75.0))
        if asg_avg < thresh_perf or asm_avg < thresh_perf:
            pts = int(r6.get("points", 3))
            total_score += pts
            reasons.append(TriggeredReason(
                code=r6.get("code", "LOW_ACADEMIC_PERFORMANCE"),
                label=r6.get("label", f"Assignment or assessment average below {thresh_perf:.0f}%"),
                points=pts,
                description=f"Academic performance flag: Assignment avg {asg_avg:.1f}%, Assessment avg {asm_avg:.1f}%.",
            ))

        # Determine Risk Band
        bands = self.config.get("risk_bands", {})
        low_band = bands.get("low", {"max_score": 2, "name": "On Track", "key": "Low"})
        med_band = bands.get("medium", {"max_score": 5, "name": "Watch", "key": "Medium"})
        high_band = bands.get("high", {"name": "Needs Review", "key": "High"})

        if total_score <= low_band.get("max_score", 2):
            risk_level = "Low"
            support_name = low_band.get("name", "On Track")
            suggested_action = "Maintain regular positive academic reinforcement."
        elif total_score <= med_band.get("max_score", 5):
            risk_level = "Medium"
            support_name = med_band.get("name", "Watch")
            suggested_action = "Send supportive check-in nudge or review assignment submissions."
        else:
            risk_level = "High"
            support_name = high_band.get("name", "Needs Review")
            suggested_action = "Schedule 1:1 advisor check-in and coordinate academic support resources."

        return StudentRiskEvaluation(
            student_id=str(row["student_id"]),
            course_id=str(row["course_id"]),
            term=str(row.get("term", "Fall 2026")),
            risk_score=total_score,
            risk_level=risk_level,
            support_level_name=support_name,
            reasons=reasons,
            suggested_action=suggested_action,
        )

    def evaluate_features_dataframe(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate all student-course records in a DataFrame.
        
        Args:
            features_df: DataFrame containing computed features.
            
        Returns:
            DataFrame with risk scores, risk levels, and reasons JSON.
        """
        if features_df.empty:
            return pd.DataFrame()

        eval_records = []
        for _, row in features_df.iterrows():
            evaluation = self.evaluate_student(row)
            eval_dict = evaluation.to_dict()
            import json
            eval_records.append({
                "student_id": eval_dict["student_id"],
                "course_id": eval_dict["course_id"],
                "term": eval_dict["term"],
                "risk_score": eval_dict["risk_score"],
                "risk_level": eval_dict["risk_level"],
                "reasons_json": json.dumps(eval_dict["reasons"]),
                "calculated_at": pd.Timestamp.now(datetime.timezone.utc).isoformat(),
            })

        return pd.DataFrame(eval_records)
