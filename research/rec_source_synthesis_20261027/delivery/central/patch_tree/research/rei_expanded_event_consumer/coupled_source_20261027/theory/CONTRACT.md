# PW19 native source to coupled particle/energy operator

Status: FROZEN_FOR_ROOT_PREEXECUTION_REVIEW, R1-R5/R9 derivation complete; execution NOT_RUN. Original DAG remains 32/88. Intended original incomplete node: REC-COUPLED; result ceiling is a constructive selected-source partial. This contract grants no run authorization.

## Original authority and gates

Canonical source: research/orchestration_expansion_20261025/DAG.json at REI commit 413729993919d21895e2196cc65f0c1c007e8614, SHA256 8b93c017fa2da46f06ac4637fa85c2c61e8f2abe8cba85b6f648838499a2abf7.
REC-COUPLED original equation is dY/dt=Nu R, C(Y,T)dT/dt=Q_th+work-(partial U_th/partial Y)dY/dt; matter/radiation tensors remain separate. Original gate: "Selected source gates,independent oracle,observable error allocation; U5holds retained". Original next action is a genuinely new bounded control then separate convergence; new IVP remains unauthorized. Conditional dependencies HISTORY, LI and FIELD activate only for their selected processes. The photo-only increment activates FIELD (already admitted scoped), not retarded history or Li physics. Other native species remain spectator coordinates in this selected operator.

REC-EXP-COUPLED depends on REC-COUPLED and additionally requires full coupled residual/JVP, thermal/history state, signed matter/radiation stress and selected closed channels, IC and observable/error allocation. REI-EXP-EVENT-CONSUMER is already PASS_SCOPED_GRID044_ENDPOINT_OTHER_CHANNELS_OPEN: another event binding adds zero nodes. REI-L2 still requires a physical beta daughter and stopping provider, branch-resolved energy, baryon/charge, source domains/uncertainty and unique electron update. PW19 photoelectrons do not discharge that obligation.

REC-COUPLED lacks independently declared units, outputs and PR boundary in its source. This bounded REI consumer contract supplies these for this unit without modifying the original contract or its readiness guard. Full thermal kinetics, source uncertainty/error allocation, convergence and original owner admission remain open; passing the proposed checks does not itself close REC-COUPLED or REC-EXP-COUPLED. L4 remains false.

## Fixed source, snapshot and interface

Reuse blocker_closure_20261026/implementation/pw19_rec_callback.py (SHA256 5cb2601b98639345bca4f6f1a39536ed8924b1c6ad37cb109e974267a4705000), class PW19HeIINetwork. Constructor arguments: source_z=2.479, source_route="PW19_z2.479_HeII_exclusive", isotope_policy="ElementalElectronicEquality_He3_He4_conditional", photo_owners=("REC119_photo_HeII_one_owner",). Inherited AtomicNetwork.evaluate/rates are unchanged, source SHA256 baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80.

Reuse admitted MOMENTS.json SHA256 4856cabb34ee24d3c626b795cb1098b228e752c857dda1dc874fe4583deb936e and PW19 CSV SHA256 f93db0bb33dc6b7011cc0490f96253a489e5c7cd20cba99005b1461a3e56a5d1. Finite atomic photon domain is 54.42..50000 eV, three bands [54.42,204.42],[204.42,2000],[2000,50000]. Source coefficient Gamma=7.130091128981093e-15 s^-1. K and A are respectively primary and absorbed eV/s per absorber; per band A=54.42 Gamma+K. Physical primary support is 0..49945.58 eV. No spectral quadrature or source reconstruction.

Reuse saved CALLBACK.json SHA256 df5d289dac63d01200cbbffb30fb8c52e6760fc06748c3588c7f26c5d1e12e7e for snapshot and independent saved callback values; do not rerun donor interpolation. Original donor NPZ SHA256 ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b. Snapshot is adjacent convex eta representation at z=2.479, T=14919.863839279506 K, r=8.033643390985384 m^-3, beta=1.328080003500061, nb=10.669321142818111 m^-3; H is snapshot.geometry.H_s_inverse. Y=x/beta, nb=beta r. Physical interpolation uncertainty stays null.

