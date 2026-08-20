"""
StudentPulse AI - Data Transformation & Cleaning Module
Cleans, normalizes, and prepares raw academic datasets for feature engineering.
"""

from dataclasses import dataclass
import logging
from typing import Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CleanedDatasets:
    """Container holding cleaned and standardized academic DataFrames."""
    students: pd.DataFrame
    enrolments: pd.DataFrame
    attendance: pd.DataFrame
    assignments: pd.DataFrame
    assessments: pd.DataFrame
    interventions: pd.DataFrame


def clean_and_transform_data(dataframes: Dict[str, pd.DataFrame]) -> CleanedDatasets:
    """
    Cleans, deduplicates, and standardizes raw DataFrames.
    
    Args:
        dataframes: Raw ingested DataFrames dictionary.
        
    Returns:
        CleanedDatasets dataclass containing prepared DataFrames.
    """
    # 1. Clean Students
    students = dataframes.get("students", pd.DataFrame()).copy()
    if not students.empty:
        students["student_id"] = students["student_id"].astype(str).str.strip()
        students["program"] = students["program"].astype(str).str.strip()
        students["cohort_year"] = pd.to_numeric(students["cohort_year"], errors="coerce").fillna(2026).astype(int)
        students = students.drop_duplicates(subset=["student_id"])
    else:
        students = pd.DataFrame(columns=["student_id", "program", "cohort_year"])

    valid_students = set(students["student_id"])

    # 2. Clean Enrolments
    enrolments = dataframes.get("enrolments", pd.DataFrame()).copy()
    if not enrolments.empty:
        enrolments["student_id"] = enrolments["student_id"].astype(str).str.strip()
        enrolments["course_id"] = enrolments["course_id"].astype(str).str.strip()
        enrolments["term"] = enrolments["term"].astype(str).str.strip()
        enrolments["section"] = enrolments["section"].astype(str).str.strip()
        # Drop duplicates and invalid foreign keys
        enrolments = enrolments[enrolments["student_id"].isin(valid_students)]
        enrolments = enrolments.drop_duplicates(subset=["student_id", "course_id", "term"])
    else:
        enrolments = pd.DataFrame(columns=["student_id", "course_id", "term", "section"])

    # 3. Clean Attendance
    attendance = dataframes.get("attendance", pd.DataFrame()).copy()
    if not attendance.empty:
        attendance["student_id"] = attendance["student_id"].astype(str).str.strip()
        attendance["course_id"] = attendance["course_id"].astype(str).str.strip()
        attendance["session_date"] = pd.to_datetime(attendance["session_date"], errors="coerce")
        attendance["attendance_status"] = attendance["attendance_status"].astype(str).str.strip().str.capitalize()
        # Drop invalid rows
        attendance = attendance.dropna(subset=["session_date"])
        attendance = attendance[attendance["student_id"].isin(valid_students)]
        valid_statuses = {"Present", "Late", "Absent", "Excused"}
        attendance = attendance[attendance["attendance_status"].isin(valid_statuses)]
        attendance = attendance.drop_duplicates(subset=["student_id", "course_id", "session_date"])
    else:
        attendance = pd.DataFrame(columns=["student_id", "course_id", "session_date", "attendance_status"])

    # 4. Clean Assignments
    assignments = dataframes.get("assignments", pd.DataFrame()).copy()
    if not assignments.empty:
        assignments["student_id"] = assignments["student_id"].astype(str).str.strip()
        assignments["course_id"] = assignments["course_id"].astype(str).str.strip()
        assignments["assignment_id"] = assignments["assignment_id"].astype(str).str.strip()
        assignments["due_date"] = pd.to_datetime(assignments["due_date"], errors="coerce")
        assignments["submitted_at"] = pd.to_datetime(assignments["submitted_at"], errors="coerce")
        assignments["max_score"] = pd.to_numeric(assignments["max_score"], errors="coerce").fillna(100.0)
        assignments["score"] = pd.to_numeric(assignments["score"], errors="coerce")
        # Ensure score bounds
        assignments.loc[assignments["score"] < 0, "score"] = 0.0
        assignments.loc[assignments["score"] > assignments["max_score"], "score"] = assignments["max_score"]
        assignments = assignments[assignments["student_id"].isin(valid_students)]
        assignments = assignments.drop_duplicates(subset=["student_id", "course_id", "assignment_id"])
    else:
        assignments = pd.DataFrame(columns=["student_id", "course_id", "assignment_id", "due_date", "submitted_at", "score", "max_score"])

    # 5. Clean Assessments
    assessments = dataframes.get("assessments", pd.DataFrame()).copy()
    if not assessments.empty:
        assessments["student_id"] = assessments["student_id"].astype(str).str.strip()
        assessments["course_id"] = assessments["course_id"].astype(str).str.strip()
        assessments["assessment_date"] = pd.to_datetime(assessments["assessment_date"], errors="coerce")
        assessments["assessment_type"] = assessments["assessment_type"].astype(str).str.strip()
        assessments["max_score"] = pd.to_numeric(assessments["max_score"], errors="coerce").fillna(100.0)
        assessments["score"] = pd.to_numeric(assessments["score"], errors="coerce").fillna(0.0)
        # Ensure score bounds
        assessments.loc[assessments["score"] < 0, "score"] = 0.0
        assessments.loc[assessments["score"] > assessments["max_score"], "score"] = assessments["max_score"]
        assessments = assessments[assessments["student_id"].isin(valid_students)]
        assessments = assessments.drop_duplicates(subset=["student_id", "course_id", "assessment_type", "assessment_date"])
    else:
        assessments = pd.DataFrame(columns=["student_id", "course_id", "assessment_date", "assessment_type", "score", "max_score"])

    # 6. Clean Interventions
    interventions = dataframes.get("interventions", pd.DataFrame()).copy()
    if not interventions.empty and "student_id" in interventions.columns:
        interventions["student_id"] = interventions["student_id"].astype(str).str.strip()
        interventions["course_id"] = interventions["course_id"].astype(str).str.strip()
        interventions["action_date"] = pd.to_datetime(interventions["action_date"], errors="coerce")
        interventions["action_type"] = interventions["action_type"].astype(str).str.strip()
        interventions["outcome_note"] = interventions["outcome_note"].astype(str).str.strip()
        if "staff_user" not in interventions.columns:
            interventions["staff_user"] = "academic_advisor"
        interventions = interventions[interventions["student_id"].isin(valid_students)]
    else:
        interventions = pd.DataFrame(columns=["student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"])

    return CleanedDatasets(
        students=students,
        enrolments=enrolments,
        attendance=attendance,
        assignments=assignments,
        assessments=assessments,
        interventions=interventions,
    )
