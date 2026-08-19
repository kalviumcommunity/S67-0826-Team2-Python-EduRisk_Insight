"""
StudentPulse AI - Data Quality & Validation Engine
Implements 14 comprehensive validation rules to safeguard academic reporting integrity.
"""

from dataclasses import asdict, dataclass, field
import datetime
import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

VALID_ATTENDANCE_STATUSES = {"Present", "Late", "Absent", "Excused"}


@dataclass
class QualityRuleResult:
    """Represents the audit outcome for an individual data quality rule."""
    table_name: str
    rule_code: str
    rule_name: str
    status: str  # 'PASS', 'WARN', 'FAIL'
    severity: str  # 'High', 'Medium', 'Low'
    records_evaluated: int
    records_failed: int
    failure_rate: float
    remediation_note: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationReport:
    """Structured report summarizing data quality across all ingested datasets."""
    run_id: str
    evaluated_at: str
    overall_health_pct: float
    total_rules_evaluated: int
    passed_rules: int
    warned_rules: int
    failed_rules: int
    total_records_failed: int
    rule_results: List[QualityRuleResult] = field(default_factory=list)
    table_summaries: Dict[str, dict] = field(default_factory=dict)
    has_blocking_errors: bool = False

    def to_dataframe(self) -> pd.DataFrame:
        """Convert rule results into a DataFrame for SQL storage or display."""
        records = []
        for r in self.rule_results:
            records.append({
                "run_id": self.run_id,
                "table_name": r.table_name,
                "rule_code": r.rule_code,
                "rule_name": r.rule_name,
                "status": r.status,
                "severity": r.severity,
                "records_evaluated": r.records_evaluated,
                "records_failed": r.records_failed,
                "failure_rate": round(r.failure_rate, 4),
                "remediation_note": r.remediation_note,
                "evaluated_at": self.evaluated_at,
            })
        return pd.DataFrame(records)


