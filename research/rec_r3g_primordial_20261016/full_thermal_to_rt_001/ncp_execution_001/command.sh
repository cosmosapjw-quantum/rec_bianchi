#!/bin/bash
set -eu
root=/root/REC_R3G_FULL_THERMAL_TO_RT_20261016_001
cd "$root/capsule_001/source"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec timeout --signal=TERM --kill-after=10s 300s /usr/bin/time -v taskset -c 40 /root/REC_R3G_PRIMORDIAL_HHE_20261016_001/.venv/bin/python scripts/verify_r3g_full_thermal_continuation.py --execute --evidence-dir "$root/result_001" --execution-manifest "$root/capsule_001/controller_execution_manifest.json" --u5-stop-npz /root/REC_R3G_THERMAL_TRANSITION_20261016_001/result_001/checkpoint_0032_stop.npz --u5-stop-json /root/REC_R3G_THERMAL_TRANSITION_20261016_001/result_001/checkpoint_0032_stop.json --u5-original-verification /root/REC_R3G_THERMAL_TRANSITION_20261016_001/result_001/verification.json --u5-scoped-audit "$root/capsule_001/source/research/rec_r3g_primordial_20261016/thermal_transition_001/ROUNDOFF_AUDIT_REPAIR_001.json" --u5-scoped-admission "$root/capsule_001/source/research/rec_r3g_primordial_20261016/thermal_transition_001/U5_SCOPED_REVIEW.json" --max-extra-accepted 2604
