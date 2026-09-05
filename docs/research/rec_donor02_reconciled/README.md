# REC-DONOR-02: amended-contract / existing-source reconciliation

## Frozen objective and ancestry

Implement the minimal module under the owner-corrected contract, without
rewriting a source that already exists. The current readback found two sibling
PRs that must be distinguished:

- PR #59, parent for this child: `8436c135d62ebc33e329b5541ebea53d9a067ffd`,
  tree `b1b71f7571b5d58b25164e37149d645e4bef0b46`. It fixes the equilibrium
  support probe and refuses unresolved hash-only deposition.
- PR #58, source donor: `a83204c887785ee3453be2c2361b7fda012e16ba`.
  Its exact-head run 33914620365/job 101158794419 executed 27 tests: 26
  passed and one errored at the obsolete deposition-success expectation.
  That historical failure remains a failure and is not rewritten.

Only one production file is added, by reusing the existing Git blob:

```text
src/full_bianchi_hyrec/physical_source_authority.py
6d4f39d48993c4715f5002ba068e8dcf98336be3
```

The PR58 safety suite and numerical probe are also reused byte-for-byte:

```text
tests/trajectory/test_rec_donor02_source_safety.py
e432652b4f626bd9cf98d96f9770ba44e36cea44
scripts/probe_rec_donor02.py
c2fbd594d1ca05b3165890ba156056257f9cfdfa
```

The PR59 test is retained except for the explicit absence-to-presence control
migration, its method name and explanatory comments/docstring. All thirteen
behaviour methods, including both owner corrections, are byte-unchanged.
No old contract, amendment, receipt, RED runner/manifest, policy, trajectory
module, physical data, COM deposition code or other repository is modified.

## Observable outcome and bounded verification

The candidate is NOT GREEN until a fresh exact-head execution succeeds.
The read-only runner checks exact borrowed blobs, the authorized test migration,
the single production addition, scoped diff hygiene, syntax, all 27 tests,
36 rational action cases, 108 rational fixed-coordinate JVP cases, six adjacent
float support probes, three formula mutants and frozen semantic hashes in two
fresh processes. There are no xfails, skips or error-to-success relabels.

```bash
python3 -B scripts/run_rec_donor02_reconciled.py \
  --expected-head <exact-commit> --output-dir <new-directory-outside-worktree>
```

It requires a detached worktree. The workflow checks out the exact push SHA
with read-only permissions and no persisted credential. Historical RED gates
are not rerun on the changed child. No native build, installation, broad suite
or fabricated physical matrix is needed. It is not repository-wide validation.
The operator's Dropbox checkout is not mounted or changed by this session.

The prior execution's TDD sequence is preserved: PR57 implementation-absent
RED, PR58 additional safety RED and candidate, PR59 owner-approved repair,
then this exact-byte reconciliation. No new duplicate RED gate is introduced.

## PHYS-MATH audit

This is the existing scalar, angular-representation-neutral affine primitive:

```text
C[f] = eta(1+f)-kappa*f = eta-(kappa-eta)*f
dC = (1+f)*deta-f*dkappa-(kappa-eta)*df
```

Occupation is nonnegative and dimensionless; primary rates are nonnegative
inverse seconds; chi=kappa-eta is signed; photon energy is in joules in the
declared hydrogen rest frame. No c, hbar or k_B is set to one or inserted.
Spacetime signature remains (-,+,+,+); no spacetime tensor is computed here.
The JVP is partial at FIXED photon energy, support and trajectory/event binding.
It is not an event/saltation, moving-support or physical background JVP.

The PR59 values remain exactly C(1/2)=0, C(2)=-3/4 s^-1 on active support;
outside [2.0e-18,2.5e-18) J the action is zero. The tangent fixture is 13/16.
Source off has non-unique equilibrium; equal positive rates have no finite
equilibrium; kappa>eta has eta/(kappa-eta); amplification remains permitted.

The companion-frequency sum is labelled MANUFACTURED_LINEAR_PACKET_PROBE.
It tests nonlocal dependency, not the HyRec two-photon/Raman physical law.
Unresolved deposition always raises: a matrix hash and application_count=1
are not an operator evaluation. Angular/moment bindings execute no transform.
All source provenance remains DECLARED_NOT_AUTHENTICATED, and physical-authority
and provider-export properties remain false.

## PHYS-MATH-CODE audit and remaining risks

Exact donor reuse prevents accidental source-law or numerical changes during
contract reconciliation. The runner rejects any new production delta beyond
the source file, any source/safety/probe blob drift, or any unapproved test edit.
Factory construction, immutable nested metadata, signed-zero identity, overflow
refusal, target/source mismatch, restart binding and observer-boost rejection
are covered by the retained safety suite.

This review is by the same assistant; no independent reviewer PASS is claimed.
Rational reference arithmetic is algorithmically distinct, not another agent.
Remaining limits: no authenticated input resolver; no executed deposition;
no original atomic kernel; no global/coupled JVP; no BASS state wiring; no
provider. Public frozen Python objects are not a hostile-code security boundary.
Zero dyadic residuals are not an arbitrary-input binary64 error bound.

The retained probe writes two SVGs and their CSV data. Numerical-coordinate
checking is not rendered visual inspection; rendered_plot_audit remains
NOT_PERFORMED unless a separate actual viewing is recorded. No physical
history or coupled convergence is inferred from those manufactured curves.

## Literature and formal-tool readback

Fresh SciSpace discovery was checked against the primary abstracts:

- Hirata, Phys. Rev. D 78, 023001 (2008), arXiv:0803.0808v2:
  resonant two-photon processes and Raman transfer require the appropriate
  radiative-transfer treatment, not a generic local effective coefficient.
- Ali-Haimoud and Hirata, Phys. Rev. D 83, 043513 (2011), arXiv:1011.3758v2:
  HyRec couples radiation-field evolution and atomic populations/free electrons.

These are scope/method references only; authority_effect=NONE. No paper-derived
coefficient, source payload or physical-deposition map is introduced here.

Fresh Wolfram context and evaluator both failed BEFORE any kernel result:
MCP SSE endpoint probe HTTP 404 (not the historical 502). Assistant container
and Python entrypoints returned ClientError before execution. The available
execution route is GitHub-hosted Python and the exact Fraction oracle. No fresh
Wolfram, SymPy, mpmath, Octave, Sage, Singular or Lean PASS is claimed here.

## Checkpoint and one next action

On an executed protocol PASS, the minimal representation-neutral local-source
protocol is complete under the amended contract, while physical admission is
unchanged. The next task is a bounded resolved-deposition adapter using the
existing COMSourceDepositionPlan and explicit verified B, mu and R inputs.
A manufactured fixture can verify its computation but cannot supply authentic
atomic data or physical channel ownership. Do not add another source-metadata
redesign before testing that actual operation.

NO_PASS_REC_PHYSICAL_SPLIT. No physical source authentication, BASS/REI binding,
provider export, repository-wide all-green, ready transition or merge.
