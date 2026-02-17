"""SEC EDGAR data access for hyperscaler financial data.

Uses the SEC EDGAR XBRL APIs (no authentication required, no API key).
Rate limit: 10 req/sec. All requests include User-Agent header per SEC policy.

API docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
Company Facts: https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
Company Concept: https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json
Submissions: https://data.sec.gov/submissions/CIK{cik}.json
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

# SEC requires User-Agent with contact info
USER_AGENT = "Systems Research Project systems-research@proton.me"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}

# Rate limiting: 10 req/sec max → 0.12s between requests
_MIN_INTERVAL = 0.12
_last_request_time = 0.0

# ── Company registry ─────────────────────────────────────────────────

COMPANIES: dict[str, tuple[str, str]] = {
    "META": ("0001326801", "Meta Platforms Inc"),
    "AMZN": ("0001018724", "Amazon.com Inc"),
    "GOOGL": ("0001652044", "Alphabet Inc"),
    "MSFT": ("0000789019", "Microsoft Corp"),
}

# XBRL concepts to extract (tag -> taxonomy)
# Note: these companies use the "...AndFinanceLeaseRightOfUseAsset..." variants
# in recent filings. We extract both old and new tag names.
XBRL_CONCEPTS: dict[str, str] = {
    # Aggregate PP&E (for cross-validation)
    "PropertyPlantAndEquipmentGross": "us-gaap",
    "PropertyPlantAndEquipmentNet": "us-gaap",
    (
        "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset"
        "BeforeAccumulatedDepreciationAndAmortization"
    ): "us-gaap",
    (
        "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset"
        "AfterAccumulatedDepreciationAndAmortization"
    ): "us-gaap",
    (
        "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset"
        "AccumulatedDepreciationAndAmortization"
    ): "us-gaap",
    "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment": "us-gaap",
    # Capex
    "PaymentsToAcquirePropertyPlantAndEquipment": "us-gaap",
    # Deferred tax (useful for depreciation analysis)
    "DeferredTaxLiabilitiesPropertyPlantAndEquipment": "us-gaap",
}
# Note: Employee headcount is NOT available via XBRL for META/AMZN/GOOGL.
# Headcount values are sourced from 10-K Item 1 and stored in source_citations.csv.

# PP&E category normalization per company
# Maps lowercase substring in raw label → normalized category
CATEGORY_MAPPINGS: dict[str, list[tuple[str, str]]] = {
    "META": [
        ("server", "equipment"),
        ("network", "equipment"),
        ("equipment", "equipment"),
        ("building", "buildings"),
        ("land", "land"),
        ("construction", "construction_in_progress"),
        ("leasehold", "other"),
        ("furniture", "other"),
    ],
    "AMZN": [
        ("land and building", "buildings"),
        ("building", "buildings"),
        ("land", "land"),
        ("equipment", "equipment"),
        ("construction", "construction_in_progress"),
        ("leasehold", "other"),
    ],
    "GOOGL": [
        ("information technology", "equipment"),
        ("technical infrastructure", "equipment"),
        ("office space", "buildings"),
        ("building", "buildings"),
        ("land", "land"),
        ("not yet in service", "construction_in_progress"),
        ("construction", "construction_in_progress"),
        ("corporate", "other"),
    ],
    "MSFT": [
        ("computer", "equipment"),
        ("server", "equipment"),
        ("building", "buildings"),
        ("land", "land"),
        ("construction", "construction_in_progress"),
        ("leasehold", "other"),
        ("furniture", "other"),
    ],
}


# ── Rate-limited HTTP ─────────────────────────────────────────────────


def _get_json(url: str) -> dict[str, Any]:
    """Rate-limited GET returning parsed JSON. Raises on HTTP errors."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    logger.debug("GET %s", url)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    _last_request_time = time.time()
    resp.raise_for_status()
    return resp.json()


