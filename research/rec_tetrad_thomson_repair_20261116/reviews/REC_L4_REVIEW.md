# Independent REC l≤4 quadrature review

Updated verdict: **Q_LABEL_NUMERICS_PASS_PHYSICAL_INTERPRETATION_REJECTED**. The checks below pass for a positive degree-4 quadrature in the fixed q labels and its finite-q128 method-comparison gate. The historical REC199 failure remains a historical failure. This does not establish continuum angular convergence, a new native gas/photon evolution, transported polarization, or a source-owner/DAG promotion.

Reviewer independence: a separate agent started with `fork_turns=none`, did not author the producer, and did not modify the author’s files. I read the code, derivation and supplied source data; reran the seven author tests; and independently calculated all 640 native stages, 1,280 channel tensors and 81,920 angular output rows. The independent path uses centered long-double input reductions, a separate harmonic fit to small residuals, and a three-dimensional coherency tensor instead of the producer’s Q/U matrices. This is a distinct-agent review, not an external human review or independent replay of the original Rust source. Current-turn execution probe: `PYTHON_PASS` (Python 3.12.14, NumPy 2.3.5). The first reviewer script attempt hit a reviewer-only ring-grouping error caused by floating-point duplicate z values; canonical ±{1,3,5,7}/8 grouping fixed it before the reported run. No author output was changed.

## Material source-frame correction discovered during review

The subsequently inspected original `source_spectral_support.py` explicitly calls q “angular Killing rays”, computes g²=Σqᵢ²exp(−2Hᵢt), and injects isotropic photons using weights proportional to exp(−ΣHᵢt)/g³. `source_capture_native_angles.py` groups the native surviving counts by this same fixed Killing-ray index. Consequently the prior REC199 assertion that q are the actual event-time normal-tetrad directions is incorrect in Bianchi I. For A=diag(exp(−Hᵢt)), the actual tetrad direction is n=Aq/|Aq| and dΩ_n/dΩ_q=det(A)/|Aq|³. The captured masses already encode their q-cell allocation; physical intensity must be estimated as mass/J and integrated with physical n-sky weights, without multiplying the native masses by J a second time. The corrected physical-frame output has now passed a separate scoped independent check recorded in `REC_TETRAD_REVIEW.md` and `.json`. The original `results/native_l4_*` tables remain q-label diagnostics and cannot be accepted as physical source-native Thomson Stokes output. The original q-label numerical evidence is preserved below.

## Mathematical scope and positivity

Write the normalized sky integral as ⟨f⟩=(4π)⁻¹∫f dΩ. The original source is an eight-ring midpoint sky with sixteen equally spaced azimuths. Solving the three exact rational polar constraints ⟨1⟩=1, ⟨z²⟩=1/3 and ⟨z⁴⟩=1/5 gives the author’s coefficients independently:

`w_i=[68083/61440−(64517/47520)z_i²+(2641/1485)z_i⁴]/128`.

The ring reflection and azimuthal symmetry handle odd monomials and nonzero azimuthal harmonics through degree 4. All Cartesian monomials of total degree ≤4 match their spherical means to at most 5.55×10⁻¹⁷ in the supplied floating-point q file. The weights are strictly positive, ranging from 0.006633966619318182 to 0.008680802162247475.

For incident intensity I=I₀+b·q+qᵀSq with tr S=0, the normalized quadrupole is 2S/(15I₀). Its integrand has degree at most four, so degree-4 quadrature is the appropriate exactness requirement. The old second-moment-only rule could annihilate a monopole but could not integrate an arbitrary quadrupole sky exactly. The reviewer’s nonspecial symmetric tensor test agrees with the exact result to 2.04×10⁻¹⁸.

For projected positive masses m and 0≤p≤1, Kᵢⱼ=(3/4)wᵢ[1+(qᵢ·qⱼ)²] is nonnegative and column stochastic. The second-moment identity gives Kw=w, so the isotropic field is a stationary state. The full post-event mass (1−p)m+pKm is nonnegative. Photon number and energy channels each conserve their own totals. The input energy-per-photon ratio may change under the separate number and energy projection normalizations; this is a measurement reweighting, not a physical update of the source spectrum.

The independent polarization construction uses C=(3/4)∑ⱼmⱼ(1−qⱼqⱼᵀ), then Iᵢ=pwᵢ(Cθθ+Cφφ), Qᵢ=pwᵢ(Cθθ−Cφφ), Uᵢ=2pwᵢCθφ. C is positive semidefinite for m≥0, proving √(Q²+U²)≤I. For an isotropic input C is proportional to the identity, proving zero Q/U. These signs agree with the documented Q=Iθ−Iφ convention.

