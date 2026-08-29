# Codex handoff — rec_bianchi split-domain replacement

```text
scientific state: HOLD
exact next action: REC-BOOT-00
terminal ceiling: PASS_REC_SPLIT_DOMAIN_REPLACEMENT_AND_INTERFACE_V1
```

## Exact audit evidence

```text
audit branch: audit/ode-four-loop-external-audit-20260823
audit commit: 4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3
audit tree:   3f8731cfab9c9493fcdaa18d855d95768eee1d47
```

The package branch was created from live `main`. Resolve and record its exact pre-package parent before mutation. The audit branch is read-only evidence and a source-reconstruction input; never merge it wholesale.

## Preserve local state

Use a new isolated worktree. Do not clean, reset, stash, amend, rebase, force-push, switch an occupied worktree, or delete unknown bytes.

## Intake

Read this package, then the repository's `HANDOFF_PROMPT.md`, `state/PROJECT_STATE.json`, recovery receipt, remote/supersession ledgers, `docs/CURRENT_STATE.md`, the dynamic ownership formalism, and the split-domain replacement plan.

Run the documented offline bootstrap and quick checks. Classify every commit between the exact main-derived base and the audit head as:

```text
SOURCE_BEARING_V075
AUDIT_OR_PACKAGING_ONLY
UNRESOLVED
```

Apply only source-bearing commits whose provenance receipts match. Stop on unresolved source identity; do not infer missing bytes.

Verify the canonical HyRec archive byte identity:

```text
archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27
```

## Execute

Proceed in order:

```text
REC-BOOT-00
REC-SPLIT-01
REC-VERIFY-02
REC-INTERFACE-03
REC-DELIVER-04
```

Write genuine RED before implementation. The replacement must own exterior native cells, interior COM cells and each interface exactly once. Preserve indices 136..143 inside COM; handle crossing edges (135,136) and (143,144) explicitly. No additive full-native-plus-COM path is permitted.

Implement residual and analytic JVP together. Compare JVP independently on nondegenerate interface states; do not use the implementation's own residual report as the oracle. Close number, energy, four-force, primitive/Schur/interface, event and restart ledgers in one stage.

Emit a typed rec→rei interface receipt, but do not edit `rei_bianchi` or its lock. The receipt must bind source/input, state and rate schema with units, residual/JVP identity, ledgers, event/restart semantics, validity domain and numerical uncertainty.

Use typed identity: exact bytes for immutable source and contractual deterministic evidence; residual/invariant/convergence and semantic agreement for numerical histories. A packaging hash difference alone is not scientific failure.

Do not start the dynamic macro, preconditioner, Rust/performance optimization, production history or Bianchi family sweep. Finish with one bounded review, at most one reproduced P0/P1 repair, ordinary push and one draft PR. Stop without merge or ready transition.