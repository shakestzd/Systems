import marimo

__generated_with = "0.19.11"
app = marimo.App(width="full", app_title="Research Source Tracker")


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo
    import pandas as pd

    _repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(_repo_root))
    return Path, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Research Source Tracker

    *Systems / Where AI Capital Lands*

    ---

    Tracks manually-retrievable primary sources across all deep dives.
    Edit `data/external/manual_sources.csv` to update status or add new sources.
    Retrieved files go in `data/external/` at the path in the `local_filename` column.
    """)
    return


@app.cell
def _(Path, pd):
    _repo_root = Path(__file__).parent.parent
    sources = pd.read_csv(_repo_root / "data" / "external" / "manual_sources.csv")

    # Clean up multi-value columns for display
    sources["dds"] = sources["supporting_dds"].str.replace(";", " · ")
    sources["claims"] = sources["analytical_claims"].str.replace(";", " · ")

    # Status ordering for sort
    _status_order = {"pending": 0, "in_progress": 1, "retrieved": 2, "verified": 3}
    sources["status_rank"] = sources["status"].map(_status_order).fillna(9)

    # Priority ordering
    _priority_order = {"P0": 0, "P1": 1, "P2": 2}
    sources["priority_rank"] = sources["priority"].map(_priority_order).fillna(9)
    return (sources,)


@app.cell(hide_code=True)
def _(mo, sources):
    _total = len(sources)
    _pending = (sources["status"] == "pending").sum()
    _retrieved = (sources["status"] == "retrieved").sum()
    _verified = (sources["status"] == "verified").sum()
    _p0 = ((sources["priority"] == "P0") & (sources["status"] == "pending")).sum()

    mo.hstack([
        mo.stat(label="Total Sources", value=str(_total)),
        mo.stat(label="Pending", value=str(_pending), caption="need retrieval"),
        mo.stat(label="Retrieved", value=str(_retrieved), caption="in data/external/"),
        mo.stat(label="Verified", value=str(_verified), caption="cited in notebook"),
        mo.stat(label="P0 Pending", value=str(_p0), caption="do these first"),
    ])
    return


@app.cell(hide_code=True)
def _(mo, sources):
    _p0_pending = sources[
        (sources["priority"] == "P0") & (sources["status"] == "pending")
    ][["source_name", "supporting_dds", "access_type", "estimated_minutes", "access_path"]]

    if len(_p0_pending) > 0:
        mo.callout(
            mo.md(
                "## Do These First — P0 Pending\n\n"
                + "\n\n".join(
                    f"**{row['source_name']}** `{row['supporting_dds']}`  \n"
                    f"Access: `{row['access_type']}` · ~{row['estimated_minutes']} min  \n"
                    f"Path: {row['access_path'][:120]}{'...' if len(str(row['access_path'])) > 120 else ''}"
                    for _, row in _p0_pending.iterrows()
                )
            ),
            kind="warn",
        )
    else:
        mo.callout(mo.md("All P0 sources retrieved."), kind="success")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## All Sources
    """)
    return


@app.cell
def _(mo, sources):
    filter_priority = mo.ui.multiselect(
        options=["P0", "P1", "P2"],
        value=["P0", "P1", "P2"],
        label="Priority",
    )
    filter_status = mo.ui.multiselect(
        options=["pending", "in_progress", "retrieved", "verified"],
        value=["pending", "in_progress"],
        label="Status",
    )
    filter_dd = mo.ui.multiselect(
        options=sorted(
            {dd for dds in sources["supporting_dds"].str.split(";") for dd in dds}
        ),
        value=[],
        label="Deep Dive",
    )
    mo.hstack([filter_priority, filter_status, filter_dd], gap="1rem")
    return filter_dd, filter_priority, filter_status


@app.cell
def _(filter_dd, filter_priority, filter_status, sources):
    _mask = (
        sources["priority"].isin(filter_priority.value)
        & sources["status"].isin(filter_status.value)
    )
    if filter_dd.value:
        _mask = _mask & sources["supporting_dds"].apply(
            lambda x: any(dd in x for dd in filter_dd.value)
        )

    filtered = (
        sources[_mask]
        .sort_values(["priority_rank", "status_rank", "estimated_minutes"])
        .reset_index(drop=True)
    )
    return (filtered,)


@app.cell
def _(filtered, mo):
    _display = filtered[[
        "priority", "status", "source_name", "dds", "claims",
        "access_type", "estimated_minutes", "local_filename",
    ]].rename(columns={
        "priority": "Pri",
        "status": "Status",
        "source_name": "Source",
        "dds": "DDs",
        "claims": "Claims",
        "access_type": "Access",
        "estimated_minutes": "Min",
        "local_filename": "Save to",
    })

    mo.ui.table(
        _display,
        selection=None,
        show_column_summaries=False,
        pagination=True,
        page_size=20,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## Access Instructions (selected row)
    """)
    return


@app.cell
def _(filtered, mo):
    id_select = mo.ui.dropdown(
        options={row["source_name"]: row["id"] for _, row in filtered.iterrows()},
        label="Select source for full access instructions",
        value=None,
    )
    id_select
    return (id_select,)


@app.cell
def _(id_select, mo, sources):
    if id_select.value is None:
        mo.md("*Select a source above to see full retrieval instructions.*")
    else:
        _row = sources[sources["id"] == id_select.value].iloc[0]
        mo.md(f"""
        ### {_row['source_name']}

        | Field | Value |
        |:---|:---|
        | **Priority** | {_row['priority']} |
        | **Status** | {_row['status']} |
        | **Deep Dives** | {_row['supporting_dds']} |
        | **Analytical Claims** | {_row['analytical_claims']} |
        | **Access Type** | {_row['access_type']} |
        | **Estimated Time** | {_row['estimated_minutes']} minutes |
        | **Save to** | `{_row['local_filename']}` |

        **Access Path:**
        ```
        {_row['access_path']}
        ```

        **What to extract / Notes:**
        {_row['notes']}
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## How to Update Status

    Edit `data/external/manual_sources.csv` directly.
    Status values: `pending` → `in_progress` → `retrieved` → `verified`

    When a source is `retrieved`, place the file at the path in `local_filename`
    and add the key figures to `data/external/source_citations.csv` so they
    can be loaded into the stats computation cell in the relevant notebook.

    ### Access Type Legend

    | Type | Meaning |
    |:---|:---|
    | `direct_download` | URL → direct PDF/file download, no auth needed |
    | `browser_navigation` | Free but requires JS-enabled browser + navigation |
    | `registration` | Free with email registration |
    | `edgar_search` | EDGAR full-text or CIK search, free |
    | `paywall_workaround` | Paywalled; try archive.ph, monthly free articles, or find Reuters/Bloomberg confirmation |
    | `foia_request` | Requires formal public records request; allow days/weeks |
    | `direct_access` | Free with minor fee (e.g. Delaware $10) |
    """)
    return


if __name__ == "__main__":
    app.run()
