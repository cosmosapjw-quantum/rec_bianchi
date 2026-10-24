# Final independent review — REC-HISTORY-THERMO01

**Decision: PASS_SCOPED_LOCAL_PRIMITIVE_JACOBIAN_AFTER_SERIALIZATION_CONTINUATION.**

**Material blockers: 0. Presentation finding: CLOSED.** Root retains final
scientific admission and publication authority.

Reviewer `/root/thermo_independent_review` performed the theory/source,
implementation, targeted serialization-continuation, raw-result and image
reviews in the same reviewer session. Requested Astra/high; actual runtime
model identity was not observed. The reviewer did not implement scientific
code and ran no independent numerical probes, source evaluations, solves,
native execution, IVPs or old campaign replay. Reviewer modifications are
confined to its own evidence files.

## Evidence continuity

The original preexecution reviews and all diagnosed findings remain in
PREEXEC_THEORY_REVIEW.md and PREEXEC_CODE_REVIEW.md. After workspace loss, the
seven code files and full original 23-file source snapshot were recovered
byte-identically; original canonical snapshot SHA256 is
`adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54`.
That recovery reused the existing review without another assurance loop.

The first primary invocation failed after 13 large RHS at serialization of a
NumPy boolean. Its original exception, source identity, A/B comparisons, saved
arrays and execution receipt remain preserved. The same reviewer inspected
the narrowly authorized continuation, which completed saved C and unreached
D/E/F using 12 remaining large RHS. It did not replay the first 13 RHS or
relax any threshold. PREEXEC_CONTINUATION_REVIEW.md records this targeted
review. POSTRUN_C9_REVIEW.md gives detailed observed metrics and qualifications.

## Scientific acceptance within the frozen local scope

| Check | Observed outcome |
|---|---|
| A literal-native reconstruction | All blocks and structural zeros pass; maximum normalized difference 1.5551741193678365e-10 versus 5e-9 |
| B independent complex-step derivatives | Maximum 1.6263934969885847e-11 versus 2e-8 |
| C primal/tangent backward residuals | 7.22743791382896e-16 / 1.6778326936217204e-15; zero-gross checks pass |
| D identities | 9 groups pass, including 11 direct pure-H restriction checks under the frozen roundoff criterion |
| E mixed directions | Both directions, all six steps pass; worst outgoing/F/number differences 7.197124258333325e-9 / 7.726000750109759e-8 / 7.203078558642897e-9, each below 2e-5 |
| F manufactured systems | Three exact Cramer-reference cases pass; six small numerical RHS |
| F escape/domain controls | Fourteen 60-digit-reference depth probes and all 27 refusal controls pass |

The actual saved state/output derivative shapes are 313x6 and 314x6. The
complete primitive coefficient dependence, explicit H product term, outgoing
responses, ionization source and paired single-event energy responses satisfy
the prescribed tests at the retained source face. The physical pure-H fraction
direction is the sum of the independent xe and xHII columns.

This is acceptance of a local numerical derivative of a specified source map.
The finite-difference results do not establish an asymptotic convergence rate.
The floating diagnostics are not interval enclosures.

## Arithmetic and incoming-operator binding

A1 separates literal-native reconstruction from the consistently stable
scientific evaluation. Native small-branch polynomials are retained. Recorded
stable-versus-native normalized differences include M=1.0492531849543418e-9,
sv=2.9307291478809673e-6, and solved outgoing=1.4344654803842884e-13. The sv gap
is an explicitly disclosed representation difference, not a failed literal
parity check. The new stable matrix must not be identified with the previous
frozen native binary64 matrix.

As specified in OPERATOR_BINDING_CLARIFICATION.md, the full differential of
the stable source Phi_s requires a consistently bound pair:

    delta o = J_s delta theta + K_s delta u.

The previous RESP01 certificate belongs to its native represented incoming
operator K_0. It is **not transferred to K_s** by this unit. It also does not
justify combining the current J_s with K_0 without a quantitative transfer
bound or another valid common-operator binding. A small outgoing-value gap is
not a bound on the norm of K_s-K_0. No such transfer was computed or admitted.

## Images and presentation closure

The reviewer actually opened all four PNGs:

- results/figures001/six_axis_outgoing.png
- results/figures001/ionization_number_energy.png
- results/figures002/six_axis_outgoing.png
- results/figures002/ionization_number_energy.png

The first pair revealed long-label clipping and overlapping zero/near-zero
ticks. Root authorized one formatting-only child while preserving those
images and all scientific inputs/results. The corrected pair resolves the
reported readability defect and preserves data, signs, axes, units and the
verification criterion. **The presentation finding is closed.** No further
render is requested. Delivery captions should explicitly identify symmetric
logarithmic (symlog) ordinate scales and bracketed axis factors; exact numbers
remain available in REPORTED_VALUES.json and NPZ arrays.

## Budget and preserved invocation outcomes

| Invocation | Exit | Inclusive CPU seconds | Recorded execution-wall seconds |
|---|---:|---:|---:|
| Original primary | 1, serialization failure preserved | 0.791030 | 0.808640620 |
| Authorized continuation | 0 | 1.002246 | 0.976096903 |
| First saved-data figure process | 0 | 4.240177 | 4.219067001 |
| Authorized formatting-only process | 0 | 2.329394 | 2.332832932 |
| Total | — | 8.362847 | 8.336637456 |

All four receipts report cap compliance and unchanged bound inputs. Exactly
25 cumulative large RHS were used. Figure processes used zero source
evaluations and zero solves. Their combined cost is 6.569571 CPU seconds and
6.551899933 execution-wall seconds, within the unchanged 10/30 allowance
after root's explicit process-count amendment. Largest observed child RSS
highwater is 142720 KiB, a process-scope measurement rather than live aggregate
telemetry. Provider I/O, recovery, packaging and total elapsed conversation
time are separate from these execution figures.

## Unchanged unresolved obligations

H5 independent endpoint/reference uncertainty, validated full-cell curvature,
physical epsilon and absolute history bound remain absent/null. The full
coupled thermodynamic/angular/characteristic H7 Jacobian remains open. There
is no physical-history certification, global-convergence result, production
approval or REI activation. The same-source incoming-operator binding remains
a separate unmet requirement for any future coupled derivative claim.