## Independently reproduced evidence

| Check | Result |
|---|---:|
| Author tests rerun | 7/7 pass |
| Native stages / channel tensors / angular rows | 640 / 1,280 / 81,920 |
| Largest tensor component difference from saved output | 1.385×10⁻¹⁶ |
| Largest I/Q/U difference, divided by p∑N (or p∑E) | 9.68×10⁻¹⁸ |
| Largest saved elastic ledger residual, divided by p total | 3.324×10⁻¹⁶ |
| Largest FLRW tensor norm, independent centered reduction | 9.77×10⁻¹⁷ |
| Native p versus −expm1(−cσₜnₑΔt) | zero floating-point discrepancy |
| Original-hat tick142 number: ‖Q₄‖ | 2.8016217586×10⁻⁹ |
| Same witness: ‖Q₄−Qfit‖/‖Q₄‖ | 0.001484637526 (0.148464%) |
| Same witness: ‖Q₄−Q₆‖/‖Q₄‖ | 0.025146173425 (2.514617%) |

The reported maximum comparisons over all models also reproduce. The old gate definition compares the quadrupole estimator to the l≤2 fit on Bianchi stages with amplitude above 10⁻¹². Its 3% threshold is unchanged. `new_l4_same_3pct_gate` checks this fit comparison; the l6 comparison is a separate diagnostic, although its actual maximum is also below 3%. The fit and l6 use the same 128 angular samples; their agreement is not independent angular convergence evidence.

## Required limits and small implementation findings

1. **A degree-4 quadrature is not an exact quadrupole extractor for arbitrary incident skies.** With positive I=1+0.1P₄(z), the exact continuum quadrupole vanishes, yet this l4 rule gives ‖Q‖=0.0026104353323. The l6 rule gives 4.90×10⁻¹⁶. This is an expected degree-six-integrand counterexample, not a defect in the degree-four theorem. Higher angular structure, aliasing and native q128 continuum resolution remain unresolved. The native fixed-hat result can be reported as estimator sensitivity, not as a certified ≤3% physical quadrupole error.

2. **The source interpretation matters.** Replacing equal angular cell weights by wᵢ is justified as a declared alternative integration of sampled continuum intensity. If the native rays instead mean a physically discrete collection of beams, reweighting changes that angular distribution. The source declaration says equal-area midpoint directions and optional collision measurement; do not describe projected masses as unchanged original per-ray packets. Their global totals, not every ray value, are preserved. The two channels use separate normalizations.

3. **Numerical centering is improved but not maximal.** `quadrupole()` removes the isotropic baseline before the tensor sum, avoiding the older subtraction of two order-one tensors. However, `I/mean−1` and the direct Q/U matrix products retain an O(machine-epsilon) absolute floor. Reviewer centering `(n−n_ref−weighted_mean(n−n_ref))/mean` gives a trace residual below 4.82×10⁻²³. The existing output’s ≤1.4×10⁻¹⁶ component discrepancy is far below the tick142 gate margin and does not change its verdict. At nearly isotropic FLRW amplitudes, relative errors should remain unreported.

4. **Standalone grid validation checks only even moments.** Antipodally folding all q into z>0 preserves the tested second/fourth moments, so `weights_l4()` accepts that invalid full-sky grid; its weighted ⟨z⟩ is nonzero. This does not affect `run_native_l4.py`, which pins the entire original q file by SHA256. If the kernel is exposed to arbitrary grids, also validate odd moments or source identity before calling it a general degree≤4 validator.

5. **Byte provenance is verified; original-native execution is not independently repeated.** The local q SHA256 is `a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92`; native-angle SHA256 is `70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1`. Both match the pinned producer constants and supplied REC199 authority snapshot at c10e97ab3178c423cc7699684b33e1730d26437a. Saved derived-output hashes match the result manifest. The source-native capture execution and upstream BASS provenance are inherited evidence; this review makes no fresh Rust-replay claim.

Units are consistent: nₑ[cm⁻³] c[cm/s] σₜ[cm²] Δt[s] is dimensionless; p, w, q and the normalized quadrupole are dimensionless; Q/U and collision increments carry photons/H or eV/H with their respective input channels. Elastic, stationary-electron, unpolarized-input, endpoint first-Born/splitting assumptions remain material. No recoil, electron thermal correction, multiple scattering, transport or full coupled IVP was checked or added.

Machine-readable measurements and file hashes are in `REC_L4_REVIEW.json`; the independent replay is `rec_l4_independent_check.py`.
