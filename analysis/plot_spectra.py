"""Plot a time series of SuperLite spectra, stacked with vertical offsets.

Each snapshot is a SuperLite output folder (with `output.flx_grid` and
`output.flx_luminos`). Spectra are normalized by their median and plotted as
log10(F_lambda) + offset, earliest epoch at the top.

Examples
--------
    python plot_spectra.py run/day_5 run/day_10 run/day_20 --labels 5d 10d 20d
    python plot_spectra.py run/day_* --lines -o spectra.pdf
    python plot_spectra.py run/day_5 run/day_20 run/day_60 --offsets 3 1.5 0
"""
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from sncsm_io import nearest_index, read_superlite

# A few common optical lines [A] to mark with --lines
LINES = {
    "Ca II H&K": 3945.0, "Mg II": 4481.0, "Fe II": 5169.0, "He I": 5876.0,
    "Si II": 6355.0, r"H$\alpha$": 6563.0, "O I": 7774.0, "Ca II NIR": 8579.0,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("snapshots", nargs="+", help="SuperLite snapshot folders, earliest first")
    ap.add_argument("--labels", nargs="+", help="epoch labels (default: folder names)")
    ap.add_argument("--offset", type=float, default=1.0, help="even vertical spacing in log flux (default 1.0)")
    ap.add_argument("--offsets", nargs="+", type=float, help="explicit offset per spectrum (overrides --offset)")
    ap.add_argument("--xlim", nargs=2, type=float, default=(2000, 9000), help="wavelength range [A]")
    ap.add_argument("--lines", action="store_true", help="mark common optical lines")
    ap.add_argument("--title", default="")
    ap.add_argument("-o", "--output", default="spectra.pdf")
    args = ap.parse_args()

    labels = args.labels or [os.path.basename(os.path.normpath(s)) for s in args.snapshots]
    if len(labels) != len(args.snapshots):
        ap.error("give one label per snapshot")

    fig, ax = plt.subplots(figsize=(10, 11))
    n = len(args.snapshots)
    if args.offsets and len(args.offsets) != n:
        ap.error("give one offset per snapshot")
    offsets = args.offsets or [(n - 1 - i) * args.offset for i in range(n)]
    for i, (snap, label) in enumerate(zip(args.snapshots, labels)):
        wl, fl = read_superlite(snap)
        keep = (wl >= args.xlim[0]) & (wl <= args.xlim[1]) & (fl > 0)
        y = np.log10(fl[keep]) + offsets[i]
        ax.plot(wl[keep], y, color="k", lw=1.2)
        j = nearest_index(wl[keep], args.xlim[1] - 0.12 * (args.xlim[1] - args.xlim[0]))
        ax.text(wl[keep][j], y[j] + 0.1, label, color="red", fontsize=12, fontweight="bold")

    if args.lines:
        for name, lam in LINES.items():
            if args.xlim[0] < lam < args.xlim[1]:
                ax.axvline(lam, color="grey", ls=":", lw=1)
                ax.text(lam, 1.0, name, rotation=90, va="bottom", ha="center", fontsize=10,
                        transform=ax.get_xaxis_transform())

    ax.set_xlim(*args.xlim)
    ax.set_xlabel(r"Rest wavelength [$\mathrm{\AA}$]", fontsize=18)
    ax.set_ylabel(r"Normalized $\log_{10} F_\lambda$ + const", fontsize=18)
    if args.title:
        ax.set_title(args.title, fontsize=16, pad=40 if args.lines else 6)
    ax.minorticks_on()
    fig.tight_layout()
    fig.savefig(args.output, dpi=300)
    print("saved", args.output)


if __name__ == "__main__":
    main()
