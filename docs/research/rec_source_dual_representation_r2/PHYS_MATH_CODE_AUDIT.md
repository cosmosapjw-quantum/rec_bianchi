# PHYS–MATH–CODE audit — REC source over BASS dual evolution

**Disposition:** `ARCHITECTURE_CORRECTED / DUAL_ADAPTER_IMPLEMENTATION_NOT_STARTED`

## Code-path reconstruction

### BASS direct-grid lane

`bianchi/matter/grid_boltzmann.py` stores a finite phase-space array `F[r,a]=f(q_r,n_a)` and applies a directly discretized Thomson kernel. It is genuinely a non-PSTF distribution path, but its inspected implementation is a massless Bianchi-I slice and its collision gate is isotropic-background limited.

`bianchi/matter/grid_coupled.py` removes moment closure from the coupled matter state, but evolves a radially integrated angular density `G_a`, not the full spectral distribution `f(q,e)`. It is a class-A diagonal, massless, single-species slice.

### BASS PSTF lane

`bianchi/matter/hierarchy.py` computes PSTF moments directly from the distribution and supplies hierarchy RHS operators. Its dense numerical tensor path is bounded by a finite supported rank.

`bianchi/matter/pstf_coeff.py` supplies canonical `2l+1` coefficients and closed-form Gaunt/Wigner operator blocks at generic rank. Formula authority and a finite numerical workspace must remain distinct claims.

### REC source lane

`hyrec_source_adapter.py` already contains:

- a source-identical virtual-spike map and analytic JVP;
- a positive paired one-photon source with explicit phase-space measure;
- a signed net affine coefficient derived from positive emission and absorption.

`characteristic_angular.py` supplies an arbitrary-direction characteristic reference and exact constant-coefficient transfer/JVP, but its bounded `IsotropicTransferCoefficients` interface requires a nonnegative field named opacity. It cannot host a negative `chi=kappa-eta` without an explicit paired-source adapter or a renamed signed-affine API.

## What is genuinely fixed by R2

- REC no longer claims ownership of a third state-evolution representation.
- One source bundle feeds both BASS representations.
- The positive `(eta,kappa)` pair is primary; signed `chi` is derived.
- The PSTF source is an exact projected product, not an entropy closure.
- Finite source-product work rank and output rank are separate.
- The virtual-spike exponential jump is recognized as an infinite-tail operation.
- A 26-direction face remains a derived readout.

## Missing implementation path

No current REC module exposes a common interface such as:

```text
SourceAuthorityBundle
  -> evaluate_grid_source(...)
  -> project_pstf_source(...)
  -> apply_grid_jump(...)
  -> project_pstf_jump(..., tail_tolerance)
  -> jvp(...)
  -> receipt(...)
```

No test currently runs one immutable source bundle through both BASS lanes and measures a projected residual.

## Required TDD RED

The next test-only slice must fail unless:

1. grid and PSTF adapters reference the same source-bundle hash;
2. the positive `eta,kappa` pair survives serialization;
3. `chi<0` is accepted when the pair is physical;
4. `L_work<L_out+L_chi` is rejected for exact polynomial-rate projection;
5. an anisotropic exponential jump cannot claim finite exact closure;
6. grid-to-PSTF and native-PSTF source actions agree on an exactly band-limited manufactured state;
7. a 26-direction readout without parent state/source/background hashes is rejected;
8. TEFF diagnostics never overwrite or close the BASS state.

## Regression risks

- silently feeding signed `chi` into a nonnegative-opacity API;
- comparing a full spectral grid path with the radially integrated `G_a` path as if they were identical states;
- treating generic-rank formula support as an already converged finite numerical run;
- using analysis/synthesis round-trip alone as nonlinear product de-aliasing evidence;
- applying a finite-rank exponential jump and hiding its omitted tail;
- letting an entropy representative become the production distribution;
- mixing hydrogen-frame source direction with outward-sky convention;
- promoting a 26-node compatibility object to authority.

## Ranked findings

- **P0:** none introduced by this documentation-only R2 node.
- **P1:** exact BASS owner commit/blob pins must be refreshed on the implementation parent.
- **P1:** grid/PSTF source residual and convergence matrix do not yet exist.
- **P1:** current REC characteristic transfer API cannot represent every physical positive pair through a signed net coefficient.
- **P1:** two-photon/Raman deposition and reverse detailed-balance partners remain absent.
- **P2:** direct-grid BASS support is broad architecturally but uneven in the inspected numerical slices.
- **P2:** jump-tail and product de-aliasing policies need independent tolerances and receipts.
- **P2:** TEFF regularity/normalization gates need executable guards.

## Acceptance before physical admission

A later physical-face claim requires source-complete channel data, both adapter paths, cross-representation convergence, event/restart closure and exact parent provenance. This R2 node satisfies none of those admission gates by itself.
