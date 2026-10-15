"""Brightness-Temperature-Timescale-Radius (BTTR) diagram.

Plots rise time (x) against peak bolometric luminosity (y, log scale). Marker
color shows the photospheric temperature and marker area scales with the
photospheric radius squared. Models are drawn with black outlines on top of
observed transients.

Inputs
------
--models TABLE   whitespace table with a header and columns
                 name  rise_time  log_peak_lum  r_phot  t_phot
                 (days, log10 erg/s, cm, K). Rows whose names share a prefix
                 before "(" (e.g. "A(-2d)", "A(peak)", "A(+4d)") are joined by
                 a line and labeled with that prefix.

Observed transients, either
--obs TABLE      same five columns, already measured, or
--extrabol-dir DIR --rise-times FILE
                 one extrabol output file per object (<name>.txt) plus a table
                 with `name` and `Rise_Time_med` columns (e.g. MOSFiT fits).
                 Peak luminosity, temperature and radius are averaged over
                 +/-5 days around the luminosity peak; --save-obs writes them to
                 a table you can reuse with --obs.

Example
-------
    python plot_bttr.py --models models_bttr.txt --obs observed_bttr.txt -o bttr.pdf
    python plot_bttr.py --models models_bttr.txt \
        --extrabol-dir extrabol/ --rise-times fit_params.txt --save-obs observed_bttr.txt
"""
import argparse
import glob
import os

import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLUMNS = ["name", "rise_time", "log_peak_lum", "r_phot", "t_phot"]
LINESTYLES = ["--", ":", "-.", "-"]


def read_table(path):
    df = pd.read_csv(path, sep=r"\s+", header=0)
    df = df.iloc[:, :5]
    df.columns = COLUMNS
    return df


def measure_extrabol(extrabol_dir, rise_file, window=5.0):
    """Peak luminosity, temperature and radius (mean within +/-window days of
    the luminosity peak) from extrabol outputs, with rise times from a table."""
    rise = pd.read_csv(rise_file, sep=r"\s+", header=0)
    rows = []
    for f in sorted(glob.glob(os.path.join(extrabol_dir, "*.txt"))):
        name = os.path.splitext(os.path.basename(f))[0]
        match = rise.loc[rise["name"].astype(str) == name, "Rise_Time_med"]
        if match.empty:
            print(f"skipping {name}: no rise time in {rise_file}")
            continue
        df = pd.read_csv(f, sep=r"\s+", header=0)
        t = df["Time (MJD)"].to_numpy()
        L = df["Log10(Bol. Lum)"].to_numpy()
        T = df["Temp./1e3 (K)"].to_numpy() * 1e3
        R = df["Radius/1e15 (cm)"].to_numpy() * 1e15

        peaks = np.where(L == np.nanmax(L))[0]
        t_peak = t[peaks[len(peaks) // 2]]          # middle one if the peak is flat
        idx = np.where((t >= t_peak - window) & (t <= t_peak + window))[0]
        sl = slice(idx[0], idx[-1])                 # same window as the original analysis
        rows.append((name, float(match.iloc[0]), L[sl].mean(), R[sl].mean(), T[sl].mean()))
    print(f"measured {len(rows)} objects from {extrabol_dir}")
    return pd.DataFrame(rows, columns=COLUMNS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", help="model table (name rise_time log_peak_lum r_phot t_phot)")
    ap.add_argument("--obs", help="observed table with the same columns")
    ap.add_argument("--extrabol-dir", help="folder of extrabol outputs, one <name>.txt per object")
    ap.add_argument("--rise-times", help="table with name and Rise_Time_med columns")
    ap.add_argument("--save-obs", help="write the measured observed table here")
    ap.add_argument("--tmin", type=float, help="color-scale minimum [10^3 K] (default: data)")
    ap.add_argument("--tmax", type=float, help="color-scale maximum [10^3 K] (default: data)")
    ap.add_argument("--size-scale", type=float, default=3000.0, help="marker area of the largest radius")
    ap.add_argument("--xlim", nargs=2, type=float, default=(0, 140))
    ap.add_argument("--ylim", nargs=2, type=float, default=(4e42, 1.2e45))
    ap.add_argument("-o", "--output", default="bttr.pdf")
    args = ap.parse_args()

    obs = None
    if args.obs:
        obs = read_table(args.obs)
    elif args.extrabol_dir:
        if not args.rise_times:
            ap.error("--extrabol-dir needs --rise-times")
        obs = measure_extrabol(args.extrabol_dir, args.rise_times)
        if args.save_obs:
            obs.to_csv(args.save_obs, sep="\t", index=False, float_format="%.4g")
            print("wrote", args.save_obs)
    models = read_table(args.models) if args.models else None
    if obs is None and models is None:
        ap.error("give --models and/or observed data")

    frames = [d for d in (obs, models) if d is not None]
    t_all = np.concatenate([d["t_phot"].to_numpy() / 1e3 for d in frames])
    vmin = args.tmin if args.tmin is not None else np.nanmin(t_all)
    vmax = args.tmax if args.tmax is not None else np.nanmax(t_all)
    r_ref = max(np.nanmax(d["r_phot"]) for d in frames)

    def size(r):
        return (np.asarray(r) / r_ref) ** 2 * args.size_scale

    fig, ax = plt.subplots(figsize=(13, 11))
    sc = None
    if obs is not None:
        sc = ax.scatter(obs["rise_time"], 10 ** obs["log_peak_lum"], c=obs["t_phot"] / 1e3,
                        s=size(obs["r_phot"]), cmap="coolwarm_r", vmin=vmin, vmax=vmax, alpha=0.9)
    if models is not None:
        sc = ax.scatter(models["rise_time"], 10 ** models["log_peak_lum"], c=models["t_phot"] / 1e3,
                        s=size(models["r_phot"]), cmap="coolwarm_r", vmin=vmin, vmax=vmax,
                        edgecolors="black", linewidths=2, zorder=3)
        groups = models["name"].astype(str).str.split("(").str[0]
        for k, (g, rows) in enumerate(models.groupby(groups, sort=False)):
            x, y = rows["rise_time"].to_numpy(), 10 ** rows["log_peak_lum"].to_numpy()
            if len(rows) > 1:
                ax.plot(x, y, LINESTYLES[k % len(LINESTYLES)], color="k", alpha=0.9, zorder=2)
            mid = len(rows) // 2
            txt = ax.text(x[mid] + 2, y[mid], g, fontsize=14, fontweight="bold", zorder=4)
            txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground="white")])

    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(r"Photospheric temperature [$10^{3}$ K]", fontsize=20)

    # radius legend
    for r, label in ((1e15, r"$10^{15}$ cm"), (5e15, r"$5\times10^{15}$ cm")):
        ax.scatter([], [], s=size(r), color="black", label=label)
    ax.legend(title="Photospheric radius", loc="upper right", fontsize=16, title_fontsize=17,
              labelspacing=1.5, borderpad=1.2, frameon=True)

    ax.set_yscale("log")
    ax.set_xlim(*args.xlim)
    ax.set_ylim(*args.ylim)
    ax.set_xlabel("Rise time [rest-frame days]", fontsize=20)
    ax.set_ylabel(r"Peak bolometric luminosity [erg s$^{-1}$]", fontsize=20)
    ax.tick_params(labelsize=15)
    fig.tight_layout()
    fig.savefig(args.output, dpi=300)
    print("saved", args.output)


if __name__ == "__main__":
    main()
