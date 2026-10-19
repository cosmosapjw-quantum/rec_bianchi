# R3O independent C9 review — VigilODE/Rust extension

Review date: 2026-10-19 UTC. Selected stage: C9 only. Final review status:
**C9_COMPLETE: RETAINED_LOCAL_NUMERICAL_SCOPE_PASS; THREE_P2_REPAIRS_CLOSED;
FRESH_CARGO_COMPILE_PENDING.**
This is a bounded source/evidence review of the new Rust caller and its launchers.
The reviewer changed only this report, performed no native build or new physical
integration, and dispatched no recursive agents. Corrected launcher identities and
targeted controls have been checked. There is no remaining critical source finding
for the retained/default 16-step path. One nonblocking one-step CLI inconsistency
is recorded below. The parent owns the corrected package's fresh compile gate;
this report does not wait for or predict that result. The capsule is not a Git
checkout. The existing core R6/C9 review and parent full-raw packet readback are
reused; they are not described as new reviewer executions.

## Outcome that already has direct support

`build_002/build.json` and `verify_001/verification.json`, below
`/workspace/scratch/afe554957b2e/rec_recovery/r3o_rust_runs/`, were actually read.
The reviewer independently verified the recorded binary hash, all 57 numerical
artifact hashes, 102 six-scalar byte comparisons, and 64 retained scalar recurrence
and memory-rotation checks. At that readback, every code hash in both receipts
matched the current capsule. No P0/P1 predictor, input-stage, normalization, or
source-operator defect was found in this bounded path.

| Retained object | SHA256 / result |
|---|---|
| `build_002/build.json` | `5c83ec3c219d9516d4b82a6eb5e36de671a74ed805d9bede3af37e501d5c1daf` |
| Newly linked Rust caller | `a29462c2b47508a88396357c43fc303364dcb5a28208ff1cb81cc39a1b1a2907` |
| `verify_001/verification.json` | `8ea76f2e08b824734ddf4e5c628931772facb87359add9833244d68314a5fdf8` |
| `verify_001/primary.json` | `771795452b3ca3597a1f31ced387644e19434ffab01d507f46057c67b4a023d6` |
| Fixed Rust / original C | 17 states, 6 scalars each, all 102 byte comparisons match |
| Independent Python comparison | State and common-input RHS residuals meet the unchanged fixed-h2 gates |
| Exploratory RODAS | 16 attempts, 16 accepted steps, 17 direct outputs, 225 integration-source callbacks |
| Limited-attempt control | Exit 3; 1 accepted step; 2 outputs; last committed output retained |
| Callback failure control | Exit 3; 3 rejected attempts; 4 attempted callbacks; 1 actual source call; initial committed output retained |

**The combined diagnostic PASS is not original same-h equivalence for RODAS.**
Independently recomputing the saved comparison gives maximum scaled residuals
`[2.530216356188792, 0.014734335610808365]` for xe and Tm, and maximum WRMS
`1.7891634790833368`. The xe comparison exceeds 1 in the old same-h scale.
The output correctly declares `EXPLORATORY_METHOD_COMPARISON`,
`admission_test=false`, `same_algorithm_parity=false`, and
`production_admission=false`. These declarations are necessary to interpret the
measured result. The fixed Rust/C byte lane and the independent Python fixed-h2
lane have their own successful comparisons.

The faer-backed 2x2 check is real: its linear residual is
`1.2507140131633662e-16`, and its solution differs from the explicit 2x2 formula
by 0 at the retained floating-point values. The RODAS integrator reports
`InPlaceZeroSkipping` for its own LU backend. Therefore faer is correctly reused
in the separate actual-Jacobian linear probe; it is not the claimed backend of
every RODAS stage and no speed result follows.

## Findings and smallest corrections

### C9-RUST-P2-01 — finalization can retain PASS after its resource allowance — CLOSED

**Original relevance: FIX_SOON before sealing final launcher resource claims.** The small
retained numerical run itself is far below its allowance; this finding concerns
the general launcher contract and does not invalidate the retained state values.

