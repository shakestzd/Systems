import pandas as pd
import pytest

from src.data.cloud_capex import capex_to_revenue_ratio


# Sample data fixtures
@pytest.fixture
def capex_df():
    return pd.DataFrame([
        {"ticker": "AMZN", "year": 2024, "capex_bn": 79.6},
        {"ticker": "AMZN", "year": 2025, "capex_bn": 131.8},
        {"ticker": "GOOGL", "year": 2024, "capex_bn": 52.5},
        {"ticker": "GOOGL", "year": 2025, "capex_bn": 91.4},
        {"ticker": "MSFT", "year": 2024, "capex_bn": 48.3},
        {"ticker": "MSFT", "year": 2025, "capex_bn": 83.1},
    ])


@pytest.fixture
def cloud_rev_df():
    rows = []
    for ticker, qtrs in [
        ("AMZN", [25.0, 26.3, 27.5, 28.8, 29.3, 30.9, 33.0, 35.6]),
        ("GOOGL", [9.6, 10.3, 11.4, 12.0, 12.3, 13.6, 15.2, 17.7]),
        ("MSFT", [26.7, 28.5, 24.1, 25.5, 26.8, 29.9, 30.9, 32.9]),
    ]:
        for i, rev in enumerate(qtrs):
            year = 2024 if i < 4 else 2025
            q = (i % 4) + 1
            rows.append({"ticker": ticker, "quarter": f"{year}-Q{q}", "revenue_bn": rev})
    return pd.DataFrame(rows)


def test_ratio_computed_correctly(capex_df, cloud_rev_df):
    """AMZN 2024: capex=79.6, revenue=25.0+26.3+27.5+28.8=107.6, ratio≈0.74."""
    result = capex_to_revenue_ratio(capex_df, cloud_rev_df, ["AMZN"], [2024])
    assert len(result) == 1
    row = result.iloc[0]
    assert row["ticker"] == "AMZN"
    assert row["year"] == 2024
    expected_ratio = 79.6 / (25.0 + 26.3 + 27.5 + 28.8)
    assert abs(row["ratio"] - expected_ratio) < 0.01


def test_output_has_expected_columns(capex_df, cloud_rev_df):
    """Result DataFrame must have exactly the columns: ticker, year, capex_bn, revenue_bn, ratio."""
    result = capex_to_revenue_ratio(capex_df, cloud_rev_df, ["AMZN", "GOOGL", "MSFT"], [2024, 2025])
    assert list(result.columns) == ["ticker", "year", "capex_bn", "revenue_bn", "ratio"]


def test_output_sorted_by_ticker_year(capex_df, cloud_rev_df):
    """Result must be sorted ascending by [ticker, year]."""
    result = capex_to_revenue_ratio(capex_df, cloud_rev_df, ["MSFT", "AMZN", "GOOGL"], [2024, 2025])
    expected_order = result.sort_values(["ticker", "year"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_order)


def test_missing_ticker_raises_valueerror(capex_df, cloud_rev_df):
    """Requesting a ticker not in data must raise ValueError naming the missing ticker."""
    with pytest.raises(ValueError, match="NVDA"):
        capex_to_revenue_ratio(capex_df, cloud_rev_df, ["AMZN", "NVDA"], [2024])


def test_ratio_above_one_when_capex_exceeds_revenue(capex_df, cloud_rev_df):
    """When capex exceeds annual cloud revenue, ratio must be > 1.0."""
    # Build minimal data where capex clearly exceeds revenue
    capex_high = pd.DataFrame([{"ticker": "AMZN", "year": 2024, "capex_bn": 999.0}])
    result = capex_to_revenue_ratio(capex_high, cloud_rev_df, ["AMZN"], [2024])
    assert result.iloc[0]["ratio"] > 1.0
