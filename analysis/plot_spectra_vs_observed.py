"""Compare SuperLite model spectra with observed spectra, epoch by epoch.

Each --pair is "MODEL_DIR,OBS_FILE,Z,LABEL": a model snapshot folder, an
observed two-column spectrum (wavelength [A], flux), the object's redshift,
and an epoch label. Pairs are stacked
earliest at the top; within each pair the observed spectrum (colored) sits
just above the model (black).

Example
-------
    python plot_spectra_vs_observed.py \
        --pair "run/day_5,obs/sn_p005.dat,0.03,5d" \
        --pair "run/day_20,obs/sn_p020.dat,0.03,20d" \
        --obs-name "SN XXXX" -o spectra_vs_obs.pdf
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np

from sncsm_io import nearest_index, read_observed_spectrum, read_superlite


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pair", action="append", required=True, metavar="MODEL_DIR,OBS_FILE,Z,LABEL",
                    help="model snapshot, observed spectrum, redshift, epoch label (repeatable)")
    ap.add_argument("--obs-name", default="Observed", help="legend name for the observed object")
    ap.add_argument("--model-name", default="Model", help="legend name for the model")
    ap.add_argument("--offset", type=float, default=1.2, help="spacing between pairs in log flux")
    ap.add_argument("--obs-shift", type=float, default=0.5, help="observed spectrum shift above model")
    ap.add_argument("--xlim", nargs=2, type=float, default=(3000, 9500), help="wavelength range [A]")
    ap.add_argument("--color", default="tab:blue", help="color of the observed spectra")
    ap.add_argument("-o", "--output", default="spectra_vs_observed.pdf")
    args = ap.parse_args()

    pairs = []
    for p in args.pair:
        parts = p.split(",")
        if len(parts) != 4:
            ap.error(f"--pair needs MODEL_DIR,OBS_FILE,Z,LABEL; got '{p}'")
        pairs.append(parts)
    args.pair = pairs

    fig, ax = plt.subplots(figsize=(10, 12))
    n = len(args.pair)
    x_label = args.xlim[1] - 0.10 * (args.xlim[1] - args.xlim[0])

    for i, (model_dir, obs_file, z, label) in enumerate(args.pair):
        base = (n - 1 - i) * args.offset

        wl, fl = read_superlite(model_dir)
        keep = (wl >= args.xlim[0]) & (wl <= args.xlim[1]) & (fl > 0)
        y = np.log10(fl[keep]) + base
        ax.plot(wl[keep], y, color="k", lw=1.2, label=args.model_name if i == 0 else None)
        j = nearest_index(wl[keep], x_label)
        ax.text(wl[keep][j], y[j] + 0.08, label, fontsize=12, fontweight="bold")

        wo, fo = read_observed_spectrum(obs_file, float(z))
        keep = (wo >= args.xlim[0]) & (wo <= args.xlim[1]) & (fo > 0)
        ax.plot(wo[keep], np.log10(fo[keep]) + base + args.obs_shift, color=args.color, lw=1.2,
                alpha=0.8, label=args.obs_name if i == 0 else None)

    ax.set_xlim(*args.xlim)
    ax.set_xlabel(r"Rest wavelength [$\mathrm{\AA}$]", fontsize=18)
    ax.set_ylabel(r"Normalized $\log_{10} F_\lambda$ + const", fontsize=18)
    ax.minorticks_on()
    ax.legend(fontsize=13, loc="upper left")
    fig.tight_layout()
    fig.savefig(args.output, dpi=300)
    print("saved", args.output)


if __name__ == "__main__":
    main()