Objects: `scripts/build_r3o_rust.py::main` finalizer (reviewed source SHA256
`3e3f0ae3cb19fb49c8b47eac2896850b33abe5eaa70687b1f40eb15080d79743`,
lines 361–391), and `scripts/verify_r3o_rust.py::main` finalizer (SHA256
`4877bf538184d06143d45a2a5bef051130a198d25760a7b0c68498814c731055`,
lines 338–362).

The build finalizer hashes source/dependencies and records total CPU/wall, but
does not reapply its 240 CPU-second / 480 wall-second admission criterion. The
verification finalizer applies its 20/60 criterion before hashing its output
artifacts, so that work is absent from the reported total and decision.

Actual bounded reproduction: the reviewer compiled and executed the exact
`ast.Try.finalbody` statements from each current `main`, replacing only I/O,
source hashing, and clocks with in-memory controls. No build or physical
calculation occurred. The build control moved from 238 CPU seconds to 241 during
source finalization and to 481 wall seconds; its output remained `BUILD_PASS`,
exit 0. The numerical control moved from 18 CPU / 57 wall seconds to
20.25 CPU / 60.25 wall seconds during the artifact hash; its output still
reported 18/57 and the combined numerical PASS, exit 0.

Smallest correction: finish required source/input/binary/artifact identity work
before the final resource measurement, reject an over-limit total with nonzero
exit status, and reserve a bounded final receipt-writing margin within the same
allowance. Preserve partial/failure evidence. A targeted control of the actual
finalization branch, with an over-limit and a below-limit case, is sufficient;
no historical numerical campaign is needed.

Closure: the actual finalizers now perform required identity/artifact hashing
before `finalize_resource_record`, which measures the total and reserves 2 CPU
seconds / 3 wall seconds for the final receipt serialization/fsync. Its scope
explicitly excludes that last write; it does not claim an observed post-fsync
total. The reviewer executed the corrected helper plus the real finalizer ASTs
with controlled clocks: build 241 CPU / 481 wall and verification 21 / 61 both
became FAILED, exit 2; both 2.5 / 3 below-limit cases remained PASS, exit 0.
These four synthetic controls advanced zero physical steps.

The directly controlled build source was `fff07473328d1c2a69c956f72ffba7acc918232f3ff79825e79fe2c4abdf8ead`;
the verifier was `e99dbc6e022eab3301c6f4db8ee3cd5bd2e27a53eeeba2872a84a03e6d646a26`.
The final build source `d33f4761482720cd822a3006460e9462091c9219180541e78cdc51a4ca35cfd5`
adds exactly seven resource-coverage metadata lines. Removing that inspected
block reproduces the controlled build source SHA256 exactly. There is no change
to the controlled helper, finalizer, lock logic, or process monitor. The separate
retained corrective suite also exercised both finalizers against the final d33
source and passed. Closure therefore does not require another physical run.

### C9-RUST-P2-02 — unavailable descendant telemetry is silently recorded as zero — CLOSED

**Original relevance: FIX_SOON for accurate sandbox resource evidence.**

Object: `scripts/build_r3o_rust.py::live_usage`, lines 60–73, and the associated
`Budget.run` resource fields in the same source identity as P2-01.

Reading `/proc/PID/stat` and `/proc/PID/task/PID/children` is one `try` block. If
the children entry is absent, `FileNotFoundError` discards the successfully read
stat values and returns `(0., 0)`. A new bounded control launched a Python child
that allocated 8 MiB and slept 0.5 seconds. The child PID and Popen PID both were
6; `/proc/6/stat` existed, `/proc/6/task/6/children` did not, and `live_usage(6)`
returned CPU 0 / RSS 0. The readable stat exposed nonzero RSS (483,328 bytes).
The independently observed stat value is only that surface's value, not a claim
to have measured the child's true peak allocation. Every retained command in
build_001/build_002 similarly records `max_polled_process_tree_rss_bytes: 0`.

