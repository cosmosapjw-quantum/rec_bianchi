# REC HD MULTICHANNEL AFFINITY01 | conditional two-energy thermodynamic-cycle construction

**Date:** 2026-10-29. **Scope:** immutable **2021-06-07 LAMDA HD**, 9 J-labelled states, 8 adjacent radiative transitions, 9 downward collisional pairs for each of para-H₂ and ortho-H₂, at the *only three tabulated* temperatures 50, 100, 200 K. **This is a conditional source-consistency diagnostic, not a measurement or a source correction.** No vibrational label is inferred. Original 35 Hz gate **FAIL 7/8**, full HD spectroscopy unresolved.

## Microscopic channel map and units

Let `i=J-1`, `j=J`. Define separately (i) the stored level gap `ΔE_J = hc·100 (w_J-w_(J-1))`, w in cm⁻¹, and (ii) the catalog photon energy `ε_J = h·10⁹ ν_J`, ν in GHz. Define `δν_J=(ΔE_J-ε_J)/h` in Hz, with exact SI c=299792458 m/s, h=6.62607015e-34 J s, k_B=1.380649e-23 J/K. For T>0 write β=(k_BT)⁻¹.

The source's downward radiative `A_J` has units s⁻¹. A *synthetic* blackbody at T yields occupation `n̄_J = (exp(βε_J)-1)⁻¹` and channel rates

`r^(γ)_(j→i) = A_J (1+n̄_J)`, `r^(γ)_(i→j) = A_J (g_j/g_i)n̄_J`, with `g_J=2J+1`. Thus `r_up/r_down = (g_j/g_i) exp(-βε_J)`.

The original p-H₂/o-H₂ downward collision `q^(a)_(j→i)(T)` is in cm³ s⁻¹; for a *separately specified positive* collider number density `n_a` in cm⁻³, `r^(a)_down = n_a q^(a)_down`. Source-level Boltzmann detailed balance defines the formal reverse rate `r^(a)_up=r^(a)_down (g_j/g_i)exp(-βΔE_J)`. This is conditional on same T, not a validated microscopic upward cross-section or isotope-specific scattering result. The two channels **never average** into a single collision coefficient. Additional stored collisional J=2→0 has energy `E₂-E₀`.

## Proposition A. Two-channel circulation detects the energy-column mismatch

For loop `j --(radiation down)→ i --(collision a up)→ j` define

`A^(γ,a)_J := log[ (r^(γ)_down r^(a)_up)/(r^(γ)_up r^(a)_down) ]`.

Using the explicit forward/back rates and cancelling degeneracies, A_J = β(ε_J - ΔE_J) = **−h δν_J/(k_BT)**. It is independent of collider density, Einstein A coefficient, downward q and which H₂ spin species is used, provided each channel's two rates are strictly positive. This is a dimensionless *cycle affinity for a mathematical marked-channel Markov process*.

The previous source-locked cross-energy Kirchhoff ratio is

`R_J(T) = [exp(βε_J)-1]/[exp(βΔE_J)-1]`.

Hence, writing `K_J=R_J-1`, exact cancellation yields

`K_J(T) = [exp(A_J)-1]/[1-exp(-βΔE_J)]`.

This identity was independently simplified to zero by Wolfram `FullSimplify`. It is not a first-order approximation. For δν>0 the affinity and K have negative sign, and vice versa. There is no extrapolation in T.

## Proposition B. Three-edge triangle and stationary Markov diagnostic

The two stored radiative edges 0↔1 and 1↔2 together with the *actual stored* collisional 2↔0 create a triangle even without inventing a radiative 2↔0 line. Give the triangle orientation `0 --γ↑→ 1 --γ↑→ 2 --col(a)↓→ 0`. Its dimensionless affinity is

`A_tri = log[(r^γ_01 r^γ_12 r^a_20)/(r^γ_10 r^γ_21 r^a_02)] = β[(E₂−E₀)−(ε₁+ε₂)] = h(δν₁+δν₂)/(k_BT) = −A₁−A₂`.

This holds separately for para-H₂ and ortho-H₂, and both yield the same affinity when at the same T. The collision J2↔J0 entry exists in both pinned tables. This is a source-specific nontrivial cycle, not a graph assembled from inferred extra rates.

Define `p_j(t)` for exactly nine Markov levels and form `Q_{ji}=Σ_a r^{(a)}_{i→j}` for i≠j, and `Q_{ii}=−Σ_{j≠i}Q_{ji}`. For source-positive rates, connected finite network yields a unique positive stationary `p*` satisfying `Q p*=0` and `Σp*=1`. The *formal* channel-resolved Schnakenberg entropy-production diagnostic is

`σ/k_B = Σ_(i<j,a) (p_i r^(a)_{i→j}−p_j r^(a)_{j→i}) log[(p_i r^(a)_{i→j})/(p_j r^(a)_{j→i})]`, units s⁻¹ per synthetic molecule, and is nonnegative term by term because `(x−y)log(x/y)≥0` for positive x,y.

**Strict conditional positivity:** If any δν_J≠0 and radiative and at least one collisional channel for that same pair are both positive, σ=0 would imply *both* channels have zero net flux, forcing a single p_j/p_i to satisfy two incompatible ratios. Contradiction. Thus σ>0 for this **specified artificial two-energy Markov construction**. That mathematical sign result is not physical entropy production: a real energy-conserving microphysics would require one consistently attributed energy exchange, and no actual photon/collider histories are known here. The model deliberately tests the consequences of stitching two inconsistent source columns. No physical gas heating, UVB response, dynamical solution, H5 epsilon, spectral-correction prescription or observational signal is certified.

## Numerical contract

Use the immutable private 2,289-byte source SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`, source date 2021-06-07, archived Git ref `rei_bianchi@641a725ada4be27473069c2c35005a94c2ab0248`. Temperatures T∈{50,100,200} K; two **arbitrarily chosen diagnostic collider densities**, each p/o independently equal n_a=10³ or 10⁶ cm⁻³, are not cosmological predictions. Solve the 9×9 stationary linear system at 90-digit mpmath precision; independent NumPy Float64 and Decimal100 verify populations and affinities. Replace printed photon frequencies by matching ΔE/h only in *negative-control* model, never in the owner source, admitted adapter or provider.

Pre-registered gates: immutable SHA; level/line/collider identity; 8×3 two-edge exact relation; 3 triangle temperatures; 6 finite nonnegative 9×9 stationary distributions, residual <1e-65 in high precision; 6 strictly positive source-mixed formal σ; 6 counterfactual equal-energy σ<1e-65; independent Float64 population abs <1e-8 and Decimal100 affinity abs <1e-50; source-corruption and out-of-grid negative controls; original FAIL7/8 unchanged.

**References:** J. Schnakenberg, *Rev. Mod. Phys.* **48** (1976) 571, DOI https://doi.org/10.1103/RevModPhys.48.571 (cycle affinity and Markov network theory); U. Seifert, *Rep. Prog. Phys.* **75** (2012) 126001, arXiv:1205.4176 (stochastic thermodynamics); J. Ryu, S. Yeola, D. M. Jonas, *PNAS* 2024 https://pmc.ncbi.nlm.nih.gov/articles/PMC11406287/ (Einstein detailed-balance relations, general formulation). LAMDA source https://home.strw.leidenuniv.nl/~moldata/HD.html and format https://home.strw.leidenuniv.nl/~moldata/molformat.html. Source identity and previous failures take precedence over generic literature. No novelty claim for Schnakenberg inequalities or general Markov theorem.
