# Central integration plan — REC-H5-NATIVE-REFERENCE01

## Actual base and count

The last directly inspected shared central source is `rei_bianchi@74aff0740d1812c732466563a9c66108a3a4d8fd`, branch `research/orchestration-sandbox-20261022`. Its new BASS owner return records **28/88**, increased from27 by completion of the existing B3h selected finite-transaction contract. `survey/remote/R3_CENTRAL_COMPARE.json`, `R3_CENTRAL_STATUS.json`, `R3_CENTRAL_RETURN.json` and `DELTA_R3.json` preserve this evidence. The new REC reference unit has count increment0. L4 remains false and global physical completion null.

The local full DAG at `research/rec_source_synthesis_20261027/delivery/central/patch_tree/research/orchestration_expansion_20261025/DAG.json` is an older source-synthesis candidate. It was inspected only for88-node/17-edge schema and the existing REC-H5 wrapper. **Do not publish that DAG or import its older working wrappers.** The first fetch_file calls returned empty content; a later contents fetch and blob retrieval recovered the exact current74aff bytes as described below. The latest live HEAD may already differ from74aff; use its actual source/return count and preserve all parallel changes.

### Fresh complete DAG recovered

`assembly/recovered/DAG_74aff074.json` is the exact source at `74aff0740d1812c732466563a9c66108a3a4d8fd`. Directory metadata supplied blob `af5280b83acd18a54f525f45bff6311100c9ce4c` and1619494bytes. The blob-specific fetch returned identical text to the independent contents fetch. Local bytes match both provider size and Git blob SHA1; SHA256 is `bae9177f301a6c6e5de3af0111574e53bf7c47ef9563930ae6f13b70365c7ee7`. It parses as88nodes/17edges and contains the target REC-H5 node. The live central HEAD was reread as74aff before this recovery. Exact observations and measured metadata CPU are in `assembly/recovered/RECOVERY_RECEIPT.json` and `DAG_PROVIDER_METADATA.json`. This resolves the previous full-DAG input gap for74aff. Root still checks branch freshness immediately before the expected-SHA update.

## Minimal target files

At the fresh current central tree, prepare:

1. `research/orchestration_expansion_20261025/returns/REC_H5_NATIVE_REFERENCE01_20261027.json`: actual ACKed REC science commit, exact root C9 decision and source hashes, actual313 reference/representation scope, physical H5 coverage0/313, null physical epsilon/full-stateK/physicalM2, count effect0.
2. `research/orchestration_expansion_20261025/status/REC_H5_NATIVE_REFERENCE01_20261027.json`: sibling scoped status, actual current central completed count and unchanged parent status.
3. `research/orchestration_expansion_20261025/DAG.json`: add only `owner_return_native_reference01_20261027` to the existing `REC-H5-DEFECT-BOUND01` node, pointing to that return. Preserve every original field, including status, claim gate, next action, budgets and nested immutable preimages. Preserve other87 nodes, all88contracts/dependencies,17edges and all non-node objects.

Existing `status/CURRENT_STATUS.json`, `contracts/REC-H5-DEFECT-BOUND01.json`, node plans, CR/BASS returns and provider budgets need no rewrite for this partial sibling observation. Their current evidence remains authoritative. No new DAG node or integration edge is required. Do not promote M2_ref to physical M2 or deterministic reference bounds to physical epsilon.

## Assembly and publication mechanics

`assembly/prepare_central.py` creates the three-file candidate only after root provides the fresh whole-DAG SHA256, expected commit, current count, ACKed REC science commit and exact C9 decision. It uses a byte-local JSON splice for the one sibling pointer. It then removes that pointer from the parsed candidate and requires full equality with the original88-node document. The byte complement outside the modified node is also checked. The helper never updates remote state.

Root reviews the three-file diff and mechanical receipt, then creates a tree against the **fresh current central commit/tree**, creates its commit and calls the ref update with that same `expected_sha` and `force:false`. A changed HEAD requires reassembly from the new DAG, preserving the new owner returns/count; do not force or reset. Actual ref readback and source file/blob readback supply the publication ACK. These later ACKs belong in separate delivery receipts.

If fresh complete DAG bytes cannot be recovered, the narrow fallback is to prepare/publish only the two new sibling return/status files against the fresh current tree. Record DAG-pointer integration as pending rather than replacing the large DAG with an older local copy. This preserves current88-node/17-edge contracts and all parallel evidence while retaining a reviewable central owner return.

## Execution status

Preparation only. No source archive built, no scientific sources imported or executed, no tests or solver replay, no Git/provider mutation, no new scientific admission. Root owns C9, final packaging release, publication, backups and completion decisions. Packaging has a separate cumulative60CPU ceiling with lowcompression ZIP level1; historical and foreign budgets remain unchanged.
