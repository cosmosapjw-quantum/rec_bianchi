# Portable source/input archive preparation

`prepare_portable_source.py` is prepared for the parent-authorized archive-only
step after the final C10 commit. It has not built an archive during preparation.
No science, Git, cloud operation, dependency installation or scientific test runs.

The exact invocation is:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python /workspace/scratch/6104ad84b826/rec_bianchi/research/rec_source_synthesis_20261027/delivery/prepare_portable_source.py --source-head EXACT_40_HEX_FINAL_C10_COMMIT --output /workspace/scratch/6104ad84b826/deliverables/REC_SYNTHESIS_20261027_SOURCE.zip
```

Replace the placeholder with the parent-provided C10 commit. The helper records
that identifier without inferring the stale local HEAD. It requires all twenty
R/C stage files, ROOT_DECISION and the existing independent theory/code decisions.
It snapshots all currently present final C10 documentation within the new unit.

The ZIP preserves repository paths under `rec_bianchi/`; it includes the complete
new unit, complete reused GEO01 unit, complete program_expansion_20261025 tree,
the frozen native hydrogen.c, repository metadata, and the original private LAMDA
source at `survey_literature/lamda_hd_live.dat`. Curated central DAG/recovery/delta
context lives under `source_context/survey_repo/`. All NPZ inputs and all prior
partial-cost, failure and repair evidence are preserved. Historical archives,
Git metadata, caches, temporary fixture and credential paths are excluded and
listed by reason in the manifest. No unrelated repositories or account inventory
are discovered or included.

Member ordering, timestamps, file modes and JSON formatting are deterministic.
SOURCE_MANIFEST.json records every other member's byte count and SHA256. Its own
byte count and SHA256 are in the external packaging receipt, avoiding a recursive
self-hash. Every member, including the manifest, receives full CRC and byte/hash
readback. RESTORE_README_KO.md explains layout, private raw-data handling, manifest
verification, and equivalent path rebinding for historical absolute commands.

Output must be strictly below 95 MiB. An oversized complete partial ZIP is retained
with a failure receipt and options for parent-authorized transport/splitting;
inputs are never silently omitted. Existing outputs/partials/receipts prevent an
unchanged overwrite. Packaging CPU, wall time and peak RSS are recorded separately
from science, with unmeasured I/O tails UNKNOWN_NOT_ZERO. The helper writes its
receipt outside the ZIP and does not include its own future cloud acknowledgement.

Preparation used static source/metadata reads only; no archive, scientific test or
scientific run was executed. Parent GO is still required before invoking it.
