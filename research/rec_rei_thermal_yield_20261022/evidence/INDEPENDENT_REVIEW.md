# THERM01 independent physics and implementation review

Reviewer task: `/root/compact_reuse`. One bounded review pass; read-only scientific/code inspection. The reviewer previously assessed PR220 source reuse, but did not implement THERM01, set its acceptance thresholds, perform its eight IVPs, or alter its donor sources. Current review state: **PASS_SCOPED_THERM01_WITH_SOURCE_CLARIFICATION**. Stage C has now been inspected in this same bounded pass; the pre-run findings below retain their original scope.

## Material actually read

`FROZEN_CONTRACT.md`, `AMENDMENT_Q1.md`, `THEORY_SOURCE_MEMO.md`, `COMPACT_REUSE.md`, `IMPLEMENTATION.md`, all four new `code/*.py` files, `UNIT_CHECKS.json`, `STAGE_B_EXECUTOR_RECEIPT.json`, and the earlier pinned PR220 donor code/provenance used in the reuse assessment. REC checkout has no local root `AGENTS.md`; the actual REI `AGENTS.md` previously read governs the donor-source work and the communicated execution/review split. No model identity is inferred from a task name.

## Pre-run findings

**No BLOCK_NOW defect found.** Proceeding to the frozen eight new IVPs is supported within the stated conditional model.

- The new source owner uses the same GL4 nodes and weights for rate, absorbed-energy and photoelectron moments, with fixed physical support and H I normalization. The numerical midpoint failure was preserved and Q1 changes quadrature only.
- The cancellation-resistant RR moment formula is algebraically equivalent to `k_B T^2 alpha'(T)+(3/2)k_B T alpha(T)`, including the temperature derivative of Badnell's B. The DR expression retains signed fit terms before summation. Source-fit derivative accuracy is correctly distinguished from measured cooling accuracy.
- Recombination escape includes capture kinetic energy plus one binding increment; thermal cooling removes only the kinetic moment. The photoionization ionization-potential increment and thermal excess sum to absorbed photon energy. No binding or DR excitation term is counted twice.
- `w=(3/2)eta T` is a thermal energy per baryon divided by k_B. Its `-2w` expansion term is the proper monatomic adiabatic work. Inverting this state gives the composition-dependent particle-count term without adding it a second time.
- The new RHS and diagnostics evaluate actual dynamic T. The donor prescribed-T `point`, RHS, Jacobian and diagnostics are not reused. SciPy computes a fresh finite-difference Jacobian for the new owner.
- Common scalar T and isotope-independent coefficients preserve the old element/isotope map. Reflection-even geometry is unchanged. The new arrays have explicitly distinct compact34/full63 schemas and restore all21 populations, including zero n/T.
- The rate domain is enforced in actual evaluations, including Newton and quadrature trials. There is no temperature floor, clipping, abundance renormalization or hidden heat bath.
- The per-baryon energy ledger has the correct sign and expansion factor. Its end-point energy comes from saved w/Y; absorbed, escaped and work terms are evaluated independently by GL8/16 on dense output. These are not integrated tally states. This checks finite numerical consistency, not empirical rate/cooling accuracy.
- The original REC126, REI129 and warm729 cases are not dispatched. The new cases are prospective and named separately. Fixed physical HOLD, REC U5 holds, global convergence NOT_RUN, production NOT_APPROVED and REI_activation=false remain explicit.

## Independent arithmetic actually executed

One fresh, no-ODE check used a separate scalar implementation of the VF cross-section formula from the pinned coefficient JSON and SciPy adaptive `quad`, integrating from each threshold to Emax40/60. It compared rate, absorbed-energy and kinetic-heating moments for H I, He I, He II, Li I, Li II and Li III (36 comparisons, including structural zeros), independently normalizing to H I Gamma=1e-12 s^-1.

Maximum relative discrepancy from implemented GL4 was **7.295998463231063e-13**, at He II heating for Emax60. Implemented `4.3523872393956254e-33 W/ion`; independent adaptive integral `4.35238723939245e-33 W/ion`. All inactive charge-channel moments were exactly zero. The independent reference used `epsrel=1e-11`, threshold-split scalar integration, and no implementation photo-cross-section helper. This supports the photon quadrature repair under the fixed fit/spectrum; it does not assess the underlying physical cross-section uncertainty.

The reviewer did not rerun the unit suite, any historical ODE, any new IVP, a benchmark, or the campaign wrapper.

## Completed Stage C saved-result review

