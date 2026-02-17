import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Who Pays for the Grid
    ## Part 3 — The Cost-Liability Map

    *Thandolwethu Zwelakhe Dlamini*

    ---

    AI infrastructure creates durable physical obligations, but the capital
    structure that builds it is designed to exit. This notebook maps the
    asymmetry: who owns assets, who bears maintenance, and what determines
    who is left holding the cost when the capital moves.

    The durability taxonomy from DD-001 classifies investments by asset
    lifespan. Here it is extended to classify by *liability holder*:

    - **Equipment** (6-year life): sits on hyperscaler balance sheet — they
      bear the depreciation risk. Portable: can be redeployed to other facilities.
    - **Data center construction** (40-year life): on hyperscaler balance sheet,
      but land and building are geographically fixed. Harder to repurpose.
    - **Grid upgrades** (30–40-year life): in utility rate base — on *ratepayer*
      tabs. Not owned by the hyperscaler at all. Even if the data center exits,
      the amortization continues.
    - **Tax abatements** (foregone public revenue): sunk cost to the state
      regardless of data center tenure.

    The key regulatory lever is FERC AD24-11: an active FERC proceeding on
    whether large loads (data centers) should pay their own interconnection
    upgrade costs, or have those costs socialized across all ratepayers — the
    same cost-causation question resolved for generators in Order 2023.

    **This is Part 3 of three.** It asks: what is the full cost-liability map
    across the AI infrastructure buildout, and which regulatory decisions
    determine who pays?
    """)
    return


if __name__ == "__main__":
    app.run()
