"""Shared notebook setup utilities.

Provides consistent style, path resolution, and configuration
for all marimo notebooks in this project.

Usage in a marimo notebook cell:

    from src.notebook import setup, save_fig
    cfg = setup()
    # cfg.style is already applied to matplotlib
    # cfg.img_dir, cfg.project_root, cfg.data_dir available

    # Save a figure for embedding in prose:
    fig = some_plot()
    save_fig(fig, cfg.img_dir / "my_chart.png")

    # In a prose cell:
    chart = mo.image(src=(cfg.img_dir / "my_chart.png").read_bytes(), width=800)
    mo.md(f"Here's the analysis: {chart}")
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class NotebookConfig:
    """Immutable notebook configuration paths."""

    project_root: Path
    style_path: Path
    img_dir: Path
    data_dir: Path
    models_dir: Path


def setup() -> NotebookConfig:
    """Apply project style and return resolved paths.

    Call once in your notebook's import cell. Returns a frozen
    config object with all paths pre-resolved.
    """
    style_path = PROJECT_ROOT / "notebooks" / "shakes.mplstyle"
    plt.style.use(style_path)

    return NotebookConfig(
        project_root=PROJECT_ROOT,
        style_path=style_path,
        img_dir=PROJECT_ROOT / "notebooks" / "images",
        data_dir=PROJECT_ROOT / "data",
        models_dir=PROJECT_ROOT / "src" / "dynamics",
    )


def save_fig(fig: plt.Figure, path: Path, *, close: bool = True) -> Path:
    """Save a matplotlib figure and optionally close it.

    Returns the path so you can chain: mo.image(src=save_fig(fig, p).read_bytes())
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    if close:
        plt.close(fig)
    return path
