# Frozen research record: rec_bianchi physics-specific ODE remediation

## Pre-registration (frozen before evidence collection)

### Research question

Which physics-specific formulations and structure-preserving numerical methods can eliminate or sharply reduce every confirmed current ODE/DAE/continuation blocker in rec_bianchi, and what falsifiable gates distinguish a structural cure from a numerical symptom treatment?

### Hypotheses and falsifiers

- H1 FRAME-COVARIANCE: A single declared observer tetrad for angular ordinates, with all collision and Liouville quantities transformed through one four-momentum map, removes finite-tilt frame disagreement. Falsifier: transformed collision and transport characteristics disagree for any locked finite-tilt snapshot or fail the beta-to-zero limit.
- H2 CONSTRAINED-BACKGROUND: Evolving constraint-compatible Bianchi variables and monitoring the Hamiltonian/Gauss constraint with physical event functions prevents validated negative density and branch drift. Falsifier: Omega becomes negative or the reconstructed constraint exceeds its scale-aware bound without a terminal event.
- H3 KINETIC-STRUCTURE: A detailed-balance-preserving collision operator plus exact discrete collision invariants and conservative moving-grid remap restores equilibrium, positivity, number/energy/four-momentum accounting, and removes tautological ledgers. Falsifier: Planck/Bose equilibrium is not a discrete null state, entropy production has the wrong sign, or an independently computed invariant changes across a closed step.
- H4 INDEX-AWARE-DAE: An index-aware implicit DAE with physics-scaled component norms, domain-preserving coordinates, consistent initialization, continuous events, and reinitialization removes adaptive/restart false acceptance. Falsifier: acceptance depends on unit rescaling, a near event is overshot, a rejected nonlinear solve repeats unchanged, or split-run and uninterrupted trajectories disagree.
- H5 IMMUTABLE-PHYSICAL-IDENTITY: Binding every accepted state/history/restart to an immutable digest derived from the actual physical operator and discretization prevents substitute-problem and cross-redshift acceptance. Falsifier: changing dt, frame, grid, network, background, ownership, or event schedule leaves the digest valid.
- H6 NONOVERLAPPING-SPLIT: An exterior-native/interior-COM/interface finite-volume or Schur-complement decomposition with one owner per physical flux removes E1C double counting. Falsifier: any spike/edge has zero or multiple owners, or global invariants differ from the sum of independently assembled boundary fluxes and local sources.

### Planned methods

- M1 confirmatory: trace current equations, conventions, state variables, and acceptance surfaces to a finite blocker-to-physics map.
- M2 confirmatory: retrieve primary literature for relativistic kinetic transport/tetrads and Bianchi constrained dynamics; derive limiting-case gates.
- M3 confirmatory: retrieve primary literature for cosmological recombination, detailed balance, conservative kinetic discretization, and moving-grid remap; map to native/COM ownership.
- M4 confirmatory: retrieve primary literature and official solver documentation for stiff index-1 DAEs, event handling, positivity, physics-scaled norms, and restart consistency.
- M5 confirmatory: synthesize a dependency-ordered remediation matrix with structural cure, mitigation, forbidden shortcut, validation gate, and residual risk for every issue family.
- M6 confirmatory: one independent review with no expected verdict supplied.

### Stopping rules

- Stop when every frozen issue family has at least one physically motivated remedy, a discriminating falsifier, and a claim boundary; or report it as unresolved.
- Use primary papers, original method papers, official project documentation, and current local source only for material technical claims.
- No code changes or new production run; bounded scratch derivations are allowed only to clarify limits.
- Exactly one independent review round; no repair loop beyond one closeout reconciliation.

## Evidence log

### 2026-08-23 local evidence

