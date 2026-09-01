"""
StudentPulse AI - End-to-End Orchestration Pipeline
Automates the complete workflow from raw CSV data to SQL reporting database.
"""

from dataclasses import dataclass
import datetime
import logging
from pathlib import Path
import time
from typing import Optional
import pandas as pd

from src.ingest import ingest_raw_data
from src.validate import DataQualityValidator, ValidationReport
from src.transform import clean_and_transform_data
from src.features import compute_student_course_features
from src.risk_rules import RiskEngine
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("studentpulse.pipeline")


@dataclass
class PipelineRunResult:
    """Summary metrics of an automated pipeline execution."""
    run_id: str
    status: str  # 'SUCCESS', 'WARNING', 'FAILED'
    duration_seconds: float
    total_students: int
    total_enrolments: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    validation_health_pct: float
    error_message: Optional[str] = None


def run_pipeline(
    raw_dir: Path = Path("data/raw"),
    db_path: Path = Path("data/studentpulse.db"),
    config_path: Path = Path("config/risk_thresholds.yaml"),
    processed_dir: Path = Path("data/processed")
) -> PipelineRunResult:
    """
    Executes the entire reproducible data pipeline:
    RAW CSV -> INGESTION -> VALIDATION -> CLEANING -> FEATURES -> RISK -> SQL DB
    
    Args:
        raw_dir: Directory with raw CSV files.
        db_path: Target SQLite database path.
        config_path: YAML configuration file for risk engine.
        processed_dir: Directory to save processed snapshot CSVs.
        
    Returns:
        PipelineRunResult object with execution summary statistics.
    """
    start_time = time.time()
    run_id = f"run_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.info("Starting StudentPulse pipeline execution: %s", run_id)

    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ingestion
    logger.info("Step 1: Ingesting raw CSV files from %s...", raw_dir)
    ingestion_res = ingest_raw_data(raw_dir)
    if not ingestion_res.success:
        err = "; ".join(ingestion_res.errors)
        logger.error("Ingestion failed: %s", err)
        return PipelineRunResult(
            run_id=run_id,
            status="FAILED",
            duration_seconds=time.time() - start_time,
            total_students=0,
            total_enrolments=0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            validation_health_pct=0.0,
            error_message=err,
        )

    # 2. Data Quality & Schema Validation
    logger.info("Step 2: Performing 14-rule data quality audit...")
    validator = DataQualityValidator(run_id=run_id)
    val_report: ValidationReport = validator.validate_all(ingestion_res.dataframes)
    logger.info("Validation completed. Health score: %.1f%% (Passed: %d, Warned: %d, Failed: %d)",
                val_report.overall_health_pct, val_report.passed_rules, val_report.warned_rules, val_report.failed_rules)

    # 3. Data Cleaning and Normalization
    logger.info("Step 3: Cleaning and transforming datasets...")
    cleaned = clean_and_transform_data(ingestion_res.dataframes)

    # 4. Feature Engineering
    logger.info("Step 4: Computing student-course features...")
    features_df = compute_student_course_features(cleaned)
    logger.info("Features computed for %d student-course records.", len(features_df))

    # 5. Risk Intelligence & Scoring
    logger.info("Step 5: Evaluating rule-based risk signals from config %s...", config_path)
    risk_engine = RiskEngine(config_path=config_path)
    risk_df = risk_engine.evaluate_features_dataframe(features_df)

    high_risk = int((risk_df["risk_level"] == "High").sum()) if not risk_df.empty else 0
    med_risk = int((risk_df["risk_level"] == "Medium").sum()) if not risk_df.empty else 0
    low_risk = int((risk_df["risk_level"] == "Low").sum()) if not risk_df.empty else 0
    logger.info("Risk scoring complete: High=%d, Medium=%d, Low=%d", high_risk, med_risk, low_risk)

    # 6. Database Persistence & SQL Views
    logger.info("Step 6: Persisting data to SQLite database at %s...", db_path)
    db = DatabaseManager(db_path=db_path)
    db.init_database()

    # Save facts and dimension tables
    db.save_dataframe(cleaned.students, "students", if_exists="replace")
    db.save_dataframe(cleaned.enrolments, "enrolments", if_exists="replace")
    db.save_dataframe(cleaned.attendance, "attendance", if_exists="replace")
    db.save_dataframe(cleaned.assignments, "assignments", if_exists="replace")
    db.save_dataframe(cleaned.assessments, "assessments", if_exists="replace")
    if not cleaned.interventions.empty:
        db.save_dataframe(cleaned.interventions, "interventions", if_exists="replace")

    # Save feature and risk tables
    db.save_dataframe(features_df, "student_course_features", if_exists="replace")
    db.save_dataframe(risk_df, "risk_assessments", if_exists="replace")

    # Save data quality report
    val_df = val_report.to_dataframe()
    db.save_dataframe(val_df, "data_quality_reports", if_exists="append")

    # Re-apply views and indexes
    db.init_database()

    # Save processed CSVs snapshot
    features_df.to_csv(processed_dir / "student_course_features.csv", index=False)
    risk_df.to_csv(processed_dir / "risk_assessments.csv", index=False)
    val_df.to_csv(processed_dir / "latest_quality_report.csv", index=False)

    duration = round(time.time() - start_time, 2)

    # Log Pipeline Run
    run_log = pd.DataFrame([{
        "run_id": run_id,
        "started_at": datetime.datetime.fromtimestamp(start_time, tz=datetime.timezone.utc).isoformat(),
        "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "SUCCESS" if not val_report.has_blocking_errors else "WARNING",
        "total_students": len(cleaned.students),
        "total_enrolments": len(cleaned.enrolments),
        "high_risk_count": high_risk,
        "medium_risk_count": med_risk,
        "low_risk_count": low_risk,
        "duration_seconds": duration,
    }])
    db.save_dataframe(run_log, "pipeline_runs", if_exists="append")

    logger.info("Pipeline execution %s finished in %.2fs with status %s.", run_id, duration, "SUCCESS" if not val_report.has_blocking_errors else "WARNING")

    return PipelineRunResult(
        run_id=run_id,
        status="SUCCESS" if not val_report.has_blocking_errors else "WARNING",
        duration_seconds=duration,
        total_students=len(cleaned.students),
        total_enrolments=len(cleaned.enrolments),
        high_risk_count=high_risk,
        medium_risk_count=med_risk,
        low_risk_count=low_risk,
        validation_health_pct=val_report.overall_health_pct,
    )
