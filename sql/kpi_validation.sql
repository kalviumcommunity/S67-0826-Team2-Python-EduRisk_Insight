-- ==============================================================================
-- StudentPulse AI - SQL KPI Validation Queries
-- Canonical SQL queries used to validate dashboard metrics against Python/Pandas
-- ==============================================================================

-- KPI 1: Overall Headline Metrics across all courses & sections
SELECT
    COUNT(DISTINCT f.student_id) AS total_enrolled_students,
    SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
    SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
    ROUND(AVG(f.attendance_rate), 4) AS avg_attendance_rate,
    ROUND(AVG(f.submission_completion_rate), 4) AS avg_submission_completion_rate,
    ROUND(AVG(f.assessment_average), 4) AS avg_assessment_score,
    ROUND(AVG(f.assignment_average), 4) AS avg_assignment_score
FROM student_course_features f
LEFT JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term;


-- KPI 2: Metrics Filtered by Specific Course and Term
-- (Example: course_id = 'DATA-101' AND term = 'Fall 2026')
SELECT
    f.course_id,
    f.term,
    COUNT(DISTINCT f.student_id) AS course_enrolled_students,
    SUM(CASE WHEN r.risk_level = 'High' THEN 1 ELSE 0 END) AS course_high_risk_count,
    SUM(CASE WHEN r.risk_level = 'Medium' THEN 1 ELSE 0 END) AS course_medium_risk_count,
    SUM(CASE WHEN r.risk_level = 'Low' THEN 1 ELSE 0 END) AS course_low_risk_count,
    ROUND(AVG(f.attendance_rate), 4) AS course_avg_attendance,
    ROUND(AVG(f.submission_completion_rate), 4) AS course_avg_submission_completion,
    ROUND(AVG(f.assessment_average), 4) AS course_avg_assessment
FROM student_course_features f
LEFT JOIN risk_assessments r
    ON f.student_id = r.student_id
    AND f.course_id = r.course_id
    AND f.term = r.term
GROUP BY f.course_id, f.term;
