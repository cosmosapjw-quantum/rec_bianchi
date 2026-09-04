# R5D trusted RF-00 payload gate — current R6 source

This REC-owned handoff is the trusted-native companion to the completed BASS R6C behavior-level replay.

## Why the original gate was revised

The historical v1 runner was pinned to the R5 source protocol and schema-v1 payload hash. The current BASS source-authority implementation is the R6 GREEN source:

```text
source commit  92d67dc79cf645947beb93ac01a9505ee277dabd
source tree    65cb63e6d08e80e9a8f38f83e3a536cb0a00a693
source blob    869677390004f68aef9f547e6556f5f1c15bd012
```

The v2 gate therefore validates the stable R5 suite and R6 hardening suite together, the schema-v2 source and integrated-binding identities, a clean source worktree, and the current source against an admitted native payload. The historical v1 gate remains recoverable from the preceding Git commit.

## Closed behavior prerequisite

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
```

R6C used a source-built development payload and established behavior-level parent/GREEN equivalence only. It did not establish trusted production-native provenance.

## Trusted payload

```text
artifact commit
50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda

wheel SHA-256
99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302

installed shared-object SHA-256
5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633
```

The runner extracts the wheel directly from BASS Git history, installs it with `BASS_ALLOW_UNVERIFIED_NATIVE_DEV` unset, verifies the installed shared-object byte identity, builds the root Python package from an exact non-Git `git archive` stage, and reruns the current focused and backend cones.

## Run

From the REC checkout:

```bash
bash research/handoffs/rec_source_r5d_20260903/R5D_TRUSTED_RF00_PAYLOAD_GATE.sh
```

The script may be launched from any directory and locates BASS through `remote.origin.url`.

Expected terminal classification:

```text
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

R7 opens only under the conjunction:

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
AND
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

Neither result authorizes physical REC source wiring, grid/PSTF numerical parity, a physical directional face, provider export, `PASS_REC_PHYSICAL_SPLIT`, or `PASS_RF04`.
