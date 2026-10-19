# R3O bounded Rust / VigilODE implementation handoff

Status at worker freeze, 2026-10-19 UTC: **C3–C7 implementation complete; local bounded numerical verification passed; targeted launcher repairs passed.** Parent reports `C9_RUST.md` is now **C9_COMPLETE**, with all three P2 findings closed. No additional local build or physical campaign is needed. Parent owns the corrected push, fresh Cargo CI and the narrow P3 parser follow-up described below. Provisional publication `44934c47bc06af01a365f346ee19b830b4bda3d6` is distinct from the worker-freeze launcher identities below.

The worker-freeze relation is `rec_recovery/r3o_rust_runs/handoff_001/final_binding.json`, SHA256 `06a12560cf4cc57f211feb37f0a435e0c51365ef616ff2437923436221f3b271`. Status: `SCOPED_BINDING_PASS_FRESH_CARGO_IDENTITY_SEPARATE`. It binds the retained physical execution to unchanged numerical source, six parent EOF-only changes and the actually tested launcher corrections. It does **not** claim that the final complete source snapshot was rebuilt locally. This receipt remains the exact pre-P3 worker identity; the parent records its parser-only follow-up separately.

## Ownership and skill context

Capsule: `/workspace/scratch/afe554957b2e/rec_work`, not Git. Worker writes were limited to the independent Rust package, requested build/verification scripts, new C bridge, new trajectory test, `rec_recovery/r3o_rust_runs/**` and this note. Existing core operators, immutable VigilODE tip, compiler/cache directories, prior dependency target and parent reports were read-only to this worker. Parent made the documented EOF normalization and vendor packaging changes in its integration role.

Applied physmath-research-loop 1.3.0 from `/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/`: `SKILL.md`, `references/CODING_LOOP.md` (actual location), `references/POLICY_INTEGRATION.md`, `references/STAGE_GUIDE_KO.md`, and `references/SUBAGENT_MODE.md`. Selected C3–C7 plus authorized build/handoff. No recursive agents were launched. Parent expanded intake was read from `research/rec_r3o_grid_frontiers_20261019/receipts/EXPANDED_INTAKE.json`.

## 1. Exact fixed-h2 owner loop

Rust owns `(xe, Tm_K, Hprev, Hprev2, Tprev, Tprev2)` and applies exactly:

```text
xe_new = xe + h2 * (1.25 * Hnow - 0.25 * Hprev2)
Tm_new = Tm + h2 * (1.25 * Tnow - 0.25 * Tprev2)
(Hprev, Hprev2, Tprev, Tprev2)_new = (Hnow, Hprev, Tnow, Tprev)
```

The new C bridge source-includes the existing low-z harness, retaining original static rates/cosmology in the same translation unit. It calls the original atomic/thermal functions. The independent native oracle advances its own six-scalar initial state with original `rec_get_xe_next2_HTm`; it is never reseeded with a Rust result. Input-stage selection and absorbing Peebles metadata are retained. Python starts separately from its reviewed Python boundary. Original C members compile with no fast math and `-ffp-contract=off`; only the isolated h2 header is changed.

Actual `verify_001`: 16 advanced states per lane, 17 rows including the initial state, **102 exact six-scalar byte comparisons PASS**, including all four predictor memories. Python state/memory and common-input RHS comparisons passed unchanged gates:

| Quantity | Maximum scaled residual | Existing limit |
|---|---:|---:|
| xe | 7.434376394267938e-14 | 5e-9 |
| Tm | 2.49687949887451e-16 | 5e-10 |
| Hydrogen memories | 6.539907504432563e-16 | 2e-8 |
| Thermal memories | 3.6101122023224644e-14 | 2e-8 |
| Common-input hydrogen RHS | 2.1707559781417694e-14 | 3e-10 |
| Common-input thermal RHS | 3.621030056849089e-14 | 2e-10 |

Terminal iz 58405: `xe=0.001325115601523151`, `Tm_K=1821.2627044735057`, `Hprev=-0.004693585163625916`, `Hprev2=-0.004695102110002198`, `Tprev=-1857.6810997372552`, `Tprev2=-1857.7563146812574`. No stage event occurred in the physical span. The absorbing input-stage control is separate and retained.

