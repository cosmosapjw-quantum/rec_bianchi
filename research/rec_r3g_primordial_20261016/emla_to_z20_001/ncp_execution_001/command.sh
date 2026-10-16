#!/bin/bash
set -eu
root=/root/REC_R3G_EMLA_TO_Z20_20261016_001
cd "$root/capsule_001/source"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec timeout --signal=TERM --kill-after=10s 300s /usr/bin/time -v taskset -c 40 /root/REC_R3G_PRIMORDIAL_HHE_20261016_001/.venv/bin/python scripts/verify_r3g_emla_to_z20.py --execute --evidence-dir "$root/result_001" --execution-manifest "$root/capsule_001/controller_execution_manifest.json" --u6-stop-npz /root/REC_R3G_FULL_THERMAL_TO_RT_20261016_001/result_001/checkpoint_0006_stop.npz --u6-stop-json /root/REC_R3G_FULL_THERMAL_TO_RT_20261016_001/result_001/checkpoint_0006_stop.json --u6-verification /root/REC_R3G_FULL_THERMAL_TO_RT_20261016_001/result_001/verification.json --u6-c-stdout /root/REC_R3G_FULL_THERMAL_TO_RT_20261016_001/result_001/native_oracle_stdout.csv --u6-admission "$root/capsule_001/source/research/rec_r3g_primordial_20261016/full_thermal_to_rt_001/U6_SCOPED_REVIEW.json" --max-extra-accepted 40804
