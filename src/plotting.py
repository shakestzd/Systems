"""Data visualization design system and reusable plotting functions.

This module is the single source of truth for all visual decisions:
colors, typography, figure sizing, and chart helpers. Notebooks import
constants and functions from here — no hex colors, font sizes, or
figure dimensions should appear as magic numbers in notebooks.

Design principles (inspired by Cara Thompson's dataviz design system):
- Parametrize everything through named constants
- Semantic color mapping: colors encode meaning, not just aesthetics
- Text hierarchy: clear visual levels from title to caption
- Accessibility: colorblind-safe palettes, sufficient contrast
- Consistency: same visual language across all notebooks

All functions return matplotlib Figure objects (never call plt.show()).
Style is applied via src.notebook.setup() which loads shakes.mplstyle.
Titles are NOT rendered on charts — use Marimo markdown H1 headings
above the chart instead.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Colors, Typography, Sizing
# ═══════════════════════════════════════════════════════════════════════════


# ---------------------------------------------------------------------------
# Semantic role colors — use these for directional meaning
# ---------------------------------------------------------------------------

COLORS: dict[str, str] = {
    "positive": "#2ca02c",      # growth, increase, good
    "negative": "#d62728",      # decline, decrease, bad
    "neutral": "#888888",       # neither good nor bad
    "accent": "#e74c3c",        # highlight, call attention
    "muted": "#cccccc",         # de-emphasized, fallback
    "reference": "#999999",     # reference lines, thresholds
    "text_dark": "#323034",     # primary text on white bg
    "text_light": "#666666",    # secondary text, annotations
    "background": "#f5f5f5",    # map fills, chart backgrounds
    "grid": "#e0e0e0",          # gridlines
}


# ---------------------------------------------------------------------------
# Domain colors — energy infrastructure
# ---------------------------------------------------------------------------

FUEL_COLORS: dict[str, str] = {
    "solar": "#f0b429",
    "wind": "#4ecdc4",
    "battery": "#7b68ee",
    "gas_cc": "#e74c3c",
    "gas_ct": "#ff8c69",
    "nuclear": "#3498db",
    "hydro": "#2ecc71",
    "coal": "#555555",
    "biomass": "#8c564b",
    "geothermal": "#d4a574",
    "other": "#bbbbbb",
}


# ---------------------------------------------------------------------------
# Company colors — hyperscaler brand identity
# ---------------------------------------------------------------------------

COMPANY_COLORS: dict[str, str] = {
    "MSFT": "#00a4ef",
    "AMZN": "#ff9900",
    "GOOGL": "#4285f4",
    "META": "#0668e1",
    "NVDA": "#76b900",
    "ORCL": "#f80000",
    "AAPL": "#a2aaad",
}

COMPANY_LABELS: dict[str, str] = {
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "META": "Meta",
    "NVDA": "Nvidia",
    "ORCL": "Oracle",
    "AAPL": "Apple",
}


# ---------------------------------------------------------------------------
# Categorical palette — colorblind-safe (Paul Tol qualitative scheme)
# Use for arbitrary series when no semantic mapping applies.
# ---------------------------------------------------------------------------

CATEGORICAL: list[str] = [
    "#4477AA",  # blue
    "#EE6677",  # red
    "#228833",  # green
    "#CCBB44",  # yellow
    "#66CCEE",  # cyan
    "#AA3377",  # purple
    "#BBBBBB",  # grey
    "#EE8866",  # orange
]


# ---------------------------------------------------------------------------
# Typography — font sizes by role
# ---------------------------------------------------------------------------

FONTS: dict[str, int] = {
    "axis_label": 15,       # xlabel, ylabel
    "tick_label": 14,       # xticklabels, yticklabels
    "annotation": 14,       # arrow annotations, callout text
    "value_label": 14,      # value labels on bars / scatter points
    "legend": 13,           # legend entries
    "panel_title": 14,      # subplot panel titles (multi_panel)
    "suptitle": 16,         # figure suptitle
    "caption": 11,          # figure captions, source notes
    "small": 11,            # small annotations, dense charts
}


# ---------------------------------------------------------------------------
# Figure size presets — named dimensions for consistency
# ---------------------------------------------------------------------------

FIGSIZE: dict[str, tuple[float, float]] = {
    "single": (10, 5),      # default for most charts
    "wide": (12, 5),        # time series, many categories
    "tall": (10, 7),        # vertical bar rankings
    "square": (8, 7),       # scatter, pie
    "double": (13, 5),      # side-by-side panels (1x2)
    "dashboard": (14, 8),   # 2x2 panel grids
    "map": (12, 7),         # US scatter maps
    "large": (16, 9),       # complex multi-panel
}


# ---------------------------------------------------------------------------
# Element defaults — consistent bar/scatter styling
# ---------------------------------------------------------------------------

BAR_DEFAULTS: dict[str, object] = {
    "alpha": 0.85,
    "edgecolor": "white",
    "linewidth": 0.5,
}

SCATTER_DEFAULTS: dict[str, object] = {
    "alpha": 0.6,
    "edgecolors": "white",
    "linewidth": 0.5,
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS — Color lookups, annotations, reference lines
# ═══════════════════════════════════════════════════════════════════════════


def fuel_color(fuel_type: str) -> str:
    """Look up color for a fuel/generation type, with graceful fallback."""
    return FUEL_COLORS.get(fuel_type, COLORS["muted"])


def company_color(ticker: str) -> str:
    """Look up brand color for a company ticker, with graceful fallback."""
    return COMPANY_COLORS.get(ticker, COLORS["muted"])


def company_label(ticker: str) -> str:
    """Look up display name for a company ticker."""
    return COMPANY_LABELS.get(ticker, ticker)


def annotate_point(
    ax: plt.Axes,
    text: str,
    xy: tuple[float, float],
    xytext: tuple[float, float],
    *,
    color: str | None = None,
    fontsize: int | None = None,
    arrowstyle: str = "->",
    arrow_lw: float = 1.5,
    bbox: bool = True,
    ha: str = "center",
    **kwargs: object,
) -> None:
    """Annotate a data point with consistent arrow + text styling.

    Parameters
    ----------
    ax : Axes
        Target axes.
    text : str
        Annotation text.
    xy : (x, y)
        Point to annotate (data coordinates).
    xytext : (x, y)
        Text position (data coordinates).
    color : str, optional
        Text and arrow color.  Defaults to COLORS["text_light"].
    fontsize : int, optional
        Font size.  Defaults to FONTS["annotation"].
    arrowstyle : str
        Matplotlib arrow style string.
    arrow_lw : float
        Arrow line width.
    bbox : bool
        Whether to draw a rounded box behind the text.
    ha : str
        Horizontal alignment.
    **kwargs
        Forwarded to ax.annotate().
    """
    color = color or COLORS["text_light"]
    fontsize = fontsize or FONTS["annotation"]

    bbox_props = (
        {"boxstyle": "round,pad=0.3", "fc": "white", "ec": color, "alpha": 0.8}
        if bbox
        else None
    )

    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        ha=ha,
        arrowprops={"arrowstyle": arrowstyle, "color": color, "lw": arrow_lw},
        bbox=bbox_props,
        **kwargs,
    )


def reference_line(
    ax: plt.Axes,
    value: float,
    orientation: str = "h",
    *,
    label: str | None = None,
    color: str | None = None,
    linestyle: str = "--",
    linewidth: float = 1.5,
    alpha: float = 0.7,
    label_pos: str = "right",
) -> None:
    """Add a labeled reference line (horizontal or vertical).

    Parameters
    ----------
    ax : Axes
        Target axes.
    value : float
        Position of the line.
    orientation : "h" or "v"
        Horizontal or vertical line.
    label : str, optional
        Text label placed near the line.
    color : str, optional
        Line and label color.  Defaults to COLORS["reference"].
    linestyle : str
        Line style.
    linewidth : float
        Line width.
    alpha : float
        Line transparency.
    label_pos : "left" or "right" (for h) / "top" or "bottom" (for v)
        Where to place the label text.
    """
    color = color or COLORS["reference"]
    line_fn = ax.axhline if orientation == "h" else ax.axvline
    line_fn(value, color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)

    if label:
        if orientation == "h":
            _x = ax.get_xlim()[1] if label_pos == "right" else ax.get_xlim()[0]
            _ha = "right" if label_pos == "right" else "left"
            ax.text(
                _x, value, f" {label} ",
                fontsize=FONTS["small"], color=color, fontweight="bold",
                va="bottom", ha=_ha,
            )
        else:
            _y = ax.get_ylim()[1] if label_pos == "top" else ax.get_ylim()[0]
            _va = "top" if label_pos == "top" else "bottom"
            ax.text(
                value, _y, f" {label} ",
                fontsize=FONTS["small"], color=color, fontweight="bold",
                va=_va, ha="left",
            )


# ---------------------------------------------------------------------------
# Legend placement — single pattern for all charts.
# ---------------------------------------------------------------------------

def legend_below(
    ax: plt.Axes,
    *,
    ncol: int | None = None,
    handles: list | None = None,
    labels: list[str] | None = None,
    **kwargs,
) -> None:
    """Place legend below the axes in a horizontal column layout.

    Works with save_fig's ``bbox_inches='tight'`` to auto-expand the
    saved figure so the legend is never clipped.

    Parameters
    ----------
    ax : Axes
        The axes whose legend to relocate.
    ncol : int, optional
        Number of columns.  Defaults to ``min(len(handles), 5)``.
    handles, labels : optional
        Explicit legend handles/labels.  When *None*, pulled from *ax*.
    **kwargs
        Forwarded to ``ax.legend()``.
    """
    if handles is None:
        h, lab = ax.get_legend_handles_labels()
        handles = h
        if labels is None:
            labels = lab
    elif labels is None:
        labels = [h.get_label() for h in handles]
    if not handles:
        return
    if ncol is None:
        ncol = min(len(handles), 5)
    # Remove existing legend so it doesn't stack
    old = ax.get_legend()
    if old:
        old.remove()
    _anchor = kwargs.pop("bbox_to_anchor", (0.5, -0.15))
    ax.legend(
        handles, labels,
        loc="upper center",
        bbox_to_anchor=_anchor,
        ncol=ncol,
        fontsize=FONTS["legend"],
        frameon=False,
        **kwargs,
    )


def annotated_series(
    df: pd.DataFrame,
    columns: dict[str, dict],
    title: str,
    *,
    annotations: list[tuple[str, object, float, tuple]] | None = None,
    ylabel: str = "Index",
    fill_between: tuple[str, str] | None = None,
    figsize: tuple[float, float] = (10, 5),
) -> plt.Figure:
    """Plot time series with optional annotations and fill.

    Parameters
    ----------
    df : DataFrame
        DatetimeIndex dataframe.
    columns : dict
        Mapping of column name -> style kwargs.
        Example: {"Transformer_PPI": {"color": "#d62728", "label": "Actual"}}
    title : str
        Plot title.
    annotations : list of (text, x_date, y_val, xytext_pos), optional
        Arrow annotations to overlay.
    ylabel : str
        Y-axis label.
    fill_between : (col_upper, col_lower), optional
        Shade area between two columns.
    figsize : tuple
        Figure size.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    for col, style in columns.items():
        ax.plot(df.index, df[col], **style)

    if fill_between:
        upper, lower = fill_between
        ax.fill_between(df.index, df[upper], df[lower], color="gray", alpha=0.1)

    if annotations:
        for text, date, y_val, arrow_pos in annotations:
            ax.annotate(
                text,
                xy=(date, y_val),
                xytext=arrow_pos,
                arrowprops=dict(
                    facecolor="black", shrink=0.05, width=1, headwidth=5
                ),
                fontsize=FONTS["annotation"],
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8
                ),
            )

    ax.set_ylabel(ylabel, fontsize=FONTS["axis_label"])
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    legend_below(ax)
    return fig


