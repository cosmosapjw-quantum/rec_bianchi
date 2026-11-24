# Anisotropic one-temperature effective-atom source (R110)

`rust/rec_microphysics/src/anisotropic.rs` assembles the HYREC-2 TLA hydrogen
source of `hydrogen_peebles::hyrec2_one_temperature_source` for a homogeneous
anisotropic background. The derivation and the numerical checks are in BASS
`research/r110_cloud_highl_sky/THEORY.md` (D8) and `THEORY_CHECKS.json`.

Input: positively weighted directions, each with a Planck temperature T(e) and
the velocity-gradient factor f(e)=1+Σ:ee of K=H(I+Σ), Σ=σ/H. All rates are SI.

| Quantity | Isotropic HYREC-2 TLA | Anisotropic assembly |
|---|---|---|
| Matter temperature | T_m=T_r | Compton temperature of the direction-averaged occupation, kT_C=h∫n̄(1+n̄)ν⁴/(4∫n̄ν³) |
| α_B | PPB fit at T_m | PPB fit at T_C |
| β_p (n=2 photoionization) | detailed balance at T_r | ⟨β(T(e))⟩, each direction in detailed balance |
| Lyα blue-wing occupation | e^{−E21/kT_r} | ⟨f e^{−E21/kT(e)}⟩/⟨f⟩ (thick Sobolev weights) |
| Escape rate per 2p atom | r_α(H)=8πH/(3λ³n₁) | r_α(H)·(⟨f⟩ − τ₀⟨e^{−τ}/τ⟩), τ(e)=τ₀/f(e), τ₀=A_2p1s/r_α(H) |

Lemma (thick limit): for trace-free Σ with λ_min(Σ)>−1 the escape factor equals
1 to all orders in Σ; the remainder is ≤e^{−τ₀/(1+λ_max)}. A contracting
direction (f≤0) fails closed.

Tests (`tests/anisotropic.rs`): the isotropic sky reproduces the HYREC-2 TLA
source (relative ≤10⁻¹¹ for α_B through T_C, ≤10⁻¹³ for β_p, b, r_α); the
escape factor is 1 within 10⁻¹³ for τ₀=10³…10⁹ with a strong rotated shear;
the Wien average obeys Jensen's inequality and matches (x²/2−x)⟨δ²⟩ at δ=10⁻³
within 1%, exceeding it by more than 20% at a 0.1 quadrupole; invalid inputs
fail closed.

Scope: a pointwise source. A recombination history on a BASS background also
needs He, Compton heating of a separate matter temperature, and the coupling
of x_e to the native sky; these are not part of this module.

```bash
cd rust/rec_microphysics
cargo test --release --locked --test anisotropic
```
