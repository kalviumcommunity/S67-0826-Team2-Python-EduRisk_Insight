# Praveen Backend PR Tracker

## Status Legend
- ⬜ Not Started
- 🟡 In Progress
- 🟢 PR Created
- 🔵 Merged

## PR Roadmap

| PR | Status | Title | Main File/Area | LU |
|----|--------|-------|----------------|----|
| PR #1 | 🟢 | Data Ingestion | src/ingest.py | 2.2, 2.3, 2.15 |
| PR #2 | 🟢 | Data Validation | src/validate.py | 2.3, 2.14, 2.18, 2.19, 2.20, 2.24 |
| PR #3 | 🟢 | Data Transformation | src/transform.py | 2.5, 2.18, 2.19, 2.21, 2.22, 2.25 |
| PR #4 | 🟢 | Feature Engineering | src/features.py | 2.26, 2.27, 2.34 |
| PR #5 | 🟢 | Risk Engine | src/risk_rules.py | 2.34, 2.35, 2.36 |
| PR #6 | 🟢 | Analytics Engine | src/analytics/ | 2.6, 2.28, 2.30, 2.32 |
| PR #7 | 🟢 | Trend & Behaviour Analysis | src/analytics/ | 2.29, 2.31, 2.32 |
| PR #8 | 🟢 | KPI & Business Metrics | analytics/KPI logic | 2.6, 2.30, 2.34 |
| PR #9 | 🟢 | Insights & Anomaly Detection | src/insights.py | 2.28, 2.29, 2.35, 2.36 |
| PR #10 | 🟢 | Pipeline Orchestration | src/pipeline.py | 2.13, 2.58 |
| PR #11 | 🟢 | Backend Testing | tests/ | Backend testing |
| PR #12 | 🟢 | Backend Integration | backend integration | 2.13, 2.26, 2.58 |
| PR #13 | 🟢 | Automated Pipeline Execution | pipeline/scripts | 2.13, 2.58 |
| PR #14 | ⬜ | GitHub Validation / CI | .github/workflows/ | 2.59 |
| PR #15 | ⬜ | Backend Documentation & Delivery | README/docs | 2.60 |

## Completed PRs

### PR #1
Status: 🟢 PR Created
Branch: backend/lu-2.15-ingestion
Commit: e01c7a5c4e026de268d19e32685519dfb95ed1f7
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/tree/backend/lu-2.15-ingestion
Date: 2026-08-18

Files:
- src/ingest.py

LU:
- 2.2
- 2.3
- 2.15

Result:
- Data ingestion implementation completed (CSV & JSON loading, schema validation, error handling)
- Ingestion pipeline functions tested and verified

---

### PR #2
Status: 🟢 PR Created
Branch: backend/lu-validation
Commit: 58cf37390f39def8fd610ff2416703ded44c2a0d
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-validation
Date: 2026-08-19

Files:
- src/validate.py

LU:
- 2.3
- 2.14
- 2.18
- 2.19
- 2.20
- 2.24

Result:
- Data quality validation engine implemented (`DataQualityValidator`, `QualityRuleResult`, `ValidationReport`)
- Verified schema integrity, null checks, foreign key validity, attendance enum validation, and assignment/assessment score bounds
- 7 unit tests in `tests/test_validation.py` passed (100%)

---

### PR #3
Status: 🟢 PR Created
Branch: backend/lu-transformation
Commit: 80440f92187c02d99dfe81bc0f6f4ddbebc8c7e6
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-transformation
Date: 2026-08-20

Files:
- src/transform.py
- tests/test_transform.py

LU:
- 2.5
- 2.18
- 2.19
- 2.21
- 2.22
- 2.25

Result:
- Data transformation and standardization pipeline implemented (`clean_and_transform_data`, `CleanedDatasets`)
- Handles deduplication, string normalization, date parsing, invalid status pruning, score bound clipping [0, max_score], and foreign key referential integrity
- 7 unit tests in `tests/test_transform.py` passed (100%), full suite (31 tests) passing (100%)

---

### PR #4
Status: 🟢 PR Created
Branch: backend/lu-features
Commit: cc121e841fd8c45744257e41e5cae0c1dd977ce8
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-features
Date: 2026-08-21

