# PR-05C2C1B2B1E1A research report

## Decision

`PASS_PR05C2C1B2B1E1A_SOURCE_CONDITIONED_SINGLE_COM_MACRO_ROUNDOFF_LIMITED_ROOT_ATOMIC_HISTORY_COUPLING_OPEN`

The v0.73 source-derived parent does admit a positive conservative root of the
bounded nonlinear COM collision--transport subproblem.  The apparent
`O(1e-6)` net/state residual floor is not a physical nonconvergence: the raw
residual is `1.123e-03` times the explicit
gross-event floating-point bound, while the gross backward error is
`3.192e-17`.

The result survives an independent pair-loop collision oracle and closes the
photon-number ledger after a `1.344e-11`
maximum activity-direction correction.  Exact face-energy bookkeeping is also
roundoff limited relative to the gross photon-energy event scale.

## Narrowed claim

The numerical root-existence blocker for the COM subblock is closed.  The
native boundary was held at its source-derived v0.73 value, and atomic
one-/two-photon/Raman populations and accepted history were not evolved.  The
next stage must connect those representation-local owners before exactly one
history append can be claimed.
