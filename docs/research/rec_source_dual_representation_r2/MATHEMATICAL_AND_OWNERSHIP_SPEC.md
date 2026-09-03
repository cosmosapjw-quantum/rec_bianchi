# Mathematical and ownership specification

## 1. Scope and conventions

We use

\[
 g_{ab}=(-,+,+,+),\qquad \epsilon_{123}=+1,
\]

retain `c` explicitly, and write `e^a` for the photon propagation direction in the local orthonormal frame. An outward observed sky direction satisfies `n_sky^a=-e^a` and is not used silently in REC source formulas.

Photon occupation is dimensionless. Ordinary frequency `nu` has dimension `T^-1`. The BASS ray-length Liouville coefficients have

\[
 [R_s]=[V_s^a]=L^{-1},
\]

and physical-time coefficients are

\[
 R_t=cR_s,\qquad V_t^a=cV_s^a,
\]

with dimension `T^-1`.

This R2 contract is initially scalar/unpolarized. BASS retains authority for coherency-matrix transport, screen rotation and cold non-tilted electron-rest Thomson scattering. A polarized REC source extension requires a separate theorem and source-identity lane.

## 2. Ownership theorem

### BASS-owned state evolution

BASS owns both representations of the evolving distribution:

\[
 f(t,\nu,e)
\]

on a direct phase-space/angular grid, and

\[
 F_{A_\ell}(t,\nu)
\]

or the equivalent harmonic coefficients at generic rank. The formula-level distribution/PSTF/Wigner maps are representation changes of the same BASS transport equation.

### REC-owned source authority

REC owns an immutable source authority bundle

\[
 \mathfrak S_{\rm REC}
 =\{\eta,\kappa,\mathcal J,\mathcal B,
     D\mathfrak S,\mathcal P\},
\]

where:

- `eta(t,nu,e)>=0` is the positive emission/stimulated-emission coefficient;
- `kappa(t,nu,e)>=0` is the positive absorption coefficient;
- `J` is the source-identical jump/event family, including the virtual spike;
- `B` is accepted incoming/initial boundary data;
- `D S` contains analytic JVP/Jacobian information;
- `P` contains frame, measure, ordering, channel and byte/semantic provenance.

The net affine coefficient

\[
 \chi=\kappa-\eta
\]

is signed. The positive pair `(eta,kappa)` remains the primary physical object; an adapter may derive `chi` but may not discard the pair.

## 3. Distribution-grid adapter

The pointwise grid action is

\[
 \mathcal C^{\rm grid}_{\rm REC}[f](t,\nu,e)
 =\eta(t,\nu,e)[1+f(t,\nu,e)]
  -\kappa(t,\nu,e)f(t,\nu,e)
 =\eta-\chi f.
\]

For constant coefficients along one characteristic segment,

\[
 f_{n+1}=e^{-\chi\Delta t}f_n
 +\eta\Delta t\,\phi_1(-\chi\Delta t),
\qquad
 \phi_1(z)=\frac{e^z-1}{z}.
\]

Because `eta>=0`, this exact affine solution preserves `f>=0` even when `chi<0`. A numerical API that calls `chi` a nonnegative opacity is not equivalent to this paired-source contract.

## 4. PSTF/harmonic adapter

For a fixed frequency, write

\[
 f(e)=\sum_{\ell m}f_{\ell m}Y_{\ell m}(e),\quad
 \eta(e)=\sum_{\ell m}\eta_{\ell m}Y_{\ell m}(e),\quad
 \chi(e)=\sum_{LM}\chi_{LM}Y_{LM}(e).
\]

The exact projected source is

\[
 C_{\ell m}
 =\eta_{\ell m}
 -\sum_{LM}\sum_{\ell'm'}
  \chi_{LM}f_{\ell'm'}
  \mathcal G_{\ell m;LM;\ell'm'},
\]

where

\[
 \mathcal G_{\ell m;LM;\ell'm'}
 =\int_{S^2}Y^*_{\ell m}Y_{LM}Y_{\ell'm'}d\Omega
\]

is evaluated in the exact convention locked by BASS. The real-PSTF form is the same intertwining statement in the BASS basis.

This is not a moment closure: the source coefficients are the exact projection of the distribution-level source. A finite numerical work rank is a convergence parameter, not a new constitutive ansatz.

## 5. Exact commutation statement

Let `Pi_P` be the exact BASS distribution-to-PSTF transform. On the stated integrability domain,

\[
 \boxed{
 \Pi_P\,\mathcal C^{\rm grid}_{\rm REC}[f]
 =\mathcal C^{\rm PSTF}_{\rm REC}[\Pi_P f]
 }
\]

