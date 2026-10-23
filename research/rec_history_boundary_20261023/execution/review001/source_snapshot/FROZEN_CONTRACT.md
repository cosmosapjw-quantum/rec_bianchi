# REC-HISTORY-01: native history boundary contract

Task date: 2026-10-23 (Asia/Seoul). This file is frozen before implementation and
the first finite-case execution. Parent REC-HISTORY remains a larger node; this
unit supplies a source-bound finite adapter and its explicit remaining inputs.

## Authority, source and reuse

The user selected REC-HISTORY after REC-LINE02, through rei_bianchi commit
0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17. REC source parent is
a7c46fd8338971e2cefa776f5dd7b25a46974990, root tree
dfa61d68aacfd3d3adc7ac5a5603f10e67349e3e. No applicable root or research AGENTS.md
exists at this pin. Current branches/PRs were read; a separate history branch
and path are used. The original LINE02 branch and all its artifacts are immutable.

The LINE02 final companion receipt has now been found and both providers'
metadata confirmed. Reuse its 194 checks and completed review, primary elapsed
2.077208039998368 s, 202 rank queries, and six historical off-grid probes without
replaying any of them. Preserve old unavailable raw records and U5 holds.

Exact sources: ../rec_line_native_owner_20261023/vendor/hydrogen.c (37471 bytes,
SHA256 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b),
hydrogen.h, the retained native CSV (SHA256
3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7), and the already
prepared M/source/X0 in results/attempt001/PREPARED_BLOCKS.npz. The saved arrays
are reused as inputs, without running the LINE02 preparer or solver campaign.

## Scientific contract

Signature (-,+,+,+), local non-tilted orthonormal frame; time in s, energy in eV
internally and J in ledgers; occupation and departures dimensionless. Keep c,
hbar and k_B explicit in the report. Native LYA_FACT=4.662899067555897e15 cm^-3
and E21=10.198714553953742 eV remain the source convention. The native phase
measure G_N=3*1e6*LYA_FACT m^-3 is distinct from the modern-SI E^3/(pi^2 hbar^3 c^3).

For s=xr_p/(3*x1s), u=tau/q, T=exp(-u), A=-expm1(-u), the local outgoing map is
d_out=d_in+(s-d_in)*A. Require x1s>0, tau>=0, q>0, finite inputs and nonnegative
absolute incoming and source occupations f_W+d_in and f_W+s. Signed departures
are valid; clipping is forbidden. f_W=exp(-E21/TR_eV) specifies the native Wien
reference. Store log transmission=-u even if T underflows. This local ray map
has an exact finite-opacity JVP; no angular propagation is inferred from it.

For q=1 the exclusive boundary number flux is G_N*H*(d_out-d_in). It equals
nH_SI*r0*A*(xr_p-3*x1s*d_in), with r0=LYA_FACT*H/(nH_cm3*x1s).
Use the stable difference (s-d_in)*A to compute the flux. The same event owns
atomic internal energy -E21_J*R and radiation +E21_J*R. Writing outgoing
occupation transfers the event to the transport boundary; it does not add a
second radiation source. General q labels a local directional flux only.

Native scalar transport uses eta=ln a, eta_emit=eta_face-ln(E_source/E_target),
the native two-neighbor linear interpolation, and strictly known prefix columns.
iz<2 or eta_emit<eta0 returns a thermal departure zero. For iz>=2,
eta_emit>=eta0+h*(iz-1) is rejected, including exact equality. No extrapolation,
negative weighting, signed-departure clipping, or future data reads are admitted.
At a knot the value is continuous and the query derivative is one-sided; callers
must not infer a two-sided derivative there. The 313 actual source-to-target links
are read from fplus_from_fminus; the outgoing record has 311 bins and 3 lines.
The implemented native history link is scalar FLRW (q=1). A directional Bianchi
history owner must supply a geodesic energy/direction/frame map in a later unit.

At fixed thermodynamic/geometry coefficients the native 313x313 matrix M is
independent of incoming u=(virtual311,Lya,Lyb). The RHS increment is B*du:
row0=3*r0*x1s*1.664786871919931*du_Lyb; row1=3*r*x1s*du_Lya;
virtual_b=Tvv0_b*x1s*P_b*du_b. P_b is the literal native branch in hydrogen.c.
For finite direct Lya use r=r0*(1-exp(-tau)); only its original diagonal/source
pair is replaced. dF=Mstar*dX-B*du and dX=Mstar^-1*B*du. Native virtual outgoing
updates and Lyb/Lyg remain source-owned. The history derivative includes both
interpolated past-value tangents and query-time tangents. Thermodynamic coefficient
derivatives, a new IVP, and the full cosmological Jacobian are separate obligations.

## Error allocation, frozen before code

1. Arithmetic/source parity: source C/Python interpolation absolute error <=64eps
   times the sum of absolute weighted values (floor 1e-300); no tiny-net scale.
2. Local outgoing/reference and number-energy closure: <=128eps gross term scale;
   tau=0 and equilibrium have absolute zero or the corresponding gross-scale gate.
   High-precision reference uses 80 decimal digits and the actual binary64 inputs.
