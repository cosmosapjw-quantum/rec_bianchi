# R3R bounded spectral stream audit: independent PHYS-MATH review

**Verdict: PASS_SCOPED.** Independent spectral comparison lanes may be batched with the source's separate binary64 operations, exact scalar Planck cache, ordered scalar failure replay, and synchronous guard boundaries. This conclusion applies to the declared audit-input contract. It does not establish new numerical equivalence by execution, measured acceleration, global convergence, or physical validity.

Reviewer: independent agent /root/context_intake, separate from implementation author /root/source_intake. Review date: 2026-10-20 UTC. Final source read began at 13:46:56 UTC. No solver, old R3P benchmark, or old validation suite was executed by this reviewer for this audit. The companion JSON records exact inspected source identities and claim gates.

## 1. Scope and source identity

The frozen reference is scripts/verify_r3q_h4_continuation.py::compare_native_stream; the candidate is the opt-in scripts/r3r_stream_audit.py::compare_native_stream. This is the spectral CSV audit after integration. The reviewed candidate was an uncommitted file on the following observed base:

| Identity | Value |
| --- | --- |
| Observed base HEAD | 4a1912b661f4227707ad7efa93df56bfa47f930a |
| Observed base tree | eac9172f63a3b4a07181e4c9a97258e680d066b0 |
| Candidate SHA256 | 10021e086b9f842dce21cf18a9b1207bdcdc127c56384715b181500db3b9aea8 |
| Candidate Git blob | 6b6f78b6130228139def030d91ad0a81c267841e |
| Frozen comparator SHA256 | 30b415cbf1328c89ac96a864b7bd99b91c2f52fc59481f75cdafaaa70d42261a |

Imported state/RHS checks and quarter-start cosmology were also inspected. The recorded git diff command over src and both frozen comparator/helper scripts exited 0 with empty stdout. This is a source observation, not an executed physics validation. A shipping receipt must bind this candidate blob to its actual committed source SHA; the base commit is not that source commit.

## 2. Physical quantity, units, and unchanged gate

For spectral lane \(\ell=(j,t,b)\), \(t\in\{V,A,L\}\), let \(p_\ell,c_\ell\) be the Python and native photon occupation values. The source maps \(j\) to the same integer index \(72892+j\), selects the same energy bin, and computes

\[
 \Theta_j=k_{\rm B}T_0(1+z_j),\qquad
 f^{\rm BB}_\ell=\frac{1}{\operatorname{expm1}(E_\ell/\Theta_j)}.
\]

Here \(E\) and \(k_{\rm B}T\) are in eV, so the exponential argument, occupation values, tolerance, and ratio are dimensionless. The physical domain \(T_0>0,\ z>-1,\ E>0\) makes \(f^{\rm BB}>0\), subject to original floating-point evaluation. The original gate is

\[
 \tau_\ell=10^{-7}\max(|p_\ell|,|c_\ell|)+10^{-10}f^{\rm BB}_\ell,\qquad
 r_\ell=\frac{|p_\ell-c_\ell|}{\tau_\ell},\qquad
 \operatorname{finite}(r_\ell)\ \land\ r_\ell\le 1.
\]

The candidate changes neither coefficient, the acceptance boundary, energy selection, nor scalar math.expm1. It introduces no positivity requirement that could silently alter the reference's acceptance set. Passing this comparison does not prove that each occupation is physically admissible.

Atomic/thermal operators, predictor recurrence, accepted states, causal/stage boundaries, and original C same-h checks remain outside the modified function and are frozen in the inspected working tree. HyRec's original convergence demonstrations cannot be transferred to this Bianchi branch merely because comparison parity is preserved. Sections V.D–V.E and Appendix C of the original paper describe the coupled radiation/atomic solve and discretization requirements; these support preserving the operator and recurrence, not inferring a new global convergence result. [Ali-Haïmoud & Hirata, arXiv:1011.3758v2](https://arxiv.org/abs/1011.3758v2), [inspected original PDF](https://arxiv.org/pdf/1011.3758).

## 3. Binary64 operation graph

Writing \(\operatorname{RN}\) for the environment's ordinary binary64 rounding operation, the relevant graph for valid finite lanes is

\[
 u=\operatorname{RN}(p-c),\quad d=|u|,\quad
 m=\max(|p|,|c|),\quad
 a=\operatorname{RN}(10^{-7}m),\quad
 b=\operatorname{RN}(10^{-10}f^{\rm BB}),\quad
 \tau=\operatorname{RN}(a+b),\quad
 r=\operatorname{RN}(d/\tau).
\]

The candidate uses separate subtract, absolute value, maximum, multiply, multiply, add, and divide ufunc calls with float64 buffers. It does not combine products and sum into an FMA, change parentheses, introduce a signed summation reduction, or use a vector exponential. The cached Planck denominator retains the source order KB_EV_K*c.T0_K*(1.+z); final scalar division and math.expm1 are unchanged.

Thus the algorithm preserves the rounded per-lane graph under the declared binary64 contract and same supported arithmetic environment. This explains why a bitwise gate is reasonable; it is not a portable bitwise guarantee obtained from algebra alone. CPU dispatch, floating-point modes, library versions, and exceptional semantics still require actual paired execution. NumPy describes ufuncs as elementwise operations without promising that every replacement of scalar expressions is bitwise equivalent on every platform. Python's evaluation order likewise does not make real identities floating-point identities. [NumPy 2.3 ufunc reference](https://numpy.org/doc/2.3/reference/ufuncs.html), [Python 3.14 evaluation order](https://docs.python.org/3.14/reference/expressions.html#evaluation-order), [Python floating-point tutorial](https://docs.python.org/3.14/tutorial/floatingpoint.html).

