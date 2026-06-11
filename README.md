# PyLap (an unsupported experimental fork)

A Python 3 wrapper for the PHaRLAP ionospheric raytracer.

> **Warning:** PyLap is based on the scientific software PHaRLAP and is not meant for operational use as stated on PHaRLAP's website. Any and all risk falls to you if you are using this software.

## About this fork of a fork
This is my attempt at getting the 4.7.4-support fork to actually work correctly on more recent python versions (e.g. 3.13), and just work in general. There's lots of issues with the fork that mean it probably only works in very specific use-cases.

Some problems I initially encountered:
* Use of packages which are removed in Python 3.13 (e.g. cgi)
* Older versions assumed Numpy <2.0
* Lots of references to IRI versions (2007, 2012) that aren't in PHaRLAP anymore
* The examples and wrappers mixed legacy IRI names with PHaRLAP 4.7.4's IRI-2020 library.
* Incorrect calls into the IRI-2020 wrapper, breaking things.

I am unapologetically attacking this with Codex, in part as an experiment to see if I can use an LLM for something useful.

Main initial aims are:
* Support Python 3.9 or newer
* Support the last Numpy 1.x release as well as Numpy >2.0
* Make the examples work.
* Try and rearrange the repository to more closely align with modern python packaging conventions (if this is possible), and avoid having to set up very specific environment variables for it to work.

Consider this repository to be broken unless this readme gets updated to say otherwise, and consider everything below to probably be wrong in various ways.


## Requirements

- **OS:** Ubuntu/Debian Linux (x86_64), WSL2 on Windows 10/11, macOS (arm64 or x86_64)
- **Python:** 3.9+
- **NumPy:** 1.26.4 or 2.x
- **PHaRLAP:** 4.7.4 required for raytracing (request access from DST Australia — see below)
- **gfortran:** Required to build PyLap — `apt install gfortran` on Linux, `brew install gcc` on macOS. Intel Fortran is **not** required (removed in this fork).
- **parfor/Ray:** Required only for parallel ionosphere generation with `num_workers > 1` or `--iono-workers`; installed by `requirements.txt`.


## Manual Setup

### 1. Obtain PHaRLAP

PHaRLAP is **not** redistributed with this repo — you must obtain it separately.

**PHaRLAP 4.7.4** (required for raytracing):
- Request access at https://www.dst.defence.gov.au/our-technologies/pharlap-provision-high-frequency-raytracing-laboratory-propagation-studies
- License restricts use to research; see PHaRLAP's own license terms
- After extracting, verify `lib/` contains `linux/`, `maca/`, `maci/` subdirectories (these hold the static libraries this fork links against)

Suggested layout:

```
~/pylap_project/
├── PyLap/            # This repository
└── pharlap_4.7.4/    # PHaRLAP toolbox (from DST)
```

### 2. Install System Dependencies

```bash
# Linux
sudo apt-get install python3-pip python3-venv gfortran libqt5gui5 python3-pyqt5
sudo apt-get install libxcb-randr0-dev libxcb-xtest0-dev \
    libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev

# macOS
brew install gcc
```

### 3. Create a Virtual Environment

```bash
cd ~/pylap_project/PyLap
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 5. Build and Install PyLap

```bash
export PHARLAP_HOME=~/pylap_project/pharlap_4.7.4
python -m pip install --no-build-isolation .
```


### 6. Run Examples

```bash
# Test IRI-2020
python examples/test_iri2020.py

# Test raytracing
python examples/ray_test1.py
```



## IRI-2020 Ionosphere Model

PyLap supports IRI-2020 through PHaRLAP 4.7.4's bundled `libiri2020` library. The standalone `iri2020` Python package is not used.

### Supported Profile Types

| Profile Type | Description |
|--------------|-------------|
| `'iri2020'` | IRI-2020 model backed by PHaRLAP 4.7.4 |
| `'iri'` | Compatibility name backed by PHaRLAP 4.7.4's IRI-2020 library |
| `'firi'` | Compatibility FIRI path, backed by the available PHaRLAP 4.7.4 libraries |

### Example Usage

```python
from pylap.ionosphere import gen_iono_grid_2d as gen_iono

# Generate ionosphere using IRI-2020
iono_pf_grid, iono_pf_grid_5, collision_freq, irreg, iono_te_grid = \
    gen_iono.gen_iono_grid_2d(
        origin_lat, origin_long, R12, UT, ray_bear,
        max_range, num_range, range_inc, start_height,
        height_inc, num_heights, kp, doppler_flag, 
        'iri2020'  # Use IRI-2020
    )
```

## Contact

I'm not offering support in running this repository right now, but my email is vk5qi@rfhead.net


## Various bits from the previous fork's readme

### About this fork (from upstream repo)

This is a patched fork of [HamSCI/PyLap](https://github.com/HamSCI/PyLap) maintained for use with [hf-timestd](https://github.com/mijahauan/hf-timestd) and other HF-propagation projects. The upstream version will not build or run correctly against current PHaRLAP (4.7.4) without these patches:

- **PHaRLAP 4.7.4 support** — upstream targets 4.5.x; this fork's `setup.py` links against 4.7.4 static libraries and gracefully skips legacy IRI modules (`iri2007`, `iri2012`) when their `.a` files are absent.
- **Cross-platform builds** — adds macOS arm64 and macOS x86_64 alongside Linux x86_64 (upstream is Linux-only).
- **Unified gfortran build** — Intel Fortran redistributable is no longer required; Linux and macOS both build against gfortran, eliminating a significant install-time hurdle.
- **GCC 14+ compatibility** — adds `-Wno-error=incompatible-pointer-types` so builds succeed on Debian 13/trixie and other distros that ship GCC 14 (which promotes this warning to an error).
- **Multi-hop stride fix in `raytrace_2d.c`** — the `ray_data` C-array hop stride was `num_rays × 9`; corrected to `num_rays × 24` so fields past hop 0 are read from the right offsets under PHaRLAP 4.7.4.
- **`iri2020` module wraps IRI-2020** — PHaRLAP 4.7.4 ships IRI-2020 as the supported IRI implementation, and the Python wrapper now exposes it under the same name.
- **Fortran SAVE-variable segfault workaround (caller-side note)** — repeated `raytrace_2d` calls can crash due to persistent Fortran state; make a single call with `nhops=max_hops` and iterate hops in Python.
- **Ne unit convention (caller-side note)** — IRI-2020 returns electron density in m⁻³ but `raytrace_2d` expects cm⁻³; scale by 10⁻⁶ before passing the grid.
