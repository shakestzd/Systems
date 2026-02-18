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
        "title": "DD-001: AI Valuations vs Physical Infrastructure Reality",
        "subtitle": "Capex cycles, market cap misalignment, and what the physical economy actually built",
        "color": "#1f77b4",
        "notebooks": [
            {
                "file": "notebooks/dd001_capital_reality/01_capex_vs_reality.py",
                "title": "Part 1 \u2014 Capex vs Reality",
                "desc": (
                    "Comparing AI company capex and market cap trajectories "
                    "against what the physical supply chain can actually deliver."
                ),
            },
        ],
    },
    {
        "id": "dd002",
        "title": "DD-002: AI Capital and Grid Modernization",
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
    {
        "id": "dd003",
        "title": "DD-003: AI Capital Flows and Labor Markets",
        "subtitle": "Who gets hired, who gets displaced, and where the skills gap lands",
        "color": "#ff7f0e",
        "notebooks": [
            {
                "file": "notebooks/dd003_labor_markets/01_who_gets_hired.py",
                "title": "Part 1 \u2014 Who Gets Hired?",
                "desc": (
                    "Mapping AI-driven labor demand: where the jobs are, "
                    "what they require, and who\u2019s excluded."
                ),
            },
        ],
    },
    {
        "id": "dd004",
        "title": "DD-004: AI Capital and Who Pays for the Grid",
        "subtitle": "Utility regulation, cost socialization, and ratepayer impact",
        "color": "#9467bd",
        "notebooks": [
            {
                "file": "notebooks/dd004_utility_regulation/01_pe_utility_acquisitions.py",
                "title": "Part 1 \u2014 PE Utility Acquisitions",
                "desc": (
                    "Private equity\u2019s move into utility ownership and "
                    "what it means for rate structures."
                ),
            },
            {
                "file": "notebooks/dd004_utility_regulation/02_data_center_community_impact.py",
                "title": "Part 2 \u2014 Data Center Community Impact",
                "desc": (
                    "How large load additions reshape costs and services "
                    "for existing ratepayers."
                ),
            },
            {
                "file": "notebooks/dd004_utility_regulation/03_cost_liability_map.py",
                "title": "Part 3 \u2014 Cost Liability Map",
                "desc": (
                    "Who ultimately pays for grid upgrades triggered "
                    "by hyperscaler demand."
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
    """Export a single marimo notebook to static HTML (code hidden).

    Returns True if the HTML file was produced, even if some cells had
    runtime errors (marimo exits 1 with "cells failed to execute" message
    but still writes a valid HTML file in that case).
    """
    full_path = PROJECT_ROOT / nb_file
    if not full_path.exists():
        print(f"  SKIP  {nb_file} (file not found)")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, "-m", "marimo", "export", "html",
         "--no-include-code",
         str(full_path), "-o", str(output_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        if result.returncode != 0:
            # Marimo exits 1 when some cells fail but still writes the HTML.
            # Deploy it anyway — failed cells render as error panels, which is
            # better than a grayed-out "unavailable" card on the index.
            print(f"  WARN  {nb_file} ({size_kb:.0f} KB, some cells had errors)")
        else:
            print(f"  OK    {nb_file} ({size_kb:.0f} KB)")
        return True

    # HTML was not written at all — real failure.
    print(f"  FAIL  {nb_file}")
    if result.stderr:
        lines = result.stderr.strip().split("\n")
        for line in lines[-8:]:
            print(f"         {line}")
    return False


# ---------------------------------------------------------------------------
# Shared HTML fragments
# ---------------------------------------------------------------------------

_NAV = """\
    <nav>
        <a href="index.html">Research</a>
        <a href="about.html">About</a>
        <a href="https://github.com/Shakes-tzd/Systems">GitHub</a>
    </nav>"""

_SHARED_CSS = """\
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Oxygen, Ubuntu, sans-serif;
            background: #fafafa;
            color: #1a1a2e;
            line-height: 1.6;
        }
        header {
            background: #1a1a2e;
            color: white;
            padding: 3rem 2rem 2rem;
            text-align: center;
        }
        header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            letter-spacing: -0.5px;
        }
        .subtitle {
            font-size: 1.05rem;
            opacity: 0.85;
            max-width: 680px;
            margin: 0 auto 0.5rem;
        }
        nav {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            padding: 1rem 0 0;
            border-top: 1px solid rgba(255,255,255,0.15);
            margin-top: 1.5rem;
        }
        nav a {
            color: rgba(255,255,255,0.75);
            text-decoration: none;
            font-size: 0.9rem;
            letter-spacing: 0.02em;
        }
        nav a:hover { color: white; }
        main {
            max-width: 860px;
            margin: 2.5rem auto;
            padding: 0 1.5rem;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: #aaa;
            font-size: 0.82rem;
            border-top: 1px solid #eee;
            margin-top: 2rem;
        }
        footer a { color: #888; }
        @media (max-width: 600px) {
            header { padding: 2rem 1.25rem 1.5rem; }
            header h1 { font-size: 1.7rem; }
            main { padding: 0 1rem; }
        }"""

_FOOTER = """\
    <footer>
        Built with <a href="https://marimo.io">marimo</a> &middot;
        <a href="https://github.com/Shakes-tzd/Systems">Source on GitHub</a>
    </footer>"""


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
{shared_css}
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
        .nb-content {{ flex: 1; }}
        .nb-title {{
            font-weight: 600;
            font-size: 1rem;
            color: #1a1a2e;
            text-decoration: none;
        }}
        .nb-title:hover {{ text-decoration: underline; }}
        .nb-desc {{
            color: #666;
            font-size: 0.88rem;
            margin-top: 0.2rem;
        }}
        .nb-unavailable {{ opacity: 0.45; }}
        .nb-unavailable .nb-title {{
            color: #999;
            pointer-events: none;
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
{nav}
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
        {{sections}}
    </main>
{footer}
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
    template = INDEX_TEMPLATE.format(
        shared_css=_SHARED_CSS,
        nav=_NAV,
        footer=_FOOTER,
    )

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

    # Use replace instead of format to avoid conflicts with CSS curly braces
    # that were injected in the first format pass.
    return template.replace("{sections}", "\n".join(sections))


# ---------------------------------------------------------------------------
# About page generation
# ---------------------------------------------------------------------------

ABOUT_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About &mdash; Where AI Capital Lands</title>
    <style>
{shared_css}
        .about-content {{
            max-width: 680px;
        }}
        .about-content h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            margin: 2rem 0 0.75rem;
            color: #1a1a2e;
        }}
        .about-content h2:first-child {{
            margin-top: 0;
        }}
        .about-content p {{
            color: #444;
            font-size: 0.97rem;
            line-height: 1.75;
            margin-bottom: 1rem;
        }}
        .about-content ul {{
            margin: 0.5rem 0 1rem 1.25rem;
            color: #444;
            font-size: 0.97rem;
            line-height: 1.75;
        }}
        .about-content ul li {{
            margin-bottom: 0.3rem;
        }}
        .timeline {{
            border-left: 2px solid #e4e4e4;
            margin: 1rem 0 1.5rem 0.5rem;
            padding-left: 1.25rem;
        }}
        .timeline-item {{
            margin-bottom: 1rem;
            position: relative;
        }}
        .timeline-item::before {{
            content: "";
            width: 8px;
            height: 8px;
            background: #1a1a2e;
            border-radius: 50%;
            position: absolute;
            left: -1.6rem;
            top: 0.45rem;
        }}
        .timeline-year {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #999;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .timeline-desc {{
            font-size: 0.95rem;
            color: #333;
            line-height: 1.5;
        }}
        .links {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }}
        .link-pill {{
            display: inline-block;
            background: #1a1a2e;
            color: white;
            text-decoration: none;
            padding: 0.4rem 0.9rem;
            border-radius: 4px;
            font-size: 0.88rem;
            transition: opacity 0.15s;
        }}
        .link-pill:hover {{ opacity: 0.8; }}
        .name-pronunciation {{
            font-size: 0.85rem;
            color: #888;
            margin-top: 0.1rem;
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
{nav}
    </header>
    <main>
        <div class="about-content">

            <h2>Thandolwethu Zwelakhe Dlamini</h2>
            <p class="name-pronunciation">Goes by Shakes &mdash; from Eswatini (formerly Swaziland), Southern Africa</p>

            <p>
                I am a systems engineer and policy analyst. My background spans
                mechanical engineering, technology policy, and energy infrastructure
                &mdash; specifically how capital decisions at the top of the stack
                propagate into physical systems at the bottom.
            </p>

            <p>
                This project is the practical application of that lens: tracing
                $200B+/year in AI capital expenditure from financial commitment
                to physical asset, and analyzing what gets locked in, what depends
                on regulatory regimes, and where feedback loops amplify or distort
                outcomes.
            </p>

            <h2>Background</h2>

            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-year">2015 &ndash; 2020</div>
                    <div class="timeline-desc">
                        <strong>Duke University</strong> &mdash; B.S. Mechanical Engineering,
                        Minor in German. Study abroad in Berlin; took three engineering
                        courses in German after 18 months of study.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2017 &ndash; 2018</div>
                    <div class="timeline-desc">
                        <strong>Eswatini Electricity Company / One Power (Lesotho)</strong>
                        &mdash; Worked on microgrid projects in rural Southern Africa,
                        including Eswatini&rsquo;s first microgrid, electrifying a
                        remote village unreachable by conventional grid infrastructure.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2019</div>
                    <div class="timeline-desc">
                        <strong>COP25, Madrid</strong> &mdash; Represented Eswatini
                        as part of the national delegation at the UN Climate Conference.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2020 &ndash; 2022</div>
                    <div class="timeline-desc">
                        <strong>MIT</strong> &mdash; S.M. Technology &amp; Policy
                        (Systems Engineering focus). Research on energy systems,
                        infrastructure investment, and policy interaction.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2022 &ndash; 2025</div>
                    <div class="timeline-desc">
                        <strong>SunStrong Management LLC</strong> (formerly Sunnova Energy)
                        &mdash; Senior Data Analyst. Managed data infrastructure and
                        Energy Community ITC analysis for a portfolio of 200,000+
                        solar installations across the U.S.
                    </div>
                </div>
            </div>

            <h2>Why This Project</h2>

            <p>
                AI capex numbers appear in quarterly earnings reports, get written
                up in press releases, and vanish into abstraction. But the capital
                doesn&rsquo;t vanish &mdash; it converts into transformers, transmission
                lines, gas turbines, semiconductor fabs, and data center concrete.
                That infrastructure is durable. It reshapes supply chains, labor
                markets, grid topology, and trade patterns for decades.
            </p>

            <p>
                The analysis tries to answer a specific question: <em>Where does
                AI capex land in the physical economy, what does it lock in, and
                how do current regulatory decisions amplify or distort those
                outcomes?</em>
            </p>

            <p>
                Each case study traces one supply chain node &mdash; grid equipment,
                generation mix, labor markets, utility regulation &mdash; and
                applies the same framework: capital flow mapping, durability
                taxonomy, and systems dynamics modeling to identify feedback
                architecture and policy leverage points.
            </p>

            <h2>Methods</h2>

            <p>
                All analysis is done in
                <a href="https://marimo.io" style="color:#1a1a2e">marimo</a>
                &mdash; reactive Python notebooks that are valid .py files and
                diff cleanly in git. Data sources are government databases,
                regulatory filings, and company disclosures. The code,
                data pipelines, and methodology are fully visible in the
                source repository.
            </p>

            <ul>
                <li>Data pipelines: DuckDB + dlt</li>
                <li>Systems dynamics: PySD</li>
                <li>Visualization: matplotlib (Storytelling with Data principles)</li>
                <li>Statistics: PyMC, statsmodels</li>
            </ul>

            <h2>Contact</h2>

            <div class="links">
                <a href="https://github.com/Shakes-tzd/Systems" class="link-pill">
                    Source Code
                </a>
                <a href="https://github.com/Shakes-tzd" class="link-pill">
                    GitHub Profile
                </a>
            </div>

        </div>
    </main>
{footer}
</body>
</html>
"""


def generate_about() -> str:
    """Generate the about.html content."""
    return ABOUT_TEMPLATE.format(
        shared_css=_SHARED_CSS,
        nav=_NAV,
        footer=_FOOTER,
    )


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
    print("\n[1/4] Checking data...")
    ensure_data()

    # Step 2: Export notebooks
    print("\n[2/4] Exporting notebooks...")
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
    print("\n[3/4] Generating index page...")
    index_html = generate_index(exported)
    (SITE_DIR / "index.html").write_text(index_html)
    print(f"  OK    index.html")

    # Step 4: About
    print("\n[4/4] Generating about page...")
    about_html = generate_about()
    (SITE_DIR / "about.html").write_text(about_html)
    print(f"  OK    about.html")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Done: {ok}/{total} notebooks exported")
    if ok < total:
        print(f"  {total - ok} notebook(s) skipped \u2014 marked unavailable in index")
    print(f"Output: {SITE_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"{'=' * 60}")

    # Always exit 0 — partial exports are valid; failed notebooks appear grayed out
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