## 4. Lane independence and cache identity

A ratio uses only its parsed native value, corresponding binary64 array element, fixed cosmology, and selected energy. No lane changes a state used by another lane. Buffers copy already-read scalar values, so evaluation observes the same values under the stated input contract.

The scalar Planck cache is limited to one j. V and A share the same energy-bin key because the frozen formula selects table.energy_eV[b] for both; L uses keys 311–313 for LINE_EV[b]. A j change invalidates all 314 entries. Arbitrary V/A/L interleaving remains legal: original independent per-tag sequence counters are checked, and returning to another j recomputes rather than reusing an incorrectly keyed value.

The proof requires ordinary binary64 scientific arrays, pure source cosmology/redshift calculation, and stable inputs between synchronous guards. Source redshift is a deterministic function of the validated integer index. At a guard the candidate drains prior rows, invalidates Planck values and array maps, and then calls the callback; later rows read live inputs. This supports deliberate mutation at those boundaries. Concurrent mutation, side-effecting getters, arbitrary custom array subclasses, and side effects on every scalar redshift read are outside the proof.

NumPy's copy/view distinction supports this ownership analysis: views alias buffers, while copies own data. Pending values are copied into the candidate's fixed buffers; temporary slices view those owned buffers and do not escape a flush. [NumPy 2.3 copies and views](https://numpy.org/doc/2.3/user/basics.copies.html).

## 5. First failure, exceptional values, and maxima

Metadata, per-tag order, array access, native float parsing, and scalar Planck evaluation remain in input order. A row enters the buffer only after those operations succeed. Before propagating a later parse, metadata, control-record, or stream-read exception, earlier pending numerical rows are evaluated. An earlier numerical failure therefore retains priority.

If any vector ratio fails, the complete pending block is replayed in scalar row order using the frozen tolerance and diagnostic formatting. This finds the first original failure rather than choosing a vector extremum or tag-dependent failure. Clearing the pending reference before evaluation prevents replaying an already-failed block twice. Non-spectral control rows, every original synchronous guard, and EOF drain the buffer before proceeding.

Python's ordered scalar max and numpy.maximum have different general NaN selection semantics. Here NaN inputs lead to an unacceptable ratio and full scalar replay; that vector intermediate is not published as success. Nonfinite ratios caused by infinities, zero tolerance, invalid operations, or overflow follow the same route. Non-default NumPy policies requesting raising, callbacks, printing, or underflow handling bypass vector arithmetic and replay scalar rows. Scalar math.expm1 exceptions still occur while processing the same source-ordered lane. [NumPy 2.3 maximum reference](https://numpy.org/doc/2.3/reference/generated/numpy.maximum.html).

Every ratio in a healthy block is finite and satisfies the gate. Grouping per-tag maxima is safe because maximum selects an existing finite value rather than rounding a sum. Signed zero is the possible equal-value bit distinction: both paths initialize the published maximum to positive zero, and the outer scalar max keeps it when tied with either zero sign. No NaN ratio enters a successful reduction.

Diagnostic equivalence covers verdict and exception class/message. Warning stack locations and emission timing are not preserved. Allocation failures and asynchronous interruption timing are also outside the mathematical reordering proof.

## 6. Guards and bounded resource addition

The reference calls its stream guard before record numbers divisible by 8192 and its completion guard after count/event receipt checks. The candidate preserves this schedule. Draining pending rows before a callback corresponds to the reference having already evaluated those earlier rows.

Equal callback positions do not imply equal CPU-budget outcomes: lower cost may keep one backend below a cap reached by another. The candidate neither allocates a new integration nor raises a launcher limit. CPU/wall/address-space caps and receipt reserve remain the supervising launcher's responsibility.

For block size \(B\), \(1\le B\le625\), persistent NumPy payload is \(25B\) bytes: three float64 arrays and one uint8 tag array. A conservative temporary-plus-persistent payload bound is \(60B\), at most 37,500 bytes. Pending metadata is \(O(B)\); the Planck cache has at most 314 entries. This bounds additional batching payload. It excludes Python object overhead, allocator behavior, file buffers, existing accepted history, and RSS; it does not prove the whole process remains below 2 GiB.

## 7. Findings, reused evidence, and remaining gates

No open P1/P2 mathematical finding was identified within the stated source and contract. Review feedback is incorporated in the stable source's warning and CPU-outcome scope. This review consists of independent derivation and source inspection. Tests, adversarial executions, timings, and independent code review are separate evidence.

The new 32-step profile supports this audit path as a candidate because frozen stream comparison has substantial exclusive elapsed cost. cProfile quantities here are elapsed profiling times, not process-tree CPU measurements. They establish candidate relevance only; they do not measure candidate acceleration or predict full5210 or production speedup.

| Claim axis | This audit's verdict |
| --- | --- |
| Mathematical correctness | PASS_SCOPED: conditional lane reordering, cache identity, maxima grouping, and first-failure argument |
| Numerical equivalence | REQUIRES_PAIRED_EXECUTION: no fresh bitwise run by this reviewer |
| Implementation correctness | REQUIRES_CODE_AUDIT_AND_TESTS |
| Measured acceleration | NOT_ASSESSED_BY_THIS_AUDIT |
| Memory/resource behavior | PASS_SCOPED_PAYLOAD_BOUND; whole-process RSS and budget outcome require measurement |
| Physical validity | UNCHANGED_NOT_ESTABLISHED |
| Production readiness | NOT_ISSUED |

Historical same-h HOLD results, unrepeated global convergence status, closed cost ledger, REI_activation=false, and absence of a newly authorized full5210 allocation remain independent conditions. No mathematical no-go result is asserted. Completed R3P evidence is reused as precedent, not counted as fresh R3R validation.

