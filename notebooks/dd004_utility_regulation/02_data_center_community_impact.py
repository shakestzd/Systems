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
    ## Part 2 — Data Centers and Rural Communities

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Tech companies are barreling into rural communities with the promise of
    good jobs. The investment figures are real — $1B+ campuses, announced with
    press conferences and gubernatorial handshakes. The jobs are not.

    Hyperscale data centers invest $3–10M per permanent direct employee. A
    comparable manufacturing facility at the same capital investment would
    employ 10–30x more workers. The public subsidies — tax abatements, sales
    tax exemptions on equipment — run $100K–$500K+ per permanent job created.
    Virginia's data center tax exemptions cost the state $437M in foregone
    revenue in FY2023 alone.

    Meanwhile, the physical footprint is durable: grid upgrades, water
    withdrawal, zoning locked in for industrial use. These persist regardless
    of whether the data center stays.

    **This is Part 2 of three.** It asks: what do communities actually receive
    from data center siting, what costs do they bear, and what happens when
    the data center leaves?
    """)
    return


if __name__ == "__main__":
    app.run()
