# Bounded R3O Rust / VigilODE caller

This independent package contains two distinct numerical lanes. It preserves
`h2=4.245e-5`, source indices `58389..211716`, the frozen original cosmology,
the original Oct-2012 source ZIP and the previous U5 hold statuses. It advances
16 steps by default, never a full 153327-step trajectory. REI remains false.

## Fixed-h2 owner and scientific mapping

The accepted state is `(xe, Tm_K, Hprev, Hprev2, Tprev, Tprev2)`. At the input
index, the original outer temperature guard selects EMLA2s2p or the absorbing
Peebles stage. Rust calls the original C atomic and thermal operators and applies

```
xe_new = xe + h2 * (1.25 * Hnow - 0.25 * Hprev2)
Tm_new = Tm + h2 * (1.25 * Tnow - 0.25 * Tprev2)
(Hprev, Hprev2, Tprev, Tprev2)_new = (Hnow, Hprev, Tnow, Tprev)
```

`scripts/c_harness/original_hyrec_r3o_rust_bridge.c` source-includes the existing
low-z harness. An independent copy of the same C initial state is advanced by
the original `rec_get_xe_next2_HTm`, whose own post-RT switch selects EMLA. Every
accepted state and all four predictor memories must agree bit for bit with
Rust. The C oracle is never reseeded with a Rust result. Python starts from its
separate reviewed state and is advanced with the existing frozen Python code.

The Python state residuals are `|py-c|/max(|c|, floor)`, with floors `1e-8` for
xe and `1 K` for Tm, and limits `5e-9`, `5e-10`. Each memory has limit `2e-8`
after scaling by `max(1, |c|)`. Common-input hydrogen RHS uses
`max(|py|, |c|, 1e-13)` and limit `3e-10`; thermal RHS uses `max(1, |c|)` and
limit `2e-10`. These gates remain separate from VigilODE's error controller.
The source recurrence has its original discretization/truncation error;
bit agreement checks implementation and floating-point ordering at the same h.

## Actual VigilODE diagnostic

The second lane calls `integrate_rodas5p_fast_observed` from the pinned upstream
core/krylov/integrators libraries. Its classification is
`EXPLORATORY_METHOD_COMPARISON`. It solves the original C EMLA continuous RHS in
`tau=ln(a/a_U6)`, with `u=[xe/xe_U6, Tm/Tm_U6]`. The constant normalizers imply
`du_i/dtau=F_i(tau,S*u)/S_i` and `J_u[i,j]=(S_j/S_i) J_y[i,j]`.

The problem is explicitly **nonautonomous**. Its centered finite-difference
Jacobian uses `cbrt(machine epsilon)*max(1,|u_j|)`. Its explicit partial time
derivative holds the state fixed, uses a `1e-7` log(a) displacement, and switches
to second-order one-sided differences at the two span boundaries. Every source
sample must stay in the EMLA physical domain. FULL and cross-stage source calls
are absent from this continuous wrapper. The FastSmall driver is not used.

The solver receives the explicit requested times `i*h2`, including both ends.
The fast driver's direct output collector is used; no dense interpolation is
requested. Maximum attempts is 32 and therefore accepted internal steps cannot
exceed 32. Normalized tolerances are `atol=1e-12`, `rtol=1e-9`; the output also
records the corresponding physical absolute tolerances `S_i*atol`. Comparisons
with the fixed-h2 trajectory are descriptive and have no admission threshold.
Finite-difference, adaptive integration and roundoff errors are additional to
the common physical closure; this is a different algorithm from the fixed loop.

