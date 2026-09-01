"""
StudentPulse AI - Data Ingestion Module
Safely loads, inspects, and validates raw CSV and JSON source datasets for academic analytics.
Supports Lesson Unit 2.15 (CSV & JSON Data Ingestion).
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".json"}

REQUIRED_SOURCE_FILES = [
    "students.csv",
    "enrolments.csv",
    "attendance.csv",
    "assignments.csv",
    "assessments.csv",
]

OPTIONAL_SOURCE_FILES = [
    "interventions.csv"
]


@dataclass
class IngestionResult:
    """Container for ingested datasets and metadata."""
    success: bool
    dataframes: Dict[str, pd.DataFrame] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    file_metadata: Dict[str, dict] = field(default_factory=dict)


def load_csv_safely(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """
    Safely load a CSV file without crashing on malformed rows or empty contents.
    
    Args:
        file_path: Path to the target CSV file.
        
    Returns:
        DataFrame if successfully loaded, None on unrecoverable read failure.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File does not exist: %s", path)
        return None

    if not path.is_file():
        logger.warning("Path is not a regular file: %s", path)
        return None

    if path.stat().st_size == 0:
        logger.warning("File is empty (0 bytes): %s", path)
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, low_memory=False)
        return df
    except pd.errors.EmptyDataError:
        logger.warning("File contains no data: %s", path)
        return pd.DataFrame()
    except Exception as e:
        logger.error("Failed to read CSV %s: %s", path, str(e))
        return None


