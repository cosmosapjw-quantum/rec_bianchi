# REC-DONOR-02B: explicit-map component experiment

Status at source publication: NOT_EXECUTED. Read the exact-head workflow and
subsequent CLOSEOUT.json for observed results. This is a numerical research
probe, not a new production adapter or a physical input admission.

## Frozen scope

Parent PR60 head: b97e9f399d865d9e1bf4467c063393aa5e72d282.
Parent tree: 664d76bc47b02816aa94504e1d173454ca994739.
The remote PR60 already reconciled PR58/59 and executed 27/27 tests; those
unchanged tests are not repeated. No existing source/test/manifest is modified.

Reuse existing COMSourceDepositionPlan at blob
a3662cf399f14b7148d880266825be12baf934a0. All source-tree bytes must match the
parent. Three additions: this note, a numerical probe and its read-only CI
workflow. A later result-only CLOSEOUT.json is allowed. Operator Dropbox files,
existing branches, main, ready/merge status and other repositories are untouched.

## Question and manufactured experiment

Does a concrete provided deposition map actually execute
A_iq = n_H/mu_i sum_s B_is R_sq, and its fixed-map partial JVP, with independently
checkable number/energy moments? Can those moments alone select the map?

Use powers-of-two SI density and energy units, three targets, two source
channels and two angular readout directions. This is not a two-direction
transport approximation. No source distribution is reconstructed.

B = [[1/2,0],[1/2,1/2],[0,1/2]],
B_alt = [[3/4,1/4],[0,0],[1/4,3/4]],
E/E_unit = [1,2,3], E_source/E_unit = [3/2,5/2].
Both maps have unit column sums and the same energy columns. Their different
occupation actions are a constructive counterexample to inferring B from
conservation alone. Neither map is asserted to be the physical REC map.

## Predeclared acceptance and mathematical audit

Occupation f is dimensionless. R is a signed photon-packet rate per H per
second, n_H and mu have units m^-3, and B is dimensionless. Therefore A has
units s^-1. Negative A is not a negative occupation. Metric (-,+,+,+), source
hydrogen frame, no observer boost or implicit c/hbar/k_B substitution.

Use Fraction scalar sums independent of NumPy matrix multiplication. Check
12 density/rate combinations (72 action values and 72 JVP values), requiring
exact zero residual for this finite dyadic corpus only. No tolerance is tuned.
Check directional number/energy contractions and source/photon cG^a matching.
Reject number/energy-invalid maps, zero measure, nonfinite rates, bad rate
shape and boolean density. Detect omission and double application of n_H/mu.

The existing JVP is partial with B and mu fixed:
dA = (dn_H B R + n_H B dR)/mu.
The full moving-input differential additionally has
+n_H dB R/mu - A dmu/mu. A manufactured moving-measure example exposes the
nonzero omitted term; it is not implemented as a new coupled JVP. SymPy checks
the quotient derivative if available. Wolfram context/evaluator both failed
at MCP SSE HTTP404 before results in this session; no Wolfram PASS is claimed.

## Code and claim audit

This probe imports and executes existing numerical source; it does not merely
inspect declarations. Identity checks bind exact source blob/tree and workflow
head. Output is outside the worktree; artifacts include actual arrays and
versions. Optional generated figures are explanatory and cannot be called
visually audited without rendered inspection. Source code has not been
reviewed by an independent person/agent in this task.

No claim of physical source authentication, resolved authority adapter,
once-only global transaction ledger, physical two-photon/Raman kernel,
continuous-sphere positivity, moving-map/event JVP, BASS/REI wiring or provider.
NO_PASS_REC_PHYSICAL_SPLIT remains.

## Literature boundary and one next action

SciSpace discovery and primary abstract checks: Ali-Haimoud & Hirata,
Phys.Rev.D83:043513 (arXiv:1011.3758v2); Hirata, Phys.Rev.D78:023001
(arXiv:0803.0808v2). They support explicit radiation/atomic coupling and the
nonlocal two-photon/Raman scope, not these matrices or this implementation.
The map-nonuniqueness and moving-measure identities above are direct algebra,
not claims extracted from those abstracts.

After the bounded experiment, connect a typed resolved numerical adapter to
the existing plan with explicit array identities and provenance classifications.
Do not infer the physical B from conserved moments or rewrite the source owner.
