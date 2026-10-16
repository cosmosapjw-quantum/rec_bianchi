# R3G-U7-EMLA-TO-Z20-001 code preflight

This is bounded code preparation for the original October 2012 HyRec source
switch at local hydrogen index 10972 (global 29195). The predecessor U6 STOP
NPZ, sidecar, verifier, C stdout, and independent scoped admission are pinned
by SHA-256 in the loader. Historical U5 original verification remains `FAIL`;
its nine average-spectrum pairs remain `HOLD_ORIGINAL_TOLERANCE_NOT_MET`.

The independent Python continuation carries U6 hydrogen and thermal derivative
memories through the original source recurrence, evaluates the original 2012
EMLA2s2p effective-level rate table, and does not read or write photon history
after the source's FULL-to-EMLA switch. Original C is replayed independently;
its stdout is used only as an oracle. At full length, exactly 40,804 EMLA
updates reach global 69999 (local 51776). The four available source-grid
points 69996–69999 define the original `rec_interp1d` cubic value at z=20.

The candidate REI donor is recorded with `activation=false`. U7 does not
establish temporal refinement, REI production behavior, optical depth,
Bianchi recombination, or a CMB observable. Source guards may produce a typed
`HOLD_NEXT_STAGE_REQUIRED` before the target; such an output is not a PASS.

Local pinned-input preflight and one-step original-C/Python smoke passed;
`LOCAL_PREFLIGHT.json` records their hashes and observed errors. The full U7
NCP launch requires fresh independent scientific preflight review.

The first independent preflight found two failure-path defects, retained in
`LOCAL_PREFLIGHT.json`. The bounded repair keeps F/G memories at the last
accepted state when a candidate is rejected, records attempted evaluations
separately, and matches the Python/C thermal guard code. Its targeted test
uses a deliberately unphysical H RHS of `-1e8` to force rejection. The same
falsifier using the real pinned U6 STOP is saved in
`REAL_U6_REJECTED_CANDIDATE.json`; this is a guard test, not a physical
trajectory. `LOCAL_PREFLIGHT_REPAIR_001.json` records the second local smoke.

Execution interface:

```text
python scripts/verify_r3g_emla_to_z20.py --preflight|--execute \
  --evidence-dir NEW_CREATE_ONLY_DIR \
  --u6-stop-npz U6_STOP.npz --u6-stop-json U6_STOP.json \
  --u6-verification U6_VERIFICATION.json --u6-c-stdout U6_C_STDOUT.csv \
  --u6-admission U6_SCOPED_REVIEW.json \
  [--execution-manifest CONTROLLER_MANIFEST.json] \
  [--source-dir EXTRACTED_ORIGINAL_HYREC] \
  [--max-extra-accepted 40804]
```

Execution manifest keys: `controller_verified`, `execution_revision`, pinned
U6 SHA fields, `source_zip_sha256`, and SHA-256 map `u7_files_sha256`. This
manifest binds the frozen source and implementation revision before NCP use.
