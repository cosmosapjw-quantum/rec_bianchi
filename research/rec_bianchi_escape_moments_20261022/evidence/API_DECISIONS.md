# ANGULAR01 implementation choices

Implementation reads and follows FROZEN_CONTRACT.md and THEORY.md. No tolerance was changed.

- `angular_moments(t,S,mode="auto")` is the public general path. Explicit `quadrature` preserves the finite-depth integrand; explicit `thick` rejects inputs outside the same frozen analytic gate used by AUTO.
- `validate_inputs` performs the fixed 64-epsilon symmetry/trace/positive-expansion checks, projects only inside that roundoff band, and returns its correction norm.
- Principal-frame integration uses an octant with normalized positive product Gauss-Legendre weights. Reflection symmetry makes off-diagonal principal-frame second moments exactly zero in the continuous problem. The full tensor is rotated back; it is never replaced by an isotropic scalar.
- `lrs_moments` uses an independent 1D Gauss-Legendre reduction. Its axis is a real nonzero vector, normalized to set orientation.
- `lab_frame_oracle` uses full-sphere Gauss-Legendre polar nodes and a periodic azimuthal rule, integrating every tensor component directly in the lab frame. This is a separate numerical discretization, not an independent physical derivation.
- The vector probability is `-expm1(-tau)/tau`. Twenty new scalar reference calls use the unchanged vendored PR114 class. A spike attenuation map is not described as a full Sobolev emissivity model.
- Analytic thick bounds include their logarithms and representation status. Underflow produces a `None` numeric value plus the finite logarithm, never an exact-zero certificate. Finite two-level differences have an explicitly observational result type.
- AUTO grid decisions reuse already computed nominal quadratures; representative standalone checks exercise both public AUTO branches. Grid quadratures, new donor comparisons, standalone rotation/weak-shear checks, and pre-study boundary regressions are counted separately.
- `run_study.py --execute --attempt attempt_001` refuses to overwrite an old attempt, streams every row and check, records exact source hashes/environment/calls, and preserves partial rows on budget termination. It contains no cosmological integration and does not run old test suites.
- `plot_results.py` reads saved measurements only. It creates three figures (PNG+PDF) and preserves every plotted array as CSV with a hash manifest.

The independent reviewer found three finite-domain edge defects before the study. The previous module and a repair record are preserved in evidence/. Only their targeted regressions are authorized before the full frozen study; the study itself is not repeated for reassurance.

Skill context used: physmath-research-loop 1.3.0 SKILL.md, STAGE_SELECTION.md, SUBAGENT_MODE.md, POLICY_INTEGRATION.md, CODING_LOOP.md; selected implementation/verification scope C2–C8 under the parent's frozen ANGULAR01 contract. Parent owns theory, provenance, delivery, DAG, report, and external publication.
