# THERM01 — finite source-bound thermal / ionic-yield closure

Frozen 2026-10-22 KST before new scientific integration. Owner: root scientific controller. This is a new finite research cohort, not a rerun of REC126, REI129, warm729, or any completed campaign.

## Sources and immutable roles

- REC completion/recovery anchor: PR119, HEAD `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`; latest recovery comment `6327410942`. Historical 125 main + 1 control remain separate.
- REI compact source: PR220, HEAD `8be7533cc97b3302bf42608699d6e8313ed6af8a`; compact_system.py blob `4769767f1fb6a13856c86e0c36484a95282be570`, donor subtree `33b218da2710e274aa79aa4239d1b949529c21c9`. Historical 127 main + 2 full62 oracle remain separate; first-attempt raw remains local-only in its historical preservation scope.
- Keep all 57 donor files byte-identical and keep donor verification operational. Import its coefficient tables, atomic inventory, prepared geometry, and constant P/R maps through an isolated `vendor/rei_pr220` copy. Do not run its campaign wrappers or tests.
- Atomic source coefficients are the pinned VF1996 photo/RR and Badnell RR/DR rows. Their physical units, signed DR fit terms and isotope-electronic-equality convention remain unchanged.
- Bounded latest-PR survey found REI219 HEAD `5a1e5220b301a1c497f2863d6fd823e605faba80`: separate DD/passive nuclear calculation and dossier. It is a source lead only; its nonzero transmutation would invalidate this cohort's equal-isotope reduction and is not imported.

## Selected physical problem

Non-tilted reflection-even LRS Bianchi I. SI units, signature (-,+,+,+), explicit c and k_B. Isotropic baryon gas remains a test fluid with pi_b=0. The separate collisionless massive component and photon+neutrino stresses remain signed and separately reported before summation/norms. The geometry, finite angular/radial discretization and Einstein closure are the donor's.

New photon support: 5 to Emax eV, Emax=60 for main cases and40 for one source control; number power index -2.5, 64 base log bins split at thresholds, each source renormalized to late Gamma_HI=1e-12 s^-1. UV time envelope Q(z)=0.5[1+tanh((7-z)/0.8)] is prescribed; T is dynamic. This source change is explicit and does not alter or reinterpret the old 5–200eV cohorts.

Admitted smoothed ground-state photochannels have unit final electron yield and adjacent charge increase. Emax60 is below Li I direct core-hole64.39eV, He I ionization-excitation to HeII(n=2) about65.4eV, and the higher He/Li double-ionization thresholds. Core excitation is zero for this support. Every event partitions E=chi+E_heat, with E_heat>=0. Reject any requested Emax>60 before integration. Full60–200eV final-charge/excitation data remain an explicit input obligation. No guessed Li Auger branching is inserted.

Retained thermal processes: photoelectron kinetic deposition, source-fit RR/DR capture kinetic cooling, ionization-potential storage, prompt escaping recombination cascade photons, and adiabatic work. Adopt rapid Maxwellian thermalization and low-density case-A escape. Secondary ionization, collisional ionization/excitation, CX, molecules, free-free, Compton energy exchange, excited-level kinetics, nuclear reactions and nuclear decay energy are excluded from this finite retained-process closure. No complete thermodynamic or nuclear closure is claimed. n/T inventories and their actual decay flux remain zero.

Rate domain is100<=T<=1e6K, with no temperature floor, population clipping or renormalization. If a new trial/accepted path leaves the admitted domain, preserve failure and return for a source/IC decision; do not silently extend fits.

## Equations and computational form

Y_i=n_i/n_b, Y_e=q dot Y, eta=sum(Y)+Y_e, dot n_b=-3H n_b. I_i is cumulative ground-state ionization energy in J. Define w=epsilon_th/k_B=(3/2)eta T, in K; epsilon_ion=I dot Y in J per baryon. This thermal coordinate automatically includes particle-number heat-capacity changes; T=2w/(3eta).

For the fitted Maxwellian recombination coefficient alpha(T), beta(T)=k_B*T^2*dalpha/dT+(3/2)*k_B*T*alpha, in J m^3/s. This is an exact moment identity for temperature-independent microscopic cross sections, and a declared derivative closure when applied to fitted rates. Empirical cooling accuracy remains unmeasured.

RR: u=sqrt(T/T0), v=sqrt(T/T1), B=B0+C*exp(-T2/T), b1=C*(T2/T)*exp(-T2/T). Use theta=(1-B)/(2*(1+u))+(1+B)/(2*(1+v))+b1*(log1p(u)-log1p(v)); beta_RR=k_B*T*alpha_RR*theta. DR: beta_DR=k_B*T^(-3/2)*sum(c_j*E_j*exp(-E_j/T)), with the original c converted cm^3 to m^3 and E_j in K. Signed individual fit terms are not probability channels; preserve their sum and never clip beta.

P_abs=n_b sum(Y_i absorbed_power_i). H_photo=n_b sum(Y_i primary_kinetic_power_i). C_rec=n_b*n_e sum(Y_parent*(beta_RR+beta_DR)). P_escape=C_rec+n_b*n_e sum(Y_parent*chi_parent*(alpha_RR+alpha_DR)). Do not count binding energy twice or add a second DR excitation cooling term.

