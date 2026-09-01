"""
StudentPulse AI - SQL vs. Python KPI Validation Suite
Compares headline academic indicators calculated independently in Python/Pandas vs. SQL views.
Ensures 100% reproducibility across analytical layers as required by the PRD.
"""

import argparse
from pathlib import Path
import sys
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import DatabaseManager


def validate_kpis(db_path: Path = Path("data/studentpulse.db")) -> bool:
    """
    Compares metrics computed via Python (reading raw processed tables) vs. SQL reporting views.
    
    Args:
        db_path: Path to the SQLite database.
        
    Returns:
        True if all KPI checks PASS within tolerance, False otherwise.
    """
    db = DatabaseManager(db_path=db_path)

    # 1. Compute KPIs in Python via Pandas
    features_df = db.query_dataframe("SELECT * FROM student_course_features")
    risk_df = db.query_dataframe("SELECT * FROM risk_assessments")

    if features_df.empty or risk_df.empty:
        print("ERROR: student_course_features or risk_assessments table is empty. Run pipeline first.")
        return False

    merged_py = pd.merge(features_df, risk_df, on=["student_id", "course_id", "term"], how="inner")

    py_total_students = int(merged_py["student_id"].nunique())
    py_high_risk = int((merged_py["risk_level"] == "High").sum())
    py_med_risk = int((merged_py["risk_level"] == "Medium").sum())
    py_low_risk = int((merged_py["risk_level"] == "Low").sum())
    py_avg_attendance = round(float(merged_py["attendance_rate"].mean()), 2)
    py_avg_submission = round(float(merged_py["submission_completion_rate"].mean()), 2)
    py_avg_assessment = round(float(merged_py["assessment_average"].mean()), 2)

    # 2. Compute KPIs via SQL from v_overview_kpis / direct SQL query
    sql_query = """
        SELECT
            COUNT(DISTINCT f.student_id) AS total_enrolled_students,
            SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
            SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
            SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
            ROUND(AVG(f.attendance_rate), 2) AS avg_attendance_rate,
            ROUND(AVG(f.submission_completion_rate), 2) AS avg_submission_completion_rate,
            ROUND(AVG(f.assessment_average), 2) AS avg_assessment_score
        FROM student_course_features f
        LEFT JOIN risk_assessments r
            ON f.student_id = r.student_id
            AND f.course_id = r.course_id
            AND f.term = r.term
    """
    sql_res = db.execute_query(sql_query)
    if not sql_res:
        print("ERROR: SQL query returned no results.")
        return False

    sql_row = sql_res[0]
    sql_total_students = int(sql_row["total_enrolled_students"])
    sql_high_risk = int(sql_row["high_risk_count"])
    sql_med_risk = int(sql_row["medium_risk_count"])
    sql_low_risk = int(sql_row["low_risk_count"])
    sql_avg_attendance = round(float(sql_row["avg_attendance_rate"]), 2)
    sql_avg_submission = round(float(sql_row["avg_submission_completion_rate"]), 2)
    sql_avg_assessment = round(float(sql_row["avg_assessment_score"]), 2)

    # 3. Compare with strict tolerances
    metrics = [
        ("Total Enrolled Students", py_total_students, sql_total_students, 0, "count"),
        ("High-Risk Count (Needs Review)", py_high_risk, sql_high_risk, 0, "count"),
        ("Medium-Risk Count (Watch)", py_med_risk, sql_med_risk, 0, "count"),
        ("Low-Risk Count (On Track)", py_low_risk, sql_low_risk, 0, "count"),
        ("Average Attendance Rate", py_avg_attendance, sql_avg_attendance, 0.05, "pct"),
        ("Average Submission Rate", py_avg_submission, sql_avg_submission, 0.05, "pct"),
        ("Average Assessment Score", py_avg_assessment, sql_avg_assessment, 0.05, "pct"),
    ]

    print("=" * 80)
    print(" STUDENTPULSE AI — DUAL SQL / PYTHON KPI VALIDATION AUDIT")
    print("=" * 80)
    print(f"{'KPI METRIC NAME':<32} | {'PYTHON':<10} | {'SQL':<10} | {'DIFF':<8} | {'STATUS'}")
    print("-" * 80)

    all_passed = True
    for name, py_val, sql_val, tol, m_type in metrics:
        diff = abs(py_val - sql_val)
        passed = diff <= tol
        if not passed:
            all_passed = False
        
        status_str = "PASS ✓" if passed else "FAIL ✗"
        if m_type == "count":
            print(f"{name:<32} | {py_val:<10} | {sql_val:<10} | {diff:<8} | {status_str}")
        else:
            print(f"{name:<32} | {py_val:<9.2f}% | {sql_val:<9.2f}% | {diff:<7.2f}% | {status_str}")

    print("=" * 80)
    if all_passed:
        print(">>> OVERALL VALIDATION STATUS: PASS (All headline KPIs match within tolerance)")
    else:
        print(">>> OVERALL VALIDATION STATUS: FAIL (Discrepancy detected between Python and SQL)")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate SQL vs Python KPIs")
    parser.add_argument("--db", type=str, default="data/studentpulse.db", help="Path to SQLite database")
    args = parser.parse_args()

    success = validate_kpis(Path(args.db))
    sys.exit(0 if success else 1)