def _get_html(url: str) -> str:
    """Rate-limited GET returning HTML text. Raises on HTTP errors."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    headers = {**HEADERS, "Accept": "text/html"}
    logger.debug("GET %s", url)
    resp = requests.get(url, headers=headers, timeout=60)
    _last_request_time = time.time()
    resp.raise_for_status()
    return resp.text


# ── XBRL Company Concept API ─────────────────────────────────────────


def get_company_concept(
    cik: str, taxonomy: str, tag: str
) -> dict[str, Any]:
    """Fetch all historical values for a single XBRL concept.

    Returns the raw JSON response from the Company Concept API.
    """
    url = (
        f"https://data.sec.gov/api/xbrl/companyconcept/"
        f"CIK{cik}/{taxonomy}/{tag}.json"
    )
    return _get_json(url)


def extract_annual_facts(
    concept_data: dict[str, Any],
    ticker: str,
) -> list[dict[str, Any]]:
    """Extract annual (10-K) values from a Company Concept API response.

    Filters to 10-K filings with annual duration (>= 300 days) to avoid
    quarterly values. Returns most recent filing per fiscal year to handle
    amendments (10-K/A).
    """
    results: list[dict[str, Any]] = []
    tag = concept_data.get("tag", "unknown")
    units = concept_data.get("units", {})

    # Determine the unit key — typically "USD" for dollar amounts or
    # "pure"/"shares" for counts
    for unit_key, values in units.items():
        for entry in values:
            form = entry.get("form", "")
            # Only 10-K and 10-K/A filings
            if form not in ("10-K", "10-K/A"):
                continue

            # For financial values, filter to full-year frames (not quarterly)
            # Employee count has no start date, so skip duration check for dei
            start = entry.get("start")
            end = entry.get("end", "")
            if start and end:
                try:
                    d_start = datetime.strptime(start, "%Y-%m-%d")
                    d_end = datetime.strptime(end, "%Y-%m-%d")
                    duration = (d_end - d_start).days
                    if duration < 300:  # skip quarterly/semiannual
                        continue
                except ValueError:
                    pass

            # Extract fiscal year from the end date
            fiscal_year = int(end[:4]) if end else None
            if fiscal_year is None:
                # For point-in-time values (like employee count), use filed date
                filed = entry.get("filed", "")
                fiscal_year = int(filed[:4]) if filed else None

            if fiscal_year is None:
                continue

            results.append(
                {
                    "ticker": ticker,
                    "concept": tag,
                    "fiscal_year": fiscal_year,
                    "value": entry.get("val"),
                    "unit": unit_key,
                    "filed": entry.get("filed", ""),
                    "form": form,
                    "end_date": end,
                }
            )

    # Keep only the most recent filing per fiscal year (handles amendments)
    by_year: dict[int, dict] = {}
    for r in results:
        fy = r["fiscal_year"]
        if fy not in by_year or r["filed"] > by_year[fy]["filed"]:
            by_year[fy] = r
    return list(by_year.values())


# ── Submissions API (filing discovery) ────────────────────────────────


def get_submissions(cik: str) -> dict[str, Any]:
    """Fetch filing submission history for a company."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    return _get_json(url)


def find_10k_accession(
    submissions: dict[str, Any], fiscal_year: int
) -> tuple[str, str] | None:
    """Find the 10-K filing accession number and primary document for a fiscal year.

    Returns (accession_number, primary_document) or None if not found.
    The accession_number has dashes stripped for URL construction.
    """
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form not in ("10-K", "10-K/A"):
            continue
        filing_date = dates[i] if i < len(dates) else ""
        # Match fiscal year: filing typically happens in Q1 of the next year
        # (e.g., FY2024 10-K filed Feb 2025)
        filing_year = int(filing_date[:4]) if filing_date else 0
        if filing_year in (fiscal_year, fiscal_year + 1):
            accession = accessions[i] if i < len(accessions) else ""
            primary_doc = primary_docs[i] if i < len(primary_docs) else ""
            return (accession, primary_doc)
    return None


# ── 10-K HTML download ────────────────────────────────────────────────


