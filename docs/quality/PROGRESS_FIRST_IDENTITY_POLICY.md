# Progress-first, typed-identity, and durable-execution policy

This is the compact repository form of the four 2026-08-28 directives:

- `Universal Anti-Meta-Loop and Progress-First.md`;
- `Universal Audit-Compiled Execution Plan -.md`;
- `Universal Byte Identity vs Semantic Identity.md`;
- `Anti-Stall, Durable Checkpoint, and.md`.

It replaces reassurance-only process with a smaller set of mechanically useful
rules. It does not relax scientific authority.

## 1. Authority and progress

Authority precedence is:

1. latest explicit user decision;
2. inspectable canonical repository state;
3. merged code, tests, and contracts;
4. accepted durable evidence;
5. documentation and PR history;
6. transcript-only claims.

Fail closed on claims, not on exploratory progress. `NOT_ATTEMPTED`, `DEFERRED`,
`UNRESOLVED`, `REFUTED`, and `PASS` are distinct. A missing production authority
blocks physical promotion; it does not prohibit a labelled
`EXPLORATORY/NONAUTHORITATIVE` diagnostic or manufactured test.

Default bounded loop:

```text
one implementation objective
→ one risk-scoped verification pass
→ optionally one independent read-only review
→ one targeted repair
→ checkpoint and stop
```

Two materially equivalent failures exhaust the retry budget. Two consecutive
cycles without a material artifact or execution delta are
`STALL_PROCESS_ACCRETION`; stop meta-work and checkpoint.

## 2. Audit-compiled work units

Before a nontrivial change, freeze:

- exact base commit/tree and allowed paths;
- observable outcome and non-goals;
- scientific conventions and invariants that must not change;
- observed P0/P1 failure modes;
- one detector for every P0/P1: test, assertion/invariant, or explicit blocker;
- targeted, negative, and directly affected verification commands;
- completion and stop conditions.

Do not guess across a semantic boundary. Do not change fixtures, expected
scientific outputs, conventions, or tolerances merely to obtain green tests.
A new gate requires an observed failure not covered by existing controls and
should replace or merge an older check.

## 3. Typed identity

Classify an object before treating a mismatch as blocking.

| Class | Examples in this repository | Required relation |
|---|---|---|
| 1 — immutable source/input | tracked NPZ/source bytes, locked owner arrays | byte identity |
| 2 — deterministic evidence | fetched publication artifact and stage manifest entries | byte identity when the stored artifact is checked |
| 3 — numerical/scientific output | recomputed diagnostics, states, residuals, observables | justified numerical/semantic equivalence |
| 4 — packaging/metadata | host path, timestamps, JSON presentation, archive metadata | content/structural identity unless exact packaging is requested |

Keep result validity, provenance validity, and packaging validity separate.
`BYTE_IDENTITY_MISMATCH` is not automatically a scientific failure. Numerical
tolerances must be fixed from mathematics, conditioning, convergence, or an
independent oracle, never widened after observing a mismatch.

### REC receipt mapping

- The two V1 raw receipts are **forensic fingerprints conditional on an actual
  NumPy dispatch lane**. Known lanes are X86_V4 and X86_V3. A lane absent from a
  host is `HOST_LANE_UNAVAILABLE`, not a failed scientific result.
- AMD Ryzen 9 5900X provides X86_V3/AVX2 but not X86_V4/AVX-512. Native and
  `NPY_DISABLE_CPU_FEATURES=X86_V4` therefore legitimately produce the same V1
  X86_V3 fingerprint.
- The V2 authority projection, diagnostic-contract digest, raw
  `momentum_scale` owner, locked-energy owner, invariant predicates, status,
  claim, and blocker set remain load-bearing on every host.
- The whole V2 JSON SHA is an archival publication seal. Fresh continuation is
  decided by the canonical authority/diagnostic projections and their
  validation, not by a recomputed whole-file SHA.
- A stored artifact fetched from Git still must match its stage manifest bytes.

## 4. Physical-face firewall

Neither a manufactured 52-ray solve nor SHA-shaped declarations create physical
authority. Production admission remains false until all current prerequisites
are independently resolvable:

1. frame/tetrad/frequency convention;
2. exact incoming half-range authority;
3. unit-locked, once-only `virtual_spike`, `one_photon`, `two_photon`, and
   `raman` source laws;
4. Lagrangian boundary semantics or fixed-node remap/advection with
   conservation and JVP tests;
5. zero-speed event/restart semantics;
6. an external verifier resolving declarations to approved source bytes.

Until then, keep every physical-face/materialization flag false and the claim
`NO_PASS_REC_PHYSICAL_SPLIT`.

### Representation and unit firewall

Formula closure is not source authority.  In particular, keep these domains
distinct in types, digests, tests, and execution paths:

- the original-HyRec virtual spike acts on signed spectral distortion
  `Delta_f`; one-photon paired coefficients act on nonnegative total
  occupation `f`;
- converting `Delta_f` to `f` requires an explicit, hash-bound reference field
  and primal/JVP adapter.  An implicit conversion or direct composition is
  forbidden;
- two-photon and Raman primitives produce photon-packet rates per hydrogen atom
  per second.  They become occupation rates only after an approved deposition
  applies `n_H / mu_i * sum_s B_is R_sq` exactly once;
- a formula package, digest-shaped declaration, or manufactured vector may
  describe a proposed contract but cannot supply incoming values, bin/channel
  ownership, deposition authority, or an external byte verifier.

Keep the following event surfaces separately typed.  They coincide only under
additional static-grid assumptions and must not share a restart certificate:

1. `CHARACTERISTIC_R_H_ZERO`;
2. `RED_FACE_V_X_ZERO`;
3. `BLUE_FACE_V_X_ZERO`.

At an upwind ownership switch, the one-sided directional derivatives need not
form a Frechet JVP.  A tangential or simultaneous event therefore fails closed
unless an approved accepted-transaction/saltation contract covers it.

## 5. Checkpoints and handoff

A durable checkpoint contains only:

- phase/objective;
- completed and unresolved work;
- decisions and assumptions;
- changed artifacts and branch/commit;
- verification actually run;
- current blockers;
- exactly one next action.

Reuse unchanged valid evidence. Do not regenerate immutable historical evidence
or duplicate machine-readable inventories into prose. An explicit backup or
checkpoint request interrupts optional analysis and review immediately.

## 6. Current mechanical controls

- `tests/trajectory/test_rec_local02_portable_receipt.py` binds V1 fingerprints
  to the NumPy feature lane while requiring V2 semantic invariance.
- `tests/trajectory/test_directional_face_admission.py` binds the exact
  zero-speed ordered nodes and preserves all physical-admission blockers.
- `scripts/run_rec_local02_source_bound_gate.py --check-portable-receipt`
  performs read-only V2 semantic validation.
- `scripts/run_rec_next01_coding_research.py --check-record` performs read-only
  coding-record semantic validation.
- The current stage `MANIFEST.sha256` verifies stored publication bytes.

Broader suites are run only when they can detect a distinct affected failure.
Missing optional dependencies and unavailable hardware lanes are recorded as
environment gaps; tests and scientific contracts are not weakened to hide them.
