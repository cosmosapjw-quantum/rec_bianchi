# PR-05C2C1B2B1B/v0.71 research report

## Result

`PASS_P0_FALSE_CONVERGENCE_GATE_FIXED_PHYSICAL_RESIDUAL_JVP_CONNECTED_MATRIX_FREE_CONTINUATION_OPEN`

The adaptive CMB/BASS protocol requires contract reconstruction and baseline
mismatch resolution before performance-first optimization.  The current DAG
node was therefore narrowed to the physical acceptance metric rather than a
Rust port or a 9x4 macro sweep.

## Evidence

- exact v0.70 reconstructed parent provenance;
- complete z~1100 direct network node;
- actual v0.48 Bianchi-II background sequence;
- source-conditioned red/blue original-HyRec boundary occupations;
- durable nonlinear Bose action, conservative frequency transport and analytic JVP;
- dt sweep, variable-rescaling mutation and matrix-free shifted-JVP regression.

## Main finding

At the recorded canonical step, the old generic diagnostic is
`3.893e-15` and would pass the
`1e-11` threshold.  The state-relative generic diagnostic is
`5.143e+02`, while the
load-bearing physical gross and number gates are
`1.000e+00` and
`1.000e+00`.  The initial
state is not a physical macro root.

A unit-rescaling adversary changes the legacy metric by a factor of
`1.000e+18` but changes the corrected
metric by only `1.110e-16`
relatively.

## PHYS-MATH audit

- Definitions: physical step and pseudo-time are separate.
- Units: occupations and all acceptance diagnostics are dimensionless; JVP maps
  occupation perturbations to occupation residuals.
- Positivity: physical states remain strictly positive; no clipping is used.
- Conservation: generic residual size cannot replace the independent photon
  number gate.
- Known limit: the scalar stiff manufactured problem reaches its exact root,
  but the physical canonical parent is correctly rejected.

## PHYS-MATH-CODE audit

- Equation-to-code: `CoupledCollisionTransportProblem.residual` and
  `residual_jvp` are the load-bearing operator path.
- Dense assembly: audit only; `shifted_linear_operator` is the continuation path.
- Regression: tiny-state, actual-lane JVP, scaling-invariance and hard-gate tests.
- Remaining P0: there is no safeguarded matrix-free nonlinear solve yet.

## Claim

Surviving claim: the false zero-iteration acceptance path is removed and the
physical residual/JVP is connected.  Narrowed claim: matrix-free continuation is
available as an operator interface, not as a converged macro solver.  Rejected
claim: v0.70-P0 generic acceptance alone establishes physical convergence.
