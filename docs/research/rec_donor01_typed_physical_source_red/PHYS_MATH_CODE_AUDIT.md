# PHYS-MATH-CODE audit — REC-DONOR-01 RED

## Verdict

```text
status                 PASS_FOR_IMPLEMENTATION-ABSENT_RED_SOURCE
production change      none
runtime RED             not yet observed
physical source         absent
provider                withheld
```

## Existing code-path reality

The current repository already contains three distinct layers that must not be
collapsed:

1. `trajectory/primitive_rates.py` binds original-HyRec tables, units, and local
   interpolation/JVP information.
2. `trajectory/paired_source_transfer.py` provides a robust exact constant-pair
   formula primitive and explicitly classifies itself as nonauthoritative.
3. `trajectory/directional_source_assembly.py` demonstrates typed source-channel
   separation on an ordered 26-node research grid, while explicitly withholding
   incoming physical-face authority and packet deposition authority.

Those paths are useful donors and controls.  None is silently promoted into the
new representation-neutral authority.

## Why a new module is justified

The missing interface is not another numerical transfer routine.  It is a
physical-source identity object above representation-specific consumers.  The
future module therefore belongs at

```text
src/full_bianchi_hyrec/physical_source_authority.py
```

rather than inside the current 26-node assembly module.  This placement avoids
making a directional face, a trajectory solver, or the BASS adapter the owner of
atomic source semantics.

## Test-first architecture

The RED test uses only Python's standard library.  It loads the future top-level
module only after verifying that its exact path exists.  On the RED head every
future-behaviour method calls the same loader, which converts only the missing
future module into an assertion failure.

The following are not converted into admissible failures:

- missing existing package/dependency;
- syntax or collection error;
- import error from inside an existing module;
- wrong base ancestry/tree;
- unexpected changed path;
- any `src/` delta;
- dirty worktree;
- skip or unexpected success.

Thus the expected RED cannot be manufactured from an unprovisioned BASS backend
or a broken Python environment.

## Runner contract

`scripts/run_rec_donor01_typed_physical_source_red.py` performs:

1. exact base tree verification;
2. base-ancestor verification;
3. exact changed-path verification;
4. production-path absence verification;
5. no-`src/`-delta verification;
6. `git diff --check`;
7. clean-worktree check;
8. direct `unittest` execution;
9. exact 16-test and 13-failure-name comparison;
10. zero errors/skips/unexpected-successes;
11. post-run clean-worktree check;
12. external atomic receipt, summary, log, and SHA-256 manifest publication.

The wrapper exits zero only for

```text
PASS_EXPECTED_REC_DONOR01_TYPED_PHYSICAL_SOURCE_RED.
```

That classification is an executed TDD state, not a source or physics pass.

## P0/P1 detector mapping

| Failure mode | Detector |
|---|---|
| local and nonlocal laws conflated | nonlocal-kernel test |
| packet unit converted zero or two times | deposition-binding test |
| angular realization changes source identity | representation-neutrality test |
| arbitrary-rank claim from 26 nodes | fixed-face rejection test |
| observer boost folded into source | boost rejection test |
| trajectory/restart reuse across contexts | trajectory-binding test |
| integrated closure inferred from source | moment-map binding test |
| source hash omits physical/provenance fields | metadata/hash mutation test |
| signed net rate treated as primary positive rate | primary-pair test |
| JVP label hides finite differences | analytic-JVP test |

## Minimal GREEN implementation boundary

A future GREEN should add one standard-library module only.  It should not
modify the existing directional assembly or trajectory integrators in the same
commit.  The first implementation can use immutable tuples, dataclasses or
validated value objects, canonical JSON, and SHA-256.  Numerical arrays,
quadrature, BASS imports, and provider exports are unnecessary at this node.

## Regression cone after GREEN

The minimal affected cone is:

```text
python -m unittest -v \
  tests.trajectory.test_rec_donor01_typed_physical_source_red

python -m pytest -q \
  tests/trajectory/test_paired_source_transfer.py \
  tests/trajectory/test_directional_source_assembly.py \
  tests/trajectory/test_directional_face_admission.py
```

The existing source-policy and packaging tests should be added only if the
future module becomes publicly exported.  Broad full-repository tests are not a
substitute for the focused physical contract.

## Current risks

### P1 — test contract is source-level until executed

The counts and failure names are statically designed but must be observed on an
exact checkout.  A hosted job that never receives a runner is
`PRESTART_NO_EXECUTION`, not a RED pass.

### P1 — future API is intentionally narrow

The tests define ownership, identity, units, local/nonlocal separation, and
firewalls.  They do not define a complete physical HyRec spectral kernel or a
BASS coupler.  Passing them later must not be described as provider admission.

### P2 — direct public export deferred

The RED does not edit `full_bianchi_hyrec/__init__.py` or
`trajectory/__init__.py`.  Public re-export should occur only after the module
has a GREEN implementation and focused compatibility review.

## Old local BASS log classification

The supplied historical BASS R5 replay passed all 11 focused source-protocol
tests and then failed before native numerical comparison because `jax` and
`bianchi_rustcore` were absent.  That is an environment/provisioning gap, not an
observed REC-DONOR-01 failure and not evidence against the later trusted R5D
receipt.  No REC source contract or BASS production code is changed in response
to it.
