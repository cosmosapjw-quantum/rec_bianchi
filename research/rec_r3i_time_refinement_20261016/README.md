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

## H2_CONTINUATION: scoped PASS after NCP and independent review

The separate `h2_continuation_001/CONTRACT.json` fixes the event and resource
caps. `SOURCE_MANIFEST_V5.json` SHA-256
`03804f8f4d022d03e6004f7384f821b2cfc8dbc99a3b6281c1a7595fae390faa`
pins the 90-file capsule, including the reviewed checkpoint, original source
ZIP, Python package, verifier and harness. A one-step local smoke passed with
same-h `xe` difference zero; it is `SMOKE_ONLY` and does not establish an event
or a convergence order. The V5 independent review authorized one NCP execution,
with full result review still pending.

The NCP run used the frozen commit `53edd26ee5ff58edf7389e44fd05c41392dc3f28`
and independently reached helium cutoff at global index 37205,
`z=1648.074602926592`, followed by exactly two H-only accepted steps.
It took 753 additional accepted steps and 3,012 FULL source evaluations.
The final state at index 37207 is `xe=0.9979346805949129`,
`Tm=4494.16659111864 K`. The independently generated same-h C history
has maximum relative `xe` error `1.1124844999609022e-16`, absolute HeII
error `4.87890977618477e-19`, scaled H RHS error
`6.498029544999007e-11`, and maximum spectral tolerance ratio
`0.0011406261097209518`. All 761 accepted columns and their 625
spectral values were independently checked. A separate review reconstructed
942,756 causal link checks with no current or future history read.
The NCP run used one CPU, 14.04488 cumulative CPU seconds, 14.44640 wall
seconds, and parent/child peak RSS 114,147,328 / 112,721,920 bytes
(separate high-water measurements). The raw archive SHA-256 is
`0c6105a816277420b551471b7c9815085269a7475e8c4b7a7c3d31fa93208132`;
the owner PC re-read all 46 archived member hashes. The full result remains
under the 4,096-step, 16,384-evaluation, 600-CPU-second, 900-wall-second,
2-GiB caps. The slim receipt is `h2_continuation_001/ncp_run_001/verification.json`.

The next READY node is `H2_U4_POST_SAHA_EXIT`: continue the reviewed h/2
checkpoint from index 37207 through the source H-only post-Saha exit and two
hydrogen ODE steps. Its contract must retain exact source stage switching,
the same-h independent C oracle and prior resource caps. The H ODE and
thermal ODE transitions, U5, full primordial history, h/4 Python history,
and h/h2/h4 Python order remain NOT_RUN. The original U5 nine FAIL/HOLD is
unchanged. The claim ceiling is original q=0 HyRec FULL H+He only.
