# REC scalar prefix audit

This independent Rust 2021 `cdylib` audits at most 64 consecutive columns of
the native `PV`/`PL` CSV prefix. Its reference is the prefix branch of
`scripts/verify_r3i_h2_u6_rt_boundary.py::compare_native_stream`, at REC base
`368d87ad5de90dde74226ed109c3ba29d9607c84` (lines 213–229).

The C ABI is in [include/rec_stream_audit.h](include/rec_stream_audit.h).
The shared-library basename is `librec_stream_audit.so` on Linux. There is no
Python binding, physical ODE code, C physics workspace, or integration benchmark
in this crate. Python retains stream-stage checks, the guard cadence, history
assembly, accepted-step audit, forensic diagnostics, and scalar Tr computation.

## Build and inspect

Use the restored official Rust **1.94.1**, edition **2021**. The only direct
dependency is **`rayon = "=1.12.0"`**. Cargo.lock pins all six registry packages;
it was generated once. Builds and tests must use `--locked`; do not regenerate
the lockfile as part of preflight. License texts and metadata are preserved in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and `licenses/`.

From the REC repository root:

```sh
export CARGO_HOME=/workspace/scratch/afe554957b2e/cargo_r3p
export CARGO_TARGET_DIR=/tmp/rec_r3p_rust_impl_target
export RUSTC=/workspace/scratch/afe554957b2e/rust194/bin/rustc
export RUSTDOC=/workspace/scratch/afe554957b2e/rust194/bin/rustdoc
/workspace/scratch/afe554957b2e/rust194/bin/cargo test \
  --locked --offline --lib --manifest-path rust/rec-stream-audit/Cargo.toml
/workspace/scratch/afe554957b2e/rust194/bin/cargo test \
  --release --locked --offline --lib --manifest-path rust/rec-stream-audit/Cargo.toml
/workspace/scratch/afe554957b2e/rust194/bin/cargo build \
  --release --locked --offline --manifest-path rust/rec-stream-audit/Cargo.toml
cc -std=c11 -Wall -Wextra -Werror -ffp-contract=off \
  -Irust/rec-stream-audit/include rust/rec-stream-audit/tests/abi_smoke.c \
  -L"$CARGO_TARGET_DIR/release" -Wl,-rpath,"$CARGO_TARGET_DIR/release" \
  -lrec_stream_audit -lm -o "$CARGO_TARGET_DIR/abi_smoke"
"$CARGO_TARGET_DIR/abi_smoke"
```

Emit artifacts for compiler inspection, using the same environment:

```sh
/workspace/scratch/afe554957b2e/rust194/bin/cargo rustc \
  --release --locked --offline --lib \
  --manifest-path rust/rec-stream-audit/Cargo.toml -- --emit=llvm-ir,asm,link
```

