# REC-HD-CONSUMER-CALLSITE01 | coding contract and actual verification

## C1 — Baseline / acceptance

Parent PR155 immutable HEAD `861b7f8b3e52d580437a1b4ad448d9669b0d2706`. Reuse source-pinned original HD (2289 bytes, SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`) and two **real** prior consumer code blobs: PR151 `multichannel.py` `029255494bf0a63b93bf8b2715327a8585afb5f3`, PR155 `field_semantics.py` `21517960f912efbd2dc9df8b94fd577e03ca2e27`. Acceptance: exact source/parent-code identities, correct local energy-ledger formula, actual consumer call, selective in-memory mutation, 8 exact rational coefficients, 6 bounded source-node runs, no old stationarity/IVP/native replay, no source correction.

## C2 — Code/formula/data mapping

- PR151 `generate`, lines 55–75: radiative `nu` from printed `e['nu_GHz']` unless `source_consistent=True`, radiative photon energy `h nu`; collision detailed balance from `dE=E_u-E_l` in both policies. This is **MIXED** in default diagnostic mode.
- PR155 `parse_lamda_hd` and `frequency_comparison`: source hash and core/meta projection, both `nu_E` and `nu_P` as exact rational numbers, no production.
- REC production `hyrec_source_adapter.py` lines 123–166: one-photon action and self-referential Planck null helper, hydrogen atomic source, no demonstrated HD source ingestion. REC `frequency_liouville.py` lines 93–145: `nu_abs_Hz + x Doppler_width_Hz` locked frequency grid and mode-measure check, not a CDMS HD source.
- BASS main `bianchi/thermo/recombination.py` lines 37–105: hydrogen Saha/Peebles and Ly-alpha; `bianchi/matter/collision_ladder.py` lines 42–118: Thomson/BGK. REI main `src/rei_bianchi/multigroup_hhe_transmission.py` lines 1–78: HI/HeI/HeII photoionization continuum. These **inspected files** do not prove presence or absence of HD consumer elsewhere.
- `CALLSITE_MATRIX.json` binds each code path to its exact commit and blob SHA, with source-to-physical policy and execution status.

## C3 — Algorithm and error structure

`audit_consumer.py` uses Python `Fraction` created from original decimal tokens to calculate `nu_E`, `nu_P`, `delta_nu`, `h(nu_P-nu_E)` exactly as rational numbers. It imports PR151 and PR155 by path only **after** checking the Git blob SHA, then calls the actual PR151 `generate` at declared `T={50,100,200} K`, `n_H2={1000,1000000} cm^-3`. No `solve_stationary`, IVP or collision network recomputation. `mpmath` 95-digit local precision evaluates the synthetic Boltzmann/Planck net-rate identity; this is not a directed interval proof. Direct code rate and a separately derived stable `expm1` formula must agree to absolute `1e-78` on this bounded finite source. The exact rational per-event coefficients do not depend on the high-precision evaluation.

## C4 — Execution boundary and reproducibility

Private owner archive contains original `source_private/hd.dat` and exact original parent code snapshots. Public Git contains only `audit_consumer.py`, `tests/`, `CALLSITE_MATRIX.json`, reports, manifest and small derived JSON/figure. Do not commit original HD bytes. The required CLI takes `--source`, `--multichannel`, `--field-semantics`, `--output`, optional `--T` and `--den-cm3`. A different parent code blob or altered original source fails immediately. A read-only checkout of PR155 is sufficient for public code; the private source is restored separately.

## C5 — Implementation

Actual source-only `audit_consumer.py`, `create_callsite_matrix.py`, `plot_ledger.py` and 2 test files were written and executed in the current Python runtime. The matrix is generated from nine actually inspected source files and includes exact code blobs. In-memory mutation adds `0.001 GHz` to the second printed photon frequency without touching the 2289-byte donor. The only changed PR151 edge is radiative J2->1, index1. The other 7 radiative and all18 collision channels are unchanged. The diagnostic `source_consistent=True` closes the photon-vs-level energy coefficient but is **not** a physical source choice.

## C6 — Software verification and repaired failures

First implementation run raised `AssertionError: Einstein bath rate discrepancy J1`. Root cause was an extra `exp(-x_E)` factor in the separately coded synthetic rate oracle, not a source-data or solver defect. The correct rate is `A*g*n_l*expm1(x_P-x_E)/expm1(x_P)`; this was repaired before acceptance. A first matrix unit test wrongly assumed every human-readable consumer label contains uppercase `HD`; the test was replaced with a structural imported-code identity check. Both red failures are preserved in this document, not presented as passing initial tests.

Final `python3 -m unittest discover -s tests -v`: **23/23 PASS**, exit0, source restored. `python3 -m compileall -q audit_consumer.py tests plot_ledger.py`: exit0. Negative controls: nonfinite input, nonpositive frequencies, source byte mutation, parent-code blob mutation, original 35Hz failure preserved, policy mutation only changes one radiative edge, no physical DAG promotion. The standalone `Decimal` oracle reconstructs all eight source deltas and compares them exactly to `Fraction` coefficients.

## C7 — Scientific checks

The symbolic two-sector local ledger and synthetic Boltzmann/Planck rate were independently checked in Wolfram Language; the null helper's self-referential identity returned zero. The maximum absolute per-event energy coefficient is **1.210962399179234431758e-27 J/event**, J6->5. A genuine source-incompatible synthetic bath produces a nonzero net radiative rate and a nonnegative total local source residual, but this is a *mathematical counterexample*, not physical entropy production. The existing PR151 collision channels remain identical when printed photon metadata changes, as required by their `dE` dependence.

## C8 — Numerical/figure verification

Six T/density cases passed: T=50,100,200 K × n=1000,1000000 cm^-3. Each called only `generate` and the ledger, no stationary solve. Median per-call measured wall time ~0.00491 s for this host, **not a solver speedup claim**; whole-process max RSS was 99856 KiB and includes Python/import overhead. Exact coefficients are unaffected by precision, while mpmath95 is a finite diagnostic oracle rather than rigorous directed rounding. `results/SIX_CASE_PREFLIGHT.json` stores all timings.

`results/LOCAL_LEDGER.png` and `.svg` show **signed per-net-down-event coefficients** in 1e-27 J/event, not actual energy production. Initial visual audit found J1/J8 visually indistinguishable from zero; a footnote reports their nonzero values in plotted units. Final 90-mm single-column preview was opened; axis, sign, units, title and labels are legible. The exact values remain in JSON. Do not interpolate across discrete J or fit a physical model.

## C9 — Review status

Same-context source audit and mutation/Decimal/Wolfram crosschecks are complete, but a genuinely distinct-author review of the new implementation was **NOT_RUN** (native subagent tool not exposed). Keep C9 `PARTIAL_NONAUTHOR_NOT_RUN`. The inherited PR155 GitHub Actions `verify-durable-backup` job at run40790802170 failed at `scripts/verify_repo.py --quick`, with historical trailing whitespace in `research/rec_source_synthesis_20261027` CSV among the reported violations. This is a separate repository-wide verification failure; neither a success nor a scientific error in the new scoped code. Do not silently reformat old source data to make this PR green.

## C10 — Release / handoff

Release is **scoped research only**: executable source-only consumer audit with reproducible source/code identity, exact energy-ledger coefficients, 23 targeted tests and 6 preflight cases. Production HD source admission, physical H5 epsilon, CDMS v2 reconciliation, L4/REI and native Bianchi transport remain blocked. The new branch and Draft PR are add-only and stacked on PR155, with no main merge. Final provider ACKs and per-stage Git receipts must be recorded from actual responses, not assumed. The central canonical remains **28/88 (+0)**, REC physical **0/313 (+0)**. Native subagent NOT_RUN; R6/C9 partial.
