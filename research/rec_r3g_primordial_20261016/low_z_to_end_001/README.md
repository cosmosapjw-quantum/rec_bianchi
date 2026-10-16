# R3G-U8-LOW-Z-TO-END-001 code preparation

This bounded continuation begins at the independently reviewed U7 STOP:
global source index 69999, hydrogen-local index 51776, (z\simeq19.99757).
Python carries the accepted (x_e,T_m) state and both two-step hydrogen and
thermal derivative memories. It integrates at most 35,859 source-native
updates through accepted global index 105858, with no photon-history reads or
writes. At the first input where either original effective-rate table guard is
false, `history.c` switches irreversibly to the Peebles three-level atom with
Fudge=1. Thermal evolution continues without a new seed.

The original source's final accepted grid point has a slightly negative
redshift. It is used only as the last interpolation node; no rate is evaluated
there. `rec_interp1d` clamps the (z=0) interpolation index to 105856 and uses
global nodes 105855–105858 with fraction 1.7363115444604773. The same generic
source interpolation operator includes the beginning clamp at (z=8000).

The 8,001 integer-redshift outputs are assembled from the immutable verified
U1 helium prefix, globals 0–18222, and the independently integrated hydrogen
nodes, globals 18223–105858. The duplicate index 18223 is checked before the
prefix row is dropped. Original C is replayed separately and `rec_build_history`
is called once for independent full-precision output. Original C is only an
oracle for the Python trajectory.

`LOCAL_PREFLIGHT.json` records the exact local pinned-input checks, unit tests,
and one-step original-C/Python smoke. The complete U8 integration and 8,001-row
comparison require a fresh independent preflight decision and one bounded NCP
case. U5's historical average-spectrum gate remains HOLD; temporal refinement
is NOT_RUN, and REI activation remains false.

Execution interface:

```text
python scripts/verify_r3g_low_z_to_end.py --preflight|--execute \
  --evidence-dir NEW_CREATE_ONLY_DIR \
  --u7-stop-npz U7_STOP.npz --u7-stop-json U7_STOP.json \
  --u7-verification U7_VERIFICATION.json --u7-c-stdout U7_C_STDOUT.csv \
  --u7-admission U7_SCOPED_REVIEW.json \
  --u1-rows U1_ACCEPTED_ROWS.jsonl --u1-verification U1_VERIFICATION.json \
  [--execution-manifest CONTROLLER_MANIFEST.json] \
  [--source-dir EXTRACTED_ORIGINAL_HYREC] \
  [--max-extra-accepted 35859]
```

The execution manifest binds the committed U8 files, original ZIP, pinned U7
and U1 inputs, baseline gzip, execution revision, and controller verification.