def download_10k_html(
    ticker: str,
    cik: str,
    fiscal_year: int,
    save_dir: Path,
) -> Path | None:
    """Download the primary 10-K HTML document and cache locally.

    Returns the local file path, or None if the filing wasn't found.
    Skips download if the file already exists (caching).
    """
    cache_dir = save_dir / ticker
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{fiscal_year}_10k.html"

    if cache_path.exists():
        logger.info("Cached: %s", cache_path)
        return cache_path

    submissions = get_submissions(cik)
    result = find_10k_accession(submissions, fiscal_year)
    if result is None:
        logger.warning("No 10-K found for %s FY%d", ticker, fiscal_year)
        return None

    accession, primary_doc = result
    accession_no_dashes = accession.replace("-", "")
    cik_numeric = cik.lstrip("0")
    url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_numeric}/{accession_no_dashes}/{primary_doc}"
    )

    logger.info("Downloading %s FY%d 10-K from %s", ticker, fiscal_year, url)
    html = _get_html(url)
    cache_path.write_text(html, encoding="utf-8")
    logger.info("Saved to %s (%d bytes)", cache_path, len(html))
    return cache_path


# ── PP&E schedule extraction from 10-K HTML ──────────────────────────


def _normalize_category(raw_label: str, ticker: str) -> str:
    """Map a raw PP&E line item label to a normalized category.

    Uses a two-tier skip approach:
    1. Unambiguous total/summary rows are skipped first (these contain category
       keywords like "equipment" but are aggregates, not line items).
    2. Category mappings identify specific line items.
    3. Remaining generic skip patterns catch anything else.
    """
    label_lower = raw_label.lower().strip()

    # Tier 1: Skip unambiguous total/summary rows BEFORE category matching.
    # These rows contain keywords like "equipment" but are aggregates.
    if any(
        kw in label_lower
        for kw in [
            "total",
            "less accumulated",
            "accumulated depreciation",
            "property and equipment, gross",
            "property and equipment, net",
            "property and equipment gross",
            "property and equipment net",
            "property, plant and equipment",
            "gross property and equipment",
            "property and equipment, in service",
            "finance lease",
            "operating lease",
            "right-of-use",
        ]
    ):
        return "__skip__"

    # Tier 2: Positive category mappings (e.g. "server" → equipment)
    mappings = CATEGORY_MAPPINGS.get(ticker, [])
    for substring, category in mappings:
        if substring in label_lower:
            return category

    # Tier 3: Generic skip patterns — header/label rows and depreciation lines
    if any(
        kw in label_lower
        for kw in [
            "depreciation", "amortization",
            "in millions", "in thousands",
            "june 30", "december 31", "march 31", "september 30",
        ]
    ):
        return "__skip__"

    logger.warning(
        "Unknown PP&E category for %s: '%s' — mapping to 'other'",
        ticker,
        raw_label,
    )
    return "other"


def _parse_dollar_value(text: str) -> float | None:
    """Parse a dollar value from table cell text.

    Handles: $1,234  (1,234)  1234  —  empty
    Returns value in millions (assumes filing values are in millions).
    """
    text = text.strip().replace("$", "").replace(",", "").replace("\xa0", "")
    if not text or text in ("—", "–", "-", ""):
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    try:
        val = float(text)
        return -val if negative else val
    except ValueError:
        return None


