# Independent physical-tetrad Thomson review

Verdict: **PASS_SCOPED_TETRAD_L4_ESTIMATOR** for the corrected event-time physical-frame collision source at the original 640 native stages. The prior q-label calculation remains numerically reproduced but its interpretation as physical tetrad Stokes output is rejected. Both the historical 3% estimator failure and the later frame error remain part of the record. Continuum angular convergence, a coupled polarized Boltzmann evolution, and owner/DAG promotion remain unresolved or unperformed.

This is a distinct-agent review (`fork_turns=none`), with no producer code authored or edited. I independently read the newly retrieved source scenario, spectral-support code, native continuous driver and capture code, and recalculated all 640 stages, 1,280 channel tensors and 81,920 saved angular rows. The independent implementation solves the constrained weights with an SVD minimum-norm solve instead of the producer’s normal equations; it uses long-double centered intensity residuals and a 3×3 coherency tensor for I/Q/U. The original Rust stage solver was not rerun. The nine new physical-frame author tests were independently rerun and passed 9/9. After the producer added the explicit scenario SHA256/continuum guards and loaded H from that scenario, the full independent data check was rerun; derived output identities were unchanged. Current-turn execution: `PYTHON_PASS`.

## Source semantics and physical map

The original `science_scenario_v1.json` explicitly defines an isotropic continuum angular measure, a positive midpoint-μ/uniform-φ quadrature as its numerical approximation, and conserved covariant/Killing photon momentum between interactions. It specifies aᵢ(t)=exp(Hᵢt), aᵢ(0)=1, zero tilt, and the same Bianchi/FLRW H arrays used by the runner. The continuous source driver uses the fixed q grid, initially assigns N/128, and injects later isotropic matter-frame emission with `original_birth_weights∝exp(−ΣHᵢt)/g³`. Native angular capture groups surviving packet counts by those fixed q indices. Thus q is a Killing-direction label, not the later orthonormal-tetrad direction.

Let A=diag(exp(−Hᵢt)) and g=|Aq|. The physical unit propagation direction is n=Aq/g. For a tangent vector u on the original unit sphere,

`Dn[u]=(1−nnᵀ)Au/g`.

Taking the oriented tangent-area determinant gives

`dΩ_n/dΩ_q = J = det(A)/g³`.

The review independently checks this Jacobian against the tangent derivative at all used directions/times; the maximum absolute discrepancy is 6.66×10⁻¹⁶. In the isotropic FLRW limit A=a⁻¹1, n=q and J=1, as required. All factors are dimensionless.

Native mass N_q is already allocated per fixed q angular cell. The physical intensity sample is therefore proportional to N_q/J. Multiplying by J again would double-count that coordinate measure. The corrected collision projection `m_i∝(N_q,i/J_i)w_phys,i`, followed by normalization to the original native total, is the appropriate declared estimator. Photon number and energy receive separate total-preserving projection normalizations; original per-ray native packets are preserved as inputs, not asserted identical to their projected values.

## Quadrature and verification

The author starts with mapped positive weights w₄(q)J and applies the minimum Euclidean correction enforcing all homogeneous Cartesian moments of degree 4 in n (or degree 6 for the comparator). Because |n|²=1, the degree-4 constraints imply degree-2 and degree-0 constraints. On the actual antipodally symmetric grid, odd moments vanish too. The independent checker explicitly tests all Cartesian monomials up to the requested degree, rather than relying only on this argument.

Strict positivity was checked at every original stage, with minimum degree-4 weight 0.0066338297714 and minimum degree-6 weight 0.0023033306938. The largest condition numbers of the moment matrix are 7.677 and 43.337, respectively; no near-rank-deficient constraint system was found in this dataset. General anisotropic backgrounds can fail positivity or become ill-conditioned, so this result is scoped to the actual supplied source histories.

