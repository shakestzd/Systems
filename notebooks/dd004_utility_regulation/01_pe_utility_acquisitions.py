import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="compact",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Who Pays for the Grid
    ## Part 1 — Private Equity and Regulated Utilities

    *Thandolwethu Zwelakhe Dlamini*

    ---

    AI infrastructure creates durable physical obligations — but the capital that
    creates them is mobile. Private equity fund lifecycles run 7–10 years. Rate
    base assets amortize over 30–40 years. When the capital exits, someone is
    left holding the infrastructure.

    This notebook investigates the first mechanism: private equity acquisition
    of regulated electric and gas utilities. Since 2010, at least 91 fund-backed
    utility acquisitions have been filed with FERC. The PNM/Blackstone deal
    ($11.5B, New Mexico's largest electric utility) is the current live case.

    The central question is not whether rates go up after PE acquisition — the
    causal evidence is contested. The question is whether the cost allocation
    *mechanism* changes: who bears the long-duration liability when a short-
    duration financial structure owns a regulated monopoly.

    **This is Part 1 of three.** It asks: what is the pattern of PE utility
    acquisitions, what do state regulators approve, and what does the PNM/
    Blackstone case reveal about the mechanism?
    """)
    return


if __name__ == "__main__":
    app.run()