Smallest correction: distinguish a disappeared process from unavailable
descendant enumeration. Preserve usable single-PID statistics, mark tree/peak
telemetry unavailable or partial instead of claiming an observed zero, and state
the actual enforcement scope. Existing per-process RLIMIT_AS/RLIMIT_CPU and
process-group termination must remain. If aggregate live enforcement is claimed,
use a working process-tree observation mechanism or fail that claim explicitly;
the absence of telemetry is not a numerical failure. Reaped-child CPU totals are
separate from live/peak observations and should retain that distinction.

Closure: the repaired monitor maps the child's inner Popen PID to the procfs PID
using the launcher's own children and NSpid; it falls back from task/children to
PPID stat enumeration. Missing descendant enumeration no longer discards usable
stat data. It records null when there was no live RSS sample, states that its
50 ms RSS samples are not an exact peak, and distinguishes reaped-child CPU from
live observation. RLIMIT_AS/RLIMIT_CPU and process-group kill/wait remain.

The reviewer's real corrected `Budget.run` control used an in-memory receipt/log
sink and a synthetic Python CPU loop, not a native or physical calculation. It
mapped Popen PID 6 to procfs PID 349846, recorded RSS 6,553,600 bytes and
0.434228 process-tree CPU seconds / 0.4187630679953145 wall seconds, then killed
and reaped the child with the expected `R3O_AGGREGATE_CPU_CAP`, return code -9.
The parent's separately read `guard_fix_002/control.json` records PASS with the
same expected refusal, 0.423261 CPU / 0.413156242997502 wall seconds and
6,553,600 sampled RSS bytes. Its SHA256 is
`61f6ceae1f8868116d201dbcef1242c687d429ba40c64eca637caf422ec71a26`.
The intermediate guard_fix_001 missing-procfs-child failure remains a failed
control attempt. Old build receipts' zero RSS fields are not retroactively made
valid measurements of zero memory by this repair.

### C9-RUST-P2-03 — committed lockfile is regenerated before the code seal — CLOSED

**Origin: independently identified by the parent and confirmed in this source
review; one shared finding, not a second review demand. Original relevance: FIX_SOON.**

The reviewed launcher unconditionally executes `cargo generate-lockfile` before
capturing `code_before`. The subsequent `--locked` build locks the regenerated
resolution. In the default online Cargo route this can update allowed transitive
versions while still reporting unchanged before/after code for this invocation.
The actual retained lock contains faer 0.24.4 and matches the retained run, so
this is a reproducibility defect in future invocation, not evidence that the
retained binary linked another faer version.

Smallest correction, already sent by the parent to the implementer: require and
retain the committed lock, capture code identity before any command that could
mutate it, and build with `--locked`; use `--offline` only for the explicit
registry-vendor route. Check failure on missing/incompatible lock without
silently creating a replacement. Final build receipts should bind the corrected
launcher identity.

Closure: the final source requires the committed Cargo.lock before the first
Cargo command, captures `code_before` first, never runs generate-lockfile, and
uses `--locked` for metadata and build. The ordinary Cargo route remains usable
without a private registry-vendor directory. The source order was inspected;
the parent/implementer corrective suite then observed both a missing-lock
failure before any Cargo command and an actual locked Cargo exit 101 on a
malformed lock, preserving its bytes and producing no binary. The malformed
fixture is deliberately checked by `cargo build --locked`, because metadata
with `--no-deps` alone does not prove that the lock was parsed.

The actual corrective suite receipt is
`/workspace/scratch/afe554957b2e/rec_recovery/r3o_rust_runs/contracts_fix_002/contracts_receipt.json`,
SHA256 `c4dc18ea862e2346fc6fa03a64b05182c39e32dcf44ead189ac3d585dd3339e6`.
Its raw log reports **16 tests PASS**, no skips, 1.542 seconds for the suite;
the wrapper records 1.7661719999999999 CPU / 1.7651928689956549 wall seconds,
zero physical steps, unchanged request/binary and before/after source seals.
The retained binary is the original build_002 binary. This is corrective control
evidence, not another physical integration or fresh library compile. The reviewer
independently read and matched 22 selected guard/finalizer/lock/log artifacts
against the receipt and confirmed its final d33/e99/51c6 source identities.

