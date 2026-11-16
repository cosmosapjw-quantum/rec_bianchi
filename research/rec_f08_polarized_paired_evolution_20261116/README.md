# F08 persistent polarized paired receiver

**Status:** research-scoped conditional point evolution; production and owner admission HOLD. Original q-frame 3% failure and fixed-hat physical support failure are retained. Canonical DAG deltas are zero. No merge or automatic successor is requested.

Start with [REPORT_KO.md](REPORT_KO.md), [THEORY.md](THEORY.md), [results/RESULT.json](results/RESULT.json), and [REVIEW.md](REVIEW.md). This package is a child of REC PR200, which supplies the physical-tetrad moment rule.

## Files

| File | Role |
|---|---|
| `collision.py` | Exact frozen-geometry, complex-coherency Thomson semigroup |
| `transport.py` | Original source/physical-energy remap and triaxial Stokes screen transport |
| `receiver.py` | Explicit conditional q-cell/physical-quadrature adapter and optical clock |
| `paired_bridge.rs` | Persistent direct caller of unchanged original `paired_runtime` |
| `prepare_runtime.py` | Source-full backup restore, 12+51+4 locks, separate offline Rust build |
| `run_evolution.py` | Actual coupled native execution with persistent polarized state |
| `analyze_tick142.py` | Reuse original angular source and preserve the historical 3% FAIL |
| `summarize_results.py` | Compile measurements and identities from the five actual cases |
| `test_*.py` | Thirty source-free physical/implementation checks |
| `results/` | Actual outcomes, sparse time witnesses, build/test/execution evidence |

Full spectral arrays and native endpoint witnesses are in the source-complete backup, not duplicated as new repository arrays. The inherited REC199 original angular source remains unchanged.

## Environment

Source-free tests were executed with Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. The actual native campaigns and independent raw-data audit used the remote Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0 environment. `results/BUILD_RECEIPT.json` records the actual remote Rust compiler and binary identity. The original Rust source has no network dependency and builds offline. The native runs used `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`; at most two independent cases ran concurrently.

## Reproduce

Run from the repository root. The sibling REC199 and REC200 research directories must be present.

```bash
REC_UNIT=research/rec_f08_polarized_paired_evolution_20261116
python3 -m unittest discover -v -s "$REC_UNIT" -p 'test_*.py'
python3 -O -m unittest discover -v -s "$REC_UNIT" -p 'test_*.py'
python3 "$REC_UNIT/analyze_tick142.py" --out /tmp/f08_tick142_recheck.json
```

The last command records the retained science FAIL and exits successfully when the diagnostic is correctly reproduced. It does not relabel the old science criterion PASS.

Use the existing source-full archive `REC199_ORIGINAL_F08_NATIVE_THOMSON_STOKES_SOURCE_FULL_20261115.zip`, SHA256 `ba557fd45fe643f42c5dffc793b237e311c1db1260b4f1d3c9b4068e7f91f93f`. Choose a **new** work directory for the build; the preparer refuses overwrite.

```bash
python3 "$REC_UNIT/prepare_runtime.py" \
  --archive /path/to/REC199_ORIGINAL_F08_NATIVE_THOMSON_STOKES_SOURCE_FULL_20261115.zip \
  --work /path/to/new_f08_runtime

REC_BINARY=/path/to/new_f08_runtime/bridge/target/release/rec_f08_polarized_bridge
REC_RUNS=/path/to/new_f08_runs
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 "$REC_UNIT/run_evolution.py" \
  --binary "$REC_BINARY" --out "$REC_RUNS" --geometry S0_BI --steps 160 --degree 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 "$REC_UNIT/run_evolution.py" \
  --binary "$REC_BINARY" --out "$REC_RUNS" --geometry S0_BI --steps 160 --degree 4 --control
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 "$REC_UNIT/run_evolution.py" \
  --binary "$REC_BINARY" --out "$REC_RUNS" --geometry S0_FLRW --steps 160 --degree 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 "$REC_UNIT/run_evolution.py" \
  --binary "$REC_BINARY" --out "$REC_RUNS" --geometry S0_BI --steps 160 --degree 6
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 "$REC_UNIT/run_evolution.py" \
  --binary "$REC_BINARY" --out "$REC_RUNS" --geometry S0_BI --steps 320 --degree 4
python3 "$REC_UNIT/summarize_results.py" --runs "$REC_RUNS" --out /path/to/new_f08_summary
```

`--steps` divides the fixed source duration **1e11 seconds**; 320 is a dt/2 run at the same endpoint, not a longer scenario. These commands are bounded experiments. They do not start the original 16,000-step owner campaign.

## Source and approximation contract

The input pair digest `0a2bec...` and the source-file digest `b6c1d2...` are distinct identities. `prepare_runtime.py` verifies both their original context and the original 67 source locks, then copies the unchanged `paired_runtime.rs` into a separate bridge crate. No owner source is patched.

The actual source H is `(1.01,0.99,1.00)e-14 /s`, a triaxial diagonal Bianchi I. The source proper macro dt is `625000000 s`; populations are per H nucleus; collisions use common physical-energy nodes. Photon I, Q, U, V, guards, electron density and the clock are from the same original source.

`FEEDBACK` checks energy-group photon totals, replaces the native point photons and reinitializes their interval boxes to points. Gas state, gas boxes and source/work/absorption ledgers are retained. This cannot propagate a cumulative photon interval certificate. `local_bound` and `public_width` are conditional native-stage diagnostics after that reset, not global accuracy estimates.

The physical collision semigroup is linear and exact for the finite moment rule. The native q-cell adapter is explicitly nonlinear because it normalizes the inverse projection at each physical energy. Its drift and nonlinearity are measured. The low-energy guard remains a two-moment representation with joint PSD checks. Full spectral guard reconstruction, continuum angular convergence and all 14 owner interval ledgers remain unresolved.

## Failure preservation

The old original-hat tick142 mismatch stays `0.04152277708926094 > 0.03`, FAIL. The inherited physical energy support defect also remains: about 41.992% of photons occupy forbidden fixed-hat nodes at the final BI time. These are different failures with different mechanisms. Neither is removed by successful implementation tests.

Two early integration failures are retained in `results/FAILURE_HISTORY.json` and the full backup logs: an interface field mismatch before native execution, and a source-arithmetic parity mismatch after two native trials. The latter was repaired by matching the original scalar redshift arithmetic; no tolerance changed. Completed science counts exclude those failed attempts and the JSON also reports the inclusive totals.
