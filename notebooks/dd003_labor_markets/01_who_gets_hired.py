import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="AI Capital and Labor Markets")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # AI Capital Flows and Labor Impact
    ## Who Gets Hired, Who Gets Displaced, and Where Do Jobs Land?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Placeholder — analysis in progress.
    """
    )
    return


@app.cell
def _():
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    from src.notebook import setup

    setup()

    return mo, setup, sys


if __name__ == "__main__":
    app.run()
