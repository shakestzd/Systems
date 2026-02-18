#!/usr/bin/env python3
"""Build marimo notebooks for GitHub Pages deployment.

Exports registered notebooks to static HTML and generates an index page
with navigation between case studies.

Usage:
    uv run python .github/scripts/build.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SITE_DIR = PROJECT_ROOT / "_site"

# ---------------------------------------------------------------------------
# Site identity — single source of truth for title, subtitle, and URLs
# ---------------------------------------------------------------------------

SITE = {
    "title": "The Physical Economy of AI",
    "subtitle_html": (
        "An independent investigation into the short, medium, and long-term "
        "impacts of accelerated AI capital investment on physical infrastructure "
        "&mdash; from grid topology and supply chains to labor markets and "
        "regulatory regimes."
    ),
    "github_url": "https://github.com/Shakes-tzd/Systems",
}

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
                "file": "notebooks/dd001_capital_reality/01_markets_and_money.py",
                "title": "Part 1 \u2014 Markets and Money",
                "desc": (
                    "Is the capital commitment justified by revenue? "
                    "Market cap gains against disclosed capex and cloud revenue trajectories."
                ),
            },
            {
                "file": "notebooks/dd001_capital_reality/02_conversion_reality.py",
                "title": "Part 2 \u2014 Conversion Reality",
                "desc": (
                    "From announcement to infrastructure: interconnection queues, "
                    "the physical sequence, and the asset-life distribution."
                ),
            },
            {
                "file": "notebooks/dd001_capital_reality/03_risk_and_durability.py",
                "title": "Part 3 \u2014 Risk and Durability",
                "desc": (
                    "Who holds the downside when long-lived infrastructure "
                    "outlasts the demand thesis that justified it."
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


_NOTEBOOK_NAV = (
    # Adaptive nav that follows system dark/light preference.
    # No forced background override — marimo's own theming handles content area.
    '<style>'
    '.snb{background:#f5f1eb;padding:0.85rem 2.5rem;display:flex;align-items:center;'
    "gap:2rem;border-bottom:1px solid #d6cfc7;font-family:'DM Mono',monospace;"
    'position:sticky;top:0;z-index:9999}'
    '.snb a{color:#9a9490;text-decoration:none;font-size:0.67rem;'
    'letter-spacing:0.12em;text-transform:uppercase;transition:color .14s}'
    '.snb a:hover{color:#1a1917}'
    '@media(prefers-color-scheme:dark){'
    '.snb{background:#14120f;border-bottom-color:#2e2b27}'
    '.snb a{color:#5a5650}'
    '.snb a:hover{color:#e5e0d8}'
    '}'
    '</style>\n'
    '<div class="snb">'
    '<a href="../index.html">&#8592; Research</a>'
    '<a href="../about.html">About</a>'
    f'<a href="{SITE["github_url"]}">GitHub</a>'
    '</div>'
)


def inject_site_nav(html_path: Path) -> None:
    """Inject a sticky nav bar into a marimo-exported notebook HTML file.

    Inserts the nav immediately after <body> so readers can return to the
    index from any notebook page.
    """
    html = html_path.read_text(encoding="utf-8")
    marker = "<body>"
    idx = html.find(marker)
    if idx == -1:
        return  # unexpected structure — leave untouched
    insert_at = idx + len(marker)
    html = html[:insert_at] + "\n" + _NOTEBOOK_NAV + "\n" + html[insert_at:]
    html_path.write_text(html, encoding="utf-8")


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

    # Remove any stale output so existence-check after the run is unambiguous.
    output_path.unlink(missing_ok=True)

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
        inject_site_nav(output_path)
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


# ---------------------------------------------------------------------------
# Index page generation
# ---------------------------------------------------------------------------
#
# Uses sentinel replacement (__KEY__) instead of str.format() so that CSS
# curly braces need no escaping. _SHARED_CSS / _NAV / _FOOTER are only used
# by the About page; the index carries its own self-contained styles.
# ---------------------------------------------------------------------------

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__SITE_TITLE__</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Mono:wght@400;500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
    <script>
        /* Anti-FOUT: apply stored theme before first paint */
        (function(){var t=localStorage.getItem('color-theme');if(t)document.documentElement.dataset.colorTheme=t;})();
    </script>
    <style>
        :root {
            --paper: #f5f1eb;
            --ink: #1a1917;
            --ink-mid: #4d4a46;
            --ink-light: #9a9490;
            --rule: #d6cfc7;
            --accent: #b84c2a;
        }
        /* Dark mode — system preference (no manual override) */
        @media (prefers-color-scheme: dark) {
            :root:not([data-color-theme]) {
                --paper: #14120f;
                --ink: #e5e0d8;
                --ink-mid: #ada89f;
                --ink-light: #5a5650;
                --rule: #2e2b27;
                --accent: #d4634a;
            }
        }
        /* Manual overrides via toggle */
        :root[data-color-theme="dark"] {
            --paper: #14120f;
            --ink: #e5e0d8;
            --ink-mid: #ada89f;
            --ink-light: #5a5650;
            --rule: #2e2b27;
            --accent: #d4634a;
        }
        :root[data-color-theme="light"] {
            --paper: #f5f1eb;
            --ink: #1a1917;
            --ink-mid: #4d4a46;
            --ink-light: #9a9490;
            --rule: #d6cfc7;
            --accent: #b84c2a;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            background: var(--paper);
            color: var(--ink);
            font-family: 'DM Sans', sans-serif;
            font-weight: 300;
            line-height: 1.6;
            min-height: 100vh;
        }
        /* paper grain overlay */
        body::after {
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 999;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
        }
        /* nav */
        .site-nav {
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 1.2rem 2.5rem;
            border-bottom: 1px solid var(--rule);
            position: sticky;
            top: 0;
            background: var(--paper);
            z-index: 50;
        }
        .site-nav a {
            font-family: 'DM Mono', monospace;
            font-size: 0.67rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--ink-light);
            text-decoration: none;
            transition: color 0.14s;
        }
        .site-nav a.active { color: var(--ink); }
        .site-nav a:hover { color: var(--ink); }
        .nav-spacer { flex: 1; }
        .theme-toggle {
            background: none;
            border: none;
            cursor: pointer;
            font-family: 'DM Mono', monospace;
            font-size: 0.82rem;
            color: var(--ink-light);
            padding: 0;
            line-height: 1;
            transition: color 0.14s;
        }
        .theme-toggle:hover { color: var(--ink); }
        /* masthead */
        .masthead {
            padding: 5rem 2.5rem 3.5rem;
            border-bottom: 1px solid var(--rule);
        }
        .kicker {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-family: 'DM Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--ink-light);
            margin-bottom: 1.75rem;
        }
        .kicker::before {
            content: '';
            display: inline-block;
            width: 1.75rem;
            height: 1px;
            background: var(--accent);
        }
        .site-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(2.75rem, 5.5vw, 4.75rem);
            font-weight: 300;
            line-height: 1.06;
            letter-spacing: -0.025em;
            color: var(--ink);
            margin-bottom: 1.5rem;
            animation: up 0.7s ease both;
        }
        .site-desc {
            font-size: 0.92rem;
            color: var(--ink-mid);
            max-width: 540px;
            line-height: 1.7;
            font-weight: 300;
            animation: up 0.7s 0.08s ease both;
        }
        .byline {
            margin-top: 2.25rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            animation: up 0.7s 0.15s ease both;
        }
        .byline-author {
            font-family: 'DM Mono', monospace;
            font-size: 0.67rem;
            letter-spacing: 0.07em;
            color: var(--ink-light);
        }
        .byline-dot {
            width: 2px;
            height: 2px;
            background: var(--rule);
            border-radius: 50%;
        }
        .byline-ongoing {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.07em;
            color: var(--accent);
        }
        @keyframes up {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        /* lede */
        .lede {
            padding: 2.5rem 2.5rem;
            max-width: 700px;
            border-bottom: 1px solid var(--rule);
        }
        .lede p {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.1rem;
            font-style: italic;
            font-weight: 300;
            color: var(--ink-mid);
            line-height: 1.8;
        }
        .lede a {
            color: inherit;
            text-decoration-color: var(--rule);
            transition: text-decoration-color 0.14s;
        }
        .lede a:hover { text-decoration-color: currentColor; }
        /* case study rows */
        .cs-row {
            display: grid;
            grid-template-columns: 88px 1fr;
            gap: 0 2.5rem;
            padding: 2.75rem 2.5rem;
            border-bottom: 1px solid var(--rule);
            animation: up 0.5s ease both;
        }
        .cs-meta { padding-top: 0.15rem; }
        .cs-id {
            display: block;
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            color: var(--accent);
            font-weight: 500;
            margin-bottom: 0.4rem;
        }
        .cs-status {
            font-family: 'DM Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: var(--ink-light);
        }
        .cs-heading {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.5rem;
            font-weight: 400;
            letter-spacing: -0.01em;
            line-height: 1.2;
            color: var(--ink);
            margin-bottom: 0.3rem;
        }
        .cs-tagline {
            font-size: 0.82rem;
            color: var(--ink-light);
            font-weight: 300;
            margin-bottom: 1.2rem;
        }
        /* notebook entries */
        .nb-list {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        a.nb-entry {
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            padding: 0.45rem 0.7rem;
            margin-left: -0.7rem;
            border-radius: 3px;
            text-decoration: none;
            transition: background 0.12s;
        }
        a.nb-entry:hover { background: rgba(26,25,23,0.05); }
        a.nb-entry.na { opacity: 0.35; pointer-events: none; }
        .nb-num {
            font-family: 'DM Mono', monospace;
            font-size: 0.6rem;
            color: var(--ink-light);
            margin-top: 0.18rem;
            min-width: 1.1rem;
        }
        .nb-label {
            display: block;
            font-size: 0.875rem;
            font-weight: 400;
            color: var(--ink);
            line-height: 1.3;
        }
        .nb-note {
            display: block;
            font-size: 0.775rem;
            color: var(--ink-light);
            font-weight: 300;
            margin-top: 0.1rem;
            line-height: 1.4;
        }
        /* footer */
        .site-footer {
            padding: 2.5rem 2.5rem;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        .site-footer a,
        .site-footer span {
            font-family: 'DM Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.05em;
            color: var(--ink-light);
            text-decoration: none;
        }
        .site-footer a:hover { color: var(--ink); }
        /* mobile */
        @media (max-width: 680px) {
            .site-nav { padding: 1rem 1.25rem; gap: 1.5rem; }
            .masthead { padding: 3rem 1.25rem 2.5rem; }
            .lede { padding: 2rem 1.25rem; }
            .cs-row {
                grid-template-columns: 1fr;
                gap: 0.5rem;
                padding: 2rem 1.25rem;
            }
            .cs-meta { display: flex; align-items: center; gap: 1rem; }
            .site-footer { padding: 2rem 1.25rem; }
        }
    </style>
</head>
<body>
    <nav class="site-nav">
        <a href="index.html" class="active">Research</a>
        <a href="about.html">About</a>
        <span class="nav-spacer"></span>
        <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Toggle dark/light mode">◑</button>
        <a href="__GITHUB_URL__">GitHub</a>
    </nav>
    <div class="masthead">
        <p class="kicker">Independent Research</p>
        <h1 class="site-title">__SITE_TITLE__</h1>
        <p class="site-desc">__SITE_SUBTITLE__</p>
        <div class="byline">
            <span class="byline-author">Thandolwethu Zwelakhe Dlamini</span>
            <span class="byline-dot"></span>
            <span class="byline-ongoing">Ongoing</span>
        </div>
    </div>
    <div class="lede">
        <p>AI companies are deploying over $200B/year in capital expenditure.
        I&rsquo;m trying to understand where that money actually lands:
        what it builds, what it locks in, and what the consequences are
        across different time horizons. Source on
        <a href="__GITHUB_URL__">GitHub</a>.</p>
    </div>
    __SECTIONS__
    <footer class="site-footer">
        <span>Built with <a href="https://marimo.io">marimo</a></span>
        <a href="__GITHUB_URL__">Source on GitHub</a>
    </footer>
    <script>
        (function() {
            var root = document.documentElement;
            var btn = document.getElementById('theme-toggle');
            function effective() {
                var s = localStorage.getItem('color-theme');
                return s || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            }
            function apply(theme) {
                root.dataset.colorTheme = theme;
                if (btn) btn.textContent = theme === 'dark' ? '◐' : '◑';
            }
            apply(effective());
            window.toggleTheme = function() {
                var next = effective() === 'dark' ? 'light' : 'dark';
                localStorage.setItem('color-theme', next);
                apply(next);
            };
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                if (!localStorage.getItem('color-theme')) apply(e.matches ? 'dark' : 'light');
            });
        })();
    </script>
</body>
</html>
"""


