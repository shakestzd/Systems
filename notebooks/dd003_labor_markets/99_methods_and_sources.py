import marimo

__generated_with = "0.19.11"
app = marimo.App(width="compact", app_title="DD-003 Methods & Sources")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # DD-003 Methods & Reproducibility
    ## AI Capital Flows and Labor Impact

    Companion notebook for:
    `notebooks/dd003_labor_markets/01_who_gets_hired.py`
    """
    )
    return


@app.cell
def _():
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    from src.data.db import query

    return mo, query, sys


if __name__ == "__main__":
    app.run()