### Closed source finding — default NCP/CI route required an unprovided registry

The initial source SHA256
`c35ce026d05f04d3d55c6989a6e12beb60afa57c8df39597b0d6359b1218381c`
required `--registry-vendor` or `REC_CARGO_VENDOR` for every build. The parent CI
uses `python scripts/build_r3o_rust.py --output r3o-ci/build` without either.
The revised `3e3f0ae...` source allows the ordinary Cargo route with no vendor
argument and reserves mandatory offline registry input for explicit dependency
reuse. This source-level incompatibility is closed. Actual fresh Cargo CI remains
a separate execution receipt, not a conclusion drawn from this code inspection.

### Parent packaging finding — upstream automatic build script omitted — SOURCE REPAIRED, COMPILE PENDING

This is the parent's concrete portability finding, not a new numerical failure.
Fresh Cargo CI for published commit `44934c47bc06af01a365f346ee19b830b4bda3d6`
failed while compiling rodas5p-integrators. The reviewer read the materialized
build receipt and stderr below
`/workspace/scratch/afe554957b2e/rec_recovery/r3o_ci_failed_44934c47/build/`.
The receipt SHA256 is
`a99e535dd684ddd96e34589d32996acef1a07d4f11f983bca7457feaf53824e5`;
it records status FAILED, wrapper exit 2 / Cargo exit 101, `numerics=NOT_RUN`,
160.25054099999997 CPU seconds and 159.068994161 wall seconds. Stderr identifies
unset `VIGILODE_CARGO_PROFILE_DIR` at g4_s5b0_regime_atlas.rs:5401 and 5683,
and unset `VIGILODE_CARGO_PROFILE` at line 5682.

The initial source archive omitted the upstream automatic
`crates/rodas5p-integrators/build.rs`. The corrected archive includes its unchanged
587 bytes, SHA256 `a212e1bd0d2d4c6286cbd8015fa01e317111788d535efecd41c37c408bac5f7e`,
Git blob `725309e91c989f79e5a5e75307addd7ae3478937`.
The reviewer read the script: it emits the two missing compile-time profile
variables and rerun-if-changed metadata; it changes no numerical operator.
The corrected archive and all selected source/member hashes were independently
read back as described below. This closes the identified missing-file source
defect. **Successful fresh compilation remains the parent's execution gate**;
archive inclusion alone is not BUILD_PASS. The old local numerical receipt is
neither refuted nor converted into fresh-Cargo evidence by this failure/repair.

### C9-RUST-P3-01 — advertised one-step verifier conflicts with its partial-run control — NONBLOCKING OPEN

Object: `scripts/verify_r3o_rust.py`, SHA256
`e99dbc6e022eab3301c6f4db8ee3cd5bd2e27a53eeeba2872a84a03e6d646a26`,
line 224 and lines 303–309. The parser accepts `--steps 1`, but the unconditional
diagnostic control uses max-attempts=1 and requires exit 3 / partial failure with
one accepted step. On the retained boundary, that step reaches tau=h; for a
one-step request it also reaches tf and is complete. The verifier would reject
the expected successful return from that child. This conclusion is a source
counterexample using the already retained accepted first step and the upstream
completion condition; no new one-step native execution is claimed.

Reproduction after a matched build: invoke the published verification command
with its otherwise valid build/packet/output arguments and `--steps 1`. The
smallest correction is to restrict this verifier to steps 2–32, or to make its
one-step partial-control expectation conditional. Default 16-step verification
and the retained 102 byte comparisons are unaffected. This does not block the
parent's 16-step compile/verification gate and does not request another campaign.

## Changed scientific surfaces actually reviewed

- `fixed.rs` consumes current F and `prev2` in
  `Y + h*(1.25*Fnow - 0.25*Fprev2)`, then rotates all four memories. The native
  C oracle advances its own six-scalar copy. It is never reseeded from the new
  Rust state. The independent Python tail remains separately derived.
