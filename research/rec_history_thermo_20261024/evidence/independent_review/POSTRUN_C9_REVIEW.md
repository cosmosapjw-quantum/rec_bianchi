# Same-reviewer postrun review: REC-HISTORY-THERMO01

Reviewer `/root/thermo_independent_review`; requested Astra/high, actual model
identity unobserved. This continues the original independent theory, source,
code and targeted-continuation review. No independent numerical probe, source
evaluation, solve, native runtime, IVP or replay was executed by the reviewer.
Review actions read saved JSON, NPZ member headers, receipts and the actual
first two PNGs.

## Scoped recommendation

**ACCEPT the completed local six-axis numerical derivative evidence under the
frozen contract and arithmetic addendum A1.** Root owns final admission.
All A–F checks have attained passing results, combining original A/B with the
authorized continuation's C/D/E/F. The original primary invocation remains a
failed invocation due to JSON serialization; it must not be relabeled as an
uninterrupted successful run. No unresolved scientific defect was found.

The first two PNGs and the two authorized corrected PNGs were actually
inspected. Their numerical content is consistent with the saved results. The
concrete presentation-only readability finding recorded below is now closed.

## Evidence inspected and results

| Criterion | Observed result | Frozen interpretation |
|---|---|---|
| A literal reconstruction | All named blocks and structural zeros pass; maximum normalized residual 1.5551741193678365e-10 at sv | Below 5e-9; this is the literal parity view |
| B complex derivative comparison | Maximum 1.6263934969885847e-11 at lnTR real source sr/s | Below 2e-8 across coefficient/output/state checks |
| C primal backward residual | 7.22743791382896e-16, exact zero-gross check passes | Below 1024 eps64 |
| C tangent backward residual | 1.6778326936217204e-15 over 1878 components, exact zero-gross check passes | Below 1024 eps64 |
| D identities | All 9 groups pass, including 11 direct restricted-seed/implicit checks | Frozen 512 eps64 gross checks retained; pure-H complex comparison also passes |
| E mixed finite differences | Both directions and all 6 steps pass; no branch refusal | Worst outgoing 7.197124258333325e-9, F 7.726000750109759e-8, R_gamma 7.203078558642897e-9, each below 2e-5 |
| F manufactured systems | All 3 independent Cramer cases pass, 6 small numerical RHS | Maximum normalized derivative difference 1.816728585750256e-16 |
| F escape derivatives | All 14 depths pass against 60-digit reference | Largest derivative absolute discrepancy 1.5543122344752192e-15 at tau=.03 |
| F refusal controls | All 27 expected refusals observed | Includes nonfinite/domain and native branch-surface controls |

The finite-difference errors do not decrease monotonically with step size.
These three steps verify the prescribed local comparison; they do not establish
an asymptotic convergence rate or a trajectory error bound.

NPZ member headers confirm actual saved array dimensions: analytic dX is
313x6, outgoing derivative is 314x6, coefficient dM is 313x313x6, dT/dP are
314x313x6, and the complex and pure-H arrays have the corresponding prescribed
dimensions. This inspection read stored headers without loading a solver.

## Native versus stable arithmetic

The independent A1 distinction matters quantitatively. The recorded stable
versus literal-native matrix gap is 1.0492531849543418e-9 in normalized max
norm. The virtual source sv gap is 2.9307291478809673e-6. The new stable solved
outgoing vector differs from stored native outgoing by
1.4344654803842884e-13 in the same blockwise normalization.

The sv representation gap exceeds the literal reconstruction tolerance, but
that tolerance applies to literal reconstruction against native stored data,
not to equality of the two arithmetic representations. A1 was specified before
execution and explicitly separates these views. Do not call the new stable
matrix the old frozen RESP01 matrix, or call its six columns derivatives of
IEEE rounding operations. These are checked derivatives of the stable
evaluation of the source's piecewise real equations, retaining native small
branch polynomials.

The reviewer read and accepts OPERATOR_BINDING_CLARIFICATION.md. If Phi_s is
the stable source map, its full differential requires the consistently bound
pair J_s=partial_theta Phi_s and K_s=partial_u Phi_s. The earlier RESP01 incoming
operator K_0 and its represented norm certificate belong to its frozen native
arrays. They do not automatically certify K_s or justify combining K_0 with
the present J_s. A small outgoing-value discrepancy supplies no operator-norm
bound on K_s-K_0. No quantitative transfer or replacement incoming-operator
certificate was computed here. THEORY.md's decomposition is conditional on
using a consistent source/operator identity.