## 2. Actual nonautonomous VigilODE diagnostic

The client actually calls `integrate_rodas5p_fast_observed` on the original C continuous EMLA source. It uses `tau=ln(a/a_U6)`, fixed normalization `u=[xe/xe_U6,Tm/Tm_U6]`, a finite-difference Jacobian and explicit partial-t at fixed state. `OdeProblem` is nonautonomous; FastSmall is not substituted. Exact requested times `i*h2`, dimensions and counts are checked. No dense interpolation, FULL or cross-stage continuous callback is used. Out-of-span/nonphysical samples are rejected.

Actual span `16*h2=0.0006792`: 16 attempts, 16 accepted steps, zero rejections and 17 direct outputs. Integrator work: 128 RHS calls, 16 Jacobian builds, 16 partial-t calls, 16 factorizations, 128 linear solves. Integration callbacks made 225 C primitive evaluations; separate initial probes used 10. Final physical state: `[0.001325115584759103,1821.2627044600886]`.

Classification is **EXPLORATORY_METHOD_COMPARISON**, with `same_algorithm_parity=false`, `admission_test=false` and `production_admission=false`. Against fixed Python, maximum existing-scale residuals are `[2.530216356188792,0.014734335610808365]`, WRMS `1.7891634790833368`. The xe difference exceeds the old same-h scale of 1. This diagnostic PASS does not admit a same-algorithm parity result.

Meaningful VigilODE reuse includes `CoreError`, `WorkCounters`, `error_scale`/`wrms`, `DenseMatrix`, and faer 0.24.4-backed `LuFactorization` in a separate actual-Jacobian 2x2 solve. Linear residual: `1.2507140131633662e-16`; difference from explicit 2x2 solution: zero. The integrator itself reports `InPlaceZeroSkipping` for LU, so faer is not claimed as every RODAS stage's backend. No 2x2 speed claim. Thermal analytic Jacobian discrepancy: `7.410278366797428e-12`; partial-t delta/half-delta consistency: `1.3505160253291377e-7`. Initial continuous/fixed C RHS bytes agree.

Expected `partial.json` exit 3: one accepted step, two outputs, actual last committed state at `tau=h2`: `[0.0013281105157509029,1822.445894284509]`.

Expected `callback_failure.json` exit 3: three rejected attempts, four attempted callbacks, one actual C source call, three retained failed callbacks, zero accepts and initial committed state retained. Failed inputs are not labelled accepted states. The upstream API exposes committed requested-grid outputs, not arbitrary unreported internal states; that limitation is explicit.

## Portable boundary packet

`rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json` is a **derived boundary packet, not the original full producer artifact**. It contains separate native/Python six-scalar states, all memories, exact binary64 hex encodings, iz, cosmology/source pins, full original input SHA256 values and derivation/review provenance. No photon or full-history arrays.

Packet SHA256: `4adfdeee1ae236725f8a654072498649c89f8e5b2e33f88eb6f40080ffbcb19d`. The `.sha256` seal is in the code/fixture closure. serde_json `float_roundtrip` is enabled; comparison paths check exact lengths and time order before pairing.

The export used `load_reviewed_u6_boundary`, evolved zero steps, and is retained in `packet_001/packet_receipt.json`. Parent independently read it back against full raw: `review/RUST_BOUNDARY_PARENT_READBACK.json` records MATCH. This worker did not repeat that full-raw readback. Portable numerical mode needs only the packet and checked-in original ZIP, with no private backup credentials or NPZ/CSV download.

