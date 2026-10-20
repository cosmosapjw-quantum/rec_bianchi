# REC R3P Rust prefix audit handoff

## Binding contract available

- Crate: `/workspace/scratch/afe554957b2e/rec_work/rust/rec-stream-audit`.
- Header: `include/rec_stream_audit.h`; library basename `librec_stream_audit.so`.
- `rec_prefix_new(size_t threads) -> void*`, threads 1..4; `rec_prefix_free(void*)`.
- `rec_prefix_audit` has the exact requested argument order. `RecStatus` is
  `{ int32_t code; size_t row; int32_t detail; size_t processed_rows; }` with C
  alignment/padding. Return code equals `status.code` unless status cannot safely
  be written (invalid status pointer or detected buffer overlap).
- `rec_ratio_batch(size_t n, const double* py, const double* c,
  const double* fbb, double* out) -> int` is included, with n <= 20096.
- Arrays have exact audit lengths: `columns*314`, `columns`, `314`,
  `columns*314`; columns 1..64. Text cap: 4 MiB. LF/CRLF and final unterminated
  record are supported. Python owns original scalar-associated Tr computation.
- Success/no record uses `row=SIZE_MAX`. A failing row is zero-based within the
  block. `processed_rows` counts present records actually entered by all column
  jobs, including failing and speculative later-column records. Panic uses
  `processed_rows=SIZE_MAX` (unknown). Ignore output arrays on any failure.
- Numeric error codes and pointer/alias obligations are fixed in the header.

## State: implementation complete, local validation passed

Restored tools used:
`rustc 1.94.1 (e408947bf 2026-03-25)` and
`cargo 1.94.1 (29ea6fb6a 2026-03-24)`.

The initial sandboxed registry request hit an unreachable proxy. The approved
unsandboxed Cargo retry generated Cargo.lock once; dependencies are now cached
under the requested CARGO_HOME. Subsequent builds use --locked --offline.
Resolved Rayon 1.12.0, rayon-core 1.13.0, either 1.19.0, crossbeam-deque 0.8.8,
crossbeam-epoch 0.9.21, crossbeam-utils 0.8.23. No toolchain was downloaded.

### Actual validation

All commands use the user-requested CARGO_HOME and
`CARGO_TARGET_DIR=/tmp/rec_r3p_rust_impl_target`. Reproduction commands are in
the crate README, including the C compiler invocation.

| Check | Result |
| --- | --- |
| `cargo test --locked --offline --lib` | PASS: 18/18 native tests, debug profile |
| `cargo test --release --locked --offline --lib` | PASS: 18/18 native tests, optimized profile |
| `cargo rustc --release --locked --offline --lib -- --emit=llvm-ir,asm,link` | PASS: cdylib, rlib, LLVM IR, assembly emitted |
| `tests/abi_smoke.c`, compiled with C11 and `-Wall -Wextra -Werror -ffp-contract=off` | PASS: C struct layout, real exports, native parsed bits, 1/2/4-thread parity/work counts, batch ratios |
| `nm -D --defined-only` | Exactly four public C symbols: new/free/audit/ratio_batch |
| `readelf -d` | Explicit `libm.so.6` dependency |
| LLVM/assembly inspection of `ratio_kernel` | `<2 x double>` arithmetic; `subpd/mulpd/addpd/divpd` plus scalar tail; no fast/reassoc/contract/afn/arcp flags or fused operation in this kernel |
| Whitespace check across all 21 owned crate files | PASS |
| Upstream license byte comparison | PASS: 12/12 MIT/Apache files unchanged |

The kernel observation is scoped to this default x86-64 optimized build. Parent
should inspect its own final build artifacts. No speedup or production resource
measurement is claimed. The independent C smoke test complements Rust tests;
no separate reviewer agent was available in this delegated runtime.