Exactly **six nominal histories + one tight compact34 validation + one full63 oracle = eight new IVPs** have complete receipts and193 saved epochs each. Seven raw histories have34 coordinates and one has63; every output restores21 populations. All raw SHA256s and source/config identities match. The57 donor files were actually verified again as part of the source/adoption check. No old cohort was replayed by this reviewer or by the inspected dispatcher.

From saved raw arrays, the reviewer independently reconstructed temperature, total stored energy, charge neutrality, isotope totals, baryon number, zero n/T, number monopoles, optical-depth increments, signed stress summation, normalized integrated-energy residual and GL8/16 differences. Maximum isotope residual is1.672e-15, baryon residual8.882e-16, signed stress sum residual5.421e-20; minimum scaled population is0. Accepted temperatures span204.0817–15939.455K across all eight histories. ActualT agrees with diagnostics to roundoff. All relevant raw checks agree with receipts.

The planned finite comparisons were recomputed from saved arrays:

| Comparison to nominal split60 | Relative T | Absolute charge fraction | Absolute tau | Absolute signed observable |
|---|---:|---:|---:|---:|
| tight compact34 |1.0212332e-6|6.1671320e-8|8.1872922e-10|3.8377683e-9|
| full63 oracle |5.4192095e-8|3.7277791e-8|5.9665911e-11|1.9609618e-9|

These pass the predeclared3e-5/3e-5/3e-7/3e-7 criteria for the representative case. They do not provide an unperformed isotropic tight solve or global continuum convergence result.

### Energy gate and narrow margin

The largest normalized energy residual is **2.935629461677083e-6**, in isotropic60 atz=11.9105512 (elapsed191.9237023Myr), below the frozen3e-6 gate. It uses97.8543% of the permitted threshold, leaving2.1457% margin. This is a finite PASS with a narrow observed margin; no tolerance was changed and no cross-platform robustness is inferred.

The largest GL8/16 difference over all cases is1.8433032674e-10. To resolve the concrete near-threshold risk without another IVP, the reviewer independently rebuilt both quadratures for isotropic60 using stored dense states, a separate scalar adaptive photo integral and separately coded recombination energy expressions. The3072 GL16 nodes reproduce the stored integral to normalized4.21473597e-14 and give peak2.935629475906332e-6, still passing. The1536 GL8 nodes were also checked. Thus neither end-point bookkeeping nor the new photo quadrature explains away the observed residual; retain the residual as the actual finite numerical result. Small GL8/16 disagreement is not by itself a rigorous total-error bound.

### Figure and CSV inspection

All three actual PNGs were viewed. Temperature is logarithmic; ion fractions are shown directly; ledger magnitudes/residuals are logarithmic with exact-zero masking explicitly stated; signed stress differences use a labeled symlog threshold. Time is elapsed properMyr fromz20, with an explicitly labeled split60 redshift reference for multi-case figures and per-case redshift in stress panels. Separate massive-matter and photon+neutrino stresses are plotted before summation. Labels, legends and curves are readable, and the near-gate energy peak remains visible. No semantic or clipping defect requires a figure repair.

All16 hash-bound figure/CSV outputs match their manifest. Each of eight history CSVs has193 rows and21 species columns; diagnostics and populations round-trip exactly to saved raw arrays. The two difference tables and PNG/PDF outputs are bound by their actual hashes. Direct PDF rendering was not performed; actual visual review covered PNGs produced by the same figure objects.

### Source wording correction

The frozen sentence saying core excitation is zero was too broad as a physical statement. The published Müller etal2026 primary confirms Li resonant core excitations within50–70eV. The correct scope is that the **retained direct Li I1s-photoionization branch** vanishes below64.39eV, whereas resonant core excitation/decay is an excluded process and has no zero omission bound. This is recorded in `evidence/SOURCE_SCOPE_CLARIFICATION_REVIEW.md`; root will carry the exact correction into the result/handoff scope note. It changes neither the already declared smoothed-continuum retained-process model nor its numerical source identity, so no code change or IVP rerun is required.

## Final scoped decision

**PASS_SCOPED_THERM01_WITH_SOURCE_CLARIFICATION; remaining current-task blockers: none.** The evidence supports the implemented5–40/60eV retained-process thermal/ionic-yield model, its eight specified new histories and the inspected figures. Source-fit derivative cooling accuracy, omitted resonant/excited/secondary/collisional processes, full60–200eV yields and complete thermodynamic/nuclear closure remain outside this numerical admission. Physical/REC holds, global convergence NOT_RUN, production NOT_APPROVED and REI_activation=false are unchanged.

The reviewer executed zero IVPs, zero old/test-suite reruns and zero benchmarks. This single pass is closed; no recursive reviewer or optional extra campaign is requested.
