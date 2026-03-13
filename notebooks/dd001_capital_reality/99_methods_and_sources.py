import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="DD-001 Sources & Verification",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # DD-001 — Sources & Publication Gate

    **Companion to:** `observable/src/dd001.md` — *The $13 Trillion AI Bet*

    This notebook is the **pre-publication verification record** for DD-001.
    Every number that appears in the Observable article is listed here with its
    source, a link to verify it, and a verification status.

    **Before marking an article as published:**
    1. Click each URL to verify the source says what the article claims
    2. Note any caveats or discrepancies in the `notes` column of `data/external/dd001_stat_sources.csv`
    3. Set `verified=true` and today's date in `verified_date` in the CSV
    4. Re-run the pipeline: `uv run python -c "from src.data.pipelines import _make_pipeline, dd001_stat_sources; p = _make_pipeline(); p.run(dd001_stat_sources())"`
    5. Reload this notebook — the publication gate will turn green when all required stats are verified
    """)
    return


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo
    import pandas as pd

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))

    from src.data.db import query

    return mo, pd, query


@app.cell
def _(query):
    # ── Load the verification manifest ────────────────────────────────────────
    stat_sources = query(
        """
        SELECT
            stat_key, description, unit, source_type,
            primary_source, source_detail, url, citation_key,
            db_table, verified, verified_date, notes
        FROM energy_data.dd001_stat_sources
        ORDER BY
            CASE source_type
                WHEN 'uncited'    THEN 1
                WHEN 'hardcoded'  THEN 2
                WHEN 'citation_csv' THEN 3
                WHEN 'computed_db'  THEN 4
                WHEN 'derived'    THEN 5
                ELSE 6
            END,
            stat_key
        """
    )

    # ── Load current computed values from stats pipeline ──────────────────────
    stats_values = query(
        """
        SELECT key, value, value_text
        FROM energy_data.source_citations
        """
    )
    stats_dict = dict(zip(stats_values["key"], stats_values["value"]))
    return (stat_sources,)


@app.cell
def _(pd, query):
    # ── Data freshness ────────────────────────────────────────────────────────
    freshness_queries = {
        "hyperscaler_capex": "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.hyperscaler_capex",
        "mag7_market_caps": "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.mag7_market_caps",
        "cloud_revenue": "SELECT MAX(quarter) AS as_of FROM energy_data.cloud_revenue",
        "hyperscaler_ocf": "SELECT MAX(period) AS as_of FROM energy_data.hyperscaler_ocf",
        "capex_guidance": "SELECT MAX(year) AS as_of FROM energy_data.capex_guidance",
        "source_citations": "SELECT MAX(source_date) AS as_of FROM energy_data.source_citations",
        "dd001_stat_sources": "SELECT COUNT(*) AS as_of FROM energy_data.dd001_stat_sources",
    }

    freshness_rows = []
    for _metric, _sql in freshness_queries.items():
        _val = query(_sql).iloc[0, 0]
        freshness_rows.append({"table": _metric, "as_of": str(_val)})

    data_freshness = pd.DataFrame(freshness_rows)
    return (data_freshness,)


@app.cell
def _(mo, stat_sources):
    # ── Compute publication readiness ─────────────────────────────────────────
    total = len(stat_sources)
    verified_count = int(stat_sources["verified"].sum())
    unverified = stat_sources[~stat_sources["verified"]]
    uncited = stat_sources[stat_sources["source_type"] == "uncited"]
    hardcoded = stat_sources[stat_sources["source_type"].isin(["hardcoded"])]

    n_uncited = len(uncited)
    n_hardcoded = len(hardcoded)
    n_unverified = len(unverified)

    _ready = n_unverified == 0 and n_uncited == 0

    if _ready:
        _gate = mo.callout(
            mo.md(f"**READY TO PUBLISH** — all {total} stats verified"),
            kind="success",
        )
    elif n_uncited > 0 or n_hardcoded > 0:
        _gate = mo.callout(
            mo.md(
                f"**NOT READY** — {n_unverified}/{total} stats unverified | "
                f"**{n_uncited} uncited** (hardcoded in article, no pipeline source) | "
                f"**{n_hardcoded} hardcoded** (in pipeline, needs citation)"
            ),
            kind="danger",
        )
    else:
        _gate = mo.callout(
            mo.md(
                f"**IN PROGRESS** — {verified_count}/{total} stats verified "
                f"({n_unverified} remaining)"
            ),
            kind="warn",
        )

    _gate
    return hardcoded, n_hardcoded, n_uncited, uncited


@app.cell(hide_code=True)
def _(hardcoded, mo, n_hardcoded, n_uncited, uncited):
    # ── Show action-required items prominently ────────────────────────────────
    _sections = []

    if n_uncited > 0:
        _rows = []
        for _, _row in uncited.iterrows():
            _rows.append(
                f"- **`{_row['stat_key']}`** — {_row['description']}\n"
                f"  - {_row['notes']}"
            )
        _sections.append(
            mo.callout(
                mo.md("### Action required — uncited values in article\n\n" + "\n".join(_rows)),
                kind="danger",
            )
        )

    if n_hardcoded > 0:
        _rows = []
        for _, _row in hardcoded.iterrows():
            _rows.append(
                f"- **`{_row['stat_key']}`** — {_row['description']}\n"
                f"  - {_row['notes']}"
            )
        _sections.append(
            mo.callout(
                mo.md("### Action required — hardcoded values needing citations\n\n" + "\n".join(_rows)),
                kind="warn",
            )
        )

    mo.vstack(_sections) if _sections else mo.md("")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Source Verification Table

    Every stat used in the DD-001 Observable article. Sorted by urgency: uncited → hardcoded → citations → computed → derived.

    **To verify a source:**
    1. Click the link in the **URL** column
    2. Confirm the source says what the article claims (check description + source_detail)
    3. Open `data/external/dd001_stat_sources.csv`, set `verified=true` and `verified_date=YYYY-MM-DD`
    4. Re-run pipeline and reload this notebook

    Color guide: 🔴 uncited (no pipeline source) · 🟠 hardcoded (needs citation) · ⚪ unverified · ✅ verified
    """)
    return