- E-L1 | source=`docs/PR05C2C0_THEORY_CLOSURE_FORMALISM.md` | sha256=`651b8d71c74035d3e0ccb24bded08bcae9b155afa149e9d2d99b891aec512389` | observation: the declared theory already chooses a hydrogen-frame scalar occupation, derives normal/hydrogen characteristics, detailed-balance activity fluxes, an entropy metric, micro-macro split, conservative upwind flux, and an index-one fixed-branch DAE; it explicitly requires event localization and restart.
- E-L2 | source=`docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md` | sha256=`9c666767feaa7a8c39145ca5206798500cd2759c4e7de744325d1c0f7573572d` | observation: the intended cure is exterior native plus interior COM plus two single-owner interface edges, with residual/JVP/invariant/restart/parity co-delivery; it is not implemented evidence.
- E-L3 | source=`docs/PR05B1_SOURCE_IDENTIFIABLE_DAE_FORMALISM.md` | sha256=`84baa249eea3d6ed7a15eb4673a723d697e3eb015a1ff1bb5b952d0ef63b99e0` | observation: canonical data identify one differential electron row, 313 algebraic rows, and causal memory; no finite native-spike mass can be inferred from point centres and integrated rates.
- E-L4 | source=`src/full_bianchi_hyrec/recoil/frequency_liouville.py` | sha256=`e1ce23a87f95f91a6220bd096849c15f2fca3b15e95aa90b43fc971a8401ae26` | observation: transport consumes grid directions as normal-frame inputs while the collision runtime consumes the same untagged array as hydrogen-frame directions.
- E-L5 | source=`src/full_bianchi_hyrec/recoil/nonlinear_bose_runtime.py` | sha256=`5ec3472eb075a7d050341b42837319e4397fb4175480b23e1e8ef9924385fd58` | observation: collision construction explicitly inverse-aberrates grid directions from hydrogen to normal frame.
- E-L6 | source=`src/full_bianchi_hyrec/trajectory/adaptive_macro.py` | sha256=`4100818b72f76d95c9e4bff7768dfe549e2feb648705a44f78b519088acba66a` | observation: current step-doubling, event clipping, history candidate, and restart surfaces lack the physical endpoint/event/operator binding required by H4 and H5.
- E-L7 | source=`src/full_bianchi_hyrec/trajectory/pseudotransient_continuation.py` | sha256=`4c2ec9ea675fda9c3197397946f20a7198273a2d44c901e93fd87e80d688c58f` | observation: the generic pseudo-transient metric and dense solve are not derived from the physical mass/entropy metric and do not constitute the missing 910-state driver.
- E-L8 | source=`src/full_bianchi_hyrec/background/evolution_provider.py` | sha256=`e82bb47ebe5b5f1cb178668aa67cd317b70e8c93549786582522855dff396204` | observation: the current Bianchi-II provider does not enforce Omega nonnegativity or independently evaluate the Gauss constraint.

### 2026-08-23 external primary and official evidence

