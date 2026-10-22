## Why

The retained thermal closure in PR121 does not include Compton energy transfer
or H/He collisional heating/cooling. A source budget is needed to choose the
next coupling work and keep source-domain limitations visible.

## Changes and results

This stacked research unit postprocesses the eight immutable full63 thermal
trajectories at109 saved nodes each:872 states, zero new ODE integrations and
zero old-IVP reruns. It adds actual-U hot-electron Compton, a separately owned
isotropic Planck reference, inherited dilute UV Compton exchange, source-bound
HG97 H/He CI and H I/He II CE, native availability masks and complete arrays.

On four primary paths, hot Compton removes2.576–2.592 eV/baryon from z7.9637
to2, equivalent to29.72–29.92% of the existing primary photoelectron heat.
Supplied H I CE is about−0.00132 eV/baryon; CI moves about2.05e−5 from kinetic
to binding energy and adds an electron. UV Compton contributes about+6.23e−5.
The directly integrated log-temperature forcing is about−1.03; this is not
a solved temperature correction or a rigorous omission-error bound.

## Validation

-6 focused Compton and10 collisional test methods pass, including independent
 cgs/SI conversions, Planck equilibrium, angular averaging,9 actual35-digit
 Wolfram CI fixtures, native conservation, particle/energy ownership,
 strict source domains, explicit continuation and absent-channel masks.
-Independent raw-NPZ recomputation of all872 states agrees to at most1.493e−14
 in power,7.866e−14 in coefficients and3.286e−15 in integrals.
-65 implementation/provenance checks pass; actual source/result/trajectory
 hashes and all retained-grid arrays are saved. The first postprocess took
0.6769 s wall; no completed IVP or old test suite was repeated.
-Three current PNG/PDF figures with exact plot data; actual PNG visual review,
 independent physics and implementation reviews, and explicit authorship.

## Scope and next step

Full CMB recoil/induced closure remains conditional on a supplied spectrum;
the Planck reference is not inferred from the actual moments. He I CE/
metastable and Li CI/CE remain unsupported. Fit continuation, missing channels
and underflow are distinct.109/55/Simpson comparisons are retained-grid
diagnostics; RR-alternative sensitivity is not numerical uncertainty.

The next finite contract proposes8 new full63 IVPs over two seeds, two
Compton branches and their nominal/refined pairs, with explicit test-fluid
gas/bath transfer accounting. Those future IVPs are NOT_RUN here.

Physical HOLD; production NOT_APPROVED; global convergence NOT_RUN;
REI_activation=false; U5 CLOSED_HOLD_NOT_RESET. This PR is a draft.

## Review entry points

Read REPORT_KO.md, THEORY_KO.md, HANDOFF_KO.md, NEXT_UNIT_CONTRACT.md,
results/budget_v1/RESULT.json and evidence review receipts under
research/rec_thermal_omitted_budget_20261022. Current figures are figures/v3;
v1/v2 preserve documented correction artifacts.

Publication and create-only backup are explicitly authorized. Remote commits
may have new headers, so exact Git root-tree equality and local/remote mapping
are recorded. Original local history is retained in the final archive bundle.
