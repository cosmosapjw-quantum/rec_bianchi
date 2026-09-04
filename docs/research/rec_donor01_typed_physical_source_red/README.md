# REC-DONOR-01 — typed physical source authority expected RED

## Status

```text
phase                         TEST-FIRST CONTRACT
base                          926e0c79a3fe7c3f5b24d5c5bb81304332def232
base tree                     ce0654041d097768fae4f6a52b23c2137558f7be
future production module      src/full_bianchi_hyrec/physical_source_authority.py
future production module      DELIBERATELY ABSENT
expected test result          16 tests / 13 assertion failures / 3 controls
claim effect                  NONE — CONTRACT ONLY
```

This stage opens the representation-neutral primordial-recombination donor lane
identified by FED-02.  It does not create a physical source, a 26-direction
face, a BASS state adapter, a recombination provider, or a scientific result.

The future owner must distinguish:

1. a local bosonic affine occupation source
   `C[f]=eta(1+f)-kappa f`, with nonnegative primary `eta` and `kappa`;
2. nonlocal two-photon and Raman photon-packet kernels;
3. packet-to-occupation deposition, applied under a separately identified
   measure and normalization exactly once;
4. source identity from any angular representation used by a consumer;
5. physical atomic/source-frame quantities from downstream local-observer
   boosts.

The source contract also binds physical seconds, photon energy in joules,
source/data provenance, background-trajectory identity, event surface,
restart certificate, and an analytic JVP or an explicit fail-closed no-JVP
status.

## Local expected-RED command

Run only in a clean isolated worktree at the exact branch head and keep output
outside Git:

```bash
out="/tmp/REC_DONOR01_EXPECTED_RED_$(date -u +%Y%m%dT%H%M%SZ)"
python3 scripts/run_rec_donor01_typed_physical_source_red.py \
  --repo-root "$PWD" \
  --output-dir "$out"
```

The sole successful wrapper classification is:

```text
PASS_EXPECTED_REC_DONOR01_TYPED_PHYSICAL_SOURCE_RED
```

A wrapper pass means only that the implementation is absent in the intended,
fully classified way.  It is not source authority or physical validation.

## Next node

After the exact RED has been observed and read back:

```text
REC-DONOR-02_MINIMAL_REPRESENTATION_NEUTRAL_SOURCE_GREEN
```

That GREEN may add only the standard-library physical-source authority module
needed by this test contract.  It must not add an angular face, solver-loop
wiring, BASS background coupling, REI import, observer boost, provider export,
or claim promotion.
