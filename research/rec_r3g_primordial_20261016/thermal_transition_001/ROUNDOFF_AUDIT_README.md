# R3G U5 saved first-failure roundoff audit

This is a posthoc audit of the original NCP U5 `result_001`. It does not advance or alter the Python history. The original verifier remains `FAIL` at average virtual bin 8, row 2218. The immutable source run used commit `766023946a2219530d58e66eb8bc306dd89071a9`, original HyRec ZIP SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, and saved STOP NPZ SHA-256 `09e702caf0bc0ce0edb1ce629477669c55e59c7fff34cd7298d759613719528f`.

`ROUNDOFF_AUDIT.json` contains the complete compact numerical receipt; `ROUNDOFF_AUDIT_TIME.txt` records the local execution. The audit checks all 7,364 new accepted rows, their state, H and thermal derivatives and memories, source event and two coupled thermal updates, and all 625 outgoing spectrum values per row against the saved original C stdout. The 9 average virtual failures are exactly `(2218,8)`, `(3017,10)`, `(3456,11)`, `(4046,13)`, `(4458,12)`, `(4489,14)`, `(4734,11)`, `(4835,14)`, `(4864,14)`. Virtual outgoing and Lyman channels have no failures. Maximum original average tolerance ratio is 32.65320690729941, so original photon parity is still `HOLD`.

For those nine pairs only, the script uses each owner's saved state and causal history, 18 independent Python atomic snapshots, 18 unmodified original C FULL calls, and 18 unmodified C populate calls. It proves each active retarded interpolation pair lies in saved C columns 8 through `j-1` before filling unsaved columns 0 through 7 with zero placeholders. It checks the source diagonal identity at bins below diffusion, computes `phi=1-(1-exp(-tau))/tau` in binary64 and with precision-80 `Decimal.from_float(tau)`, and bounds the propagated binary64 cancellation. The precision-80 residual between the two owner histories is below the original photon tolerance for all nine pairs. This is a diagnosis of the saved first failure, not a source-algorithm replacement or a new trajectory PASS.

Run locally from the repository root with the recovered immutable `result_001` folder:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
timeout 120s python scripts/audit_r3g_u5_roundoff.py \
  --folder /path/to/recovered/result_001 \
  --report /new/create-only/ROUNDOFF_AUDIT.json
python -m pytest -q tests/trajectory/test_r3g_u5_roundoff_audit.py
```

The measured audit used one CPU, 9.97 s wall, 9.09 s user CPU, and 266,548 KiB peak RSS. Five focused tests passed. Scientific scope is the bounded original `q=0` FLRW HyRec H+He history through the first thermal event plus two steps; a full primordial Python history, source-grid refinement, REI activation, and Bianchi/CMB predictions are not established.
