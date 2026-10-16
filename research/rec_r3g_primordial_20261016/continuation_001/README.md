# R3g U3 bounded NCP continuation

This is a scoped original October 2012 HyRec `q=0` H+He continuation.
The independently integrated Python trajectory resumes its U2 checkpoint
and accepts 374 new source-native steps, ending at global index 18605
(`z=1647.72462398495`). It crosses the source HeII cutoff at index 18603
and accepts two H-only steps. It has not reached H post-Saha termination or
completed the primordial history.

## Identity and raw evidence

- Base PR #98 HEAD: `7f7ca8d3d497b9b9ef90b46b33f8bd6f981b17b1`.
- Frozen U3 execution commit: `7a85032a32bd2d593b9622331c85c6da1b1e179d`.
- Original HyRec ZIP SHA-256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- NCP namespace: `/root/REC_R3G_PRIMORDIAL_HHE_20261016_001`.
- Returned complete NCP archive SHA-256: `6160a4810eda1edeb2db5c96ffd342202d87bb223c91d0d9bdf3331bc44a2527`.
- `verification.json` contains individual build, C oracle, Python trajectory,
  source, state, photon and resource receipts. `NCP_RETURN.json` binds its
  compact files to the returned archive. The raw archive includes source
  capsule, accepted rows, native stdout, checkpoints, build output and launch
  timing; it is not checked into Git.

## Reproduction and limits

After verifying the capsule manifest, the NCP launch ran:

```sh
timeout --signal=TERM --kill-after=10s 600s /usr/bin/time -v \
  taskset -c 40 .venv/bin/python scripts/verify_r3g_continuation.py \
  --execute --evidence-dir /root/REC_R3G_PRIMORDIAL_HHE_20261016_001/result_001 \
  --execution-manifest /root/REC_R3G_PRIMORDIAL_HHE_20261016_001/capsule_001/controller_execution_manifest.json \
  --max-extra-accepted 2048
```

`OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and
`NUMEXPR_NUM_THREADS` were set to 1 before Python import. The parent used a
2 GiB virtual-address limit and 540 s process CPU limit. The outer `timeout`
limited the whole command to 600 s. Actual whole-command wall was 8.97 s,
user+system CPU was 8.89 s, and peak RSS was 115,596 KiB. The source and
output hashes in `verification.json` are for this single run; no output was
fabricated from the C oracle.

Independent read-only review recomputed all 374 C/Python trajectory rows and
233,750 photon values from raw output. This admits only the U3 interval.
The next source branch and time-step refinement remain separate work.