def load_json_safely(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """
    Safely load a JSON file into a DataFrame without crashing on empty or malformed contents.
    Supports JSON arrays, record streams, and keyed dictionaries.
    
    Args:
        file_path: Path to the target JSON file.
        
    Returns:
        DataFrame if successfully loaded, None on unrecoverable read failure.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File does not exist: %s", path)
        return None

    if not path.is_file():
        logger.warning("Path is not a regular file: %s", path)
        return None

    if path.stat().st_size == 0:
        logger.warning("File is empty (0 bytes): %s", path)
        return pd.DataFrame()

    try:
        # First attempt standard pd.read_json
        df = pd.read_json(path)
        return df
    except (ValueError, json.JSONDecodeError):
        # Attempt fallback to python json parser for custom structures or empty structures
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return pd.DataFrame()
                raw_data = json.loads(content)
                if isinstance(raw_data, list):
                    return pd.DataFrame(raw_data)
                elif isinstance(raw_data, dict):
                    return pd.json_normalize(raw_data)
                else:
                    logger.error("Unexpected JSON structure in %s: %s", path, type(raw_data))
                    return None
        except Exception as inner_e:
            logger.error("Failed to parse JSON %s: %s", path, str(inner_e))
            return None
    except Exception as e:
        logger.error("Failed to read JSON %s: %s", path, str(e))
        return None


def load_file_safely(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """
    Safely loads a dataset file (CSV or JSON) based on file extension.
    Rejects unsupported file formats cleanly.
    
    Args:
        file_path: Path to CSV or JSON file.
        
    Returns:
        DataFrame if successfully parsed, None otherwise.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        logger.error("Unsupported file format '%s' for file: %s", suffix, path)
        return None

    if suffix == ".csv":
        return load_csv_safely(path)
    elif suffix == ".json":
        return load_json_safely(path)

    return None


def split_unified_dataframe(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Splits a single consolidated DataFrame containing 'record_type' column into individual domain tables.
    """
    tables: Dict[str, pd.DataFrame] = {}
    if df.empty or "record_type" not in df.columns:
        return tables

    table_col_mapping = {
        "student": ("students", ["student_id", "program", "cohort_year"]),
        "students": ("students", ["student_id", "program", "cohort_year"]),
        "enrolment": ("enrolments", ["student_id", "course_id", "term", "section"]),
        "enrolments": ("enrolments", ["student_id", "course_id", "term", "section"]),
        "attendance": ("attendance", ["student_id", "course_id", "session_date", "attendance_status"]),
        "assignment": ("assignments", ["student_id", "course_id", "assignment_id", "due_date", "submitted_at", "score", "max_score"]),
        "assignments": ("assignments", ["student_id", "course_id", "assignment_id", "due_date", "submitted_at", "score", "max_score"]),
        "assessment": ("assessments", ["student_id", "course_id", "assessment_date", "assessment_type", "score", "max_score"]),
        "assessments": ("assessments", ["student_id", "course_id", "assessment_date", "assessment_type", "score", "max_score"]),
        "intervention": ("interventions", ["student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"]),
        "interventions": ("interventions", ["student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"]),
    }

    for rt, sub in df.groupby(df["record_type"].astype(str).str.lower()):
        if rt in table_col_mapping:
            t_name, cols = table_col_mapping[rt]
            avail_cols = [c for c in cols if c in sub.columns]
            clean_sub = sub[avail_cols].dropna(how="all").copy()
            tables[t_name] = clean_sub

    return tables


def ingest_raw_data(data_dir: Union[str, Path]) -> IngestionResult:
    """
    Ingests all core and optional academic CSV and JSON datasets from the target directory.
    Supports both discrete multi-file directories and single consolidated datasets.
    
    Args:
        data_dir: Path to directory containing raw datasets.
        
    Returns:
        IngestionResult containing loaded DataFrames and quality metadata.
    """
    data_dir = Path(data_dir)
    result = IngestionResult(success=True)

    if not data_dir.exists() or not data_dir.is_dir():
        result.success = False
        result.errors.append(f"Source directory does not exist: {data_dir}")
        return result

    # Check for consolidated/unified all-in-one CSV in data_dir
    unified_files = list(data_dir.glob("*complete*.csv")) + list(data_dir.glob("*unified*.csv"))
    if not unified_files:
        # Check all CSV files in data_dir for record_type column
        for candidate in data_dir.glob("*.csv"):
            try:
                head = pd.read_csv(candidate, nrows=2)
                if "record_type" in head.columns:
                    unified_files.append(candidate)
                    break
            except Exception:
                pass

    if unified_files:
        unified_path = unified_files[0]
        logger.info("Detected unified consolidated dataset at %s", unified_path)
        u_df = load_csv_safely(unified_path)
        if u_df is not None and "record_type" in u_df.columns:
            split_tables = split_unified_dataframe(u_df)
            for t_name, df_table in split_tables.items():
                result.dataframes[t_name] = df_table
                result.file_metadata[t_name] = {
                    "row_count": len(df_table),
                    "column_count": len(df_table.columns),
                    "columns": list(df_table.columns),
                    "file_size_bytes": unified_path.stat().st_size,
                    "source_format": "csv (unified)",
                }
            # Also save discrete CSV files into data_dir for standard persistence
            for t_name, df_table in split_tables.items():
                target_csv = data_dir / f"{t_name}.csv"
                df_table.to_csv(target_csv, index=False)
            
            # If interventions not present, add empty
            if "interventions" not in result.dataframes:
                result.dataframes["interventions"] = pd.DataFrame(columns=[
                    "student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"
                ])

            return result

    # Standard Discrete Multi-File Ingestion
    for filename in REQUIRED_SOURCE_FILES:
        table_name = Path(filename).stem
        csv_path = data_dir / f"{table_name}.csv"
        json_path = data_dir / f"{table_name}.json"

        target_path: Optional[Path] = None
        if csv_path.exists():
            target_path = csv_path
        elif json_path.exists():
            target_path = json_path

        if target_path is None:
            result.success = False
            result.errors.append(f"Missing required dataset: {table_name} (.csv or .json)")
            continue

        df = load_file_safely(target_path)
        if df is None:
            result.success = False
            result.errors.append(f"Could not parse required dataset: {target_path.name}")
            continue

        result.dataframes[table_name] = df
        result.file_metadata[table_name] = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "file_size_bytes": target_path.stat().st_size,
            "source_format": target_path.suffix.lstrip(".").lower(),
        }

    # Load optional tables (e.g., interventions)
    for filename in OPTIONAL_SOURCE_FILES:
        table_name = Path(filename).stem
        csv_path = data_dir / f"{table_name}.csv"
        json_path = data_dir / f"{table_name}.json"

        target_path = None
        if csv_path.exists():
            target_path = csv_path
        elif json_path.exists():
            target_path = json_path

        if target_path is not None:
            df = load_file_safely(target_path)
            if df is not None:
                result.dataframes[table_name] = df
                result.file_metadata[table_name] = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                    "file_size_bytes": target_path.stat().st_size,
                    "source_format": target_path.suffix.lstrip(".").lower(),
                }
            else:
                result.warnings.append(f"Optional dataset {target_path.name} could not be parsed.")
        else:
            # Create empty default dataframe with required columns
            if table_name == "interventions":
                empty_df = pd.DataFrame(columns=[
                    "student_id", "course_id", "action_date", "action_type", "outcome_note", "staff_user"
                ])
                result.dataframes[table_name] = empty_df
                result.warnings.append(f"Optional {table_name} dataset not found; initialized empty table.")

    return result
