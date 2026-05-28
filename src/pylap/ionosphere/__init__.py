"""Ionosphere grid generators for PyLap."""

from importlib import import_module

__all__ = ["gen_iono_grid_2d", "gen_iono_grid_3d", "gen_SAMI3_iono_grid_2d"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(f"{__name__}.{name}")
    globals()[name] = module
    return module