- `contracts.rs` checks the pinned start/end/h2, bounded lengths, finite/domain
  states, index order, and paired absorbing-event metadata. Serde denies unknown
  fields. The portable checkpoint loader verifies the checked-in packet digest,
  six binary64 words per lane, cosmology, source/checkpoint identities, original
  producer identities, and unchanged reviewed reader hash.
- `ffi.rs` serializes initialization and all C calls under one process-local
  mutex. The C initializer is idempotent and guards missing rate files before
  the original reader. The private synchronous CLI has no worker-thread or
  reentrant callback route. FFI buffers have matching fixed C lengths.
- The bridge includes the already reviewed original-C low-z harness and invokes
  the unchanged four original translation units. Its continuous EMLA callback
  uses the supplied tau, xe, and Tm and explicitly rejects an out-of-span or
  out-of-stage evaluation. Reusing the fixed radiation-history index is safe
  in this explicit EMLA branch; the full transport branch is not selected.
- `diagnostic.rs` holds the two normalization scales constant. Its state
  differences differentiate the normalized RHS, and partial-t differences hold
  the normalized state fixed. `OdeProblem(... autonomous=false ...)` supplies an
  explicit partial-t callback. Upstream RODAS actually consumes this callback
  in nonautonomous stage construction. No autonomous FastSmall substitution or
  dense output is used.
- The initial continuous and fixed C RHS bytes agree. The thermal Jacobian
  relative discrepancy is `7.410278366797428e-12`; partial-t delta/half-delta
  relative consistency is `1.3505160253291377e-7`. These are local diagnostics,
  not a new convergence order result.
- Output lengths, dimensions, finiteness and every direct-grid time are checked
  before comparison. Four fresh in-memory controls rejected a truncated output,
  wrong state width, NaN output, and inconsistent fixed-lane stage metadata.
  Partial and failed-callback outputs retain committed output separately from
  uncommitted callback states; work performed before failure is not erased.

## Source/dependency identity and reused evidence

For the retained build's original packaging, the reviewer checked the SHA256 of
`rust/vendor/vigilode-a21d573-three-crates.tar.gz`
(`f36c451b9e80b529b1de989988a96561db830694bcfdb107fe47035151a8c8ba`),
its 123 packaged members, and all materialized member hashes against
`rust/VIGILODE_SOURCE.json`. The 122 selected upstream files are preserved;
the additional original root manifest and documented workspace member removal
are packaging changes. The parent's remote Git blob verification is reused,
not claimed as a new remote retrieval by this reviewer. Original history.c,
hydrogen.c, helium.c and hyrectools.c in the build directory independently match
the authoritative ZIP bytes. The reviewed h2 header-only change is reused.

At final source review, the corrected packaging metadata SHA256 is
`d05094bd55820f3d86cb7e00d0012d060b3834da5fb8fb47c3f2c9dc30ff18fc`.
The replacement archive is 731,431 bytes, SHA256
`77c03b85844909b45428bfafd066d2403cb6f7f1870b8a68d705c4bfd1e7aca4`.
The reviewer read it in memory, without extracting or rewriting inputs, and
matched all 123 selected upstream file sizes, SHA256 values and Git blob digests
against the recorded manifest; there are 124 packaged file members. The original
root Cargo.toml is retained as Cargo.upstream.toml, while the reduced workspace
manifest matches the recorded packaging transformation. The additional selected
file is the upstream build.rs described above. Local recomputation of Git blob
digests verifies their recorded identities; the parent's upstream Git retrieval
is reused rather than claimed as a new remote readback.

The retained build explicitly recompiles the C bridge and new Rust caller while
reusing read-only libraries compiled at `8a8bd409b1d96c7b7421f496d229e119fd3d284e`.
It records the selected source relationship to
`a21d573980f66fe02891bd216153443b5352f921`, a coherent graph of 163 dependency
edges, and unchanged before/after dependency hashes. This is not a fresh compile
of every a21d573 library. Default Cargo source compilation is a separate route:
the first actual CI failed before numerics, and the corrected package's fresh
compile outcome is pending at this review cutoff.

