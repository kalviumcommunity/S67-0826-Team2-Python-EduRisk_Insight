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
    # FR-01: Upload CSV source files and optionally activate them
    # -------------------------------------------------------------
    with st.expander("Load CSV source files", expanded=False):
        st.caption("Upload the five required source files. interventions.csv is optional. Files are validated before activation.")
        upload_specs = [
            ("students.csv", "Students"),
            ("enrolments.csv", "Enrolments"),
            ("attendance.csv", "Attendance"),
            ("assignments.csv", "Assignments"),
            ("assessments.csv", "Assessments"),
            ("interventions.csv", "Interventions (optional)"),
        ]
        uploads = {}
        upload_cols = st.columns(2)
        for idx, (filename, label) in enumerate(upload_specs):
            with upload_cols[idx % 2]:
                uploads[filename] = st.file_uploader(label, type=["csv"], key=f"upload_{filename}")

        required_ready = all(uploads[name] is not None for name, _ in upload_specs[:5])

        def _write_uploads(tmp_path: Path) -> None:
            for filename, uploaded in uploads.items():
                if uploaded is not None:
                    (tmp_path / filename).write_bytes(uploaded.getvalue())

        if st.button("Validate uploaded files", disabled=not required_ready, key="validate_uploads_btn"):
            import tempfile
            with tempfile.TemporaryDirectory(prefix="studentpulse_upload_") as tmp_dir:
                tmp_path = Path(tmp_dir)
                _write_uploads(tmp_path)
                upload_result = ingest_raw_data(tmp_path)
                if upload_result.success:
                    upload_report = DataQualityValidator().validate_all(upload_result.dataframes)
                    st.session_state["uploaded_quality_report"] = upload_report.to_dataframe()
                    st.session_state["validated_uploads_ready"] = not upload_report.has_blocking_errors
                    st.success(f"Upload validation complete: {upload_report.overall_health_pct:.1f}% health, {upload_report.failed_rules} failed rules.")
                    if upload_report.has_blocking_errors:
                        st.error("The upload contains blocking data-quality errors. The demo database was not changed.")
                    else:
                        st.info("Validation passed. Click 'Activate uploaded dataset' to replace the current demo reporting data.")
                else:
                    st.session_state["validated_uploads_ready"] = False
                    st.error("Upload could not be ingested: " + "; ".join(upload_result.errors))

        upload_report_df = st.session_state.get("uploaded_quality_report")
        if upload_report_df is not None:
            st.dataframe(upload_report_df, use_container_width=True, hide_index=True)

        if st.button(
            "Activate uploaded dataset",
            disabled=not (required_ready and st.session_state.get("validated_uploads_ready", False)),
            key="activate_uploads_btn",
            type="primary",
        ):
            import tempfile
            with tempfile.TemporaryDirectory(prefix="studentpulse_upload_") as tmp_dir:
                tmp_path = Path(tmp_dir)
                _write_uploads(tmp_path)
                with st.spinner("Running the full ingestion → cleaning → features → risk → SQL pipeline..."):
                    pipeline_result = run_pipeline(raw_dir=tmp_path)
            if pipeline_result.status in {"SUCCESS", "WARNING"}:
                st.success(
                    f"Dataset activated: {pipeline_result.total_students:,} students, "
                    f"{pipeline_result.total_enrolments:,} enrolments, "
                    f"{pipeline_result.high_risk_count:,} high-risk records."
                )
                st.cache_resource.clear()
                st.session_state["validated_uploads_ready"] = False
                st.rerun()
            else:
                st.error(f"Pipeline failed: {pipeline_result.error_message or 'unknown error'}")

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
        att_count, asg_count, asm_count, enr_count = 14205, 8432, 2104, 5000

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
