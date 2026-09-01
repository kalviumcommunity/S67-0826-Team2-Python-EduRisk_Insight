# StudentPulse AI — Academic Engagement & Early-Risk Insights

StudentPulse AI is an explainable academic early-warning MVP. It combines attendance, assignment submission, and assessment data at student-course level and gives qualified staff transparent support signals. It is a prioritisation aid, **not** an automated decision system.

## MVP scope

Implemented against the supplied PRD:

- CSV ingestion for students, enrolments, attendance, assignments and assessments; optional interventions
- schema, date, duplicate, enum, foreign-key, null and score-range validation
- reproducible cleaning and student-course feature engineering
- configurable rule-based risk scoring with human-readable reasons
- SQLite reporting database and SQL reporting views
- SQL/Python KPI validation
- Streamlit Overview, Risk Explorer, Student Detail, Data Quality and Academic Reports views
- filters for course, term, section, support level, attendance range, submission status and student search
- CSV export of the filtered risk explorer
- support-action/intervention logging
- synthetic demo dataset with realistic risk archetypes
- automated tests and an acceptance/health-check script

The PRD defines the MVP as complete when valid CSVs load, cleaned reporting data is produced, metrics/risk rules are calculated, filtering works, risk reasons are shown, all four core dashboard views exist, cohort insights are documented, SQL reproduces KPIs, and the README explains setup, data schema, run instructions, screenshots/limitations and safeguards.

## Repository layout

```text
studentpulse-ai/
├── app.py
├── config/
│   └── risk_thresholds.yaml
├── data/
│   ├── fixtures/              # intentionally invalid CSVs for validation tests
│   ├── raw/                   # synthetic demo source data
│   ├── processed/             # pipeline outputs
│   └── studentpulse.db        # packaged demo database
├── src/
│   ├── ingest.py
│   ├── validate.py
│   ├── transform.py
│   ├── features.py
│   ├── risk_rules.py
│   ├── database.py
│   ├── reporting.py
│   ├── insights.py
│   └── pipeline.py
├── sql/
│   ├── schema.sql
│   ├── reporting_views.sql
│   └── kpi_validation.sql
├── analytics/
├── ui/
├── scripts/
└── tests/
```

## Quick start

Python 3.11+ is recommended. Create a fresh virtual environment; **do not use the old `.venv` from the ZIP** because virtual environments are machine-specific.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the packaged demo

The ZIP contains a ready-to-query SQLite database and synthetic source files. Start the dashboard with:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit.

### Rebuild the demo dataset from scratch

```bash
python scripts/generate_data.py
python scripts/run_pipeline.py
python scripts/validate_kpis.py
python scripts/health_check.py
```

The generator creates synthetic/pseudonymous data only. Never place real student PII in `data/raw` or commit it to GitHub.

## Data model

| Dataset | Grain | Required fields |
|---|---|---|
| students | one row/student | `student_id`, `program`, `cohort_year` |
| enrolments | one row/student-course-term | `student_id`, `course_id`, `term`, `section` |
| attendance | one row/class session/student | `student_id`, `course_id`, `session_date`, `attendance_status` |
| assignments | one row/assignment/student | `student_id`, `course_id`, `assignment_id`, `due_date`, `submitted_at`, `score`, `max_score` |
| assessments | one row/assessment/student | `student_id`, `course_id`, `assessment_date`, `assessment_type`, `score`, `max_score` |
| interventions | one row/support action | `student_id`, `course_id`, `action_date`, `action_type`, `outcome_note` |

## Risk logic

Risk scoring is intentionally transparent and configurable in `config/risk_thresholds.yaml`. The default rules mirror the PRD: low attendance, recent attendance decline, incomplete submissions, missing assignments, high late-submission rate, and low assignment/assessment performance.

Default bands:

- **Low / On Track:** 0–2 points
- **Medium / Watch:** 3–5 points
- **High / Needs Review:** 6+ points

These thresholds are prototype assumptions and must not be presented as validated institutional policy. Every flagged record stores the triggered rule codes, labels, points and explanations.

## Dashboard pages

1. **Overview** — six headline KPIs, engagement trends, support-level distribution, dynamic signals and priority review list.
2. **Risk Explorer** — multi-dimensional filters, explainable reasons, student inspection, and CSV export.
3. **Student Detail** — attendance history, assignment status, assessment performance, risk explanation and support-action logging.
4. **Data Quality** — validation health, source-feed counts, rule audit, pipeline history, and CSV upload validation.
5. **Academic Reports** — course/section comparison, cohort insights and exportable filtered reporting.

## Validation and testing

Run:

```bash
pytest -q
python scripts/validate_kpis.py
python scripts/health_check.py
```

The packaged build was checked with the project test suite and pipeline. The health check verifies required tables/views, core row counts, risk-level integrity, explainable reasons, and SQL/Python KPI agreement.

## Privacy and ethics

- Demo data is synthetic and uses pseudonymous IDs.
- Do not expose names, emails, health/disability information, demographic categories, or other unnecessary sensitive attributes.
- Risk levels are support signals requiring qualified human review.
- The project must use language such as “associated with” or “signal”, not “caused by”.
- Do not automate disciplinary, grading, admissions or eligibility decisions from these scores.

## Deployment note

For production, move from the packaged SQLite demo to a managed database, add authentication/authorisation, secret management, audit logging, encrypted transport/storage, institution-approved data governance, and a validated model/rule review process. The current repository is an MVP/demo, not a production student-record system.
