# R5D-v2 trusted RF-00 payload local-runtime closeout

**Date:** 2026-09-04 UTC  
**Classification:** `PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE`

This directory mirrors the selected UTF-8 evidence from the exact local R5D-v2
execution. The complete original receipt directory remains in Dropbox at:

```text
/bianchi/_runtime_receipts/BASS_REC_SOURCE_R5D_V2_20260904T021026Z
```

## Exact source and trusted payload

```text
BASS source publication head
6ffbcceb660896f29d569533f0349c8ebaafbbe1

BASS production source commit
92d67dc79cf645947beb93ac01a9505ee277dabd

tree
65cb63e6d08e80e9a8f38f83e3a536cb0a00a693

source blob
869677390004f68aef9f547e6556f5f1c15bd012

trusted RF-00 artifact commit
50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda

trusted wheel SHA-256
99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302

installed shared-object SHA-256
5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633
```

## Executed result

- exact native identity: PASS;
- R5+R6 focused source suites: 21/21 PASS;
- backend policy/integration/packaging cone: 54 PASS;
- forbidden unverified-development provenance lines: zero;
- schema-v2 source and integrated-binding hashes: deterministic in two fresh
  Python processes;
- source worktree: clean;
- root package build: non-Git staging directory;
- `BASS_ALLOW_UNVERIFIED_NATIVE_DEV`: unset.

This closes the REC-owned trusted-native prerequisite for the next test-only
dual-adapter node, but does not implement a physical REC source, grid/PSTF
adapters, numerical parity, directional physical face, provider export, or
`PASS_REC_PHYSICAL_SPLIT`.
