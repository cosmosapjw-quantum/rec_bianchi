# Notation amendment — source opacity versus TEFF chemical perturbation

Two independent quantities are denoted by `chi` in the source literature and the attached TEFF Paper II. They must not share one implementation symbol.

## REC source coefficient

Use

\[
 \chi_{\rm aff}:=\kappa-\eta,
 \qquad [\chi_{\rm aff}]=T^{-1},
\]

with code name

```text
chi_affine_s_inv
```

or derive it locally from the primary positive pair `(eta_s_inv,kappa_s_inv)`.

## TEFF thermochemical perturbation

Paper II writes `chi := delta eta_eff` in its shellwise linearization. In REC/BASS interface code and receipts use

\[
 \delta\eta_{\rm eff}
\]

with code name

```text
d_eta_eff
```

instead.

The shellwise inverse is therefore recorded as

\[
 \delta\eta_{{\rm eff},A_l}
 =\frac{4n_{A_l}-3r_{A_l}}{J_\xi},
 \qquad
 t_{A_l}=\frac{a_\xi r_{A_l}-c_\xi n_{A_l}}{J_\xi}.
\]

## Policy

- Existing mathematical quotations retain their source notation when clearly labeled.
- New APIs, schemas, logs and plots must use `chi_affine_s_inv` for the source coefficient and `d_eta_eff` for the TEFF perturbation.
- A test must reject a receipt that places both meanings under one unqualified `chi` field.

This amendment changes notation only. It does not change either formula or any authority/admission state.
