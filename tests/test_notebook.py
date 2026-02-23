from pathlib import Path

import matplotlib.pyplot as plt

from src.notebook import save_fig, setup


def test_setup_returns_path_objects(monkeypatch):
    """setup() returns a NotebookConfig where all path fields are Path instances."""
    monkeypatch.setattr("src.notebook.plt.style.use", lambda *a, **kw: None)
    cfg = setup()
    assert isinstance(cfg.project_root, Path)
    assert isinstance(cfg.img_dir, Path)
    assert isinstance(cfg.data_dir, Path)
    assert isinstance(cfg.models_dir, Path)


def test_save_fig_creates_file(tmp_path):
    """save_fig() writes a PNG to the given path."""
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    out = tmp_path / "out.png"
    save_fig(fig, out)
    assert out.exists()


def test_save_fig_close_false_leaves_figure_open(tmp_path):
    """save_fig(close=False) saves the file but keeps the figure open."""
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    out = tmp_path / "out.png"
    save_fig(fig, out, close=False)
    assert plt.fignum_exists(fig.number)
    plt.close(fig)
