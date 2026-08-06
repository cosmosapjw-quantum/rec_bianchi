# Current scientific state — PR-05B2 / v0.60

PR-04 is complete at the source-conditioned split-domain operator-contract
level. PR-05A locks the primitive rate/schema layer. PR-05B1 fixes the
source-identifiable rank-one local DAE and rejects an invented finite local
virtual-spike mass. PR-05B2 now closes the canonical accepted characteristic
history itself.

## PASS results

- Guarded instrumentation leaves the original-HyRec numerical history unchanged
  and dumps the complete source-order accepted radiation history through the
  source `z~900` step.
- The deterministic history contains 7,489 accepted `eta=ln(a)` slices and
  4,680,625 stored dimensionless departure values:
  `Dfminus[311]`, `Dfminus_Ly[3]`, and `Dfnu[311]` per slice.
- Every `hydrogen.c::fplus_from_fminus` path is represented: exactly 313
  queries per snapshot, comprising 308 virtual-to-virtual, three
  line-to-virtual, and two virtual-to-line channels.
- Maximum source real/virtual algebraic residual at `z~1300,1100,900`:
  `3.4992746547891075e-14`.
- Maximum electron-rate discrepancy: `2.983987151472822e-14`.
- Maximum source-order outgoing virtual discrepancy:
  `4.1516803496059265e-12`; this is a cancellation-amplified relative
  diagnostic at `z~1300`, with the absolute discrepancy retained in the
  evidence ledger.
- Maximum analytic history-JVP discrepancy: `4.14421999460274e-12`.
- Maximum 120-digit interpolation discrepancy: `2.6184810423156507e-16`.
- Photon number per H is conserved along every free characteristic to
  `1.2308212967416113e-15`; photon-energy change is exactly assigned to
  cosmological redshift work, and the characteristic atom source is zero.
- Rejected steps do not mutate history. Accepted append, rollback and binary
  restart are byte-exact. Future endpoints and unlocalized stencil switches fail
  closed.
- Fixed-local-state Bianchi II, class-B `VI_h`, and exceptional `VI_-1/9`
  local microphysics firewall residual is exactly zero.

## Ownership boundary

The typed scalar history replacement contract is complete, but the owner swap
has not yet occurred. Canonical Sobolev Ly-alpha escape, native `A1s`
diffusion, completed/Schur `Tvv`, and the existing history callback remain
active until PR-05B3 performs an XOR owner transition inside the same residual,
Jacobian, conservation ledger and restart contract.

## Claim boundary

PR-05B2 proves a source-identical, causal, transaction-safe accepted-step
operator. It does not claim a finite-volume native grid, a native-derived COM
interior trajectory, adaptive integration, FLRW `x_e(z)` parity, visibility
parity or CMB parity.

The next stage is **PR-05B3 scalar history ownership swap and coupled
accepted-step residual**.