- E-W1 | source=`https://doi.org/10.1016/0003-4916(66)90207-7` | fingerprint=`Lindquist 1966 relativistic transport on invariant mass-shell phase space` | observation: a photon distribution is evolved covariantly on phase space; tetrads are observer choices, not interchangeable labels for the same stored angular ordinate.
- E-W2 | source=`https://arxiv.org/abs/0706.2075` | fingerprint=`Pontzen-Challinor exact Bianchi tetrad radiative-transfer hierarchy` | observation: Bianchi geometry transports frequency and direction in a declared group-invariant tetrad, supporting one explicit frame convention and exact tetrad transformations.
- E-W3 | source=`https://doi.org/10.1088/0264-9381/6/10/011` | fingerprint=`Hewitt-Wainwright expansion-normalized Bianchi dynamical system` | observation: physical Bianchi state spaces use dimensionless normalized variables plus algebraic constraints; Omega nonnegativity is a state-space condition, not a passive diagnostic.
- E-W4 | source=`https://arxiv.org/abs/gr-qc/0008037` | fingerprint=`tilted Bianchi-II orthonormal-frame Hubble-normalized dynamics` | observation: finite tilt is a dynamical observer/frame variable and must remain in the constrained state rather than be silently reinterpreted by radiation operators.
- E-W5 | source=`https://arxiv.org/abs/gr-qc/0211071` | fingerprint=`exceptional VI_-1/9 has distinct orthonormal-frame dynamics` | observation: exceptional VI_-1/9 cannot be admitted by extrapolating a nonexceptional VI_h/BII provider.
- E-W6 | source=`https://arxiv.org/abs/1011.3758` | fingerprint=`HyRec simultaneous radiation-level-xe evolution with full Ly-alpha transfer` | observation: native radiation/history and atomic populations are dynamically coupled; replacing native support with an unidentifiable moment fit is physically unjustified.
- E-W7 | source=`https://doi.org/10.1103/PhysRevD.80.023001` | fingerprint=`Ly-alpha transfer includes true emission absorption Hubble drift diffusion recoil` | observation: a structure-preserving frequency operator must retain equilibrium drift-diffusion balance and full time dependence.
- E-W8 | source=`https://arxiv.org/abs/1009.2748` | fingerprint=`boson Boltzmann discrete conservation entropy Bose-Einstein equilibria` | observation: mass/energy invariants, entropy sign, and Bose equilibrium can be preserved simultaneously and should be solver gates rather than post-hoc algebraic ledgers.
- E-W9 | source=`https://doi.org/10.1016/0021-9991(70)90001-X` | fingerprint=`Chang-Cooper positivity conservation exact equilibrium` | observation: exponential fitting at Fokker-Planck faces is a physics-specific route for Ly-alpha diffusion/recoil rather than generic centered differencing.
- E-W10 | source=`https://doi.org/10.1137/19M1297907` | fingerprint=`conservative positivity-preserving radiative-transfer remap on deforming meshes` | observation: a moving Doppler grid requires a geometric conservation law and conservative positive remap; point interpolation is not equivalent.
- E-W11 | source=`https://doi.org/10.1137/20M1361407` | fingerprint=`single flux-mortar coupling of nonmatching representations` | observation: native and COM supports can remain distinct while a single interface flux enforces conservation without global remapping.
- E-W12 | source=`https://arxiv.org/abs/1807.06109` | fingerprint=`positive asymptotic-preserving micro-macro kinetic scheme` | observation: a conserved macro mode plus relaxing kinetic modes and realizability control can remain stable as collision stiffness grows.
- E-W13 | source=`https://arxiv.org/abs/2006.07497` | fingerprint=`Schur-complement AP kinetic transport` | observation: Schur reduction and globally stiffly accurate IMEX are principled only after the physical micro-macro split is identified.
- E-W14 | source=`https://doi.org/10.1137/0903023` | fingerprint=`Petzold DAEs require DAE-specific error and discontinuity handling` | observation: ordinary ODE error control is insufficient for algebraic variables and discontinuous branch inputs.
- E-W15 | source=`https://doi.org/10.1137/0909014` | fingerprint=`Pantelides consistent DAE initialization` | observation: initial and post-event states must satisfy algebraic and hidden consistency conditions before integration resumes.
- E-W16 | source=`https://petsc.org/release/manual/ts/` | fingerprint=`PETSc implicit F(t,u,udot), shifted Jacobian, events and postevent` | observation: the target executable interface can represent the index-one residual, continuous event indicators, post-event state/operator changes, and shifted Jacobian.
- E-W17 | source=`https://doi.org/10.1137/S0036142996304796` | fingerprint=`Kelley-Keyes pseudo-transient convergence uses underlying transient structure` | observation: pseudo-transient continuation is physically motivated only when its mass/scaling reflects the underlying time-dependent system; convergence alone is not a dynamic macro endpoint.
- E-W18 | source=`https://doi.org/10.1137/120881075` | fingerprint=`physics-based radiative-transfer preconditioning insensitive to timestep in tests` | observation: nonlinear elimination plus low-order/moment physics can precondition stiff transport, but performance must be re-established on the actual COM-native operator.

## Consolidated findings supplied for independent review

