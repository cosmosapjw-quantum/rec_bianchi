# Independent R3T-U4A Review 001

Reviewer: Astra-tier read-only PHYS-MATH/CODE reviewer, not an implementer.
Initial decision: `HOLD_REPAIR_REQUIRED`; no NCP execution admitted. The
original findings below are preserved as the first review record.

The review confirmed the normal-path h/4 clock (`DLNA=8.49e-5/4`), source
origin 72892, restart endpoint 74411, prefix length 1519, causal column
ownership, original `/2./delta` operation order, next-node redshift/Tm update,
Schur gate and species ledger. The reviewed implementation identities were:

- `primordial_2012_quarter_u4a.py`: `c3a880c1ebb2c0f3c5d5ff4030451ea9a7a6febf0c747dcc4ab2b4312600ec9e`
- `verify_r3t_u4a.py`: `79e452677764ac409deff18581c971e2f5845878a9bcb57f1ab79354d18be88e`
- `test_primordial_2012_quarter_u4a.py`: `13e6ee31426337cc071f2776e80b9cb447552330f4210e6690703deed1b27cb2`

## Blocking findings

1. **F1, P1 implementation:** the runner passed the primitive rate table to a
   callback that reads `.energy_eV`; it also selected an R3O harness build
   that does not export the R3Q shared oracle symbol. The actual common-input
   spectral callback could not run.
2. **F2, P1 numerical verification gap:** common-input atomic RHS/photon
   equality and Python one-shot/split equality do not independently verify
   the U4 update equation. A sign or correction error in the Python post-Saha
   update could pass both. Add a same-checkpoint native restart call to the
   original `rec_get_xe_next1_H` and compare accepted states, predictor,
   post-Saha flags, RHS and committed spectra under the frozen same-h gates.
3. **F3, P1 resource contract:** independent parent and child CPU limits do
   not cap their cumulative process-tree CPU. The `--supervised` flag does
   not establish a supervisor, final over-budget output is not rejected, and
   signal termination may leave no terminal receipt. Add actual cumulative
   accounting/enforcement, wall timeout and descendant cleanup; keep 2 GiB
   per process.
4. **F4, P1 evidence/restart:** no accepted state/predictor/photon arrays or
   raw accepted rows were retained on PASS or partial failure. Flush accepted
   rows and checkpoint prefixes as the run advances; exclude probe/scratch
   data.
5. **F5, P2 restart boundary:** the integrator can enter ODE after a
   post-Saha exit but rejects a valid `post_saha=false` restart checkpoint.
   Allow this state and preserve exact event index/type; test the off branch
   and a split at the event.
6. **F6, P2 scope:** accepted-step limit is per call. Repeated restart can
   extend the task beyond index 74443. Enforce the cumulative endpoint cap.

The independent reviewer also found the full R3R stream parser is fixed to
initial-event framing and cannot be applied to this U4-only stream. Reuse only
its validated NumPy spectral-lane arithmetic/guard with a dedicated U4
framing; do not synthesize control or prefix rows.

Repair all findings as one bounded lower-tier change. Do not alter archived
HyRec source, equations, tolerances, prior allocations, original terminal
HOLD, or scientific claim ceiling. Preserve this first review and obtain a
new independent review of the repaired code before NCP execution.

## Review 002 addendum (2026-10-21)

Decision: `PASS_SCOPED`; one bounded 16- or 32-step NCP launch admitted.

This fresh read-only review was limited to the terminal systemd accounting
repair and current allocation gate. It verified the observed NCP terminal
snapshot (`ControlGroup=`, `MemoryCurrent=[not set]`,
`MemoryPeak=[not set]`, `CPUUsageNSec=[not set]`, `ActiveState=inactive`),
the `REMOVED` cgroup branch, worker CPU receipt checks against the last active
cgroup counter, and fail-closed behavior for absent, invalid, over-limit, or
underreported CPU receipts. The RUSAGE value is explicitly scoped from the
worker's measurement baseline through its finally block; it excludes Python
imports/bootstrap and is not represented as process lifetime CPU.

Reviewed SHA256:

- `scripts/run_r3t_u4a_supervised.py`:
  `9395e69b02ac53c10cc8d8107acc606c3ffe4be620690d589c22e56698077106`
- `scripts/verify_r3t_u4a.py`:
  `3df40476ddec9bb145af7f32bb73d741cc3bce2969342c4c05bf7fda63b7e628`
- `tests/trajectory/test_r3t_u4a_supervisor.py`:
  `f4336f6999f3a9e6b336b097029e08f9c1f7ff392d551e63b21c163e31ded838`

Evidence: **17 passed, exit 0**, stderr empty; stdout SHA256
`346950c20b827b9579236acefba8252f98c083f9896d87c93c94348b8b501753`.
Approval is for a single fresh allocation bounded at 60 CPU seconds, 180
wall seconds and 2 GiB per process. It does not approve a relaunch after CAP,
reset historical accounting, or alter the scientific claim ceiling.