3. JVP of local boundary and history composition: scaled discrepancy <=5e-9;
   full313 backward residual <=5e-12; the scale is the sum of absolute operator
   terms. Cross-knot finite differences are not used as smooth derivative oracles.
4. Interpolation error: if |d''(eta)|<=M2 on the sampled cell, error <=
   M2*h^2*alpha*(1-alpha)/2 <= M2*h^2/8. Include transported endpoint uncertainty
   (1-alpha)*e0+alpha*e1. Propagate this envelope through the boundary and B/Mstar
   without conflating it with floating-point error. Two explicit smooth analytic
   histories, three fixed spacings and a bounded finite set of queries validate
   this conditional bound. Their domain is manufactured and labelled as such.
5. Actual physical-history calibration: the retained one-state CSV contains no
   retarded-history time series or independent same-domain curvature/error witness.
   Its quantitative interpolation allocation remains INPUT_DEPENDENT_UNCALIBRATED.
   The conditional bound and manufactured validation do not close that gate.
6. The local finite transfer is exact within the frozen ground-opacity/Wien model.
   Actual directional transport, real history accuracy, field feedback and global
   convergence each retain their own claim gate.

## Fresh allocation and finite execution

Allocation REC-HISTORY-01-20261023: at most 60 cumulative process CPU seconds,
180 cumulative execution wall seconds, 1 CPU thread and 1 GiB RSS for new finite
checks/plots. This does not reset any inherited ledger. Record actual CPU/wall
per attempt. Primary subprocess timeout 90s. A single independent changed-source
review may execute up to four risk-directed tiny additional cases within this same
allocation. Any diagnosed repair preserves failed outputs and reruns affected
checks only. No old tests/campaign, native full runtime or new IVP.

Primary maximum: 54 local ray controls (6 tau x3 q x3 drive types), 20 scalar
interpolation controls against extracted unchanged native C, one native 313-link
mapping comparison, 12 derivative directions, 3 frozen full-system history RHS
directions (<=8 total dense RHS solves, no native preparation), two analytic history
families x3 spacings x<=8 queries, <=20 invalid/owner cases, four deliberate
sign/normalization/future-read/duplicate-source mutations, and two figures from
the saved rows. Include tau=0,1e-10,.3,2,30,native tau; q=.6,1,1.4; emission,
absorption,equilibrium. Full histories used in tests are manufactured fixtures.

The standalone C oracle extracts interp_Dfnu and fplus_from_fminus from the pinned
source, with source constants. It is a finite function oracle, not the native
recombination runtime. Preserve the extracted bytes and compilation command.

## API shared with the independent harness

code/history_boundary.py provides:

- boundary(d_in, xr_p, x1s, tau, q=1, reference_occupation=0) -> dict with
  outgoing, delta, transmission, absorbed_fraction, log_transmission, source.
- boundary_jvp(d_in,xr_p,x1s,tau,q,dd_in,dxr_p,dx1s,dtau,dq) -> float.
- interpolation(eta0,h,values,iz,eta) -> dict value,k,alpha,thermal,query_slope,
  at_knot; interpolation_jvp(result,dvalues,deta=0) -> float.
- interpolation_envelope(h,alpha,curvature_bound,left_error=0,right_error=0).
- native_links(energies_eV) -> (source_indices,target_energies,source_energies),
  outgoing order bins311,Lya,Lyb,Lyg; incoming bins311,Lya,Lyb.
- incoming_history(eta0,h,outgoing_history,iz,eta_face,energies_eV) -> dict
  incoming,stencils; incoming_history_jvp(result,history_tangent,query_tangent=0).
- load_frozen(csv_path,prepared_npz) -> FrozenHistoryMap with Mstar(tau),
  source_increment(du,tau), outgoing(X,incoming,tau), outgoing_jvp(dX,du,tau),
  plus energies,x1s,r0,TR,nH,H,X0,u0; tau defaults to native infinite-depth
  convention for the full native history map. Local finite-ray tests are separate.
- line_ledger(d_in,xr_p,x1s,tau,nH_cm3,H,q=1,owner='boundary') -> dict R,
  atomic_internal_J_m3_s,radiation_J_m3_s,stable_jump,normalization. Only one
  radiation owner, 'boundary' or 'event', is accepted; a sequence/duplicate is rejected.

FrozenHistoryMap is a scientific sandbox adapter. Existing production modules are
unchanged. The two source functions and adopted history coefficients are attributed
to exact paths/blob hashes. No speedup claim is made.

## Completion and publication

Complete this unit after source mapping, derivation, finite checks, actual PNG
inspection, one independent review, expected-SHA publication and Dropbox/Drive
ACKs. Record R1-R10/C1-C10 with real evidence. Parent REC-HISTORY is complete only
after its actual-history calibration and selected propagation owner are admitted;
this unit may end COMPLETE_SCOPED_BOUNDARY while the parent is PARTIAL.
Update the global DAG, machine-readable claim gates and handoff accordingly.
Keep Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