@app.cell
def _(mo, pd, stat_sources):
    # ── Build formatted verification table ───────────────────────────────────
    _rows = []
    for _, _r in stat_sources.iterrows():
        _stype = _r["source_type"]
        _verified = bool(_r["verified"])

        # Status indicator
        if _stype == "uncited":
            _status = "🔴 UNCITED"
        elif _stype == "hardcoded":
            _status = "🟠 HARDCODED"
        elif _verified:
            _status = f"✅ {_r['verified_date']}"
        else:
            _status = "⚪ unverified"

        # URL — make it a clickable link if available
        _url_raw = str(_r["url"]).strip()
        if _url_raw and _url_raw not in ("nan", "", "paywalled"):
            _url_cell = f"[link]({_url_raw})"
        elif _url_raw == "paywalled":
            _url_cell = "🔒 paywalled"
        else:
            _url_cell = "—"

        # Truncate long strings for display
        _detail = str(_r["source_detail"])[:80] + "…" if len(str(_r["source_detail"])) > 80 else str(_r["source_detail"])
        _notes_val = str(_r["notes"])
        _notes_short = _notes_val[:60] + "…" if len(_notes_val) > 60 else _notes_val

        _rows.append({
            "status": _status,
            "stat_key": _r["stat_key"],
            "description": _r["description"],
            "unit": _r["unit"],
            "source_type": _stype,
            "primary_source": str(_r["primary_source"])[:50],
            "source_detail": _detail,
            "url": _url_cell,
            "notes": _notes_short if _notes_val != "nan" else "",
        })

    _df = pd.DataFrame(_rows)

    mo.ui.table(_df, selection=None, show_column_summaries=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Full Source Detail

    For each stat, the complete source detail including notes and any caveats.
    Expand this section when verifying individual claims.
    """)
    return


@app.cell
def _(mo, stat_sources):
    # ── Full detail cards — grouped by source type ────────────────────────────
    _type_order = ["uncited", "hardcoded", "citation_csv", "computed_db", "derived"]
    _type_labels = {
        "uncited":     "🔴 Uncited — values hardcoded in article prose with no pipeline source",
        "hardcoded":   "🟠 Hardcoded — values in pipeline but lacking formal citations",
        "citation_csv":"📋 Citation CSV — values from source_citations.csv (manually researched)",
        "computed_db": "🗄️  Computed DB — values calculated from DuckDB tables (SEC filings / Yahoo Finance)",
        "derived":     "🔢 Derived — values calculated from other stats in the pipeline",
    }
    _sections = []
    for _stype in _type_order:
        _group = stat_sources[stat_sources["source_type"] == _stype]
        if _group.empty:
            continue
        _items = []
        for _, _r in _group.iterrows():
            _url_raw = str(_r["url"]).strip()
            if _url_raw and _url_raw not in ("nan", "", "paywalled"):
                _url_md = f"[Verify source →]({_url_raw})"
            elif _url_raw == "paywalled":
                _url_md = "🔒 Paywalled — verify via institutional access or news coverage"
            else:
                _url_md = "No direct URL — see source_detail"

            _verified_str = f"✅ Verified {_r['verified_date']}" if bool(_r["verified"]) else "⚪ Not yet verified"
            _notes_val = str(_r["notes"])
            _notes_md = f"\n  > ⚠️ {_notes_val}" if _notes_val and _notes_val != "nan" else ""

            _items.append(
                f"**`{_r['stat_key']}`** ({_r['unit']}) — {_r['description']}\n"
                f"  - **Source:** {_r['primary_source']}\n"
                f"  - **Detail:** {_r['source_detail']}\n"
                f"  - **DB table:** `{_r['db_table']}`\n"
                f"  - {_url_md}\n"
                f"  - {_verified_str}"
                f"{_notes_md}"
            )

        _sections.append(mo.accordion({
            _type_labels[_stype]: mo.md("\n\n".join(_items))
        }))

    mo.vstack(_sections)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Data Freshness

    When was each underlying database table last updated? These dates determine
    how current the computed stats are.
    """)
    return


