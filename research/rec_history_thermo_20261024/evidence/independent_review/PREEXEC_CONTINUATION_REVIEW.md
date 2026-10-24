# Same-reviewer targeted continuation review

Reviewer `/root/thermo_independent_review`, continuing R6 without a new review
loop. Requested Astra/high; actual model identity unobserved. No scientific
probe, import, solve, native execution or replay was performed by the reviewer.

## Observed failure and attained evidence

The preserved primary exception identifies default JSON serialization of a
NumPy boolean at `BACKWARD_RESIDUALS.json`, after 13 large RHS. The reviewed
`backward` implementation compares against NumPy-scalar EPS, permitting this
boolean scalar type in its returned dictionary. This is a serialization failure
and does not itself establish C acceptance or rejection. Original A/B JSON and
saved C residual/gross arrays exist; D/E/F had not been reached.

Direct inspection of attained A/B JSON confirms all named A blocks and
structural zeros pass. The largest A normalized residual is
1.5551741193678365e-10 (sv); outgoing at stored X0 is
7.710416008469986e-16 and F is 4.56984849489973e-13.
The largest B comparison residual is 1.6263934969885847e-11 (lnTR real source
sr/s); the largest output comparison is R_gamma lnH at
5.199550630273307e-12. These are recorded results, not rerun evaluations.

## Two-file static delta review

Read `repair/continuation.py` and `repair/run_continuation_bounded.py` in full,
against `evidence/ROOT_SERIALIZATION_CONTINUATION_DECISION.md`.

- JSON conversion is narrowly limited to `np.generic.item()` and retains
  `allow_nan=False`; unsupported objects still fail.
- C uses the saved residual/gross arrays with unchanged 1024-epsilon and exact
  zero-gross criteria; it performs no residual or source solve replay.
- D consumes saved coefficient/output columns and performs the previously
  unreached direct pure-H restricted seed build with saved X and combined dX.
  The frozen 512-epsilon and separate complex comparison criteria remain.
- Only the mixed finite-difference stage invokes the continuation's large
  solver. The hard local count is 12 and cumulative count 13+12 is at most 25.
  Directions, steps, ownership checks and the 2e-5 criterion are unchanged.
- F calls the previously reviewed independent Cramer/escape/refusal controls,
  which were not reached by the original invocation.
- Importing original primary helpers does not execute `main`; no base, six-axis
  tangent or complex solve is replayed.
- The launcher checks the original 23-file snapshot and binds all original
  primary files plus continuation code before and after execution. Results
  are written in the new continuation directory, and the original failed
  invocation remains explicitly failed in aggregate reporting.
- Limits are 10 inclusive CPU seconds, 30 execution-wall seconds, one thread,
  and 1 GiB address space. Child hard-limit inheritance and full parent/child
  accounting follow the reviewed launcher correction.
- The final added REPORTED_VALUES projection and diagnostic counts/maxima
  read already-loaded arrays or recorded diagnostics only. Scalar arrays are
  explicitly converted with item(), and derivative arrays with tolist(). No
  extra source evaluation, solve or acceptance change is introduced.

## Final reviewed file identities

| File | Bytes | SHA256 |
|---|---:|---|
| repair/continuation.py | 13277 | 9fb48a5617cdb7153359fff4323e8e67f7bacd73b10386fb67f353b891cc2a1d |
| repair/run_continuation_bounded.py | 6042 | a1177bb963a7508e3fede361534b3434b44ea4b06764e10944e867979dd765bb |

## Decision

No material static blocker found in the targeted continuation. Root retains
RUN_READY and final admission. The numerical C/D/E/F outcomes and first two
PNGs remain pending; this review changes no tolerance, model, claim boundary,
or scientific budget. H5 uncertainty inputs and full coupled H7 remain open.
