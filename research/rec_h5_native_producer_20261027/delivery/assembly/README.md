# Prepared delivery mechanics

These helpers are prepared source only. They have not built the final archive, executed scientific code, run tests, or written Git/provider state. Root supplies the actual C9 decision and releases delivery after admission.

## Source snapshot

`prepare_source.py` freezes every noncache file under the new unit, including source, theory, saved evidence, figures and existing receipts. It also includes byte-preserved original SOURCE_CONTEXT, target native CSV, original history NPZ and all seven original `.py/.c/.h` source dependencies in the THERMO01 vendor directory. Five immutable source SHA256 locks match CODING_CONTRACT/FROZEN_CONTRACT. Scientific modules are not imported.

The final ZIP uses DEFLATE level1. A member SHA256/size/Git-blob manifest is embedded, then CRC and all member bytes are read back. Its final archive SHA256, measured packaging CPU and pending provider status are external sidecars. Subsequent ACKs belong in a companion and do not cause repacking.

The helper produces `GIT_TEXT_ENTRIES.json`, `GIT_BINARY_BLOBS.json` and `GIT_EXCLUSIONS.json`. Binary entries contain exact base64 bytes for allowed figures with their paths and expected Git blob SHA1; root creates blobs with `encoding=base64`, checks returned SHA, then uses those SHAs in the same tree as the text entries. No binary blob/commit/ACK is inferred by this helper. Unchanged original dependencies, raw LAMDA data, all remote survey inventories/account metadata, archives, NPZ and large nonfigure binary payloads remain archive-only. The private inventories remain in the complete source archive.

Run only after root supplies the actual admitted decision:

```sh
python3 research/rec_h5_native_producer_20261027/delivery/assembly/prepare_source.py \
  --repo /workspace/scratch/6104ad84b826/rec_bianchi \
  --out /workspace/scratch/6104ad84b826/deliverables/REC_H5_NATIVE_REFERENCE01_FINAL \
  --science-commit ACTUAL_ACKED_C9_SCIENCE_SHA \
  --decision ACTUAL_OWNED_ROOT_DECISION_PATH \
  --decision-sha256 ACTUAL_DECISION_SHA256 \
  --release-after-c9 --prior-packaging-cpu ACTUAL_CUMULATIVE_PACKAGING_CPU
```

The 60CPU ceiling is cumulative. Prior debit is mandatory and cannot be reset. The child process receives the remaining CPU limit; startup/closing and remote/tool/model costs remain unmeasured unless root measures them externally. Preparation has not consumed a scientific execution allocation. Preserve a failed preparation and debit before any root-authorized retry.

## Central scoped return

Read `../CENTRAL_INTEGRATION_PLAN.md`. `prepare_central.py` accepts a fresh complete central DAG, exact expected HEAD/hash and actual root decision. It creates exactly three candidate files: new return, new scoped status and a byte-local additive sibling pointer in the existing REC-H5 node. Its comparison removes that one key and requires the entire original DAG to be structurally equal, including all88contracts, dependencies, budgets,17edges and top-level metadata. Bytes outside the target node remain identical. CURRENT_STATUS is unchanged. The source snapshot and current central completed count are explicit root inputs; count increment is0.

The helper does not fetch, publish, update a ref, create a backup or adopt science. No use of a stale local DAG is permitted. Fetch the current whole DAG at the exact expected central commit, then recheck the live branch HEAD before the expected-SHA/non-force ref update. If parallel work advances HEAD, assemble from the new complete DAG while preserving its observations and current count.

```sh
python3 research/rec_h5_native_producer_20261027/delivery/assembly/prepare_central.py \
  --dag FRESH_COMPLETE_DAG_PATH --dag-sha256 ACTUAL_DAG_SHA256 \
  --expected-head FRESH_CENTRAL_HEAD --science-commit ACTUAL_ACKED_C9_SCIENCE_SHA \
  --decision ACTUAL_OWNED_ROOT_DECISION_PATH --decision-sha256 ACTUAL_DECISION_SHA256 \
  --central-completed ACTUAL_CURRENT_CENTRAL_COUNT \
  --out /workspace/scratch/6104ad84b826/central_preparation/REC_H5_NATIVE_REFERENCE01_FINAL
```

Before use, root reviews these preparation-only sources. Final runtime/CRC/SHA and actual publication/backup evidence are pending. Syntax parsing is metadata verification, not a scientific or packaging execution.