The parent preserved the source matching the executed build before removing
one extra EOF LF byte from Cargo.toml, the caller build.rs, contracts.rs,
diagnostic.rs, ffi.rs and the C bridge. The reviewer compared each preserved
member to the current file and verified `old_bytes == new_bytes + b"\n"` for
all six. The preserved archive
`rust_local/EXECUTED_SOURCE_build002_matching_files.zip` has SHA256
`10c5986f838ce3a243b6ccd4a6ac8bfee514eecd4028d30ff5edf50e526b3a24`;
the parent's `review/RUST_PUBLICATION_FORMAT.json` has SHA256
`88b2e9819a368f14439f623c8ec4eeb60e190d23b016e01ade185e8f2379e753`.
This supports unchanged source bodies under the documented EOF normalization,
not byte identity between the old and new files or a new binary execution.
Launcher, test and vendor packaging changes are substantive separate changes
with their own controls and pending compile gate, not hidden in that EOF claim.

The compact packet hash is
`4adfdeee1ae236725f8a654072498649c89f8e5b2e33f88eb6f40080ffbcb19d`.
Its seal, exact six binary64 values per lane, and reference to the parent's
`review/RUST_BOUNDARY_PARENT_READBACK.json` were checked. That receipt records a
real readback against reviewed full R3M raw inputs and zero numerical steps. The
reviewer did not repeat the approximately 400 MB raw intake.

`build_001` remains a preserved LLVM linker allocation failure under the 3 GiB
limit, with no new binary or numerical result. Its caller command records
6.672158 CPU seconds and 1.6237179860036122 wall seconds. It is not a physical
FAIL, and the prior core CI result is not Rust CI evidence.

## Reviewer execution and scope

The new controls stayed within the assigned 6 CPU-second / 30 wall-second
control allowance. The successful measured control invocations are:

| Reviewer control | Recorded CPU seconds |
|---|---:|
| Original finalizer counterexamples, real finalizer AST with controlled clocks/I/O | 0.072039650 |
| Original live telemetry counterexample, parent plus reaped child | 0.042374129 + 0.019444000 |
| Retained arithmetic/hash readback and four in-memory rejection controls | 0.129328402 |
| Corrected finalizers, source-order and preserved EOF-byte checks | 0.078830284 |
| Corrected actual CPU guard, parent plus reaped child | 0.117716435 + 0.417524000 |
| **Successful measured control total** | **0.877256900** |

One intermediate reviewer closure-control invocation exited with AttributeError
because its in-memory fake budget lacked the newly extracted helper's cpu_s
attribute. It emitted no usable CPU measurement; its process had a hard 2 CPU
second limit and an 8 wall-second alarm. This failed reviewer scaffolding attempt
is neither a passed control nor an implementation/numerical failure. The corrected
control then passed as recorded above. This disclosure keeps the unmeasured
attempt separate from the measured total rather than inventing an exact charge.
Source and existing-receipt reads are not new numerical campaigns or benchmarks.
There were zero reviewer native builds and zero new physical history steps.

Skill context actually read: physmath-research-loop 1.3.0 `SKILL.md`,
`references/CODING_LOOP.md` C9, `references/SUBAGENT_MODE.md`, and
`references/POLICY_INTEGRATION.md`, under the exact user-supplied plugin directory.
The permitted sole write is this report. The current callable inventory did not
expose an agent-message tool; actionable findings were returned through the
shared commentary and this report, without inventing send receipts.

This completes the selected C9 pass against the corrected file hashes and
scope-matched controls. Publication, backups and the fresh Cargo gate belong to
the parent; the reviewer neither changes their DAG files nor claims their future
results. The bounded node may record source review and retained 16-step evidence
as reviewed, while fresh Cargo compilation stays pending. No repeat of the core
scientific campaign is required by the resolved findings.

The original ZIP identity, h2=4.245e-5, original atomic/thermal operator, stage
boundary and unchanged same-h criteria remain the basis of the local comparison.
The inherited U5 original-h HOLD_9_FAIL and h2 HOLD_8_FAIL and closed historical
cost ledger are not reopened. Full h2 low-z 153327 steps, full h4, global
convergence, production speedup and Bianchi/REI/CMB admission remain NOT_RUN or
unadmitted by this extension; REI activation=false. The previously reported
core 835 PASS / 4 SKIP / 72 subtests is reused core CI, not Rust CI.

