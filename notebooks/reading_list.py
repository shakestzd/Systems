import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="Reading List",
    css_file="../src/notebook_theme/custom.css",
    html_head_file="../src/notebook_theme/head.html",
)


@app.cell
def _():
    import uuid
    from datetime import datetime
    from pathlib import Path

    import duckdb
    import marimo as mo
    import pandas as pd

    return datetime, duckdb, mo, pd, uuid, Path


@app.cell
def _(Path, duckdb):
    db_path = Path(__file__).parent.parent / "data" / "research.duckdb"

    with duckdb.connect(str(db_path)) as _con:
        _con.execute("""
            CREATE TABLE IF NOT EXISTS energy_data.reading_notes (
                note_id   VARCHAR,
                source_type VARCHAR,
                source_key  VARCHAR,
                note_text   TEXT,
                tags        VARCHAR,
                created_at  TIMESTAMP,
                updated_at  TIMESTAMP
            )
        """)
        _con.execute("""
            CREATE TABLE IF NOT EXISTS energy_data.reading_custom_sources (
                source_id     VARCHAR,
                title         VARCHAR,
                author        VARCHAR,
                url           VARCHAR,
                source_type   VARCHAR,
                relevance_tags VARCHAR,
                description   TEXT,
                added_at      TIMESTAMP
            )
        """)

    return (db_path,)


@app.cell
def _(mo):
    get_refresh, set_refresh = mo.state(0)
    return get_refresh, set_refresh


@app.cell
def _(db_path, duckdb, get_refresh, pd):
    # Depend on get_refresh so this cell re-runs after every write
    get_refresh()

    with duckdb.connect(str(db_path), read_only=True) as _con:
        people_df = _con.execute("""
            SELECT name, affiliation, category, topics, platform, url,
                   description, relevance_tags,
                   CAST(paywalled AS BOOLEAN) AS paywalled, added
            FROM energy_data.people_to_follow
            ORDER BY category, name
        """).df()

        custom_df = _con.execute("""
            SELECT title AS name, author AS affiliation,
                   'custom' AS category, '' AS topics,
                   source_type AS platform, url, description,
                   relevance_tags, FALSE AS paywalled,
                   CAST(added_at AS VARCHAR) AS added
            FROM energy_data.reading_custom_sources
            ORDER BY added_at DESC
        """).df()

        notes_df = _con.execute("""
            SELECT note_id, source_type, source_key,
                   note_text, tags, created_at, updated_at
            FROM energy_data.reading_notes
            ORDER BY created_at DESC
        """).df()

    return custom_df, notes_df, people_df


@app.cell
def _(custom_df, people_df, pd):
    all_sources_df = (
        pd.concat([people_df, custom_df], ignore_index=True)
        if not custom_df.empty
        else people_df.copy()
    )
    return (all_sources_df,)


# ── Browse ────────────────────────────────────────────────────────────────────


@app.cell
def _(mo, people_df):
    _tags = sorted(set(
        t.strip()
        for row in people_df["relevance_tags"].dropna()
        for t in str(row).split("|")
        if t.strip()
    ))

    browse_search = mo.ui.text(placeholder="Search name or description...", label="Search")
    browse_tag = mo.ui.dropdown(options=["All"] + _tags, value="All", label="Tag")
    browse_category = mo.ui.dropdown(
        options=["All"] + sorted(people_df["category"].dropna().unique().tolist()),
        value="All",
        label="Category",
    )
    browse_access = mo.ui.dropdown(
        options=["All", "Free only", "Paywalled"],
        value="All",
        label="Access",
    )

    mo.vstack([
        mo.md("## Browse"),
        mo.hstack([browse_search, browse_tag, browse_category, browse_access], wrap=True),
    ])
    return browse_access, browse_category, browse_search, browse_tag


