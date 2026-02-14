"""Reusable plotting functions for research notebooks.

All functions return matplotlib Figure objects (never call plt.show()).
Style is expected to be applied via src.notebook.setup() before use.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
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
