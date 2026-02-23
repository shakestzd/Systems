import duckdb
import pytest


@pytest.fixture
def tmp_db(tmp_path):
    """Minimal DuckDB in a temp dir with schema matching the research DB."""
    db = tmp_path / "test.duckdb"
    con = duckdb.connect(str(db))
    con.execute("CREATE SCHEMA IF NOT EXISTS energy_data")
    con.execute("""
        CREATE TABLE energy_data.hyperscaler_capex AS
        SELECT 'AMZN' AS ticker, DATE '2024-03-31' AS date, 13.9 AS capex_bn
        UNION ALL SELECT 'GOOGL', DATE '2024-03-31', 12.0
        UNION ALL SELECT 'MSFT', DATE '2024-03-31', 7.8
    """)
    con.close()
    return db
