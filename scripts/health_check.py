"""StudentPulse AI end-to-end acceptance/health check."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import DatabaseManager
from scripts.validate_kpis import validate_kpis


REQUIRED_TABLES = {
    "students", "enrolments", "attendance", "assignments", "assessments",
    "interventions", "student_course_features", "risk_assessments",
    "data_quality_reports", "pipeline_runs",
}
REQUIRED_VIEWS = {
    "v_overview_kpis", "v_risk_explorer", "v_course_risk_summary",
    "v_student_detail", "v_data_quality_summary",
}


def main() -> int:
    db_path = Path("data/studentpulse.db")
    if not db_path.exists():
        print(f"FAIL: database not found: {db_path}")
        return 1

    db = DatabaseManager(db_path)
    objects = db.execute_query("SELECT name, type FROM sqlite_master WHERE type IN ('table','view')")
    table_names = {r["name"] for r in objects if r["type"] == "table"}
    view_names = {r["name"] for r in objects if r["type"] == "view"}
    missing_tables = REQUIRED_TABLES - table_names
    missing_views = REQUIRED_VIEWS - view_names

    checks = []
    checks.append(("required tables", not missing_tables, sorted(missing_tables)))
    checks.append(("required views", not missing_views, sorted(missing_views)))

    counts = {}
    for table in sorted(REQUIRED_TABLES):
        counts[table] = int(db.execute_query(f"SELECT COUNT(*) AS c FROM {table}")[0]["c"])
    checks.append(("students populated", counts["students"] > 0, counts["students"]))
    checks.append(("enrolments populated", counts["enrolments"] > 0, counts["enrolments"]))
    checks.append(("features populated", counts["student_course_features"] > 0, counts["student_course_features"]))
    checks.append(("risk assessments populated", counts["risk_assessments"] > 0, counts["risk_assessments"]))

    invalid_risk = int(db.execute_query("SELECT COUNT(*) AS c FROM risk_assessments WHERE risk_level NOT IN ('Low','Medium','High')")[0]["c"])
    no_reason = int(db.execute_query("SELECT COUNT(*) AS c FROM risk_assessments WHERE risk_score > 0 AND (reasons_json IS NULL OR reasons_json = '[]')")[0]["c"])
    checks.append(("valid risk levels", invalid_risk == 0, invalid_risk))
    checks.append(("flagged rows have reasons", no_reason == 0, no_reason))

    print("=" * 72)
    print("STUDENTPULSE AI — MVP ACCEPTANCE / HEALTH CHECK")
    print("=" * 72)
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL':<6} {name:<34} {detail}")

    kpi_ok = validate_kpis(db_path)
    print(f"{'PASS' if kpi_ok else 'FAIL':<6} SQL/Python KPI validation")
    print("=" * 72)
    return 0 if all(ok for _, ok, _ in checks) and kpi_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
