#!/usr/bin/env bash
set -u -C
umask 077
base=/root/REC_R3G_LOW_Z_TO_END_20261016_001
cd "$base/source" || exit 96
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONHASHSEED=0
/usr/bin/time -v -o "$base/launch_001/time.txt" \
  /usr/bin/timeout --signal=TERM --kill-after=5s 300s \
  /usr/bin/prlimit --as=2147483648:2147483648 --cpu=270:270 -- \
  /usr/bin/taskset -c 40 \
  /root/REC_R3G_PRIMORDIAL_HHE_20261016_001/.venv/bin/python scripts/verify_r3g_low_z_to_end.py \
  --execute --evidence-dir "$base/result_001" \
  --u7-stop-npz "$base/inputs/checkpoint_0012_stop.npz" \
  --u7-stop-json "$base/inputs/checkpoint_0012_stop.json" \
  --u7-verification "$base/inputs/verification.json" \
  --u7-c-stdout "$base/inputs/native_oracle_stdout.csv" \
  --u7-admission "$base/source/research/rec_r3g_primordial_20261016/emla_to_z20_001/ncp_execution_001/U7_SCOPED_REVIEW.json" \
  --u1-rows "$base/inputs/python_accepted_rows.jsonl" \
  --u1-verification "$base/source/research/rec_r3g_primordial_20261016/helium_stage_001/verification.json" \
  --execution-manifest "$base/inputs/execution_manifest.json" \
  --max-extra-accepted 35859 \
  > "$base/launch_001/stdout.txt" 2> "$base/launch_001/stderr.txt"
rc=$?
printf '%s\n' "$rc" > "$base/launch_001/exit_code.txt"
exit "$rc"
