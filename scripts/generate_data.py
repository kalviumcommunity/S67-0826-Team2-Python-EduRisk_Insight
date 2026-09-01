"""
StudentPulse AI - Synthetic Data Generator
Generates realistic, reproducible academic datasets containing authentic engagement archetypes and controlled test fixtures.
"""

import argparse
import datetime
import logging
from pathlib import Path
import random
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_data")

PROGRAMS = [
    "Computer Science",
    "Data Analytics",
    "Information Systems",
    "Software Engineering",
    "Applied Mathematics",
    "Cybersecurity",
]

COURSES = [
    ("DATA-101", "Introduction to Data Analytics", 14),  # 14 weeks
    ("CS-204", "Data Structures & Algorithms", 14),
    ("STAT-301", "Applied Statistical Methods", 14),
    ("MATH-150", "Discrete Mathematics & Logic", 14),
]

SECTIONS = ["Section A", "Section B", "Section C"]
TERMS = ["Fall 2026", "Spring 2026"]


def generate_synthetic_academic_dataset(
    target_enrolments: int = 5000,
    seed: int = 42,
    output_dir: Path = Path("data/raw"),
    fixtures_dir: Path = Path("data/fixtures")
) -> Dict[str, pd.DataFrame]:
    """
    Generates a deterministic, rich academic dataset with authentic student engagement archetypes.
    
    Args:
        target_enrolments: Approximate number of student-course enrollments to produce (>= 5000).
        seed: Random seed for deterministic reproducibility.
        output_dir: Output directory for primary raw CSVs.
        fixtures_dir: Output directory for invalid test fixtures.
        
    Returns:
        Dictionary of generated DataFrames.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures_dir = Path(fixtures_dir)
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating synthetic dataset with seed=%d, target_enrolments=%d...", seed, target_enrolments)

    # 1. Generate Students (approx 2,500 students taking ~2 courses each)
    num_students = max(target_enrolments // 2, 2000)
    student_records = []
    for i in range(1, num_students + 1):
        student_id = f"STU-{1000 + i}"
        program = random.choice(PROGRAMS)
        cohort_year = random.choice([2023, 2024, 2025, 2026])
        student_records.append({
            "student_id": student_id,
            "program": program,
            "cohort_year": cohort_year,
        })
    students_df = pd.DataFrame(student_records)

    # 2. Generate Enrolments across courses and sections
    enrolment_records = []
    student_ids = students_df["student_id"].tolist()

    # Assign archetypes to students
    # Archetypes:
    # A (40%): High engagement, low risk (On Track)
    # B (15%): Declining attendance, missing work, low grades (Needs Review / High Risk)
    # C (15%): Good attendance, but poor assignment completion (Watch / Medium Risk)
    # D (10%): Recent attendance drop, emerging risk (Watch / Emerging)
    # E (10%): Early poor grades, now recovering (Watch / Recovering)
    # F (10%): High performing, perfect engagement (On Track)
    archetype_choices = ["A", "B", "C", "D", "E", "F"]
    archetype_weights = [0.40, 0.15, 0.15, 0.10, 0.10, 0.10]
    student_archetypes = {
        s_id: random.choices(archetype_choices, weights=archetype_weights)[0]
        for s_id in student_ids
    }

    # Section B in CS-204 will have slightly elevated archetype B to create authentic cohort finding
    enrolment_count = 0
    student_enrolments = []

    for s_id in student_ids:
        # Enrol student in 2-3 courses
        num_courses = random.choice([2, 2, 3])
        chosen_courses = random.sample(COURSES, num_courses)
        for course_id, course_name, weeks in chosen_courses:
            term = random.choice(TERMS)
            # Bias section assignment
            section = random.choice(SECTIONS)
            enrolment_records.append({
                "student_id": s_id,
                "course_id": course_id,
                "term": term,
                "section": section,
            })
            student_enrolments.append((s_id, course_id, term, section, weeks, student_archetypes[s_id]))
            enrolment_count += 1
            if enrolment_count >= target_enrolments:
                break
        if enrolment_count >= target_enrolments:
            break

    enrolments_df = pd.DataFrame(enrolment_records)

    # 3. Generate Attendance, Assignments, Assessments for each enrollment
    attendance_records = []
    assignment_records = []
    assessment_records = []
    intervention_records = []

    # Semester base dates (Fall 2026: Aug 24, 2026 to Dec 4, 2026; Spring 2026: Jan 12, 2026 to Apr 24, 2026)
    fall_start = pd.Timestamp("2026-08-24")
    spring_start = pd.Timestamp("2026-01-12")

    logger.info("Generating detailed session logs and gradebook submissions for %d enrollments...", len(student_enrolments))

    for s_id, course_id, term, section, weeks, archetype in student_enrolments:
        term_start = fall_start if "Fall" in term else spring_start
        
        # Determine archetype behavioral parameters
        if archetype == "A":  # Low Risk / On Track
            att_prob_early = 0.95
            att_prob_late = 0.95
            sub_prob = 0.98
            late_prob = 0.05
            score_mean, score_std = 85.0, 8.0
        elif archetype == "B":  # High Risk / Needs Review
            att_prob_early = 0.70
            att_prob_late = 0.45  # declining attendance
            sub_prob = 0.60       # missing multiple assignments
            late_prob = 0.40
            score_mean, score_std = 45.0, 12.0
        elif archetype == "C":  # Medium Risk / Poor Submissions
            att_prob_early = 0.88
            att_prob_late = 0.85
            sub_prob = 0.72       # misses 1-2 assignments
            late_prob = 0.25
            score_mean, score_std = 68.0, 10.0
        elif archetype == "D":  # Emerging Risk / Recent Attendance Drop
            att_prob_early = 0.92
            att_prob_late = 0.50  # acute recent drop >= 15%
            sub_prob = 0.88
            late_prob = 0.15
            score_mean, score_std = 74.0, 9.0
        elif archetype == "E":  # Recovering Risk
            att_prob_early = 0.60
            att_prob_late = 0.90  # improving engagement
            sub_prob = 0.85
            late_prob = 0.10
            score_mean, score_std = 62.0, 10.0
        else:  # Archetype F (High Performing)
            att_prob_early = 1.00
            att_prob_late = 1.00
            sub_prob = 1.00
            late_prob = 0.00
            score_mean, score_std = 94.0, 4.0

        # Section B in CS-204 extra penalty for archetype B to create sharp signal
        if course_id == "CS-204" and section == "Section B" and archetype == "B":
            att_prob_late = 0.35
            sub_prob = 0.50

        # Generate Attendance: 2 sessions per week for 10 current elapsed weeks
        elapsed_weeks = 10
        for w in range(elapsed_weeks):
            for d_offset in [1, 3]:  # Tue, Thu
                session_date = term_start + pd.Timedelta(weeks=w, days=d_offset)
                p_att = att_prob_late if w >= (elapsed_weeks - 2) else att_prob_early
                
                rand_val = random.random()
                if rand_val < p_att:
                    status = "Present"
                elif rand_val < (p_att + 0.05):
                    status = "Late"
                elif rand_val < (p_att + 0.08):
                    status = "Excused"
                else:
                    status = "Absent"

                attendance_records.append({
                    "student_id": s_id,
                    "course_id": course_id,
                    "session_date": session_date.strftime("%Y-%m-%d"),
                    "attendance_status": status,
                })

        # Generate 4 Assignments (Weeks 2, 4, 6, 8)
        for a_idx, due_week in enumerate([2, 4, 6, 8], start=1):
            due_date = term_start + pd.Timedelta(weeks=due_week, days=4, hours=23, minutes=59)
            asg_id = f"{course_id}-A0{a_idx}"
            
            # Submission decision
            if random.random() < sub_prob:
                is_late = random.random() < late_prob
                if is_late:
                    sub_time = due_date + pd.Timedelta(hours=random.randint(12, 72))
                else:
                    sub_time = due_date - pd.Timedelta(hours=random.randint(2, 48))
                
                score = min(max(round(np.random.normal(score_mean, score_std), 1), 0.0), 100.0)
                sub_str = sub_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Unsubmitted
                sub_str = None
                score = None

            assignment_records.append({
                "student_id": s_id,
                "course_id": course_id,
                "assignment_id": asg_id,
                "due_date": due_date.strftime("%Y-%m-%d %H:%M:%S"),
                "submitted_at": sub_str,
                "score": score,
                "max_score": 100.0,
            })

        # Generate 2 Assessments (Quiz 1 at week 3, Midterm Exam at week 7)
        for asm_type, asm_week in [("Quiz 1", 3), ("Midterm Exam", 7)]:
            asm_date = (term_start + pd.Timedelta(weeks=asm_week, days=2)).strftime("%Y-%m-%d")
            asm_score = min(max(round(np.random.normal(score_mean, score_std), 1), 0.0), 100.0)
            assessment_records.append({
                "student_id": s_id,
                "course_id": course_id,
                "assessment_date": asm_date,
                "assessment_type": asm_type,
                "score": asm_score,
                "max_score": 100.0,
            })

        # Generate Interventions for some students (archetype B, C, E)
        if archetype in ("B", "C", "E") and random.random() < 0.35:
            action_date = (term_start + pd.Timedelta(weeks=random.randint(4, 9))).strftime("%Y-%m-%d %H:%M:%S")
            action_type = random.choice(["1:1 Advisor Check-in", "Attendance Nudge Email", "Tutoring Center Referral", "Office Hours Meeting"])
            notes = [
                "Student discussed balancing part-time employment hours with assignment deadlines.",
                "Sent reminder regarding unsubmitted homework; student indicated intent to complete.",
                "Referred to math learning lab for supplementary tutoring on exam preparation.",
                "Reviewed attendance expectations; student agreed to office hours follow-up.",
            ]
            intervention_records.append({
                "student_id": s_id,
                "course_id": course_id,
                "action_date": action_date,
                "action_type": action_type,
                "outcome_note": random.choice(notes),
                "staff_user": "Dr. Maya",
            })

    attendance_df = pd.DataFrame(attendance_records)
    assignments_df = pd.DataFrame(assignment_records)
    assessments_df = pd.DataFrame(assessment_records)
    interventions_df = pd.DataFrame(intervention_records)

    # Save to data/raw/
    students_df.to_csv(output_dir / "students.csv", index=False)
    enrolments_df.to_csv(output_dir / "enrolments.csv", index=False)
    attendance_df.to_csv(output_dir / "attendance.csv", index=False)
    assignments_df.to_csv(output_dir / "assignments.csv", index=False)
    assessments_df.to_csv(output_dir / "assessments.csv", index=False)
    interventions_df.to_csv(output_dir / "interventions.csv", index=False)

    logger.info("Saved valid synthetic datasets: Students=%d, Enrolments=%d, Attendance=%d, Assignments=%d, Assessments=%d, Interventions=%d",
                len(students_df), len(enrolments_df), len(attendance_df), len(assignments_df), len(assessments_df), len(interventions_df))

    # -------------------------------------------------------------
    # Generate Controlled Invalid Test Fixtures in data/fixtures/
    # -------------------------------------------------------------
    logger.info("Creating invalid test fixtures with controlled quality anomalies in %s...", fixtures_dir)
    
    # 1. Invalid Students (Duplicate ID + Missing columns)
    inv_students = students_df.head(20).copy()
    inv_students.loc[len(inv_students)] = {"student_id": inv_students.iloc[0]["student_id"], "program": "Data Analytics", "cohort_year": 2026}
    inv_students.to_csv(fixtures_dir / "invalid_students_dup.csv", index=False)

    # 2. Invalid Attendance (Invalid status + Corrupt dates)
    inv_att = attendance_df.head(50).copy()
    inv_att.loc[0, "attendance_status"] = "UnknownStatus"
    inv_att.loc[1, "session_date"] = "2026-99-99"
    inv_att.to_csv(fixtures_dir / "invalid_attendance.csv", index=False)

    # 3. Invalid Assignments (Negative scores + Score > max_score)
    inv_asg = assignments_df.head(50).copy()
    inv_asg.loc[0, "score"] = -15.0
    inv_asg.loc[1, "score"] = 150.0
    inv_asg.to_csv(fixtures_dir / "invalid_assignments.csv", index=False)

    # 4. Invalid Enrolments (Unmatched student ID)
    inv_enr = enrolments_df.head(30).copy()
    inv_enr.loc[0, "student_id"] = "STU-NONEXISTENT-9999"
    inv_enr.to_csv(fixtures_dir / "invalid_enrolments_fk.csv", index=False)

    return {
        "students": students_df,
        "enrolments": enrolments_df,
        "attendance": attendance_df,
        "assignments": assignments_df,
        "assessments": assessments_df,
        "interventions": interventions_df,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic academic data for StudentPulse AI")
    parser.add_argument("--records", type=int, default=5000, help="Target number of enrollments")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--out", type=str, default="data/raw", help="Output directory")
    args = parser.parse_args()

    generate_synthetic_academic_dataset(
        target_enrolments=args.records,
        seed=args.seed,
        output_dir=Path(args.out),
    )
