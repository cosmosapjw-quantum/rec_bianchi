# THERM02 — source-bound RR/Compton compact thermal pilot

Frozen before new IVPs on 2026-10-22 KST. Workflow 1.0.0; approval v0.2.
Parent: REC PR120, `7c4af579be508cccf203d3e2a3a5aa16a4b28e38`.
This is a new cohort. REC126, REI129, warm729, THERM01 eight, PR121 thermal
eight, and other completed campaigns are reused without rerunning them.

## 1. Question and source ownership

Determine the conditional changes in temperature, ionic populations, optical
depth and separately signed matter/radiation stress when a source-backed RR
kinetic moment and Compton exchange are coupled to the existing current-state
compact34 system. Use THERM01's 5–60 eV smoothed ground-state continuum, GL4
within the existing threshold-split bins, E^-2.5 photon-number spectrum,
late Gamma_HI=1e-12 s^-1, and the same prescribed tanh UV envelope.

Mao, Kaastra & Badnell (2017), A&A 599 A10, DOI 10.1051/0004-6361/201629708,
supplies f=L/(k_B T alpha). Copy the six selected source rows, original
calc.dat/pars.dat and source lock from REC PR121
`892aad5c3e9fb0b2abd021154b62a42c39277125` without changes. Fit input is
t=k_B T/eV_J, logarithm natural, and q_initial=Z-s_recombined+1. The primary
loss L_RR=k_B T alpha_donor f_Mao is a hybrid with unchanged donor number
rates; derivative-fit loss is a separately labelled closure comparison.
DR kinetic moments retain the existing signed coefficient sums. Reuse the
upstream source-table verification; test only the new mapping/vectorization.

The 5–60 eV continuum excludes actual Li core-excitation resonances. Direct
Li I 1s-hole photoionization below its edge is zero in this source, which
does not remove the real in-band resonances. No new Li final-yield table,
nuclear channel, CI/CE, charge exchange, free-free or secondary cascade is
activated. The existing unresolved channels retain their input obligations.

## 2. State, units and physical reduction

Metric (-,+,+,+); SI units, explicit c, hbar and k_B. x=ln(a/(1/21)).
Y=n/n_b; x_e=q.Y; eta=(1+q).Y; epsilon_th=k_B w=(3/2)eta k_B T.
T=2w/(3eta). Integrate compact34; reconstruct all 21 populations and the
full63 reference using the unchanged constant P/R extended by w.

Compton creates no ion/electron number source. Common T, electronic isotope
equality and reflection-even LRS remain invariant. Continue the coupled
T -> RR/DR -> n_e -> elastic Thomson opacity -> current photon monopole
feedback. Do not replay an old ionic or photon history inside a new RHS.
Thermal baryons remain an isotropic test fluid; matter and radiation pi_ab
remain separately signed before their total is formed.

K=sigma_T c/(m_e c^2). The inherited THOMSON constant already equals
sigma_T*c [m^3/s]; multiplying it by c again is an error.
Use m_e=9.1093837139e-31 kg, exact SI h=6.62607015e-34 J s,
hbar=h/(2 pi), and a_R=pi^2 k_B^4/(15 hbar^3 c^3).

### Two different radiation owners

actual_hot:
Q_C=-4 K n_e k_B T U_gamma,
U_gamma=rho_crit,J Omega_gamma E_gamma,0/a^4 from the current state.
This is the leading nonrelativistic thermal Compton component of the
actual grey photons. Their missing recoil/induced spectrum is unresolved.

planck_reference:
Q_C=4 K n_e k_B U_ref (T_ref-T),
T_ref=2.7255 K/a and U_ref=a_R T_ref^4.
This is an independently declared external isotropic Planck bath. It is
not inferred from the actual grey photon field and is not added to Einstein
energy density. Never sum these two alternative CMB/reference sources.

For either active Compton branch, include the same low-occupation external
UV term Q_UV,C=K n_e (M_UV-4 k_B T U_UV). THERM01's GL4 nodes are not bin
centres: compute U_UV=sum(Phi_j E_j)/c and M_UV=sum(Phi_j E_j^2)/c from the
actual existing node/flux weights once, then multiply by the prescribed
UV amplitude. Phi is the angle-integrated scalar photon flux c*n_gamma,
not the net directional flux. No spectrum is re-integrated inside the RHS.
The off branch disables both the CMB/reference and UV Compton contributions.

### Affine computational form

Set (U_*,R_*)=(U_gamma,0) for actual_hot and
(U_ref,4 U_ref T_ref) for planck_reference. At each current state,
Delta w'_C=B-Aw,
A=8 K x_e (U_*+U_UV)/(3 H eta),
B=K x_e (R_*+M_UV/k_B)/H.
Six distinct (Z,q) Mao factors are evaluated once and mapped to the isotope
channels. These are exact contractions under the retained assumptions.

For fixed x,Y,geometry, the Compton+adiabatic subproblem is w'=-(2+A)w+B.
Its exact exp/expm1 solution is an independent positivity/semigroup fixture.
It is not a substitute for the coupled BDF evolution. No new time-splitting
or empirically interpolated thermal table is introduced in this unit.

## 3. Gas and transfer ledgers

w'=-2w+(Q_heat-Q_rec+Q_C+Q_UV,C)/(n_b k_B H).
epsilon_ion=I.Y. Binding energy and DR resonance kinetic energy retain
their existing owners; do not add them twice to thermal loss or escape.

d(epsilon_th+epsilon_ion)/dt+2H epsilon_th
  =(Q_abs-Q_escape+Q_C+Q_UV,C)/n_b.

