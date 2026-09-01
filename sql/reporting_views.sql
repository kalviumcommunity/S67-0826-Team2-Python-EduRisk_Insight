-- ==============================================================================
-- StudentPulse AI - SQL Reporting Views
-- High-performance views for dashboard analytics and validation
-- ==============================================================================

-- 1. Overview Headline KPIs View
CREATE VIEW IF NOT EXISTS v_overview_kpis AS
SELECT
    f.course_id,
    f.term,
    f.section,
    COUNT(DISTINCT f.student_id) AS total_enrolled_students,
    SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
    SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
    ROUND(AVG(f.attendance_rate), 2) AS avg_attendance_rate,
    ROUND(AVG(f.submission_completion_rate), 2) AS avg_submission_completion_rate,
    ROUND(AVG(f.assessment_average), 2) AS avg_assessment_score,
    ROUND(AVG(f.assignment_average), 2) AS avg_assignment_score
FROM student_course_features f
LEFT JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term
GROUP BY f.course_id, f.term, f.section;


-- 2. Risk Explorer Denormalized View
CREATE VIEW IF NOT EXISTS v_risk_explorer AS
SELECT
    f.student_id,
    s.program,
    s.cohort_year,
    f.course_id,
    f.term,
    f.section,
    r.risk_score,
    r.risk_level,
    r.reasons_json,
    ROUND(f.attendance_rate, 1) AS attendance_rate,
    ROUND(f.recent_attendance_rate, 1) AS recent_attendance_rate,
    ROUND(f.submission_completion_rate, 1) AS submission_completion_rate,
    ROUND(f.late_submission_rate, 1) AS late_submission_rate,
    f.missing_assignments,
    ROUND(f.assignment_average, 1) AS assignment_average,
    ROUND(f.assessment_average, 1) AS assessment_average,
    ROUND((f.assignment_average + f.assessment_average) / 2.0, 1) AS current_composite_avg,
    f.engagement_trend,
    r.calculated_at AS last_assessed_at
FROM student_course_features f
INNER JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term
INNER JOIN students s
    ON f.student_id = s.student_id;


-- 3. Course and Section Risk Summary View
CREATE VIEW IF NOT EXISTS v_course_risk_summary AS
SELECT
    f.course_id,
    f.term,
    f.section,
    COUNT(DISTINCT f.student_id) AS enrolled_count,
    SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
    SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
    ROUND(100.0 * SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) / COUNT(DISTINCT f.student_id), 1) AS high_risk_pct,
    ROUND(AVG(f.attendance_rate), 1) AS avg_attendance_pct,
    ROUND(AVG(f.submission_completion_rate), 1) AS avg_submission_pct,
    ROUND(AVG(f.assessment_average), 1) AS avg_assessment_pct
FROM student_course_features f
LEFT JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term
GROUP BY f.course_id, f.term, f.section;


-- 4. Student Detail Unified View
CREATE VIEW IF NOT EXISTS v_student_detail AS
SELECT
    s.student_id,
    s.program,
    s.cohort_year,
    f.course_id,
    f.term,
    f.section,
    r.risk_score,
    r.risk_level,
    r.reasons_json,
    f.attendance_rate,
    f.recent_attendance_rate,
    f.submission_completion_rate,
    f.late_submission_rate,
    f.assignment_average,
    f.assessment_average,
    f.missing_assignments,
    f.engagement_trend,
    f.total_sessions,
    f.present_sessions,
    f.excused_sessions,
    f.absent_sessions,
    f.total_assignments,
    f.submitted_assignments,
    f.late_assignments,
    f.calculated_at
FROM students s
INNER JOIN student_course_features f ON s.student_id = f.student_id
INNER JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term;


-- 5. Data Quality Summary View
CREATE VIEW IF NOT EXISTS v_data_quality_summary AS
SELECT
    run_id,
    table_name,
    COUNT(*) AS total_rules_evaluated,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed_rules,
    SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS warned_rules,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed_rules,
    SUM(records_failed) AS total_invalid_records,
    ROUND(100.0 * SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) / COUNT(*), 1) AS data_health_score,
    MAX(evaluated_at) AS last_evaluated_at
FROM data_quality_reports
GROUP BY run_id, table_name;
