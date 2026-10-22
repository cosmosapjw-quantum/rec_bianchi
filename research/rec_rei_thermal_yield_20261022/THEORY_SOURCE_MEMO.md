# THERM01 source and physics memo — 2026-10-22 KST

Scope: next source-bound thermal/ionic-yield closure after REC PR119 and REI PR220. This memo runs no ODE and makes no change to completed cohorts. It supports the new finite closure; Physical/REC U5 HOLD, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false stay fixed.

## 1. Constructive selection

Implement a new **5–60 eV source-support slice** with dynamic common gas temperature and source-fit-derived RR/DR kinetic cooling. This is a newly specified finite physical problem; it must not be described as full 5–200 eV ionic-yield closure or as a re-analysis of the old prescribed-T cohorts. Keep the full-band adapter and explicit input obligation for correlated Li and He photoionization, excitation, and secondary-electron partitions.

The reason for selecting the slice is quantitative: 60 eV is below Li I direct 1s-hole threshold 64.39 eV, below He I double-ionization threshold approximately 79 eV, and below Li I double-ionization threshold 81.032 eV. The retained ground-state H/He/Li photochannels then have a definite one-electron ionic yield under the declared ground-state, smoothed-cross-section model. He II photoionization remains active above approximately 54.4 eV. Li II and Li III photoionization are not activated by this source; their populations can still recombine if present initially. Resonant atomic excitation, secondary impact ionization, and collisions remain excluded processes, rather than being silently converted into photoheating.

An alternative full-band **conditional radiative-core channel** can be implemented, but it does not certify the physical total ionic yields; any sensitivity bracket is a scenario, not measured data. The user requested source-bound work, so a finite source-supported slice is the cleaner first completed result.

## 2. Source lookup and findings

Tools actually used: Exa search/fetch and SciSpace paper search, plus web primary-source inspection. Relevant direct sources:

1. Verner et al. 1996, ApJ 465,487, and Verner & Yakovlev 1995, A&AS109,125: author site https://www.pa.uky.edu/~verner/photo.html ; paper https://arxiv.org/pdf/astro-ph/9601009 . The 1996 fits describe outer-shell smoothed ground-state photoionization through the next inner-shell edge; inner-shell fits must be added above that edge. They do not provide charge-state branching by themselves.
2. Verner & Ferland 1996, ApJS103,467: https://www.pa.uky.edu/~verner/rec.html ; fit table https://www.pa.uky.edu/~verner/dima/rec//table1.dat ; table description https://www.pa.uky.edu/~verner/dima/rec//table.txt . Author page states a 3 K–1e9 K range for the fitted RR data. This is a potential low-temperature alternative if a new dynamic-T trajectory leaves the Badnell admitted range; such replacement must be explicit and source-pinned.
3. Badnell author RR/DR tables: https://amdpp.phys.strath.ac.uk/tamoc/RR/ and https://amdpp.phys.strath.ac.uk/tamoc/DR/ ; DR Kelvin table https://amdpp.phys.strath.ac.uk/tamoc/DR/clist_K . The pages give the exact fit forms below, including temperature-dependent B for low-charge RR. ADAS tabulated temperatures are (10^1–10^7) z^2 K, z the residual charge of the target ion. The table's E_i units must be retained: K or eV are separate files.
4. Huang et al. 1999, *Single and double photoionization of lithium*, Phys. Rev. A59,3397; author PDF https://pfwww.kek.jp/azuma/MV5.pdf ; DOI https://doi.org/10.1103/PhysRevA.59.3397 . Table I distinguishes Li+(1s²)5.39 eV, Li+(1s2s)64.4 eV, Li2+(1s)81.01 eV, Li+(2s²)151.68 eV, Li2+(2s)172.82 eV, triple203.43 eV. Below about152 eV, double ionization is correlated direct1s2s emission; above that threshold, doubly excited core channels can autoionize. A one-charge yield for every 5–200 eV absorption is a conditional approximation, and a universal two-charge Auger yield for Li K absorption is wrong.
5. Müller, Kheifets, Bray & Fursa 2026, *Photoionization of the Li atom: Convergent-close-coupling calculations with a focus on two-electron removal*, Phys. Rev. A113,033105, published2026-03-09, DOI https://doi.org/10.1103/l4xt-3sxy ; published full text https://journals.aps.org/pra/pdf/10.1103/l4xt-3sxy ; author preprint https://people.physics.anu.edu.au/~ask107/INSPEC/Muller2026.pdf . The published paper treats correlated single/double Li photoionization and its data-availability section says the numerical data are not publicly deposited and are available on reasonable request. The article is CC BY4.0. Do not claim its precise numeric tables were imported; no author contact was made.
6. NIST lithium atomic data https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable1_a.htm establishes Li I ground1s²2s and Li II ground1s², with successive first two ionization energies about5.391719 and75.6400 eV. Updated NIST ASD cited by Müller gives total double threshold81.032 eV.
7. Public code documentation at https://agnwinds.readthedocs.io/en/stable/atomic/electron_yields.html and photon_yields.html explains importing Kaastra & Mewe1993 electron and fluorescent yields (`electron_yield.data`, `kaastra_electron_yield.data`). Its displayed electron-yield examples begin Be (Z4), not Li. No Li row was found/adopted. This code is a useful future data-format precedent, but it cannot supply a fabricated Li yield.

