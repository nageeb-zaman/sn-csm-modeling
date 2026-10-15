# STELLA → SuperLite conversion

These two files are **modified copies** of tools from
[SuperLite](https://github.com/gururajw/superlite) (`Tools/stella2superlite.py`,
`Tools/myfuncts.py`) by Gururaj Wagle. They are distributed under the GNU
GPL v3 (see `LICENSE` in this folder), the same license as SuperLite. The rest
of this repository is under the license in the top-level `LICENSE`.

Changes made by Nageeb Zaman (also marked `Edit by Nageeb Zaman` in the code):

- `myfuncts.py`: `load_stella_prof` checks for duplicate radii in STELLA
  profiles; the new `refine_data` removes them and interpolates `r_center_cm`.
- `stella2superlite.py`: handles fractional days (e.g. `-d=0.4`), writes each
  snapshot into its own `day<NNN>` folder, and creates the output folder
  without an interactive prompt.

Usage is the same as upstream, e.g.

    python stella2superlite.py -o=path/to/superlite_run -p=path/to/stella/res -d=20

SuperLite itself (the Fortran radiative-transfer code) is not included; get it
from https://github.com/gururajw/superlite.
