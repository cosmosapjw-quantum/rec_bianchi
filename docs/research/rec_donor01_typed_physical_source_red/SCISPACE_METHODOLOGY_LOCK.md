# SciSpace methodology and physics-source lock

## Search questions

Two fresh semantic searches were used:

1. What interface contract is required for primordial-recombination emission,
   absorption, stimulated emission, two-photon decay, Raman scattering, and
   atomic-rate provenance in a frequency-resolved radiation solver?
2. How should modular multiphysics software validate units, source coupling,
   Jacobians/JVPs, restart provenance, separate-effects tests, and coupled
   convergence?

## Physics-source findings

### Hirata, *Two-photon transitions in primordial hydrogen recombination*

- Physical Review D 78, 023001 (2008).
- DOI: `10.1103/PhysRevD.78.023001`.
- Two-photon resonances include optically thick sequential one-photon channels;
  a single effective local coefficient is not generally sufficient.
- Raman scattering and two-photon recombination require related radiative
  transfer machinery.

Contract consequence: keep nonlocal two-photon/Raman kernels distinct from a
local one-photon affine occupation pair.

### Ali-Haimoud and Hirata, *HyRec: A fast and highly accurate primordial
hydrogen and helium recombination code*

- Physical Review D 83, 043513 (2011).
- DOI: `10.1103/PhysRevD.83.043513`.
- HyRec evolves the radiation field with level populations and the free-electron
  fraction, includes higher-level two-photon effects and Lyman-alpha frequency
  diffusion, and exploits a particular sparse equation structure.

Contract consequence: source values, radiation-state coupling, and algorithmic
provenance are separate from an angular representation chosen by a consumer.

### Chluba and Thomas, *Towards a complete treatment of the cosmological
recombination problem*

- Monthly Notices of the Royal Astronomical Society 412, 748 (2011).
- DOI: `10.1111/j.1365-2966.2010.17940.x`.
- The treatment explicitly solves Lyman-series radiative transfer and includes
  two-photon and Raman processes from multiple shells.

Contract consequence: a representation-neutral source interface must leave
room for frequency-nonlocal terms and must not promote a manufactured local
pair into complete recombination microphysics.

## Software-verification findings

### Ragusa, Mahadevan, and Mousseau, *Verification of multiphysics software:
space and time convergence studies for nonlinearly coupled applications*

The paper distinguishes convergence of individual components from nonlinear
consistency of the coupled application and uses space/time convergence studies
for the composite problem.

Contract consequence: an eventual REC--BASS join requires its own coupling and
convergence evidence; component tests alone do not provide it.

### Mesina, Aumiller, and Buschman, *Extremely accurate sequential verification
of RELAP5-3D*

- Nuclear Science and Engineering (2016).
- DOI: `10.13182/NSE14-151`.
- Sequential verification explicitly covers repeat-step, restart, multiple-case,
  and coupled/uncoupled modes.

Contract consequence: trajectory, event, and restart identities are
load-bearing source inputs rather than incidental metadata.

### Gaston et al., multiphysics software based on JFNK/MOOSE

The work motivates explicit coupled residuals and physics-aware interfaces when
multiple domain applications share one nonlinear solve.

Contract consequence: analytic JVP or an explicit no-JVP status must be typed;
a hidden finite-difference fallback is not equivalent evidence.

## Authority effect

```text
authority_effect = NONE_METHOD_AND_SCOPE_ONLY
```

These papers support the separation of local and nonlocal source laws, explicit
coupler contracts, restart/Jacobian verification, and coupled-convergence
requirements.  They do not determine REC signs, source bytes, numerical values,
Git identities, BASS projection semantics, provider admission, or scientific
claim promotion.
