# REC #195 original accepted 0→64→128→160 physical H/He trajectory

2026-11-02 KST. Owner = rec_bianchi, physical consumer of ORIGINAL rei_bianchi IGM F05 26-event source. This bounded study has physically computed original source state intervals rather than a new opacity or synthetic sky. Immutable REC parent #194 HEAD `b1f3dd6516539fc6b98a131528f42d8076b41fa3`. REI owner #363 HEAD `abf83d4d883d5f311426b7f02cb001e70138ceb4`. Original source TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; source kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.

## Real reconstruction

Starting from REI #363 actual private first64 source state, replay original **unchanged** 26-event MPRK22(1)+Alexander SDIRK2 full/half/half for [64,128] and [128,160] on 46,080 native H/He cells. Actual original accepted history is [0,64] attempt1, [64,128] attempt2, REJECTED [128,192] attempt3, [128,160] attempt4. All six new full/half native maps certify; all 14 original photon/nucleus/energy ledgers include zero per accepted interval; zero table events. No original worker/REI worktree writes.

- Tick64 original SHA256 `aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425` already source-replayed in REI #363.
- Tick128 newly computed REIADP1 SHA256 `bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6`, **byte-exact historical**; max source local defect `1.0458495067311446e-4`.
- Tick160 newly computed SHA256 `74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6`, **byte-exact historical and original sealed archive**, local defect `1.60637217206272e-4`.
- Original unchanged local gate `2e-4`, original width `2e-3`, no changes. Tick161 V1 FAIL/HOLD unchanged.

The first unpinned host NumPy2.4.2/pandas3.0.0 attempt generated tick128 SHA `ccf9acad895471e4767272e87f35943f151dd7942aec4afccb3de13d143dfc03` and failed strict original byte gate. With an isolated virtualenv matching historical NumPy2.3.5/pandas2.2.3/SciPy1.17.0, original byte parity was restored on both intervals. Specific responsible library operation remains unidentified; this is runtime/reproducibility failure diagnosis, not a new physics theorem. Nonfatal old optional numexpr/bottleneck ABI warning was observed, with exit 0. Full Python runtime fingerprint is not the complete historical source-owner production contract.

## Actual original data and new physical interpretation

46,080 source cells × four accepted endpoints 0,64,128,160 = **184,320 measured source-derived rows**, *one original physical dataset*, not 184,320 independent IVPs or observed photons. Recovered output `results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz`, SHA256 `6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c`. Machine JSON `results/SCIENCE_RESULT.json`, SHA256 `f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429`.

Original interval electron changes (electrons): [0,64] [-1.0261279532104401e62,-1.0248126998449919e62], [64,128] [-1.0132316976777894e62,-1.0091770753239848e62], [128,160] [-5.038627341100841e61,-4.9763109401954075e61]. All strictly negative global.

Original ionization binding energy B and translational gas U from the **same original** species/population intervals (not the external CMB bath). Interval source-clock SECANT magnitudes, units 10^39 erg/s:

| Original accepted ticks | Gas translational U decrease | Ionization binding B decrease |
|---|---|---|
| 0→64 | [4.69585995,4.72464719] | [7.97062697,7.98197576] |
| 64→128 | [5.45825816,5.56899111] | [7.79732313,7.83322138] |
| 128→160 | [5.84637455,6.29989148] | [7.66165011,7.77400949] |

**Distinct physical finding**: strictly increasing magnitude of kinetic energy decline over original accepted source epochs but strictly decreasing magnitude of chemical ionization binding decline, with non-overlapping interval boxes. This distinguishes physical channels and demonstrates time-resolved evolution from a genuine original 26-event source. It does NOT identify the individual rate/process responsible or establish the continuum instantaneous derivative. The source's earlier 4-group photoionization *gross positive* rates in BASS_HE #149 and REI #363 are distinct from net ΔB and must not be equated. Likewise the extra isotropic-CMB-bath Compton term from REC #194 is NOT silently inserted into this original source model.

## Independent hostile science and implementation audit

`audit_energy.py` recomputes all 184,320 source-data rows without invoking the original owner solver. It verifies source identities, all H/He nuclei and volumes unchanged, charge positivity, Thomson rate and ideal-gas U for all rows, 3 ΔNe intervals, temperature/electron density product difference identity, and non-overlap of three interval cooling/discharge rate bounds. Wolfram independently reduced the exact finite-difference product identity to 0.

The initial auditor compared differences of two ~1e66 global electron sums to per-cell summed ~1e62 increments at a spuriously strict *delta-relative* threshold, triggering a false alarm (~3e-12 relative to the small Δ but <4e-17 of parent electron inventory). Corrected to a physically justified source-inventory-scaled comparison. This is a NUMERICAL_COMPARISON repair, **not** a change to original physical tolerance or accepted state. Independent audit JSON SHA256 `24c5ca4686321181db20eed15312240279a9cc1a73614a2b2edb9dced83b1654`.

Source-free ordinary unittest 7/7 PASS and Python -O 7/7 PASS; tests include negative bad-archive-content digest (fails closed). Initial test had a mistaken literal for original tick160 SHA and was corrected without changing physics. Source-free audit regenerated JSON byte-exact locally.

New physical state replay is source-restricted local; cloud Actions in this REC PR validates **published source outputs and source-free audit**, not original owner stage/full REI IVP. The original replay's source-inclusive backup stores private state files; never push private original REI state files to the public repo.

## Stage record and DAG

R1–R4: source identity, original received owner/records, formulate direct science; theory checkpoint commit.
R5: source map & physical interval formulas derived.
R6–R7: original SHA, 14 ledgers, 6 source map computations, numerical/physical source tests.
R8–R10: read source evidence, strict scope admission, scientific report and handoff.
C1–C4: frozen sources, input map, solver ownership and preserved acceptance.
C5: real 26-event source replay and 184,320 physical material cells.
C6–C9: source SHA checks, original 14 ledgers, source-free full-row energy audit, finite corrections and regression.
C10: only source-conditioned draft delivery, source-inclusive cold restore plus exact backup acknowledgment.

**Owner central REI canonical 28/88 (+0); working 33/88 (+0); Physical Fast 4/7 (+0); REC H5 physical 0/313 (+0)**. Source endpoints were historically accepted, but new current-owner tick161 is NOT_ACCEPTED. All this is reusable source data, not a new canonical DAG node. Production HOLD, Draft/HOLD, no merge, no force push, no reionization source-owner swap or original gate relaxation. Native subagent NOT_RUN; only same-model adversarial audit, independent distinct author NOT_RUN.

Next scientifically causal blocker: original F05 [160,161] V2 owner admission, or source/clock-matched photon trajectories to Sachs/Boltzmann observables. Do NOT expand into surrogate opacity or audit-only campaigns.
