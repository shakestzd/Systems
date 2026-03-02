"""Structural events catalog for temporal chart annotations.

Single source of truth for structural inflection points across all deep dives.
Replaces ad-hoc in-notebook event annotations.

Usage:
    from src.data.events import EVENTS, mark_events
    mark_events(ax, categories=["announcement", "policy"])
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import matplotlib.pyplot as plt


@dataclass
class Event:
    date: date
    label: str
    category: str   # "policy" | "market" | "announcement" | "regulatory" | "energy"
    short_label: str = field(default="")


EVENTS: list[Event] = [
    # ── Technology milestones ────────────────────────────────────────────────
    Event(date(2022, 11, 30), "ChatGPT Launch",                       "announcement", "ChatGPT"),
    Event(date(2025,  1, 27), "DeepSeek R1 Release",                  "market",       "DeepSeek"),
    # ── Industrial policy ────────────────────────────────────────────────────
    Event(date(2022,  8,  9), "CHIPS and Science Act",                "policy",       "CHIPS Act"),
    Event(date(2022,  8, 16), "Inflation Reduction Act",              "policy",       "IRA"),
    Event(date(2025,  1, 20), "Trump Inauguration / AI EO",           "policy",       "AI EO"),
    Event(date(2025,  7,  4), "One Big Beautiful Act",                "policy",       "OBBA"),
    Event(date(2026,  1, 20), "Paris Agreement Withdrawal",           "policy",       "Paris Exit"),
    # ── FERC regulatory ──────────────────────────────────────────────────────
    Event(date(2023,  7, 28), "FERC Order 2023 (interconnection)",    "regulatory",   "FERC 2023"),
    Event(date(2024,  5, 13), "FERC Order 1920 (transmission)",       "regulatory",   "FERC 1920"),
    # ── Energy transition ────────────────────────────────────────────────────
    Event(date(2022,  3,  1), "Russia invades Ukraine / energy shock", "energy",      "Energy Shock"),
    Event(date(2024,  1,  1), "IRA clean energy credit surge",         "energy",      "IRA Deploy"),
]


def mark_events(
    ax: plt.Axes,
    categories: list[str] | None = None,
    *,
    events: list[Event] | None = None,
    color: str | None = None,
    label_color: str | None = None,
    alpha: float = 0.5,
    fontsize: int | None = None,
    y_position: float = 0.97,
    linewidth: float = 0.8,
) -> list:
    """Draw dashed vertical lines at structural events within the x-axis range.

    Parameters
    ----------
    ax : Axes
    categories : event categories to include. None = all.
        Valid values: "policy", "market", "announcement", "regulatory", "energy"
    events : override the default EVENTS catalog
    color : line color. Defaults to RULE.
    label_color : text color. Defaults to INK_LIGHT.
    alpha : line opacity. Default 0.5.
    fontsize : label font size. Defaults to FONTS["caption"].
    y_position : vertical label position in axes coords. Default 0.97 (top).
    linewidth : dashed line width. Default 0.8.

    Returns
    -------
    list of drawn matplotlib artists.

    Examples
    --------
    mark_events(ax, categories=["announcement", "policy"])
    mark_events(ax, categories=["market"])
    mark_events(ax)  # all events
    """
    import matplotlib.dates as mdates
    from flowmpl import RULE, INK_LIGHT, FONTS

    _color = color or RULE
    _label_color = label_color or INK_LIGHT
    _fontsize = fontsize or FONTS["caption"]
    _events = events if events is not None else EVENTS

    if categories is not None:
        _events = [e for e in _events if e.category in categories]

    xlim = ax.get_xlim()
    artists: list = []
    for event in _events:
        xval = mdates.date2num(event.date)
        if xlim[0] <= xval <= xlim[1]:
            line = ax.axvline(
                xval, color=_color, linewidth=linewidth,
                linestyle="--", alpha=alpha, zorder=1,
            )
            txt = ax.text(
                xval, y_position,
                event.short_label or event.label,
                transform=ax.get_xaxis_transform(),
                ha="center", va="top",
                fontsize=_fontsize, color=_label_color, rotation=90,
            )
            artists.extend([line, txt])
    return artists
