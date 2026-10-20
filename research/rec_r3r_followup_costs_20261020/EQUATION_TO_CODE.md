# Equation-to-code contract — R3R

## Lane predicate and binary64 operation graph

For each original parsed spectral record i=(tag,j,b), let p_i be the Python
occupation, c_i the native occupation, E_i the frozen energy, and
T_j=T0(1+z(72892+j)). The unchanged scalar Planck input is

    f_i = 1 / math.expm1(E_i / (KB_EV_K * T0_K * (1 + z)))

The actual parenthesization in the frozen comparator remains authoritative.
With eps_rel=1e-7 and eps_bb=1e-10, the acceptance ratio is

    d_i = abs(p_i-c_i)
    a_i = eps_rel * max(abs(p_i),abs(c_i))
    b_i = eps_bb * f_i
    t_i = a_i+b_i
    r_i = d_i/t_i

Every multiply/add/divide is an individual binary64 operation. A spectral
record passes iff isfinite(r_i) and r_i <= 1. No FMA, approximate reciprocal,
fast math, vector expm1, tolerance change or sign/positivity policy is added.

| Mathematical/behavioral object | Frozen code | R3R code |
|---|---|---|
| Original scalar Planck normalization | verify_r3q_h4_continuation.compare_native_stream | r3r_stream_audit.compare_native_stream, j/energy cache |
| Independent binary64 ratio | same function's V/A/L branch | flush: separate NumPy subtract/abs/maximum/multiply/add/divide |
| Exceptional scalar arithmetic and first-error diagnostic | original V/A/L branch | scalar_rows; entire exceptional block replay |
| Per-tag (j,b) sequence | divmod(counts[tag], bins) | identical per-tag check; arbitrary V/A/L interleaving preserved |
| STEP, branch, RHS and state predicates | original comparator helpers | delegates unchanged compare_state and checked_integrated_rhs_ratio |
| Causal callback boundary | guard before line8192 multiples and final completion | flush before guard, then invalidate caches, call original label |
| Solver state evolution and common-input samples | frozen R3Q worker/integrator | source-bound worker unchanged; only comparator binding selected |
| Whole resource supervision | existing R3P/R3O Budget | run_r3r_h4_supervised with unchanged Budget thresholds/reserves |

## Constructive equivalence argument

There are no dependencies from r_i to any other lane's inputs. Within an
interval between synchronous CPU guards, binary64 source arrays, cosmology
and energies are stable. The source redshift method is pure. Therefore
reusing exactly the same scalar f_i for identical j and energy does not
change its bits. L energies have a separate cache address from V/A energies.

The healthy batch applies the same operation graph to each lane independently.
For finite accepted values, regrouping maxima selects an existing value and
introduces no sum-rounding error. The outer scalar max retains the original
positive-zero initial maximum. Platform bitwise agreement must additionally
be measured: a real-number proof alone is not an empirical binary64 receipt.

Parsing stays in stream order. Earlier pending numerical records are drained
before a control row, a later parsing/index/order exception, the next guard,
or EOF. If the vector block is exceptional, replay in original scalar order
recovers the same first error class/message, including the .17g ratio. After
a guard, live arrays and Planck inputs are read again. The same guard record
schedule is preserved; equal actual CPU-cap crossing times are not promised.

## Explicit scope and limitations

- The comparator accepts the original binary64 scientific arrays. Concurrent
  mutation and a redshift method with call-count side effects are outside the
  frozen scientific contract.
- Warning timing and stack locations are not a bitwise/verdict guarantee.
  Non-default floating error handlers fall back to scalar evaluation.
- HE payload is ignored by the frozen comparator; the fast path preserves that
  behavior. This is not a new validation of the preceding helium history.
- Photon positivity is not separately enforced by this ratio predicate.
- At block size512, explicitly managed extra NumPy payload is bounded by
  30,720B; at the hard maximum625, by37,500B. Python objects, NumPy internals,
  source history, and total RSS require separate measurements.
- The original R3P reference h=4.245e-5 and its HOLD states are retained.
  This followup uses the already-defined R3Q quarter-grid checkpoint with
  dlna=8.49e-5/4=2.1225e-5. Native/Python comparisons use that same grid.
  No cross-grid convergence conclusion is inferred.
- A fresh source-bound pilot is limited to1..32 accepted steps by the frozen
  R3Q smoke gate, within the user's128-step ceiling. It cannot call event/full.
- -B alone can still read old .pyc files. The launcher creates empty private
  cache prefixes before project imports in both processes, verifies frozen
  files plus new runtime bytes against the expected Git commit, and records
  source identity again after execution. No frozen manifest is rewritten.

## Reused external and predecessor evidence

R3P's independent ratio operation graph and exact-cache principles are
complete_reused. NumPy official ufunc documentation establishes elementwise
semantics and out= behavior; no claim follows that any SIMD instruction was
generated or caused the full measured change. The original HyRec recurrence
and radiative-transfer treatment are unchanged; the original paper's own
accuracy tests do not validate this Bianchi extension or current HOLD gates.

Literature receipts preserve SciSpace/Exa successes, the separate
WolframContext error and successful WolframLanguageEvaluator algebra.
The conditional callback-copy model remains a deferred candidate, because
the new short profile did not establish observer copying as the current
dominant exclusive cost.

