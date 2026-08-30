# rec_bianchi research followthrough R2

This package repairs a publication-graph gap, not a scientific result. The
context/deposition component branch in PR #36 is the base. A later one-file
moving-deposition/input-binding helper had been pushed from PR #34 on a
separate branch with no tests or PR; its exact source bytes are preserved here
with focused tests and an explicit local continuation contract.

The helper is additive. It does not replace `COMSourceDepositionPlan`, identify
a physical source map, or turn the eight native proxy values into COM
occupation. Current claim: `NO_PASS_REC_PHYSICAL_SPLIT`.

Run:

```bash
sha256sum -c research/continuation_20260830/MANIFEST.sha256
python3 research/continuation_20260830/verify_payload.py --root . --repo .
python3 -m pytest -q research/continuation_20260830/tests/test_physical_inputs.py
```
