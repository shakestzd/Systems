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

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class NotebookConfig:
    """Immutable notebook configuration paths."""

    project_root: Path
    img_dir: Path
    data_dir: Path
    models_dir: Path


def setup() -> NotebookConfig:
    """Apply project style and return resolved paths.

    Call once in your notebook's import cell. Returns a frozen
    config object with all paths pre-resolved.
    """
    from flowmpl import apply_style
    apply_style()

    # Register Altair theme if altair is installed — soft dependency so
    # notebooks that don't use Altair are unaffected.
    try:
        from src.altair_theme import register as _register_altair
        _register_altair()
    except ImportError:
        pass

    return NotebookConfig(
        project_root=PROJECT_ROOT,
        img_dir=PROJECT_ROOT / "notebooks" / "images",
        data_dir=PROJECT_ROOT / "data",
        models_dir=PROJECT_ROOT / "src" / "dynamics",
    )


def save_fig(fig, path: Path, *, close: bool = True) -> None:
    """Save a matplotlib figure to disk and close it.

    Intended to be the last call in a chart cell.  The corresponding
    prose cell reads the file back independently::

        # Chart cell
        fig, ax = plt.subplots(figsize=FIGSIZE["wide"])
        ...
        save_fig(fig, cfg.img_dir / "my_chart.png")

        # Prose cell
        chart = mo.image(src=(cfg.img_dir / "my_chart.png").read_bytes())
        mo.md(f"# Insight-driven title\\n\\n{chart}")
    """
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    if close:
        plt.close(fig)
