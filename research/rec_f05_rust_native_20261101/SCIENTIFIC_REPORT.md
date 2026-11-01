# rec_bianchi historical Rust material-physics reactivation (2026-11-01)

## Original Rust architecture, scope and scientific target
This one bounded migration is on ONE Draft PR #193 stacked on immutable REC #192 HEAD 1a53d8b7a138233478550afe3f26eeb0a8f5db5b. Historical rec_bianchi already contains the actual edition2024 rust/rec_microphysics library, rust/rec-stream-audit and rust/rec-hyrec-vigilode. Verified historical commits for selected He, finite-tilt frame, Peebles pure H, source-screen, Rust audit. We add one source-authentic original F05 H/He accepted 0→160 material module into the EXISTING rust/rec_microphysics crate, one executable and tests, preserving all historical files except the one-line library module export. This is **NOT** a claim that primordial HyRec's complete C/Python physics or original REI F05 owner has been fully rewritten.

REI original 26-event H/He source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, original initial NPZ SHA256 7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d, original forcing SHA256 9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268, original accepted160 three lane states source hashes in source loader, identical numeric array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01. Accepted history receipts 0→64,64→128,128→160; archive has original state bytes only at tick160. Tick161 remains NONAUTHORITATIVE and production HOLD.

## Constructive material physics and real Rust generated output
Original source 46,080 H/He cell weights W_node, original constant first-interval z_source=5.95; V_j=W_node_j*MPC_CM^3/(1+z)^3 (proper cm^3). Five species (HI,HII,HeI,HeII,HeIII), N_e=N_HII+N_HeII+2N_HeIII, n_e=N_e/V_j, Gamma_T=c*sigma_T*n_e with c=29979245800 cm/s and sigma_T=6.6524587051e-25 cm^2. Exact accepted-endpoint change at constant source volume is deltaGamma_T=c*sigma_T*deltaNe/V_j, NOT an instantaneous IVP derivative. Source clumping Ce=Vsum*(sum Ne_j^2/V_j)/(sum Ne_j)^2 >=1.

Rust loads immutable ORIGINAL TAR, NPZ and source forcing bytes by read-only tar/unzip and sha256sum utilities, decodes little-endian numpy f64 and REIADP1 native arrays; original physics and all numerical reductions execute in rec_microphysics Rust. All 3 source lanes SHA and common original 46,080-row binary payload checked. No original source rerun, no new ionization IVP or time-interpolated sky.

Executed original-source Rust science summary:
- Original accepted material cells: 46080, three original source shapes collapsed into ONE physical realization.
- Initial volume-weighted Thomson collision rate: 1.35829120060093477e-18 s^-1.
- Accepted160 rate [1.35823333811822384e-18,1.35823341769999859e-18] s^-1.
- Accepted0→160 rate change [-5.78624827108946518e-23,-5.77829009364074070e-23] s^-1.
- Electron clumping initial 5.89306883190828135; accepted160 [5.89045081623442268,5.89045837792826266].
- Spatial signed physical cell classes gain=3660, loss=42384, ambiguous=36.
- Rust 46,080 physical CSV SHA256 f2e9170c711b42d968d0c09d60640dad89e6823a573a1d03a8a694d939c1bed0.
- Rust result JSON SHA256 12dcadaca92d4664a143585e0bd7d34296d43856dcc68678532851b770a69202.
- Independent original Python Decimal source oracle CSV SHA256 4ecf6d930a4f1d6ef5d8c6e8b3cde60ece4df906c8bc87a59be679b5fecb449f, oracle JSON SHA256 9509bc02e9f4c45dc91ec66b997a829819125562c81d46d1d15594cd2902b545.

## Actual numerical/source verification and hostile science audit
- Existing Rust rec_microphysics baseline tests prior to change: 108/108 PASS, Rust runtime 1.99.0, source existing Cargo.toml edition2024/rust-version1.94 with NO dependencies.
- Added 8 native Rust physics/sign/charge/volume/clumping/negative-source tests 8/8 PASS. Full Rust crate after change: 116/116 PASS (historical 108+new 8).
- New Rust files scoped rustfmt --edition 2024 --check PASS. Historical full cargo fmt --check PRE-EXISTING FAIL due old tests/forward.rs formatting; this migration does not touch old source nor falsely claim repository-wide format PASS.
- Original full 46,080-row x17-column parity: exactly 0 sign-class mismatches, maximum non-cancellation-field numerical relative deviation 6.40342181756292575e-16; cancellation-scaled absolute comparisons PASS for all source rows. Global accepted collision-rate delta relative error maximum 2.14031761378433578e-12, due to f64 subtraction of large nearly equal totals vs Python Decimal.from_float. Preserve this explicit distinction; source binary SHA is byte identity, numerical material is scientific equivalence, and different output CSV byte SHA is EXPECTED.
- Negative tamper: mutate copied original NPZ one byte, Rust source loader fails closed; original files untouched. Identity parser checks original F05 TAR, NPZ, forcing, all three lane state files, common numeric payload, original 0→160 accepted receipt and source proper-time forcing.
- Wolfram exact algebra independently checks deltaGamma constant-volume identity and positive weighted-clumping identity; no claim of formal outward MPFR over the original 26-event IVP.

Finite hostile review: Python-Decimal and Rust-binary64 numerical different printouts are NOT a source violation. Very tiny deltaGamma and helium electron delta fields have large misleading relative differences from cancellation; compare their absolute differences on a parent physical scale without changing original F05 error/tolerance gates. Electron clumping is NOT a multiplicative opacity correction, material Gamma_T is NOT dimensionless line-of-sight tau, original isotropic volume forcing is NOT Bianchi/Sachs geometry, and two accepted snapshots cannot substitute for continuous accepted photon/electron history. Different-author blind referee NOT_RUN, native subagent NOT_RUN.

## Deployment and DAG
This Rust port is a source-scoped research consumer and does NOT replace production REI solver nor full HyRec ionization pipeline. No merge, force push, original source owner swap, F05 worker mutation or tolerance change. Next meaningful research: original REI F05 official versioned tick161 admission and source-matched Bianchi photon/geometry full LoS; stop further source-only equivalent atlases. DAG REI canonical 28/88(+0), working 33/88(+0), Physical Fast 4/7(+0), REC H5 physical 0/313(+0). Do NOT count 46,080 rows or Rust tests as new canonical DAG nodes. Source physics CI and binary archive backup must be independently read and recorded after actual outcomes.
