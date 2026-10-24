# REC-HISTORY-02 — retarded characteristic and occupation-reference connection

User date: 2026-10-24 Asia/Seoul. Controller contract, frozen before implementation.
Policy: the explicitly supplied physmath-research-loop 1.0.0, full R1–R10/C1–C10;
current plugin 1.3.0 constructive/finite-review rules are compatible supplements.

## R1–R2. Position, authorization and reusable evidence

The selected next leaf connects the existing REC characteristic owner to the
already reviewed HISTORY01 finite boundary. It implements a retarded energy
crossing, source direction, reference-occupation transport, fixed-cell tangent,
and conditional error propagation. It also admits a bounded existing actual h4
history prefix as data, subject to the producer's time-column mapping.

REC base a7c46fd8338971e2cefa776f5dd7b25a46974990 has no root/research AGENTS;
the recovery publication is 93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa, draft PR130.
Central base is 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17. Its AGENTS requires
mechanical central serialization to use a coding executor and independent review.
REI-L0 is owned by another thread; its paths and budget are reserved.

The previous HISTORY01 608 primary +14 independent checks, native LINE02
194 checks, and C7/C9/G1B completed runs are reused, not replayed. The restored
checkpoint SHA256 is 3f579aca52addb0bc1b638ca23d8e733567696f5479323c00489d097c5d5f110;
114 payload hashes and ZIP CRC115 were checked after the runtime transition.
Prior failures, runtime interruption, holds and cumulative ledgers remain intact.

Source owners:

- REC `src/full_bianchi_hyrec/trajectory/axisymmetric_batched.py`, Git blob
  96a4769d46635ee33fc1f408d6645680383f842f, SHA256
  68ba14db113cd376683cdeabeea141aaa53ce311daffcc3677f94ac48a1c47bc.
- REC `background/axisymmetric_bianchi_i.py`, blob
  eaabdc4fac25bab3f2f65e4f59ec360b76af8238, SHA256
  5296880dbf2d1b00e2810c969e6a0406b46f10acff04c794e8f718aff5813955.
- REC generic angular characteristic blob c6676ee112a892bb558ab8aab670481617201c7f.
- BASS G1B 28b7705cbb236c26e1b273335f6da7e9da4d1aaf supplies the general
  non-tilted frame law; its V/VIII moment/radial histories do not supply REC spectra.
- Actual h4 NPZ blob f3d1d58563ea24bc34c977efc67106e1936cd5cc, 119349 bytes,
  SHA256 b2489168155ad1a18a887a880eb0ca90376be5506c3c61d6bf06e9e70007c54c.
  It contains virtual[311,24], Lyman[3,24], states17, steps16, h=2.1225e-5.

Latest-source reconciliation includes 9 relevant repository branch inventories
(REC147+REI263+external924), all REC129/REI221 PRs, traceable conversation comments,
relevant Dropbox/Drive listings, ANGTHERM02 and HE-ANG receipts. Enumeration
coverage and unavailable raw ChatGPT search are recorded separately. ANGTHERM02
is adopted only as a prescribed-bath Li-threshold response; HE-ANG actual supplier
remains pending. They do not close actual REC time interpolation calibration.

## R3–R5. Convention, construction and implementation equations

Use metric (-,+,+,+), proper normal-frame photon propagation direction n=p/|p|,
dimensionless eta=ln(a), photon energy E=ħω in the same units as k_B T. Restore c
in p_i=a exp(beta_i) (E/c)n_i. Keep c, ħ, k_B in physical statements; energy and
occupation ratios in code are dimensionless. The literature's conformal eta and
observed direction d=-n are not identified with these variables.

In general a homogeneous non-tilted frame gives d ln E/dt=-H-sigma_ab n^a n^b.
On H>0 and q=1+sigma_nn/H>0, a source line crossing satisfies
integral[eta_s,eta_t] q(eta,n(eta))deta=Lambda=ln(E_s/E_t).
The source direction follows the source-owned frame/curvature characteristic.
This leaf implements the exact Bianchi I subclass and specifies the general
interface. It does not numerically integrate a new cosmological history.

