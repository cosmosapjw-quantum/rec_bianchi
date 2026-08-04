# Next stage: PR-01B1-B3B finite-volume invariant pair amplitude

## Goal

Replace the centre-sampled v0.14 amplitude cache by a fresh two-sided
frequency finite-volume integral on the exact invariant Maxwell–Jüttner
pair measure.

## Unknown to compute

For source cell \(I_s\), target cell \(I_t\), and harmonic order \(\ell\),
compute one unordered conductance

\[
\mathcal S_{ts}^{(\ell)}
=
\int_{I_s}d\nu_s
\int_{I_t}d\nu_t
\frac12\int_{-1}^{1}d\mu\,
P_\ell(\mu)\,
\mathcal I(\nu_s,\nu_t,\mu),
\]

where

\[
\mathcal I
\propto
\nu_s\nu_t e^{-h\nu_s/(k_BT_m)}
S_{\rm MJ}(q,\delta)
\overline{|\mathcal T_{2p}|^2}.
\]

The bar is the conditional transverse-atom integral left after the
Breit-frame delta reduction.

## Numerical decomposition

1. **Frequency cells:** tensor Gauss–Legendre with adaptive subdivision
   across the resonant pole surface.
2. **Angular integral:** continuous-\(\mu\) endpoint split inherited from
   v0.32:
   - backscatter coordinate near \(\mu=-1\);
   - regular middle interval;
   - coherent-forward analytic cell deposit near \(\mu=1\).
3. **Conditional atom integral:**
   - Breit longitudinal momentum fixed analytically;
   - transverse energy represented by Laguerre/exponential variables;
   - scattering-plane component uses a tangent map around each 2p root;
   - out-of-plane component uses Gaussian/Laguerre quadrature.
4. **Amplitude audit:** forward and PT-reverse amplitudes evaluated
   independently on selected nodes.

## Normalization

No fitted global factor is allowed. The invariant-amplitude adapter must
recover both

\[
\int d\nu\,\sigma_\nu=\pi r_ecf_{12}
\]

and the heavy-atom Hummer-II finite-volume kernel.

## First bounded release

Generate

\[
\ell=0,\ldots,6,
\qquad
17\times17
\]

conductances and red/blue exterior fluxes.

## Gates

\[
\epsilon_{S=S^T}<10^{-10},
\qquad
\epsilon_{\rm quadrature}<10^{-8},
\]

\[
\epsilon_{N_\gamma}<10^{-12},
\qquad
\epsilon_{\rm equilibrium}<10^{-12},
\]

\[
\epsilon_{Q_\gamma+Q_H}<10^{-11},
\qquad
\mathcal S_{ij}^{(0)}\ge0.
\]

Selected high-precision amplitude nodes require

\[
\epsilon_{\rm PT,node}<10^{-12}.
\]

Only after this bounded matrix passes should the calculation be extended
to adaptive \(\ell_{\max}=12,20,24\).
