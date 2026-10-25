# REC-HISTORY-KS01 executable projection

The root owns scientific equations, tolerance changes and execution authorization.
These modules are a mechanical implementation of FROZEN_CONTRACT.md.

Preparation (hashing and syntax only): `python code/prepare_snapshot.py`.
Execution requires `evidence/RUN_READY.json` with `authorization: RUN_READY` and
uses `python code/run_bounded.py`. It refuses any existing attempt/result path.
The scientific child has 45 CPU seconds / 135 wall seconds, 1 GiB address space,
one BLAS thread, 639 large RHS and 12 small RHS hard ceilings. There is no retry.
Raw stderr/stdout, partial arrays, exceptions, byte hashes and resource receipts
remain on any failure. Reserved repair is not authorized by this implementation.

Each command accepts explicit `--thermo`, `--history`, `--query-map` paths.
The default THERMO source is the previous sibling research unit in a full repo,
otherwise the restored archive under `inputs/thermo_s2/`. History and query map
have restored-input defaults; pass their paths when using another archive layout.
No native module is imported, no old derivatives are recalculated, and no IVP is
integrated. The interval module is byte-identical to retained RESP01 interval.py;
certificate.py contains its generic certify function without native ownership.

The exact identities manifest covers all 23 prior canonical source/input members,
the retained loader subset, reused results and provenance, actual payload, query
map, and every new Python source. Every identity is checked before any solve.
The canonical 23 inputs are separately checked against their original snapshot.
At run time a real stable base build must reproduce stored M,s,T,P,p,Tvv,Beta
exactly. A difference refuses the run before solving.

`conditional_box.lower` is a lower bound on the *worst-case box gain* (a weighted
row sum of exact absolute coefficients); it is not a lower bound on every actual
output perturbation. The API's absent epsilon yields null bound and physical
epsilon remains null. Any epsilon in manufactured controls is synthetic only.

Ionization, number and energy interval coefficients certify exact real algebra
on represented binary64 coefficients/constants. Stored Js remains a separately
numerically checked derivative. Atomic energy is the exact sign partner of the
same radiation event. Their cancellation does not establish global energy closure.
The original payload contains no cosmological parameter block: parameters are
bound by retained input.dat/producer provenance and local scalar FLRW consistency.
Admission is a same-h prefix reconstruction, not a physical history error bound.

Figures: `python code/figures.py --results results/primary001 --out results/figures001`.
This reads saved outputs only. Root and independent reviewer must view both PNGs.
The first generated files must remain unchanged. Figure resource accounting is
owned by root under the separate 10 CPU / 30 wall figure-and-scalar allowance.
