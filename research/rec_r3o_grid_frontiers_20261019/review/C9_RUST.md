# R3O independent C9 review — VigilODE/Rust extension

Review date: 2026-10-19 UTC. Selected stage: C9 only. Status at this checkpoint:
**RETAINED_NUMERICAL_EVIDENCE_REVIEWED; RESOURCE_AND_LOCK_REPAIRS_OPEN.**
This is a bounded source/evidence review of the new Rust caller and its launchers.
The reviewer changed only this report, performed no native build or new physical
integration, and dispatched no recursive agents. Final launcher identities and any
replacement build/run receipts remain to be checked after the implementer freezes
the repair. The existing core R6/C9 review and parent full-raw packet readback are
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

### C9-RUST-P2-01 — finalization can retain PASS after its resource allowance

**Relevance: FIX_SOON before sealing final launcher resource claims.** The small
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

### C9-RUST-P2-02 — unavailable descendant telemetry is silently recorded as zero

**Relevance: FIX_SOON for accurate sandbox resource evidence.**

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

### C9-RUST-P2-03 — committed lockfile is regenerated before the code seal

**Origin: independently identified by the parent and confirmed in this source
review; one shared finding, not a second review demand. Relevance: FIX_SOON.**

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

### Closed source finding — default NCP/CI route required an unprovided registry

The initial source SHA256
`c35ce026d05f04d3d55c6989a6e12beb60afa57c8df39597b0d6359b1218381c`
required `--registry-vendor` or `REC_CARGO_VENDOR` for every build. The parent CI
uses `python scripts/build_r3o_rust.py --output r3o-ci/build` without either.
The revised `3e3f0ae...` source allows the ordinary Cargo route with no vendor
argument and reserves mandatory offline registry input for explicit dependency
reuse. This source-level incompatibility is closed. Actual fresh Cargo CI remains
a separate execution receipt, not a conclusion drawn from this code inspection.

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

The reviewer checked the SHA256 of
`rust/vendor/vigilode-a21d573-three-crates.tar.gz`
(`f36c451b9e80b529b1de989988a96561db830694bcfdb107fe47035151a8c8ba`),
its 123 packaged members, and all materialized member hashes against
`rust/VIGILODE_SOURCE.json`. The 122 selected upstream files are preserved;
the additional original root manifest and documented workspace member removal
are packaging changes. The parent's remote Git blob verification is reused,
not claimed as a new remote retrieval by this reviewer. Original history.c,
hydrogen.c, helium.c and hyrectools.c in the build directory independently match
the authoritative ZIP bytes. The reviewed h2 header-only change is reused.

The retained build explicitly recompiles the C bridge and new Rust caller while
reusing read-only libraries compiled at `8a8bd409b1d96c7b7421f496d229e119fd3d284e`.
It records the selected source relationship to
`a21d573980f66fe02891bd216153443b5352f921`, a coherent graph of 163 dependency
edges, and unchanged before/after dependency hashes. This is not a fresh compile
of every a21d573 library. Default Cargo source compilation is a separate route
whose new CI receipt is pending.

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

The three new reviewer control processes consumed 0.07203965 CPU seconds;
0.042374129 parent + 0.019444 reaped-child CPU seconds; and 0.129328402 CPU
seconds respectively. Aggregate reported CPU: 0.263186181 seconds. The actual
new computations are two synthetic finalizer controls, one live telemetry
control, retained-evidence arithmetic/hash checks, and four in-memory rejection
controls. There were zero new native builds and zero new physical history steps.

Skill context actually read: physmath-research-loop 1.3.0 `SKILL.md`,
`references/CODING_LOOP.md` C9, `references/SUBAGENT_MODE.md`, and
`references/POLICY_INTEGRATION.md`, under the exact user-supplied plugin directory.
The permitted sole write is this report. The current callable inventory did not
expose an agent-message tool; actionable findings were returned through the
shared commentary and this report, without inventing send receipts.

The final review will close source findings against the implementer's corrected
file hashes and scope-matched receipts. It will not request a repeat of the
already reviewed core scientific campaign. Full h2 low-z, full h4, global
convergence and speedup remain unexecuted here; existing U5 holds and REI=false
are inherited unchanged.

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

Additional read source/evidence identities:

| File | SHA256 |
|---|---|
| `rust/VIGILODE_SOURCE.json` | `b555ebb6ed562c20743b49bf6cfbf4ce70d54dd03af9666c96e519828f65ec1d` |
| `research/rec_r3o_grid_frontiers_20261019/VIGILODE_REUSE_KO.md` | `dcb03b2c78b506812ff4952021eb3968725b6446cedb9f75e9639dd7fd063919` |
| `research/rec_r3o_grid_frontiers_20261019/review/RUST_BOUNDARY_PARENT_READBACK.json` | `e852bb047d971136564b67eb3e78e73c3e2ed81092e8235903297ae33439dd8f` |
| `.github/workflows/verify-r3o-rust.yml` | `e5faf45e85201cf91691411daa920b333f43b3f64f600226d18a971133a6c337` |