Evaluate native network once at selected amplitude lambda=1 and optionally once at lambda=0 for actual native component extraction. The insertion component is evaluate(...)[photo_rhs], not full dY_dt. Compare it against native-on minus native-off at inherited source scales and saved source_on_off_dY_dt. RR/DR/decay remain available as unchanged side outputs; they do not enter the augmented source operator. Use evaluate photo_rhs and rates G0 (or native _Gphoto) for production; independent oracle builds only the two explicit source reactions from cached per-band Gamma/K/A. This oracle tests coupling implementation, not empirical validity of the imported rates.

He3II/III indices 8/9; He4II/III 11/12. Retain native exact labels, A, q, isotope policy and one photo owner. Electronic equality for He3 and He4 is conditional, with separate isotope abundances and baryon weights. n and T populations are zero at this donor snapshot; their production/decay physics remains open in the wider model.

## Constructive source operator and thermal particle correction

Use baryon-normalized state
  Z=(Y[21], zeta, w_nt, w_ext, ell),
where zeta=n_nt/nb counts selected primary nonthermal electrons per baryon, w_nt and w_ext are selected nonthermal energy and signed external photon transfer in J/baryon, and ell=log(T/1 K). w_ext is an open-source transfer ledger, not a positive photon energy density. Initial zeta=w_nt=w_ext=0 is the convention for newly accumulated selected-source increments at this snapshot; it does not assert that all real cosmic nonthermal particles are absent.

Define a=1+q, chi_th=a dot Y-zeta, xe_total=q dot Y, xe_th=xe_total-zeta. Total charge-derived electrons are still nb*q dot Y. The new zeta is a subset label, not a second electron added to charge neutrality. Bound state domain: Y>=0, A dot Y=1, nb>0, T>0, lambda>=0, 0<=zeta<=q dot Y, chi_th>0, finite all inputs. No clipping or renormalization. Per-reference form uses zeta_ref=beta*zeta and energies_ref=beta*w.

Let G be native _Gphoto and S=Y8+Y11. With frozen admitted source moments and fixed background at this instant,
  P=lambda G Y,
  e=q dot P=lambda Gamma S,
  k=lambda K_J S,
  a_gamma=lambda A_J S,
  F_Z=(P,e,k,-a_gamma,0).
Here K_J=K*1.602176634e-19 and A_J=A*1.602176634e-19. Binding energy derivative is I dot P=chi_J e, where native I is cumulative ionization energy per ion and selected threshold chi=54.42 eV. It is diagnostic only: do not add a separate binding energy state in addition to I dot Y.

The exact thermal particle source is
  dot(chi_th)=a dot P-dot(zeta)=(1+q) dot P-q dot P=ones dot P=0.
Ion count is conserved in photoionization. The new free electron remains in the explicitly nonthermal primary population. Thus the thermal electron source q dot P-dot(zeta)=0. In the common thermal ideal-gas bath U_th=(3/2)nb k_B T chi_th, the photo-only source contribution satisfies
  dot(ell)=[2 Q_th/(3 nb k_B T)-dot(chi_th)]/chi_th=0,
using Q_th=0 for this pre-assimilation operator. This is not an empirical zero-stopping claim: collisions/assimilation are a separate unqualified operator. No artificial dilution term -e/chi_th is applied.

Meaningful adverse comparator: assign all newly born electrons to thermal count while keeping primary kinetic energy in w_nt. This gives dot(chi_bad)=e and dot(ell_bad)=-e/(a dot Y). Report its nonzero negative value at the actual snapshot, beside correct zero. The comparator is a bookkeeping inconsistency with the chosen nonthermal count; it is not a new thermal evolution model.

Source energy conservation:
  I dot P + dot(w_nt)+dot(w_ext)=chi_J e+k-a_gamma=0.
Number conservation for isotope a and baryons follows A^T P=0 and each isotope indicator dot P=0. The change in ionic charge equals e; total charge neutrality uses that electron once.

