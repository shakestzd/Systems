"""Data loader: article frontmatter → JSON for the homepage article grid.

Published articles are the source of truth for their own metadata (title,
question, focus, arc). The CSV in research/deep_dives.csv is the fallback
for planned articles that don't have a .md file yet.

Ordering follows the CSV row order so the landing page sequence is
controlled in one place.
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parents[3]  # Systems/
SRC = pathlib.Path(__file__).parents[1]   # observable/src/
CSV_PATH = ROOT / "research" / "deep_dives.csv"


def parse_frontmatter(md_path: pathlib.Path) -> dict:
    """Extract YAML frontmatter key-value pairs from a .md file."""
    text = md_path.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w+):\s*"?(.+?)"?\s*$', line)
        if kv:
            fm[kv.group(1)] = kv.group(2)
    return fm


def discover_articles() -> dict:
    """Scan src/dd*.md for parent articles (not sub-articles like dd001-conversion)."""
    articles = {}
    for md in sorted(SRC.glob("dd*.md")):
        name = md.stem  # e.g. "dd001", "dd001-conversion"
        # Only parent articles (dd001, dd002, ...) — skip sub-articles
        if not re.match(r"^dd\d{3}$", name):
            continue
        fm = parse_frontmatter(md)
        if fm.get("id"):
            articles[fm["id"]] = {
                "id": fm["id"],
                "focus": fm.get("focus", ""),
                "topic": fm.get("title", ""),
                "question": fm.get("question", ""),
                "status": "Active",
                "url": "/" + name,
                "arc": fm.get("arc", "").split("→") if fm.get("arc") else [],
            }
    return articles


def load_csv_planned() -> list:
    """Load CSV rows for articles that aren't published yet."""
    rows = []
    with CSV_PATH.open() as f:
        for row in csv.DictReader(f):
            if row["Status"] in ("Archived",):
                continue
            rows.append(row)
    return rows


# Build the final list: CSV controls ordering, articles override metadata
csv_rows = load_csv_planned()
articles = discover_articles()
warnings = []

dives = []
seen_ids = set()

for row in csv_rows:
    rid = row["ID"]
    seen_ids.add(rid)

    if rid in articles:
        # Published article — frontmatter is source of truth
        dives.append(articles[rid])
    else:
        # Planned/unpublished — CSV is the source
        if row["Status"] == "Archived":
            continue
        dives.append({
            "id": rid,
            "focus": row["Focus Area"],
            "topic": row["Topic"],
            "question": row["Core Question"],
            "status": row["Status"],
            "url": row.get("url") or None,
            "arc": row["arc"].split("→") if row.get("arc") else [],
        })

# Warn about articles that exist but aren't in the CSV
for aid in articles:
    if aid not in seen_ids:
        warnings.append(f"WARNING: {aid} has a published article but no CSV row (won't appear on landing page)")

for w in warnings:
    print(w, file=sys.stderr)

print(json.dumps(dives, indent=2))
