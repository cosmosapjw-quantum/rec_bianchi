# PR-05C2C1B2B1E1B0 literature basis

This bounded stage is decided by repository-local source matrices and support
registries.  Literature is used only to constrain the architecture of the next
replacement.

1. **Original HyRec physics and ownership.**  The official HyRec page describes
   the original code as a time-dependent radiative-transfer calculation with
   Lyman-line feedback, two-photon emission/absorption/Raman scattering, and
   Ly-alpha frequency diffusion.  The 2011 HyRec paper further states that the
   radiation field, level populations, and free-electron fraction are evolved
   simultaneously.  Hence the native block cannot be treated as a disposable
   correction table when its physical support overlaps the COM representation.

   - https://cosmo.nyu.edu/yacine/hyrec/hyrec.html
   - https://arxiv.org/abs/1011.3758

2. **Representation-local states with a single interface owner.**  Flux-mortar
   methods retain separate nonmatching subdomain representations and couple
   them through an explicit interface flux variable.  The present project does
   not import the Darcy/Stokes equations; it adopts only the structural rule
   that a cross-interface process has one coupling owner, while each subdomain
   retains its local state and operator.

   - https://epubs.siam.org/doi/10.1137/20M1361407

3. **Atomic radiative-transfer channels.**  Two-photon decay, inverse
   two-photon absorption, and Raman scattering share a radiative-transfer
   formulation, while resonant Ly-alpha scattering produces frequency
   diffusion and recoil drift.  These sources reinforce the need for an
   explicit support/owner split rather than additive full-native plus COM
   operators.

   - https://arxiv.org/abs/0803.0808
   - https://arxiv.org/abs/0903.4925

No external source supplies the missing exterior Schur operator.  That operator
must be derived and validated from the canonical October-2012 source bytes and
the durable COM/interface contracts.