when all ranks are retained and the same source bundle is used.

The equality follows from linearity of `Pi_P`, the exact Gaunt/PSTF product law, and justified interchange of angular projection with the source evaluation. It is an equation-level representation theorem, not a numerical-parity claim.

## 6. Finite work-rank theorem

Assume `chi` is band-limited through `L_chi`. A target source coefficient of rank `ell<=L_out` receives a contribution from a distribution rank `ell'` only when the Gaunt triangle condition permits

\[
 |L-\ell'|\le\ell\le L+\ell'.
\]

Hence

\[
 \ell'\le \ell+L\le L_{\rm out}+L_\chi.
\]

Therefore an exact low-rank source projection requires

\[
 \boxed{L_{\rm work}\ge L_{\rm out}+L_\chi.}
\]

This bound is sharp in general. For isotropic rates, `L_chi=0`, and no extra angular buffer is required.

The clean Wolfram regression in this package uses `L_out=L_chi=2`. A distribution through rank four gives zero projection residual, while a same-cutoff rank-two input misses explicit rank-three/rank-four couplings.

For a grid projection of band-limited fields, the angular quadrature must also integrate the triple-product degree required by the target, source and distribution bands. Sampling invertibility alone is not an aliasing certificate.

## 7. Non-polynomial jump theorem

The virtual-spike map has the form

\[
 f^+(e)=T(e)f^-(e)+[1-T(e)]f_{\rm eq}(e),
\qquad T(e)=e^{-\tau(e)}.
\]

If

\[
 \tau(e)=\tau_0+\alpha P_1(\mu),
\]

then `T=e^{-tau_0}e^{-alpha mu}` has nonzero Legendre coefficients at every rank. The rank-`ell` coefficient begins at order `alpha^ell` for small anisotropy. Thus a finite-rank optical-depth field does not imply a finite-rank transmission field.

Consequences:

1. pointwise grid evaluation is an exact representation of the declared discrete state;
2. a PSTF implementation must adapt the transmission/product tail and report convergence;
3. no finite exact work-rank formula analogous to `L_out+L_chi` exists generically for the exponential jump;
4. finite Taylor expansion in optical-depth anisotropy is not an authority path.

## 8. TEFF diagnostics, not evolution

Paper I defines the static quotient-first decomposition

\[
 D_H(f\|f^\star_{E,L})
 =I_{\rm spec}^{(E)}+I_{\rm ang,L}^{(E)}.
\]

On the common massless number-energy branch, Paper II refines it to

\[
 D_H(f\|f^\star_{E,L})
 =I_{\rm shape}^{(N,E)}
  +I_{\mu\text{-frame}}
  +I_{\rm ang,L}^{(E)},
\]

provided the displayed regular representatives and divergences exist in one normalization.

These are checkpoint diagnostics for BASS outputs:

- a large spectral/shape term requests frequency/source refinement;
- a large angular term requests larger PSTF work rank or a finer angular grid;
- a large frame term shows that number information materially changes the entropy-selected reference;
- failure of regular BE realizability forbids use of the regular thermochemical inverse and triggers a full-state/critical-sector diagnostic.

They do not replace `f` by a two-field closure and do not authorize switching backends from low moments alone.

## 9. Dual-backend numerical receipt

For one exact initial state, background and REC source bundle, define

\[
 r^{(L)}(t,\nu)
 =\Pi_{\le L}f_{\rm grid}(t,\nu)
  -F^{\rm PSTF}_{\le L}(t,\nu).
\]

A valid receipt must vary independently:

- time step;
- frequency resolution and boundary treatment;
- angular grid/quadrature;
- PSTF output rank and work buffer;
- source adapter resolution;
- jump-tail tolerance.

The comparison is valid only after the two paths use the same conventions, source bytes, background bytes, initial state, physical time/ray parameter and collision tier.

## 10. Derived 26-direction readout

A 26-direction face object is

\[
 \mathcal R_{26,q}[f],\qquad q\in\{r,b\},
\]

and is a derived query on a parent BASS state. It must record:

```text
parent_state_sha256
parent_source_bundle_sha256
parent_background_sha256
representation = GRID | PSTF_RECONSTRUCTION
projection_or_interpolation_method
node_order_hash
frame/convention hash
cross-backend discrepancy if both paths exist
```

It is not a state authority and cannot self-promote a physical face.

## 11. Scope boundaries

This theorem does not establish numerical grid/PSTF parity, a source-complete two-photon/Raman deposition, finite-electron-tilt Thomson scattering, polarized REC source terms, an admitted physical face, a provider export, or `PASS_REC_PHYSICAL_SPLIT`.
