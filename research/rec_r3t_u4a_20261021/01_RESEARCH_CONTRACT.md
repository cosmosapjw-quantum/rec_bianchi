# R3T-U4A Research Contract

Status: frozen contract; bounded execution admitted by independent scoped
PHYS-MATH/CODE review on 2026-10-21 after repair of systemd terminal accounting.

- New allocation: `REC_R3T_U4A_NCP_20261021_001`
- Hard bounds: 60 process-tree CPU seconds, 180 wall seconds, 2 GiB address
  space per process; supervisor initiates termination at 50 CPU / 150 wall s.
- The independent reviewer approved one 16- or 32-step execution only. No
  automatic relaunch or scientific HOLD reset is authorized.

## Question and scope

Can the existing h/4 HyRec2012 H-only history be restarted at its actually
accepted source index 74411, including its two-entry H predictor memory and
accepted photon/causal prefix, and advanced through a separately bounded
16- or 32-step interval with the original source operator and same-h common
input reference checks? This node validates only that restart path and bounded
interval. It does not claim U4 exit, U5/U6 completion, convergence, physical
validity, or production readiness.

## Frozen identities

- Base metadata/implementation HEAD: `8737bdad851e53a8c78c484f1153b8e0dd455927`
- Base tree: `6a0069d5f1a7f13d2e799d5c14d83ae92d5a318f`
- R3S five-job execution source (historical): `52f884b7b27814f808b9b4f7fd5ac9a3c6283e32`
- R3S post-run adapter publication (historical): `aefee2cf62ba089c4a520b5a772f3b3614b5fdb5`
- R3Q h4 source archive: `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`
- h4 initial checkpoint SHA256: `40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef`
- R3Q accepted event+2 checkpoint: `research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz`, SHA256 `7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9`
- R3Q source closure: `research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json`, SHA256 `0332531f65a2851119f50806cdf7bc384b494b09759fcf5d497d6c1a7d032bcf`

## Restart contract

The source-owned global clock is h/4 with `DLNA = 8.49e-5/4`,
`izH0 = 72892`, and `z(iz)=8001*exp(-DLNA*iz)-1`. Reuse the accepted R3Q
endpoint at `iz=74411`, which is `H_ONLY`, `xHeII=0`, `post_saha=true`.
Restart state includes the complete endpoint species/temperature state;
the two accepted H RHS values at input indices 74409 and 74410; and the
accepted `virtual_out`, `average_virtual`, and `lyman_out` columns owned by
indices 72892..74410 (1519 columns). The next accepted RHS input is global
index 74411 and owns photon column `74411-72892=1519`. No history column may
be duplicated, omitted, synthesized, or read before its accepted write.
The event+2 R3S pre-event smoke output is not a restart source.

The H-only accepted update preserves original `history.c` ordering: evaluate
the current FULL source at the accepted input; commit that input's photon
column; compute the next species state with the existing post-Saha helper
when active, otherwise `xe_next = xe + DLNA*(1.25*f_current - 0.25*f_prev2)`;
compute steady-state `Tm` at the indexed output redshift; then shift predictor
memory only after acceptance. The post-Saha Jacobian keeps source operation
order `(fp-fm)/2./delta`. The helium predictor row is retained as historical
memory but is not advanced in H_ONLY.

At each accepted input, preserve both original stage guards: the H-only thermal
loop continues only while `1 - Tm/[T0*(1+z)] < DLNT_MAX` with
`DLNT_MAX=5e-4`; the FULL source branch continues only while
`iz-izH0 < nzrt`, where `nzrt` is computed on the h/4 clock from the original
RT setup. A guard must be checked before any current source evaluation or
photon write. A cap ending before either physical boundary is a bounded
partial validation, not U4 completion.

The existing h/2 U4 implementation is equation/order reference only. Its
h/2 global indices, checkpoint, RT-stop clock, prefix sizing, and source
identity are not reusable for h/4. The h/4 runner must use its own frozen
checkpoint SHA/index, clock, causal prefix, and C oracle. Reuse the validated
R3R NumPy atomic/spectral audit components under their existing tolerances;
do not call the R3R full-stream parser on this U4-only stream or fabricate
earlier event/prefix records.

## New allocation and acceptance

Register a new allocation independent of R3S/historical U5 accounting,
bounded by 60 CPU seconds, 180 wall seconds, and 2 GiB per process. The
bounded runner may request at most 32 accepted steps from index 74411 (thus
at most output index 74443) and at most 128 FULL evaluations for a single
trajectory. Do not enlarge this by changing an old 1..32-step launcher.
Record setup/compile separately from integration and audit. If any hard cap is
reached, preserve first failure and classify `CAP/HOLD`; do not relaunch under
a replacement allocation.

