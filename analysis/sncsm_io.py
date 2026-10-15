"""Readers for STELLA, MESA/STELLA hydro, SuperLite, and observed data.

All plotting scripts in this folder use these functions, so file-format
details live in one place.
"""
import os

import numpy as np
import pandas as pd

ANGSTROM_PER_CM = 1.0e8
PC_IN_CM = 3.0856775814913673e18
L_SUN = 3.828e33  # erg/s


# --------------------------------------------------------------------------
# STELLA
# --------------------------------------------------------------------------
def find_file(path, name):
    """Return `path` if it is a file, else look for `name` in path or path/stella_output."""
    if os.path.isfile(path):
        return path
    for cand in (os.path.join(path, name), os.path.join(path, "stella_output", name)):
        if os.path.isfile(cand):
            return cand
    raise FileNotFoundError(f"No {name} found at {path} or {path}/stella_output")


def read_lbol(path):
    """Bolometric light curve from a STELLA `mesa.lbol` file.

    Returns time [days] and log10 L_bol [erg/s].
    """
    f = find_file(path, "mesa.lbol")
    t, log_l = np.loadtxt(f, usecols=(0, 2), skiprows=1, unpack=True)
    return t, log_l


def read_band_mag(path, column=11, skiprows=63):
    """Absolute magnitude in one band from a STELLA `mesa.tt` file.

    `column` selects the band (11 = R in the standard STELLA .tt layout);
    `skiprows` skips the .tt header.
    Returns time [days] and absolute magnitude.
    """
    f = find_file(path, "mesa.tt")
    t, mag = np.loadtxt(f, usecols=(0, column), skiprows=skiprows, unpack=True)
    return t, mag


def read_hyd(path):
    """Hydro profile from a STELLA input `mesa.hyd` file (ejecta + any CSM).

    Returns a dict with mass [Msun], radius [cm], density [g/cm^3],
    temperature [K], velocity [cm/s].
    """
    f = find_file(path, "mesa.hyd")
    m, r, rho, T, v = np.loadtxt(f, usecols=(1, 2, 3, 4, 5), skiprows=1, unpack=True)
    return {"mass": m, "radius": r, "density": rho, "temperature": T, "velocity": v}


# --------------------------------------------------------------------------
# SuperLite
# --------------------------------------------------------------------------
def read_superlite(snapshot_dir, normalize=True):
    """Spectrum from one SuperLite snapshot folder.

    Reads `output.flx_grid` and `output.flx_luminos` in `snapshot_dir`.
    normalize=True : flux at 10 pc, divided by its median non-zero value
                     (for comparing spectral shapes).
    normalize=False: specific luminosity L_lambda [erg/s/A] (for blackbody fits).
    Returns wavelength [A] and flux arrays.
    """
    grid = pd.read_csv(os.path.join(snapshot_dir, "output.flx_grid"))
    edges = np.array([float(x) for x in grid.iloc[0, 0].split()]) * ANGSTROM_PER_CM
    dwl = np.diff(edges)

    lum = np.loadtxt(os.path.join(snapshot_dir, "output.flx_luminos"))
    flux = lum / dwl
    if normalize:
        flux = flux / (4.0 * np.pi * (10.0 * PC_IN_CM) ** 2)
        nonzero = flux[flux != 0.0]
        flux = flux / np.median(nonzero)

    # flux[i] belongs to the bin starting at edges[i]
    return edges[: len(flux)], flux


# --------------------------------------------------------------------------
# Observations
# --------------------------------------------------------------------------
def read_observed_spectrum(path, z=0.0):
    """Two-column (wavelength [A], flux) spectrum, shifted to rest frame and
    normalized by its median."""
    wl, fl = np.loadtxt(path, usecols=(0, 1), unpack=True)
    return wl / (1.0 + z), fl / np.median(fl)


def read_observed_lc(path, band="R"):
    """Whitespace-separated light curve with a header row.

    Needs a `Time` column and a column named after the band (case-insensitive
    fallback, e.g. `R` or `r`). Returns time [days] and apparent magnitude.
    """
    data = pd.read_csv(path, header=0, sep=r"\s+", engine="python")
    col = band if band in data.columns else next(
        (c for c in data.columns if c.lower() == band.lower()), None)
    if col is None:
        raise KeyError(f"{path}: no '{band}' column (have {list(data.columns)})")
    return data["Time"].to_numpy(float), data[col].to_numpy(float)


def absolute_mag(m_app, distance_mpc):
    """Apparent to absolute magnitude for a luminosity distance in Mpc."""
    return m_app - 5.0 * np.log10(distance_mpc * 1.0e6 / 10.0)


def nearest_index(array, value):
    return int(np.abs(np.asarray(array) - value).argmin())
