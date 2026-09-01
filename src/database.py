"""
StudentPulse AI - Database Management Module
Handles SQLite persistence, schema initialization, reporting view execution, and query utilities.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/studentpulse.db")
SCHEMA_SQL_PATH = Path("sql/schema.sql")
VIEWS_SQL_PATH = Path("sql/reporting_views.sql")


class DatabaseManager:
    """Manages SQLite database connections, schema updates, and persistence."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Returns an active SQLite connection with row factory configured."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys and WAL mode for concurrent reads
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def init_database(self, schema_path: Optional[Path] = None, views_path: Optional[Path] = None) -> None:
        """
        Executes schema and reporting view DDL scripts.
        
        Args:
            schema_path: Path to schema.sql
            views_path: Path to reporting_views.sql
        """
        schema_file = schema_path or SCHEMA_SQL_PATH
        views_file = views_path or VIEWS_SQL_PATH

        with self.get_connection() as conn:
            if schema_file.exists():
                with open(schema_file, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
                logger.info("Executed schema DDL from %s", schema_file)

            if views_file.exists():
                with open(views_file, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
                logger.info("Executed reporting views DDL from %s", views_file)

    def save_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> int:
        """
        Persists a DataFrame to a database table.
        
        Args:
            df: Target DataFrame to persist.
            table_name: Destination SQL table name.
            if_exists: 'replace', 'append', or 'fail'.
            
        Returns:
            Number of rows saved.
        """
        with self.get_connection() as conn:
            if df.empty:
                if if_exists == "replace":
                    try:
                        conn.execute(f"DELETE FROM {table_name};")
                    except Exception:
                        pass
                return 0

            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            return len(df)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns list of dictionaries.
        
        Args:
            query: SQL statement to execute.
            params: Optional tuple of query parameters.
            
        Returns:
            List of dict records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def query_dataframe(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns results as a pandas DataFrame.
        
        Args:
            query: SQL statement.
            params: Query parameters.
            
        Returns:
            pandas DataFrame.
        """
        with self.get_connection() as conn:
            if params:
                return pd.read_sql_query(query, conn, params=params)
            return pd.read_sql_query(query, conn)
