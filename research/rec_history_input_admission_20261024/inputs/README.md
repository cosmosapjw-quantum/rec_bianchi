# Immutable input locations

The current capsule preserves source/contract files, exact recovered primary
SUMMARY and recovery-aware review records. It does not duplicate the large
original NPZ payloads. The original numerical study read all four actual NPZs;
their exact hashes are in INPUTS.json. No study is rerun to reconstruct lost rows.

At rec_bianchi commit93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa:

- h2_u4.npz: research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/ncp_run_001/python_u4_exit.npz
- h4_r3q_event.npz: research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz
- h4_smoke.npz: research/rec_r3s_ncp_campaign_20261021/ncp_execution_001/evidence/campaign_001/jobs/h4_legacy16/run/worker/python_continuation.npz

h2_u5.npz is member run_001/python_u5_thermal.npz in the original Dropbox archive:

/bianchi/rec_bianchi/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz

Dropbox ID id:BSpOijBcT10AAAAAAD-8UA. Archive SHA256
8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c.
Member SHA256 7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b,
79,241,133 bytes. The prior recovery observed whole-byte archive/member identity;
see provenance/U5_RECOVERY_RECEIPT.json. Original verification FAIL is preserved.

Original target CSV is bundled and remains SHA256
3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.
Reading these locations is input recovery, not authorization for a new integration
or repeated verification. See NEXT_INPUT_CONTRACT.md for the next actual obligation.