| Independent check | Result |
|---|---:|
| Stages / channel tensors / saved angular rows | 640 / 1,280 / 81,920 |
| Degree≤4 monomial maximum absolute residual | 4.44×10⁻¹⁶ |
| Degree≤6 monomial maximum absolute residual | 1.52×10⁻¹⁵ |
| Arbitrary l≤2 intensity exactness, maximum tensor error | 1.01×10⁻¹⁷ |
| Isotropic centered tensor | exactly zero in checker |
| Isotropic coherency spin residual | ≤7.56×10⁻¹⁶, relative to unit source scale |
| Saved tensor versus independent tensor | ≤1.462×10⁻¹⁶ componentwise |
| Saved I/Q/U versus independent coherency | ≤1.421×10⁻¹⁷ after division by p total |
| Saved elastic total residual | ≤2.869×10⁻¹⁶ after division by p total |
| Characteristic BI photon peak P/scattered-in | 5.67473765937×10⁻⁶ |
| Characteristic BI energy peak P/scattered-in | 7.42816881008×10⁻⁶ |
| Original-hat BI photon peak P/scattered-in | 5.14402651226×10⁻⁶ |
| Original-hat BI energy peak P/scattered-in | 6.90016564639×10⁻⁶ |

The original-hat tick142 physical photon tensor has Frobenius norm 5.02279931697×10⁻⁶, with relative l4-versus-fit difference 8.49034263×10⁻⁷ and relative l4-versus-l6 difference 1.43772496×10⁻⁵. The largest l4-versus-fit difference over actual Bianchi channel stages is 1.31412×10⁻⁶; the largest l4-versus-l6 difference is 2.22566×10⁻⁵. These are fractions, not percent values. The former 0.148% and 2.515% witness comparisons belong to the old q-label target and must not be quoted as the corrected physical-frame result.

With the physical moment identities, the positive Thomson kernel is stochastic, isotropic radiation is a fixed point, and the coherency tensor is positive semidefinite. Thus the conservation and polarization inequalities established in the q-label review transfer to the actual physical tetrad. The original p calculation, units and endpoint/Born assumptions are unchanged. In particular p=cσₜnₑΔt+O(p²) is dimensionless, and Q/U carry photons/H or eV/H according to their channel.

## Scope of the accepted result

The source-authoritative continuum interpretation is now established, resolving the earlier beam-versus-cell ambiguity. The degree-4 quadrature exactly extracts moments of an l≤2 physical intensity field; it does not integrate arbitrary higher-multipole fields exactly. The explicit positive I=1+0.1P₄ counterexample retained in `REC_L4_REVIEW.md` still demonstrates this boundary at t=0. An l6 comparator and l≤2 fit on the same 128 rays measure estimator sensitivity, not independent angular convergence or a rigorous continuum error bound.

The original and corrected outputs are different physical targets. The runner’s `q2_*` values compare the historical wrong-frame tensor to the new physical fit, so they are diagnostic only; the manifest correctly identifies this. The tiny new l4-versus-fit fraction is partly influenced by the restored physical-frame quadrupole in the denominator. It must not be presented as a proof that the earlier 3% physical-accuracy question was settled by merely changing quadrature degree.

The author’s baseline subtraction is sufficient for the recorded signal amplitudes but retains a machine-precision floor in near-isotropic fields. Direct Q/U products also retain such a floor. FLRW relative comparisons below the 10⁻¹² amplitude threshold remain uninformative and are appropriately excluded. Unpolarized input, stationary comoving electrons, Thomson elasticity, no recoil/thermal corrections, and single-scattering source-only evaluation remain material assumptions.

Exact local file hashes, independently computed measurements, source-contract hash, and corrected-output identities are in `REC_TETRAD_REVIEW.json`. The independent replay is `rec_tetrad_independent_check.py`. The original source-native Rust capture is inherited provenance evidence; this review verifies byte identity of inputs and calculation on those inputs, not an independent upstream native replay.
