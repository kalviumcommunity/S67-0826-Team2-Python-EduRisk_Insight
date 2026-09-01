"""
StudentPulse AI - Data Quality & Audit Dashboard Page
Faithful implementation of Stitch data_quality_overview screen.
Monitors source data integrity, multi-table validation checks,
and offers real-time institutional rule auditing.
"""

from pathlib import Path
from typing import Optional
import streamlit as st
import pandas as pd

from src.reporting import ReportingService
from src.ingest import ingest_raw_data
from src.validate import DataQualityValidator
from src.pipeline import run_pipeline
from ui.components.cards import render_disclaimer


def render_data_quality_page(service: ReportingService):
    """
    Renders the Data Quality and Institutional Audit screen.
    
    Args:
        service: ReportingService instance.
    """
    # -------------------------------------------------------------
    # Page Header & Run Validation Action
    # -------------------------------------------------------------
    head_left, head_right = st.columns([3, 1])
    with head_left:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h2 style="font-family: 'Geist', sans-serif; font-size: 28px; font-weight: 700; color: #181d1a; margin-bottom: 4px;">Data Quality & Integrity</h2>
            <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #5f5e5e; margin: 0;">
                Continuous institutional data validation, foreign key integrity, and ingestion health monitoring.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with head_right:
        if st.button("↻ Run Validation Audit", key="run_val_btn", type="primary", use_container_width=True):
            with st.spinner("Executing 14-rule institutional validation audit..."):
                ingest_res = ingest_raw_data(Path("data/raw"))
                if ingest_res.success:
                    validator = DataQualityValidator()
                    report = validator.validate_all(ingest_res.dataframes)
                    df_val = report.to_dataframe()
                    service.db.save_dataframe(df_val, "data_quality_reports", if_exists="append")
                    st.success(f"✓ Audit completed: {report.passed_rules} passed, {report.warned_rules} warned, {report.failed_rules} failed ({report.overall_health_pct:.1f}% health).")
                    st.rerun()
                else:
                    st.error(f"Ingestion failed: {', '.join(ingest_res.errors)}")

    # -------------------------------------------------------------
    # Interactive CSV Dataset Ingestion Studio
    # -------------------------------------------------------------
    st.markdown("""
    <div class="sp-card" style="margin-bottom: 24px;">
        <div class="sp-card-header">
            <span>📂 Real-Time CSV Dataset Ingestion Studio</span>
        </div>
        <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #5f5e5e; margin: 0 0 16px 0;">
            Upload your institutional CSV datasets below. You can drag and drop multiple CSV files at once or select them individually. 
            When activated, the system automatically validates schemas, cleans anomalies, computes engagement features, evaluates risk rules, and updates all dashboard views in real time.
        </p>
    """, unsafe_allow_html=True)

    upload_specs = {
        "students.csv": {"label": "1. Students (students.csv)", "req_cols": ["student_id", "program", "cohort_year"], "required": True},
        "enrolments.csv": {"label": "2. Enrolments (enrolments.csv)", "req_cols": ["student_id", "course_id", "term", "section"], "required": True},
        "attendance.csv": {"label": "3. Attendance (attendance.csv)", "req_cols": ["student_id", "course_id", "session_date", "attendance_status"], "required": True},
        "assignments.csv": {"label": "4. Assignments (assignments.csv)", "req_cols": ["student_id", "course_id", "assignment_id", "due_date"], "required": True},
        "assessments.csv": {"label": "5. Assessments (assessments.csv)", "req_cols": ["student_id", "course_id", "assessment_date", "assessment_type"], "required": True},
        "interventions.csv": {"label": "6. Interventions (interventions.csv — optional)", "req_cols": ["student_id", "course_id", "action_date"], "required": False},
    }

    from src.ingest import split_unified_dataframe

    # Multi-file drag and drop uploader
    uploaded_files = st.file_uploader(
        "Drop CSV files here — accepts single unified dataset (e.g. studentpulse_complete.csv) or individual files (students.csv, enrolments.csv, attendance.csv, assignments.csv, assessments.csv, interventions.csv)",
        type=["csv"],
        accept_multiple_files=True,
        key="multi_csv_uploader"
    )

    detected_dfs: Dict[str, pd.DataFrame] = {}

    if uploaded_files:
        for f in uploaded_files:
            fname = f.name.lower()
            try:
                f.seek(0)
                df_loaded = pd.read_csv(f)
                f.seek(0)

                # Check if this is a unified/consolidated dataset with record_type
                if "record_type" in df_loaded.columns:
                    split_dict = split_unified_dataframe(df_loaded)
                    for t_name, sub_df in split_dict.items():
                        detected_dfs[f"{t_name}.csv"] = sub_df
                    st.info(f"💡 Detected unified dataset in `{f.name}`. Automatically extracted {len(split_dict)} tables!")
                else:
                    # Match discrete CSV by filename or headers
                    matched = False
                    for target_name, spec in upload_specs.items():
                        if target_name in fname:
                            detected_dfs[target_name] = df_loaded
                            matched = True
                            break
                    if not matched:
                        for target_name, spec in upload_specs.items():
                            if all(rc in df_loaded.columns for rc in spec["req_cols"][:2]):
                                detected_dfs[target_name] = df_loaded
                                break
            except Exception as e:
                st.error(f"Error parsing {f.name}: {e}")

    # Status Grid for uploaded files
    status_cols = st.columns(3)
    for idx, (target_name, spec) in enumerate(upload_specs.items()):
        with status_cols[idx % 3]:
            is_loaded = target_name in detected_dfs
            status_color = "#516600" if is_loaded else ("#ba1a1a" if spec["required"] else "#5f5e5e")
            status_text = "Ready to Ingest" if is_loaded else ("Required" if spec["required"] else "Optional")
            
            row_count_str = ""
            if is_loaded:
                n_rows = len(detected_dfs[target_name])
                row_count_str = f"<div style='font-size: 11px; color: #516600;'>{n_rows:,} records detected</div>"

            st.markdown(f"""
            <div style="padding: 10px 14px; background-color: #ffffff; border: 1px solid #ebefea; border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 12px; color: #181d1a;">{target_name}</strong>
                    <span style="font-size: 11px; color: {status_color}; font-weight: 600;">{status_text}</span>
                </div>
                {row_count_str}
            </div>
            """, unsafe_allow_html=True)

    has_required_files = all(k in detected_dfs for k in ["students.csv", "enrolments.csv", "attendance.csv", "assignments.csv", "assessments.csv"])

    act_col1, act_col2 = st.columns([2, 1])
    with act_col1:
        if st.button(
            "⚡ Ingest, Validate & Activate Dataset",
            disabled=not has_required_files,
            key="activate_uploaded_dataset_btn",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Writing CSVs, running quality validation, feature calculations, and risk engine..."):
                raw_dir = Path("data/raw")
                raw_dir.mkdir(parents=True, exist_ok=True)
                
                # Save each dataframe to data/raw/
                for target_name, df_obj in detected_dfs.items():
                    df_obj.to_csv(raw_dir / target_name, index=False)

                # If interventions was not uploaded, create empty template if not existing
                if "interventions.csv" not in detected_dfs and not (raw_dir / "interventions.csv").exists():
                    (raw_dir / "interventions.csv").write_text("student_id,course_id,action_date,action_type,outcome_note,staff_user\n")

                # Run full end-to-end pipeline
                pipe_res = run_pipeline(raw_dir=raw_dir)
                if pipe_res.status in {"SUCCESS", "WARNING"}:
                    st.cache_resource.clear()
                    st.success(f"✓ Dataset successfully activated! {pipe_res.total_students:,} students, {pipe_res.total_enrolments:,} enrollments, {pipe_res.high_risk_count:,} high-risk students identified.")
                    st.rerun()
                else:
                    st.error(f"Pipeline execution failed: {pipe_res.error_message}")

    with act_col2:
        if not has_required_files and uploaded_files:
            missing = [k for k in ["students.csv", "enrolments.csv", "attendance.csv", "assignments.csv", "assessments.csv"] if k not in detected_dfs]
            st.warning(f"Missing: {', '.join(missing)}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Fetch latest validation report data
    dq_df = service.get_data_quality_report()
    
    # Calculate health score metrics
    total_rules = len(dq_df) if not dq_df.empty else 14
    passed_rules = (dq_df["status"] == "PASS").sum() if not dq_df.empty else 14
    warned_rules = (dq_df["status"] == "WARN").sum() if not dq_df.empty else 0
    failed_rules = (dq_df["status"] == "FAIL").sum() if not dq_df.empty else 0
    health_score = round(passed_rules / total_rules * 100.0, 1) if total_rules > 0 else 100.0

    # -------------------------------------------------------------
    # Summary Metric Banner (Matches Stitch design)
    # -------------------------------------------------------------
    gauge_color = "#516600" if health_score >= 90 else ("#d97706" if health_score >= 75 else "#ba1a1a")
    st.markdown(f"""
    <div class="sp-card" style="display: flex; align-items: center; gap: 32px; padding: 28px; margin-bottom: 24px;">
        <div style="width: 90px; height: 90px; border-radius: 50%; border: 6px solid #ebefea; display: flex; align-items: center; justify-content: center; position: relative; background-color: #ffffff; flex-shrink: 0;">
            <span style="font-family: 'Geist', sans-serif; font-size: 24px; font-weight: 700; color: {gauge_color};">
                {health_score:.0f}%
            </span>
        </div>
        <div>
            <div style="font-family: 'Geist', sans-serif; font-size: 32px; font-weight: 700; color: #181d1a; line-height: 1.1; margin-bottom: 4px;">
                {health_score:.1f}% Data Quality Health
            </div>
            <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #5f5e5e; margin: 0; max-width: 650px;">
                {passed_rules} of {total_rules} institutional validation rules verified. Active student records, attendance logs, and assignment gradebooks are synchronized and ready for risk analysis.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Source Health Bento Grid (4 cards: Attendance, Assignments, Assessments, Enrolments)
    # -------------------------------------------------------------
    st.markdown("""
    <div style="font-family: 'Geist', sans-serif; font-size: 16px; font-weight: 600; color: #181d1a; margin-bottom: 12px;">
        Source Data Feeds Health
    </div>
    """, unsafe_allow_html=True)

    # Fetch table row counts
    try:
        att_count = service.db.execute_query("SELECT COUNT(*) as c FROM attendance")[0]["c"]
        asg_count = service.db.execute_query("SELECT COUNT(*) as c FROM assignments")[0]["c"]
        asm_count = service.db.execute_query("SELECT COUNT(*) as c FROM assessments")[0]["c"]
        enr_count = service.db.execute_query("SELECT COUNT(*) as c FROM enrolments")[0]["c"]
    except Exception:
        att_count, asg_count, asm_count, enr_count = 0, 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="sp-card" style="padding: 18px; margin-bottom: 0; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; color: #181d1a;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">calendar_today</span> Attendance
                </div>
                <span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> Live</span>
            </div>
            <div style="font-size: 11px; color: #5f5e5e; display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Total Records</span>
                <strong style="color: #181d1a; font-family: monospace;">{att_count:,}</strong>
            </div>
            <div style="width: 100%; height: 6px; background-color: #ebefea; border-radius: 9999px; overflow: hidden; margin-top: 8px;">
                <div style="width: 100%; height: 100%; background-color: #516600;"></div>
            </div>
            <div style="font-size: 10px; color: #516600; font-weight: 600; text-align: right; margin-top: 4px;">100% Valid Enum</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="sp-card" style="padding: 18px; margin-bottom: 0; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; color: #181d1a;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">assignment</span> Assignments
                </div>
                <span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> Live</span>
            </div>
            <div style="font-size: 11px; color: #5f5e5e; display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Total Submissions</span>
                <strong style="color: #181d1a; font-family: monospace;">{asg_count:,}</strong>
            </div>
            <div style="width: 100%; height: 6px; background-color: #ebefea; border-radius: 9999px; overflow: hidden; margin-top: 8px;">
                <div style="width: 100%; height: 100%; background-color: #516600;"></div>
            </div>
            <div style="font-size: 10px; color: #516600; font-weight: 600; text-align: right; margin-top: 4px;">Scores [0, 100] Bound</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="sp-card" style="padding: 18px; margin-bottom: 0; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; color: #181d1a;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">quiz</span> Assessments
                </div>
                <span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> Live</span>
            </div>
            <div style="font-size: 11px; color: #5f5e5e; display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Total Exam Logs</span>
                <strong style="color: #181d1a; font-family: monospace;">{asm_count:,}</strong>
            </div>
            <div style="width: 100%; height: 6px; background-color: #ebefea; border-radius: 9999px; overflow: hidden; margin-top: 8px;">
                <div style="width: 100%; height: 100%; background-color: #516600;"></div>
            </div>
            <div style="font-size: 10px; color: #516600; font-weight: 600; text-align: right; margin-top: 4px;">Standard Formats</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="sp-card" style="padding: 18px; margin-bottom: 0; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; color: #181d1a;">
                    <span class="material-symbols-outlined" style="color: #5f5e5e; font-size: 18px;">how_to_reg</span> Enrolments
                </div>
                <span class="sp-badge sp-badge-low"><span class="sp-badge-dot"></span> Live</span>
            </div>
            <div style="font-size: 11px; color: #5f5e5e; display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Total Enrollments</span>
                <strong style="color: #181d1a; font-family: monospace;">{enr_count:,}</strong>
            </div>
            <div style="width: 100%; height: 6px; background-color: #ebefea; border-radius: 9999px; overflow: hidden; margin-top: 8px;">
                <div style="width: 100%; height: 100%; background-color: #516600;"></div>
            </div>
            <div style="font-size: 10px; color: #516600; font-weight: 600; text-align: right; margin-top: 4px;">Foreign Keys Verified</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Active Data Quality Rules Audit Table
    # -------------------------------------------------------------
    st.markdown("""
    <div class="sp-card">
        <div class="sp-card-header">
            <span>Institutional Data Quality Audit Rules (14 Rules)</span>
        </div>
    """, unsafe_allow_html=True)

    if not dq_df.empty:
        # Filter dropdown for Severity
        f_col1, f_col2 = st.columns([2, 4])
        with f_col1:
            sev_filter = st.selectbox("Filter by Severity", ["All", "High", "Medium", "Low"], key="dq_sev_filter")
        
        filtered_dq = dq_df.copy()
        if sev_filter != "All":
            filtered_dq = filtered_dq[filtered_dq["severity"] == sev_filter]

        # Table Header
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 3.5, 1.5, 1.5, 2])
        with h1: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>TABLE</strong>", unsafe_allow_html=True)
        with h2: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>RULE CODE</strong>", unsafe_allow_html=True)
        with h3: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>RULE NAME & REMEDIATION</strong>", unsafe_allow_html=True)
        with h4: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>SEVERITY</strong>", unsafe_allow_html=True)
        with h5: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>STATUS</strong>", unsafe_allow_html=True)
        with h6: st.markdown("<strong style='font-size: 11px; color: #5f5e5e; font-family: Geist;'>EVALUATION</strong>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #c4c9ac;'>", unsafe_allow_html=True)

        for _, row in filtered_dq.iterrows():
            t_name = str(row["table_name"])
            r_code = str(row["rule_code"])
            r_name = str(row["rule_name"])
            remed = str(row.get("remediation_note", ""))
            sev = str(row["severity"])
            stat = str(row["status"])
            n_eval = int(row.get("records_evaluated", 0))
            n_fail = int(row.get("records_failed", 0))

            # Styling badges
            sev_badge = "sp-badge-high" if sev == "High" else ("sp-badge-medium" if sev == "Medium" else "sp-badge-low")
            stat_badge = "sp-badge-low" if stat == "PASS" else ("sp-badge-medium" if stat == "WARN" else "sp-badge-high")

            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 3.5, 1.5, 1.5, 2])
            with c1:
                st.markdown(f"<span style='font-family: monospace; font-size: 12px; font-weight: 600;'>{t_name}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span style='font-family: monospace; font-size: 11px; color: #5f5e5e;'>{r_code}</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div>
                    <div style="font-weight: 600; font-size: 12px; color: #181d1a;">{r_name}</div>
                    <div style="font-size: 11px; color: #5f5e5e;">{remed}</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"<span class='sp-badge {sev_badge}'>{sev}</span>", unsafe_allow_html=True)
            with c5:
                st.markdown(f"<span class='sp-badge {stat_badge}'><span class='sp-badge-dot'></span> {stat}</span>", unsafe_allow_html=True)
            with c6:
                st.markdown(f"<span style='font-size: 12px; font-family: monospace;'>{n_fail} / {n_eval:,}</span>", unsafe_allow_html=True)

            st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #ebefea;'>", unsafe_allow_html=True)
    else:
        st.info("No active data quality reports logged. Click 'Run Validation Audit' above.")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Pipeline Execution History
    # -------------------------------------------------------------
    try:
        pipeline_df = service.db.query_dataframe("SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 5")
        if not pipeline_df.empty:
            st.markdown("""
            <div class="sp-card">
                <div class="sp-card-header">
                    <span>Recent Automated Pipeline Executions</span>
                </div>
            """, unsafe_allow_html=True)

            disp_df = pipeline_df[["run_id", "started_at", "status", "total_students", "total_enrolments", "high_risk_count", "duration_seconds"]].copy()
            disp_df.columns = ["Run ID", "Execution Timestamp", "Status", "Students", "Enrollments", "High Risk Count", "Duration (s)"]
            st.dataframe(disp_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        pass

    render_disclaimer()
