# BASS–REC Source R5D Trusted RF-00 Payload Gate

This REC-side handoff closes the exact blocker exposed by the local R5B run. The source protocol, environment provisioning, JAX/native imports, focused eleven-test contract, and two-process canonical payload hash all passed. The backend cone failed because the freshly built wheel was not an admitted BASS RF-00 payload.

## Exact failed R5B evidence

```text
BASS source candidate
fc4d21b92a1abd1e9b35178f7d666831fc5c827d

local rebuilt wheel SHA-256
bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609

focused source protocol
11/11 PASS

canonical source payload hash, two processes
ca3807fa4ef49b5292bd65fd80b6fe9947c1cef7f835979122bff572900eb906

backend disposition
UnverifiedNativePayloadError
installed_wheel_or_manifest_does_not_match_trusted_payload
```

## Trusted payload selected for the next critical gate

The runner recovers the immutable RF04 scalar-raw/RF02C wheel directly from BASS Git history:

```text
BASS commit
50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda

path
artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/rf02c-wheel/
bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl

wheel SHA-256
99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302

shared-object SHA-256
5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633
```

## Run

The command may be launched from `rec_bianchi` or any other directory:

```bash
bash research/handoffs/rec_source_r5d_20260903/R5D_TRUSTED_RF00_PAYLOAD_GATE.sh
```

When BASS is stored elsewhere:

```bash
BASS_REPO=/absolute/path/to/bass \
bash research/handoffs/rec_source_r5d_20260903/R5D_TRUSTED_RF00_PAYLOAD_GATE.sh
```

The runner:

1. verifies the local BASS origin;
2. fetches the exact candidate and trusted artifact branches;
3. creates a detached candidate worktree and isolated Python 3.12 venv;
4. installs the exact Python-oracle lock;
5. extracts and verifies the trusted wheel from Git bytes;
6. installs the trusted wheel with `BASS_ALLOW_UNVERIFIED_NATIVE_DEV` unset;
7. verifies the installed shared-object hash;
8. reruns the focused protocol, two-process source payload hash, and backend cone;
9. writes durable logs and checksums under `~/Dropbox/bianchi/_runtime_receipts`;
10. leaves the caller checkout unchanged.

## Pass condition

Only this terminal classification opens the R6 hardening RED:

```text
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

A behavior-only run under `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` is useful as an optional diagnostic but has `authority_effect=NONE` and cannot open R6.

## Claim boundary

```text
NO_REC_SOURCE_INTEGRATION
NO_GRID_PSTF_NUMERICAL_PARITY
NO_SOURCE_IDENTICAL_PHYSICAL_FACE
NO_PROVIDER_EXPORT
NO_PASS_REC_PHYSICAL_SPLIT
NO_PASS_RF04
NO_MERGE_OR_READY_TRANSITION
```
