#!/usr/bin/env python3
"""Benchmark 3D ionosphere generation and numerical raytracing."""

import argparse
import math
import time

import numpy as np

from pylap.ionosphere import gen_iono_grid_3d as gen_iono
from pylap.raytrace_3d import raytrace_3d


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a 3D ionosphere and trace a fan of rays over elevation "
            "and azimuth. Defaults are based on ray_test_3d.py."
        )
    )
    parser.add_argument(
        "--num-rays",
        type=int,
        default=1000,
        help=(
            "Target number of rays. Used when --num-elevations and "
            "--num-azimuths are not both supplied. Default: 1000."
        ),
    )
    parser.add_argument(
        "--num-elevations",
        type=int,
        default=None,
        help="Number of elevation samples. Default: derived from --num-rays.",
    )
    parser.add_argument(
        "--num-azimuths",
        type=int,
        default=None,
        help="Number of azimuth samples. Default: derived from --num-rays.",
    )
    parser.add_argument(
        "--min-elevation",
        type=float,
        default=3.0,
        help="Minimum launch elevation in degrees. Default: 3.",
    )
    parser.add_argument(
        "--max-elevation",
        type=float,
        default=82.0,
        help="Maximum launch elevation in degrees. Default: 82.",
    )
    parser.add_argument(
        "--min-azimuth",
        type=float,
        default=-3.0,
        help="Minimum launch bearing offset in degrees. Default: -3.",
    )
    parser.add_argument(
        "--max-azimuth",
        type=float,
        default=3.0,
        help="Maximum launch bearing offset in degrees. Default: 3.",
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
        default=4,
        help="Number of hops to raytrace. Default: 4.",
    )
    parser.add_argument(
        "--mode",
        choices=["o", "x", "no-field"],
        default="o",
        help="Magneto-ionic ray mode. Default: o.",
    )
    parser.add_argument(
        "--profile-type",
        default="iri2020",
        help="Ionospheric profile model. Default: iri2020.",
    )
    return parser.parse_args()


def sample_counts(args):
    if args.num_rays < 1:
        raise ValueError("--num-rays must be at least 1")

    if args.num_elevations is not None and args.num_elevations < 1:
        raise ValueError("--num-elevations must be at least 1")
    if args.num_azimuths is not None and args.num_azimuths < 1:
        raise ValueError("--num-azimuths must be at least 1")

    if args.num_elevations is not None and args.num_azimuths is not None:
        return args.num_elevations, args.num_azimuths

    if args.num_elevations is not None:
        return args.num_elevations, math.ceil(args.num_rays / args.num_elevations)

    if args.num_azimuths is not None:
        return math.ceil(args.num_rays / args.num_azimuths), args.num_azimuths

    num_azimuths = math.ceil(math.sqrt(args.num_rays))
    num_elevations = math.ceil(args.num_rays / num_azimuths)
    return num_elevations, num_azimuths


def ray_mode(mode):
    if mode == "o":
        return 1
    if mode == "x":
        return -1
    return 0


def main():
    args = parse_args()
    num_elevations, num_azimuths = sample_counts(args)

    ut = [2000, 9, 21, 0, 0]
    r12 = 100
    origin_lat = -20.0
    origin_long = 130.0
    origin_ht = 0.0
    doppler_flag = 1
    tol = [1e-7, 0.01, 25]

    ht_start = 60
    ht_inc = 2
    num_ht = 201
    lat_start = -20.0
    lat_inc = 0.3
    num_lat = 101
    lon_start = 128.0
    lon_inc = 1.0
    num_lon = 5
    iono_grid_parms = [
        lat_start,
        lat_inc,
        num_lat,
        lon_start,
        lon_inc,
        num_lon,
        ht_start,
        ht_inc,
        num_ht,
    ]

    b_ht_start = ht_start
    b_ht_inc = 10
    b_num_ht = math.ceil(num_ht * ht_inc / b_ht_inc)
    b_lat_start = lat_start
    b_lat_inc = 1.0
    b_num_lat = math.ceil(num_lat * lat_inc / b_lat_inc)
    b_lon_start = lon_start
    b_lon_inc = 1.0
    b_num_lon = math.ceil(num_lon * lon_inc / b_lon_inc)
    geomag_grid_parms = [
        b_lat_start,
        b_lat_inc,
        b_num_lat,
        b_lon_start,
        b_lon_inc,
        b_num_lon,
        b_ht_start,
        b_ht_inc,
        b_num_ht,
    ]

    elevations = np.linspace(
        args.min_elevation, args.max_elevation, num_elevations, dtype=float
    )
    azimuths = np.linspace(args.min_azimuth, args.max_azimuth, num_azimuths)
    az_grid, elev_grid = np.meshgrid(azimuths, elevations)
    elevs = elev_grid.ravel()[: args.num_rays]
    ray_bears = az_grid.ravel()[: args.num_rays]
    freqs = args.frequency_mhz * np.ones(elevs.size, dtype=float)

    print("3D raytrace benchmark")
    print(f"  rays: {elevs.size}")
    print(f"  elevation samples: {num_elevations}")
    print(f"  azimuth samples: {num_azimuths}")
    print(f"  elevation range: {args.min_elevation:g}..{args.max_elevation:g} deg")
    print(f"  azimuth range: {args.min_azimuth:g}..{args.max_azimuth:g} deg")
    print(f"  frequency: {args.frequency_mhz:g} MHz")
    print(f"  hops: {args.nhops}")
    print(f"  mode: {args.mode}")
    print(f"  profile: {args.profile_type}")

    iono_start = time.perf_counter()
    iono_pf_grid, iono_pf_grid_5, collision_freq, bx, by, bz = (
        gen_iono.gen_iono_grid_3d(
            ut,
            r12,
            iono_grid_parms,
            geomag_grid_parms,
            doppler_flag,
            profile_type=args.profile_type,
        )
    )
    ionosphere_seconds = time.perf_counter() - iono_start

    iono_en_grid = iono_pf_grid**2 / 80.6164e-6
    iono_en_grid_5 = iono_pf_grid_5**2 / 80.6164e-6

    trace_start = time.perf_counter()
    raytrace_3d(
        origin_lat,
        origin_long,
        origin_ht,
        elevs,
        ray_bears,
        freqs,
        ray_mode(args.mode),
        args.nhops,
        tol,
        iono_en_grid,
        iono_en_grid_5,
        collision_freq,
        iono_grid_parms,
        bx,
        by,
        bz,
        geomag_grid_parms,
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