def multi_panel(
    df: pd.DataFrame,
    panels: list[dict],
    suptitle: str,
    *,
    ncols: int = 2,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Create a multi-panel figure from a single DataFrame.

    Parameters
    ----------
    df : DataFrame
        Source data with DatetimeIndex.
    panels : list of dict
        Each dict defines one subplot:
        - "columns": dict of col -> style kwargs (same as annotated_series)
        - "title": str
        - "ylabel": str (optional)
        - "ylim": tuple (optional)
    suptitle : str
        Overall figure title.
    ncols : int
        Number of columns in subplot grid.
    figsize : tuple, optional
        Figure size. Defaults to (6*ncols, 4*nrows).

    Returns
    -------
    matplotlib.figure.Figure
    """
    nrows = int(np.ceil(len(panels) / ncols))
    if figsize is None:
        figsize = (6 * ncols, 4 * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.atleast_2d(axes)

    for idx, panel in enumerate(panels):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]

        for column, style in panel["columns"].items():
            ax.plot(df.index, df[column], **style)

        ax.set_title(panel.get("title", ""), fontsize=FONTS["panel_title"])
        ax.set_ylabel(panel.get("ylabel", ""), fontsize=FONTS["axis_label"])
        if "ylim" in panel:
            ax.set_ylim(panel["ylim"])
        if any("label" in s for s in panel["columns"].values()):
            ax.legend(fontsize=FONTS["legend"])

    # Hide unused axes
    for idx in range(len(panels), nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)
    plt.tight_layout()
    return fig


def stacked_bar(
    df: pd.DataFrame,
    x_col: str,
    stack_cols: dict[str, dict],
    title: str,
    *,
    ylabel: str = "",
    figsize: tuple[float, float] = (10, 5),
    rotation: int = 0,
) -> plt.Figure:
    """Stacked bar chart for categorical breakdowns.

    Parameters
    ----------
    df : DataFrame
        Source data.
    x_col : str
        Column to use for x-axis categories.
    stack_cols : dict
        Mapping of column name -> style kwargs (must include 'color', 'label').
    title : str
        Insight-driven chart title.
    ylabel : str
        Y-axis label.
    figsize : tuple
        Figure size.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(df[x_col]))
    width = 0.7
    bottom = np.zeros(len(x))

    for col, style in stack_cols.items():
        color = style.pop("color", None)
        label = style.pop("label", col)
        values = df[col].values.astype(float)
        ax.bar(x, values, width, bottom=bottom, color=color, label=label, **style)
        bottom += values

    ax.set_xticks(x)
    _ha = "right" if rotation else "center"
    ax.set_xticklabels(df[x_col], rotation=rotation, ha=_ha)
    ax.set_ylabel(ylabel, fontsize=FONTS["axis_label"])
    plt.tight_layout()
    legend_below(ax)
    return fig


