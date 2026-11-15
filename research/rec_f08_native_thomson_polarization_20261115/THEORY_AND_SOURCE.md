# REC F08 S0 original-native Thomson angular collision and polarization

2026-11-15 KST, scoped R5→C5/C9 physical unit.
REC immutable parent #198: fa5c484405e901992501ab01795079ed8f2bdee1.
BASS original-native F08 S0 donor #328: b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6.
Original REI F08 S0 pair SHA256:
0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
Original 640 native gas+photon trajectories SHA256:
75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843.
Original 128-q sky SHA256:
a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92.

## Scientific objective

REC #198 computed unscattered Thomson opacity/visibility along 128
original rays, but not angular photon redistribution or induced
polarization. This unit records the REAL original BASS #328 Rust-native
coupled HI/HeI/HeII gas + emitted photon packet survivors at each of 160
proper-time stages in four original scenarios: Bianchi I/FLRW x
characteristic-energy/original fixed-hat photon models.
No original source file or gas solver is changed; use an isolated source
recovery and byte-locked source. Record per-source-ray photons/H and eV/H.

Compute at each *true* original source stage one leading-order
Thomson angular scattering intensity and generated linear Stokes Q/U
in the comoving electron normal-tetrad frame. Do not feed scattering
back into BASS Rust gas evolution; this is first-order Born collision
source data for a future paired photon Boltzmann runtime, not a
new coupled gas IVP, observed CMB map, or fully transported polarization.

## Units, tetrad and event definitions

Metric (-,+,+,+), c=29979245800 cm/s, sigma_T=6.6524587051e-25 cm^2,
k_B=1.380649e-16 erg/K. Native photon birth energy 13.7 eV.
Native proper dt=625000000 s, nH0=1e-4 cm^-3, helium/H number fHe=.083.
Original Bianchi I H=(1.01,0.99,1.00)*1e-14 s^-1;
FLRW H=(1,1,1)*1e-14 s^-1, t_k=k*dt.
Original native gas xHII,xHeII,xHeIII,T at t_k give:
xe=xHII+fHe*(xHeII+2*xHeIII),
ne(t)=nH0 exp[-(H1+H2+H3)t]*xe(t),
Gamma_T=c*sigma_T*ne [s^-1],
p_k=1-exp[-Gamma_T(t_k)*dt], p_k=O(1e-9).
This is an endpoint-source first-order splitting convention; gas
evolution is original native Rust stage before the scattering event.
Incoming radiation is unpolarized, source q_i are actual native
128 normal-tetrad photon propagation directions. No electron tilt,
recoil, gas heating or Klein-Nishina correction added.

## R5: Thomson angular conservation and spin-2 source

The continuum unpolarized differential phase function is
(3 sigma_T/16 pi)(1+mu^2), mu=qout dot qin.
Original 128 q midpoint sky has exact original equal-area mean:
  <q_z^2> = 21/64,
  <q_z^4> = 777/4096,
  <q_x^2>=<q_y^2>=43/128.
Thus the original equal-area midpoint quadrature is NOT exact at l=2
(<q_z^2> != 1/3), and naïve raw Stokes scattering of truly isotropic
light has spurious polarization fraction up to 0.0051302007.
This false signal can be larger than Bianchi physical anisotropy.

Define strictly positive moment-exact angular weights on the ORIGINAL
directions, only for THIS optional collision measurement:
   w_i=(1/128)[1+(4/63)(q_iz^2-21/64)].
Wolfram exact rational identity: sum(w)=1;
sum(w_i q_i^a q_i^b)=delta^{ab}/3.
All physical source native N_i and E_i remain unchanged and locked.
For scattering evaluation, project the original equal-area per-ray
photon counts and energy without changing their global actual totals:
   ntilde_i = N_i (w_i/(1/128)) * sum(N)/sum_j[N_j w_j/(1/128)];
   utilde_i = U_i (w_i/(1/128)) * sum(U)/sum_j[U_j w_j/(1/128)].
