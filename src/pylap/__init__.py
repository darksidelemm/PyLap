"""Python interface to PHaRLAP.

Only ``PHARLAP_HOME`` needs to be set by the caller.  The PHaRLAP reference
data directory is always the ``dat`` subdirectory, so derive it automatically
unless the caller has explicitly provided ``DIR_MODELS_REF_DAT``.
"""

from importlib import import_module
import os
from pathlib import Path


def configure_pharlap(pharlap_home=None):
    """Configure PHaRLAP-related environment variables for this process."""
    if pharlap_home is not None:
        os.environ["PHARLAP_HOME"] = str(pharlap_home)

    pharlap_home = os.environ.get("PHARLAP_HOME")
    if pharlap_home and "DIR_MODELS_REF_DAT" not in os.environ:
        os.environ["DIR_MODELS_REF_DAT"] = str(Path(pharlap_home) / "dat")

    return pharlap_home


configure_pharlap()

_NATIVE_MODULES = {
    "abso_bg", "dop_spread_eq", "ground_bs_loss", "ground_fs_loss",
    "igrf2007", "igrf2011", "igrf2016",
    "iri2007", "iri2012", "iri2020",
    "irreg_strength", "nrlmsise00",
    "raytrace_2d", "raytrace_2d_sp",
    "raytrace_3d", "raytrace_3d_sp",
}

__all__ = ["configure_pharlap", *_NATIVE_MODULES]


def __getattr__(name):
    if name not in _NATIVE_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(f"{__name__}.{name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