- C1 FRAME: declare the hydrogen tetrad as the canonical collision grid, route every consumer through one frame map, and evolve the full covariant frequency-plus-angular Liouville operator. A direction-only aberration patch is not a cure.
- C2 BACKGROUND: Bianchi II can use log-N1, an independently evolved shadow Omega, constrained dense interpolation, and continuous physical events. Generic VI_h, exceptional VI_-1/9, and recollapsing IX require distinct constrained state spaces; the cited D-normalized IX equations are LRS-only.
- C3 COLLISION: compile nonnegative reciprocal event conductances, use Bose activities/log means, and derive conservation and four-force from event incidence and independent material/photon contributions. Post-hoc opposite assignments and clipping are not proofs.
- C4 E1C: keep native exterior, COM interior, point-supported source nodes, physical cross-interface diffusion/recoil, and pure representation transfer as disjoint event owners. Do not infer finite cells for canonical point spikes.
- C5 MOVING GRID/HISTORY: use an ALE geometric conservation law and positive conservative remap only where source-cell overlap is identifiable; otherwise use hybrid nodes or a flux mortar. Treat retarded radiation history as an accepted, endpoint-bound method-of-steps state.
- C6 DAE: form one index-one residual F(t,y,ydot)=0 with consistent initial/post-event algebraic solves, physical component scales, domain-preserving coordinates, and complete invariant admission. Index one remains conditional on the algebraic Jacobian after null-mode handling.
- C7 ADAPTIVE/EVENT: accept the two-half backward-Euler state, shrink on each non-LTE failure class, locate continuous state-dependent roots even below the ordinary minimum step, and reinitialize the physical operator and history after events.
- C8 STIFFNESS/PTC: split conserved activity modes from relaxing kinetic modes, use entropy-metric graph and native/interface Schur blocks, and confine pseudo-transient continuation to physical-mass root globalization. AP/performance remains benchmark-dependent.
- C9 PROVENANCE: bind accepted states and restarts to immutable physical-operator and numerical-policy manifests and require byte, one-step, and split-trajectory replay gates.
- C10 CLAIM BOUNDARY: these are physics-derived remediation designs and falsifiers, not implemented or trajectory-validated cures. Tolerance tightening, clipping, global remap without source geometry, solver replacement alone, or higher precision alone are mitigations at best.

## Independent review round 1 and closeout reconciliation

- Verdicts: C4 and C10 CONFIRMED; C1-C3 and C5-C9 PARTIALLY_CONFIRMED; none REJECTED. The review emphasized that most remedies are conditional designs, not implemented cures.
- R1: hydrogen-frame storage is a natural design choice, not the unique covariant choice. The invariant requirement is one explicit tetrad/four-momentum/frequency/angular-measure convention consumed consistently by all operators.
- R2: shadow Omega is an independent diagnostic, not a constraint cure. Algebraic constraint construction and an independently derived matter/Einstein residual remain authoritative.
- R3: use conserved collision moments/null modes, not the overbroad phrase conserved activity modes; distinguish closed detailed-balance blocks from source, boundary, Liouville, and matter entropy terms.
- R4: a delay/history system is not automatically a finite-dimensional index-one DAE. Keep the index-one local residual and method-of-steps history contract distinct unless a finite augmentation is supplied.
- R5: separate physical-operator and numerical-policy digests. Require byte equality only for canonical serialization/local round trip; require tolerance-bounded physics equivalence for cross-platform split trajectories.
- R6: global remap without source geometry and post-hoc clipping are invalid workarounds, not useful mitigations. Higher precision is a local cure only for a proven roundoff-dominated cancellation.
- R7 omitted-family closeout: the final synthesis must explicitly cover half-step/nonfinite contamination, nonfinite solver inputs, grazing/simultaneous events, characteristic phi-function/JVP cancellation and zero-distance validation, PTC serialization/resume/fabricated result, complete full-coupled admission, clipping/JVP and nested-tolerance mismatch, causal-history complexity/restart stencil, and the absent executable E1C/full dynamic macro operator.
- R8 corrected dependency order: conventions and linked manifests; source geometry/event ownership; collision/interface/ALE discretization; residual/JVP/rank/domain/consistent initial state; event/history transaction; adaptive/nonlinear/PTC/preconditioner; restart/AP/performance/science parity.