Acceptance requires: immutable input/source checks; actual recovery of the
R3Q checkpoint; h4 source/index/stage/predictor/history shape and finiteness
checks; common-input same-h C/Python comparisons at every tested FULL source
input with the existing contract (`|rhs_py-rhs_c|/max(1,|rhs_c|) <= 2e-10`;
each photon lane within `1e-7*max(|py|,|c|)+1e-10*f_bb`); restart split
16+16-versus-32 equality for accepted states, predictor and committed
histories; explicit tests that duplicate, missing, or uncommitted history is
rejected; and synthetic exact-boundary tests proving thermal/RT guards stop
before source evaluation. Same-h accepted-state comparisons retain the
existing `xe/xHII` relative tolerance `5e-9` with floor `1e-8`, `xH1s` same
comparison, `xHeII` absolute `5e-10`, `Tm` relative `5e-10` with floor 1,
`z` absolute `2e-12`, and exact index/post-Saha. Integrated H RHS remains
`2e-7`; Schur residual `2e-10`; species ledger `5e-13`. The event may not be
reached within 32 steps; then report `NO_EVENT_WITHIN_BOUND`, not a pass for
crossing. Raw evidence, argv, exits, hashes, resource observations and
cleanup evidence must be preserved.

## Adversarial review repair gate (closed for bounded execution)

Independent PHYS-MATH/CODE review found pre-execution blockers. Repair these
in the same bounded change before any NCP launch:

1. Pass the canonical two-photon energy table (not the primitive rate table)
   into the common-input spectrum observer, and load the shared C oracle
   symbol from the R3Q shared harness. A focused test must exercise the real
   callback once.
2. Compare the actual accepted U4 update against upstream
   `rec_get_xe_next1_H` from the same accepted checkpoint, predictor and
   photon prefix. This is a native restart comparison, not an independently
   reconstructed full native history. Compare accepted states, post-Saha
   flags, H RHS memory, and committed V/A/L columns at every tested node with
   the existing same-h limits above. Keep the C update adapter in a new
   harness; do not change archived upstream source or scientific tolerances.
3. Preserve every accepted row and the exact accepted checkpoint/prefix to
   create-only output after each accepted step, and preserve a final checkpoint
   and raw stream/evidence files on both PASS and bounded CAP/exception. A
   failed or post-Saha probe column must not enter the accepted checkpoint.
4. Enforce the complete new allocation's cumulative CPU budget across parent,
   compiler and all descendants, plus 180 wall seconds and per-process 2 GiB
   address-space limits. `--supervised` alone is not supervisor evidence.
   Retain process-tree cleanup and measured CPU/wall/RSS. If aggregate CPU
   cannot be enforced from the verified host, do not launch; record CAP/HOLD.
5. Permit a valid post-Saha-off accepted restart and continue with the original
   AB predictor; preserve exact event index/type. Enforce the cumulative
   `START_IZ..START_IZ+32` limit across split calls so restarting cannot reset
   the node cap. Add a controlled event/off-branch split test.
6. Report compile, integration, C oracle, Python audit, and total separately;
   account for all full evaluations. Record lanes/s and records/s only if raw
   I/O makes those measures meaningful; include bytes read/written or
   `NOT_MEASURED`.

The repairs do not alter equations, accepted tolerances, historical
allocations, or the claim ceiling. Independent review approved the exact
current supervisor/verifier/test identities recorded in
`INDEPENDENT_REVIEW_001.md`. The NCP host previously confirmed active-scope
CPU accounting and enforced memory scope; terminal scope removal is handled
by checking the worker's bounded `RUSAGE_CHILDREN` CPU receipt against the
last active cgroup observation. This measurement excludes import/bootstrap
before the worker baseline and must be reported with that scope.

## Claim ceiling and preserved state

Previously completed R3P, R3M full5210, R3Q h4 event+2, h2 low-z, R3R, and
R3S five-job campaign are reused without rerun. Keep original terminal HOLD
SHA `eaee72446c4f8b2e5ce8de52a8a508e88a3dfb34f3697b070db29af239006625`
unchanged; link scoped 5-job acceptance only by additive adjudication.
Preserve `U5 h=HOLD_9_FAIL`, `U5 h/2=HOLD_8_FAIL`,
`CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, global convergence
`NOT_RUN`, physical validity `HOLD`, and production readiness
`NOT_APPROVED`. No U4 exit or downstream gate can be inferred from a 32-step
bounded run.
