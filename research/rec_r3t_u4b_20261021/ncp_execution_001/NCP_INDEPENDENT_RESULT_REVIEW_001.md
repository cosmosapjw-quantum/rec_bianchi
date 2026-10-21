# Independent U4B result review

Verdict: `PASS_SCOPED_U4B_NUMERICAL_RESTART`, restricted to the actual 32 accepted steps 74443→74475. Reviewer was read-only and did not rerun the solver.

- All 49 MANIFEST SHA256 entries match.
- U4A checkpoint/result input binding matches; 1551 causal prefix columns remain unchanged and exactly 32 columns append (1583 total).
- State/index/predictor/photon ownership and small checkpoint continuity verified.
- Native raw output has 20,064 rows (=32×627). Independently recomputed maximum scaled residuals: state 4.930470639159558e-14, H RHS 1.5519280305298366e-11, photon lane tolerance ratio 2.3476254700241836e-4.
- Accepted Schur maximum 5.786145415750408e-16; thermal predicate maximum 1.041836845350197e-6 < 5e-4. All 33 states post-Saha. RT stop 116777 not reached; event/boundary crossing `NOT_RUN`.
- Common-input 128 evaluations and worker split 16+16 exact equality are supported by the executed path/receipt. No separately retained split raw stream exists, so independent split recomputation is not claimed.
- Exact systemd InvocationID terminal CPU 5.375101 s; worker exit 0, supervisor exit 0, unit stop exit 0; MemoryPeak 336064512 bytes. Whole-allocation CPU/wall are `UNRESOLVED`; additive accounting correction records omitted intervals and the unmeasured prelaunch attempt.
- No plot was generated or reviewed (`NOT_REVIEWED`). No global convergence, physical validity, or production claim.

The two metadata/accounting findings are resolved additively in `receipts/addenda/ALLOCATION_ACCOUNTING_ADDENDUM_001.json`; immutable original receipts remain unchanged.
