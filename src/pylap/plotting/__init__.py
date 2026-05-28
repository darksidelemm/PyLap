"""Plotting helpers for PyLap."""

from importlib import import_module

_ALIASES = {
    "Plot_2D_slice": "plot_2d_slice",
    "Plot_map": "plot_map",
}

__all__ = ["plot_2d_slice", "plot_map", "plot_ray_iono_slice", "plot_test", *_ALIASES]


def __getattr__(name):
    module_name = _ALIASES.get(name, name)
    if module_name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(f"{__name__}.{module_name}")
    globals()[name] = module
    return module