At x=ln(a/(1/21)), dY/dx=atomic.evaluate(Y,T,Q,n_b).dY_dt/H. dw/dx=-2*w+(H_photo-C_rec)/(n_b*k_B*H). Geometry and tau use the same evolving n_e. New physical schema is compact34=23geometry+9element fractions+tau+w; reference full63=full62+w. Use old restrict/lift on the first33/62 only. Do not reuse donor diagnostics/thermal path or its prescribed-T Jacobian unchanged. A fresh finite-difference BDF Jacobian is acceptable; this work makes no speed claim.

Local energy ledger: d(epsilon_th+epsilon_ion)/dt+2H epsilon_th=(P_abs-P_escape)/n_b. Independently integrate dense-output absorbed, escaped and work terms with Gauss-Legendre8/16 quadrature between saved epochs. Do not introduce integrated tally states or claim that an algebraic identity alone establishes numerical accuracy.

## Finite new run contract

All new physical histories are z20 to2, x0=0 toln7,193 saved epochs. BDF nominal rtol2e-8, geometry/tau atol2e-11, isotope-scaled atol2e-10, w atol2e-6K, max_step0.025, dense output. Single process / one numerical thread; per-case cooperative ceiling180s, total science ceiling1200s. Report elapsed time only as execution evidence.

Six nominal cases (new THERM01 IDs):

| ID | Sigma_F | matter_A | radiation_A | T0 K | Emax eV | UV multiplier |
|---|---:|---:|---:|---:|---:|---:|
| thermal_iso60 |0|0|0|1000|60|1|
| thermal_split60 |0.15|0.6|0.15|1000|60|1|
| thermal_opposed60 |0.15|0.6|-0.15|1000|60|1|
| thermal_split40 |0.15|0.6|0.15|1000|40|1|
| thermal_warm60 |0.15|0.6|0.15|5000|60|1|
| thermal_uv_off |0.15|0.6|0.15|10000|60|0|

Two validation histories only: `thermal_split60_tight34` with rtol2e-10 and all atols divided by100; `thermal_split60_oracle63` with full63 at nominal tolerances. Total prospective8 unique new IVPs. These are current-model finite validation cases, never old-cohort replay. No extra grid, benchmark or broad convergence campaign. Cache successful outputs by current source/config identity and raw hash; do not reintegrate successful cases for plotting/reporting/recovery.

## Prospective acceptance and positive next action

- Unit source/yield checks: unsupported spectrum rejection; core rate exactly0; per-event charge gain1; per-event E=chi+heat relative residual<5e-14; threshold zeros; immutable donor validation.
- New fit checks:121 log-spaced T in[100,1e6] plus endpoints; summed alpha,beta finite/nonnegative. Compare analytic RR/DR derivative moments to centered-log finite differences where rates exceed1e-280, mixed relative error<2e-5; report underflow separately. Photon64/128-bin moment comparison uses5e-3 relative tolerance for nonzero source channels and preserves GammaHI normalization.
- New invariant/limit checks: RP=I, extended compact/full RHS parity<1e-12 scaled at three eligible frozen states; zero-process adiabatic w'=-2w and T'=-2T; electron-count thermal derivative identity; source-off recombination binding+kinetic escape identity.
- All trajectories:finite,193 epochs/full interval; min isotope fraction>=-2e-8; per-isotope inventory residual<2e-7; baryon error<2e-8; n_e>=0; rate temperature domain retained; tau nondecreasing to2e-10; number monopoles<2e-9; Einstein algebraic residual<2e-13; signed Pi_total=Pi_m+Pi_r to2e-16; trace energy fraction<1e-5. Reconstruct21 species explicitly, including exact zeros.
- Integrated energy gate: at all saved nodes absolute residual divided by max(initial absolute total energy, |current total energy|, cumulative absorbed+escaped+work magnitude) <3e-6. GL8/16 normalized difference<3e-6. Independent definition of end-point energy uses saved w/Y; source/escape/work are quadrature terms.
- Tight34 and oracle63 versus nominal: max relative T error<3e-5; max common charge-fraction absolute error<3e-5; max absolute tau and signed normalized-observable error<3e-7. State scope explicitly:finite representative checks, global convergence NOT_RUN.
- PASS moves to plotting/results/source-report and one independent scientific/implementation review; resolve concrete defects with one targeted repair episode, preserve failed evidence, do not expand review recursion.

## Deliverables and frozen statuses

Executable one-command path with fresh unit checks and cached new histories; raw NPZ/JSON per case; CSV plot sources; at least3 actual PNG/PDF figures (T/ionization versus elapsedMyr with redshift companion axis, energy ledger, signed stresses/finite residual comparison); inspect rendered PNGs for semantic and layout errors. Keep old donor output files unmodified. Save finite source assumptions and provenance beside results.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false. New numerical PASS is only for THERM01's stated subset. NG1–NG7 no-go admission is not applicable: no impossibility theorem is asserted.

Stage checkpoints: A source/physics contract -> B code+new unit checks -> C eight new histories+plots+scoped independent review -> D final backup/publication/handoff. Preserve exact backup and Git receipts at each boundary without repeating completed scientific work.
