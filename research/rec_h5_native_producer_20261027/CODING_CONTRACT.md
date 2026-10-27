# R9 formal coding contract
Astra-authored implementation contract for delegated lower-tier execution. FROZEN_CONTRACT.md and theory/THEORY.md define the mathematical specification; this file fixes the executable interface and admission obligations.

## Input and authority boundary
The program reads the locked SOURCE_CONTEXT, tagged target native CSV, native hydrogen.h and wrapper source from existing repository paths. Check their SHA256 locks before use. Build exactly 313 typed rows and preserve each existing field used by the source/anchor mapping. Do not rerun native history, IVP, matrix, HD or prior scientific outputs. A read-only metadata/hash verification is permitted.

Original native constants use exact float.fromhex / as_integer_ratio conversion; the tagged decimal CSV scalars first reconstruct their binary64 source values, then become exact rationals. The full source identity and conversion rules appear in every primary packet. Both original context and CSV stay unchanged. Native source routing and prefix5127 are checked for all rows.

## Code boundaries
- code/interval arithmetic: precision80, directed basic operations, correctly rounded elementary functions expanded outward; detect overflow, underflow, subnormal, invalid/nonfinite input and reject.
- code/producer: finite endpoint/critical-point envelope, actual313 bridge/chord/anchor composition and typed partial H5 packet.
- code/independent reference: precision140 point evaluation from original raw inputs and direct native/absolute interpolants, without importing production interval formulas or decomposition. It is an independent finite-precision diagnostic in addition to the analytic enclosure argument.
- code/controls: critical point inclusion, both sides of x=1, singleton/invalid domains, zero characteristic/temperature bridge, exact quadratic/affine chord and smooth toy defect translation.
- code/run_bounded.py: one-thread process, RLIMIT_CPU and address-space cap, independent wall watchdog; record executed argv, environment, versions, exits, timing and RSS. Failed attempts remain evidence.
- figures: two inspectable plots, (i) whole-cell reference curvature and chord actual/bound, (ii) separated query/temperature/native-anchor bridge scales. Plot exported numerical values only; no image generation.
- results: immutable run directories primary001 and controls001, source manifest, per-row enclosures, independent checks, controls and concise summary. Root alone admits and publishes.

## Frozen commands, numerical settings and ceilings
Run from repository root using Python3.12:
```sh
python3.12 research/rec_h5_native_producer_20261027/code/run_bounded.py --mode primary --cpu-seconds 90 --wall-seconds 180 --memory-mib 2048 --output research/rec_h5_native_producer_20261027/results/primary001
python3.12 research/rec_h5_native_producer_20261027/code/run_bounded.py --mode controls --cpu-seconds 60 --wall-seconds 120 --memory-mib 2048 --output research/rec_h5_native_producer_20261027/results/controls001
```
Primary precision80; independent precision140; one thread; memory2GiB/process. Implementation/execution subtotal ceiling300CPU seconds; primary90 and controls60 are smaller per-process ceilings, not separate 300-second grants. C4 publishes the execution allowance before root releases execution. No automatic precision scan, parameter sweep, repeated primary, or new solver run. A concrete failing check may receive one targeted root-authorized repair within the same cumulative budget.

## Required exact and numerical acceptance
1. Source hashes,313 ordered row bindings, source/target energies, special routes, strict stored-cell containment, prefix, exact alpha, curvature coefficient and exact old anchor radius pass.
2. Per row enclose x and reference values/derivatives; include all possible critical points conservatively; report proved monotone regime separately.
3. Keep signed Bchar,BTR,Btotal,Jref and direct/decomposed anchor bridge. Interval intersection/containment and independent direct point evaluation must agree.
4. Prove abs(Jref)<=curvature-based chord bound using outward endpoints, allowing a numerically unresolved sign only if its interval includes zero; do not force a sign.
5. Independent precision140 original-formula points lie inside precision80 output intervals. For actual nonzero derived quantities, width/(1e-100+abs(midpoint))<=1e-40. Zero-containing controls use absolute containment, not an invalid relative ratio.
6. Analytic critical point and equality/invalid-domain controls pass; failure evidence is retained and interpreted before any repair.
7. Every authoritative numeric bound is serialized as decimal endpoint strings. Float conversions serve only plotted diagnostics.
8. Scalar occupation K=1 stays typed as scalar sensitivity; full_state_K and physical_M2 remain null. All physical H5 radii/epsilon/outgoing bound remain null and physical coverage0/313.

## Review and deliverables
C5-C8 supply actual code, raw outputs, useful findings, plots and measured budget. A separate Astra reviewer at C9 reads the exact code and saved results, checks interval arithmetic and original source binding, and may perform a bounded independent targeted check. It does not rerun the primary by default. C10 publishes admitted result, source ZIP, actual Git/Dropbox/Drive receipts, central DAG scoped return and a copyable handoff. Original88-node contracts and foreign budgets are preserved.

## Runtime identity
The orchestration request is a lower-tier gpt-6.1-sol implementer and independent Astra review. Runtime model identity is not independently observable and must not be claimed as verified.
