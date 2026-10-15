# MESA setups (r22.05.1)

Three MESA work directories that take an 18 M☉ + 14 M☉ binary to a stripped,
exploded star ready for STELLA. Compiled files are not included; build each
with `./mk` after setting `MESA_DIR`.

Run them in order. Each stage loads the model saved by the previous one:

1. **`01_binary_progenitor`** – binary evolution (period 365 d) until the
   primary is stripped of its hydrogen envelope. Run with `./rn`; saves the
   stripped primary as `18M_to_4.7M.mod`.
2. **`02_stripped_core_to_cc`** – loads `18M_to_4.7M.mod`, then: end of core
   He burning → remove remaining H → end of core C burning → log T_c = 9.55 →
   core collapse. Saves `18M_to_4.7M_Collapsed_Core.mod`.
3. **`03_explosion_stella`** – loads the collapsed core, runs infall, energy
   deposition, and five shock-propagation parts, then writes the STELLA inputs
   (`mesa.hyd`, `mesa.abn`). Add CSM with `../csm/add_csm.py` before running
   STELLA.

Three intermediate models are included so you can start at any stage:
`02_stripped_core_to_cc/18M_to_4.7M.mod` (output of stage 1),
`02_stripped_core_to_cc/lgTmax.mod`, and
`03_explosion_stella/18M_to_4.7M_Collapsed_Core.mod` (output of stage 2).

The setups are adapted from MESA test-suite cases (binary examples,
`20M_pre_ms_to_core_collapse`, `ccsn_IIp`).
`03_explosion_stella/src/stella/` contains the STELLA include files that ship
with MESA.
