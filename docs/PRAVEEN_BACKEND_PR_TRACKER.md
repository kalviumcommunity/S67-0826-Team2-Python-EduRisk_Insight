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
| PR #3 | ⬜ | Data Transformation | src/transform.py | 2.5, 2.18, 2.19, 2.21, 2.22, 2.25 |
| PR #4 | ⬜ | Feature Engineering | src/features.py | 2.26, 2.27, 2.34 |
| PR #5 | ⬜ | Risk Engine | src/risk_rules.py | 2.34, 2.35, 2.36 |
| PR #6 | ⬜ | Analytics Engine | src/analytics/ | 2.6, 2.28, 2.30, 2.32 |
| PR #7 | ⬜ | Trend & Behaviour Analysis | src/analytics/ | 2.29, 2.31, 2.32 |
| PR #8 | ⬜ | KPI & Business Metrics | analytics/KPI logic | 2.6, 2.30, 2.34 |
| PR #9 | ⬜ | Insights & Anomaly Detection | src/insights.py | 2.28, 2.29, 2.35, 2.36 |
| PR #10 | ⬜ | Pipeline Orchestration | src/pipeline.py | 2.13, 2.58 |
| PR #11 | ⬜ | Backend Testing | tests/ | Backend testing |
| PR #12 | ⬜ | Backend Integration | backend integration | 2.13, 2.26, 2.58 |
| PR #13 | ⬜ | Automated Pipeline Execution | pipeline/scripts | 2.13, 2.58 |
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
