#!/usr/bin/env python3
"""Benchmark 2D ionosphere generation and numerical raytracing."""

import argparse
import time

import numpy as np

from pylap.ionosphere import gen_iono_grid_2d as gen_iono
from pylap.raytrace_2d import raytrace_2d


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a 2D ionosphere and trace a fan of rays. Defaults are "
            "based on the first ray_test1.py example."
        )
    )
    parser.add_argument(
        "--num-rays",
        type=int,
        default=1000,
        help="Number of elevation rays to trace. Default: 1000.",
    )
    parser.add_argument(
        "--min-elevation",
        type=float,
        default=2.0,
        help="Minimum launch elevation in degrees. Default: 2.",
    )
    parser.add_argument(
        "--max-elevation",
        type=float,
        default=62.0,
        help="Maximum launch elevation in degrees. Default: 62.",
    )
    parser.add_argument(
        "--frequency-mhz",
        type=float,
        default=15.0,
        help="Ray frequency in MHz. Default: 15.",
    )
    parser.add_argument(
        "--nhops",
        type=int,
        default=1,
        help="Number of hops to raytrace. Default: 1.",
    )
    parser.add_argument(
        "--profile-type",
        default="iri2020",
        help="Ionospheric profile model. Default: iri2020.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.num_rays < 1:
        raise ValueError("--num-rays must be at least 1")

    ut = [2026, 3, 15, 7, 0]
    r12 = 100
    ray_bear = 324.7
    origin_lat = -23.5
    origin_long = 133.7
    tol = [1e-7, 0.01, 10]
    irregs_flag = 0
    kp = 0
    doppler_flag = 1

    max_range = 10000
    num_range = 201
    range_inc = max_range / (num_range - 1)
    start_height = 0
    height_inc = 3
    num_heights = 201
    iri_options = {"Ne_B0B1_model": "Bil-2000"}

    elevs = np.linspace(
        args.min_elevation, args.max_elevation, args.num_rays, dtype=float
    )
    freqs = args.frequency_mhz * np.ones(elevs.size, dtype=float)

    print("2D raytrace benchmark")
    print(f"  rays: {elevs.size}")
    print(f"  elevation range: {args.min_elevation:g}..{args.max_elevation:g} deg")
    print(f"  frequency: {args.frequency_mhz:g} MHz")
    print(f"  hops: {args.nhops}")
    print(f"  profile: {args.profile_type}")

    iono_start = time.perf_counter()
    iono_pf_grid, iono_pf_grid_5, collision_freq, irreg, _iono_te_grid = (
        gen_iono.gen_iono_grid_2d(
            origin_lat,
            origin_long,
            r12,
            ut,
            ray_bear,
            max_range,
            num_range,
            range_inc,
            start_height,
            height_inc,
            num_heights,
            kp,
            doppler_flag,
            args.profile_type,
            iri_options,
        )
    )
    ionosphere_seconds = time.perf_counter() - iono_start

    iono_en_grid = iono_pf_grid**2 / 80.6164e-6
    iono_en_grid_5 = iono_pf_grid_5**2 / 80.6164e-6

    trace_start = time.perf_counter()
    raytrace_2d(
        origin_lat,
        origin_long,
        elevs,
        ray_bear,
        freqs,
        args.nhops,
        tol,
        irregs_flag,
        iono_en_grid,
        iono_en_grid_5,
        collision_freq,
        start_height,
        height_inc,
        range_inc,
        irreg,
    )
    raytrace_seconds = time.perf_counter() - trace_start

    total_seconds = ionosphere_seconds + raytrace_seconds
    print("")
    print(f"  ionosphere generation: {ionosphere_seconds:.3f} s")
    print(f"  raytracing:            {raytrace_seconds:.3f} s")
    print(f"  total:                 {total_seconds:.3f} s")
    print(f"  raytrace throughput:   {elevs.size / raytrace_seconds:.1f} rays/s")


if __name__ == "__main__":
    main()
