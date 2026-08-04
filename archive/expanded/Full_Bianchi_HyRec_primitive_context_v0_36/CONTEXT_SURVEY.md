# Primitive Bianchi solver context survey

## Question

How should the supplied `bianchibianchic2` code influence the remaining 12-PR Full Bianchi–HyRec design, and can it already provide useful background-evolution references?

## Evidence inspected

- User archive SHA-256: `ba10a80ca7e4cec510e935d5a75032725ae822b89cb25c6dd2599d770955ef38`.
- 82 Python modules under `bianchi/` and 62 pytest modules.
- `README.md`, `PR-STATUS.md`, `PLAN-NEXT-v4.md`, chart, matter and thermodynamic source modules.
- Read-only SciPy reference runs in `background_runs.csv`.
- Targeted FLRW/recombination tests in `TARGETED_TESTS.txt`.

## Findings

### Mature background host

The archive already contains class A, class B, exceptional VI*_-1/9, tilted class B and recollapse-safe IX charts. It also contains kinetic–Einstein feedback references for Bianchi I and V. It is substantially more mature than a disposable primitive.

### Recombination module is a baseline, not the target

`thermo/recombination.py` is a Peebles/RECFAST-level model with helium Saha corrections and an injectable scalar H(z). It is useful for FLRW and mean-H-only regression but has no direction-dependent Ly-alpha radiation state.

### Natural feedback interface already exists

`general_matter.py`, `kinetic_einstein.py` and `type_v_coupled.py` show how Omega, Q_a and Pi_ab can feed geometry. Full Bianchi–HyRec should provide these moments through a stable adapter rather than be embedded separately into every chart.

### Transplant should wait for schema lock

The archive has no Git history and no explicit license file. Since the user supplied their own code, this is not treated as a scientific blocker. Before actual transplantation, provenance, license and supersession metadata should be added.

## Reference-run conclusions

- Seven selected background/feedback runs completed.
- IX maximum expansion was detected at finite D-time.
- Class-B, exceptional and tilted constraints remained controlled.
- Bianchi-V Friedmann/Codazzi feedback residuals remained at the levels recorded in `background_runs.csv`.
- Bianchi-I exact-quadrature and hierarchy feedback trajectories agreed at the 1e-8 scale in the short run.
- The H-only Bianchi-I recombination adapter gives a controlled sensitivity baseline; it is explicitly not Full Bianchi–HyRec.

## Plan adjustment

1. Keep PR-01 through PR-04 focused on local microphysics and common-measure validation.
2. At PR-05, implement `BackgroundSnapshot` and `RadiationFeedback` before the primitive HYREC monolithic residual.
3. Use this archive as the target host and regression oracle from PR-06 onward.
4. Use Bianchi I and V coupled modules as independent feedback oracles.
5. Defer code transplantation until the state schema and primitive residual are frozen.
6. Preserve the existing RECFAST module as a baseline lane; do not upgrade it in place into HyRec.

## Confidence

High for architecture and background-chart findings: direct source evidence and executed trajectories. Medium for final runtime integration: the pinned Diffrax stack was unavailable from the current isolated package index, so the trajectories use an external SciPy reference adapter rather than the source-native Diffrax path.