@app.cell(hide_code=True)
def _(data_freshness, mo):
    mo.ui.table(data_freshness, selection=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Verification Workflow

    ```
    1. Open this notebook in edit mode:
       uv run marimo edit notebooks/dd001_capital_reality/99_methods_and_sources.py

    2. For each stat in the table above:
       a. Click the URL link to open the primary source
       b. Confirm the source says what the article claims
       c. Note any discrepancy in the notes field

    3. When a source is verified, update the CSV:
       data/external/dd001_stat_sources.csv
       — Set verified=true
       — Set verified_date=YYYY-MM-DD (today)

    4. Re-run the pipeline to sync to DuckDB:
       uv run python -c "
         from src.data.pipelines import _make_pipeline, dd001_stat_sources
         p = _make_pipeline()
         p.run(dd001_stat_sources(), write_disposition='replace')
       "

    5. Reload this notebook — publication gate updates automatically

    6. For UNCITED values: add them to source_citations.csv first,
       then parametrize in the article (replace hardcode with stats.* reference),
       then re-run the full reference pipeline.
    ```

    ### What counts as "verified"?

    - **computed_db**: Verify the underlying data in the DuckDB table matches the SEC
      filing or data source. Run the SQL query in the source_detail field.
    - **citation_csv**: Click the URL, confirm the number appears in the source.
      For paywalled articles, check if the figure appears in news coverage.
    - **derived**: Verify the formula (source_detail) is correct, and that the
      underlying inputs are themselves verified.
    - **hardcoded**: Find the primary source, add it to source_citations.csv,
      then switch to citation_csv type. Mark verified after adding the source.
    - **uncited**: Find the source, add to source_citations.csv, parametrize in
      the article. Until parametrized, the article cannot be published.
    """)
    return


if __name__ == "__main__":
    app.run()
