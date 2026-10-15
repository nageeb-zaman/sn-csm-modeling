"""Fit a blackbody to SuperLite spectra to get temperature and photospheric radius.

Fits L_lambda = 4 pi R^2 * pi B_lambda(T) to the specific luminosity of each
snapshot. Prints T and R with 1-sigma errors, and with --table writes them to
a text file. With --plot, saves one figure per snapshot showing the fit.

Example
-------
    python fit_blackbody.py run/day_5 run/day_10 run/day_20 \
        --labels 5 10 20 --table bb_fits.txt --plot
"""
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
from astropy import constants as const
from scipy.optimize import curve_fit

from sncsm_io import read_superlite

H = const.h.cgs.value
C = const.c.cgs.value
K_B = const.k_B.cgs.value


def blackbody_lambda(lam_A, T, R):
    """Specific luminosity [erg/s/A] of a sphere of radius R [cm] at temperature T [K]."""
    lam = lam_A * 1e-8
    b_lam = (2.0 * H * C**2) / lam**5 / np.expm1(H * C / (lam * K_B * T)) * 1e-8
    return 4.0 * np.pi * R**2 * np.pi * b_lam


def fit(wl, lum, T_guess=12000.0, R_guess=1e14):
    popt, pcov = curve_fit(blackbody_lambda, wl, lum, p0=[T_guess, R_guess], maxfev=20000)
    return popt, np.sqrt(np.diag(pcov))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("snapshots", nargs="+", help="SuperLite snapshot folders")
    ap.add_argument("--labels", nargs="+", help="epoch labels (default: folder names)")
    ap.add_argument("--table", help="write results to this text file")
    ap.add_argument("--plot", action="store_true", help="save a fit plot per snapshot")
    args = ap.parse_args()

    labels = args.labels or [os.path.basename(os.path.normpath(s)) for s in args.snapshots]
    if len(labels) != len(args.snapshots):
        ap.error("give one label per snapshot")

    rows = []
    for snap, label in zip(args.snapshots, labels):
        wl, lum = read_superlite(snap, normalize=False)
        (T, R), (dT, dR) = fit(wl, lum)
        rows.append((label, T, dT, R, dR))
        print(f"{label:>10s}  T = {T:8.1f} ± {dT:6.1f} K   R = {R:.3e} ± {dR:.1e} cm")

        if args.plot:
            fig, ax = plt.subplots(figsize=(9, 6))
            ax.plot(wl, lum, color="k", lw=1, label=f"Model {label}")
            ax.plot(wl, blackbody_lambda(wl, T, R), "r-", label=f"Blackbody, T = {T:.0f} K")
            ax.set_xlabel(r"Wavelength [$\mathrm{\AA}$]", fontsize=14)
            ax.set_ylabel(r"$L_\lambda$ [erg s$^{-1}$ $\mathrm{\AA}^{-1}$]", fontsize=14)
            ax.set_xlim(1000, 20000)
            ax.legend()
            fig.tight_layout()
            fig.savefig(f"bb_fit_{label}.png", dpi=200)
            plt.close(fig)

    if args.table:
        with open(args.table, "w") as f:
            f.write("# label  T[K]  T_err[K]  R[cm]  R_err[cm]\n")
            for r in rows:
                f.write("%s  %.1f  %.1f  %.4e  %.4e\n" % r)
        print("wrote", args.table)


if __name__ == "__main__":
    main()
