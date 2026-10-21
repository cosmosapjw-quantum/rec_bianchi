# R3T-U4B independent audit results

- Prelaunch A–C review: `PASS_SCOPED_PRELAUNCH_A_C` on the exact execution source.
- Result review: `PASS_SCOPED_U4B_NUMERICAL_RESTART`; read-only, no solver rerun.
- 49 manifest files: all SHA256 entries match. U4A input checkpoint/result binding verified.
- 1551-column causal prefix unchanged; 32 owned columns appended; 1583 total. State/index/predictor/photon history continuity verified.
- Native raw output 20,064 lines (=32×627): max state scaled residual 4.930470639159558e-14, H RHS 1.5519280305298366e-11, lane tolerance ratio 2.3476254700241836e-4.
- Common-input 128 evaluations; worker split 16+16 exact equality. Independent raw split recomputation is not claimed because a separate split raw stream was not retained.
- Accepted Schur max 5.786145415750408e-16; thermal predicate max 1.041836845350197e-6 < 5e-4; all 33 states post-Saha. RT stop 116777 not reached. Boundary crossing `NOT_RUN`.
- Resource: terminal unit CPU 5.375101 s, worker exit 0, supervisor exit 0, stop exit 0, MemoryPeak 336064512 bytes, per-process AS limit 2 GiB. Whole-allocation CPU and wall remain `UNRESOLVED` per additive accounting correction. I/O `NOT_MEASURED`.
- No plot was generated or reviewed (`NOT_REVIEWED`). No physical validity/global convergence claim.