class DataQualityValidator:
    """Validates raw academic datasets against institutional integrity rules."""

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or f"run_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    def validate_all(self, dataframes: Dict[str, pd.DataFrame]) -> ValidationReport:
        """
        Execute all 14 data quality checks across the provided datasets.
        
        Args:
            dataframes: Dict mapping table names to DataFrames.
            
        Returns:
            ValidationReport with full rule outcomes and remediation guidance.
        """
        results: List[QualityRuleResult] = []
        table_summaries: Dict[str, dict] = {}
        
        students_df = dataframes.get("students", pd.DataFrame())
        enrolments_df = dataframes.get("enrolments", pd.DataFrame())
        attendance_df = dataframes.get("attendance", pd.DataFrame())
        assignments_df = dataframes.get("assignments", pd.DataFrame())
        assessments_df = dataframes.get("assessments", pd.DataFrame())
        interventions_df = dataframes.get("interventions", pd.DataFrame())

        # Track valid student IDs for foreign key validation
        valid_student_ids = set()
        if not students_df.empty and "student_id" in students_df.columns:
            valid_student_ids = set(students_df["student_id"].dropna().astype(str).unique())

        # -------------------------------------------------------------
        # Table 1: Students Dimension Checks
        # -------------------------------------------------------------
        if students_df.empty:
            results.append(QualityRuleResult(
                table_name="students",
                rule_code="STUDENTS_EMPTY",
                rule_name="Students table must not be empty",
                status="FAIL",
                severity="High",
                records_evaluated=0,
                records_failed=1,
                failure_rate=1.0,
                remediation_note="Provide a non-empty students.csv file containing student_id and program.",
            ))
        else:
            n_students = len(students_df)
            # Rule: Required columns
            req_cols = ["student_id", "program", "cohort_year"]
            missing_cols = [c for c in req_cols if c not in students_df.columns]
            results.append(QualityRuleResult(
                table_name="students",
                rule_code="STUDENTS_SCHEMA",
                rule_name="Students schema contains required columns",
                status="FAIL" if missing_cols else "PASS",
                severity="High",
                records_evaluated=len(req_cols),
                records_failed=len(missing_cols),
                failure_rate=len(missing_cols) / len(req_cols),
                remediation_note=f"Add missing columns: {missing_cols}" if missing_cols else "All required columns present.",
            ))

            # Rule: Duplicate student IDs
            if "student_id" in students_df.columns:
                dup_ids = students_df["student_id"].duplicated().sum()
                results.append(QualityRuleResult(
                    table_name="students",
                    rule_code="STUDENTS_DUP_ID",
                    rule_name="Unique student IDs in students dimension",
                    status="FAIL" if dup_ids > 0 else "PASS",
                    severity="High",
                    records_evaluated=n_students,
                    records_failed=int(dup_ids),
                    failure_rate=float(dup_ids / n_students) if n_students else 0.0,
                    remediation_note="Deduplicate student_id records before ingesting." if dup_ids > 0 else "Primary keys are unique.",
                ))

            # Rule: Null rates in students
            null_count = int(students_df[req_cols].isnull().sum().sum()) if not missing_cols else 0
            results.append(QualityRuleResult(
                table_name="students",
                rule_code="STUDENTS_NULL_CHECK",
                rule_name="Null check on core student attributes",
                status="WARN" if null_count > 0 else "PASS",
                severity="Medium",
                records_evaluated=n_students * len(req_cols),
                records_failed=null_count,
                failure_rate=float(null_count / (n_students * len(req_cols))) if n_students else 0.0,
                remediation_note="Populate missing student profile attributes." if null_count > 0 else "No missing values in core fields.",
            ))

            table_summaries["students"] = {
                "records": n_students,
                "unique_students": len(valid_student_ids),
                "status": "Healthy" if all(r.status == "PASS" for r in results if r.table_name == "students") else "Needs Attention"
            }

        # -------------------------------------------------------------
        # Table 2: Enrolments Fact Checks
        # -------------------------------------------------------------
        if not enrolments_df.empty:
            n_enrol = len(enrolments_df)
            req_cols = ["student_id", "course_id", "term", "section"]
            missing_cols = [c for c in req_cols if c not in enrolments_df.columns]
            results.append(QualityRuleResult(
                table_name="enrolments",
                rule_code="ENROLMENTS_SCHEMA",
                rule_name="Enrolments schema contains required columns",
                status="FAIL" if missing_cols else "PASS",
                severity="High",
                records_evaluated=len(req_cols),
                records_failed=len(missing_cols),
                failure_rate=len(missing_cols) / len(req_cols),
                remediation_note=f"Add missing columns: {missing_cols}" if missing_cols else "All required columns present.",
            ))
            
            # Foreign key check
            if "student_id" in enrolments_df.columns and valid_student_ids:
                unmatched = (~enrolments_df["student_id"].astype(str).isin(valid_student_ids)).sum()
                results.append(QualityRuleResult(
                    table_name="enrolments",
                    rule_code="ENROLMENTS_FK_STUDENT",
                    rule_name="Enrolment student_ids exist in Students dimension",
                    status="FAIL" if unmatched > 0 else "PASS",
                    severity="High",
                    records_evaluated=n_enrol,
                    records_failed=int(unmatched),
                    failure_rate=float(unmatched / n_enrol),
                    remediation_note="Ensure all enrolled students exist in the master student registry." if unmatched > 0 else "All student references match.",
                ))

            # Rule 8: Duplicate Enrolments (student_id, course_id, term)
            if set(["student_id", "course_id", "term"]).issubset(enrolments_df.columns):
                dups = enrolments_df.duplicated(subset=["student_id", "course_id", "term"]).sum()
                results.append(QualityRuleResult(
                    table_name="enrolments",
                    rule_code="ENROLMENTS_DUP_CHECK",
                    rule_name="Unique student enrollment per course and term",
                    status="WARN" if dups > 0 else "PASS",
                    severity="Medium",
                    records_evaluated=n_enrol,
                    records_failed=int(dups),
                    failure_rate=float(dups / n_enrol),
                    remediation_note="Consolidate duplicate student-course enrollment records." if dups > 0 else "No duplicate enrollments detected.",
                ))

            table_summaries["enrolments"] = {
                "records": n_enrol,
                "courses": enrolments_df["course_id"].nunique() if "course_id" in enrolments_df.columns else 0,
                "sections": enrolments_df["section"].nunique() if "section" in enrolments_df.columns else 0,
                "status": "Healthy"
            }

        # -------------------------------------------------------------
        # Table 3: Attendance Quality Checks
        # -------------------------------------------------------------
        if not attendance_df.empty:
            n_att = len(attendance_df)
            req_cols = ["student_id", "course_id", "session_date", "attendance_status"]
            missing_cols = [c for c in req_cols if c not in attendance_df.columns]
            results.append(QualityRuleResult(
                table_name="attendance",
                rule_code="ATTENDANCE_SCHEMA",
                rule_name="Attendance schema contains required columns",
                status="FAIL" if missing_cols else "PASS",
                severity="High",
                records_evaluated=len(req_cols),
                records_failed=len(missing_cols),
                failure_rate=len(missing_cols) / len(req_cols),
                remediation_note=f"Add missing columns: {missing_cols}" if missing_cols else "All required columns present.",
            ))
            # Rule: Valid attendance status enum
            if "attendance_status" in attendance_df.columns:
                invalid_statuses = (~attendance_df["attendance_status"].isin(VALID_ATTENDANCE_STATUSES)).sum()
                results.append(QualityRuleResult(
                    table_name="attendance",
                    rule_code="ATTENDANCE_STATUS_ENUM",
                    rule_name="Attendance status belongs to allowed set (Present, Late, Absent, Excused)",
                    status="FAIL" if invalid_statuses > 0 else "PASS",
                    severity="High",
                    records_evaluated=n_att,
                    records_failed=int(invalid_statuses),
                    failure_rate=float(invalid_statuses / n_att),
                    remediation_note="Remap unexpected attendance statuses to standard values (Present, Late, Absent, Excused)." if invalid_statuses > 0 else "All attendance categories valid.",
                ))

            # Rule 3 & 4: Date parsing & logical boundaries
            if "session_date" in attendance_df.columns:
                parsed_dates = pd.to_datetime(attendance_df["session_date"], errors="coerce")
                invalid_dates = parsed_dates.isna().sum()
                results.append(QualityRuleResult(
                    table_name="attendance",
                    rule_code="ATTENDANCE_DATE_VALIDITY",
                    rule_name="Attendance session dates parse successfully",
                    status="FAIL" if invalid_dates > 0 else "PASS",
                    severity="High",
                    records_evaluated=n_att,
                    records_failed=int(invalid_dates),
                    failure_rate=float(invalid_dates / n_att),
                    remediation_note="Correct ISO-8601 formatting on unparseable session dates." if invalid_dates > 0 else "All session dates valid.",
                ))

            # Rule 8: Duplicate attendance logs per student-course-session
            if set(["student_id", "course_id", "session_date"]).issubset(attendance_df.columns):
                att_dups = attendance_df.duplicated(subset=["student_id", "course_id", "session_date"]).sum()
                results.append(QualityRuleResult(
                    table_name="attendance",
                    rule_code="ATTENDANCE_DUP_CHECK",
                    rule_name="Unique attendance log per student, course, and date",
                    status="WARN" if att_dups > 0 else "PASS",
                    severity="Medium",
                    records_evaluated=n_att,
                    records_failed=int(att_dups),
                    failure_rate=float(att_dups / n_att),
                    remediation_note="Remove duplicate attendance logs with identical timestamps." if att_dups > 0 else "No duplicate logs found.",
                ))

            table_summaries["attendance"] = {
                "records": n_att,
                "status": "Healthy"
            }

        # -------------------------------------------------------------
        # Table 4: Assignment Quality Checks
        # -------------------------------------------------------------
        if not assignments_df.empty:
            n_asg = len(assignments_df)
            req_cols = ["student_id", "course_id", "assignment_id", "due_date", "submitted_at", "score", "max_score"]
            missing_cols = [c for c in req_cols if c not in assignments_df.columns]
            results.append(QualityRuleResult(
                table_name="assignments",
                rule_code="ASSIGNMENTS_SCHEMA",
                rule_name="Assignments schema contains required columns",
                status="FAIL" if missing_cols else "PASS",
                severity="High",
                records_evaluated=len(req_cols),
                records_failed=len(missing_cols),
                failure_rate=len(missing_cols) / len(req_cols),
                remediation_note=f"Add missing columns: {missing_cols}" if missing_cols else "All required columns present.",
            ))
            
            # Score range validation (0 <= score <= max_score)
            if set(["score", "max_score"]).issubset(assignments_df.columns):
                valid_scores = assignments_df["score"].dropna()
                negative_scores = (valid_scores < 0).sum()
                exceeding_scores = (assignments_df["score"] > assignments_df["max_score"]).sum()
                score_violations = int(negative_scores + exceeding_scores)
                
                results.append(QualityRuleResult(
                    table_name="assignments",
                    rule_code="ASSIGNMENT_SCORE_RANGE",
                    rule_name="Assignment scores within [0, max_score] bounds",
                    status="FAIL" if score_violations > 0 else "PASS",
                    severity="High",
                    records_evaluated=len(valid_scores),
                    records_failed=score_violations,
                    failure_rate=float(score_violations / len(valid_scores)) if len(valid_scores) else 0.0,
                    remediation_note="Audit assignment gradebook for negative scores or points exceeding maximum." if score_violations > 0 else "All recorded scores within bounds.",
                ))

            # Rule 9: Submission lateness calculability
            if set(["due_date", "submitted_at"]).issubset(assignments_df.columns):
                due_parsed = pd.to_datetime(assignments_df["due_date"], errors="coerce")
                sub_parsed = pd.to_datetime(assignments_df["submitted_at"], errors="coerce")
                
                # Check for invalid due dates
                invalid_due = due_parsed.isna().sum()
                results.append(QualityRuleResult(
                    table_name="assignments",
                    rule_code="ASSIGNMENT_DUE_DATE_VALIDITY",
                    rule_name="Assignment due dates parse successfully",
                    status="FAIL" if invalid_due > 0 else "PASS",
                    severity="High",
                    records_evaluated=n_asg,
                    records_failed=int(invalid_due),
                    failure_rate=float(invalid_due / n_asg),
                    remediation_note="Repair malformed due date timestamps." if invalid_due > 0 else "All due dates formatted properly.",
                ))

            table_summaries["assignments"] = {
                "records": n_asg,
                "status": "Healthy"
            }

        # -------------------------------------------------------------
        # Table 5: Assessment Quality Checks
        # -------------------------------------------------------------
        if not assessments_df.empty:
            n_asm = len(assessments_df)
            if set(["score", "max_score"]).issubset(assessments_df.columns):
                valid_scores = assessments_df["score"].dropna()
                negative_scores = (valid_scores < 0).sum()
                exceeding_scores = (assessments_df["score"] > assessments_df["max_score"]).sum()
                score_violations = int(negative_scores + exceeding_scores)
                
                results.append(QualityRuleResult(
                    table_name="assessments",
                    rule_code="ASSESSMENT_SCORE_RANGE",
                    rule_name="Assessment scores within [0, max_score] bounds",
                    status="FAIL" if score_violations > 0 else "PASS",
                    severity="High",
                    records_evaluated=len(valid_scores),
                    records_failed=score_violations,
                    failure_rate=float(score_violations / len(valid_scores)) if len(valid_scores) else 0.0,
                    remediation_note="Inspect exam scoring feeds for invalid values outside [0, max_score]." if score_violations > 0 else "All exam scores valid.",
                ))

            table_summaries["assessments"] = {
                "records": n_asm,
                "status": "Healthy"
            }

        # Calculate summary health metrics
        total_rules = len(results)
        passed = sum(1 for r in results if r.status == "PASS")
        warned = sum(1 for r in results if r.status == "WARN")
        failed = sum(1 for r in results if r.status == "FAIL")
        total_failed_recs = sum(r.records_failed for r in results)
        
        health_pct = round((passed / total_rules * 100.0) if total_rules > 0 else 100.0, 1)
        has_blocking = failed > 0

        return ValidationReport(
            run_id=self.run_id,
            evaluated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            overall_health_pct=health_pct,
            total_rules_evaluated=total_rules,
            passed_rules=passed,
            warned_rules=warned,
            failed_rules=failed,
            total_records_failed=total_failed_recs,
            rule_results=results,
            table_summaries=table_summaries,
            has_blocking_errors=has_blocking,
        )