For beta_i(eta)=b_i eta+constant, sum b_i=0 and a_i=1+b_i>0, set
Delta=eta_t-eta_s, g_i=n_ti exp(a_i Delta), D=||g|| and n_si=g_i/D.
The retarded equation F(Delta)=ln D-Lambda=0 has
F'=q_s=sum a_i n_si^2 in [a_min,a_max]. For Lambda>=0 it has the unique root
Lambda/a_max<=Delta<=Lambda/a_min. The Lambda=0 endpoint is Delta=0.
For the existing REC LRS convention beta=(-B,-B,2B), use b=(-B',-B',2B');
then the map reduces exactly to the existing C9 source formula. This is reuse
of its Killing map, with a new retarded crossing and boundary composition.

Evaluate log D and normalized directions with a shifted exponential/log-sum
form. Axis components may vanish; do not divide by n_ti. For an admitted tangent
n_t·delta_n_t=0, sum delta_b=0,

delta_Delta = [delta_Lambda - sum n_si exp(a_i Delta-ln D) delta_n_ti
              - Delta sum n_si^2 delta_b_i] / q_s.
delta_eta_s = delta_eta_t-delta_Delta.
v_i=exp(a_i Delta-ln D)delta_n_ti+n_si(Delta delta_b_i+a_i delta_Delta).
delta_n_s=v-n_s(n_s·v).

Unrepresentable transformed inputs/tangents are rejected explicitly. Floating
underflow of a physical occupation is allowed; exponent overflow is avoided by
using log arguments. Direction inputs are finite 3-vectors with unit norm within
64eps, normalized only within that roundoff. Shear trace tolerance is 64eps times
max(1,||b||_1). Invalid nonpositive a_min is outside this unique-root contract.

Collisionless propagation preserves absolute occupation f. Native HyRec stores
departure d=f-W, W(x)=exp(-x), x=E/(k_B T), not exact Planck occupation. Therefore

d_in = H(eta_s,n_s)+W(x_s)-W(x_t).

For the selected reference T_s=T_t exp(Delta), x_s=x_t exp(Lambda-Delta).
This temperature is a reference owner, not a newly solved gas temperature.
The offset vanishes in FLRW and need not vanish in anisotropic propagation.
Evaluate W(x_s)-W(x_t) with exp(-min(x_s,x_t)) and expm1 of a nonpositive
argument; retain a signed finite answer even when one or both exponentials
underflow. Never clip a negative departure when the absolute occupation is valid.

delta_x_s=x_s(delta_ln_x_t+delta_Lambda-delta_Delta),
delta_offset= W_t x_t delta_ln_x_t-W_s delta_x_s.
For x exp(-x), use a stable/log-domain evaluation so infinite limiting x gives0.
The full history tangent is
delta_din=delta_H_data+H_eta delta_eta_s+grad_n H·delta_n_s+delta_offset.

The selected directional history representation is a time-linear polynomial
H=c0+v·n+n^T Q n (10 coefficients: scalar,3vector,3diagonal,3offdiagonal).
Each coefficient uses the unchanged HISTORY01 strict-past interpolation.
Its directional gradient is v+2Qn. This is a declared degree<=2 field/synthetic
control interface, not an assertion that actual angular spectra have this form.
No query before the retained prefix or at/after its exclusive upper endpoint is
silently thermalized. At a time knot, a nonzero source-time tangent is rejected
as NONSMOOTH_QUERY. Zero query tangent can use the fixed recorded cell.

The target finite boundary uses HISTORY01 `boundary` and `boundary_jvp` unchanged,
with q_t=sum a_i n_ti^2, s=xr_p/(3x1s), A=-expm1(-tau/q_t), T=exp(-tau/q_t):
d_out=d_in+(s-d_in)A. Its q tangent is
delta_q_t=sum n_ti^2 delta_b_i+2sum a_i n_ti delta_n_ti.
The old same-event number/energy ledger remains the sole local line owner;
redshift work between events belongs to the propagation/field owner.

### Conditional finite error statement

For the represented characteristic, a root residual bound eps_F (including
explicit arithmetic allowance) gives eps_Delta<=eps_F/a_min. Because
||dn_s/dDelta||=sqrt(Var_n(a))<= (a_max-a_min)/2, and
|dW_s/dDelta|=x_s exp(-x_s)<=1/e, an admitted source-field error e_H and Lipschitz
bounds K_eta,K_n imply

e_in <= e_H + [K_eta+K_n(a_max-a_min)/2+1/e]eps_Delta+e_reference_arithmetic.

Here e_H may include the HISTORY01 conditional h^2 M2/8, endpoint and angular
errors. No curvature bound is inferred from the finite actual h4 values.
At fixed target coefficients, e_out<=T e_in and
e_number_rate<=G_native H_t q_t A e_in; e_energy_rate=E_target,J e_number_rate.
General geometry/thermal uncertainty must be separately supplied. These are
conditional estimates, not a physical calibration claim from one saved prefix.

## C1–C4. Frozen implementation and verification contract

Allowed writes: this unit only, plus later reviewed delivery/progress records;
old science and source snapshots remain byte-identical. Code is an isolated
research adapter, using numpy/scipy/math and Decimal if a high-precision oracle
is needed. No production module mutation, new IVP, old cohort replay, or new
native recombination run. Save every execution stdout/stderr, raw finite rows,
summary, source/code identity and inclusive CPU/wall/RSS.

New bounded allocation: 60 CPU seconds, 180 wall seconds, one thread, 1GiB;
primary run <=40CPU/90wall; one independent changed-source review with at most
8 new finite probes and <=10CPU/30wall; remaining10CPU reserved for diagnosed
targeted repair/figure rendering. External API waiting and file transfer are
reported as orchestration, not scientific CPU. Historical ledgers are unchanged.

Primary finite controls, freeze before execution:

1. At most96 retarded cases covering FLRW, axes/zero components, LRS and triaxial
   shears, Lambda=0/small/native line ratios/large log ratios, q_min boundary.
   Compare independent Decimal root, exact axes and original C9 formula.
2. At most24 tangent directions, including angular, shear, line ratio and mixed
   changes, against high-precision differences. No arbitrary FD tolerance tuning.
3. At most32 Wien-reference controls including opposite signs, nearly equal x,
   x=0, underflow and would-overflow naive formulas; show absolute f preservation.
4. At most24 fixed-cell polynomial-history + finite-boundary composites with
   endpoint/time/direction/reference tangents and local energy ledger reuse.
5. Actual retained prefix: at most24 channel/cell queries after source-column
   admission; compare independent linear interpolation. This proves adapter use
   of actual bytes only, not h/h2/h4 physical convergence or an angular supplier.
6. At most24 invalid cases: causal future/prefix gaps, malformed unit directions,
   trace/domain violation, absent uncertainty input, nonfinite/overflow tangents,
   negative absolute f, knot direction and malformed history dimensions.
7. At most24 finite error-envelope cases with analytic polynomial/smooth fields,
   plus 3 deliberate defects (FLRW clock in shear, omit reference offset,
   shift source column by one) that must be detected.

Acceptance: root and direction scaled error <=5e-12; energy/Killing/norm invariant
<=5e-12; JVP scaled error <=5e-9; absolute occupation/boundary scaled error
<=5e-12; saved linear interpolation <=64eps scaled; finite analytic envelopes
must contain the reference including predeclared arithmetic term. Scale for
value/JVP comparisons is max(1,abs(expected),abs(actual)); also save absolute
errors to avoid masking small occupations. Extreme-occupation controls use
absolute scale max(abs(reference),1e-300) with independently justified roundoff.
No physical tolerance is changed to obtain a PASS.

Make 2 figures from saved rows: retarded shifts/reference correction and actual
prefix coverage/error-control evidence. Inspect both actual PNGs once. Use one
primary verification pass and one independent review; repair only actual findings.

## R8–R10 / C9–C10. Acceptance and delivery

Admit only the derived/implemented retarded-characteristic boundary leaf after
the independent reviewer accepts the changed dependencies. Parent REC-HISTORY
remains PARTIAL while actual same-domain interpolation uncertainty, angular
supplier and full thermodynamic Jacobian remain open. No strong no-go is claimed;
NG1–NG7 apply if a new impossibility claim is proposed.

Every R/C stage has separate science, publication, backup and global-DAG status.
Stage checkpoints are cumulative, so their payload includes completed earlier
steps. Save the pre-code theory checkpoint, implemented checkpoint and final
reviewed checkpoint to Dropbox and Drive; record actual ACK/size/byte-readback
levels. Publish with expected-SHA ref updates, preserve draft/no-merge status,
and update central DAG observed-completion wrappers without changing its40
original node contracts,17edges, HE-X1 or unrelated parallel work. Final handoff
must contain exact source/current SHA, results, cumulative budgets, provider
IDs and the next input/derivation to perform, in copyable Korean text.
