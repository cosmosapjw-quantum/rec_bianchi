# U6: coupled FULL history to the RT boundary

The new Python continuation reads the reviewed U5 h/2 checkpoint at global input 53179 and advances its own accepted H, Tm, and 311+3 photon histories. The thermal branch stays latched. At most 5,210 FULL evaluations are allowed; the last accepted output is global index 58389, before the first EMLA evaluation.

The C harness starts independently at z=8000 on the same h/2 grid, emits the full 16,733-column accepted prefix, and then emits the new source-native steps. The verifier checks the checkpoint SHA, the 109-file source closure, same-grid states, H/Tm derivatives, spectra, Schur residuals, and all 313 causal frequency links for each new input. Original mean-photon and restricted roundoff-aware decisions are reported separately.

Local one-step smoke: `SMOKE_ONLY`, 4 targeted tests PASS. The latest smoke checks one Python FULL evaluation against one independently generated C step, 625 spectral fields, and 313 causal links. `PRE_REVIEW.json` holds hashes and the cumulative budget ledger. The full U6 run is `NOT_RUN` pending fresh static review. This node has only the original HyRec q=0 FULL H+He scope.
