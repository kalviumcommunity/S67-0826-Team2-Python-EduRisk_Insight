"""
StudentPulse AI - CLI Pipeline Execution Script
Runs the data pipeline and displays summary statistics and data quality health.
"""

import argparse
import logging
from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_pipeline")


def main():
    parser = argparse.ArgumentParser(description="Run StudentPulse AI Data Pipeline")
    parser.add_argument("--raw", type=str, default="data/raw", help="Directory with raw CSV files")
    parser.add_argument("--db", type=str, default="data/studentpulse.db", help="Target SQLite DB path")
    parser.add_argument("--config", type=str, default="config/risk_thresholds.yaml", help="Risk thresholds config")
    parser.add_argument("--processed", type=str, default="data/processed", help="Processed outputs directory")
    args = parser.parse_args()

    print("=" * 70)
    print(" STUDENTPULSE AI — ACADEMIC ENGAGEMENT & EARLY-RISK PIPELINE")
    print("=" * 70)

    result = run_pipeline(
        raw_dir=Path(args.raw),
        db_path=Path(args.db),
        config_path=Path(args.config),
        processed_dir=Path(args.processed),
    )

    print("-" * 70)
    print(f" Execution Status:        {result.status}")
    print(f" Run ID:                  {result.run_id}")
    print(f" Total Duration:          {result.duration_seconds:.2f} seconds")
    print(f" Unique Students:         {result.total_students:,}")
    print(f" Total Enrollments:       {result.total_enrolments:,}")
    print(f" High Risk (Needs Review): {result.high_risk_count:,}")
    print(f" Medium Risk (Watch):     {result.medium_risk_count:,}")
    print(f" Low Risk (On Track):     {result.low_risk_count:,}")
    print(f" Validation Health Score: {result.validation_health_pct:.1f}%")
    print("=" * 70)

    if result.status == "FAILED":
        print(f"Error: {result.error_message}")
        sys.exit(1)
    else:
        print("✓ Pipeline completed successfully. Ready for dashboard display.")
        sys.exit(0)


if __name__ == "__main__":
    main()