Files:
- src/features.py
- tests/test_features.py

LU:
- 2.26
- 2.27
- 2.34

Result:
- High-performance vectorized feature engineering engine implemented (`compute_student_course_features`)
- Computes comprehensive attendance metrics (effective rate, recent rate, prior rate), assignment rates (completion rate, late submission rate, missing assignments count), assessment averages, and engagement trend classification (`improving`, `stable`, `declining`, `insufficient_data`)
- 4 unit tests in `tests/test_features.py` passed (100%), full test suite (31 tests) passing (100%)

---

### PR #5
Status: 🟢 PR Created
Branch: backend/lu-risk-engine
Commit: d8d877242ba027633c7a2056b57d7f8c76d3545e
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-risk-engine
Date: 2026-08-24

Files:
- src/risk_rules.py
- src/risk_explanations.py
- config/risk_thresholds.yaml
- tests/test_risk_engine.py

LU:
- 2.34
- 2.35
- 2.36

Result:
- Configurable rule-based risk scoring engine implemented (`RiskEngine`, `StudentRiskEvaluation`, `TriggeredReason`)
- Loads YAML risk thresholds and scoring rules dynamically (`config/risk_thresholds.yaml`)
- Transparent point accumulation with clear risk band assignment: High (Needs Review), Medium (Watch), Low (On Track)
- Human-readable explainable reason serialization and advisor recommendation helpers (`src/risk_explanations.py`)
- 4 unit tests in `tests/test_risk_engine.py` passed (100%), full test suite passing (100%)

---

### PR #6
Status: 🟢 PR Created
Branch: backend/lu-analytics
Commit: d3d6ed7fa0b7b6d7daae18a04f558a39eb0f887b
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-analytics
Date: 2026-08-25

Files:
- analytics/__init__.py
- analytics/cohort_analysis.py
- analytics/profiling.py
- tests/test_analytics.py

LU:
- 2.6
- 2.28
- 2.30
- 2.32

Result:
- Descriptive analytics and cohort profiling engine implemented (`generate_cohort_profile`, `analyze_cohort_disparities`)
- Computes comprehensive statistical distribution metrics across attendance, submission completion, quantiles, and engagement trends
- Multi-dimensional cohort disparity aggregation across courses and sections with high-risk percentage rates
- 5 unit tests in `tests/test_analytics.py` passed (100%), full test suite (36 tests) passing (100%)

---

### PR #7
Status: 🟢 PR Created
Branch: backend/lu-trend-analysis
Commit: 7a233571540916aef441daa225ec6aafdfddcefd
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-trend-analysis
Date: 2026-08-27

Files:
- analytics/__init__.py
- analytics/trend_analysis.py
- analytics/behaviour_analysis.py
- tests/test_analytics.py

LU:
- 2.29
- 2.31
- 2.32

Result:
- Longitudinal trend dynamics and student velocity trajectory engine implemented (`compute_weekly_trends`, `compute_student_trend_trajectories`)
- Student submission punctuality profiling and turnaround delay analysis (`analyze_submission_behaviour`)
- Consecutive unexcused absence streak detection and critical disengagement alerts (`detect_consecutive_absence_streaks`)
- Institutional behavioural summary profile metrics (`generate_behavioural_profile`)
- 16 unit tests in `tests/test_analytics.py` passed (100%), full test suite (38 tests) passing (100%)

---

### PR #8
Status: 🟢 PR Created
Branch: backend/lu-kpi-metrics
Commit: 75bf645db4b1b7c6bc59e12d44aff56ded077016
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-kpi-metrics
Date: 2026-08-31

Files:
- analytics/__init__.py
- analytics/kpi_metrics.py
- tests/test_analytics.py

LU:
- 2.6
- 2.30
- 2.34

Result:
- Executive headline academic KPI aggregation engine implemented (`compute_executive_kpis`)
- Comparative course and section scorecard with composite academic health scoring (`compute_course_level_kpis`)
- Institution-wide disengagement risk indicator profiling (`compute_disengagement_kpi_indicators`)
- Dual-engine SQL vs. Python parity validation audit utility (`validate_sql_vs_python_kpis`)
- 25 unit tests in `tests/test_analytics.py` passed (100%), full test suite (56 tests) passing (100%)

