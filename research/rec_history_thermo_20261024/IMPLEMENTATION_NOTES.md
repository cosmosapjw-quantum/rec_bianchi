# THERMO01 implementation — prepared, not executed

Requested executor routing is gpt-6.1-sol/high. Actual runtime model identity was not observed. Root Astra owns scientific acceptance and execution authorization. Scientific import, coefficient evaluation, source probe, linear solve, native compilation and IVP counts are all zero at this preparation checkpoint.

## Source correspondence and changes

`vendor/` preserves original bytes as source-only references and is never imported. Exact hydrogen.c comes from the baseline native-owner record, SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`; the ROOT transport read reference has an added newline and was not selected as immutable authority. `inputs/INPUT_IDENTITIES.json` records twelve exact assets and their observed byte sizes, SHA256, Git blob and runtime roles.

`code/inputs.py` reads only the five local runtime files: native CSV, PREPARED_BLOCKS and the three original tables. It checks frozen identities before reading, uses scalar libm logarithms and source-order A2s normalization, and copies native primitive values directly. There is no temperature/density/cosmology conversion or larger-project import.

`code/source.py::rates` transcribes hydrogen.c interpolate_rates and primitive_rates.py local four-point Lagrange polynomials. The active baseline stencils are retained for complex evaluation and checked independently at each finite-difference endpoint. xe/xHII are open ambient arguments; the source domain allows xe>0 and 0<xHII<1 without imposing the old wrapper's xe>=xHII restriction. Temperature/density/H logarithmic increments are applied to the positive native baseline values.

`build` retains native real/virtual coefficient order: real-real and source entries, pre-diffusion two-photon couplings, full temperature-dependent diffusion recurrences, gamma/tau formation before neighboring-bin Lyα adjustments, then virtual diagonals and sources. Unlike the old diffusion wrapper, no negative-rate clipping is inserted. Bose denominators retain literal exp(delta/TR)-1 with the fixed energy-sign branch; no additional expm1 substitution was made there.

The root ARITHMETIC_ADDENDUM is implemented explicitly. The literal real parity view uses native p/A formulas, stored X0, and zero new RHS. All scientific values, Dual6 tangents, plain-complex oracle and finite differences use the same stable escape evaluation: native quadratic branches below1e-6, k1..10 p series until.03, expm1 expressions above.03. Both native and numerical-representation masks are compared at every endpoint. There is no constant anchoring correction. Native-vs-stable matrix and observable gaps are separately retained. The series truncation and its derivative are checked against60digit values within the single bounded primary.

`code/scalar.py` propagates six forward components through elementary scalar operations. Complex evaluation uses plain complex scalars and never calls Dual propagation. Thus the source equations are shared, while derivative methods differ. `primary.py` computes the implicit tangent from M dX=ds−dM X, then differentiates native outgoing evaluation, F and the paired event. M,s,T,P and all primitive blocks and derivatives are exported.

The proper-second ionization source H F includes the H product rule. Number and energy observables derive from a single Lyα event; radiation and atomic energies are exactly paired with opposite signs. The pure-H direction is saved as ambient xe+xHII, checked separately with a directly restricted seed at512eps gross, and compared with the independent complex columns. Restricted seeding reuses X and dX and performs zero additional RHS.

## Verification prepared

The primary saves every prescribed literal block residual, coefficient/output six-axis complex comparison, selected outgoing/F/number components, primal/tangent componentwise backward residual, structural identity, mixed finite-difference result and refusal. Two fixed directions at three steps require at least one passing step each; all results and worsening are preserved. No asymptotic convergence claim is inferred.

Three new dimension1/2/3 manufactured systems include nonsymmetric matrices and nonzero coefficient derivatives. Their exact reference derivatives use Fraction Cramer determinants differentiated as rational functions, independently of the numerical implicit RHS. They require six small numerical RHS; determinant algebra uses no linear solver. Fourteen escape depths include zero, both sides of the native switch, moderate and large depths. Invalid/nonfinite primitives, table domain/boundary, native switch and stencil-surface refusals are prepared.

Large RHS allocation is exactly base1+tangent6+complex6+mixedFD12=25. Literal parity and restricted pure-H rebuilding add zero RHS. Each solve increments a hard25-column counter. Three toy systems use6 numerical RHS, below16. The primary never imports native code, reruns627-column RESP01 work, evolves a trajectory or replays old campaigns.

## Commands and resource enforcement

From this unit directory, only after root supplies a matching RUN_READY authorization:

```bash
python code/run_bounded.py primary --authorization evidence/execution/RUN_READY.json
```

The authorization must bind `unit=REC-HISTORY-THERMO01`, `action=primary`, `decision=RUN_READY`, and an exact `source_snapshot` matching code/inputs/vendor plus THEORY/FROZEN_CONTRACT/ARITHMETIC_ADDENDUM. The prepared snapshot is in `evidence/execution/PREPARED_SOURCE_SNAPSHOT.json`.

The launcher enforces one thread across BLAS/OpenMP variables and1GiB address space before the child imports scientific packages. Primary child CPU limit39s plus parent soft/hard1s conservatively fits the inclusive40s allowance; child wall timeout is inside the120s total window. Parent pre-fork hard limit39 is raised no further in the child, then parent hard limit becomes1 after spawn. Full parent process CPU plus wait4 child CPU is reported; process-scope RSS highwater is identified accurately. Input/code hashes are recorded before/after, stdout/stderr are retained, environment/start failure records preserve diagnosis, and automatic retries are zero. Wall origin is explicit: after authorization parsing, before hashing/child launch.

Figures have a separate authorization and one process:

```bash
python code/run_bounded.py figures --authorization evidence/execution/FIGURES_READY.json
```

The figure script imports only saved arrays and plotting libraries, with no source or solver import. It prepares two PNG/PDF figures: six-axis signed outgoing curves with a full-width derivative-verification residual panel; and ionization, number and paired radiation/atomic energy primitive responses with units. Figure child9s+parent1s and30s wall fit its10CPU/30wall allocation. The reserved repair10CPU/30wall is not authorized by either command.

## Current stopping state

All seven code files passed ast.parse only. No module import or numerical preflight was run. Static review and exact snapshot delivery precede S1 backup and root RUN_READY. Results, numerical criterion outcomes and scientific admission remain NOT_RUN/pending.