Projection weights are positive and the two normalizations are explicit.

For mu_ij=q_i dot q_j, the moment-exact quadrature phase matrix
   K_ij=(3/4)w_i(1+mu_ij^2)
has K_ij>0, sum_i K_ij=1 and K w=w. Therefore K preserves photon
number and photon energy and maps exactly isotropic native intensity
to itself in the corrected measurement quadrature.

At true original native stage t_k the source event:
   DeltaN_i = p_k[(K ntilde)_i-ntilde_i]  photons/H,
   DeltaU_i = p_k[(K utilde)_i-utilde_i] eV/H.
Its full sum is zero in each channel, not an energy-loss term.
Only leading elastic Thomson scattering, evaluated on preexisting
unscattered original photon field, is computed. No multi-scattering
or re-excitation of native photoionization is claimed.

For outgoing q_i, choose e_theta,e_phi orthonormal tangent vectors
with e_theta cross e_phi=q_i, and define Stokes Q=I_theta-I_phi.
For initially unpolarized incoming angular photon population:
  Q_i=(3p/4)w_i sum_j ntilde_j
       [(q_j dot e_phi_i)^2-(q_j dot e_theta_i)^2],
  U_i=-(3p/2)w_i sum_j ntilde_j
       (q_j dot e_theta_i)(q_j dot e_phi_i).
Energy-weighted Q and U follow with utilde_j in place of ntilde_j.
For a positive polarization density tensor each output obeys
   sqrt(Q_i^2+U_i^2) <= p (K ntilde)_i.
No circular V arises from unpolarized Thomson input.
The spin-frame-specific Q/U must NOT be identified as
gauge invariant E/B CMB harmonic spectra.

The moment-exact weights make Q=U=0 for isotropic N_i proportional
to equal-area ray mass. Compare to raw original q midpoint leakage
as a required negative control. For original BI source, physical
nonzero quadrupole should generate polarization; for FLRW source
the isotropic limit should be sharply smaller. If it is not,
classify quadrature/source numerical contamination, not a discovery.

## Execution and evidence

Restore the frozen 2026-11-03 BASS_REC_F08_S0 source-inclusive backup
in a new private scratch directory. Verify 12 original S0 source files,
51 Rust original source files, 4 original photon checkpoints and
the real 640-row native trajectory hash. Compile original unchanged
Rust primary coupled example offline. Instrument ONLY the REC-side
driver wrapper around its actual native_one output to record
per-direction surviving N and U at each of the 640 source stages,
without changing the original Rust or BASS source files.
Check 640 regenerated native gas/material/photon outcomes against
the exact original donor, distinguishing byte and numerical identity.
Then produce 4*160*128=81920 event rows and 640 physical stage
aggregation rows; no source reset and no independent synthetic IVPs.

Hostile review: source signature and proper clock; unmodified original
native ionization/energy/source conservation; quadrature l=0,l=2;
phase positivity/stochastic columns; photon number and elastic
energy conservation; isotropic zero polarization; Q/U Stokes positivity;
FLRW versus BI directional source; 640-stage physical evidence.
One bounded same-model hostile checker and negative tamper cases.
The continuum photon HHe/Thomson coupled Boltzmann collision feedback,
polarization parallel transport and observed CMB are NOT claimed.

At each R/C research checkpoint: REI canonical 28/88,
working 33/88, PhysicalFast 4/7, REC H5 physical 0/313,
all delta zero unless central REI owner expressly changes a node.
REI F05 original official tick160/131072, V2 tick163 research only;
REI F08 original paired_runtime HOLD, no source-owner replacement,
no force-push, main merge, gate widening or auto-next.
Native subagent NOT_RUN, different-author referee NOT_RUN.

Primary kernel literature: Hu & White, Phys Rev D 56 596 (1997);
Challinor, Phys Rev D 62 043004 (2000);
Sung & Coles, JCAP06(2011)036 (Bianchi polarization).
These references are scientific context, not original REI source owner.