## Retained build_002 / verify_001 code identity

These are the actual mutually matching build/run source seals, not an inferred
Git commit. Later source repairs require their own explicit relation or receipt.

| File | SHA256 |
|---|---|
| `rust/rec-hyrec-vigilode/src/contracts.rs` | `7bc44b15caa479ac80735d1b4f140613a4da324ab0ca2e669af24027072b7cc1` |
| `rust/rec-hyrec-vigilode/src/ffi.rs` | `d03b025a1b9f687757ab2cfd0d0e15e67d5606086023a375f84aaa11a8c49a56` |
| `rust/rec-hyrec-vigilode/src/fixed.rs` | `615f75ab44030fcde9858401b75e8696f337b39d599f0fb7c94d3db94d1a6d33` |
| `rust/rec-hyrec-vigilode/src/diagnostic.rs` | `68d63c32d988b81e767c6fae8b417d6e8efe429c32da1d1df963e57f7b74ad57` |
| `rust/rec-hyrec-vigilode/src/main.rs` | `cb6869b061187ebdd46a5126318e8333baa63b16cca5509748c1effb47deea20` |
| `rust/rec-hyrec-vigilode/Cargo.toml` | `e609d27c770495ba2c09dfc57be83c2f866d548bda10e46cae087e9a596e6784` |
| `rust/rec-hyrec-vigilode/Cargo.lock` | `c2a43007f2eeaea4005a912d1b8447ece43fa793986c4672fca427aaf9e73dc8` |
| `rust/rec-hyrec-vigilode/build.rs` | `d8c8dca1ff53e0c8bdf8fb4ba80a97beb626ca8931e4fe76450fdf3e6607f2fc` |
| `rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json` | `4adfdeee1ae236725f8a654072498649c89f8e5b2e33f88eb6f40080ffbcb19d` |
| `rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.sha256` | `dce777930232a218f7fb8f2ff4c4f79abd2e1483367e8f1da77d11644c3c936c` |
| `scripts/c_harness/original_hyrec_r3o_rust_bridge.c` | `be0a49760ba35946304261d727b2e4dbc673efdc0d979b2512950ccdeba1dfdc` |
| `scripts/build_r3o_rust.py` | `3e3f0ae3cb19fb49c8b47eac2896850b33abe5eaa70687b1f40eb15080d79743` |
| `scripts/verify_r3o_rust.py` | `4877bf538184d06143d45a2a5bef051130a198d25760a7b0c68498814c731055` |
| `tests/trajectory/test_r3o_rust.py` | `ccb1084ed6d42ac1d30efbda2fa3c9602f0cf1a7e23f449eaaedf5b496142bc9` |

Additional initial read source/evidence identities (historical snapshot; final
identities follow separately):

| File | SHA256 |
|---|---|
| `rust/VIGILODE_SOURCE.json` | `b555ebb6ed562c20743b49bf6cfbf4ce70d54dd03af9666c96e519828f65ec1d` |
| `research/rec_r3o_grid_frontiers_20261019/VIGILODE_REUSE_KO.md` | `dcb03b2c78b506812ff4952021eb3968725b6446cedb9f75e9639dd7fd063919` |
| `research/rec_r3o_grid_frontiers_20261019/review/RUST_BOUNDARY_PARENT_READBACK.json` | `e852bb047d971136564b67eb3e78e73c3e2ed81092e8235903297ae33439dd8f` |
| `.github/workflows/verify-r3o-rust.yml` | `e5faf45e85201cf91691411daa920b333f43b3f64f600226d18a971133a6c337` |

## Final reviewed source snapshot

These hashes identify the final local source snapshot read for this review.
They do not assert that every file was compiled by the retained build_002.
The retained packet JSON and seal hashes remain those in the previous table.
The current workflow was read: it invokes the default source build, the sealed
packet's 16-step verifier, and always preserves failure/success artifacts.
Its existence is not evidence that the corrected compile has passed.

