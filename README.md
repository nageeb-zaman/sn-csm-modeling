# sn-csm-modeling

Tools for modeling **stripped-envelope supernovae interacting with
circumstellar material (CSM)**: from a binary-stripped progenitor to synthetic
light curves and spectra.

```
MESA binary  →  MESA single star  →  MESA explosion  →  add CSM  →  STELLA  →  SuperLite  →  analysis
 (mesa/01)        (mesa/02)            (mesa/03)        (csm/)    (light      (spectra)       (analysis/)
                                                                   curves)
```

- **Progenitor:** an 18 M☉ + 14 M☉ binary in MESA strips the primary's
  hydrogen envelope; the stripped star is evolved to core collapse.
- **Explosion:** MESA follows infall, energy deposition, and shock propagation,
  then hands the ejecta to STELLA.
- **CSM:** `add_csm.py` surrounds the ejecta with a wind, a Gaussian shell, or
  both, before the STELLA radiation-hydrodynamics run.
- **Spectra:** STELLA snapshots are converted to SuperLite inputs to compute
  Monte Carlo radiative-transfer spectra.
- **Analysis:** command-line scripts plot light curves and spectra, compare
  them with observed supernovae, fit blackbodies, and place models on a
  brightness–temperature–timescale–radius (BTTR) diagram.

## Repository layout

| Folder | Contents |
|---|---|
| `mesa/01_binary_progenitor` | MESA binary run that strips the primary |
| `mesa/02_stripped_core_to_cc` | Stripped star from core-He burning to core collapse |
| `mesa/03_explosion_stella` | Collapse, explosion, shock propagation, STELLA hand-off |
| `csm/` | `add_csm.py`: wind, Gaussian-shell, or wind + Gaussian CSM |
| `superlite/` | STELLA → SuperLite input converter (modified from SuperLite, GPL-3) |
| `analysis/` | Light-curve and spectra plotting, observed comparisons, blackbody fits, BTTR diagram |
| `data/` | Where to get the data the scripts need |

## Requirements

- [MESA](https://docs.mesastar.org) **r22.05.1** (includes STELLA)
- [SuperLite](https://github.com/gururajw/superlite)
- Python ≥ 3.9 with numpy, scipy, pandas, matplotlib, astropy:

```bash
conda env create -f environment.yml
conda activate sncsm
```

## Quick start

```bash
# 1. Progenitor and explosion (each folder is a MESA work directory)
export MESA_DIR=/path/to/mesa-r22.05.1
cd mesa/03_explosion_stella && ./mk && ./rn      # or start from mesa/01

# 2. Add CSM to the STELLA input (edit the parameter block first)
python ../../csm/add_csm.py

# 3. After STELLA and SuperLite, plot the results
python analysis/plot_lightcurves.py run_a run_b --labels "No CSM" "Wind" --density
python analysis/plot_spectra.py run_b/day_5 run_b/day_20 run_b/day_60 --lines
```

See the README in each folder for details.

## Citation

If you use this code, please cite this repository (`CITATION.cff`) and the
codes it builds on: MESA (Paxton et al. 2011, 2013, 2015, 2018, 2019; Jermyn et
al. 2023), STELLA (Blinnikov et al. 1998, 2000, 2006), and SuperLite.

## License

MIT (`LICENSE`), except `superlite/`, which contains modified SuperLite tools
under the GNU GPL v3 (`superlite/LICENSE`).

## Contact

Nageeb Zaman, Department of Physics & Astronomy, Louisiana State University ·
ORCID [0009-0006-6787-461X](https://orcid.org/0009-0006-6787-461X)
