# KS01 independent pre-execution code review

Final current verdict: **PASS_RUN_READY**. See final closure and exact fingerprint below; earlier FIX_BEFORE_RUN entries are preserved historical findings.

Scope: static review only; reviewer did not execute scientific code or modify implementation.
Reviewed retained source mapping, interval certifier, actual-history admission, immutable-input verification, controls and resource driver.
Same review session as PREEXEC_REVIEW.md. No new literature search or reviewer recursion.

## Initial snapshot and concrete findings

Initial primary.py SHA256: 0f9e155cf2cdc6cc85adc7ce5b7e474bdef5e39de352e3534e52ad4619dadcca.
Initial tests/manufactured.py SHA256: 94e1050d8ed4acefa4919804e1ffa8f0530dca6e4bcccb8fce1bea0deb887dbc.
Initial inputs/EXACT_IDENTITIES.json SHA256: 3f4d1e3fc8c3364300ce84fa211fb1acbdbea7c0375cebcef77f1fbee925f1bf.

Initial verdict: **FIX_BEFORE_RUN** for the following two implementation/accounting issues.

1. Small RHS accounting omitted exact Fraction RHS. Two manufactured cases of dimensions2 and3 used np.linalg.solve for both V and Z, totaling10 numerical RHS, plus exact_solve(M,B) with another5 rational RHS. The frozen cap12 therefore requires a correction. Root accepted the minimal remedy Z=solve(M,I), V=Z@B, with exact B solves counted:5 numerical+5 exact=10 total. This changes only the candidate used in the existing manufactured certificate check; it adds no new controls or physical tolerance changes.
2. Completed endpoint evidence was retained only in memory until all affine/joint controls finished. A later exception or CPU kill would lose prior completed endpoints. The same issue affected manufactured partial case reports/counts on an assertion failure. Root accepted per-endpoint NPZ, per-pair JSON and incremental small-RHS/case accounting. These writes add no solve or science replay.

The root authorized one bounded pre-execution correction by the same implementer, preserving the original snapshot/diff and regenerating the exact manifest. This reviewer will inspect only that corrective diff and close these findings in this same report.

## Static checks already completed

- certificate.py uses outward elementary point_dot for ZM, MV, |Z||R| and TV. The rho, positive denominator, column error, |T| row sums and final interval widening implement the reviewed proof. No BLAS residual enters the interval proof. Nonfinite endpoints refuse.
- Represented Vhat/Khat are distinct from certified real-algebra intervals. The positive beta/H ionization response, Ly-alpha incident subtraction and opposite energy sign are implemented consistently.
- common.verify validates every retained source_snapshot member against its retained23 identity map, checks the canonical snapshot token, then checks every current input/source against EXACT_IDENTITIES. The retained loader independently verifies its existing input manifest before parsing data. No science solve precedes this chain.
- Fresh source build compares M,s,T,P,p,Tvv,Beta with stored stable arrays and exits before any solve on numerical-array inequality. This compares binary64 numeric values using array_equal; source/input byte identity is separately hash-checked.
- history_admission binds the exact35MB payload hash and size, raw C-order f64 members, immutable energy grid and source hashes. It checks strict eta ordering/grid, indices0..7488, original scalar frame/parameter chain, all313 native channel owners and query times. It uses outgoing_virtual/outgoing_lyman rather than average_virtual.
- Source routing includes virtual139->alpha, virtual270->beta, virtual310->gamma, alpha->virtual140 and beta->virtual271. Only prefix0..5126 is used; latest knot/future refuse and earlier-than-start uses the explicit thermal-zero branch.
- History arrays do not encode cosmology; the exported admission correctly labels its parameter evidence as the retained input.dat/producer chain plus scalar-density consistency. No physical epsilon is manufactured.
- endpoint() uses stable source.build with the original branch/stencil ownership for every affine and joint perturbation. It does not import native code, recalculate six old theta derivatives or integrate a trajectory.
- Primary large RHS count639 agrees with313(V)+313(Z)+1base+4affine+8joint and is checked before each solve. The wrapper sets single-thread environment and CPU45s/address-space1GiB/core0 limits before child execution, enforces135s wall timeout, preserves stdout/stderr, and refuses attempt/result path reuse.
- Existing manufactured controls use exact rational references and exercise nonsymmetric systems, nontrivial T/P, cancellation, rho failure, nonfinite inputs, negative epsilon, zero/synthetic boxes and current basic-arithmetic/subnormal behavior.
- README resolves the prior box.lower interpretation and actual provenance location. It explicitly distinguishes numerical Js, certified represented Ks and absent physical history uncertainty.
- figures.py reads saved outputs only and does not execute the scientific source. Actual PNG inspection remains a postrun obligation.