def generate_index(exported: dict[str, bool]) -> str:
    """Generate the index.html content.

    Uses sentinel replacement (__KEY__) to avoid CSS brace escaping.

    Parameters
    ----------
    exported : dict
        Mapping of notebook file path -> True if exported successfully.
    """
    rows = []

    for idx, cs in enumerate(CASE_STUDIES):
        # "dd001" → "DD–001"
        cs_id_disp = cs["id"][:2].upper() + "\u2013" + cs["id"][2:]

        # Active if any notebook exported; Draft otherwise
        active = any(exported.get(nb["file"], False) for nb in cs["notebooks"])
        status = "Active" if active else "Draft"

        # Strip "DD-00X: " prefix — the ID is already shown separately
        raw_title = cs["title"]
        clean_title = raw_title.split(": ", 1)[-1] if ": " in raw_title else raw_title

        nb_rows = []
        for i, nb in enumerate(cs["notebooks"]):
            stem = Path(nb["file"]).stem
            ok = exported.get(nb["file"], False)
            href = f"{cs['id']}/{stem}.html" if ok else "#"
            na_cls = "" if ok else " na"

            nb_rows.append(
                f'            <a href="{href}" class="nb-entry{na_cls}">\n'
                f'                <span class="nb-num">{i + 1:02d}</span>\n'
                f'                <span>\n'
                f'                    <span class="nb-label">{escape(nb["title"])}</span>\n'
                f'                    <span class="nb-note">{escape(nb["desc"])}</span>\n'
                f'                </span>\n'
                f'            </a>'
            )

        delay = f"{idx * 0.08:.2f}s"
        rows.append(
            f'    <div class="cs-row" style="animation-delay:{delay}">\n'
            f'        <div class="cs-meta">\n'
            f'            <span class="cs-id">{cs_id_disp}</span>\n'
            f'            <span class="cs-status">{status}</span>\n'
            f'        </div>\n'
            f'        <div class="cs-content">\n'
            f'            <div class="cs-heading">{escape(clean_title)}</div>\n'
            f'            <div class="cs-tagline">{escape(cs["subtitle"])}</div>\n'
            f'            <div class="nb-list">\n'
            + "\n".join(nb_rows)
            + "\n            </div>\n"
            f'        </div>\n'
            f'    </div>'
        )

    html = INDEX_TEMPLATE
    html = html.replace("__SITE_TITLE__", SITE["title"])
    html = html.replace("__SITE_SUBTITLE__", SITE["subtitle_html"])
    html = html.replace("__GITHUB_URL__", SITE["github_url"])
    html = html.replace("__SECTIONS__", "\n".join(rows))
    return html


