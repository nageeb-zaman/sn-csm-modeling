# Adding CSM to STELLA models

`add_csm.py` takes the ejecta profiles that MESA writes for STELLA
(`mesa.hyd`, `mesa.abn`) and appends a circumstellar medium (CSM). One script
covers three density structures:

| `density_profile` | CSM structure | Key parameters |
|---|---|---|
| `'wind'` | Steady wind, ρ ∝ r⁻² | `m_dot` (M☉/yr), `v_csm` (km/s), `csm_r_out` (cm) |
| `'gaussian'` | Gaussian shell of given mass | `csm_mass` (M☉), `csm_r_in`, `csm_r_out` (σ = width/10) |
| `'wind+gaussian'` | Wind with a Gaussian density bump | wind parameters + `r_i`, `r_f`, `height` (peak ρ, g cm⁻³) |

Other inputs: `csm_zones` (number of CSM zones, 400 by default) and `t_csm`
(CSM temperature, 0.1 × the outer ejecta temperature by default). The CSM
composition is copied from the outermost ejecta zone. Between the ejecta edge
and the CSM, the script adds transition zones so the density falls smoothly
instead of jumping.

## Usage

1. Run MESA through `mesa/03_explosion_stella` so it writes `mesa.hyd` and
   `mesa.abn`.
2. Edit the **INPUTS (CSM parameters)** block in `add_csm.py`.
3. Run `python add_csm.py` in the folder with `mesa.hyd`/`mesa.abn`. It writes
   `mesa_csm_v5.hyd`/`.abn`, prints the CSM mass, and saves a
   `Density_profile.png` check plot.
4. Rename the outputs to `mesa.hyd`/`mesa.abn` and run STELLA.