REC124 ComptonFull63._compton_state uses xe=q dot Y and eta=(1+q) dot Y, and compton_logT_rhs uses xe B/(H eta). That source is interface evidence, not an importable full63 assembly here (its ThermalSystem/compton_budget dependencies are absent). Naively inserting zeta while retaining all qY as thermal electrons would change its physics. Similarly native RR/DR uses ne=nb qY; after zeta>0 a full thermal recombination model requires a qualified bath-electron treatment and separate nonthermal rates. This unit neither modifies those inherited routines nor supplies their caloric closure. It implements the actual native photo component as an augmented coupled source boundary.

## JVP, normalization, clocks and positivity

At fixed T/source shape, for directions (v[21], dzeta, dw_nt, dw_ext, dell, dlambda):
  dP=lambda G v+(G Y)dlambda,
  de=q dot dP,
  dk=K_J[lambda(v8+v11)+S dlambda],
  da_gamma=A_J[lambda(v8+v11)+S dlambda],
  dF_Z=(dP,de,dk,-da_gamma,0).
Derivatives of source with respect to zeta,w_nt,w_ext,ell,nb are zero in baryon normalization. dchi_th=(1+q) dot v-dzeta belongs to the state-domain/thermal diagnostic, not to the zero source row. At lambda=0, F_Z=0 while amplitude derivative is finite.

Per reference, f_ref=beta F_Z for reaction and reservoir components; d f_ref=dbeta F_Z+beta dF_Z, with dbeta=A dot dx and v=(dx-Y dbeta)/beta. zeta_ref/energy_ref conversion is required only if those state coordinates are actually passed per reference; do not mix the two normalizations. For selected nuclear-conserving source beta is constant along its physical evolution. Physical source densities are nb F_Z, with derivative dnb F_Z+nb dF_Z. Physical per-reference equivalent is r f_ref. Species rates are s^-1, nonthermal number source m^-3 s^-1, powers J m^-3 s^-1, and log-temperature source s^-1.

For eta=log(a/a_start), d/deta=H^-1 d/dt, use F_eta=F_Z/H and dF_eta=dF_Z/H-F_Z dH/H^2 once. H>0 and finite. The fixed donor H is prescribed, not source-induced geometry feedback. The clock JVP may use an independent dH control; it is a local quotient derivative, not a cosmological H equation.

At physical boundaries Y_II=0, that loss source vanishes; Y_III=0 has nonnegative influx; zeta=0 has nonnegative source. The gap q dot Y-zeta has exactly zero source derivative, and chi_th remains unchanged. Nonthermal energy rises for positive source. The signed external debit can decrease without a positivity bound because its energy reservoir is prescribed/open. No finite step or orbit is needed to demonstrate these inward/tangency conditions.

## One bounded implementation and checks

Proposed API: augmented_photo_source(network, Y, T_K, nb_m3, lambda_source, zeta_per_baryon=0, H_s_inverse=None, v=None, dlambda=0, dnb=0, dzeta=0, dH=0). Return source/JVP vectors in native and optionally eta clock; source-specific thermal and charge counts; per-band/totals energy ledger; physical number/powers and JVP; bad-allthermal comparator; domain and owner metadata. Store exact input identities and actual source status. Keep unknown provider/model/isotope/continuum uncertainties null.

Freeze inherited floating checks: native component identity, per-band energy and analytic conservation/JVP 2e-14 relative to positive event/power scales, never max(1,tiny). FD remains 2e-8 with positive trial controls and h=0.01 (the previous diagnosed hydrogen repair step); no tolerance loosening. A new direct bilinear source JVP may be independently checked by the explicit two-event oracle at 2e-14 without replaying full native Jacobian columns. If using FD, at most one changed aggregate direction with positive HeII trials, fixed zeta=0, and one amplitude/H quotient direction; zero rows require exact zero or natural sum-of-operand scale. A zero-temperature source assembled from exact cancellation may be checked exactly after the individual nonzero terms have passed independent checks.

