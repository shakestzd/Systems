"""Smoke tests for src/plotting.py — verify all public symbols are importable."""

import src.plotting as plotting


def test_site_tokens_exported():
    """New site identity tokens are importable from the plotting shim."""
    import flowmpl

    assert plotting.PAPER == flowmpl.PAPER
    assert plotting.INK == flowmpl.INK
    assert plotting.INK_MID == flowmpl.INK_MID
    assert plotting.INK_LIGHT == flowmpl.INK_LIGHT
    assert plotting.RULE == flowmpl.RULE


def test_helper_functions_exported():
    """New helper functions are importable from the plotting shim."""
    import inspect

    assert callable(plotting.add_source)
    assert callable(plotting.add_rule)
    assert "fig" in inspect.signature(plotting.add_source).parameters
    assert "ax" in inspect.signature(plotting.add_rule).parameters


def test_all_declared_symbols_importable():
    """Every symbol listed in __all__ can be retrieved from the module."""
    for name in plotting.__all__:
        assert hasattr(plotting, name), f"'{name}' is in __all__ but not importable"


def test_events_exported():
    """Events catalog and mark_events are importable from the plotting shim."""
    import inspect
    from datetime import date

    assert hasattr(plotting, "EVENTS")
    assert hasattr(plotting, "Event")
    assert callable(plotting.mark_events)

    # EVENTS is a non-empty list of Event objects
    assert len(plotting.EVENTS) > 0
    first = plotting.EVENTS[0]
    assert isinstance(first.date, date)
    assert first.category in {"policy", "market", "announcement", "regulatory", "energy"}

    # mark_events accepts ax and categories keyword
    assert "ax" in inspect.signature(plotting.mark_events).parameters
    assert "categories" in inspect.signature(plotting.mark_events).parameters


def test_add_brand_mark_exported():
    """add_brand_mark is callable and accepts fig + logo_path."""
    import inspect

    assert callable(plotting.add_brand_mark)
    sig = inspect.signature(plotting.add_brand_mark)
    assert "fig" in sig.parameters
    assert "logo_path" in sig.parameters
