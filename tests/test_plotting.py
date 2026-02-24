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
