"""
StudentPulse AI - Reporting Service Layer
Provides the decoupled service API consumed by the Streamlit user interface.
Ensures zero business/SQL logic is embedded inside UI presentation components.
"""

from dataclasses import dataclass
import datetime
import json
import logging
from typing import Any, Dict, List, Optional
import pandas as pd

from src.database import DatabaseManager
from src.insights import generate_cohort_insights, InsightFinding
from src.risk_explanations import parse_reasons_json

logger = logging.getLogger(__name__)


@dataclass
class OverviewMetrics:
    """Headline metrics for dashboard overview display."""
    total_enrolled: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_attendance_rate: float
    avg_submission_completion: float
    avg_assessment_score: float
    avg_assignment_score: float


class ReportingService:
    """Central service providing reporting datasets and insights for UI components."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Returns available terms, courses, and sections for UI filter dropdowns."""
        courses = ["All"]
        terms = ["All"]
        sections = ["All"]

        try:
            res_c = self.db.execute_query("SELECT DISTINCT course_id FROM enrolments ORDER BY course_id")
            if res_c:
                courses.extend([r["course_id"] for r in res_c])

            res_t = self.db.execute_query("SELECT DISTINCT term FROM enrolments ORDER BY term DESC")
            if res_t:
                terms.extend([r["term"] for r in res_t])

            res_s = self.db.execute_query("SELECT DISTINCT section FROM enrolments ORDER BY section")
            if res_s:
                sections.extend([r["section"] for r in res_s])
        except Exception as e:
            logger.warning("Could not fetch filter options: %s", str(e))

        return {
            "courses": courses,
            "terms": terms,
            "sections": sections,
            "risk_levels": ["All", "Needs Review", "Watch", "On Track"],
        }

    def get_overview_metrics(self, filters: Optional[Dict[str, Any]] = None) -> OverviewMetrics:
        """
        Calculates high-level KPI card metrics for the filtered cohort.
        
        Args:
            filters: Optional dict with 'term', 'course_id', 'section'.
            
        Returns:
            OverviewMetrics object.
        """
        filters = filters or {}
        conditions = []
        params = []

        if filters.get("term") and filters["term"] != "All":
            conditions.append("f.term = ?")
            params.append(filters["term"])
        if filters.get("course_id") and filters["course_id"] != "All":
            conditions.append("f.course_id = ?")
            params.append(filters["course_id"])
        if filters.get("section") and filters["section"] != "All":
            conditions.append("f.section = ?")
            params.append(filters["section"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT
                COUNT(DISTINCT f.student_id) AS total_enrolled,
                SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
                SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
                SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
                AVG(f.attendance_rate) AS avg_attendance,
                AVG(f.submission_completion_rate) AS avg_submission,
                AVG(f.assessment_average) AS avg_assessment,
                AVG(f.assignment_average) AS avg_assignment
            FROM student_course_features f
            LEFT JOIN risk_assessments r
                ON f.student_id = r.student_id
                AND f.course_id = r.course_id
                AND f.term = r.term
            {where_clause}
        """

        try:
            results = self.db.execute_query(query, tuple(params) if params else None)
            if results and results[0]["total_enrolled"] is not None:
                r = results[0]
                return OverviewMetrics(
                    total_enrolled=int(r["total_enrolled"] or 0),
                    high_risk_count=int(r["high_risk_count"] or 0),
                    medium_risk_count=int(r["medium_risk_count"] or 0),
                    low_risk_count=int(r["low_risk_count"] or 0),
                    avg_attendance_rate=round(float(r["avg_attendance"] or 0.0), 1),
                    avg_submission_completion=round(float(r["avg_submission"] or 0.0), 1),
                    avg_assessment_score=round(float(r["avg_assessment"] or 0.0), 1),
                    avg_assignment_score=round(float(r["avg_assignment"] or 0.0), 1),
                )
        except Exception as e:
            logger.error("Failed to compute overview metrics: %s", str(e))

        return OverviewMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)

    def get_risk_students(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Retrieves filtered student records for the Risk Explorer table.
        
        Args:
            filters: Dict containing optional filters ('term', 'course_id', 'section', 'risk_level', 'search').
            
        Returns:
            DataFrame containing student risk details and parsed reasons.
        """
        filters = filters or {}
        conditions = []
        params = []

        if filters.get("term") and filters["term"] != "All":
            conditions.append("term = ?")
            params.append(filters["term"])
        if filters.get("course_id") and filters["course_id"] != "All":
            conditions.append("course_id = ?")
            params.append(filters["course_id"])
        if filters.get("section") and filters["section"] != "All":
            conditions.append("section = ?")
            params.append(filters["section"])
        if filters.get("risk_level") and filters["risk_level"] != "All":
            # Map UI label to DB value
            lvl = filters["risk_level"]
            db_lvl = "High" if "Review" in lvl else ("Medium" if "Watch" in lvl else ("Low" if "Track" in lvl else lvl))
            conditions.append("risk_level = ?")
            params.append(db_lvl)
        if filters.get("search"):
            conditions.append("(student_id LIKE ? OR program LIKE ?)")
            q = f"%{filters['search'].strip()}%"
            params.extend([q, q])
        if filters.get("attendance_min") is not None:
            conditions.append("attendance_rate >= ?")
            params.append(float(filters["attendance_min"]))
        if filters.get("attendance_max") is not None:
            conditions.append("attendance_rate <= ?")
            params.append(float(filters["attendance_max"]))
        if filters.get("submission_status") and filters["submission_status"] != "All":
            if filters["submission_status"] == "Incomplete":
                conditions.append("submission_completion_rate < 80")
            elif filters["submission_status"] == "Complete":
                conditions.append("submission_completion_rate >= 80")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM v_risk_explorer {where_clause} ORDER BY risk_score DESC, student_id ASC"

        try:
            df = self.db.query_dataframe(query, tuple(params) if params else None)
            if not df.empty and "reasons_json" in df.columns:
                df["parsed_reasons"] = df["reasons_json"].apply(parse_reasons_json)
                df["primary_signal_labels"] = df["parsed_reasons"].apply(
                    lambda rs: [r.get("label", "") for r in rs] if rs else ["No active risk signals"]
                )
            return df
        except Exception as e:
            logger.error("Failed to query risk students: %s", str(e))
            return pd.DataFrame()

    def get_student_detail(self, student_id: str, course_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed individual profile including history, attendance logs, and assignment records.
        
        Args:
            student_id: Pseudonymous student identifier.
            course_id: Optional course code.
            
        Returns:
            Dictionary containing student profile, feature metrics, and sub-table activity.
        """
        params = [student_id]
        course_clause = ""
        if course_id:
            course_clause = "AND course_id = ?"
            params.append(course_id)

        detail_query = f"SELECT * FROM v_student_detail WHERE student_id = ? {course_clause} LIMIT 1"
        try:
            rows = self.db.execute_query(detail_query, tuple(params))
            if not rows:
                return None
            profile = dict(rows[0])
            profile["parsed_reasons"] = parse_reasons_json(profile.get("reasons_json"))

            # Fetch attendance logs
            att_query = "SELECT session_date, attendance_status FROM attendance WHERE student_id = ? ORDER BY session_date DESC LIMIT 30"
            profile["attendance_history"] = self.db.execute_query(att_query, (student_id,))

            # Fetch assignment submissions
            asg_query = "SELECT assignment_id, due_date, submitted_at, score, max_score FROM assignments WHERE student_id = ? ORDER BY due_date ASC"
            profile["assignment_history"] = self.db.execute_query(asg_query, (student_id,))

            # Fetch assessments
            asm_query = "SELECT assessment_type, assessment_date, score, max_score FROM assessments WHERE student_id = ? ORDER BY assessment_date ASC"
            profile["assessment_history"] = self.db.execute_query(asm_query, (student_id,))

            # Fetch interventions
            int_query = "SELECT action_date, action_type, outcome_note, staff_user FROM interventions WHERE student_id = ? ORDER BY action_date DESC"
            profile["interventions"] = self.db.execute_query(int_query, (student_id,))

            return profile
        except Exception as e:
            logger.error("Failed to get student detail for %s: %s", student_id, str(e))
            return None

    def get_course_summary(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Returns course/section comparison summary table."""
        filters = filters or {}
        conditions = []
        params = []

        if filters.get("term") and filters["term"] != "All":
            conditions.append("term = ?")
            params.append(filters["term"])
        if filters.get("course_id") and filters["course_id"] != "All":
            conditions.append("course_id = ?")
            params.append(filters["course_id"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM v_course_risk_summary {where_clause} ORDER BY high_risk_pct DESC"

        try:
            return self.db.query_dataframe(query, tuple(params) if params else None)
        except Exception as e:
            logger.error("Failed to fetch course summary: %s", str(e))
            return pd.DataFrame()

    def get_top_insights(self, filters: Optional[Dict[str, Any]] = None) -> List[InsightFinding]:
        """Dynamically computes the top 3 cohort findings."""
        filters = filters or {}
        features_df = self.get_risk_students(filters)
        risk_df = features_df[["student_id", "course_id", "term", "risk_level"]].copy() if not features_df.empty else pd.DataFrame()
        return generate_cohort_insights(
            features_df=features_df,
            risk_df=risk_df,
            selected_course=filters.get("course_id"),
            selected_section=filters.get("section"),
        )

    def get_weekly_trends(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Aggregates weekly attendance and submission completion rates for trend charts."""
        filters = filters or {}
        attendance_conditions = ["1=1"]
        assignment_conditions = ["1=1"]
        attendance_params = []
        assignment_params = []

        if filters.get("course_id") and filters["course_id"] != "All":
            attendance_conditions.append("a.course_id = ?")
            attendance_params.append(filters["course_id"])
            assignment_conditions.append("asg.course_id = ?")
            assignment_params.append(filters["course_id"])
        if filters.get("term") and filters["term"] != "All":
            # Terms are not stored on attendance/assignment facts, so resolve the
            # selected term to the enrolled course/student population.
            attendance_conditions.append("EXISTS (SELECT 1 FROM enrolments e WHERE e.student_id = a.student_id AND e.course_id = a.course_id AND e.term = ?)")
            attendance_params.append(filters["term"])
            assignment_conditions.append("EXISTS (SELECT 1 FROM enrolments e WHERE e.student_id = asg.student_id AND e.course_id = asg.course_id AND e.term = ?)")
            assignment_params.append(filters["term"])
        if filters.get("section") and filters["section"] != "All":
            attendance_conditions.append("EXISTS (SELECT 1 FROM enrolments e WHERE e.student_id = a.student_id AND e.course_id = a.course_id AND e.section = ?)")
            attendance_params.append(filters["section"])
            assignment_conditions.append("EXISTS (SELECT 1 FROM enrolments e WHERE e.student_id = asg.student_id AND e.course_id = asg.course_id AND e.section = ?)")
            assignment_params.append(filters["section"])

        attendance_query = f"""
            SELECT
                strftime('%Y-W%W', session_date) AS week,
                ROUND(100.0 * SUM(CASE WHEN attendance_status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(*), 1) AS attendance_rate
            FROM attendance a
            WHERE {' AND '.join(attendance_conditions)}
            GROUP BY strftime('%Y-W%W', session_date)
        """
        assignment_query = f"""
            SELECT
                strftime('%Y-W%W', due_date) AS week,
                ROUND(100.0 * SUM(CASE WHEN submitted_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS submission_completion_rate
            FROM assignments asg
            WHERE {' AND '.join(assignment_conditions)}
            GROUP BY strftime('%Y-W%W', due_date)
        """
        try:
            attendance_df = self.db.query_dataframe(attendance_query, tuple(attendance_params) if attendance_params else None)
            assignment_df = self.db.query_dataframe(assignment_query, tuple(assignment_params) if assignment_params else None)
            if attendance_df.empty and assignment_df.empty:
                return pd.DataFrame(columns=["week", "attendance_rate", "submission_completion_rate"])
            result = pd.merge(attendance_df, assignment_df, on="week", how="outer").sort_values("week")
            return result.reset_index(drop=True)
        except Exception as e:
            logger.error("Failed to compute weekly trends: %s", str(e))
            return pd.DataFrame()

    def get_data_quality_report(self) -> pd.DataFrame:
        """Fetches the latest data quality audit report."""
        query = """
            SELECT * FROM data_quality_reports 
            WHERE run_id = (SELECT run_id FROM data_quality_reports ORDER BY id DESC LIMIT 1)
            ORDER BY severity DESC, rule_code ASC
        """
        try:
            return self.db.query_dataframe(query)
        except Exception as e:
            logger.error("Failed to fetch data quality report: %s", str(e))
            return pd.DataFrame()

    def add_intervention_note(self, student_id: str, course_id: str, action_type: str, note: str, staff_user: str = "Dr. Maya") -> bool:
        """Saves a new staff intervention note."""
        query = """
            INSERT INTO interventions (student_id, course_id, action_date, action_type, outcome_note, staff_user)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute(query, (
                    student_id,
                    course_id,
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    action_type,
                    note,
                    staff_user
                ))
            return True
        except Exception as e:
            logger.error("Failed to insert intervention note: %s", str(e))
            return False
