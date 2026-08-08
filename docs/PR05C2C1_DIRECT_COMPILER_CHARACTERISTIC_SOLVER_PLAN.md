# PR-05C2C1 — implement the closed theory contract

## Goal

Implement and validate the v0.65 theory contract without adding a new physical
closure.

## Task 1 — direct positive thermodynamic compiler

- compile positive nodal unordered COM--KHW event kernels at the locked
  `z~900,1100,1300` thermodynamic nodes, midpoints, and refinement nodes;
- cache state-independent atomic/radial factors by content hash;
- parallelize independent unordered-pair and same-cell blocks;
- perform deterministic ordered reduction with per-block SHA-256 receipts;
- interpolate only inside fixed-topology cells in log conductance;
- derive harmonic moments only after nodal positivity and reciprocity audit.

## Task 2 — characteristic angular solver

- initialize with isotropic hydrogen-frame scalar source data at the high-z
  boundary;
- backtrace/evolve each positive-weight angular node with exact
  `BackgroundSnapshot` characteristics and finite tilt;
- include the formal isotropic source/opacity term and direct COM--KHW
  redistribution under the owner registry;
- evaluate native red/blue traces at exact face frequency/direction;
- reproduce the FLRW scalar history in the isotropic limit.

## Task 3 — conservative face trace

- implement common-slope positivity/local-bound scaling rather than independent
  trace clipping;
- implement fixed-branch analytic JVP;
- localize limiter/upwind branch changes and restart;
- retain P0 as fallback and audit MUSCL/DG nested-grid convergence.

## Task 4 — entropy-metric preconditioner

- transform the collision block to activity-log variables;
- attach constant activity nullspace;
- build the W-orthogonal P/Q split;
- test diagonal/AP, graph multilevel, angular block, and interface/atomic Schur
  candidates;
- select only a candidate that improves unpreconditioned residual, iterations,
  wall time, and peak RSS on all locked lanes.

## Task 5 — completion evidence

- direct withheld-node relative error and refinement;
- exact 3000 K v0.50 limit;
- number, BE null, positivity, entropy, and same-event four-force;
- analytic JVP below `1e-8`;
- backward/algebraic residual below `1e-11`;
- at least four canonical macro intervals in all nine redshift/background lanes;
- exact reject/rollback/restart and one history commit per accepted macro;
- FLRW reduction evidence sufficient to enter PR-06.