Store local source transfer owners:
Q_gas=Q_abs-Q_escape+Q_C+Q_UV,C,
Q_C,bath=-Q_C, Q_UV,bath=-Q_abs-Q_UV,C, Q_escaped=Q_escape.
Their local sum vanishes. The bath transfer integrals are bookkeeping
quantities; no Compton correction is fed into the photon hierarchy or
Einstein equations. Report |Q_C|/(H U_gamma) and its x integral. For the
Planck branch also report |Q_C|/(H U_ref), with the correct denominator owner.
These measured scales do not by themselves bound omitted backreaction.

Persist GL8 and GL16 dense states/integrands for the five signed ledger
columns [absorption,escape,adiabatic_work,CMB_or_reference,UV_Compton], and
their instantaneous absolute-value integrals. Residual is
epsilon-epsilon0-I_abs+I_escape+I_work-I_C-I_UV.
Normalize by max(|epsilon0|,|epsilon|,sum_j integral |integrand_j| dx).
This is the signed-source generalization of THERM01's normalization; the
absolute throughput is integrated before taking any cancellation-prone sum.

## 4. Exactly eight new configurations

All start at z20, end at z2, save the same 193 x nodes, and use T0=1000 K,
Emax=60 eV, UV multiplier 1. Split seed is Sigma_F=.15, matter_A=.6,
radiation_A=.15. Isotropic seed is 0/0/0.

| ID | Seed | RR loss | Compton | State / tolerance |
|---|---|---|---|---|
| t02_split_mao_off | split | Mao hybrid | off | compact34 nominal |
| t02_split_mao_hot | split | Mao hybrid | actual_hot + UV | compact34 nominal |
| t02_split_mao_planck | split | Mao hybrid | planck_reference + UV | compact34 nominal |
| t02_split_derivative_planck | split | rate derivative | planck_reference + UV | compact34 nominal |
| t02_iso_mao_planck | isotropic | Mao hybrid | planck_reference + UV | compact34 nominal |
| t02_split_mao_hot_tight34 | split | Mao hybrid | actual_hot + UV | compact34 tight |
| t02_split_mao_planck_tight34 | split | Mao hybrid | planck_reference + UV | compact34 tight |
| t02_split_mao_planck_oracle63 | split | Mao hybrid | planck_reference + UV | full63 nominal |

Five nominal + two tighter + one full63 oracle = eight. The new Mao/off
case differs from THERM01's derivative/off baseline. Copy the two matching
old split/isotropic NPZs by exact hash for comparisons, without solving them.
PR122's proposed 5–200 eV / z7.9637 restart / 109-node / full63 eight-case
cohort is distinct and is not executed or relabelled here.

Nominal BDF rtol=2e-9, max_step=.025. Full63 atol is 40 geometry entries
2e-12, 21 scaled populations 2e-11, tau 2e-12, w 2e-7 K. Project that
vector with the same restriction for compact34. Tight cases divide rtol
and every atol by 100 and use max_step=.0125. This stronger new-unit
nominal allocation is frozen before results; old THERM01 gates/results
are unchanged. Retain the 3e-6 integrated-energy gate.

One numerical thread, serial science execution, 180 s cooperative per-case
ceiling including diagnostics and 1200 s total new-unit science ceiling.
Failed attempts consume the same allocation. Stop on source mismatch,
unsupported temperature, nonfinite state, solver failure, admission failure
or exhausted budget. Preserve partial returns and diagnose before repair.
No automatic extra cases, duplicate finished runs or old-suite dispatch.

## 5. Finite acceptance and pre-execution checks

Pre-ODE checks target only the new source and adapter: exact retained file
identities; six-row charge mapping and vectorized Mao factors versus the
retained scalar formula; source-unit and heat-capacity factors; Planck
equilibrium and n_e=0; actual_hot/reference distinction; independent
continuous UV U/M integrals; affine/direct-volume equality; frozen subflow
and semigroup; local gas/bath transfer; compact/full RHS mapping and the
new thermal derivative. Include sign/c/temperature-unit mutations with
explicit expected rejection. Do not rerun the old114-source-point suite.

Physical sampled gates retain the THERM01 limits: scaled population >=-2e-8;
isotope residual<2e-7; baryon residual<2e-8; electrons>=0; T in100..1e6 K
including every RHS trial seen by the thermal guard; tau increment>=-2e-10;
number monopole residual<2e-9; Einstein residual<2e-13; signed tensor sum
residual<2e-16; trace energy fraction<1e-5; exact-zero n/tritium and decay.
Finite checks apply to saved physical states and persisted accepted solver
states. Record which denser states were actually checked; no continuum
positivity claim is implied. Persist accepted BDF nodes independently of
the193 comparison samples, plus GL8/16 dense state arrays.

New local source/transfer residual<5e-12 relative to absolute source terms.
Normalized integrated gas energy residual<3e-6; normalized GL8/16 ledger
difference<3e-6. Report actual margins and peak locations.

Each Compton branch nominal/tight comparison: max relative T<3e-5,
charge fraction abs<3e-5, tau abs<3e-7, signed six-vector abs<3e-7.
The same limits apply to planck compact/full63. Show matter, radiation,
total stress and shear separately; a source/branch difference is resolved
only for observables exceeding both relevant observed refinement changes.
No performance speedup or global error-bound claim follows from this test.

## 6. Completion and next obligations

Deliver implemented code, source/input hashes, exactly-eight execution
receipts/raw arrays, data-bound PNG/PDF plots with visual inspection,
physics/code/results independent review, stage backup/publication receipts,
DAG and handoff. Current numerical study remains conditional21population
atomic/thermal test-fluid physics. N1/N2 Li final-yield resolution and a
spectral radiation-energy/Einstein backreaction closure remain separate
physical obligations. Mao source hybrid sensitivity is not statistical error.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
