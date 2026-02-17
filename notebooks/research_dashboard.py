import marimo

__generated_with = "0.19.11"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import os

    # Load databases
    dives_df = pd.read_csv("research/deep_dives.csv")

    mo.md("# 🏛️ Systems Intelligence Research Terminal")
    return dives_df, mo


@app.cell
def _(dives_df, mo):
    mo.md("## 📡 Research Pipeline")

    # Simple Pipeline visualization
    mo.md("""
    The research follows a three-phase causal architecture:
    1.  **Phase I: Supply Infrastructure** (Materials & Equipment)
    2.  **Phase II: Grid Integration** (Networks & Regulation)
    3.  **Phase III: Systemic Impact** (Economic & Environmental Outcomes)
    """)

    pipeline_table = mo.ui.table(
        dives_df[["ID", "Phase", "Topic", "Status", "Measurable Outcome"]],
        selection="single",
        label="Select a node in the pipeline to view the technical specification."
    )
    pipeline_table
    return (pipeline_table,)


@app.cell
def _(pipeline_table):
    selected_node = pipeline_table.value

    return (selected_node,)


@app.cell
def _(dives_df, mo, selected_node):
    if not selected_node.empty:
        # Get full data
        row_id = selected_node.iloc[0]['ID']
        node = dives_df[dives_df['ID'] == row_id].iloc[0]

        mo.md(f"### Technical Spec: {node['Topic']}")

        # Build status options dynamically to avoid invalid default values
        _default_statuses = ["Pending", "In-Progress", "Completed"]
        _existing_statuses = [s for s in dives_df['Status'].dropna().unique().tolist() if isinstance(s, str)]
        _status_options = list(dict.fromkeys(_default_statuses + _existing_statuses))
        _status_value = node['Status'] if isinstance(node['Status'], str) and node['Status'] in _status_options else _default_statuses[0]

        out=mo.vstack([
            mo.md(f"**Causal Question:** {node['Core Question']}"),
            mo.md(f"**Measurable Outcome:** `{node['Measurable Outcome']}`"),
            mo.md(f"**Phase:** {node['Phase']}"),
            mo.ui.text_area(label="Analyst Notes / Key Findings", value="", full_width=True),
            mo.hstack([
                mo.ui.dropdown(options=_status_options, value=_status_value, label="Status"),
                mo.ui.button(label="Update Node")
            ])
        ])
    else:
        mo.md("_Select a node from the Pipeline table above to view the deep-dive research protocol._")
    out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📊 Strategic Variables (Policy Neutral)
    Adjust the following physical and market variables to simulate different structural scenarios.
    """)
    return


@app.cell
def _(mo):


    learning_rate = mo.ui.slider(5, 30, value=15, label="Learning Rate (%) - Wright's Law")
    grid_delay = mo.ui.slider(1, 20, value=7, label="Institutional Grid Delay (Years)")

    mo.hstack([learning_rate, grid_delay])
    return


if __name__ == "__main__":
    app.run()
