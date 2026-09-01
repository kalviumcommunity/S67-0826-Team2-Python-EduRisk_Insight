-- ==============================================================================
-- StudentPulse AI - Relational Database Schema
-- Compatible with SQLite and PostgreSQL
-- ==============================================================================

-- 1. Students Dimension Table (Pseudonymous IDs only, strictly no PII)
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(64) PRIMARY KEY,
    program VARCHAR(128) NOT NULL,
    cohort_year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Enrolments Fact Table (One row per student-course-term)
CREATE TABLE IF NOT EXISTS enrolments (
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    term VARCHAR(32) NOT NULL,
    section VARCHAR(16) NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id, term),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 3. Attendance Logs
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    session_date DATE NOT NULL,
    attendance_status VARCHAR(16) NOT NULL CHECK (attendance_status IN ('Present', 'Late', 'Absent', 'Excused')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 4. Assignment Submissions
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    assignment_id VARCHAR(64) NOT NULL,
    due_date TIMESTAMP NOT NULL,
    submitted_at TIMESTAMP NULL,
    score REAL NULL,
    max_score REAL NOT NULL DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 5. Assessment / Exam Performance
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(64) NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 6. Interventions & Support Actions Log
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(64) NOT NULL,
    outcome_note TEXT NULL,
    staff_user VARCHAR(64) DEFAULT 'advisor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 7. Precomputed Student-Course Feature Aggregate Table
CREATE TABLE IF NOT EXISTS student_course_features (
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    term VARCHAR(32) NOT NULL,
    section VARCHAR(16) NOT NULL,
    attendance_rate REAL NOT NULL,
    recent_attendance_rate REAL NOT NULL,
    submission_completion_rate REAL NOT NULL,
    late_submission_rate REAL NOT NULL,
    assignment_average REAL NOT NULL,
    assessment_average REAL NOT NULL,
    missing_assignments INTEGER NOT NULL,
    engagement_trend VARCHAR(32) NOT NULL,
    total_sessions INTEGER NOT NULL,
    present_sessions INTEGER NOT NULL,
    excused_sessions INTEGER NOT NULL,
    absent_sessions INTEGER NOT NULL,
    total_assignments INTEGER NOT NULL,
    submitted_assignments INTEGER NOT NULL,
    late_assignments INTEGER NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id, term),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 8. Risk Assessment Results
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64) NOT NULL,
    term VARCHAR(32) NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_level VARCHAR(16) NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    reasons_json TEXT NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 9. Data Quality Audit Reports
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(64) NOT NULL,
    table_name VARCHAR(64) NOT NULL,
    rule_code VARCHAR(64) NOT NULL,
    rule_name VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL CHECK (status IN ('PASS', 'WARN', 'FAIL')),
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
    records_evaluated INTEGER NOT NULL,
    records_failed INTEGER NOT NULL,
    failure_rate REAL NOT NULL,
    remediation_note TEXT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Pipeline Execution Runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    status VARCHAR(32) NOT NULL,
    total_students INTEGER NOT NULL,
    total_enrolments INTEGER NOT NULL,
    high_risk_count INTEGER NOT NULL,
    medium_risk_count INTEGER NOT NULL,
    low_risk_count INTEGER NOT NULL,
    duration_seconds REAL NOT NULL
);

-- Indexes for Query Acceleration
CREATE INDEX IF NOT EXISTS idx_enrolments_lookup ON enrolments (course_id, term, section);
CREATE INDEX IF NOT EXISTS idx_attendance_lookup ON attendance (student_id, course_id, session_date);
CREATE INDEX IF NOT EXISTS idx_assignments_lookup ON assignments (student_id, course_id);
CREATE INDEX IF NOT EXISTS idx_assessments_lookup ON assessments (student_id, course_id);
CREATE INDEX IF NOT EXISTS idx_features_lookup ON student_course_features (course_id, term, section);
CREATE INDEX IF NOT EXISTS idx_risk_lookup ON risk_assessments (course_id, term, risk_level);
CREATE INDEX IF NOT EXISTS idx_interventions_lookup ON interventions (student_id, course_id);
