# REC source authority over BASS dual evolution — Research Loop R2

**Date:** 2026-09-03  
**Status:** `PASS_RESEARCH_CONTRACT / NOT_ADMITTED`  
**Authority effect:** `NONE_RESEARCH_AND_DESIGN_ONLY`

## Correction to R1

R1 correctly rejected a fixed 26-direction vector as the physical authority, but it assigned REC a new continuous-distribution evolution object. That ownership is too broad. BASS already supplies two evolution representations of the photon distribution:

1. direct phase-space/angular-grid Boltzmann evolution without moment closure;
2. distribution-level PSTF evolution of the spectral multipoles `F_{A_l}`, with generic-rank formula authority and numerical work-rank policies.

REC therefore must not create a third state-evolution scheme. REC owns the recombination source, jump, boundary, event, derivative and provenance data consumed by both BASS representations.

## Revised physical donor

The R2 donor is the representation-neutral source authority bundle

```text
REC.SOURCE.AUTHORITY.BUNDLE.V2
```

It contains positive paired rates `(eta, kappa)`, source-identical jump maps, directional face/boundary data, source Jacobian/JVP information, channel/measure metadata and immutable provenance. BASS remains the owner of the evolved state.

```text
BASS grid lane:   f(t, nu, e)        <- REC grid source adapter
BASS PSTF lane:   F_{A_l}(t, nu)     <- REC PSTF/Gaunt source adapter
                                      ^
                              same source bundle
```

At the exact function-space level the adapters must commute with the BASS distribution-to-PSTF projection. At finite numerical resolution, the discrepancy is measured and decomposed rather than hidden.

## Core result of this loop

For an unpolarized paired source

\[
  \mathcal C_{\rm REC}[f]
  =\eta(1+f)-\kappa f
  =\eta-\chi f,\qquad \chi=\kappa-\eta,
\]

the exact PSTF/harmonic source coefficients are

\[
  C_{\ell m}=\eta_{\ell m}
   -\sum_{LM}\sum_{\ell'm'}
     \chi_{LM}f_{\ell'm'}
     \mathcal G_{\ell m;LM;\ell'm'}.
\]

If `chi` is band-limited through `L_chi`, exact source coefficients through `L_out` require distribution input through

\[
  L_{\rm work}\ge L_{\rm out}+L_\chi.
\]

A clean Wolfram regression at `L_out=L_chi=2` found that `L_work=4` gives zero residual, while using the same cutoff `L_work=2` misses explicit `f_3 chi_1`, `f_3 chi_2`, and `f_4 chi_2` contributions.

An anisotropic virtual-spike transmission `T(e)=exp[-tau(e)]` is different. Even `tau=tau_0+alpha P_1` generates nonzero harmonic coefficients at every rank, with the rank-`l` coefficient beginning at order `alpha^l`. Its PSTF implementation therefore needs an adaptive tail/convergence certificate or a pointwise grid evaluation followed by projection; a finite exact buffer does not exist generically.

## Role of the TEFF papers

The two TEFF papers provide static information diagnostics, not a transport closure and not a replacement state:

- Paper I separates radial spectral loss from finite-PSTF angular loss.
- Paper II further separates number-recovered thermochemical-frame information from the unresolved spectral-shape remainder and supplies conditional finite-cutoff entropy certificates.

These quantities may be evaluated on outputs of either BASS lane to diagnose whether the unresolved error is radial, angular or representation-induced. They do not choose the physical evolution equation.

## 26-direction interface

The ordered 26-direction object remains useful only as a derived compatibility/readout surface:

```text
REC.DERIVED.26_DIRECTION_FACE.READOUT.V1
AUTHORITY_EFFECT = NONE
```

Every such readout must point to the exact BASS-evolved state and exact REC source bundle from which it was materialized.

## Immediate next node

```text
REC_SOURCE_R3_DUAL_ADAPTER_TDD_RED
```

The first code slice is test-only. It must require one immutable REC source bundle to produce both grid-space and PSTF-space source actions, reject silent same-cutoff aliasing, reject loss of the positive `(eta,kappa)` pair, and reject any 26-direction readout without a parent state/source identity.

## Claim boundary

This package does not admit a physical face, prove grid/PSTF numerical parity, complete two-photon/Raman deposition, implement finite-electron-tilt collision, promote a provider, or establish `PASS_REC_PHYSICAL_SPLIT`.
