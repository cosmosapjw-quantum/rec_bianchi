# REC-DONOR-01 typed physical source expected-RED implementation plan

> **Execution rule:** complete only this test-first node.  Do not add the future
> production module until the exact expected RED is observed and read back.

**Goal:** freeze the minimal physical and software contract for a
representation-neutral primordial-recombination source owner.

**Architecture:** the physical owner is a future standard-library module at
`src/full_bianchi_hyrec/physical_source_authority.py`.  Existing original-HyRec
rate tables, constant-pair transfer, 26-node source assembly, trajectory logic,
and BASS adapters remain separate consumers/donors.  This stage changes no
production source.

**Conventions:** photon/boson; hydrogen rest frame; physical seconds; photon
energy in joules; nonnegative primary emission/absorption; signed derived net
affine coefficient; no local-observer boost; no implicit integrated closure.

---

## Task 1 — Freeze exact authority and allowed paths

**Files:**

- Create: `docs/research/rec_donor01_typed_physical_source_red/STAGE_MANIFEST.json`
- Create: `docs/research/rec_donor01_typed_physical_source_red/DAG_STATE.json`

**Checks:**

```bash
test "$(git rev-parse 926e0c79a3fe7c3f5b24d5c5bb81304332def232^{tree})" = \
  ce0654041d097768fae4f6a52b23c2137558f7be
git merge-base --is-ancestor \
  926e0c79a3fe7c3f5b24d5c5bb81304332def232 HEAD
```

The exact changed-path set contains only the test, runner, workflow, and bounded
documentation listed in the manifest.

## Task 2 — Define the future API through failing behaviour tests

**File:**

- Create: `tests/trajectory/test_rec_donor01_typed_physical_source_red.py`

The test module contains 16 tests:

```text
3 controls
13 future behaviours
```

The future behaviours cover source identity, physical metadata, positive
primary rates, stimulated emission, equilibrium, support/units, analytic JVP,
nonlocal two-photon/Raman typing, once-only deposition, trajectory/restart
identity, moment-map binding, 26-direction rank honesty, and the observer-boost
firewall.

The future module is intentionally absent.  Only that absence is converted to
assertion failures.  Missing existing dependencies and collection errors remain
errors.

## Task 3 — Add an exact fail-closed RED classifier

**File:**

- Create: `scripts/run_rec_donor01_typed_physical_source_red.py`

The runner must require:

```text
base tree                  exact
base ancestry              true
changed path set           exact
src delta                  none
future module              absent
git diff --check           pass
worktree                   clean
tests                      16
assertion failures         exact named 13
controls                    3
errors/skips               0/0
```

The sole wrapper PASS is:

```text
PASS_EXPECTED_REC_DONOR01_TYPED_PHYSICAL_SOURCE_RED
```

All receipts are written outside the Git worktree.

## Task 4 — Add the read-only hosted execution surface

**File:**

- Create: `.github/workflows/rec-donor01-typed-physical-source-red.yml`

The workflow uses `contents: read`, a full history checkout, the system Python,
and no project dependency installation.  It uploads only the external RED
receipt/log bundle.  A run with no assigned runner is `PRESTART_NO_EXECUTION`.

## Task 5 — Compile the physics and code audits

**Files:**

- Create: `docs/research/rec_donor01_typed_physical_source_red/CONTRACT.md`
- Create: `docs/research/rec_donor01_typed_physical_source_red/PHYS_MATH_AUDIT.md`
- Create: `docs/research/rec_donor01_typed_physical_source_red/PHYS_MATH_CODE_AUDIT.md`

The audits must distinguish:

```text
local affine source             != nonlocal packet kernel
packet rate per H per s         != occupation rate per s
physical source identity        != angular realization identity
source-frame physics            != local-observer pullback
source contract                 != BASS coupling or provider admission
```

## Task 6 — Record independent research and tool boundaries

**Files:**

- Create: `docs/research/rec_donor01_typed_physical_source_red/SCISPACE_METHODOLOGY_LOCK.md`
- Create: `docs/research/rec_donor01_typed_physical_source_red/WOLFRAM_STATUS.json`
- Create: `docs/research/rec_donor01_typed_physical_source_red/OPERATOR_READBACK_AND_ENVIRONMENT_DIAGNOSIS.md`

The literature has method/scope effect only.  Wolfram HTTP 502 is recorded as
no result.  The historical BASS R5 transcript is classified as focused
source-protocol PASS plus an unprovisioned backend cone, not as a scientific
failure.

## Task 7 — Execute exactly once and stop

After publication, run the exact wrapper once on the immutable PR head.  If it
returns the declared classification, preserve the receipt and stop.  Do not add
the GREEN module in the same execution cycle.

If any of the following occurs, stop as invalid rather than repairing around it:

```text
wrong base/tree
unexpected changed path
production source present
error or skip
failure set differs
existing dependency import error
dirty worktree
```

## Successor

Only a separately authorized successor may implement:

```text
REC-DONOR-02_MINIMAL_REPRESENTATION_NEUTRAL_SOURCE_GREEN
```

Its first patch is exactly one production module plus the minimal test migration
required to turn these 13 behaviours green.  Angular faces, solver wiring,
providers, performance work, and broad refactoring remain deferred.
