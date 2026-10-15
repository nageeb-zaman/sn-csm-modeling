"""Compare a model band light curve with observed supernovae.

The model magnitude comes from a STELLA `mesa.tt` file. Each observed light
curve is a whitespace-separated table with a header, a `Time` column (days),
and a magnitude column for the band (e.g. `R` or `r`). Apparent magnitudes
are converted to absolute with the luminosity distance you give. All curves
are shifted so t = 0 is at peak brightness.

Example
-------
    python plot_lightcurve_vs_observed.py runs/model \
        --obs data/snA_lc.txt 66 --obs data/snB_lc.txt 150 \
        --band R --model-label "Model" -o lc_vs_obs.pdf
"""
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from sncsm_io import absolute_mag, read_band_mag, read_observed_lc

MARKERS = ["o", "s", "^", "<", ">", "D", "p", "v", "h", "*"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", help="model folder (or mesa.tt file)")
    ap.add_argument("--obs", nargs=2, action="append", metavar=("FILE", "DIST_MPC"), required=True,
                    help="observed light curve and its luminosity distance in Mpc (repeatable)")
    ap.add_argument("--obs-labels", nargs="+", help="legend labels (default: file names)")
    ap.add_argument("--band", default="R", help="band column in the observed files (default R)")
    ap.add_argument("--tt-column", type=int, default=11, help="band column in mesa.tt (default 11 = R)")
    ap.add_argument("--model-label", default="Model")
    ap.add_argument("--xlim", nargs=2, type=float, default=(-40, 150))
    ap.add_argument("--ylim", nargs=2, type=float, default=(-12, -20), help="magnitude range (bright end second)")
    ap.add_argument("-o", "--output", default="lightcurve_vs_observed.pdf")
    args = ap.parse_args()

    labels = args.obs_labels or [os.path.basename(f).split("_")[0] for f, _ in args.obs]
    if len(labels) != len(args.obs):
        ap.error("give one label per --obs")

    fig, ax = plt.subplots(figsize=(10, 8))

    t, mag = read_band_mag(args.model, column=args.tt_column)
    ax.plot(t - t[np.argmin(mag)], mag, "-", lw=3, color="k", label=args.model_label)

    for i, ((path, dist), label) in enumerate(zip(args.obs, labels)):
        t_obs, m_obs = read_observed_lc(path, band=args.band)
        t_peak = t_obs[np.nanargmin(m_obs)]
        ax.plot(t_obs - t_peak, absolute_mag(m_obs, float(dist)), MARKERS[i % len(MARKERS)],
                ms=6, label=label)

    ax.set_xlabel("Rest-frame phase since maximum [days]", fontsize=16)
    ax.set_ylabel(f"Absolute {args.band} magnitude [mag]", fontsize=16)
    ax.set_xlim(*args.xlim)
    ax.set_ylim(*args.ylim)
    ax.minorticks_on()
    ax.tick_params(labelsize=13)
    ax.legend(fontsize=13)
    fig.tight_layout()
    fig.savefig(args.output, dpi=300)
    print("saved", args.output)


if __name__ == "__main__":
    main()
