# Shally — Data Engineering & SQL Database PR Tracker

> **Student / Contributor**: Shally (`shally3009` <mittalshally30@gmail.com>)  
> **Repository**: [kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight)  
> **Role**: Database + Dataset / Data Engineering & SQL Analytics

---

## Status Legend
- ⬜ Not Started
- 🟡 In Progress
- 🟢 PR Created
- 🔵 Merged

---

## PR Roadmap

| PR # | Status | Branch | Title | Main File / Area | LU Covered |
|:---|:---:|:---|:---|:---|:---|
| **PR #1** | 🟢 | `data/lu-dataset-ingestion` | Dataset Intake & CSV/JSON Ingestion | `data/raw/*.csv`, `src/ingest.py` | 2.14, 2.15 |
| **PR #2** | 🟢 | `data/lu-profiling-dictionary` | Dataset Profiling & Data Dictionary Mapping | `analytics/profiling.py`, `docs/DATA_DICTIONARY.md` | 2.16, 2.17 |
| **PR #3** | 🟢 | `data/lu-imputation-cleaning` | Missing Value Imputation & String Cleaning | `src/transform.py` | 2.18, 2.21 |
| **PR #4** | 🟢 | `data/lu-types-dedup-dates` | Type Enforcement, Deduplication & DateTime Pipelines | `src/transform.py` | 2.19, 2.20, 2.22 |
| **PR #5** | 🟢 | `data/lu-outliers-quality-joins` | Outlier Detection, Quality Validation & Multi-Source Joins | `src/validate.py`, `src/transform.py` | 2.23, 2.24, 2.25 |
| **PR #6** | 🟢 | `sql/lu-schema-db-integration` | SQL Foundations, Schema DDL & DB Integration | `sql/schema.sql`, `src/database.py` | 2.7, 2.37 |
| **PR #7** | 🟢 | `sql/lu-metrics-joins-queries` | Business Metrics Query Design, Grouping & Joins | `sql/reporting_views.sql` | 2.38, 2.39, 2.40 |
| **PR #8** | 🟢 | `sql/lu-window-views-optimization` | Window Functions, Query Index Optimization & Views | `sql/reporting_views.sql`, `sql/schema.sql` | 2.41, 2.42, 2.43 |
| **PR #9** | 🟢 | `sql/lu-kpi-insight-validation` | SQL-Based KPI Parity Audit & Validation | `sql/kpi_validation.sql`, `scripts/validate_kpis.py` | 2.44 |
| **PR #10**| 🟢 | `data/lu-database-delivery` | Complete Data & SQL Architecture Delivery | `docs/SHALLY_DATA_SQL_PR_TRACKER.md` | Delivery & Summary |

---

## PR Details & Commit Logs