Minimum discriminating checks:
1. Exact source/snapshot/component identity, chosen two species pairs, selected photo ownership; cached source sums reused.
2. Production native photo component versus explicit event oracle per component; source-on/off difference uses inherited checks only as needed for changed insertion.
3. Charge-derived e equals zeta source, thermal count and its JVP vanish; source-only energy/JVP balances with unique binding/nt/external owners.
4. Nonzero bad-allthermal dilution comparison at actual state; correct logT source/JVP zero.
5. Physical-density and eta-clock products/JVP including dnb and dH; fixed-comoving reference map with unchanged beta identities.
6. Boundary source-off and HeII-zero controls; reject negative lambda, nonpositive nb/H/T, zeta<0 or zeta>qY, invalid identity/owner and nonfinite inputs. Reject attempted activation of full RR/DR thermal evolution through this source API.
7. One independent changed-dependency review of equations, actual implementation/output and gate scope.

No new scientific run by theory lane. Proposed scientific child target <=1.0 CPU s, hard <=1.5 CPU s, wall <=8 s, memory <=512 MiB, one worker and BLAS thread. Root freezes exact command and cumulative debit before GO. Known planning debit at latest root message 11.766889911 CPU s; temporary total cap14 is root-only, expires after phase back to original10 without resetting debit. Main595.225063/600 and NO_MORE_IVPs remain.

No replay: prior82 native passing checks plus2 repaired checks; prior83/13/72; completed spectral moments/quadrature, original249 compiler tests, prior species inventories, donor trajectory/interpolation, ANGTHERM01/02, C3/localflow/D10 suites, HE101 active reservation, any full native21/33/63/30 client suite. No new IVP, new thermalization fraction, full150eV kinetic injection, spectrum extension, H6 trace, HD refit, n/T physical source, or source-induced H/shear evolution in this unit.

## Optional isotropic pressure-source bound, without a new quadrature

Under the selected isotropic photon bath, stationary unpolarized target and no preferred field, the ensemble primary source is rotationally invariant even when the single-event differential distribution is not uniform. Its STF pressure source vanishes by symmetry. This statement does not supply a resolved electron angular law or recoil model. Let dS(E)>=0 be the admitted primary count-source measure in m^-3 s^-1, E the kinetic energy in joules, and M=m_e c^2>0. The isotropic kinetic pressure-source trace per direction is
  dot(P_nt)=(1/3) integral [E(E+2M)/(E+M)] dS(E).
This follows p*v=E(E+2M)/(E+M), not a monoenergetic replacement. Alpha(E)=(E+2M)/(3(E+M)) decreases because alpha'(E)=-M/[3(E+M)^2]<0. Thus for E<=Emax=49945.58 eV,
  alpha(Emax)*Q_nt <= dot(P_nt) <= (2/3)*Q_nt,
where Q_nt is the actual positive primary power in J m^-3 s^-1. This can be reported as a diagnostic interval, not as a constitutive pressure closure. For immediate SI output requiring no new physical-constant acquisition, use the weaker rigorous universal interval [Q_nt/3,2 Q_nt/3]; report the tighter formula symbolically unless an explicit electron-rest-energy constant identity is supplied. No new spectral quadrature, angular sampling or mean-energy delta spectrum is permitted. Binding and signed external photon owners remain separate; this interval is solely the primary-electron matter pressure source. Do not insert this interval as an Einstein source or identify it with an evolved pressure tensor. The diagnostic adds no node completion.

## Evidence and scientific axes

Two new remote Wolfram exact checks establish augmented count/energy JVP and density/clock product rules. WOLFRAM_CHECKS.json preserves commands, outputs and one corrected charge-vector transcription error. Remote CPU is UNKNOWN_NOT_ZERO; no local scientific Python was run by theory. Prior projective normalization check is reused.

Symmetry/gauge: isotropic normal-tetrad prescribed photon source; passive rotations preserve scalar coefficients. No observer boost, angular electron law, new gauge fixing or xAct geometry calculation is used.
Invariants: isotope nuclei/baryons, charge-derived total electrons, thermal/nonthermal electron partition, selected binding/primary/external energy and its tangent.
Actual observable: finite snapshot native abundance/electron birth source, primary and absorbed power, zero pre-assimilation thermal response and the quantified spurious-allthermal comparator. No reionization history, optical-depth/CMB prediction or empirical stopping rate is inferred.

R8 admission remains root/independent-review responsibility. Successful finite implementation is positive source-to-coupled progress, count effect0 and REC-COUPLED PARTIAL until original selected-source thermal/error/convergence obligations are met. No strong no-go is claimed.

