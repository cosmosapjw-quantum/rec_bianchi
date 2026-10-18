# REC R3i: independent h/2 start and bounded continuation

Base: PR #100, `320b8810aaf1acdaa90e2eca860cf70b9af1ef75`.
Original October 2012 HyRec ZIP SHA-256:
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
R3h C-only `h,h/2,h/4` results are a separate reference; they do not establish
Python time convergence. The original U5 photon-average gate remains 9 FAIL / HOLD.

## H2_START: scoped PASS

The frozen contract is `CONTRACT.json`. The independent Python solver starts
at `z=8000`, computes 36,447 helium source-grid rows through global index
36446, then accepts eight FULL H+He updates and eight outgoing photon columns.
It never imports C history values into the Python state. Same-h original C
outputs are comparison oracles. An independent reviewer checked the raw
`h2_start_001/run_003` output and admitted this bounded node only.

The first substantive failure was retained in `h2_start_001/run_002`:
helium trajectory RHS scaled error `5.1086298962449853e-6` at row 15438,
from one binary64 ulp in a near-equilibrium Saha state. The original C
operand association repair is restricted to the new R3i module. `run_003`
then passed: helium max state scaled error `2.1787224815068235e-16`,
trajectory RHS `2.7755575615628914e-16`; eight accepted states have
`xHII,xe,Tm` differences zero at stored precision and HeII absolute error
`2.710505431213761e-20`. Max accepted Schur residual is
`3.426326776833222e-16`. Same-input FULL RHS maximum scaled error is
`2.0255672139590786e-13`; all integrated spectral channels pass their
frozen tolerances. The recorded run used one CPU and 2.9433 s wall.

`run_003/verification.json` SHA-256:
`7cddaa2c7d0813da21819462b5dfa00d838f349b66b553048c39411cf415008d`.
The exact Python producer is preserved at
`run_003/python_producer_exact.py` with SHA-256
`82ea5c627fbb7a4e280fbb351c65f83cd6608364226aa643354bc8ab0f6435e0`.
The accepted checkpoint NPZ SHA-256 is
`a6fe8a9a9e6d32b99d5b567e62d87912fdf4d71aa7a9392b33fdf23c55b8416d`.
Large raw files remain in the immutable owner-side result and backup capsule.

## H2_CONTINUATION: READY for one bounded NCP run

The separate `h2_continuation_001/CONTRACT.json` fixes the event and resource
caps. `SOURCE_MANIFEST_V5.json` SHA-256
`03804f8f4d022d03e6004f7384f821b2cfc8dbc99a3b6281c1a7595fae390faa`
pins the 90-file capsule, including the reviewed checkpoint, original source
ZIP, Python package, verifier and harness. A one-step local smoke passed with
same-h `xe` difference zero; it is `SMOKE_ONLY` and does not establish an event
or a convergence order. The V5 independent review authorized one NCP execution,
with full result review still pending.

The next node stops at the first HeII cutoff or hydrogen post-Saha switch plus
two accepted steps, or at its 4,096-step, 16,384-FULL-evaluation, 600 cumulative
CPU-second, 900 wall-second, one-CPU, 2-GiB cap. A cap before the event plus two
is HOLD. The h/h2/h4 Python order, U4/U5, and full primordial history remain
NOT_RUN. The claim ceiling is original q=0 HyRec FULL H+He only.
