# REC R3Q: targeted literature and algorithm support

Observed 2026-10-20 13:31:40 UTC. This is source-grounded algorithm support for the parent research cycle, not an independent inspection of the current REC implementation. Parent-reported candidate counts (6,044 FULL observer calls versus approximately 117 selected oracle samples) have not been independently checked here.

## Decision support

Prioritize guarded snapshot construction if the parent source audit confirms that the sample-selection predicate depends only on already available metadata. Retain the same owned snapshots at selected events. This removes unnecessary data movement without changing the atomic/thermal operator or floating-point operation graph. Array views are not interchangeable with retained snapshots: a later history mutation can alter an earlier view. NumPy documents independent data buffers for copies and shared buffers for views [N1]. CPython documents that assignment binds objects and shallow copies retain element references [P1].

A full spectral ratio batch connection has a larger equivalence surface: float parsing, dtype promotion, exceptional lanes, temporary allocation, CSV formatting, error order, ctypes overhead, and row ordering. NumPy ufuncs are elementwise; `out=` permits reuse, whereas default output and complex expressions can allocate temporaries. Overlap may also trigger temporary copies [N2]. These API descriptions are not a cross-backend binary64 equivalence guarantee.

## Conditional preservation lemma (derived)

Let solver state/history before event k be X_k and let the unchanged integrator advance it by X_{k+1}=Phi_k(X_k). Let s(k,m_k) select events using metadata m_k, and C(X_k) form an owned snapshot. The eager observer constructs C on every event and returns without using it when s=0. The guarded observer evaluates the same s before construction.

Their selected observer trace is identical provided:

1. s is evaluated on the same event metadata and at the same causal boundary;
2. unsampled construction has no required side effects, observer-state updates, validation failures, or accounting outputs;
3. at selected events C receives the same history version and produces the same owned data;
4. the observer cannot mutate solver-owned state;
5. relevant accepted-input contracts hold, including ordinary numeric elements rather than user objects with conversion/copy hooks.

Proof: on s=0 both observers leave solver and persistent observer state unchanged; on s=1 both execute the same construction and subsequent observer work on the same X_k. Induction on k therefore gives identical solver state and selected trace. This is a conditional program argument. Parent source inspection and differential tests must discharge its assumptions. If unsampled copying previously triggered an intended exception, moving the guard changes that behavior and needs an explicit scoped compatibility decision.

Replacing the copied data by a view violates condition 3 when any later write aliases the view. Keeping copies only for selected events avoids that additional proof obligation.

## Copy-work model (derived; Wolfram checked)

For a simple uniform model, initial history length n0 >= 0, N=d m events, and selected indices d,2d,...,md, with m,d positive integers,

W_all = sum(k=1..dm)(n0+k) = d m (1+d m+2 n0)/2,

W_selected = sum(j=1..m)(n0+d j) = m (d+d m+2 n0)/2,

W_all-W_selected = (d-1)m(d m+2 n0)/2 >= 0.

Thus the copied-element work ratio is

r = d(1+d m+2 n0)/(d+d m+2 n0),

and for n0=0 it becomes (1+d m)/(1+m). The ratio equals one for d=1. It approaches d for large m. For nonuniform accepted-history lengths L_k and actual sample set S, use W_all=sum_k L_k and W_selected=sum_{k in S} L_k; the parent must compute these from its observed trace. The nominal 6,044/117 call-count ratio alone is not the copied-byte ratio.

If this removable work accounts for measured baseline time fraction f and receives speed factor r, the unchanged-work model gives total speedup 1/(1-f+f/r). This identity does not predict f or prove a runtime improvement. It is a conditional cost model with no physical units; bytes follow by multiplying actual copied element counts by their storage width and field count. Peak RSS requires separate measurements because lifetime overlap and allocation behavior are not determined by cumulative copied bytes.

