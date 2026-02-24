"""Custom Altair/Vega-Lite theme matching the project design system.

Mirrors the flowmpl color palette and DM Sans / Cormorant Garamond typography
so that interactive Altair charts feel visually consistent with the static
matplotlib charts in the same notebooks.

Usage::

    import altair as alt
    from src.altair_theme import register
    register()   # called automatically by src.notebook.setup()

    chart = alt.Chart(df).mark_line().encode(...)
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Color tokens (mirror flowmpl / site CSS variables)
# ---------------------------------------------------------------------------

_INK = "#1a1917"
_INK_MID = "#4d4a46"
_INK_LIGHT = "#9a9490"
_PAPER = "#f5f1eb"
_RULE = "#d6cfc7"
_ACCENT = "#b84c2a"

# Categorical palette — matches flowmpl CATEGORICAL order
COLORS = [
    "#1f6fa8",  # blue-slate  (primary)
    "#b84c2a",  # terracotta  (accent / negative)
    "#4a7c59",  # forest      (positive)
    "#8e6c3a",  # amber-brown
    "#5b4e8a",  # muted violet
    "#3a7d8a",  # teal
    "#a05c6a",  # dusty rose
    "#6b8a3a",  # olive
]

# ---------------------------------------------------------------------------
# Theme definition
# ---------------------------------------------------------------------------

_THEME: dict = {
    "config": {
        "background": _PAPER,
        "font": "DM Sans",
        "range": {
            "category": COLORS,
            "ordinal": COLORS,
        },
        "title": {
            "font": "Cormorant Garamond",
            "fontSize": 15,
            "fontWeight": 300,
            "color": _INK,
            "anchor": "start",
        },
        "axis": {
            "labelFont": "DM Sans",
            "labelFontSize": 11,
            "labelColor": _INK_LIGHT,
            "titleFont": "DM Sans",
            "titleFontSize": 11,
            "titleFontWeight": 400,
            "titleColor": _INK_MID,
            "gridColor": _RULE,
            "gridOpacity": 0.6,
            "domainColor": _RULE,
            "tickColor": _RULE,
        },
        "legend": {
            "labelFont": "DM Sans",
            "labelFontSize": 11,
            "labelColor": _INK_MID,
            "titleFont": "DM Sans",
            "titleFontSize": 11,
            "titleFontWeight": 400,
            "titleColor": _INK_MID,
        },
        "header": {
            "labelFont": "DM Sans",
            "labelFontSize": 11,
            "titleFont": "DM Sans",
        },
        "mark": {
            "color": COLORS[0],
        },
        "line": {
            "strokeWidth": 1.8,
        },
        "point": {
            "size": 40,
            "filled": True,
        },
        "bar": {
            "discreteBandSize": 0.7,
        },
        "view": {
            "stroke": "transparent",
        },
        "padding": {"top": 8, "right": 8, "bottom": 8, "left": 8},
    }
}


def register() -> None:
    """Register and enable the project Altair theme.

    Called automatically by ``src.notebook.setup()``. Safe to call multiple
    times — subsequent calls are no-ops.
    """
    try:
        import altair as alt
    except ImportError:
        return

    alt.themes.register("systems", lambda: _THEME)
    alt.themes.enable("systems")
