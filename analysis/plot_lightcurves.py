"""Plot STELLA bolometric light curves, optionally next to the density profiles.

Each model is a folder containing `mesa.lbol` (directly or in `stella_output/`)
and, for --density, the `mesa.hyd` STELLA input it was run from.

Examples
--------
    python plot_lightcurves.py runs/no_csm runs/wind runs/shell \
        --labels "No CSM" "Wind" "Shell" -o lightcurves.pdf

    python plot_lightcurves.py runs/no_csm runs/wind --density -o den_lc.pdf
"""
import argparse
import os

import matplotlib.pyplot as plt

from sncsm_io import read_hyd, read_lbol


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("models", nargs="+", help="model folders (or mesa.lbol files)")
    ap.add_argument("--labels", nargs="+", help="legend labels (default: folder names)")
    ap.add_argument("--density", action="store_true", help="add a density-profile panel from mesa.hyd")
    ap.add_argument("--xlim", nargs=2, type=float, metavar=("TMIN", "TMAX"), help="time range [days]")
    ap.add_argument("--ylim", nargs=2, type=float, metavar=("LMIN", "LMAX"), help="log L range")
    ap.add_argument("-o", "--output", default="lightcurves.pdf")
    args = ap.parse_args()

    labels = args.labels or [os.path.basename(os.path.normpath(m)) for m in args.models]
    if len(labels) != len(args.models):
        ap.error("give one label per model")

    if args.density:
        fig, (ax_d, ax_l) = plt.subplots(1, 2, figsize=(14, 6))
    else:
        fig, ax_l = plt.subplots(figsize=(8, 6))

    for model, label in zip(args.models, labels):
        t, log_l = read_lbol(model)
        line, = ax_l.plot(t, log_l, lw=2, label=label)
        if args.density:
            hyd = read_hyd(model)
            ax_d.loglog(hyd["radius"], hyd["density"], lw=1.5, color=line.get_color(), label=label)

    ax_l.set_xlabel("Time since explosion [days]", fontsize=14)
    ax_l.set_ylabel(r"$\log_{10} L_{\rm bol}$ [erg s$^{-1}$]", fontsize=14)
    if args.xlim:
        ax_l.set_xlim(*args.xlim)
    if args.ylim:
        ax_l.set_ylim(*args.ylim)
    else:  # hide the start-up transient at t ~ 0 that STELLA writes
        top = max(line.get_ydata().max() for line in ax_l.get_lines())
        ax_l.set_ylim(top - 3.5, top + 0.3)
    ax_l.minorticks_on()
    ax_l.legend(fontsize=11)

    if args.density:
        ax_d.set_xlabel("Radius [cm]", fontsize=14)
        ax_d.set_ylabel(r"Density [g cm$^{-3}$]", fontsize=14)
        ax_d.legend(fontsize=11)

    fig.tight_layout()
    fig.savefig(args.output, dpi=300)
    print("saved", args.output)


if __name__ == "__main__":
    main()