Full producer pins: NPZ `5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2`; native CSV `57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38`; producer verification `1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b`; original ZIP `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

## Actual build and pinned dependencies

Existing Rust 1.94.1: `/workspace/scratch/e0149eb123fd/toolchains/rust-1.94.1-prefix/bin`. No compiler was downloaded. The local route recompiled this Rust caller and C bridge, then linked coherent read-only prior libraries. It did not freshly compile all a21d573 dependencies.

Selected core `f51eeb2f0ddc1bdb`, integrators **078a9260a490d2a9**, serde `19072e2f0126ac40`, serde_json `c01bc2f455e40147`; 163 Cargo dependency fingerprint edges were verified, including faer 0.24.4. The mixed-cache integrators `236ec...` set was not used. Libraries were compiled under `8a8bd409b1d96c7b7421f496d229e119fd3d284e`; selected sources/manifests/fixtures match pin `a21d573980f66fe02891bd216153443b5352f921`. Before/after dependency hashes match. No historical benchmark timings were reused.

Build001 retained an LLVM linker allocation failure under the 3 GiB per-process address-space limit. Build002 explicitly selected LLD, one linker thread and `--lto-O0` for the available bitcode rlibs, then passed. Build001 had no numerical invocation.

Binary SHA256: `a29462c2b47508a88396357c43fc303364dcb5a28208ff1cb81cc39a1b1a2907`; 16,396,600 bytes. Build002 target: 20,995,132 bytes (about 20.0 MiB). Local evidence before the final receipt: about 36.2 MB. A fresh Cargo target was not measured locally; the default builder requires 900 MiB free headroom. No other workspace/cache data were deleted.

### Parent packaging v2 / fresh CI

Parent's initial fresh Cargo CI at `44934c47` failed before numerical work because the source archive omitted upstream integrators `build.rs`. Parent retained the full artifact and reports approximately 160 CPU seconds for this separate CI allocation.

Packaging v2 now includes the exact file, SHA256 `a212e1bd0d2d4c6286cbd8015fa01e317111788d535efecd41c37c408bac5f7e`, without invented environment values or numerical edits. Final binding verifies that it is the only added member and all previous members are byte-identical. Counts: 123 upstream files / 124 tar members. Archive SHA256 `77c03b85844909b45428bfafd066d2403cb6f7f1870b8a68d705c4bfd1e7aca4`; `VIGILODE_SOURCE.json` SHA256 `d05094bd55820f3d86cb7e00d0012d060b3834da5fb8fb47c3f2c9dc30ff18fc`. See `review/VIGILODE_PACKAGING_CLOSURE.json`.

Fresh Cargo CI for v2 and frozen launchers is **pending**, a separate build identity. No new local full build was run for EOF normalization or launcher repair.

## Concrete repairs and targeted controls

| Finding | Correction | Actual evidence |
|---|---|---|
| C9-RUST-P2-01: finalization budget | Perform source/input/binary/artifact hashing before final resource sampling; reject over-limit totals with two CPU / three wall seconds reserved for final receipt write. | Both actual main-finally branches exercised with synthetic below/over-limit hashing cost; exits 0 and 2 respectively; zero evolution. |
| C9-RUST-P2-02: unknown telemetry | Map Popen PID into procfs; use task/children or PPID stat scan for descendants. Preserve readable stat values, fail unavailable accounting, report unsampled values as null. Retain per-process RLIMIT_AS/CPU and group kill. | guard_fix_002 PASS, and repeated actual CPU-limit control in final contracts has mapped PID and positive RSS. |
| C9-RUST-P2-03 / parent lock finding | Require committed Cargo.lock; seal before Cargo; no normal generation; metadata --locked --no-deps and actual build --locked. | Missing lock fails before Cargo; actual locked build rejects and preserves invalid lock before compilation; real lock hash unchanged. |

`contracts_fix_002/contracts_receipt.json`: **16 tests PASS / exit 0** (10 actual-client contracts plus six launcher/archive controls). Current code/request/binary before/after hashes agree. Published archive extraction into a private test directory passed without modifying parent's vendor directory.

Preserve both repair failures: `guard_fix_001` failed on missing `/proc/.../task/.../children`, not a numerical failure or guard PASS. `contracts_fix_001` had 15 passes and one incorrect control assumption: metadata `--no-deps` does not parse an invalid lock. The corrected test exercises the actual `cargo build --locked` gate, which rejects before compiling. Neither failure advanced physical state.

Resource coverage: completed CPU is RUSAGE_SELF plus reaped children; mapped child/descendant usage is polled at 50 ms. RSS is sampled tree usage, not an exact peak. Old build001/build002/verify001 zero-RSS fields mean unavailable telemetry, not observed zero or a proven peak. Their OS per-process limits were applied; numerical values and completed CPU are separate from the telemetry defect.

## Binding retained results to the frozen source

The 67-file closure has 58 byte-identical files, six parent EOF-only changes and three launcher/test repairs. Each formatted file was verified against the exact matched executed-source ZIP: current bytes plus the removed one final newline reproduce the old bytes/hash. No numerical Rust/C, tolerance, request or grid semantics changed.

For the changed verifier, all functions and numerical/validation try bodies are AST-identical after removing only the repaired two finalizers. The current validator successfully rechecked the saved primary result; all 57 numerical artifact hashes match. This advanced zero states. Final contracts bind current launcher/test hashes. The changed vendor metadata is separately classified as the missing exact upstream build script.

Historical build/run receipts remain unchanged and correctly fail the strict full-current-code gate for a new invocation. A new numerical invocation must use its new build receipt. This is scoped retained-evidence reuse, not a forged updated historical build. Plotting is outside the explicit closure.

## Recorded local resources

| Allocation | Result / exit | CPU s | Wall s |
|---|---|---:|---:|
| packet_001 | Export PASS / 0, zero evolution | 3.225742 | 3.547911 |
| build_001 | Link failure / 2 | 9.998601 | 5.854021 |
| build_002 | PASS / 0 | 21.535843 | 21.781555 |
| verify_001 | Numerical/contracts PASS / 0 | 2.395937 | 2.558934 |
| guard_fix_001 | Telemetry failed, child -9 | 0.002259 | 0.001777 |
| guard_fix_002 | Guard PASS, expected child -9 | 0.423261 | 0.413156 |
| contracts_fix_001 | Control-assumption failure / 2 | 1.895476 | 1.919489 |
| contracts_fix_002 | 16 tests PASS / 0 | 1.766172 | 1.765193 |
| handoff_001 | Scoped readback PASS / 0 | 0.123532 | 0.123691 |

Recorded local BUILD aggregate: **31.534444 CPU / 27.635575 wall seconds**, within 240/480. All other recorded local allocations including packet, controls and handoff: **9.832379 CPU / 10.330150 wall seconds**. Primary numerical verification: 2.395937 CPU seconds, within 20/60. Total local recorded allocation sum: **41.366823 CPU / 37.965726 wall seconds**. No nested-command double counting. Parent CI/intake/C9 and interactive file inspection are separate; this is not a fabricated whole-session CPU meter. Receipt writing has the stated reserved margin.

## Stable implementation paths and hashes

All production paths are relative to `/workspace/scratch/afe554957b2e/rec_work`:

```text
rust/rec-hyrec-vigilode/Cargo.toml
rust/rec-hyrec-vigilode/Cargo.lock
rust/rec-hyrec-vigilode/build.rs
rust/rec-hyrec-vigilode/README.md
rust/rec-hyrec-vigilode/src/contracts.rs
rust/rec-hyrec-vigilode/src/ffi.rs
rust/rec-hyrec-vigilode/src/fixed.rs
rust/rec-hyrec-vigilode/src/diagnostic.rs
rust/rec-hyrec-vigilode/src/main.rs
rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json
rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.sha256
scripts/build_r3o_rust.py
scripts/verify_r3o_rust.py
scripts/c_harness/original_hyrec_r3o_rust_bridge.c
tests/trajectory/test_r3o_rust.py
```

Final follow-up SHA256 values:

- Builder: `d33f4761482720cd822a3006460e9462091c9219180541e78cdc51a4ca35cfd5`.
- Verifier: `e99dbc6e022eab3301c6f4db8ee3cd5bd2e27a53eeeba2872a84a03e6d646a26`.
- Tests: `51c6ec10867eb1865dcdb0654e5a8dc65ff5e9877f62028219d69435f71c4016`.

All three have exactly one trailing newline and no trailing whitespace. All source/fixture hashes are in final_binding.json. This note and `r3o_rust_runs/write_handoff_binding.py` are additional handoff artifacts outside the production closure.

Important evidence SHA256:

- build_001/build.json: `2f8f527796e492605c89ab6ce8edf7fd5c21308cefe7935af9cdb2b5e72c6bc9`.
- build_002/build.json: `5c83ec3c219d9516d4b82a6eb5e36de671a74ed805d9bede3af37e501d5c1daf`.
- verify_001/verification.json: `8ea76f2e08b824734ddf4e5c628931772facb87359add9833244d68314a5fdf8`.
- verify_001/primary.json: `771795452b3ca3597a1f31ced387644e19434ffab01d507f46057c67b4a023d6`.
- contracts_fix_002/contracts_receipt.json: `c4dc18ea862e2346fc6fa03a64b05182c39e32dcf44ead189ac3d585dd3339e6`.

## Actual commands and portable NCP interface

Historical successful local commands, from capsule root:

```bash
python -B scripts/build_r3o_rust.py \
  --output ../rec_recovery/r3o_rust_runs/build_002 \
  --rust-bin-dir /workspace/scratch/e0149eb123fd/toolchains/rust-1.94.1-prefix/bin \
  --registry-vendor /workspace/scratch/e0149eb123fd/benchmark_work/dependencies/vendor \
  --reuse-deps /workspace/scratch/e0149eb123fd/benchmark_v2/target/release/deps \
  --reuse-source /workspace/scratch/e0149eb123fd/vigilode_v2

