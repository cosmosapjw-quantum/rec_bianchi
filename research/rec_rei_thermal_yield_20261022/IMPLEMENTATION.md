# THERM01 implementation — finite dynamic thermal closure

This unit composes the immutable PR220 donor geometry, atomic source coefficients,
inventory and projection maps with a new thermal/ionic-yield owner. It does not run
a donor campaign, replay an old history, or use the donor prescribed-temperature
RHS/diagnostics. The old donor files remain byte-identical in
`vendor/rei_pr220/vendor/rec_hheli`, with the 57-file donor manifest and unchanged
compact map module beside them.

## Executable paths

From this directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLCONFIGDIR=/tmp/therm01-mpl python code/run.py --checks
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLCONFIGDIR=/tmp/therm01-mpl python code/run.py
```

The second command performs the new unit checks, exactly the eight frozen new
IVPs (or verifies successful cached outputs), finite comparison gates and figures.
It must be used only after the Stage B checkpoint authorizes Stage C. For cached
figure recovery alone, use `python code/run.py --plot` with the same environment.
No successful output is overwritten or reintegrated when identity and raw hashes
match. A preserved failed case or changed scientific source/config identity stops
execution for the root controller's decision.

`thermal.py` defines source support rejection above 60 eV, dynamic
`w=epsilon_th/kB`, temperature-dependent atomic rates, cancellation-resistant RR
moments, signed-sum DR moments, the compact34/full63 projection and new thermal
and energy diagnostics. `checks.py` performs only newly scoped checks.
`run.py` uses BDF with SciPy's fresh finite-difference Jacobian and obtains dense
output. Independent GL8 and GL16 evaluations between all saved epochs integrate
absorption, escape and adiabatic work; their integrals are not tally ODE states.
The endpoint thermal plus ionization energy comes independently from saved `w,Y`.
`plot.py` reads raw NPZ outputs and writes CSV sources plus three PNG/PDF figures.

## New checks observed before science execution

- The 57 immutable donor files verified successfully.
- Unsupported spectrum rejection, exactly zero core contribution, unit photo
  charge gain, event energy partition and structural threshold zeros passed.
- 121 log-spaced source-fit temperatures, including 100 and 1e6 K, gave finite
  nonnegative summed RR/DR rates and kinetic moments; maximum analytic versus
  centered-log derivative mixed relative discrepancy was 2.273e-7. Twelve
  positive rates at or below 1e-280 were excluded from derivative division and
  reported explicitly. Endpoint finite-difference algebra uses fit formulas
  solely to check derivatives, with no out-of-domain physical rate evaluation.
- Extended RHS parity at three frozen eligible states was below 2.826e-16 scaled;
  electron-count thermal, local energy and recombination binding/escape
  identities were below 4.5e-16. Zero-process adiabatic limits passed.
- Initial inherited midpoint source quadrature failed the prospective 64/128
  comparison for the He II primary kinetic moment at 60 eV: relative discrepancy
  0.00600657030 exceeds 0.005. Evidence is preserved in
  `evidence/PHOTON_MOMENT_INITIAL_FAILURE.json`. Root source/quadrature decision
  was requested before Stage C. No science IVP had been run at that point.

An initial NumPy boolean JSON serialization error was corrected mechanically;
its failure note remains in `evidence/UNIT_ATTEMPT1_FAILURE.txt`.

## Runtime and claim boundaries

Observed Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8. Runtime
requirements record these actual versions. The requested executor role is native
lower-tier mechanical implementation. The runtime API exposes no independently
observed model identity; no specific model identity is claimed.

No temperature floor, population clipping or abundance renormalization is used.
No integrated tally states or old diagnostic thermal path are reused.
Source-fit derivative cooling remains conditional; its empirical physical
accuracy is unmeasured. Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL,
CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED and
REI_activation=false remain fixed. The full-band 60–200 eV correlated ionic-yield
input obligation is unchanged.

## AMENDMENT_Q1 observed repair

Root authorized one bounded quadrature repair. The new adapter now evaluates
sigma(E), E sigma(E), and (E-chi)sigma(E) with fixed Gauss-Legendre4 inside each
unchanged threshold-split energy bin, weighted by the declared E^-2.5 number
spectrum. Source bounds, nominal64/check128 base bins, H I normalization,
coefficient rows and donor bytes remain unchanged. This is numerical quadrature
repair, not a changed physical source or a relaxed acceptance tolerance.

The original failed unit receipt is preserved as
`evidence/UNIT_CHECKS_MIDPOINT_FAILURE.json`. The current unit receipt explicitly
links it and reports PASS: maximum64/128 moment relative discrepancy
7.25355244761e-13, below unchanged5e-3 tolerance. All other new checks pass;
max frozen extended RHS parity2.9633e-16 and derivative discrepancy2.273e-7.
The repair command was `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1 python code/checks.py`, exit0. No science IVPs have yet run.