@app.cell
def _(browse_access, browse_category, browse_search, browse_tag, people_df):
    _f = people_df.copy()

    if browse_search.value:
        _q = browse_search.value.lower()
        _f = _f[
            _f["name"].str.lower().str.contains(_q, na=False)
            | _f["description"].str.lower().str.contains(_q, na=False)
            | _f["affiliation"].str.lower().str.contains(_q, na=False)
        ]
    if browse_tag.value != "All":
        _f = _f[_f["relevance_tags"].str.contains(browse_tag.value, na=False)]
    if browse_category.value != "All":
        _f = _f[_f["category"] == browse_category.value]
    if browse_access.value == "Free only":
        _f = _f[_f["paywalled"] == False]  # noqa: E712
    elif browse_access.value == "Paywalled":
        _f = _f[_f["paywalled"] == True]  # noqa: E712

    browse_filtered = _f.reset_index(drop=True)
    return (browse_filtered,)


@app.cell
def _(browse_filtered, mo, pd):
    _display = browse_filtered[["name", "affiliation", "platform", "relevance_tags", "paywalled", "url"]].copy()
    _display["link"] = _display["url"].apply(
        lambda u: mo.Html(f'<a href="{u}" target="_blank">↗</a>') if pd.notna(u) and u else ""
    )
    browse_table = mo.ui.table(
        _display[["name", "affiliation", "platform", "relevance_tags", "paywalled", "link"]],
        selection="single",
        label="Select a source to view details.",
    )
    browse_table
    return (browse_table,)


@app.cell
def _(browse_filtered, browse_table, mo):
    _sel = browse_table.value
    _result = mo.md("*Select a row above to see details.*")
    if not _sel.empty:
        _name = _sel.iloc[0]["name"]
        _rows = browse_filtered[browse_filtered["name"] == _name]
        if not _rows.empty:
            _r = _rows.iloc[0]
            _paywall = " · **\\$**" if _r["paywalled"] else ""
            _result = mo.vstack([
                mo.md(f"#### {_r['name']}{_paywall}"),
                mo.md(f"*{_r['affiliation']}* · {_r['platform']}"),
                mo.md(_r["description"]),
                mo.md(f"**Tags:** `{_r['relevance_tags']}`  ·  [Open →]({_r['url']})"),
            ], gap="0.5rem")
    _result


# ── Capture Notes ─────────────────────────────────────────────────────────────


@app.cell
def _(all_sources_df, mo):
    capture_source = mo.ui.dropdown(
        options=all_sources_df["name"].tolist(),
        label="Source",
    )
    capture_note = mo.ui.text_area(
        placeholder="Key points, quotes, connections to the research...",
        label="Notes",
        full_width=True,
        rows=8,
    )
    capture_tags = mo.ui.text(
        placeholder="DD-001, capital-flows",
        label="Tags (optional)",
    )
    capture_save = mo.ui.run_button(label="Save Note")

    mo.vstack([
        mo.md("## Capture Notes"),
        capture_source,
        capture_note,
        mo.hstack([capture_tags, capture_save], align="end"),
    ])
    return capture_note, capture_save, capture_source, capture_tags


@app.cell
def _(
    db_path,
    capture_note,
    capture_save,
    capture_source,
    capture_tags,
    datetime,
    duckdb,
    mo,
    set_refresh,
    uuid,
):
    mo.stop(not capture_save.value, mo.md(""))
    mo.stop(
        not capture_source.value or not capture_note.value.strip(),
        mo.callout(mo.md("Select a source and enter a note before saving."), kind="warn"),
    )

    with duckdb.connect(str(db_path)) as _con:
        _con.execute(
            "INSERT INTO energy_data.reading_notes "
            "(note_id, source_type, source_key, note_text, tags, created_at, updated_at) "
            "VALUES (?, 'person', ?, ?, ?, ?, ?)",
            [
                str(uuid.uuid4()),
                capture_source.value,
                capture_note.value.strip(),
                capture_tags.value.strip(),
                datetime.now(),
                datetime.now(),
            ],
        )

    set_refresh(lambda x: x + 1)
    mo.callout(mo.md(f"Note saved for **{capture_source.value}**."), kind="success")