python -B scripts/verify_r3o_rust.py \
  --build ../rec_recovery/r3o_rust_runs/build_002/build.json \
  --boundary-packet rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json \
  --steps 16 --output ../rec_recovery/r3o_rust_runs/verify_001
```

Do not overwrite these evidence directories or use the old receipt for a new current-code invocation. Exact subprocess arguments, exits, CPU/wall and log hashes are retained in each receipt. The final contract command is `python -B -m unittest discover -s tests/trajectory -p test_r3o_rust.py -v` with the retained binary/source/request and fresh test output passed via REC_R3O_* environment; its receipt records the exact invocation. Final binding command: `python -B ../rec_recovery/r3o_rust_runs/write_handoff_binding.py`.

For NCP, start in the published checkout with existing Rust 1.94.1 on PATH, Python/NumPy, cc and ar:

```bash
export RUSTUP_TOOLCHAIN=1.94.1

python -B scripts/build_r3o_rust.py \
  --output ../rec_recovery/r3o_rust_runs/ncp_build_001

python -B scripts/verify_r3o_rust.py \
  --build ../rec_recovery/r3o_rust_runs/ncp_build_001/build.json \
  --boundary-packet rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json \
  --steps 16 --output ../rec_recovery/r3o_rust_runs/ncp_verify_001
