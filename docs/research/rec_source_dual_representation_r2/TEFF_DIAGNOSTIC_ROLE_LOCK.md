# TEFF Papers I–II role lock for REC/BASS dual evolution

The attached September-3-2026 revisions are used as static state-space and information-geometry inputs. They are not imported as transport equations, collision operators, backend-selection algorithms or source authorities.

## Paper I

Paper I first contracts the radial distribution to the complete directional-energy field and only then projects to a finite natural inverse-temperature PSTF family. On its stated domain,

\[
 D_{H_\xi}(f\|f^\star_{E,L})
 = I_{\rm spec}^{(E)}[f]+I_{\rm ang,L}^{(E)}[f].
\]

The two terms have common kinetic Bregman units but measure different fibers. The paper supplies explicit positive witnesses showing that radial refinement cannot replace an omitted angular shell and angular refinement cannot recover unresolved radial shape.

REC/BASS use:

- evaluate `I_spec` and `I_ang,L` on a common checkpoint state reconstructed from either BASS representation;
- use the terms to choose the next **verification refinement axis**;
- do not replace the BASS state by the entropy representative;
- do not equate a finite truncation of beta, T, or log T beyond linear order.

## Paper II

On the common massless spine, Paper II retains directional number and energy,

\[
 N_f(e)=C\int E^2f(E,e)dE,
 \qquad
 \mathcal E_f(e)=C\int E^3f(E,e)dE,
\]

and selects the regular thermochemical representative

\[
 f^{\rm eff}_\xi
 =\{\exp[\beta_{\rm eff}(e)E-\eta_{\rm eff}(e)]-\xi\}^{-1}.
\]

Where the regular inverse exists, the massless information chain is

\[
 D_H(f\|f^\star_{E,L})
 = I_{\rm shape}^{(N,E)}
 + I_{\mu\text{-frame}}
 + I_{\rm ang,L}^{(E)}.
\]

Around an isotropic regular frame, with

\[
 n=\delta\ln N,\quad r=\delta\ln\mathcal E,
 \quad t=\delta\ln T_{\rm eff},\quad \chi=\delta\eta_{\rm eff},
\]

\[
 n=3t+a_\xi\chi,\qquad r=4t+c_\xi\chi,
\]

and

\[
 \chi_{A_l}=\frac{4n_{A_l}-3r_{A_l}}{J_\xi},
 \qquad
 t_{A_l}=\frac{a_\xi r_{A_l}-c_\xi n_{A_l}}{J_\xi},
 \qquad J_\xi=4a_\xi-3c_\xi>0.
\]

REC/BASS use:

- compute the three information coordinates only on the declared regular branch and common normalization;
- record failure of the regular Bose inverse instead of clipping or inventing a chemical coordinate;
- use the finite-cutoff entropy certificate only when its positivity patch and tail hypotheses are verified;
- keep massive direction-only and velocity-dressed moment maps separate;
- treat the Poisson/Markov velocity dressing as kinematic coarse graining, not physical time evolution.

## Backend diagnostic policy

The TEFF quantities do not by themselves decide that one backend is physically correct. A checkpoint may be classified as follows:

```text
large I_spec or I_shape:
    refine frequency/source representation in both BASS lanes

large I_ang,L with small spectral loss:
    refine PSTF work rank and direct angular grid independently

large I_mu-frame:
    retain number information in diagnostics and source accounting

regular-BE inverse unavailable:
    remain on the full distribution state; record critical/generalized-sector status

grid/PSTF disagreement with both TEFF tails small:
    suspect representation adapter, source convolution, quadrature or time integration
```

This is a verification polyalgorithm. It is not an entropy closure and it cannot promote a source, face or provider.

## Explicit exclusions

- no time-evolution theorem is imported from either paper;
- no transport solver performance claim is imported;
- no finite-rank thermochemical frame is declared equal to the fine distribution;
- no rate guarantee is used outside the paper's declared uncertainty class;
- no angular refinement is allowed to counterfeit spectral refinement, or vice versa.