# ---------------------------------------------------------------------------
# About page generation
# ---------------------------------------------------------------------------
#
# Uses sentinel replacement (__KEY__) — same approach as INDEX_TEMPLATE.
# ---------------------------------------------------------------------------

ABOUT_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About &mdash; __SITE_TITLE__</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Mono:wght@400;500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
    <script>
        /* Anti-FOUT: apply stored theme before first paint */
        (function(){var t=localStorage.getItem('color-theme');if(t)document.documentElement.dataset.colorTheme=t;})();
    </script>
    <style>
        :root {
            --paper: #f5f1eb;
            --ink: #1a1917;
            --ink-mid: #4d4a46;
            --ink-light: #9a9490;
            --rule: #d6cfc7;
            --accent: #b84c2a;
        }
        @media (prefers-color-scheme: dark) {
            :root:not([data-color-theme]) {
                --paper: #14120f;
                --ink: #e5e0d8;
                --ink-mid: #ada89f;
                --ink-light: #5a5650;
                --rule: #2e2b27;
                --accent: #d4634a;
            }
        }
        :root[data-color-theme="dark"] {
            --paper: #14120f;
            --ink: #e5e0d8;
            --ink-mid: #ada89f;
            --ink-light: #5a5650;
            --rule: #2e2b27;
            --accent: #d4634a;
        }
        :root[data-color-theme="light"] {
            --paper: #f5f1eb;
            --ink: #1a1917;
            --ink-mid: #4d4a46;
            --ink-light: #9a9490;
            --rule: #d6cfc7;
            --accent: #b84c2a;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            background: var(--paper);
            color: var(--ink);
            font-family: 'DM Sans', sans-serif;
            font-weight: 300;
            line-height: 1.6;
            min-height: 100vh;
        }
        body::after {
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 999;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
        }
        .site-nav {
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 1.2rem 2.5rem;
            border-bottom: 1px solid var(--rule);
            position: sticky;
            top: 0;
            background: var(--paper);
            z-index: 50;
        }
        .site-nav a {
            font-family: 'DM Mono', monospace;
            font-size: 0.67rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--ink-light);
            text-decoration: none;
            transition: color 0.14s;
        }
        .site-nav a.active { color: var(--ink); }
        .site-nav a:hover { color: var(--ink); }
        .nav-spacer { flex: 1; }
        .theme-toggle {
            background: none;
            border: none;
            cursor: pointer;
            font-family: 'DM Mono', monospace;
            font-size: 0.82rem;
            color: var(--ink-light);
            padding: 0;
            line-height: 1;
            transition: color 0.14s;
        }
        .theme-toggle:hover { color: var(--ink); }
        /* about header */
        .about-header {
            padding: 4rem 2.5rem 3rem;
            border-bottom: 1px solid var(--rule);
        }
        .kicker {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-family: 'DM Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--ink-light);
            margin-bottom: 1.25rem;
        }
        .kicker::before {
            content: '';
            display: inline-block;
            width: 1.75rem;
            height: 1px;
            background: var(--accent);
        }
        .page-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(2rem, 4vw, 3.25rem);
            font-weight: 300;
            line-height: 1.08;
            letter-spacing: -0.02em;
            color: var(--ink);
        }
        /* about body */
        .about-body {
            max-width: 700px;
            padding: 3.5rem 2.5rem 5rem;
        }
        .name-sub {
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            color: var(--ink-light);
            margin-bottom: 1.75rem;
        }
        .about-body h2 {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.5rem;
            font-weight: 400;
            letter-spacing: -0.01em;
            color: var(--ink);
            margin: 3rem 0 0.9rem;
            padding-top: 2rem;
            border-top: 1px solid var(--rule);
        }
        .about-body h2:first-of-type { border-top: none; padding-top: 0; margin-top: 0.5rem; }
        .about-body p {
            font-size: 0.93rem;
            color: var(--ink-mid);
            line-height: 1.8;
            margin-bottom: 1rem;
        }
        .about-body p em { font-style: italic; }
        .about-body ul {
            margin: 0.25rem 0 1rem 1rem;
            color: var(--ink-mid);
            font-size: 0.93rem;
            line-height: 1.8;
        }
        .about-body ul li { margin-bottom: 0.2rem; }
        .about-body a { color: var(--ink); text-decoration-color: var(--rule); }
        .about-body a:hover { text-decoration-color: var(--ink); }
        /* timeline */
        .timeline {
            border-left: 1px solid var(--rule);
            margin: 1.25rem 0 1.5rem 0.25rem;
            padding-left: 1.5rem;
        }
        .timeline-item {
            margin-bottom: 1.25rem;
            position: relative;
        }
        .timeline-item::before {
            content: '';
            width: 5px;
            height: 5px;
            background: var(--rule);
            border-radius: 50%;
            position: absolute;
            left: -1.82rem;
            top: 0.5rem;
        }
        .timeline-year {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.06em;
            color: var(--accent);
            margin-bottom: 0.2rem;
        }
        .timeline-desc {
            font-size: 0.91rem;
            color: var(--ink-mid);
            line-height: 1.6;
        }
        /* contact links */
        .links {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-top: 0.75rem;
        }
        .link-pill {
            display: inline-block;
            border: 1px solid var(--rule);
            color: var(--ink);
            text-decoration: none;
            padding: 0.4rem 0.85rem;
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            transition: border-color 0.14s;
        }
        .link-pill:hover { border-color: var(--ink); }
        /* footer */
        .site-footer {
            padding: 2.5rem 2.5rem;
            border-top: 1px solid var(--rule);
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        .site-footer a,
        .site-footer span {
            font-family: 'DM Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.05em;
            color: var(--ink-light);
            text-decoration: none;
        }
        .site-footer a:hover { color: var(--ink); }
        /* mobile */
        @media (max-width: 680px) {
            .site-nav { padding: 1rem 1.25rem; gap: 1.5rem; }
            .about-header { padding: 3rem 1.25rem 2rem; }
            .about-body { padding: 2.5rem 1.25rem 4rem; }
            .site-footer { padding: 2rem 1.25rem; }
        }
    </style>
</head>
<body>
    <nav class="site-nav">
        <a href="index.html">Research</a>
        <a href="about.html" class="active">About</a>
        <span class="nav-spacer"></span>
        <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Toggle dark/light mode">◑</button>
        <a href="__GITHUB_URL__">GitHub</a>
    </nav>
    <div class="about-header">
        <p class="kicker">About the Research</p>
        <h1 class="page-title">Thandolwethu Zwelakhe Dlamini</h1>
    </div>
    <div class="about-body">
        <p class="name-sub">Goes by Shakes &mdash; from Eswatini (formerly Swaziland), Southern Africa</p>

        <p>I&rsquo;m a mechanical engineer with a background in energy access and
        infrastructure policy. This project started from a question I couldn&rsquo;t
        find a good answer to: what does $200B+ in annual AI capital expenditure
        actually do to the physical economy, and what does it lock in across short,
        medium, and long time horizons?</p>

        <p>The approach is investigative. Each case study picks one channel through
        which AI capital reaches the physical world and follows it: what gets built,
        what gets locked in, where the feedback loops are. The methods are data
        analysis, visualization, and systems dynamics modeling.</p>

        <h2>Background</h2>

        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-year">2015 &ndash; 2018</div>
                <div class="timeline-desc"><strong>Duke University</strong> &mdash;
                B.S. Mechanical Engineering, Minor in German. Study abroad in Berlin
                (Spring 2017). Research with Duke WaSH-AID on off-grid solar PV design
                for novel sanitation technologies.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-year">Aug 2018 &ndash; Mar 2019</div>
                <div class="timeline-desc"><strong>OnePower, Lesotho</strong> &mdash;
                Energy Access Fellow. Designed powerhouses for mini-grids serving
                rural communities without grid access.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-year">Mar 2019 &ndash; Aug 2019</div>
                <div class="timeline-desc"><strong>Eswatini Electricity Company</strong>
                &mdash; Engineering Trainee. Coordinated the company&rsquo;s first
                microgrid: a US&nbsp;$230,000 off-grid electrification project for a
                remote village unreachable by conventional grid infrastructure.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-year">Aug 2019 &ndash; May 2020</div>
                <div class="timeline-desc"><strong>Duke University</strong> &mdash;
                Final year. Represented Eswatini at COP25 in Madrid (Dec 2019) as
                part of the national delegation to the UN Climate Conference.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-year">2020 &ndash; 2022</div>
                <div class="timeline-desc"><strong>MIT</strong> &mdash; S.M. Technology
                &amp; Policy. Quantitative estimation of mercury emissions from
                artisanal and small-scale gold mining (ASGM), globally and regionally.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-year">2022 &ndash; 2025</div>
                <div class="timeline-desc"><strong>SunStrong Management LLC</strong>
                (formerly Sunnova Energy) &mdash; Senior Data Analyst. Managed data
                infrastructure and Energy Community ITC analysis for 200,000+ solar
                installations across the U.S.</div>
            </div>
        </div>

        <h2>Why This Project</h2>

        <p>AI capex numbers appear in quarterly earnings reports. But the capital
        converts into transformers, transmission lines, gas turbines, semiconductor
        fabs, and data center concrete. That infrastructure is durable &mdash; it
        reshapes supply chains, labor markets, grid topology, and trade patterns
        for decades.</p>

        <p><em>Where does AI capex land in the physical economy, what does it lock in,
        and how do current regulatory decisions amplify or distort those outcomes?</em></p>

        <p>Each case study traces one supply chain node and applies the same framework:
        capital flow mapping, durability taxonomy, and systems dynamics modeling to
        identify feedback architecture and policy leverage points.</p>

        <h2>Methods</h2>

        <p>All analysis is in <a href="https://marimo.io">marimo</a> &mdash; reactive
        Python notebooks that are valid .py files and diff cleanly in git. Data sources
        are government databases, regulatory filings, and company disclosures. The code,
        data pipelines, and methodology are fully visible in the source repository.</p>

        <ul>
            <li>Data pipelines: DuckDB + dlt</li>
            <li>Systems dynamics: PySD</li>
            <li>Visualization: matplotlib (Storytelling with Data principles)</li>
            <li>Statistics: PyMC, statsmodels</li>
        </ul>

        <h2>Contact</h2>

        <div class="links">
            <a href="https://github.com/Shakes-tzd/Systems" class="link-pill">Source Code</a>
            <a href="https://github.com/Shakes-tzd" class="link-pill">GitHub Profile</a>
        </div>

    </div>
    <footer class="site-footer">
        <span>Built with <a href="https://marimo.io">marimo</a></span>
        <a href="__GITHUB_URL__">Source on GitHub</a>
    </footer>
    <script>
        (function() {
            var root = document.documentElement;
            var btn = document.getElementById('theme-toggle');
            function effective() {
                var s = localStorage.getItem('color-theme');
                return s || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            }
            function apply(theme) {
                root.dataset.colorTheme = theme;
                if (btn) btn.textContent = theme === 'dark' ? '◐' : '◑';
            }
            apply(effective());
            window.toggleTheme = function() {
                var next = effective() === 'dark' ? 'light' : 'dark';
                localStorage.setItem('color-theme', next);
                apply(next);
            };
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                if (!localStorage.getItem('color-theme')) apply(e.matches ? 'dark' : 'light');
            });
        })();
    </script>
</body>
</html>
"""


def generate_about() -> str:
    """Generate the about.html content."""
    html = ABOUT_TEMPLATE
    html = html.replace("__SITE_TITLE__", SITE["title"])
    html = html.replace("__GITHUB_URL__", SITE["github_url"])
    return html


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

    # In strict mode (CI), fail if any notebook couldn't be exported.
    # Locally, partial exports are fine — failed notebooks appear grayed out.
    # Set STRICT_BUILD=1 in CI to enable strict mode.
    strict = os.environ.get("STRICT_BUILD", "0") == "1"
    if strict and ok < total:
        print(f"  STRICT_BUILD=1: returning non-zero (use locally without STRICT_BUILD to allow partial exports)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