@app.cell
def _(capture_source, mo, notes_df):
    _result = mo.md("")
    if capture_source.value:
        _src_notes = notes_df[notes_df["source_key"] == capture_source.value]
        if not _src_notes.empty:
            _items = []
            for _, _r in _src_notes.iterrows():
                _ts = str(_r["created_at"])[:16] if _r["created_at"] is not None else ""
                _tag_str = f"  `{_r['tags']}`" if _r.get("tags") else ""
                _items.append(mo.vstack([
                    mo.md(f"*{_ts}*{_tag_str}"),
                    mo.md(_r["note_text"]),
                    mo.md("---"),
                ], gap="0.25rem"))
            _result = mo.vstack(_items)
        else:
            _result = mo.md("*No notes yet for this source.*")
    _result


# ── Add Source ────────────────────────────────────────────────────────────────


@app.cell
def _(mo):
    add_title = mo.ui.text(placeholder="Title or source name", label="Title *", full_width=True)
    add_author = mo.ui.text(placeholder="Author or publisher", label="Author / Publisher")
    add_url = mo.ui.text(placeholder="https://...", label="URL *", full_width=True)
    add_type = mo.ui.dropdown(
        options=["article", "paper", "book", "podcast", "video", "thread", "report", "other"],
        value="article",
        label="Type",
    )
    add_tags = mo.ui.text(placeholder="DD-001|DD-002", label="Relevance tags")
    add_description = mo.ui.text_area(
        placeholder="What is this? Why is it relevant to the research?",
        label="Description",
        full_width=True,
        rows=3,
    )
    add_save = mo.ui.run_button(label="Add Source")

    mo.vstack([
        mo.md("## Add Source"),
        add_title,
        mo.hstack([add_author, add_type, add_tags], wrap=True),
        add_url,
        add_description,
        add_save,
    ])
    return add_author, add_description, add_save, add_tags, add_title, add_type, add_url


@app.cell
def _(
    db_path,
    add_author,
    add_description,
    add_save,
    add_tags,
    add_title,
    add_type,
    add_url,
    datetime,
    duckdb,
    mo,
    set_refresh,
    uuid,
):
    mo.stop(not add_save.value, mo.md(""))
    mo.stop(
        not add_title.value.strip() or not add_url.value.strip(),
        mo.callout(mo.md("Title and URL are required."), kind="warn"),
    )

    with duckdb.connect(str(db_path)) as _con:
        _con.execute(
            "INSERT INTO energy_data.reading_custom_sources "
            "(source_id, title, author, url, source_type, relevance_tags, description, added_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(uuid.uuid4()),
                add_title.value.strip(),
                add_author.value.strip(),
                add_url.value.strip(),
                add_type.value,
                add_tags.value.strip(),
                add_description.value.strip(),
                datetime.now(),
            ],
        )

    set_refresh(lambda x: x + 1)
    mo.callout(mo.md(f"Source added: **{add_title.value}**"), kind="success")


# ── All Notes ─────────────────────────────────────────────────────────────────


@app.cell
def _(mo):
    notes_search = mo.ui.text(
        placeholder="Search by source, text, or tag...",
        label="Search notes",
        full_width=True,
    )
    mo.vstack([mo.md("## All Notes"), notes_search])
    return (notes_search,)


@app.cell
def _(mo, notes_df, notes_search):
    _f = notes_df.copy()

    if notes_search.value:
        _q = notes_search.value.lower()
        _f = _f[
            _f["note_text"].str.lower().str.contains(_q, na=False)
            | _f["source_key"].str.lower().str.contains(_q, na=False)
            | _f["tags"].str.lower().str.contains(_q, na=False)
        ]

    if _f.empty:
        _result = mo.md("*No notes captured yet.*")
    else:
        _items = []
        for _, _r in _f.iterrows():
            _ts = str(_r["created_at"])[:10] if _r["created_at"] is not None else ""
            _tag_str = f"  `{_r['tags']}`" if _r.get("tags") else ""
            _items.append(mo.vstack([
                mo.md(f"**{_r['source_key']}** · {_ts}{_tag_str}"),
                mo.md(_r["note_text"]),
                mo.md("---"),
            ], gap="0.25rem"))
        _result = mo.vstack(_items)
    _result


if __name__ == "__main__":
    app.run()