WolframContext failed with a current service error; WolframLanguageEvaluator independently succeeded and returned the sum, difference, ratio, nonnegativity and Amdahl formula. Exact code and raw result are in the JSON support receipt. Real/integer algebra cannot establish binary64 equivalence.

## Numerical equivalence requirements for any later ratio batch

Preserve the scalar operation graph, operand dtype and order. Evaluate each arithmetic operation separately when its intermediate rounding is part of the existing contract; do not substitute reassociation, reductions, `fast-math`, or a fused multiply-add on the strength of an algebraic identity. Python specifies expression evaluation order [P2], and its floating-point tutorial describes binary64 representation and per-operation rounding limits [P3]. NumPy documents an unfused array-expression example as separate multiply and add operations with an intermediate array [N2]; that does not certify every compiler/backend configuration.

Keep exceptional-lane behavior explicit. `numpy.maximum` propagates NaNs; `fmax` has a different policy [N3]. Check original finite-value predicates, signed zero, subnormals, zero denominators, overflow, threshold-adjacent ratios, and error diagnostic order. Initialize output slots if using `where=`: false lanes of a newly allocated output can otherwise be uninitialized [N2]. These are specific differential test obligations, not claims that the existing R3P ratio API is wrong.

## HyRec source boundary (literature-supported)

Ali-Haimoud and Hirata, *HyRec*, Phys. Rev. D 83, 043513 (2011), arXiv:1011.3758v2, revised 2011-01-21, is the primary numerical reference [H1]. Section V.D couples photon transport and level populations before updating the electron fraction. Section V.E links time stepping to spectral-bin spacing and tests switches and resolution. Appendix C uses the stored-derivative recurrence

y_{i+1} = y_i + Delta x [1.25 f_i - 0.25 f_{i-2}],

with x=ln a and f=dot(x_e)/H. The observer optimization above changes none of these operations if the preservation lemma is satisfied. The paper's fiducial Delta ln a=8.5e-5 does not replace the task's fixed h=4.245e-5. The original paper's convergence evidence cannot be transferred to Bianchi extensions or the current HOLD trajectory. Its full-history timing is not a benchmark for this audit-only optimization.

## Inspected primary sources

| ID | Primary URL | Version / inspected scope |
|---|---|---|
| N1 | https://numpy.org/doc/2.3/user/basics.copies.html | NumPy 2.3; copies/views content read |
| N2 | https://numpy.org/doc/2.3/reference/ufuncs.html | NumPy 2.3; elementwise, dtype, out, overlap, where, temporary-expression sections read |
| N3 | https://numpy.org/doc/2.3/reference/generated/numpy.maximum.html | NumPy 2.3; NaN and output semantics read |
| P1 | https://docs.python.org/3.14/library/copy.html | Python 3.14 docs; binding/shallow/deep copy distinctions read |
| P2 | https://docs.python.org/3.14/reference/expressions.html#evaluation-order | Section 6.16 directly read; web page reported 3.14.8, updated 2026-10-20 13:02 UTC |
| P3 | https://docs.python.org/3.14/tutorial/floatingpoint.html | Binary64 and rounding sections read |
| H1 | https://arxiv.org/abs/1011.3758v2 and https://arxiv.org/pdf/1011.3758 | Abstract/version metadata plus actual 24-page PDF Sections V.D/E and Appendix C read |

SciSpace was called once with the targeted HyRec question. It returned the original paper (unique_id 45gwrpvqjn, DOI 10.1103/PHYSREVD.83.043513) alongside related records. The original primary PDF, rather than SciSpace's summary, supports the numerical statements above. Exa performed two searches requesting five results each; ten returned slots were screened, then only targeted primary documents were read. Stable NumPy search results currently pointed to 2.5, so the retained documentation citations deliberately use explicit 2.3 paths; this is not a claim about the runtime installed in the parent workspace.

No external code was imported. The reusable change is the generic conditional-construction pattern and existing NumPy ownership semantics; no added scientific approximation or package is required by the proposed observer change.

