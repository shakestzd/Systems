"""Reusable plotting functions for research notebooks.

All functions return matplotlib Figure objects (never call plt.show()).
Style is expected to be applied via src.notebook.setup() before use.
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
                fontsize=9,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8
                ),
            )

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
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

        ax.set_title(panel.get("title", ""))
        ax.set_ylabel(panel.get("ylabel", ""))
        if "ylim" in panel:
            ax.set_ylim(panel["ylim"])
        if any("label" in s for s in panel["columns"].values()):
            ax.legend(fontsize=8)

    # Hide unused axes
    for idx in range(len(panels), nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)

    fig.suptitle(suptitle, fontsize=14, fontweight="bold")
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
    ax.set_xticklabels(df[x_col], rotation=45, ha="right")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, loc="upper left")
    plt.tight_layout()
    return fig


def waterfall_chart(
    items: list[tuple[str, float]],
    title: str,
    *,
    total_label: str = "Total",
    figsize: tuple[float, float] = (10, 5),
    positive_color: str = "#2ca02c",
    negative_color: str = "#d62728",
    total_color: str = "#1f77b4",
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
        ax.text(i, b + h + total * 0.01, label, ha="center", va="bottom", fontsize=9)

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
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel("$ Billions")
    plt.tight_layout()
    return fig


def horizontal_bar_ranking(
    labels: list[str],
    values: list[float],
    title: str,
    *,
    xlabel: str = "",
    color: str | list[str] = "#1f77b4",
    figsize: tuple[float, float] = (10, 6),
    highlight_indices: list[int] | None = None,
    highlight_color: str = "#d62728",
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
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.invert_yaxis()

    # Value labels at end of bars
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.01, i, f"{v:,.0f}", va="center", fontsize=9)

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
    figsize: tuple[float, float] = (12, 7),
    alpha: float = 0.6,
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
    states.plot(ax=ax, color="#f0f0f0", edgecolor="#cccccc", linewidth=0.5)

    ax.scatter(
        lons, lats, c=colors, s=sizes, alpha=alpha,
        edgecolors=edgecolors, linewidth=linewidth, zorder=3,
    )

    # Continental US bounds
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_axis_off()

    if legend_handles:
        ax.legend(handles=legend_handles, loc="lower left", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    return fig
