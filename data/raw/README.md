# StudentPulse AI — Input Data Directory (`data/raw/`)

Place your CSV data files in this directory. The system will ingest, validate, transform, and compute early-risk indicators automatically.

---

### Required CSV Files & Schemas

#### 1. `students.csv` (Required)
Defines unique students across programs and cohorts.
- `student_id` (string, primary key, e.g. `STU-1001`)
- `program` (string, e.g. `Data Analytics`, `Computer Science`)
- `cohort_year` (integer, e.g. `2026`)

#### 2. `enrolments.csv` (Required)
Maps students to courses, terms, and sections.
- `student_id` (string, foreign key matching `students.csv`)
- `course_id` (string, e.g. `DATA-101`, `CS-204`)
- `term` (string, e.g. `Fall 2026`, `Spring 2026`)
- `section` (string, e.g. `Section A`, `Section B`)

#### 3. `attendance.csv` (Required)
Records class session attendance records.
- `student_id` (string, foreign key matching `students.csv`)
- `course_id` (string, matching `enrolments.csv`)
- `session_date` (date string `YYYY-MM-DD`, e.g. `2026-09-15`)
- `attendance_status` (string enum: `Present`, `Late`, `Excused`, `Absent`)

#### 4. `assignments.csv` (Required)
Records assignment due dates, submission timestamps, and earned scores.
- `student_id` (string, foreign key)
- `course_id` (string)
- `assignment_id` (string, e.g. `DATA-101-A01`)
- `due_date` (datetime string `YYYY-MM-DD HH:MM:SS`)
- `submitted_at` (datetime string `YYYY-MM-DD HH:MM:SS` or empty if unsubmitted)
- `score` (numeric, e.g. `85.0` or empty if unsubmitted)
- `max_score` (numeric, e.g. `100.0`)

#### 5. `assessments.csv` (Required)
Records formal exams, quizzes, and midterm grades.
- `student_id` (string, foreign key)
- `course_id` (string)
- `assessment_date` (date string `YYYY-MM-DD`)
- `assessment_type` (string, e.g. `Midterm Exam`, `Quiz 1`, `Final Exam`)
- `score` (numeric, e.g. `78.5`)
- `max_score` (numeric, e.g. `100.0`)

#### 6. `interventions.csv` (Optional)
Logs historical advisor support actions and notes.
- `student_id` (string, foreign key)
- `course_id` (string)
- `action_date` (datetime string `YYYY-MM-DD HH:MM:SS`)
- `action_type` (string, e.g. `1:1 Advisor Check-in`, `Attendance Nudge Email`)
- `outcome_note` (string text description)
- `staff_user` (string, e.g. `Dr. Maya`)

---

### How to Run

1. **Option A (Via Dashboard Web UI)**:
   Navigate to the **Data Quality** page and click **"⚡ Ingest, Validate & Activate Dataset"** (or upload your CSV files directly into the drag-and-drop studio).

2. **Option B (Via Terminal CLI)**:
   ```bash
   python scripts/run_pipeline.py
   ```