---

### PR #9
Status: 🟢 PR Created
Branch: backend/lu-insights
Commit: 6d47ee6d4b5847e30d7bbcebe803f25c754685ff
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-insights
Date: 2026-09-01

Files:
- src/insights.py
- tests/test_insights.py

LU:
- 2.28
- 2.29
- 2.35
- 2.36

Result:
- Dynamic cohort insights generator implemented (`generate_cohort_insights`, `InsightFinding`)
- Produces evidence-backed, explainable findings across section risk concentration, primary risk indicator drivers, and 14-day engagement trajectories
- Dynamic fallback handling for empty or unpopulated cohorts
- 3 unit tests in `tests/test_insights.py` passed (100%), full test suite (59 tests) passing (100%)

---

### PR #10
Status: 🟢 PR Created
Branch: backend/lu-pipeline
Commit: 1834897ff76868df3260c6ae53d1ec5cfcb0e3a5
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-pipeline
Date: 2026-09-01

Files:
- src/pipeline.py
- tests/test_pipeline.py

LU:
- 2.13
- 2.58

Result:
- End-to-end data pipeline orchestrator implemented (`run_pipeline`, `PipelineRunResult`)
- Fully orchestrates Ingestion -> 14-rule Data Validation -> Cleaning & Transformation -> Feature Computation -> Risk Scoring -> SQLite Persistence
- Generates snapshot outputs in `data/processed/` and logs pipeline audit run records in `pipeline_runs` table
- 1 unit test in `tests/test_pipeline.py` passed (100%), full test suite (59 tests) passing (100%)

---

### PR #11
Status: 🟢 PR Created
Branch: backend/lu-testing
Commit: 02e231b0e51381395fc0ba97f48ff1149e6f3dfa
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-testing
Date: 2026-09-01

Files:
- tests/__init__.py
- tests/test_acceptance.py
- tests/test_validation.py
- tests/test_reporting_service.py

LU:
- Backend testing

Result:
- Comprehensive backend test suite covering acceptance criteria, database schema objects, validation rules, and reporting services
- Verified explainability invariants (every flagged student with risk score > 0 has serialized human-readable reasons)
- 59 total tests across the suite passing (100%)

---

### PR #12
Status: 🟢 PR Created
Branch: backend/lu-integration
Commit: 180a677e4fb38e9dcce69a6a84dfa1d8db0cf7ff
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-integration
Date: 2026-09-01

Files:
- src/__init__.py
- src/database.py
- src/reporting.py
- sql/schema.sql
- sql/reporting_views.sql
- sql/kpi_validation.sql

LU:
- 2.13
- 2.26
- 2.58

Result:
- Relational SQLite schema DDL and performance index management (`src/database.py`, `sql/schema.sql`)
- High-performance SQL reporting views created for zero-latency dashboard queries (`sql/reporting_views.sql`: `v_overview_kpis`, `v_risk_explorer`, `v_course_risk_summary`, `v_student_detail`, `v_data_quality_summary`)
- Fully decoupled ReportingService layer with multi-dimensional filtering, student detail lookups, intervention action persistence, and top insight generation (`src/reporting.py`)
- Dual SQL validation queries implemented (`sql/kpi_validation.sql`)

---

### PR #13
Status: 🟢 PR Created
Branch: backend/lu-automation
Commit: e379c5feeb8169fb66c61bf8e1b64e0624a0d922
PR: https://github.com/kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight/pull/new/backend/lu-automation
Date: 2026-09-01

Files:
- scripts/generate_data.py
- scripts/run_pipeline.py
- scripts/validate_kpis.py
- scripts/health_check.py

LU:
- 2.13
- 2.58

Result:
- CLI pipeline execution runner with formatted duration, throughput, and risk distribution diagnostics (`scripts/run_pipeline.py`)
- Deterministic synthetic dataset generator producing authentic student engagement archetypes (A through F) and invalid quality fixtures (`scripts/generate_data.py`)
- Dual-engine SQL vs. Python KPI parity auditor (`scripts/validate_kpis.py`)
- System-wide acceptance and database health check script (`scripts/health_check.py`)







