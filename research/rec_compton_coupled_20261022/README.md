# REC Compton-coupled native full63 pilot

This unit follows the completed omitted-process budget in draft PR122.
It asks how the previously large fixed-path Compton forcing changes the
coupled gas temperature, charge state and opacity when the existing atomic
system evolves with that source. The eight specified new IVPs are bounded
by [FROZEN_CONTRACT.md](FROZEN_CONTRACT.md).

The physics reduction is in [THEORY_KO.md](THEORY_KO.md): the added source
occupies one RHS/Jacobian row, and the frozen-composition Compton subproblem
has an exact affine-temperature relaxation solution. The actual solver
retains all 63 coupled coordinates and uses the analytic BDF Jacobian.

`actual_hot` uses the current integrated photon energy monopole.
`planck_reference` uses a separately prescribed Planck bath instead.
Both use the same inherited external UV moments. These branches are
exclusive; their difference does not reconstruct the actual grey spectrum.

## Execution and retained evidence

Run from this directory with the pinned dependencies in requirements.txt.
The driver admits only the source identity recorded in
`evidence/PREFLIGHT_ADMISSION.json`. Its default command only prints the
plan. Starting an IVP requires an explicit case or `--all`.

```sh
python3 code/run_compton.py --output results/compton8 --case s03_m03_r03_actual_hot_nominal
python3 code/run_compton.py --output results/compton8 --all --resume
python3 code/analyze_compton.py --input results/compton8 --output results/analysis_v1
```

The first case and the remaining seven share a persistent 1200 s active
campaign allocation, with a cooperative 240 s cap per case. Exact completed
results are reused; partial results and failed attempts are preserved.
The prior completed IVPs are never rerun. Each new result retains accepted
BDF nodes, the 109-point comparison grid and both 513/1025-point diagnostic
grids. Admissions apply to those saved physical states.

Stage A binds the theory and sources. Stage B binds the implementation and
actual preflight evidence. Stage C binds the new outcomes, independent
reviews, plots and handoff. A stage snapshot does not assert completion of
any later calculation or remote transfer; provider receipts establish that.

## Interpretation

This is a finite test-fluid gas calculation. The opposite Compton radiation
source is recorded in an exchange ledger but is not applied to photon energy
or Einstein dynamics. Nuclear production, additional CI/CE dynamics, full
spectral closure, global convergence and production approval remain outside
this contract. Physical HOLD, production NOT_APPROVED,
global_convergence NOT_RUN, REI_activation=false and U5 CLOSED_HOLD_NOT_RESET
are retained.
