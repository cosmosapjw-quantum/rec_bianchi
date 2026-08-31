# REC-NEXT-03 nonauthoritative formal checks

Status: **NONAUTHORITATIVE** identity checks; physical authority and repository
implementation parity are both **NOT_ESTABLISHED**.

Before evidence-producing execution, a local Codex job may use
`scripts/provision_rec_next03_formal_toolchains.py --provision --allow-network`
to install the exact Lean lane into an external ELAN_HOME and materialize a
clean external mathlib workspace. This setup writes no repository file and is
not formal evidence. Evidence-producing local execution must then use
`scripts/run_rec_next03_formal_contracts.py --run-all`, a new/empty output
directory outside Git, the exact xAct archive, and the provisioned offline
mathlib
`v4.33.0` source workspace at commit
`db584cd6d46c92f209a44c0f1c829460d327499d`, and a distinct nonexistent Lean
rebuild path under the output directory. The runner clears inherited language
search paths, performs every external tool command through its verified Linux
user+network namespace, discards prebuilt Lean artifacts in the output-only
copy, rebuilds without network access, and parses the exact 25 Lean and 25
Rocq assumption audits. Namespace verification compares the child
network-namespace inode with its parent, checks live socket interfaces for
loopback only, and rejects non-loopback routes; an inherited `/sys` mount is
diagnostic only. An unavailable or denied namespace is an `ENVIRONMENT_GAP`,
never a fallback to unsandboxed execution.

The exact command and environment contract is in the stage
`LOCAL_EXECUTION_PROMPT.md`. The direct commands below are developer
diagnostics only; by themselves they are not a formal-run receipt.

If another local job temporarily occupies the Wolfram license, the isolated
runner treats only an observed license/activation availability message as an
external capacity boundary. It records the attempts, waits at most 3600 seconds
in 30-second polls, and then resumes the Wolfram backend. It does not activate,
relicense, install, or terminate any Wolfram job. A deadline expiry is
`ENVIRONMENT_GAP`; a non-license Wolfram proof failure remains `FAIL`.

Run with Wolfram Engine and xAct/xTensor:

```bash
wolframscript -file formal/rec_next03/wolfram/verify_frame_face_event.wls \
  --output /tmp/rec-next03-wolfram.json
```

Run the exact rational Sage/libSingular verifier without writing repository files:

```bash
sage formal/rec_next03/sage/verify_remap_event.sage > /tmp/rec-next03-sage.json
```

The Sage command uses exact `QQ` arithmetic and Sage's bundled libSingular. It
emits exactly one JSON object on standard output and does not install packages or
write repository files. Its remap convention is photon content `N=m f`, with
`1^T P=1^T` and `P m_old=m_new` kept as distinct proposed obligations.
The JSON keeps repository `source_claim_inputs` separate from
`independent_math_obligations`.

Both scripts check proposed formulae but remain **NONAUTHORITATIVE**. Exit status
zero only means the encoded identities held; it does not establish repository
implementation parity, source bytes, ownership, physical authority, or production
readiness. In particular, these remain unproved authority firewalls:

- signed original-HyRec `Delta_f` versus nonnegative total occupation `f`;
- integrated two-photon/Raman packet rates versus deposited occupation rates.

`R_H=0`, `v_red=0`, and `v_blue=0` are separate event surfaces. Common exit codes
are `0` identities held without authority promotion, `1` failed identity, `69`
unavailable formal runtime/package, and `70` internal failure. Wolfram additionally
uses `2` for an output-argument error. A missing executable returns shell status `127`.
