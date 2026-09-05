# REC-DONOR-02: bounded preimplementation contract repair

## Authority and scope

The owner explicitly authorized only repairs A and B below. The exact parent
is commit `2dfd464efe91b319993e6c6759d380d53d0f3fde`, tree
`0fdb8bf0904df05ef5b495f3f0b19e5c4444a886` (Draft PR #57).

This amendment takes precedence only for the threshold probe and the
hash-only deposition success expectation in the parent's `CONTRACT.md` and
test matrix. The historical contract, RED runner, manifest, workflows and
archived evidence are preserved byte-for-byte; they describe the original RED
snapshot, not this amended child. No file under `src/` is changed.

The five owner-required files were read at that parent: `AGENTS.md`,
`docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md`, the donor-01 `CONTRACT.md`,
`tests/trajectory/test_rec_donor01_typed_physical_source_red.py`, and
`src/full_bianchi_hyrec/trajectory/com_source_deposition.py`.
`HANDOFF_PROMPT.md` was also read. Its old REC-NEXT-03 execution instruction
is not the current task; the owner's explicit bounded-repair instruction is.

## A. Separate support membership from equilibrium cancellation

Keep the original source law and SI convention:

```text
C[f] = eta*(1+f) - kappa*f
eta = 1/4 s^-1; kappa = 3/4 s^-1; f is dimensionless.
support = [2.0e-18 J, 2.5e-18 J); outside policy = ZERO_OUTSIDE_SUPPORT.
```

At `f=1/2`, `C=0` even at the included lower endpoint. The former
`assertNotEqual(... occupation=0.5, 0)` contradicts equilibrium. Support
membership cannot be inferred from a nonzero source at equilibrium.

The repaired support probe uses `f=2`, so the active value is exactly
`-3/4 s^-1`. Its four energy probes require:

| Photon energy (J) | Occupation | Exact action (s^-1) |
| --- | ---: | ---: |
| 1.99e-18 | 2 | 0 |
| 2.00e-18 | 2 | -3/4 |
| 2.25e-18 | 2 | -3/4 |
| 2.50e-18 | 2 | 0 |
| 2.00e-18 | 1/2 | 0 |

The final row independently preserves detailed balance at the included
endpoint. No coefficient, endpoint, endpoint-inclusion flag, tolerance,
source-off rule or time/frame convention changes.

The unchanged analytic tangent is

```text
dC = (1+f)*deta - f*dkappa - (kappa-eta)*df = 13/16 = 0.8125
```

for the existing interior JVP fixture. The checker uses `Fraction`, not a
finite-difference approximation or a substitute production module.

## B. A declaration is not an executed deposition

A validated `PacketDepositionBinding` containing hashes and a declared
`application_count=1` is a declaration, not an execution receipt. It contains
neither the matrix elements nor a verified operator resolver in this fixture.

Both a missing binding and the supplied hash-only, unresolved binding must
cause `deposit_packet_rate` to raise `DepositionAuthorityError`. The existing
rejection of `application_count=2` is retained. Setting a count to one does
not prove that any conversion ran, and returning that count cannot establish
once-only execution.

A future successful deposition requires resolved and verified `B_is`, positive
mode measures `mu_i`, source rates `R_s`, the hydrogen density, compatible
source/normalization identities and evidence that the declared operation
actually ran:

```text
df_i/dt = n_H/mu_i * sum_s B_is R_s.
```

`n_H` and `mu_i` have units `m^-3`; `B_is` is dimensionless; the packet-rate
normalization and source multiplicities must be declared so that the output
is an occupation rate in `s^-1`. Hash-shaped strings alone do not provide
these data. No physical matrix, grid, resolver, normalization map or successful
execution API is selected or implemented here.

`COMSourceDepositionPlan` is an existing reference component with actual
matrix/measure operations. It is read only: not modified, imported, executed,
wrapped, or promoted by this repair.

## Verification and identity boundary

The read-only checker `verify_fixture_repair.py` compiles and collects the
amended test without running its 16 test bodies. It checks the five exact
support fixtures, preserves the JVP value, detects both original defects and
ensures every byte outside the two authorized method bodies is unchanged.
It also checks that both deposition calls sit under the required exception
assertion. This is a test-contract check, not a production-behavior result.

Reproduce in a full checkout of this child using only the standard library:

```bash
python docs/research/rec_donor02_contract_repair/verify_fixture_repair.py
```

For an offline selected-file worktree, `--parent-file` accepts the original
test only after verifying Git blob `59b58011629b83fefe99670e870fa99ffa18e7f5`.
The recorded run used Python 3.13.5, not the operator's Python 3.12.13.
`VALIDATION_RECEIPT.json` records the actual environment and executed checks.

The operator's `$HOME/Dropbox/bianchi/rec_bianchi` was not mounted in this
session and was not touched. Native Git fetch failed at DNS. The fallback
used a separate no-checkout Git worktree with the exact parent commit/root
tree reconstructed from connector readback and accepted only after their
native Git object hashes matched. Only selected blobs were materialized.
No full-checkout cleanliness or repository-wide test result is claimed.
Publication applies the four declared paths to the exact remote parent tree.

Historical identities remain distinct:

```text
source_head_sha       2dfd464efe91b319993e6c6759d380d53d0f3fde
PR_merge_checkout_sha 9ab85c1fc33c9d785d3796946ee0fc6ab63a8743
shared_tree_sha       0fdb8bf0904df05ef5b495f3f0b19e5c4444a886
relation              IDENTICAL_TREE_DIFFERENT_COMMIT
```

No historical evidence is regenerated. The original exact-path RED runner
is deliberately not run against this different child. Future-module absence
is not converted into a physics, kernel or deposition PASS. No broad suite,
new workflow, dependency install, plot or external CAS is needed or executed
for this bounded contract repair.

## Checkpoint and one next action

Completed: A's support/equilibrium fixture is consistent; B's hash-only
execution success expectation is replaced by explicit refusal. The new
module, physical deposition, BASS binding, provider admission, ready and
merge remain outside scope.

The single next action is the minimal representation-neutral source module
under this amended contract, including fail-closed unresolved deposition.
Real operator binding and physical-source admission remain separate future
work. No new review loop or duplicate RED gate is introduced here.