The 2026 source is especially relevant to the full-band follow-up: it shows that a generic K-shell cascade prescription cannot substitute for Li's correlated channels. Exact full-band ionic tables are an **input-data obligation**, not a proof that the physical extension is impossible.

## 3. Energy-weighted recombination coefficient: derived relation

Assume nonrelativistic Maxwellian electrons, heavy ions at the same gas T, negligible electron/ion mass ratio correction, low-density radiative stabilization, and microscopic recombination cross section independent of the gas T. A Maxwellian rate is

    α(T) = C T^(-3/2) ∫_0^∞ E σ(E) exp[-E/(k_B T)] dE.

The energy-weighted coefficient has units J m³ s^-1:

    β(T) = C T^(-3/2) ∫_0^∞ E² σ(E) exp[-E/(k_B T)] dE
         = k_B T² α'(T) + (3/2) k_B T α(T)
         = k_B T α(T) [3/2 + d lnα / d lnT].

The relation is an exact Maxwellian moment identity for the underlying cross section. Substituting a fitted α defines a **source-fit derivative closure**: positivity and numerical derivative agreement can be tested, but accuracy of the rate fit does not automatically bound accuracy of its derivative. A cooling-rate accuracy claim requires energy-resolved cross sections or an independent cooling data comparison. This construction is not the arbitrary assignment of3k_B T/2 to every captured electron.

For VF/Badnell RR put u=sqrt(T/T0), v=sqrt(T/T1), B=B0+C exp(-T2/T), b1=dB/dlnT=C(T2/T)exp(-T2/T). Then

    α = A/[u(1+u)^(1-B)(1+v)^(1+B)],
    L = dlnα/dlnT
      = -1/2 -(1-B)u/[2(1+u)] -(1+B)v/[2(1+v)]
        +b1[ln(1+u)-ln(1+v)].

Use the cancellation-resistant expression

    θ = 3/2+L
      = (1-B)/[2(1+u)] +(1+B)/[2(1+v)]
        +b1[log1p(u)-log1p(v)],
    β_RR = k_B T α θ.

For constant B in[-1,1], θ is manifestly positive. For temperature-dependent or signed fit parameters, enforce β≥0 over the admitted domain and fail on material negatives; do not silently clip them.

For the DR source fit

    α_DR = T^(-3/2) Σ_i c_i exp(-E_i/T),
    β_DR = k_B T^(-3/2) Σ_i c_i E_i exp(-E_i/T)       [E_i in K].

If E_i are in eV, the exponent is -E_i/(k_B T in eV) and the energy multiplier is E_i times joule/eV. Some fitted c_i can be signed; these individual terms are not physical probability channels. Only the summed rate and energy moment may be adopted, with explicit domain checks. At negligible underflow, compute alpha and beta directly, without dividing beta/alpha. No need for a mean energy when the event rate vanishes.

For every RR/DR transition with ground-state binding increment χ>0, the escaping photon energy rate is n_e n_parent [χ α + β] under prompt radiative-cascade and optically thin escape assumptions. The captured electron's kinetic loss is n_e n_parent β. DR core excitation/stabilization is already inside this capture event; adding a second excitation cooling term double counts it.

## 4. Evolving thermal state and ledger

