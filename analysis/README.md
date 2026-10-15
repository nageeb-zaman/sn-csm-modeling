# Analysis and plotting

General command-line tools for STELLA and SuperLite output. Run any script with
`-h` for all options. `sncsm_io.py` holds the file readers they share.

| Script | What it makes | Inputs |
|---|---|---|
| `plot_lightcurves.py` | Bolometric light curves; `--density` adds a density-profile panel | model folders with `mesa.lbol` (and `mesa.hyd`) |
| `plot_lightcurve_vs_observed.py` | Model band light curve vs. observed SNe, aligned at peak | `mesa.tt` + observed light-curve tables and distances |
| `plot_spectra.py` | Stacked spectral time series, optional line markers | SuperLite snapshot folders |
| `plot_spectra_vs_observed.py` | Model vs. observed spectra, epoch by epoch | snapshot folders + two-column observed spectra |
| `fit_blackbody.py` | Blackbody temperature and photospheric radius per epoch | SuperLite snapshot folders |
| `plot_bttr.py` | Brightness–temperature–timescale–radius diagram: rise time vs. peak luminosity, colored by temperature, sized by radius | model table + observed table, or extrabol outputs + a rise-time table |

## Examples

```bash
python plot_lightcurves.py runs/no_csm runs/wind runs/shell \
    --labels "No CSM" "Wind" "Shell" --density -o lightcurves.pdf

python plot_lightcurve_vs_observed.py runs/shell \
    --obs data/snA_lc.txt 66 --obs data/snB_lc.txt 150 --band R

python plot_spectra.py runs/shell/day_5 runs/shell/day_20 runs/shell/day_60 \
    --labels 5d 20d 60d --lines

python plot_spectra_vs_observed.py \
    --pair "runs/shell/day_5,obs/snA_p005.dat,0.03,5d" \
    --pair "runs/shell/day_20,obs/snA_p020.dat,0.03,20d" --obs-name "SN A"

python fit_blackbody.py runs/shell/day_* --table bb_fits.txt --plot

# BTTR diagram; observed values measured from extrabol fits (+/-5 d around peak)
python plot_bttr.py --models models_bttr.txt \
    --extrabol-dir extrabol/ --rise-times fit_params.txt --save-obs observed_bttr.txt
python plot_bttr.py --models models_bttr.txt --obs observed_bttr.txt --tmin 7 --tmax 17
```

## File formats

- **STELLA**: `mesa.lbol` (time, log L_bol in column 2), `mesa.tt` (band
  magnitudes; column 11 = R by default, change with `--tt-column`),
  `mesa.hyd` (STELLA input profile). Scripts look in the folder you give and in
  its `stella_output/` subfolder.
- **SuperLite**: each snapshot folder needs `output.flx_grid` and
  `output.flx_luminos`.
- **Observed light curves**: whitespace-separated table with a header, a `Time`
  column (days) and a magnitude column per band.
- **Observed spectra**: two columns, wavelength (Å) and flux.
- **BTTR tables**: whitespace table with a header and five columns: name,
  rise time (days), log10 peak luminosity (erg/s), photospheric radius (cm),
  photospheric temperature (K). Model rows named like `A(-2d)`, `A(peak)`,
  `A(+4d)` are joined by a line and labeled `A`. Extrabol files need the
  `Time (MJD)`, `Log10(Bol. Lum)`, `Temp./1e3 (K)` and `Radius/1e15 (cm)`
  columns; the rise-time table needs `name` and `Rise_Time_med`.