### PR #1
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-dataset-ingestion`
- **Commit**: `d9686fd`
- **PR Link**: [Create PR #1](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-dataset-ingestion)
- **LU**: `2.14`, `2.15`
- **Files**:
  - `data/raw/students.csv`
  - `data/raw/enrolments.csv`
  - `data/raw/attendance.csv`
  - `data/raw/assignments.csv`
  - `data/raw/assessments.csv`
  - `data/raw/interventions.csv`
  - `data/raw/README.md`
  - `src/ingest.py`
- **Summary**: Established raw dataset schemas for all 6 core educational entities. Configured resilient CSV/JSON ingestion pipelines with format detection and schema validation.

---

### PR #2
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-profiling-dictionary`
- **Commit**: `d624d42`
- **PR Link**: [Create PR #2](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-profiling-dictionary)
- **LU**: `2.16`, `2.17`
- **Files**:
  - `analytics/profiling.py`
  - `docs/DATA_DICTIONARY.md`
- **Summary**: Implemented dataset profiling statistical functions (quantiles, null counts, cardinalities, distribution moments) and created standard business context data dictionary.

---

### PR #3
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-imputation-cleaning`
- **Commit**: `dc42736`
- **PR Link**: [Create PR #3](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-imputation-cleaning)
- **LU**: `2.18`, `2.21`
- **Files**:
  - `src/transform.py`
- **Summary**: Implemented robust missing value handling (zero-imputation for unsubmitted work, median/mode imputation) and text cleaning (whitespace trimming, case normalization, email standardization).

---

### PR #4
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-types-dedup-dates`
- **Commit**: `3479b91`
- **PR Link**: [Create PR #4](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-types-dedup-dates)
- **LU**: `2.19`, `2.20`, `2.22`
- **Files**:
  - `src/transform.py`
- **Summary**: Standardized column data types (dates to ISO YYYY-MM-DD, scores to float, counts to int), implemented deterministic deduplication across primary keys, and built weekly academic timeline parsing.

---

### PR #5
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-outliers-quality-joins`
- **Commit**: `016b761`
- **PR Link**: [Create PR #5](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-outliers-quality-joins)
- **LU**: `2.23`, `2.24`, `2.25`
- **Files**:
  - `src/validate.py`
  - `src/transform.py`
  - `data/fixtures/invalid_students_dup.csv`
  - `data/fixtures/invalid_enrolments_fk.csv`
  - `data/fixtures/invalid_attendance.csv`
  - `data/fixtures/invalid_assignments.csv`
- **Summary**: Implemented statistical outlier detection (IQR & standard deviation fences), 14 rigorous data quality validation rules (bounds, enums, nulls), and multi-table referential integrity join validation.

---

### PR #6
- **Status**: 🟢 PR Created
- **Branch**: `sql/lu-schema-db-integration`
- **Commit**: `4fbe9b5`
- **PR Link**: [Create PR #6](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/sql/lu-schema-db-integration)
- **LU**: `2.7`, `2.37`
- **Files**:
  - `sql/schema.sql`
  - `src/database.py`
- **Summary**: Designed relational database schema with foreign keys, composite unique constraints, automated timestamp triggers, and SQLite connection manager integration.

---

### PR #7
- **Status**: 🟢 PR Created
- **Branch**: `sql/lu-metrics-joins-queries`
- **Commit**: `32d22d4`
- **PR Link**: [Create PR #7](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/sql/lu-metrics-joins-queries)
- **LU**: `2.38`, `2.39`, `2.40`
- **Files**:
  - `sql/reporting_views.sql`
- **Summary**: Engineered SQL queries computing attendance rates, assignment completion rates, exam averages, and student-course join aggregations.

---

### PR #8
- **Status**: 🟢 PR Created
- **Branch**: `sql/lu-window-views-optimization`
- **Commit**: `8054379`
- **PR Link**: [Create PR #8](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/sql/lu-window-views-optimization)
- **LU**: `2.41`, `2.42`, `2.43`
- **Files**:
  - `sql/reporting_views.sql`
  - `sql/schema.sql`
- **Summary**: Created zero-latency SQL reporting views (`v_overview_kpis`, `v_risk_explorer`, `v_course_risk_summary`, `v_student_detail`, `v_data_quality_summary`) leveraging window ranking functions (`DENSE_RANK()`, `ROW_NUMBER()`) and performance indexes.

---

### PR #9
- **Status**: 🟢 PR Created
- **Branch**: `sql/lu-kpi-insight-validation`
- **Commit**: `8b60b18`
- **PR Link**: [Create PR #9](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/sql/lu-kpi-insight-validation)
- **LU**: `2.44`
- **Files**:
  - `sql/kpi_validation.sql`
  - `scripts/validate_kpis.py`
- **Summary**: Implemented dual-engine SQL vs. Python verification script confirming 100% KPI numerical parity and insight accuracy across all course cohorts.

---

### PR #10
- **Status**: 🟢 PR Created
- **Branch**: `data/lu-database-delivery`
- **Commit**: *(Pending push)*
- **PR Link**: [Create PR #10](https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/data/lu-database-delivery)
- **LU**: `Delivery & Documentation`
- **Files**:
  - `docs/SHALLY_DATA_SQL_PR_TRACKER.md`
  - `docs/DATA_DICTIONARY.md`
- **Summary**: Final documentation delivery uniting all 21 data and SQL learning units, quality audits, schema diagrams, and pull request verification links.
