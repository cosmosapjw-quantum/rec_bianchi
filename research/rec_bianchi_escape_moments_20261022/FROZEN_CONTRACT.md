# ANGULAR01 frozen physical and computational contract

Frozen before the first new numerical experiment, 2026-10-22 UTC.
Workflow: physmath-research-loop 1.3.0. Selected task: latest-state synthesis,
one bounded theory unit R1–R10 and its C1–C10 implementation/verification/handoff.
No automatic second research cycle. No cosmological ODE is authorized or needed
for this unit. Historical campaigns remain completed and are not rerun.

## Question and source boundary
Can a local isotropically emitted line's Sobolev escape monopole and PSTF
quadrupole in an expanding, non-tilted homogeneous Bianchi flow be evaluated
without angular quadrature when a derived error bound allows it?
Use a local orthonormal frame, metric (-,+,+,+), and c=hbar=k_B=1 in derivation.
H>0, sigma_ab=sigma_ba, trace sigma=0, S=sigma/H dimensionless.
C>0 is a fixed direction-independent line optical-depth coefficient [time^-1].
t=C/H>0; q(n)=1+n^T S n; tau(n)=t/q(n).
All directional expansion rates must be positive: q_min=1+lambda_min(S)>0.
The coefficient and emission source remain fixed during this local evaluation.

Reuse the exact MIT-licensed PR114 donor at
df95a074730ea0d13d609cf88d448f01f4a47ef1:
src/full_bianchi_hyrec/trajectory/hyrec_spike_transfer.py,
SHA256 3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9.
It supplies directional optical depth and spike attenuation. beta=A/tau is an
additional uniform-source optical-depth average, not a claim that spike
attenuation alone supplies a complete recombination emissivity model.
Do not globally substitute H_n for H in HyRec rate/evolution equations.
Use actual calls to the donor for the new scalar reference checks; use the
algebraically identical expm1 vector formula for new quadratures.

## Computational formulas fixed
beta(n) = -expm1[-t/q(n)] / [t/q(n)].
B = <beta>, Q_ab = <(n_a n_b-delta_ab/3) beta>, normalized 4pi average.
Q is an escape-probability moment; it is NOT matter stress or photon stress.

For b(q)=q[1-exp(-t/q)]/t,
b''(q)=-t exp(-t/q)/q^3<0, <q>=1, hence B<=beta_iso(t).
The Jensen gap is bounded above by M tr(S^2)/15, with
M=max_[qmin,qmax] t exp(-t/q)/q^3 evaluated at
q*=clamp(t/3,qmin,qmax).

Thick approximation: B0=1/t, Q0=2S/(15t).
r=exp(-t/qmax):
0<=B0-B<=r/t; ||Q0-Q||_F<=sqrt(2/3)r/t.
B>=(1-r)/t, so relative scalar and tensor-F/B bounds are respectively
r/(1-r) and sqrt(2/3)r/(1-r).
AUTO uses thick only if t/qmax>=log1p(1/epsilon), epsilon=1e-8.
Report log bounds when ordinary exp underflows. An underflowed zero is not an
exact-zero error certificate. Bounds certify analytic truncation under the
stated assumptions, not rigorous interval arithmetic for all floating errors.

Finite-t weak-shear checks:
B=beta_iso(t)-t exp(-t) tr(S^2)/15 + O(||S||^3).
Q=[2/(15t)] [1-(1+t)exp(-t)] S + O(||S||^2).
For LRS S=diag(-s/2,-s/2,s), -1<s<2, q=1+s P2(mu),
B=beta_iso(t)-s^2 t exp(-t)/10+O(s^3).

## Implementation boundary
One runnable Python module, bounded study/verification runner and data-bound
figures, using NumPy/SciPy and the pinned original donor.
General symmetric S: diagonalize once, exploit reflection symmetry so the
principal-frame second moment is diagonal, then rotate Q back. LRS cases have
a separate one-dimensional Gauss-Legendre reduction. Return B,Q,method,
qmin,qmax, node counts, assumptions, and separately typed analytic bounds.
No silently isotropizing Q. No quadrature-error claim from two-level difference.
Inputs must be finite. Reject nonpositive t, nonsymmetric/nontracefree S beyond
64*eps*max(1,||S||_F), and qmin<=64*eps*max(1,||S||_F).
Within that roundoff band canonicalize symmetry/trace and report correction norm.
Treat eigenbasis sign/degeneracy by covariance, never byte identity of eigenvectors.

## Frozen finite study
Nine shear spectra:
isotropic (0,0,0);
LRS s=-0.8,-0.2,0.2,0.8,1.8;
triaxial (-0.8,0.15,0.65),(-0.4,-0.2,0.6),(-0.97,0.27,0.70).
t grid = logspace(-8,3,45): 405 parameter points, not IVPs.
Nominal general quadrature n_mu=64,n_phi=128 and reference 128,256.
LRS one-dimensional 64 and 128 nodes. Evaluate auto decisions on the same grid.
No old oracle/test suite replay. A diagnosed failure permits only affected
new checks or grid subset to be repaired and rerun, preserving failed outputs.

Acceptance, per point, normalized by beta_iso(t):
- two-level |B128-B64|/beta_iso <=1e-8;
- ||Q128-Q64||_F/beta_iso <=1e-8;
- independent LRS 1D vs general2D <=1e-8 for B and Q_F;
- finite-precision Jensen/thick inequalities with 2e-12*beta_iso slack;
- Q symmetry/trace, B in (0,1], and PSD M=Q+B I/3 to 2e-12*beta_iso;
- donor scalar beta reference vs vector formula <=5e-14 relative, on
  t in {1e-8,1e-3,1,30,1e3}, q in {0.03,0.5,1,2.8}:20 new scalar comparisons;
- rotation covariance at triaxial spectra and t={0.03,1,30} <=1e-8 normalized,
  with an independently integrated lab-frame oracle;
- weak-shear scaled coefficient check using s=1e-3 at t={0.1,1,3,10}:
  scalar second-order remainder within explicit Taylor-third-derivative bound
  plus 2e-12 absolute; Q odd central difference coefficient within 1e-6 absolute;
- reject invalid domains (zero/negative t, nonfinite input, nondesired shape,
  negative or zero directional expansion, nontensor symmetric/trace conditions).

Resource cap: one thread; 180 seconds study target, hard process timeout240s.
Memory target <256MiB. Resource/call counts recorded; no detailed benchmark.
If time budget stops work, preserve partial rows and exact last case.
New cosmological IVPs=0; old IVPs=0. Grid quadratures and standalone checks
are counted separately, never added to REC126 or REI129.

## Evidence, interpretation and preservation
THEORY contains direct derivation; primary literature establishes transferred
assumptions, not an unverified claim that this lemma is new in the literature.
Only the selected source/code branches were searched for implementation overlap.
Plots show finite-depth scalar suppression, surviving escape quadrupole, and
the certified thick-switch domain. Save actual plotted arrays/CSV with hashes.
One production pass and one fresh independent physics/code review. No recursive
review or new historical regression campaign.

Stage A: inventory/source/derivation/contract checkpoint+publication+dual backup.
Stage B: implemented code and execution checkpoint+publication+dual backup.
Stage C: measured result/figures/one independent review/final DAG+handoff,
publication+dual backup. Upload ACK/metadata size and whole-byte readback stay
separate. Preserve source exact bytes and all material failed new runs.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET.
Global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
Historical REI first failed raw remains local-only.
Conditional low-z21-population ionic/thermal closure, complete nuclear network,
spectral backreaction, and high-z coupled recombination are separate obligations.
No automatic closure promotion from this local operator result.