Let n_b obey dot n_b=-3Hn_b, Y_i=n_i/n_b, Y_e=q·Y, η=Σ_nuclear Y_i+Y_e, u_th=(3/2)n_b ηk_B T, u_ion=n_b I·Y. There are no nuclear reaction/decay fluxes in the selected inventory; Σ_nuclear dotY_i=0. Hence dotη=dotY_e.

Per baryon define ε_th=(3/2)η k_B T, ε_ion=I·Y. For the primary one-electron source slice,

    P_abs/n_b = Σ_i Y_i ∫ Φ(E) σ_i(E) E dE,
    H_photo/n_b = Σ_i Y_i ∫ Φ(E) σ_i(E) [E-χ_i] dE,
    C_rec/n_b = n_e Σ_parent Y_parent β_parent(T),
    P_rec_escape/n_b = n_e Σ_parent Y_parent[χ_parent α_parent+β_parent].

Φ(E) here is photon number flux per area/time/energy, already integrated over the isotropic intensity convention. Keep energy integrations in one unit, convert eV toJ once. Bound-state inventory stores χ, so the thermal ODE is

    dotT = -2HT - (T/η) dotY_e + 2(H_photo-C_rec)/(3 n_b η k_B).

Equivalently evolve ε_th>0 with

    dotε_th + 2H ε_th = (H_photo-C_rec)/n_b.

The exact retained-process local energy ledger is

    d(ε_th+ε_ion)/dt + 2H ε_th = (P_abs-P_rec_escape)/n_b.

The negative particle-count term is necessary: ionizing at fixed thermal energy adds an electron, lowering T per particle. Recombination removes a selectively captured electron, not an electron with the unconditional Maxwellian mean. A logT coordinate improves positivity but its Jacobian must include dα/dT and dβ/dT. DynamicT may leave the existing source range100–1e6K; reject such a trajectory or select/pin a broader source before running. A hidden T floor adds an unaccounted heater and is not a thermal closure.

Optional Compton exchange, free-free, collisional excitation/ionization and charge exchange need their own coefficients and symmetric ledger terms. They can be excluded in this first finite retained-process closure with their scope stated once. This does not establish complete thermodynamics or full nuclear closure.

## 5. Finite acceptance proposals

These are prospective gates, not tests already performed by this memo.

- Channel identity: for all retained photo events E=χ+E_heat+E_escape; exact source-supported yield, charge gain, and nonnegative energy partition. Below thresholds rates vanish. Reject unsupported full-band yield requests.
- Frozen rates: α andβ finite/nonnegative on a predeclared logarithmicT mesh and at any trajectory extrema; compare analytic log-slope to centered differences away from underflow, e.g.relative2e-5 plus an absolute scale for negligible rates.
- Generator: off-diagonals≥0, column conservation, isotope inventory conservation, exact electron charge counting. Extend any multi-yield channel as a distinct stoichiometric vector and record its original source row.
- Thermal limits: no radiation/no reactions yields a²T=constant; photoionization with no expansion conserves ε_th+ε_ion plus declared absorbed/escaped tallies; source-off recombination loses χ+β/α in photons.
- Ledger: integrate absorbed, escaped and adiabatic-work tallies with new ODE; endpoint residual relative to the largest accumulated energy must satisfy the predeclared numerical tolerance. Independently verify algebra at frozen states, including electron heat capacity term. A structurally shared tally alone is insufficient to establish physical source accuracy.
- Compact reuse: thermalT is scalar and equal electronic rates preserve isotope proportionality, so the previous invariant projection remains valid for the new process subset. New thermal variable and ledger accumulators extend33; do not call the new code unchanged33.
- Select a handful of newly named thermal cases and one new full-coordinate oracle only as needed. These are new IVPs, never completed REC126/REI129/warm729 reruns. No speed/scaling campaign is needed.
- Keep global convergence NOT_RUN and cooling/yield source uncertainty distinct from finite numerical PASS.

## Evidence status

Literature-supported: source fit forms and tabulated units, Li competing photochannels and thresholds, non-public2026 numerical data declaration. Derived: Maxwellian energy moment, stable RR slope, thermal particle-count term, per-baryon ledger. Implementation/numerical status: this memo implements no solver and runs no ODE. Exact full5–200eV correlated ionic-yield table: unresolved input, not imported. No strong no-go claim is made; NG1–NG7 are not invoked to promote an impossibility result.