One initial compilation exposed invalid Rust float-literal spelling (`1.e-7`);
corrected to `1.0e-7`/`1.0e-10` without changing binary64 constants or association.
Both debug and release tests passed after that correction. The initial
whitespace wrapper misclassified git's normal no-index exit 1 as an error;
checking diagnostics correctly confirmed no whitespace findings.

### Artifacts available now

- Library: `/tmp/rec_r3p_rust_impl_target/release/librec_stream_audit.so`.
- LLVM IR: `/tmp/rec_r3p_rust_impl_target/release/deps/rec_stream_audit.ll`.
- Assembly: `/tmp/rec_r3p_rust_impl_target/release/deps/rec_stream_audit.s`.
- C smoke executable: `/tmp/rec_r3p_rust_impl_target/abi_smoke`.
- Cargo.lock SHA-256:
  `7af2db0a742c71381057459b36e1ba711d907003012ab122ba5eb05a2c7fb052`.
- Built cdylib SHA-256:
  `567ec4b4a2ff1009f38a51970632804e04867094579b0c967ddfa31f5195103a`.

### Binding details worth preserving

- Metadata checks happen before any input or handle read. An invalid status
  pointer or detected overlap returns a code without writing the status struct.
- Inputs are immutable during the call; output and status cannot alias inputs,
  each other, or the handle. Output arrays may be uninitialized initially.
- Per-record checks select the earliest failing record after joining every
  column job. One-thread mode also visits every column, making attempted work
  counts identical across thread counts on nonpanicking input.
- Per-block indexing scratch is below 0.4 MiB on x86-64; input/output buffers
  are borrowed. Reused pools request 256 KiB per worker stack, plus runtime/OS
  overhead; this is an allocation bound, not a measured process RSS claim.
- Code 22 preserves Python exceptions for finite-argument `expm1` overflow
  (detail 1) or a denominator rounded to zero (detail 2). Infinite quotient
  `energy/tr` itself permits `fbb=0`, matching `math.expm1(inf)`. Code 18 rejects
  nonfinite tolerance. The prefix gate uses `absdiff > tol`, including a passing
  zero/zero-difference case; it never substitutes the ratio kernel.
- The batch kernel returns finite ratios above 1 normally; code 31 rejects
  NaN/infinite ratios, including `0/0`. It does not return a row index.
- Actual C layout on x86-64: size 32, alignment 8, field offsets 0/8/16/24.

### Coding-loop completion and remaining parent work

C1/C2 reuse the frozen prefix branch and explicit block ABI. C3 preserves scalar
binary64 association and system libm. C4 bounds rows/text/threads/scratch and
isolates the build target. C5 implements parser, pool, FFI, and batch kernel.
C6 passes native/ABI contract checks. C7 checks the original numerical predicate
and Python exception boundaries; physical evolution is outside this adapter.
C8 records pinned versions, lock/build identity, commands, and scoped compiler
evidence. C9 includes independent Python-derived tolerance/FMA vectors and the
C ABI test. C10 hands these artifacts to the parent.

The parent retains Python binding/build integration, original scalar-associated
Tr generation, real saved-stream differential checks, guard/counter integration,
benchmarking and compiler-evidence review. The scalar-cache agent's script and
tests were observed in git status and were not edited. No tracked file outside
the owned crate was modified, and this agent did not commit or push. The checked
HEAD remained `368d87ad5de90dde74226ed109c3ba29d9607c84`.

## Authority and scope

Base: `368d87ad5de90dde74226ed109c3ba29d9607c84`.
Read the requested `physmath-research-loop` SKILL.md plus RESEARCH_POLICY,
CODING_LOOP, EVIDENCE_AND_HANDOFF, RUNTIME_AND_LEGACY; read repository
`docs/REPO_CHECK_PATCH_POLICY.md` and the R3P POLICY_DECISIONS. The explicit
delegation confines edits to this crate and this note and forbids commits/push.
Therefore stage-wide remote-check state writes, ledger edits, bundle creation,
commit/push and Python integration remain with the parent. No physics or
production-performance claim is introduced by this audit adapter.
