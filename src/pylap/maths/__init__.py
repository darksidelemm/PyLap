"""Math helper modules for PyLap."""

from importlib import import_module

_ALIASES = {
    "ENU2xyz": "enu2xyz",
    "xyz2ENU": "xyz2enu",
    "doStuff": "do_stuff",
}

__all__ = [
    "chapman", "coning", "deriv", "do_stuff", "earth_radius_wgs84",
    "eff_coll_freq", "eff_coll_freq_ion", "eff_coll_freq_neutrals",
    "enu2xyz", "gm_freq_offset", "iri2020_firi_interp", "julday",
    "land_sea", "latlon2raz", "pol_power_coupling", "raz2latlon",
    "relaz2xyz", "solar_za", "wgs842gc_lat", "wgs84_llh2xyz",
    "wgs84_xyz2llh", "wrapped", "xyz2elaz", "xyz2enu",
    *_ALIASES,
]


def __getattr__(name):
    module_name = _ALIASES.get(name, name)
    if module_name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(f"{__name__}.{module_name}")
    globals()[name] = module
    return module