`release/deps/rec_stream_audit.{ll,s}` (or Cargo's hash-suffixed equivalents)
contains `ratio_kernel`; `release/librec_stream_audit.so` is the ABI artifact.
The independent per-lane loop is intended for LLVM auto-vectorization. Any
SIMD or speed claim requires inspection/measurement of the actual build used
by the parent. The source and unit tests alone do not establish either.

The release profile keeps `panic="unwind"`, disables LTO, and uses ordinary
Rust binary64 operations. Compiling this crate with `panic="abort"` is rejected.
Do not supply fast-math, reassociation, reciprocal-approximation, or contraction
flags, or substitute a vector/approximate exponential. Use the same system
libm and default floating-point environment as the Python reference: round to
nearest, ties to even, with gradual underflow, no FTZ/DAZ. Keep that environment
unchanged at handle creation and during calls, including on the caller thread.

## ABI and ownership

```c
void *rec_prefix_new(size_t threads);
void rec_prefix_free(void *handle);
int rec_prefix_audit(
    void *handle,
    const uint8_t *text, size_t text_len,
    size_t start_col, size_t columns,
    const double *py_values, size_t py_len,
    const double *tr, size_t tr_len,
    const double *energies, size_t energies_len,
    double *native_values, size_t native_len,
    RecStatus *out);
int rec_ratio_batch(size_t n, const double *py, const double *c,
                    const double *fbb, double *out);
```

`RecStatus` is Rust `#[repr(C)]`, in this order, with normal C padding:

```c
typedef struct RecStatus {
    int32_t code;
    size_t row;
    int32_t detail;
    size_t processed_rows;
} RecStatus;
```

On the tested Linux x86-64 ABI, its size is 32 bytes, alignment 8, and field
offsets are 0, 8, 16, 24. Bind fields with `int32_t`/`size_t` equivalents and
native alignment; do not pack the struct.

`rec_prefix_new` accepts 1..4 threads. It returns NULL for an invalid count,
thread-pool construction failure, or caught panic. With one thread, it creates
no Rayon pool and directly runs a serial loop. With 2..4 threads, the handle
owns a reusable local pool with an explicit thread count. No global pool is
initialized. `rec_prefix_free(NULL)` does nothing; otherwise free a handle
exactly once, in the same library instance, after all calls using it complete.

Every audit pointer must be non-NULL, even the text pointer for `text_len=0`.
The caller must provide live storage of the declared extent, initialized and
immutable input elements, correctly aligned numeric arrays/status, and writable
output/status. Output arrays may start uninitialized. This implementation uses
`MaybeUninit<f64>` for them until a value has been written.

`native_values` and `out` must not overlap each other, any input, or the handle.
The input buffers may overlap each other, but cannot overlap the handle. The
ABI checks numeric address ranges and overlap before creating any slices.
It cannot prove that a non-NULL address denotes accessible allocated storage
or that an opaque handle is genuine/live; those remain caller obligations.
Never mutate an input, share a writable output between in-flight calls, unload
the library, or free the handle while it is in use. Independent calls can share
a live immutable handle and distinct buffers; serialize calls if a single
caller-level work/memory budget is required. Buffers are borrowed only until
the call returns. No pointer into caller storage is retained in the handle.

`rec_prefix_audit` returns `out->code` after writing the whole status, except
when `out` itself has invalid pointer metadata or a buffer overlap is detected:
those return the error code without writing status. Argument errors occur
before any input data or handle contents are read. On a record failure, output
contains a mixture of checked and untouched slots. **Discard the entire failed
block**, including speculatively populated later columns.

Rust unwinds are caught at every C entry point, including Rayon job panics
propagated through `install`. The library does not install a process-global
panic hook. A panic returns code 90, with unknown work count. Invalid foreign
addresses, double free, allocator abort, stack overflow, and process termination
are outside Rust unwind recovery; the pointer and lifetime contract still
applies. C/Rust allocation and OS thread overhead are not per-record resources.

## Shapes, CSV grammar, and bounds

| Argument | Required extent/condition |
| --- | --- |
| `columns` | 1..64 |
| `start_col` | `start_col + columns - 1` must fit `size_t` |
| `text_len` | At most 4,194,304 bytes; exactly `columns*314` records |
| `py_len`, `native_len` | Exactly `columns*314`, at most 20,096 |
| `tr_len` | Exactly `columns` |
| `energies_len` | Exactly 314 |

Both value arrays use contiguous row-major `[columns][314]` layout. A column
contains virtual bins 0..310, then Lyman bins 0..2. `energies` has the 311
virtual energies followed by the three Lyman energies. `tr[col]` is one
precomputed scalar per local column. Python must compute it with the original
association `KB_EV_K*c.T0_K*(1.+c.redshift(RT_IZ+global_col))`, not a reassociated
array operation. No temperature or energy conversion is done by this crate.

Records have exactly four comma-separated fields, with exact untrimmed tags
`PV` or `PL`. There is no CSV quoting/escaping. Tags, global column indices,
and bin indices must match the expected position. Integers use ASCII grammar
`[+]?[0-9]+` after Rust `str::trim`, with checked `size_t` accumulation. Leading
zeros are accepted. Signs `-`, underscores, exponents, Unicode digits, empty
indices, and overflow are rejected. Floats use `str::parse::<f64>()` after
`str::trim`; accepted values must be finite. An overflowing literal, NaN, or
infinity fails. UTF-8 is validated per record, so a later encoding error cannot
hide an earlier numerical/order error.

LF separates records. CRLF works because the trailing CR is trimmed from the
numeric field. A final record can omit its newline. An interior empty line or
extra trailing blank line is an error. An ending LF is a terminator, not an
extra empty record. Bare CR separators are outside the native-stream grammar.
The input is length-delimited; no NUL terminator is read. A NUL inside a numeric
field is invalid.

Line indexing borrows text and uses at most 20,096 `Option<&[u8]>` slots:
321,536 bytes on the tested 64-bit target. At most 64 small column outcomes
add a few KiB. Per-block library heap scratch is below 0.4 MiB; caller buffers
are excluded from that figure. Each pool worker requests a 256 KiB stack,
so one four-worker handle requests 1 MiB of worker stacks, plus bounded Rayon,
allocator, thread-local, and OS overhead. Pools are reused across calls. The
4 MiB text cap also bounds parser work for adversarially long numeric fields.

## Scalar arithmetic and failure order

For each record, the implementation checks field count, integer grammar,
tag/column/bin order, native float syntax and finiteness, Python finiteness,
positive finite Tr, and positive finite energy. Parsed finite native output is
stored before the numerical gate, just as the reference stores its native
history before parity. It then evaluates these separate binary64 operations:

```text
argument = energy / tr
denominator = system libm expm1(argument)
fbb = 1.0 / denominator
relative = 1.0e-7 * max(abs(py), abs(native))
floor = 1.0e-10 * fbb
tol = relative + floor
fail iff abs(py - native) > tol
```

`expm1` is an external C symbol linked to `libm` on Linux. There is no `mul_add`,
fast-math, vector exponential, horizontal floating-point reduction, or ratio
substitution in the prefix gate. Python and native values, Tr and energies are
validated explicitly; tolerance must be finite. Equality passes even when
`tol==0`. A nonfinite difference from finite opposite large values exceeds a
finite tolerance and therefore fails the original comparison.

Python `math.expm1` raises on finite-argument overflow, and `1./0.` raises on a
denominator rounded to zero. Code 22 preserves those failures instead of silently
turning finite-argument overflow into an accepted zero blackbody floor. If
`energy/tr` itself is positive infinity, Python `math.expm1(inf)` returns infinity;
`fbb=0` is permitted in that case. A finite denominator whose reciprocal
overflows is rejected by the finite-tolerance check.

Every column job validates its rows in order and stops at its own first failure.
For 2..4 threads, indexed `par_chunks`, zipped disjoint output chunks, and an
indexed `collect` produce ordered column outcomes. After every job has joined,
a serial scan selects the first failure. One-thread execution also processes
all columns and performs the same final scan. No parallel short circuit or
shared failure variable participates in error selection. Missing/extra row
errors participate in the same ordering, after all earlier available records.

`row` is the zero-based failing position within the block. For an extra record
it equals `columns*314`; for an absent record it is the first missing position.
On success, argument errors, or panic it is `SIZE_MAX`.

`processed_rows` counts **present expected-position records whose validation
started** across all column jobs. It includes the first failing record of each
column and all work in later columns. It excludes rows after a column's first
failure, missing rows, and extra rows. On success it equals `columns*314`; on
argument errors it is zero. On panic it is `SIZE_MAX` because interrupted work
is unknown. This is deterministic across 1/2/4 threads on nonpanicking input.

## Error codes

| Code | Name suffix | Meaning / `detail` |
| --- | --- | --- |
| 0 | `OK` | Success; detail 0 |
| 1 | `NULL` | NULL pointer; argument identifier |
| 2 | `LENGTH` | Wrong length, extent overflow, or unrepresentable range; argument identifier |
| 3 | `LIMIT` | Columns/text cap or global-column overflow; argument identifier |
| 4 | `ALIGNMENT` | Misaligned typed pointer; argument identifier |
| 5 | `OVERLAP` | Forbidden overlap; return code only, status not written |
| 10 | `FIELDS` | Record does not contain exactly four fields; detail 0 |
| 11 | `INTEGER` | Invalid/overflowing index; detail 2 column, 3 bin |
| 12 | `ORDER` | Unexpected tag/index; detail 1 tag, 2 column, 3 bin |
| 13 | `FLOAT` | Native float parse failure; detail 4 |
| 14 | `NATIVE_NONFINITE` | Native NaN/infinity; detail 4 |
| 15 | `PY_NONFINITE` | Python NaN/infinity; detail 0 |
| 16 | `TR` | Tr is nonpositive/nonfinite; detail 0 |
| 17 | `ENERGY` | Energy is nonpositive/nonfinite; detail 0 |
| 18 | `TOLERANCE` | Tolerance is nonfinite; detail 0 |
| 19 | `PARITY` | Original strict `absdiff > tol` gate fails; detail 0 |
| 20 | `ROWS` | Missing record: detail -1; extra record: detail +1 |
| 21 | `UTF8` | Invalid UTF-8 in this record; detail 0 |
| 22 | `BLACKBODY` | Finite-argument expm1 overflow: detail 1; zero denominator: detail 2 |
| 30 | `FBB` | Batch input fbb is negative/nonfinite; batch returns only a code |
| 31 | `RATIO` | Batch output ratio is nonfinite; batch returns only a code |
| 90 | `PANIC` | Caught Rust unwind; detail 0; work count unknown |

Argument identifiers: handle 1, text 2, columns 3, start_col 4, Python values 5,
Tr 6, energies 7, native output 8, status 9, batch n 10, batch fbb 11, batch c 12,
batch output 13. Codes 30/31 occur only in `rec_ratio_batch`.

## Batch ratio kernel

`rec_ratio_batch` accepts `0 <= n <= 20096` independent lanes. `n==0` succeeds
without inspecting pointers, including NULL. Otherwise inputs must be finite,
`fbb>=0`, and the output must be disjoint from inputs. First it validates all
inputs; then a pure per-lane loop computes `abs(py-c)/tol` with the same ordered
tolerance operations; finally it checks every output ratio for finiteness.
All lanes are initialized before the output scan. There is no reduction or
parallel pool in this kernel, and finite ratios greater than one are successful
outputs. A zero/zero ratio, subtraction overflow, or ratio overflow returns 31.
As with the prefix audit, discard output on any failure. No lane index is
returned by this smaller ABI. Input validation precedes output validation.

## Verification scope

Native tests cover full 64-column blocks and exact parsed bits, local-pool reuse,
1/2/4-thread first-error and attempted-work agreement, PV/PL transitions, missing
and extra rows, UTF-8, malformed fields, integer overflow, numeric whitespace,
NaN/infinity, Tr/energy positivity, zero and nonfinite tolerance, finite expm1
overflow, exact/next-ULP tolerance boundaries, pointer metadata and overlaps,
batch/scalar bit agreement, and containment of local/worker/payload panics.

The boundary constant and three one-ULP FMA counterexamples in `src/tests.rs`
were derived independently with Python 3.12.14 and Linux `math`/`libm` during
implementation. The frozen scalar auditor remains the parent's integration
reference. Native unit tests establish the bounded implementation contract;
the parent's saved-stream differential and performance runs supply integration
and resource evidence for the complete adapter.