| File | Final source SHA256 |
|---|---|
| `rust/rec-hyrec-vigilode/src/contracts.rs` | `0dd78bdf46dbd59381280722d9d51a6120f9d7e554a5ff53f9606d0fc8859fb0` |
| `rust/rec-hyrec-vigilode/src/ffi.rs` | `4b561962b23f90cacaee11ba92180b3adefbe630e672a8a1c53febfbf0a0c501` |
| `rust/rec-hyrec-vigilode/src/fixed.rs` | `615f75ab44030fcde9858401b75e8696f337b39d599f0fb7c94d3db94d1a6d33` |
| `rust/rec-hyrec-vigilode/src/diagnostic.rs` | `a010601acc09a677e65ec710fc9f13ef3de3f236604364b35dc36b316d7c4d8d` |
| `rust/rec-hyrec-vigilode/src/main.rs` | `cb6869b061187ebdd46a5126318e8333baa63b16cca5509748c1effb47deea20` |
| `rust/rec-hyrec-vigilode/Cargo.toml` | `0f57838424190cde64c227afb682c30a46d167bf855186973e1a9911e0e5d45d` |
| `rust/rec-hyrec-vigilode/Cargo.lock` | `c2a43007f2eeaea4005a912d1b8447ece43fa793986c4672fca427aaf9e73dc8` |
| `rust/rec-hyrec-vigilode/build.rs` | `ddf77de8189e45dbd458eb1167c3417f55dddd84e975e581d13421154c299450` |
| `scripts/c_harness/original_hyrec_r3o_rust_bridge.c` | `4f4365b926049bbcc1c0c27b61388655e806f9a63b603a32b19538664571e36d` |
| `scripts/build_r3o_rust.py` | `d33f4761482720cd822a3006460e9462091c9219180541e78cdc51a4ca35cfd5` |
| `scripts/verify_r3o_rust.py` | `e99dbc6e022eab3301c6f4db8ee3cd5bd2e27a53eeeba2872a84a03e6d646a26` |
| `tests/trajectory/test_r3o_rust.py` | `51c6ec10867eb1865dcdb0654e5a8dc65ff5e9877f62028219d69435f71c4016` |
| `rust/VIGILODE_SOURCE.json` | `d05094bd55820f3d86cb7e00d0012d060b3834da5fb8fb47c3f2c9dc30ff18fc` |
| `.github/workflows/verify-r3o-rust.yml` | `d69cb577e279e754c43856d1a7799080aceb2906a31e12040b2ee02259e78395` |
| `research/rec_r3o_grid_frontiers_20261019/VIGILODE_REUSE_KO.md` | `c79afe91a226ba29b647b6b6587c662b9d26f755eecb6e52aeccefe967eafc3b` |

## Disposition returned to the parent

| Scope | Review disposition |
|---|---|
| C9 source review and targeted corrective controls | COMPLETE; three P2 findings CLOSED |
| Retained local fixed 16-step comparison | PASS within the actual build_002 / verify_001 seals |
| Retained exploratory nonautonomous RODAS / faer probes | Diagnostic completion reviewed; not same-algorithm or production admission |
| Original failed fresh-Cargo package | Actual compile FAIL retained, numerics NOT_RUN |
| Corrected upstream build-script package | Source omission repaired and hashes matched; fresh compile PENDING, parent-owned |
| One-step verifier CLI | P3, nonblocking for the required 16-step path; exact correction above |
| Publication, backup receipts and DAG mutation | Parent-owned; reviewer wrote only C9_RUST.md |

For accounting clarity, the retained build_002 reports 21.535843 CPU seconds /
21.78155451299972 wall seconds; verify_001 reports 2.395937 CPU seconds /
2.558933634994901 wall seconds. These are prior actual sandbox executions,
separate from this review's controls and from GitHub CI. Old live-RSS defects
are disclosed above, so those receipts are not used as reliable peak-memory
measurements. No speed comparison is admitted.