```

Use fresh output names. Optional `--rust-bin-dir /path/to/existing/rust-1.94.1/bin`; keep that directory on PATH for the actual-Cargo negative control. Default NCP/CI uses a **fresh --locked source Cargo build**, one job, private CARGO_HOME and target. Add `--registry-vendor /path/to/vendor` for prepared offline registry packages; otherwise Cargo obtains the pinned public registry packages. The builder verifies and auto-extracts the published VigilODE archive and isolated HyRec source. Upstream tests/examples are not built. Packet mode needs no private full-raw retrieval. `--reuse-deps` is the explicit sandbox alternative, not the default.

Standalone CLI: `--input REQUEST.json --output NEW.json [--mode all|fixed|diagnostic] [--max-attempts 1..32] [--callback-limit 1..2048]`, with prepared C data directory as cwd. The verifier handles cwd and reviewed request automatically.

## Preserved scope and remaining parent work

h2 `4.245e-5`, START 58389, END 211716. Full 153327-step completion, global h/h2/h4 convergence, HyRec speedup and production admission remain **NOT_RUN**. U5 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, REI=false remain unchanged.

No remaining worker implementation finding requires another physical run. C9's three P2 findings are closed. Parent is handling C9-RUST-P3-01: the verifier's one-attempt partial-failure control completes the whole span when --steps=1, so that input cannot satisfy the intended partial-failure expectation. The narrow correction restricts verifier --steps to 2..32 (default 16 unchanged) and adds a parser-only rejection control. Parent explicitly owns further verifier/test edits; this worker makes none. This changes no retained 16-step result or physical budget.

Parent can publish the worker-freeze repairs, its separately recorded P3 follow-up and ready packaging v2, preserving all failed build/control/CI evidence. Fresh full-source Cargo CI remains pending. No worker code writes or runs remain after this note.
