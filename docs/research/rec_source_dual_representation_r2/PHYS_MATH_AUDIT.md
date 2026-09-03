# PHYS–MATH audit — REC source over BASS dual evolution

**Disposition:** `PASS_RESEARCH_THEOREM / IMPLEMENTATION_AND_ADMISSION_HELD`

## Definitions and conventions

- metric signature: `(-,+,+,+)`;
- spatial orientation: `epsilon_123=+1`;
- `e^a`: photon propagation direction;
- `n_sky^a=-e^a`: outward observed sky direction, only through an explicit adapter;
- `c` is retained;
- physical-time and ray-length coefficients satisfy `R_t=c R_s`, `V_t=c V_s`;
- occupation `f` is dimensionless;
- positive paired rates `eta,kappa` have dimensions `T^-1`; `chi=kappa-eta` is signed.

## Exact representation result

For the scalar paired source

\[
 C[f]=\eta-\chi f,
\]

angular projection gives

\[
 C_{lm}=\eta_{lm}-\sum_{LM,l'm'}\chi_{LM}f_{l'm'}G_{lm;LM;l'm'}.
\]

This is the exact projection of a distribution-level source and not a moment closure. With all ranks retained and the same source bundle,

\[
 \Pi_P C^{grid}[f]=C^{PSTF}[\Pi_Pf].
\]

## Finite-rank result

If `chi` is band-limited through `L_chi`, exact source outputs through `L_out` require

\[
 L_{work}\ge L_{out}+L_{chi}.
\]

The clean Wolfram regression for `L_out=L_chi=2` has zero residual at `L_work=4`. The same-cutoff choice `L_work=2` leaves a nonzero residual containing rank-three and rank-four distribution coefficients. This is an aliasing/source-convolution issue, not a transport closure theorem.

## Non-polynomial jump result

For

\[
 T(e)=e^{-\tau(e)},\qquad
 f^+=Tf^-+(1-T)f_{eq},
\]

a finite angular rank of `tau` does not imply a finite rank of `T`. The exact witness `tau=tau0+alpha P1` produces a coefficient at every harmonic rank, beginning at order `alpha^l`. Therefore an exact finite buffer is unavailable generically; a PSTF path requires adaptive tail control.

## TEFF role

Paper-I and Paper-II Bregman decompositions are valid only on their stated static domains and common normalization. They diagnose spectral, thermochemical-frame and angular information loss but do not generate transport dynamics. The regular Bose inverse must not be used outside its regular image or at an unconstrained critical/generalized point.

## Known limits

- isotropic rates: `L_chi=0`, so no source-product work-rank buffer is required;
- zero source: both adapters reduce to the BASS homogeneous transport source-free equation;
- Planck detailed balance: the positive paired one-photon action vanishes when populations and occupation obey the declared equilibrium relation;
- zero optical-depth anisotropy: the virtual-spike transmission is isotropic and rank preserving;
- full-rank limit: exact grid/PSTF representation commutation is recovered, assuming convergence and integrability.

## Special-case counterexamples

1. Same output/work cutoff fails for anisotropic source coefficients.
2. Finite-rank optical depth produces an infinite transmission tail.
3. A finite thermochemical representative can match number and energy while differing in every higher radial moment.
4. A 26-direction readout can miss continuous angular modes and therefore cannot be source authority.

## Ranked findings

- **P0:** none in the R2 mathematical contract.
- **P1:** two-photon/Raman packet-to-occupation deposition remains source-incomplete.
- **P1:** no numerical grid/PSTF parity run has used one exact REC source bundle.
- **P1:** polarized REC source and finite-electron-tilt collision are absent.
- **P2:** virtual-spike PSTF tail needs an explicit adaptive error norm and stopping rule.
- **P2:** regular TEFF diagnostics require branch/normalization checks before evaluation.

## Claim ceiling

`REPRESENTATION_NEUTRAL_REC_SOURCE_THEOREM_ONLY`. No physical-face admission, provider export, numerical parity or science promotion follows.
