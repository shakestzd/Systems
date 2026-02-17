# Marimo notebook: Energy Infrastructure Market Impacts
import marimo as mo

app = mo.app()

@app.cell
def _(date_str="2026-02-13"):
    import datetime as dt
    ts = dt.date.fromisoformat(date_str)
    mo.md(f"# Energy Infrastructure Buildout Impacts\n\nDate: {ts}")
    return ts

@app.cell
def _():
    mo.md(
        """
        Research objective: Assess how transmission buildout (HV lines, substations) is impacting supply and pricing
        of key components (power transformers, switchgear) in other markets, especially utilities in developing countries.

        Key questions:
        - Are global lead times and prices for transformers/switchgear rising due to OECD/AI-driven grid expansions?
        - Do developing-country utilities face procurement delays or cost inflation disproportionate to income levels?
        - What bottlenecks (steel laminations, copper, grain-oriented electrical steel, manufacturing capacity) bind supply?

        Approach:
        - Data: manufacturer lead times, tender prices, World Bank procurement datasets, IEA/IRENA grid investment reports,
          FRED commodity series (copper, steel), customs/import price indexes, utility tenders.
        - Methods: systems dynamics causal map (capacity expansion, order backlog, price), Bayesian priors on bottleneck elasticity,
          regime switching to capture boom/plateau cycles.
        """
    )

@app.cell
def _():
    mo.md("## Data sources to collect and loaders")

@app.cell
def _():
    import pandas as pd
    sources = pd.DataFrame(
        [
            {"name": "IEA Transmission Investment", "type": "report", "status": "todo"},
            {"name": "IRENA Grid Integration", "type": "report", "status": "todo"},
            {"name": "World Bank procurement (transformers)", "type": "portal", "status": "todo"},
            {"name": "FRED: Copper, Steel", "type": "timeseries", "status": "wired"},
            {"name": "UN Comtrade HS codes (transformers/switchgear)", "type": "trade", "status": "wired"},
            {"name": "World Bank Indicators (power sector)", "type": "api", "status": "wired"},
            {"name": "YFinance (OEM equities)", "type": "finance", "status": "wired"},
        ]
    )
    sources

@app.cell
def _():
    mo.md("## Modeling sketch (SD)")

@app.cell
def _():
    mo.md(
        """
        Stocks/flows:
        - Manufacturing capacity (transformers, switchgear)
        - Order backlog; delivery lead time
        - Price level; input commodity costs (Cu, steel)
        - Demand from OECD grid buildout vs. developing-country utilities

        Feedbacks:
        - Higher demand -> backlog -> longer lead times -> price increases -> capacity investment lag
        - Price increases -> rationing/prioritization -> developing-country procurement delays
        """
    )

@app.cell
def _():
    mo.md("## Loaders demo")

@app.cell
def _():
    # FRED demo: copper and steel proxies (COMMBL for steel? use CU; steel via Producer Price Index series)
    from src.data.fred import get_multiple
    fred_df = get_multiple(["PCU3311--3311--", "PCU1022--1022--", "PCU3312--3312--"])  # example PPI series
    fred_df.tail(3)

@app.cell
def _():
    # Comtrade demo: HS 8504 (transformers), 8537/8538/8535 (switchgear) example for 2023 imports by India
    from src.data.comtrade import hs_trade
    trade_df = hs_trade(flow="import", reporter="India", partner="World", period="2023", cmd_code="8504")
    trade_df.head()

@app.cell
def _():
    # World Bank demo: Indicator EG.ELC.ACCS.ZS (Access to electricity) for Sub-Saharan Africa
    from src.data.worldbank import wb_indicator
    wb_df = wb_indicator("EG.ELC.ACCS.ZS", country="SSF", date="2000:2024")
    wb_df.head()

@app.cell
def _():
    # Finance demo: OEM equities (ABB, Siemens) prices
    from src.data.finance import get_prices
    prices = get_prices(["ABBNY", "SIEGY"], period="3y")
    prices.tail(3)

@app.cell
def _():
    mo.md("## Next steps")

@app.cell
def _():
    mo.md("- Catalog datasets; define HS codes; prototype lead-time proxy via trade and tender data.")

if __name__ == "__main__":
    app.run()
