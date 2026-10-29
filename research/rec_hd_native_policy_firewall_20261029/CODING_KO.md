# REC HD native policy firewall | C1–C10 code/evidence report

**Parent** PR156 frozen `8806a4f757d916b6cf040625be931a66e2f0f6fe`. This module lives in an isolated research path and is NOT wired into REC production.

## Actual scope

C1–C2: Independent source/state/spectroscopy/production contract and exact real 35 Hz gate; found previously unlisted actual REC research HD consumer at `research/program_expansion_20261025/hd_adapter/lamda_hd.py`, Git blob `632a8a094e7eedd24a1ec3132fec20765d6e39da`.

C3–C4: Source-qualified opt-in wrapper, not a modification of the owner file. `load_pinned_adapter` validates Git blob, then dynamic import. `strict_bridge` rechecks module SHA1, authenticates the REAL `HDDataset` class, `source_roundtrip()` raw 2289 bytes SHA256, and invokes owner's real `require_energy_frequency_bridge`. The lower-level `_strict_bridge_core` accepts synthetic fixtures ONLY for test instrumentation and must never be used as a production entrypoint.

C5: `source_policy_firewall.py`, independent synthetic exact ratios, independent covariance-free SD bounds, frozen 8-line public test inputs. `generate_result.py` produces precision JSON and PNG.

C6: 19/19 new synthetic Python unittest PASS normal and -O, compileall PASS; intentional tamper tests reject source SHA label alone, module mismatch, wrong raw, bogus class, line IDs, bad inputs, owner-gate disagreement. No original source bytes/adapter are distributed publicly.

C7: Actual owner's module content read by exact Git blob and mapped to equations, independent exact Wolfram output confirmed. **Actual private LAMDA+owner-module runtime invocation NOT_RUN**, because true private source file and fully cloned source code were not mounted in the isolated run. Do not report physical/integration PASS.

C8: 7 synthetic J2 perturbations ±10 kHz, ±100 kHz, ±1 MHz and 0, exact rational ratios and visually inspected PNG plot. No production runtime benchmark; no numerical reference to physical data. Maturity PARTIAL.

C9: No native subagent or different-author reviewer was exposed. `NOT_RUN`.

C10: Git/backup and copyable handoff metadata are recorded separately on successful remote calls. The 35 Hz original source gate remains FAIL7/8; there is no automatic runtime activation or CDMS v3 substitution.

## Reproduction (source-free synthetic tests)

```bash
python3 -m unittest discover -s tests -v
python3 -O -m unittest discover -s tests -v
python3 -m compileall -q source_policy_firewall.py generate_result.py tests
python3 generate_result.py
```

## Real owner-callsite reproduction (private owner, still NOT_RUN here)

The owner must obtain private immutable HD original bytes and the original pinned module file without changing either:

```python
from source_policy_firewall import load_pinned_adapter,guarded_line_coefficients
owner=load_pinned_adapter('research/program_expansion_20261025/hd_adapter/lamda_hd.py')
state=owner.load_hd('/private/hd.dat')
result=guarded_line_coefficients(owner,state,1,1.0,0.01,1e-10)
# 2..8 must fail the original frozen bridge; do not enable production.
```

**Threat model/limitations:** Neither labels nor file names prove source identity; byte checks do. The opt-in wrapper cannot certify which other callers bypass it. Signature of original CDMS v2 and covariance is still missing. Code-replay and source choice are distinct scientific claims.