def extract_ppe_schedule(
    html_path: Path,
    ticker: str,
    fiscal_year: int,
) -> list[dict[str, Any]]:
    """Parse the PP&E property schedule table from a 10-K filing HTML.

    Finds the table containing the property/equipment breakdown and
    extracts per-category gross values.

    Returns a list of dicts with: ticker, fiscal_year, category,
    category_raw, gross_value_m.
    """
    import warnings

    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
    html = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    # Strategy: find text mentioning "property and equipment" or
    # "property, plant" near a table
    target_patterns = [
        re.compile(r"property\s+and\s+equipment", re.IGNORECASE),
        re.compile(r"property,?\s*plant\s+and\s+equipment", re.IGNORECASE),
    ]

    # Find all tables and score them by proximity to PP&E headings
    tables = soup.find_all("table")
    best_table = None
    best_score = -1

    for table in tables:
        table_text = table.get_text(" ", strip=True)
        score = 0

        # Must contain PP&E keywords
        for pattern in target_patterns:
            if pattern.search(table_text):
                score += 5

        # Check for category keywords
        table_lower = table_text.lower()
        for keyword in [
            "building", "server", "equipment", "computer",
            "construction in progress", "land", "network",
            "information technology", "technical infrastructure",
            "leasehold", "furniture",
        ]:
            if keyword in table_lower:
                score += 2

        # Strong signal: contains dollar values (numbers with commas)
        # This distinguishes the data table from the useful-life table
        dollar_pattern = re.compile(r"\d{1,3}(?:,\d{3})+")
        dollar_matches = dollar_pattern.findall(table_text)
        if len(dollar_matches) >= 4:
            score += 20  # heavily favor tables with financial data

        # Contains "accumulated depreciation" = data table, not policy
        if "accumulated depreciation" in table_lower:
            score += 10

        # Negative signals: financial statements (balance sheet, income stmt)
        # These are large tables that contain PP&E as a line item, not a schedule
        for neg_kw in [
            "stockholders' equity", "stockholders\u2019 equity",
            "liabilities and", "current assets",
            "accounts payable", "unearned revenue",
            "net income", "operating income",
        ]:
            if neg_kw in table_lower:
                score -= 5

        # PP&E schedules are compact (5-15 rows, < 2000 chars of text)
        # Penalize very large tables (balance sheets, income statements)
        if len(table_text) > 3000:
            score -= 10

        # Check preceding siblings/parents for PP&E heading
        prev = table.find_previous(
            ["h1", "h2", "h3", "h4", "p", "span", "b", "strong"]
        )
        if prev:
            prev_text = prev.get_text(" ", strip=True)
            for pattern in target_patterns:
                if pattern.search(prev_text):
                    score += 5

        if score > best_score:
            best_score = score
            best_table = table

    if best_table is None or best_score < 10:
        logger.warning(
            "Could not find PP&E schedule table in %s (best score: %d)",
            html_path.name,
            best_score,
        )
        return []

    logger.info(
        "Found PP&E table for %s FY%d (score: %d)", ticker, fiscal_year, best_score
    )

    # Detect which column index corresponds to the requested fiscal year.
    # Scan header/early rows for year references to determine column ordering.
    rows = best_table.find_all("tr")
    target_col_idx = 0  # default: first value column = most recent year

    header_text = best_table.get_text(" ", strip=True)
    year_pattern = re.compile(r"\b(20\d{2})\b")
    header_years = [int(y) for y in year_pattern.findall(header_text[:300])]
    # Deduplicate while preserving order
    seen: set[int] = set()
    unique_years: list[int] = []
    for y in header_years:
        if y not in seen:
            seen.add(y)
            unique_years.append(y)

    if len(unique_years) >= 2:
        # Find which position the target fiscal year is in
        # MSFT uses June 30 fiscal year end, so FY2024 ends June 2024
        # but the filing might show "2025 2024" (FY2025 first)
        for idx, year in enumerate(unique_years):
            if year == fiscal_year:
                target_col_idx = idx
                break
        logger.info(
            "Column years detected: %s → using column %d for FY%d",
            unique_years, target_col_idx, fiscal_year,
        )

    # Extract rows from the best table
    results: list[dict[str, Any]] = []

    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue

        label = cells[0].get_text(" ", strip=True)
        if not label or len(label) < 3:
            continue

        category = _normalize_category(label, ticker)
        if category == "__skip__":
            continue

        # Extract all numeric values from the row
        values = []
        for cell in cells[1:]:
            val = _parse_dollar_value(cell.get_text(" ", strip=True))
            if val is not None:
                values.append(val)

        if not values:
            continue

        # Pick the column matching the requested fiscal year
        col = min(target_col_idx, len(values) - 1)
        gross_value = values[col]

        results.append(
            {
                "ticker": ticker,
                "fiscal_year": fiscal_year,
                "category": category,
                "category_raw": label,
                "gross_value_m": gross_value,
            }
        )

    # Consolidate: sum values within the same normalized category
    consolidated: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        if cat in consolidated:
            consolidated[cat]["gross_value_m"] += r["gross_value_m"]
            consolidated[cat]["category_raw"] += f"; {r['category_raw']}"
        else:
            consolidated[cat] = r.copy()

    return list(consolidated.values())