## Selected physical-source outputs

The saved stable base has F=-1.502859370064622 and
R_gamma=1.3726872952695042e-8 m^-3 s^-1. In the fixed coordinate order
(xe,xHII,lnTR,lnTM,lnnH,lnH), the ionization-source derivative is
(-49.276092120082915,-55.99959971998577,95.9736685326167,
5.974114302320319,-7.0312386999879815,1.3925142021754193).

The physical pure-H fraction direction combines the first two columns:
dF=-105.27569184006867 and
dR_gamma=7.422464673009079e-5 m^-3 s^-1 per unit fraction increment.
The paired energy derivative is +1.212841278987731e-22 for radiation and its
negative for atoms, in J m^-3 s^-1 per unit fraction increment. These are local
responses at fixed incoming departures, not independent cosmological histories.

## Preserved failure, continuation and resources

The original primary failed during JSON serialization after 13 large RHS.
Its A/B evidence and C residual arrays were preserved. The reviewed narrow
NumPy-scalar serialization repair completed only unreached stages; the
continuation used 12 large RHS, giving exactly 25 cumulatively. It used no new
base/tangent/complex solves. Original source and raw hashes remained unchanged.

| Invocation | Exit | Inclusive CPU seconds | Recorded execution-wall seconds |
|---|---:|---:|---:|
| Primary | 1, preserved serialization failure | 0.791030 | 0.808640620 |
| Continuation | 0 | 1.002246 | 0.976096903 |
| Saved-data figures | 0 | 4.240177 | 4.219067001 |
| Authorized formatting correction | 0 | 2.329394 | 2.332832932 |
| Total | — | 8.362847 | 8.336637456 |

All four receipts report cap compliance, unchanged bound hashes and one-thread
settings. The largest observed child process RSS highwater is 142720 KiB. This
is process-scope telemetry, not a live aggregate-memory measurement. Provider
I/O, environment recovery, packaging and full-turn elapsed time are separate.
The figure process reports zero source evaluations and zero linear solves.
The formatting-only correction also reports zero source evaluations and
solves. Root explicitly amended the figure process count to two while retaining
the combined 10-CPU-second/30-wall-second figure allowance; its observed total
is 6.569571 CPU seconds and 6.551899933 execution-wall seconds.

## Actual first-PNG inspection

Inspected `results/figures001/six_axis_outgoing.png` and
`results/figures001/ionization_number_energy.png` through the image viewer.
The six primitive axes, signed response curves, residual panel with the 2e-8
criterion, number/energy units, and opposite paired energy signs agree with the
saved data and the reviewed figure code.

Presentation-only finding: long repeated vertical labels in the first PNG
cross panel boundaries/title space and clip at canvas edges; automatic symlog
zero/near-zero tick labels overlap in portions of both figures. Main response
curves, signs and residual comparisons remain interpretable. A minimal
formatting repair would shorten per-panel labels, put shared units in one
caption, and use sparse explicit signed ticks retaining zero. Such a repair
needs no scientific rerun. Root decides whether to authorize a saved-data-only
formatting pass within its resource policy or retain the first figures with
this readability limitation disclosed. First PNGs must remain preserved.

### Finding closure after authorized formatting correction

Root authorized one formatting-only child, with first figures and all scientific
evidence preserved. The reviewer inspected the actual
`results/figures002/six_axis_outgoing.png` and
`results/figures002/ionization_number_energy.png`. Short ordinate labels, shared
units captions and sparse signed ticks resolve the reported label clipping and
zero-tick collisions. The bracketed scale factors, response signs, primitive
axes and residual criterion remain consistent with the saved data. The
presentation finding is **CLOSED**; no further render or numerical check is
requested. Delivery captions should identify the ordinate scales as symmetric
logarithmic (symlog), rather than letting sparse ticks suggest a linear scale.
Use the saved numeric projection/NPZ for exact magnitudes.

## Claim boundary

This closes the reviewed local thermodynamic coefficient-response obligation
only. H5 independent endpoint/reference uncertainty, validated full-cell
curvature, physical epsilon and absolute history bound remain absent/null.
The full coupled thermodynamic/angular/characteristic H7 Jacobian remains
open. No interval enclosure, physical history certification, global convergence,
production approval or REI activation follows from this result.
