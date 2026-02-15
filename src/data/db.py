"""DuckDB query helper for research notebooks.

Provides a thin wrapper around DuckDB for querying the centralized
research database. All data pipelines write to data/research.duckdb;
notebooks read from it via this module.

Usage in a marimo notebook:

    from src.data.db import query

    df = query("SELECT * FROM energy_data.eia860_generators WHERE operating_year >= 2020")
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "research.duckdb"


def query(sql: str, db_path: Path | str | None = None) -> pd.DataFrame:
    """Execute SQL against the research database, return DataFrame.

    Parameters
    ----------
    sql : str
        SQL query to execute.
    db_path : Path or str, optional
        Override the default database path. Useful for testing.

    Returns
    -------
    pd.DataFrame
    """
    path = str(db_path or DB_PATH)
    with duckdb.connect(path, read_only=True) as con:
        return con.execute(sql).df()


def tables(db_path: Path | str | None = None) -> pd.DataFrame:
    """List all tables in the research database."""
    return query(
        "SELECT table_schema, table_name, estimated_size "
        "FROM information_schema.tables "
        "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
        "ORDER BY table_schema, table_name",
        db_path=db_path,
    )
