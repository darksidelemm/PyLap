#!/usr/bin/env python3
"""Smoke-test the PHaRLAP-backed IRI-2020 wrapper."""

import numpy as np

from pylap.iri2020 import iri2020


def main():
    lat = 40.0
    lon = -75.0
    ut = [2024, 6, 21, 12, 0]
    r12 = 60
    alt_min = 100
    alt_step = 5
    num_heights = 101

    print("Running PHaRLAP IRI-2020 for:")
    print(f"  Location: {lat} N, {lon} E")
    print(f"  Time: {ut}")
    print(
        f"  Heights: {alt_min} - "
        f"{alt_min + (num_heights - 1) * alt_step} km "
        f"(step: {alt_step} km)"
    )
    print()

    iono, _extra = iri2020(lat, lon, r12, ut, alt_min, alt_step, num_heights, {})
    heights = alt_min + np.arange(num_heights) * alt_step
    ne = iono[0].copy()
    ne[ne < 0] = np.nan

    f2_idx = np.nanargmax(ne)
    f2_height = heights[f2_idx]
    f2_density = ne[f2_idx]
    fp_f2 = 9e-6 * np.sqrt(f2_density)

    print("Results:")
    print(f"  F2 peak height: {f2_height:.1f} km")
    print(f"  F2 peak density: {f2_density:.2e} electrons/m^3")
    print(f"  F2 critical frequency (foF2): {fp_f2:.2f} MHz")


if __name__ == "__main__":
    main()