## Corrective diff review

Inspected evidence/preexec_before_fix/primary.py.diff, manufactured.py.diff and CORRECTION_RECEIPT.json in this same session. Corrected identities:

- primary.py: 26320226fa1e9a981c124fb0583f63e616cc2def801472023d23d9d1b9d46297.
- tests/manufactured.py: e8cf49487937466c6de4f79d930bdb44bd7f774ddb190ff59660e22c9a1c37ad.
- inputs/EXACT_IDENTITIES.json: 3de40851043a70d6c6a89315b85aa1807879a1625db2bca457b2206a0807199b.

Finding1 CLOSED: candidate V=Z@B removes the extra five numerical RHS. Numeric5+Fraction5=10 are separately charged before solve, enforcing the existing12small RHS cap. Manufactured progress and completed case evidence now survive a later assertion failure.

Finding2 endpoint/pair portion CLOSED: every base/affine/joint endpoint writes its own NPZ before returning and every completed pair writes its own JSON immediately. These changes add no solve or physical acceptance change.

One remaining location of Finding2: V,Z,K are currently written to APPROXIMATE_RESPONSE.npz only after certify() returns. A CPU limit or interval arithmetic exception during certify() can therefore lose the already completed626large-RHS candidates. Move the approximate-response write to immediately before certify(), recording RHS_USAGE at that milestone. This is the same partial-result preservation correction, adds zero solves, and does not alter theory or tolerance.

Intermediate readiness was **FIX_BEFORE_RUN** only for that remaining serialization placement. No other new finding was raised. It is closed by the final diff below.

## Final closure — 2026-10-25T02:13:49Z

Final verdict: **PASS_RUN_READY** for the exact prepared snapshot below. This is code readiness, not a scientific run PASS or a substitute for root execution authorization.

The final candidate_preservation.diff and CANDIDATE_PRESERVATION_RECEIPT.json were read in this same review session. V is now saved immediately after313RHS, Z immediately after626RHS, and the joint V/Z/K candidate file is saved before certify(). RHS_USAGE is updated at both solve milestones. This closes the remaining portion of Finding2. Finding1 and the endpoint/pair/manufactured portions remain closed. No new solve, model choice or tolerance change was introduced.

Final reviewed fingerprint:

- code/primary.py: 4f70551253935117da5dbbc18f52c4db56293d16bd51bb4c137ab4eed4c6ac33.
- tests/manufactured.py: e8cf49487937466c6de4f79d930bdb44bd7f774ddb190ff59660e22c9a1c37ad.
- inputs/EXACT_IDENTITIES.json: 77522e3a93cf75dac9f364071c567a51b4d2b11e6abb769a66a64b2020a206e8.

The current manifest entries for both changed source files match these fingerprints. All reported scientific, implementation and accounting findings from this pre-execution review are closed within their frozen scope. The plan remains639large RHS and10small RHS(numeric5+Fraction5), within the original12small cap. Root may issue its RUN_READY after its S1 delivery requirements; this reviewer has issued no execution token.

Reviewer scientific execution0; implementation edits0. Actual scientific results and rendered PNGs await the same reviewer's postrun assessment.