def waterfall_chart(
    items: list[tuple[str, float]],
    title: str,
    *,
    total_label: str = "Total",
    figsize: tuple[float, float] = (10, 5),
    positive_color: str = COLORS["positive"],
    negative_color: str = COLORS["negative"],
    total_color: str = CATEGORICAL[0],
) -> plt.Figure:
    """Waterfall chart for cost allocation or flow breakdowns.

    Parameters
    ----------
    items : list of (label, value)
        Each item adds or subtracts from the running total.
        The final total bar is added automatically.
    title : str
        Insight-driven chart title.
    total_label : str
        Label for the total bar.
    figsize : tuple
        Figure size.

    Returns
    -------
    matplotlib.figure.Figure
    """
    labels = [label for label, _ in items] + [total_label]
    values = [value for _, value in items]
    total = sum(values)

    # Compute bar positions: each starts where the previous ended
    cumulative = np.zeros(len(values) + 1)
    for i, v in enumerate(values):
        cumulative[i + 1] = cumulative[i] + v

    bottoms = np.zeros(len(labels))
    heights = np.zeros(len(labels))
    colors = []

    for i, v in enumerate(values):
        if v >= 0:
            bottoms[i] = cumulative[i]
            heights[i] = v
            colors.append(positive_color)
        else:
            bottoms[i] = cumulative[i + 1]
            heights[i] = abs(v)
            colors.append(negative_color)

    # Total bar starts from zero
    bottoms[-1] = 0
    heights[-1] = total
    colors.append(total_color)

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(labels))
    ax.bar(x, heights, bottom=bottoms, color=colors, width=0.6, edgecolor="white")

    # Value labels on bars
    for i, (b, h) in enumerate(zip(bottoms, heights)):
        val = values[i] if i < len(values) else total
        label = f"${val:,.1f}B" if abs(val) >= 1 else f"${val * 1000:,.0f}M"
        ax.text(i, b + h + total * 0.01, label, ha="center", va="bottom",
                fontsize=FONTS["value_label"])

    # Connector lines between bars
    for i in range(len(values)):
        ax.plot(
            [i + 0.3, i + 0.7],
            [cumulative[i + 1], cumulative[i + 1]],
            color="gray",
            linewidth=0.8,
            linestyle="--",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right",
                       fontsize=FONTS["tick_label"])
    ax.set_ylabel("$ Billions", fontsize=FONTS["axis_label"])
    plt.tight_layout()
    return fig


