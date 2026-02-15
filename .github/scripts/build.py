#!/usr/bin/env python3
"""Build marimo notebooks for GitHub Pages deployment.

Exports registered notebooks to static HTML and generates an index page
with navigation between case studies.

Usage:
    uv run python .github/scripts/build.py
"""

from __future__ import annotations

import subprocess
import sys
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SITE_DIR = PROJECT_ROOT / "_site"

# ---------------------------------------------------------------------------
# Notebook registry — add new case studies here
# ---------------------------------------------------------------------------

CASE_STUDIES = [
    {
        "id": "dd001",
        "title": "CS-1: Transformer Manufacturing",
        "subtitle": "Learning curves, supply chain dynamics, and trade policy",
        "color": "#1f77b4",
        "notebooks": [
            {
                "file": "notebooks/dd001_learning_curves/01_investigation.py",
                "title": "Part 1 \u2014 Investigation",
                "desc": (
                    "How AI demand creates conditions for a transformer "
                    "manufacturing learning curve."
                ),
            },
            {
                "file": "notebooks/dd001_learning_curves/02_feedback_architecture.py",
                "title": "Part 2 \u2014 Feedback Architecture",
                "desc": (
                    "Systems dynamics model of the transformer market "
                    "feedback loops and policy leverage points."
                ),
            },
        ],
    },
    {
        "id": "dd002",
        "title": "CS-2/3: AI Capital and Grid Modernization",
        "subtitle": "Power generation, interconnection queues, and cost allocation",
        "color": "#2ca02c",
        "notebooks": [
            {
                "file": "notebooks/dd002_grid_modernization/01_whats_getting_built.py",
                "title": "Part 1 \u2014 What\u2019s Getting Built",
                "desc": (
                    "The generation mix being built to serve AI demand: "
                    "solar, gas, and the IRA effect."
                ),
            },
            {
                "file": "notebooks/dd002_grid_modernization/02_who_benefits.py",
                "title": "Part 2 \u2014 Who Benefits?",
                "desc": (
                    "Interconnection queues, cost allocation, and "
                    "$4.36B socialized to ratepayers."
                ),
            },
            {
                "file": "notebooks/dd002_grid_modernization/03_feedback_architecture.py",
                "title": "Part 3 \u2014 Feedback Architecture",
                "desc": (
                    "Five feedback loops that determine whether AI capital "
                    "modernizes the grid or bypasses it."
                ),
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Data pipeline
# ---------------------------------------------------------------------------


def ensure_data() -> bool:
    """Populate the research database if it doesn't exist."""
    db_path = PROJECT_ROOT / "data" / "research.duckdb"
    if db_path.exists():
        print(f"  Database exists at {db_path.relative_to(PROJECT_ROOT)}")
        return True

    print("  Database not found. Running data pipelines...")
    result = subprocess.run(
        [sys.executable, "-m", "src.data.pipelines"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        print(f"  Pipeline error:\n{result.stderr[:2000]}")
        return False

    print("  Pipelines complete.")
    return True


# ---------------------------------------------------------------------------
# Notebook export
# ---------------------------------------------------------------------------


def export_notebook(nb_file: str, output_path: Path) -> bool:
    """Export a single marimo notebook to static HTML."""
    full_path = PROJECT_ROOT / nb_file
    if not full_path.exists():
        print(f"  SKIP  {nb_file} (file not found)")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, "-m", "marimo", "export", "html",
         str(full_path), "-o", str(output_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"  FAIL  {nb_file}")
        if result.stderr:
            # Show last few lines of error
            lines = result.stderr.strip().split("\n")
            for line in lines[-5:]:
                print(f"         {line}")
        return False

    size_kb = output_path.stat().st_size / 1024
    print(f"  OK    {nb_file} ({size_kb:.0f} KB)")
    return True


# ---------------------------------------------------------------------------
# Index page generation
# ---------------------------------------------------------------------------

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Where AI Capital Lands</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Oxygen, Ubuntu, sans-serif;
            background: #fafafa;
            color: #1a1a2e;
            line-height: 1.6;
        }}
        header {{
            background: #1a1a2e;
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        header h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font-size: 1.05rem;
            opacity: 0.85;
            max-width: 680px;
            margin: 0 auto 0.5rem;
        }}
        .author {{
            font-size: 0.9rem;
            opacity: 0.6;
            margin-top: 0.5rem;
        }}
        main {{
            max-width: 860px;
            margin: 2.5rem auto;
            padding: 0 1.5rem;
        }}
        .intro {{
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 2rem;
            line-height: 1.7;
        }}
        .case-study {{
            margin-bottom: 2.5rem;
        }}
        .case-study h2 {{
            font-size: 1.3rem;
            padding-left: 0.75rem;
            margin-bottom: 0.2rem;
        }}
        .cs-subtitle {{
            color: #777;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            padding-left: 0.85rem;
        }}
        .notebook-card {{
            background: white;
            border: 1px solid #e4e4e4;
            border-radius: 6px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .notebook-card:hover {{
            border-color: #aaa;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }}
        .nb-number {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 1.6rem;
            height: 1.6rem;
            min-width: 1.6rem;
            border-radius: 50%;
            font-size: 0.8rem;
            font-weight: 700;
            color: white;
            margin-top: 0.1rem;
        }}
        .nb-content {{
            flex: 1;
        }}
        .nb-title {{
            font-weight: 600;
            font-size: 1rem;
            color: #1a1a2e;
            text-decoration: none;
        }}
        .nb-title:hover {{
            text-decoration: underline;
        }}
        .nb-desc {{
            color: #666;
            font-size: 0.88rem;
            margin-top: 0.2rem;
        }}
        .nb-unavailable {{
            opacity: 0.45;
        }}
        .nb-unavailable .nb-title {{
            color: #999;
            pointer-events: none;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #aaa;
            font-size: 0.82rem;
            border-top: 1px solid #eee;
            margin-top: 2rem;
        }}
        footer a {{ color: #888; }}
        @media (max-width: 600px) {{
            header {{ padding: 2rem 1.25rem; }}
            header h1 {{ font-size: 1.7rem; }}
            main {{ padding: 0 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Where AI Capital Lands</h1>
        <p class="subtitle">
            How $200B+/year in AI capital expenditure converts into physical
            infrastructure and creates durable path dependencies in supply
            chains, grid topology, and energy markets.
        </p>
        <p class="author">Thandolwethu Zwelakhe Dlamini</p>
    </header>
    <main>
        <p class="intro">
            Each case study traces a specific channel through which AI capital
            reaches the physical economy. The analysis combines empirical data,
            systems dynamics modeling, and regulatory analysis. Notebooks are
            static exports of interactive
            <a href="https://marimo.io" style="color:#555">marimo</a>
            notebooks &mdash; all code, data sources, and methodology are visible.
        </p>
        {sections}
    </main>
    <footer>
        Built with <a href="https://marimo.io">marimo</a> &middot;
        <a href="https://github.com/Shakes-tzd/Systems">Source on GitHub</a>
    </footer>
</body>
</html>
"""


def generate_index(exported: dict[str, bool]) -> str:
    """Generate the index.html content.

    Parameters
    ----------
    exported : dict
        Mapping of notebook file path -> True if exported successfully.
    """
    sections = []

    for cs in CASE_STUDIES:
        cards = []
        for i, nb in enumerate(cs["notebooks"]):
            stem = Path(nb["file"]).stem
            slug = f"{cs['id']}/{stem}.html"
            ok = exported.get(nb["file"], False)
            unavail = "" if ok else " nb-unavailable"
            href = slug if ok else "#"

            cards.append(
                f'        <div class="notebook-card{unavail}">\n'
                f'            <div class="nb-number" style="background:{cs["color"]}">'
                f'{i + 1}</div>\n'
                f'            <div class="nb-content">\n'
                f'                <a href="{href}" class="nb-title">'
                f'{escape(nb["title"])}</a>\n'
                f'                <div class="nb-desc">{escape(nb["desc"])}</div>\n'
                f'            </div>\n'
                f'        </div>'
            )

        section = (
            f'    <section class="case-study">\n'
            f'        <h2 style="border-left:4px solid {cs["color"]}">'
            f'{escape(cs["title"])}</h2>\n'
            f'        <p class="cs-subtitle">{escape(cs["subtitle"])}</p>\n'
            + "\n".join(cards)
            + "\n    </section>"
        )
        sections.append(section)

    return INDEX_TEMPLATE.format(sections="\n".join(sections))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 60)
    print("Building GitHub Pages site")
    print("=" * 60)

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / ".nojekyll").touch()

    # Step 1: Data
    print("\n[1/3] Checking data...")
    ensure_data()

    # Step 2: Export notebooks
    print("\n[2/3] Exporting notebooks...")
    exported: dict[str, bool] = {}
    total, ok = 0, 0

    for cs in CASE_STUDIES:
        for nb in cs["notebooks"]:
            total += 1
            output = SITE_DIR / cs["id"] / (Path(nb["file"]).stem + ".html")
            success = export_notebook(nb["file"], output)
            exported[nb["file"]] = success
            if success:
                ok += 1

    # Step 3: Index
    print("\n[3/3] Generating index page...")
    index_html = generate_index(exported)
    (SITE_DIR / "index.html").write_text(index_html)
    print(f"  OK    index.html")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Done: {ok}/{total} notebooks exported")
    if ok < total:
        print(f"  {total - ok} notebook(s) failed — marked unavailable in index")
    print(f"Output: {SITE_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"{'=' * 60}")

    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
