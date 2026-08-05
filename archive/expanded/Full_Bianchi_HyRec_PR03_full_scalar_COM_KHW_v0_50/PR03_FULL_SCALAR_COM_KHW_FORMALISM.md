# PR-03 full scalar COM–KHW amplitude

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Frequencies are ordinary frequencies
in Hz and every energy denominator is divided by `h`; `c`, `h`, and `k_B`
remain explicit.  The background is homogeneous.  Bianchi geometry enters
only through the already-locked `BackgroundSnapshot` frame adapter.

For scalar elastic `1s -> 1s` scattering in the velocity gauge, the local
atomic amplitude is

\[
 \mathcal{M}=1-\frac12\int d f_s\,\nu_s\left[
 \frac{1}{D_s^- - i\gamma_s}+\frac{1}{D_s^+ + i\gamma_s}\right].
\]

The leading one is the `A^2` seagull.  The measure contains the complete
hydrogen `1s -> np` bound spectrum and the positive continuum density.  Both
time orderings and all interference terms are retained.  Only the unresolved
`2p` pole receives the Ly-alpha natural width in this release window.

Each intermediate internal state has rest mass
`M_s=M_H+h nu_s/c^2`.  Its COM denominators are evaluated on that mass shell,
which removes the spurious reciprocity defect produced by adding an internal
energy to a common-mass kinetic energy after relativistic recoil.

Using the TRK sum, the fixed-nucleus, zero-width elastic amplitude is exactly
rearranged as

\[
 \mathcal{M}(\nu)=-\nu^2\int\frac{d f_s}{\nu_s^2-\nu^2},
\]

so the infrared amplitude is proportional to `nu^2` and the Rayleigh cross
section to `nu^4`.  This velocity/length identity is audited in the fixed-nucleus,
zero-width limit; the finite-recoil production lane is independently audited by
statewise PT reciprocity rather than claimed as a full relativistic gauge proof.
The production Ly-alpha conditional average isolates the
`2p` pole with the Faddeeva function.  The seagull plus all higher
bound/continuum channels are compiled as a source-moment polynomial; no
cross-section fit or free normalization is introduced.

The v0.50 35-state moments are regenerated through `ell=24`.  PR-01 frame
adaptation and the PR-02 nonlinear/JVP/implicit APIs are unchanged.  The
provisional `2p` lane remains explicit only for transition parity.

## Scope boundary

This PR closes the scalar elastic Ly-alpha production window
`|x|<=21.25`, which lies below the Lyman limit.  It audits convergence of the
high-intermediate-energy continuum tail but does not claim a global causal
above-ionization photon-frequency branch.  Raman channels, fine structure,
J-state interference, polarization and atomic alignment remain outside the
12-PR scalar release.  Exterior–exterior collisions remain assigned to the
boundary/Liouville module.
