import pandas as pd
import pytest

from src.data.db import query, tables


def test_query_returns_dataframe(tmp_db):
    """query() returns a DataFrame for a trivial SELECT."""
    result = query("SELECT 1 AS n", db_path=tmp_db)
    assert isinstance(result, pd.DataFrame)
    assert "n" in result.columns
    assert result["n"].iloc[0] == 1


def test_query_respects_db_path_override(tmp_db):
    """query() reads from the provided db_path, returning all fixture rows."""
    result = query("SELECT * FROM energy_data.hyperscaler_capex", db_path=tmp_db)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3


def test_tables_returns_dataframe(tmp_db):
    """tables() returns a DataFrame that includes a 'table_name' column."""
    result = tables(db_path=tmp_db)
    assert isinstance(result, pd.DataFrame)
    assert "table_name" in result.columns


def test_query_raises_on_bad_table(tmp_db):
    """query() raises a DuckDB error naming the missing table."""
    import duckdb
    with pytest.raises(duckdb.Error, match="nonexistent_table"):
        query("SELECT * FROM energy_data.nonexistent_table", db_path=tmp_db)