def horizontal_bar_ranking(
    labels: list[str],
    values: list[float],
    title: str,
    *,
    xlabel: str = "",
    color: str | list[str] = CATEGORICAL[0],
    figsize: tuple[float, float] = FIGSIZE["tall"],
    highlight_indices: list[int] | None = None,
    highlight_color: str = COLORS["accent"],
) -> plt.Figure:
    """Horizontal bar chart for ranking comparisons.

    Parameters
    ----------
    labels : list of str
        Category labels (displayed on y-axis).
    values : list of float
        Values for each category.
    title : str
        Insight-driven chart title.
    xlabel : str
        X-axis label.
    color : str or list of str
        Bar color(s).
    figsize : tuple
        Figure size.
    highlight_indices : list of int, optional
        Indices to highlight in a different color.
    highlight_color : str
        Color for highlighted bars.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    y = np.arange(len(labels))

    if isinstance(color, str):
        colors = [color] * len(labels)
    else:
        colors = list(color)

    if highlight_indices:
        for idx in highlight_indices:
            if 0 <= idx < len(colors):
                colors[idx] = highlight_color

    ax.barh(y, values, color=colors, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel, fontsize=FONTS["axis_label"])
    ax.invert_yaxis()

    # Value labels at end of bars
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.01, i, f"{v:,.0f}", va="center",
                fontsize=FONTS["value_label"])

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# State boundary data for maps
# ---------------------------------------------------------------------------

_SHAPEFILE_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "external" / "cb_2024_us_state_20m"
)
_SHAPEFILE_URL = (
    "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip"
)

# FIPS codes for non-continental states/territories to exclude
_EXCLUDE_FIPS = {
    "02", "15", "60", "66", "69", "72", "78",  # AK, HI, AS, GU, MP, PR, VI
}


def _get_states_gdf():
    """Load continental US state boundaries, downloading if needed."""
    import geopandas as gpd

    shp_file = _SHAPEFILE_DIR / "cb_2024_us_state_20m.shp"
    if not shp_file.exists():
        import requests

        resp = requests.get(_SHAPEFILE_URL, timeout=60)
        resp.raise_for_status()
        _SHAPEFILE_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(_SHAPEFILE_DIR)

    gdf = gpd.read_file(shp_file)
    # Filter to continental US
    return gdf[~gdf["STATEFP"].isin(_EXCLUDE_FIPS)]


def us_scatter_map(
    lats: Sequence[float],
    lons: Sequence[float],
    colors: Sequence[str] | str,
    sizes: Sequence[float] | float,
    title: str,
    *,
    legend_handles: list | None = None,
    figsize: tuple[float, float] = FIGSIZE["map"],
    alpha: float = SCATTER_DEFAULTS["alpha"],
    edgecolors: str = "white",
    linewidth: float = 0.5,
) -> plt.Figure:
    """Plot scatter points on a US continental map with state boundaries.

    Parameters
    ----------
    lats : sequence of float
        Latitude values (decimal degrees).
    lons : sequence of float
        Longitude values (decimal degrees).
    colors : str or sequence of str
        Color(s) for each point.
    sizes : float or sequence of float
        Size(s) for each point.
    title : str
        Insight-driven chart title.
    legend_handles : list, optional
        Matplotlib legend handles to display.
    figsize : tuple
        Figure size.
    alpha : float
        Point transparency.
    edgecolors : str
        Edge color for scatter points.
    linewidth : float
        Edge linewidth for scatter points.

    Returns
    -------
    matplotlib.figure.Figure
    """
    states = _get_states_gdf()

    fig, ax = plt.subplots(figsize=figsize)
    states.plot(ax=ax, color=COLORS["background"], edgecolor=COLORS["muted"], linewidth=0.7)

    ax.scatter(
        lons, lats, c=colors, s=sizes, alpha=alpha,
        edgecolors=edgecolors, linewidth=linewidth, zorder=3,
    )

    # Continental US bounds
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    ax.set_axis_off()

    if legend_handles:
        labels = [h.get_label() for h in legend_handles]
        ncol = min(len(legend_handles), 5)
        ax.legend(
            handles=legend_handles, labels=labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.03),
            ncol=ncol,
            fontsize=FONTS["legend"],
            frameon=False,
            markerscale=1.3,
        )

    plt.tight_layout()
    return fig