The initial continuous and fixed-input C RHS values must agree bit for bit.
The thermal Jacobian is checked against the source formula
`F_T=A*Tr-(2+A)*Tm`, away from its near-equality branch. VigilODE `DenseMatrix`
and its faer-backed `LuFactorization` solve `(I-h2*J_u)x=F_u`; both a linear
residual and an analytic 2x2 solve are checked. `CoreError`, `WorkCounters`,
`error_scale`, and `wrms` are used in the actual error and comparison paths.
[faer 0.24.4 documentation](https://docs.rs/faer/0.24.4/faer/) describes a
medium/large matrix focus. This small residual check makes no 2x2 speed claim.

## Source and state provenance

The parent-owned `rust/VIGILODE_SOURCE.json` pins commit
`a21d573980f66fe02891bd216153443b5352f921` and authenticates the compressed
three-library source archive. The build script validates the archive SHA256
and exact member hashes before materializing an absent vendor directory.
Unchanged original source `.c` files are extracted into a new build directory;
only the isolated `hyrec_params.h` changes DLNA to `(8.49e-5/2.)`.

`fixtures/r3m_u6_boundary.json` is a **derived boundary packet**, not the full
NPZ, CSV, or verification producer artifacts. It preserves independent native
and Python six-scalar states, exact binary64 encodings, grid/cosmology/source
pins, original full-input hashes, the prior review attribution, and the reader
code identity. It contains no photon arrays. Its `.sha256` seal is included in
the build's source/fixture hash set. `serde_json` has `float_roundtrip` enabled.

The exporter and raw readback invoke the existing `load_reviewed_u6_boundary`,
which verifies all full producer hashes and structure. The portable numerical
mode only reads the packet and original source ZIP, and explicitly reports
that it did not reread the full raw artifacts during that numerical pass.

## NCP: source build and bounded run

Run from the repository/capsule root with existing Rust **1.94.1**, Python with
NumPy, and `cc`/`ar`. No compiler installation is attempted. Use a fresh output
directory for every invocation. Build and numerical allocations are separate.

```bash
python -B scripts/build_r3o_rust.py \
  --rust-bin-dir /path/to/rust-1.94.1/bin \
  --output ../rec_recovery/r3o_rust_runs/ncp_build_001

python -B scripts/verify_r3o_rust.py \
  --build ../rec_recovery/r3o_rust_runs/ncp_build_001/build.json \
  --boundary-packet rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json \
  --steps 16 --output ../rec_recovery/r3o_rust_runs/ncp_verify_001
```

The default source build obtains the pinned registry packages through Cargo.
For a prepared offline registry add `--registry-vendor /path/to/vendor` to the
build command. The script creates its own CARGO_HOME and target directory and
uses one Cargo job. It automatically verifies/extracts the published VigilODE
archive and the original HyRec ZIP. It builds only the client and its library
dependencies; upstream integration tests/examples are neither included nor run.
Budget: build at most 240 CPU seconds / 480 wall seconds / 3 GiB; numerics at
most 20 CPU seconds / 60 wall seconds. Insufficient disk or an expired budget
produces a retained failure instead of silently expanding the allocation.

For parent readback against retained raw inputs, with **zero new physical steps**:

```bash
python -B scripts/verify_r3o_rust.py \
  --check-boundary-packet rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json \
  --raw-dir ../rec_raw_verified/full5210_stored \
  --output ../rec_recovery/r3o_rust_runs/packet_readback_001
```

## Constrained sandbox build route

`--reuse-deps /path/to/target/release/deps --reuse-source /path/to/prior/source`
is an explicit alternative to the default source rebuild. It freshly compiles
the C bridge and this caller, then links read-only precompiled dependencies.
It authenticates the selected source/fixture bytes and recursively resolves
Cargo's dependency fingerprint graph for a coherent library set. These upstream
libraries were compiled under V2 commit `8a8bd409b1d96c7b7421f496d229e119fd3d284e`;
their selected source is byte-identical to the requested a21d573 source. They
are **not** relabelled freshly compiled a21d573 libraries. Historical benchmark
times are not used. The specific reuse route explicitly selects LLD, one linker
thread, and LTO optimization level zero because the available rlibs contain
LLVM bitcode. The source Cargo route remains separate.

## Retained outcomes and failure semantics

`build.json` records actual commands, exits, CPU/wall use, hashes, and dependency
provenance. `verification.json`, `primary.json`, `partial.json`, and
`callback_failure.json` retain accepted output states and attempted work.
Expected partial-failure runs return exit 3. The normal CLI uses exit 0 for a
bounded pass and exit 2 for input/build-interface errors. Output files are
create-only. Invalid dimensions, truncated histories, wrong time order,
nonfinite inputs, cap expansion and output overwrite are tested against the
new executable; packet identity contracts are also checked.

The upstream fast API exposes the last committed requested-grid output on
partial failure, not arbitrary unreported internal states. The expected one-step
failure is required to retain the actual accepted output at `tau=h2`. Failed
callback inputs and attempted source work are retained independently and are
not relabelled accepted states. The mutex-serialized unsafe C boundary is
confined to `src/ffi.rs`; no pointers escape synchronous calls.

Full low-z completion, h/h2/h4 convergence, a HyRec speedup, global cosmological
admission, and Bianchi/REI/CMB conclusions remain unrun and unadmitted. Historical
statuses remain `HOLD_9_FAIL`, `HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, REI=false.
