# R3O independent implementation review — C9

Date: 2026-10-19 UTC. Review root: `/workspace/scratch/afe554957b2e/rec_work`.
Assigned baseline: PR108, `23e0a3a6c439a1f015aa8f7380f4eedf0b569df7`.
This root is a source capsule, not a Git checkout; the baseline is the supplied
parent identity, and the byte hashes below identify what was actually reviewed.

## Decision

**C9_COMPLETE_WITH_TWO_P2_FINDINGS. The retained h2 smoke, independent h4 start,
and original-h adapter receive a scoped numerical/provenance pass.**

No P0/P1 mismatch was found in the assigned equations, source operators, grid
ownership, accepted predictor memories, or retained same-h results. Two
reproducible defects remain in the h4 runner's resource handling. They affect
timeout containment and resource-limit admission; they do not invalidate the
successful `start_002` numerical evidence. Parent owns repairs and their
targeted checks, integration, push, and backups.

| Rank | Finding | Priority / current disposition | Affected claim |
|---|---|---|---|
| 1 | C9-P2-01: h4 subprocess timeout leaves a descendant running | P2 / FIX_SOON, current runner defect | Containment of the launched process tree |
| 2 | C9-P2-02: h4 finalization can exceed its allowance and still return PASS | P2 / FIX_SOON, current runner defect | Strict total CPU/wall resource admission |
| Closed | R6-P2-01: terminal restart with insufficient cubic states | CLOSED, independently rechecked | One/two remaining steps are explicitly incomplete; three supply the stencil |

The two P2s block certifying the corresponding resource guarantees. They do not
create a new prohibition on preserving or publishing the bounded scientific
result with those limitations stated. There is no request here to repeat
historical U4/U5/U6, run full h2/h4 histories, or start another independent review.

## 1. Ranked concrete findings

### C9-P2-01 — timeout terminates the direct subprocess but not its descendants

**Location:** `scripts/verify_r3o_h4_start.py`, `Budget.run`, line 217
(`subprocess.run(..., timeout=remaining_wall, preexec_fn=limits)`).

**Observed defect.** The subprocess is not put in its own process group/session,
and timeout handling delegates to `subprocess.run`. The direct process is killed,
but a process it launched survives. The actual compiler command is a driver that
can launch other programs, so this matters to the stated bounded runner.

**Independent control.** Command C below called the actual `Budget.run` with a
manufactured Python driver and one sleeping descendant. Output was captured in
anonymous RAM-backed file descriptors; no source or evidence directory was
written. With a 0.4-second wall allowance:

- The driver returned `-9` after `TimeoutExpired`.
- `start_new_session` was false.
- The descendant remained in Linux state `S` after the timeout returned.
- The reviewer explicitly killed that test descendant. Its PID was 7 in this
  command's isolated process namespace.

This is an actual process-containment counterexample, not a HyRec calculation,
a stalled compiler observed in `start_002`, or evidence that its numerical result
failed.

**Consequence and disposition.** A timed-out compiler descendant can continue
consuming the allocation or writing outputs while the parent is finalizing the
failure record. Its later work is not included in the parent's already returned
budget check. **P2 / FIX_SOON before relying on unattended h4 timeout containment.**
The successful retained start did not hit this path.

**Smallest repair.** Launch the subprocess in a new session, and on timeout or
exception terminate and wait for its process group while retaining the actual
command, exit/termination status, and stdout/stderr. The low-z runner already has
the relevant `Popen(start_new_session=True)` / `killpg` pattern at
`scripts/verify_r3o_lowz.py`, line 200. Reuse that bounded pattern rather than
introducing a new scheduler.

**Targeted closure check.** Use a short controlled driver with one descendant;
after timeout, no descendant may remain running and the failure receipt must
remain readable. A normal fast subprocess must still return successfully.
No physical history is needed for this repair.

### C9-P2-02 — finalization is outside h4's final admission check

**Location:** `scripts/verify_r3o_h4_start.py`, final work check at line 411,
PASS assignment at line 412, alarm cancellation at line 419, resource measurement
at line 431, and artifact hashing at line 435.

**Observed defect.** The last `budget.check()` occurs before the `finally`
block. Finalization disables the wall alarm, hashes dependencies and extracted
sources, measures resources, then hashes artifacts and writes the receipt.
Neither the measured final resources nor the later artifact work can change a
successful status to a resource failure.

**Independent control.** Command C executed the real `main()` through its
`finally` path in `helium` mode, replacing scientific work and I/O with
in-memory controls. Its synthetic accounting clock stayed below the cap until
the final input-hash read, then crossed it. The actual observed return was:

```json
{
  "main_returncode": 0,
  "reported_status": "PASS_SAME_H_HELIUM",
  "allowance_cpu_s": 1,
  "reported_cpu_s": 1.25
}
```

The CPU values in this counterexample are deliberately injected accounting
values, not a measured 1.25-second physical execution. The status/return-code
combination comes from the unmodified runner. Start and helium modes share this
finalization path.

**Consequence and disposition.** A receipt can visibly report a resource overrun
while retaining PASS; artifact hashing is additionally omitted from its current
resource snapshot. **P2 / FIX_SOON before admitting a strict total-resource
guarantee.** The actual retained h4 run used 3.335698 internal CPU seconds against
20 seconds, and its outer driver used 4.353667 CPU seconds, so the retained run
has ample margin and is not refuted by this control.

**Smallest repair.** Reserve a small amount of the existing allowance for
finalization, perform required input/source and artifact readback, then recompute
total CPU and wall usage before sealing admission. An exceeded total cap must
produce a non-PASS resource status and nonzero exit while preserving the minimal
receipt. The low-z runner already separates work/recovery limits and has a final
total-cap check; no change to the physical tolerances or equations is needed.

**Targeted closure check.** Inject accounting values just below the cap at the
last work check and above it during finalization. Require non-PASS/nonzero,
and retain an otherwise identical below-cap successful case. Test CPU and wall
admission without rerunning primordial integration.

## 2. Scope, instructions, and identity

### skill_context_used

Applied **physmath-research-loop 1.3.0** from the exact user-supplied installation:

`/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/`

| Read instruction | SHA256 |
|---|---|
| `SKILL.md` | `ccb300f5b871e7e9df2ce289bc4533f4121a335b36a3b67bfa86742ca930d3a5` |
| `references/POLICY_INTEGRATION.md` | `a844f7c6d30bc7075d81bde0595b023d2a824c71250f826ce364f9a54bfc1cd0` |
| `references/STAGE_GUIDE_KO.md`, selected C9 definition | `87e4a6a714b19c7791549c913b9898a8aadff27d24b2105aa654374139e80800` |
| `references/SUBAGENT_MODE.md` | `d84fc9c0e6c229e350f2855edff545ee9dac05cd7b7958b0b97e82b92bb0c48e` |
| `references/CODING_LOOP.md`, C9 contract | `b9e3d6217c243590683bee2ddfe5bb63293206c188b70137a6380e4765442c60` |

Behavioral application: C9 only; one independent pass; zero recursive delegations;
read-only implementation and shared inputs; explicit synthetic/physical separation;
reuse of completed evidence; closure of the resolved R6 finding; two finite,
reproducible findings with smallest repairs. No new no-go claim or scientific
target was introduced. This report is the only persistent reviewer output.

The theory note, R6 review and closure receipt were read, followed by the actual
run evidence and the completed h-input worker handoff:
`../rec_recovery/r3o_h_input_agent.md` and
`../rec_recovery/r3o_h_input_implementation.json`.
The provisional `EVIDENCE.json` and `DAG.json` were read as parent integration
state. They are not substitutes for the raw evidence below. Vigilode/Rust
implementation and extension artifacts were outside this assignment and were
not inspected.

### Audited implementation byte identities

All paths in this table are relative to the review root. These identities were
rechecked after the direct evidence readback and were stable at report intake.

| File | Actual SHA256 |
|---|---|
| `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py` | `6f6cdfa281fc893f80334e43418a130cdd7526be8e14d9575eed74dcbd7edee6` |
| `src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py` | `6247e0681d74e5b6f26f9818faf4a49af4ce61e64e4970bfe3b7c21ad951fd10` |
| `scripts/verify_r3o_lowz.py` | `192f6ba070f35d7cede83fc03a96757064844f517f9b6c5910c2d7d305ddb193` |
| `scripts/verify_r3o_h4_start.py` | `96e03f326342940606dba33dd44d8f172d5bb6a773dc15f404635babca6f4deb` |
| `scripts/c_harness/original_hyrec_r3o_lowz_harness.c` | `d179b07d33562557924f763b85a58f5a2cec48ec2a78c4ab39a6702d82e88756` |
| `scripts/c_harness/original_hyrec_r3o_h4_start_harness.c` | `8b50858c0e0a3d1e6eef19e9f159673156162f70a7363b51945a9f238aa2ec8a` |
| `scripts/prepare_r3o_h_history.py` | `c5a938c0b37cae5ff8b1ec05099bb420fd2da9a17e719ef047c9192c52224cad` |
| `scripts/plot_r3o_frontiers.py` | `e952d0ca8f290d66ca61a645979a43bbdda1db085c72e2b3bacd2337b6c1b500` |
| `tests/trajectory/test_r3o_lowz.py` | `05da1804d0cd1817030b27bb8b48d7c48b9f4085c38becfc278a7bcd72293893` |
| `tests/trajectory/test_r3o_h4_start.py` | `50dceee1c92e1ab3baa50c468955affac47c6639dcd3714a492e1bb542e43359` |
| `tests/trajectory/test_r3o_h_inputs.py` | `74004e931a004f313353fb92ee345519f9d358aab1b75c9363644dd2d6ca176d` |

### Immutable original source

The authoritative ZIP was opened directly and rehashed:
`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`,
SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

| Original member | Actual SHA256 |
|---|---|
| `HyRec/history.c` | `8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976` |
| `HyRec/hydrogen.c` | `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b` |
| `HyRec/helium.c` | `1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece` |
| `HyRec/hyrectools.c` | `beb97b6cee3b80cf74d58264da7087301865881d266de1c17dd472a08665bb79` |
| `HyRec/hyrec_params.h` | `cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2` |
| `HyRec/two_photon_tables.dat` | `93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9` |

Direct comparison checked all 19 expected h2 extraction files and all 26 h4
manifest members, including the latter archive metadata members. The only
modified scientific source member is `hyrec_params.h`, with the literal DLNA
substitution. Compiled-header hashes are
`e83d8031975c0a64cdb45a2b8ba03a4a0a75c85fac5cf2437aadc915e25751bf` (h2) and
`46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f` (h4).
The 52 low-z receipt source entries and 13 h4 producer/dependency entries all
match current files. This is dependency identity checking, not a claim to have
independently reviewed every line of all those dependencies.

## 3. Passed implementation contracts

### h2 continuation and the closed R6 terminal defect

The original `history.c` input-state stage guards, `rec_get_xe_next2_HTm`,
and memory rotation were compared directly with the Python and new C harness.
The low-z path uses h2 = `4.245e-5`, starts at accepted index 58389, and carries
both hydrogen and thermal RHS tails separately for Python and native C.
The update consumes `prev2 = F[n-2]`, then rotates
`(prev2, prev) = (prev, F[n])`. No source reevaluation or reseeding is inserted
at FULL→EMLA or EMLA→Peebles. The absorbing Peebles event prevents reentry into
a source loop already exited.

The input-time `TR_MIN`/temperature-ratio ordering matches the original source.
The final source index is 211716; it is an interpolation output, and both the
Python and native step interfaces reject an additional RHS there. No photon
history is accessed by the low-z C calls: the first native step requests FULL
only so the original function itself switches to EMLA at its RT boundary.
The Python Peebles and thermal dependencies preserve the original Fudge=1 and
thermal branch formulas.

R6-P2-01 is **closed**. The new reviewer ran six controlled endpoint updates,
using actual Peebles/thermal operators on manufactured states:

| Remaining steps | Final index | Status | z=0 result |
|---|---|---|---|
| 1 | 211716 | `SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL` | Absent |
| 2 | 211716 | `SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL` | Absent |
| 3 | 211716 | `STOP_AT_SOURCE_Z0_CUBIC_STENCIL` | Present; both fields match original-C cubic bytes on the same tail |

No missing history was invented. The result is about terminal status and stencil
ownership, not a new physical low-redshift trajectory or automatic CLI resume.

The low-z runner retains accepted Python state on a comparison failure, records
actual Python/native pairs before checking parity, writes checkpoint tails, uses
exclusive output creation, and rechecks input/source/code identities in its
failure path. Full mode requires a current allocation bound to the code and a
16–32-step same-code smoke. Its historical budget remains closed. Its work and
recovery limits and final total-cap check are materially stronger than the two
h4 failure paths identified above.

### Independent h4 start and memory bounds

The original HeIII/HeII closures and post-Saha/predictor code were checked against
`history.c` and the relevant reused scalar implementations. The quarter-grid
class derives its own floor index 72892 and uses its own redshift clock. Reuse
from h2 is limited to clock-free formulas and fixed cosmology; no h2 checkpoint
or C trajectory is an evolution input.

The hydrogen seeds use the independent h4 electron history, divide by the h4
step, and subtract the correctly owned He derivatives. At endpoint 72900 the
retained final predictor owns inputs 72898 and 72899. It equals the last two
saved H/He RHS values, and all nine native memory rows match the reconstructed
Python memory sequence under the existing tolerance.

Python commits one current-input photon column per accepted step. Post-Saha
trial results are discarded. The common-input C callback receives detached
read-only past arrays. The native harness allocates `steps+1` columns for the
accepted prefix and one scratch trial, clears the trial column, and retains the
original source's `nzrt`. The original causal interpolation reads only accepted
neighbors; the h4 path passes its own step and q=0 explicitly. The retained
arrays are `virtual[311,8]`, `average[311,8]`, and `Lyman[3,8]`.

Nonfinite state/RHS/spectrum operands and invalid shapes are rejected before
the relevant parity comparisons. The existing post-Saha one-ULP temperature
representation convention is retained, with common-input and independent
trajectory comparisons kept distinct. No new operator, threshold, predictor,
or global stability/convergence assertion is admitted.

### Original-h adapter and manufactured affine figure

The completed adapter was reviewed in its final stable form. Direct NPZ readback
confirms that both 105,859-element `xe` and `Tm_K` arrays are byte-equal to their
pinned producer arrays. The three producer-file hashes, producer
`6c6c385f69f73ad477a3131d637b25fe7faca5ac`, original ZIP identity, and R3I contract
are checked. Input mutation is detected after serialization; existing output
directories and files are not reused.

The regime labels are owned by input indices: UNKNOWN before 29195, EMLA through
72465, and Peebles from 72466. The physical boundary coverage stops at ln(a)=0,
while the last slightly negative-z source output remains available to the cubic
stencil. Earlier unknown boundaries are not invented.

The adapter does not convert an 8001-point integer-z aggregate discrepancy into
a source-node error bound. Nodewise C parity is UNKNOWN; additional binary64
serialization quantization is zero. Loading the h and h2 descriptors gives
`INSUFFICIENT_LEVELS`, missing level [2], and `global_coverage=false`.

The current `affine_probe()` exactly reproduces the saved probe's content. It
is a manufactured scalar diagnostic, with three perturbation responses compared
to the rational recurrence, not a HyRec convergence calculation. Reversing only
the second legend's location in memory restores the executed plot-script hash
`63af5985535aa811f73e6ea250ad9e65e3e3402736b271dacd04b29710a4e500`.
This verifies the worker's one-line, presentation-only change without rerendering.

`FINAL_PLOT_SELECTION.json` selects the revised PNG with hash
`519794aec35f4327ced762169865d4fd104be54d679f6bf2f9341f26aed5eb35`.
The revised PDF is a zero-byte `.pdf.partial` and explicitly
`NOT_COMPLETED_CPU_LIMIT`; the original PDF is retained separately. This is a
truthfully recorded bounded rendering limitation, not a false scientific PASS.
The worker's visual inspection is reused; this C9 pass checked contract and
provenance and performed no new visual review.

## 4. Directly inspected execution evidence

The following are retained actual executions, not new production by C9.

| Lane | Actual command/exit record | Result and scope |
|---|---|---|
| h2 smoke | `../rec_recovery/r3o_lowz_smoke_002_execution.json`, exit 0 | 16 EMLA updates; outputs through 58405 |
| h4 start | `../rec_recovery/r3o_h4_runs/start_002_driver.json`, return 0 | Independent 72893-row He history and eight FULL updates through 72900 |
| h adapter | `../rec_recovery/r3o_h_input_adapter_001.execution.json`, exit 0 | 105859 reused source states; zero new HyRec integrations |
| h2 tests | `../rec_recovery/r3o_lowz_R6_P2_01_test.json` and matching log, exit 0 | 21 tests, including the R6 closure |
| h4 tests | `../rec_recovery/r3o_h4_runs/tests_002.json` and matching log, return 0 | 12 tests |
| adapter/probe tests | `../rec_recovery/r3o_h_input_tests_001.execution.json` and matching log, exit 0 | 12 tests |

Actual physical CLI invocations preserved in those records:

```sh
python3 scripts/verify_r3o_lowz.py --mode smoke --steps 16 --raw-dir /workspace/scratch/afe554957b2e/rec_raw_verified/full5210_stored --evidence-dir /workspace/scratch/afe554957b2e/rec_recovery/r3o_lowz_smoke_002
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/verify_r3o_h4_start.py --mode start --steps 8 --cpu-seconds 20 --wall-seconds 60 --evidence-dir /workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002
```

The corresponding native build command arrays and exit 0 results were read from
the run receipts. No build or primordial integration was repeated in this review.

| Evidence object | Actual SHA256 |
|---|---|
| h2 `verification.json` | `0b6219008a9efb20f2f4913af039a7b45be8ceb03c6517090078d3eb047436f9` |
| h2 `accepted_pairs.jsonl` | `4924cdf71060a7eb8cfaeebaa94e39e5ad5f05112daf7b7f40f7ed5181f27013` |
| h2 `python_native_lowz.npz` | `2d6c54f448a5b109e21cb265f469b94860a2525ae2f777ef02b19bb05ffbc784` |
| h4 `verification.json` | `6291598aae822e08be8c572437cbe04564b498b9e4c84279876dc7f82c66534e` |
| h4 `python_h4_helium.npz` | `0b4e1911cb32c40f3bec6cefbc0c138ec635d4d25f2a0a6e504c812718529f93` |
| h4 `python_h4_full_start.npz` | `40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef` |
| h4 `native_oracle.stdout` | `4e4c65f32b7ff091cf51ec025bd8cfcc002a82249f42096aba9d928bd7f28cfd` |
| adapted h `h_state_trace.npz` | `d46fb7eaeb6cc8792c5d929f28953d48684cf1e4f3305f33f6ba4f3393999fd3` |

The current raw U6 inputs were also rehashed against the producer pins:
NPZ `5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2`,
native CSV `57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38`,
and receipt `1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b`.

All 16 retained h2 pairs satisfy their own recorded binary64 update and memory
rotation exactly; the saved arrays and terminal checkpoint agree with those
pairs. Independent-lane discrepancies remain nonzero and bounded: scaled xe
`7.434376394267938e-14`, scaled Tm `2.49687949887451e-16`, common-input H RHS
`2.1707559781417694e-14`, thermal RHS `3.621030056849089e-14`.
This internal exact-recurrence check does not assert Python/C byte identity.

For h4, the native reader accepted complete raw output, with 72893 He rows,
eight steps, and nine memory rows. Recomputing the integrated comparison from
the saved arrays produced exactly the stored comparison dictionary. He-state
error maxima also reproduce the receipt. Integrated xHII/xe/Tm discrepancies
are zero in the retained binary64 states; absolute HeII discrepancy is
`5.421010862427522e-20`; maximum average-photon tolerance ratio is
`7.883083461150054e-6`; maximum matrix residual is
`2.8638673618951863e-16`. Same-input FULL RHS maximum
`2.0511717324644962e-13` is a retained execution measurement, not a newly run
atomic evaluation in C9.

## 5. CI readiness and finite handoff

`.github/workflows/verify.yml` runs `pytest -q` over `tests`, and
`pyproject.toml` supplies the src import path and test dependencies. The three
new unittest classes are collectable by that route and also have demonstrated
stdlib unittest commands. Tests cover predictor rotations, terminal and stage
neighbors, invalid/nonfinite input, immutable source copies, parser truncation,
source-clock independence, photon prefix ownership, source-cosmology mismatch,
and adapter mutation/unknown-parity semantics. The review does not claim a
GitHub Actions run from this non-checkout.

The two newly demonstrated h4 resource cases are absent from the current h4
test file and are the narrowly scoped CI regressions to add with their fixes.
The adapter tests require its bundled h descriptor/NPZ and three producer
inputs, plus the already retained h2 descriptor/NPZ. These exist in the reviewed
capsule; parent owns their inclusion in the published checkout. No full
historical campaign is required by this finding.

The existing actual results can be reused while the runner-only defects are
repaired. Preserve old receipts under their recorded hashes; bind any revised
runner and its targeted controls to their new identity. Stop this independent
pass here. This report does not modify parent EVIDENCE/DAG, scientific holds,
or any implementation file.

| Protected result/status | C9 disposition |
|---|---|
| Original h U5 | `HOLD_9_FAIL` retained |
| h2 U5 | `HOLD_8_FAIL` retained |
| Historical budget | `CLOSED_HOLD_NOT_RESET` retained |
| REI | false |
| Full h2 low-z, 153327 steps | NOT_RUN |
| Full h4 continuation | NOT_RUN |
| Global h/h2/h4 convergence | NOT_RUN / not admitted |
| Production speedup | No admission |
| Bianchi/REI/CMB | Not admitted |

## 6. New reviewer controls, limits, and raw command preservation

No full suite, native rebuild, U4/U5/U6 execution, full low-z run, or h4 primordial
start was repeated. The successful direct-readback/affine command used
1.85737906 process CPU seconds. The separate resource/terminal controls used
0.990181 parent CPU seconds plus 0.023911 reaped-child CPU seconds
(1.014092 measured combined). The synthetic sleeping descendant was inspected
then explicitly terminated; that grandchild is not included in the reaped-child
figure. Anonymous memfd output avoided temporary disk artifacts.

The first readback command failed with a reviewer-side KeyError because it
incorrectly applied h2's scientific-member mapping to a ZIP metadata member
under `__MACOSX/`. That failure is not a product finding or a PASS. The exact
diagnosed correction was to skip non-`HyRec/` members only in the h2 extraction
comparison; h4's full manifest was still checked. The corrected command passed.
The failure's host wall time was 0.896486648 seconds; its CPU was not separately
sampled. Both readback attempts had a four-second hard process CPU limit; the
control command had a three-second hard process limit. The successful measured
CPU, plus conservative single-thread wall bounds for the failed readback and
the one sleeping grandchild, remains below the assigned eight-CPU-second
additional-control ceiling. Small read-only source/receipt inspections are
distinct from scientific/test execution.

The exact raw commands and host results follow. They are preserved in this
single output file because the assignment permits no additional persistent
reviewer artifacts. Commands B and C are the completed evidence checks;
Command A is the preserved failed reviewer setup.

### A — initial readback, reviewer mapping error; exit 1

Working directory: `/workspace/scratch/afe554957b2e/rec_work`.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:scripts OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_CPU,(4,4))
import hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import verify_r3o_h4_start as h4v
import prepare_r3o_h_history as adapter
import plot_r3o_frontiers as plotting
from compare_r3n_time_grids import load_history,compare_histories
root=Path.cwd(); recovery=root.parent/'rec_recovery'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
paths=['src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py','src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py','scripts/verify_r3o_lowz.py','scripts/verify_r3o_h4_start.py','scripts/c_harness/original_hyrec_r3o_lowz_harness.c','scripts/c_harness/original_hyrec_r3o_h4_start_harness.c','scripts/prepare_r3o_h_history.py','scripts/plot_r3o_frontiers.py','tests/trajectory/test_r3o_lowz.py','tests/trajectory/test_r3o_h4_start.py','tests/trajectory/test_r3o_h_inputs.py']
identities={p:sha(root/p) for p in paths}; evidence={}; archive=root/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
assert sha(archive)==h4v.h4.PINNED_ZIP_SHA256
with zipfile.ZipFile(archive) as z:
 members={i.filename:z.read(i) for i in z.infolist() if not i.is_dir()}
 source_hashes={k:hashlib.sha256(v).hexdigest() for k,v in members.items()}
 for lane,prefix,denom,mname,okey,ckey in [('r3o_lowz_smoke_002','source_h2',2,'source_manifest.json','original_members','compiled_members'),('r3o_h4_runs/start_002','source_extract',4,'source_manifest.json','original_member_sha256','modified_member_sha256')]:
  base=recovery/lane;m=json.loads((base/mname).read_text()); actual={}
  for name,data in members.items():
   key=name.removeprefix('HyRec/') if denom==2 else name
   assert m[okey][key]==hashlib.sha256(data).hexdigest()
   if name=='HyRec/hyrec_params.h':data=data.replace(b'#define DLNA          8.49e-5',f'#define DLNA          (8.49e-5/{denom}.)'.encode())
   expected=hashlib.sha256(data).hexdigest();assert m[ckey][key]==expected and sha(base/prefix/key)==expected
   actual[key]=expected
  r=json.loads((base/'verification.json').read_text());deps=r.get('source_code_sha256',r.get('producer_and_dependency_sha256'))
  assert all(sha(root/k)==v for k,v in deps.items())
  evidence[lane]={'verification_sha256':sha(base/'verification.json'),'dependency_count':len(deps),'dependencies_match':True,'source_members_match':len(actual),'header_sha256':actual.get('hyrec_params.h',actual.get('HyRec/hyrec_params.h'))}
base=recovery/'r3o_lowz_smoke_002';r=json.loads((base/'verification.json').read_text());pairs=[json.loads(x) for x in (base/'accepted_pairs.jsonl').read_text().splitlines()]
assert len(pairs)==16
with np.load(base/'python_native_lowz.npz',allow_pickle=False) as a:
 assert a['global_iz'].tolist()==list(range(58389,58406))
 old=r['start'];maxima={'xe':0.,'Tm_K':0.}
 for j,e in enumerate(pairs):
  s=e['step'];assert s['input_iz']==58389+j and s['output_iz']==58390+j and s['model']=='EMLA2s2p'
  for lane in ('python','native'):
   prev=old[lane];new=e[lane]
   for field,mem,rhs in [('xe','hydrogen','hydrogen_rhs'),('Tm_K','thermal','thermal_rhs')]:
    derivative=s[rhs] if lane=='python' else new[mem+'_prev']
    assert new[field]==prev[field]+4.245e-5*(1.25*derivative-.25*prev[mem+'_prev2'])
    assert new[mem+'_prev2']==prev[mem+'_prev'] and new[mem+'_prev']==derivative
    k=field if lane=='python' else 'native_'+field
    assert a[k][j+1]==new[field]
   assert new['iz']==58390+j and new['peebles_event_iz'] is None
  old=e
 for lane in ('python','native'):
  key='checkpoint' if lane=='python' else 'native_checkpoint'
  assert json.loads((base/'checkpoint_00004.json').read_text())[key]==pairs[-1][lane]
assert sha(base/'python_native_lowz.npz')==r['history_sha256']
assert sha(base/'liboriginal_r3o_lowz.so')==r['native_binary_sha256']
assert sha(base/r['last_checkpoint']['path'])==r['last_checkpoint']['sha256']
for name in ('build_stdout.txt','build_stderr.txt'):
 assert sha(base/name)==r['native_build']['stdout_sha256' if 'stdout' in name else 'stderr_sha256']
raw=root.parent/'rec_raw_verified/full5210_stored'
for name,digest in r['inputs_before'].items():
 assert sha(archive if name=='source_zip' else raw/name)==digest
assert r['inputs_before']==r['inputs_after']
evidence['r3o_lowz_smoke_002'].update(accepted_pairs=16,endpoint=58405,python_and_native_recurrences='EXACT_ON_RETAINED_BINARY64_INPUTS',history_sha256=sha(base/'python_native_lowz.npz'),ledger_sha256=sha(base/'accepted_pairs.jsonl'),current_raw_inputs_match=True)
base=recovery/'r3o_h4_runs/start_002';r=json.loads((base/'verification.json').read_text())
assert all((base/k).stat().st_size==v['bytes'] and sha(base/k)==v['sha256'] for k,v in r['artifacts'].items())
assert all(sha(base/'producer_snapshot'/k)==sha(root/k) for k in h4v.H4_SOURCE_FILES)
native=h4v.parse_native(base/'native_oracle.stdout',8)
with np.load(base/'python_h4_full_start.npz',allow_pickle=False) as a:
 kw={k:a[k] for k in h4v.h4.QuarterFullStartHistory.__dataclass_fields__}
 for k,cast in [('full_evaluations',int),('dlna',float),('source_mode',str)]:kw[k]=cast(kw[k].item())
 full=h4v.h4.QuarterFullStartHistory(**kw)
 assert np.array_equal(full.final_predictor,np.array([full.helium_rhs_dln_a[-2:],full.hydrogen_rhs_dln_a[-2:]]))
 assert a['predictor_input_global_indices'].tolist()==[72898,72899]
 table=h4v._canonical_twophoton_table(archive)
 comparison=h4v.compare_full(full,native,h4v.h4.QuarterStartCosmology(),table)
 assert comparison==r['integrated_parity']
with np.load(base/'python_h4_helium.npz',allow_pickle=False) as a:
 assert a['iz'].tolist()==list(range(72893))
 for k,name in enumerate(('z','xe','xHII','xHeI','xHeII','xHeIII','Tm_K')):
  scaled=float(np.max(np.abs(a[name]-native['helium'][:,k])/np.maximum(1.,np.abs(native['helium'][:,k]))))
  assert scaled==r['helium_parity']['max_state_scaled_max1'][name]
evidence['r3o_h4_runs/start_002'].update(helium_rows=len(native['helium']),full_steps=len(native['steps']),memory_rows=len(native['memories']),endpoint=72900,full_checkpoint_sha256=sha(base/'python_h4_full_start.npz'),helium_npz_sha256=sha(base/'python_h4_helium.npz'),native_stdout_sha256=sha(base/'native_oracle.stdout'),saved_parity_recomputed_exactly=True)
trace=root/'research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001'; h=load_history(trace/'h_state_trace.json');h2=load_history(plotting.DEFAULT_H2)
assert adapter.input_hashes(trace/'producer_inputs')==adapter.INPUT_SHA256
with np.load(trace/'producer_inputs/independent_source_grid.npz',allow_pickle=False) as a:
 assert all(h.values[k].tobytes()==a[k].tobytes() for k in ('xe','Tm_K'))
assert h.global_iz.size==105859 and all(h.parity_abs[k] is None for k in ('xe','Tm_K'))
coverage=compare_histories([h,h2]);assert coverage['status']=='INSUFFICIENT_LEVELS' and coverage['levels_missing']==[2] and coverage['global_coverage'] is False
pb=trace.parent/'frontier_probes_001';probe=plotting.affine_probe();assert probe==json.loads((pb/'probe.json').read_text())
selection=json.loads((pb/'FINAL_PLOT_SELECTION.json').read_text());assert sha(pb/selection['selected_png'])==selection['selected_png_sha256'] and (pb/selection['revised_pdf']).stat().st_size==0 and selection['revised_pdf_status']=='NOT_COMPLETED_CPU_LIMIT'
new=(root/'scripts/plot_r3o_frontiers.py').read_bytes();old=new.replace(b'axes[1].legend(loc="upper right", frameon=False)',b'axes[1].legend(loc="lower left", frameon=False)')
assert new!=old and hashlib.sha256(old).hexdigest()=='63af5985535aa811f73e6ea250ad9e65e3e3402736b271dacd04b29710a4e500'
evidence['h_adapter']={'nodes':105859,'source_arrays_byte_equal':True,'nodewise_parity':'UNKNOWN','comparison':coverage['status'],'levels_missing':[2],'trace_sha256':sha(trace/'h_state_trace.npz'),'current_affine_probe_matches_saved_content':True,'legend_only_change_verified':True,'selected_png_sha256':selection['selected_png_sha256'],'revised_pdf_status':selection['revised_pdf_status']}
assert identities=={p:sha(root/p) for p in paths}
print(json.dumps({'kind':'RETAINED_PHYSICAL_EVIDENCE_READBACK_PLUS_MANUFACTURED_AFFINE_CONTROL','new_hyrec_steps':0,'source_hashes':{k:source_hashes[k] for k in ('HyRec/history.c','HyRec/hydrogen.c','HyRec/helium.c','HyRec/hyrectools.c','HyRec/hyrec_params.h','HyRec/two_photon_tables.dat')},'code_hashes':identities,'evidence':evidence,'actual_process_cpu_s':time.process_time(),'actual_wall_scope':'process execution reported by host','exit_if_all_assertions_hold':0},sort_keys=True))
PY
```

Raw host result:

```json
{
  "chunk_id": "3dd5db",
  "wall_time_seconds": 0.896486648,
  "exit_code": 1,
  "original_token_count": 29,
  "output": "Traceback (most recent call last):\n  File \"<stdin>\", line 23, in <module>\nKeyError: '__MACOSX/HyRec/._history.c'\n"
}
```

### B — corrected readback and manufactured affine control; exit 0

Working directory: `/workspace/scratch/afe554957b2e/rec_work`.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:scripts OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_CPU,(4,4))
import hashlib,json,math,time,zipfile,atexit
atexit.register(lambda: print('ACTUAL_PROCESS_CPU_S',time.process_time()))
from pathlib import Path
import numpy as np
import verify_r3o_h4_start as h4v
import prepare_r3o_h_history as adapter
import plot_r3o_frontiers as plotting
from compare_r3n_time_grids import load_history,compare_histories
root=Path.cwd(); recovery=root.parent/'rec_recovery'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
paths=['src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py','src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py','scripts/verify_r3o_lowz.py','scripts/verify_r3o_h4_start.py','scripts/c_harness/original_hyrec_r3o_lowz_harness.c','scripts/c_harness/original_hyrec_r3o_h4_start_harness.c','scripts/prepare_r3o_h_history.py','scripts/plot_r3o_frontiers.py','tests/trajectory/test_r3o_lowz.py','tests/trajectory/test_r3o_h4_start.py','tests/trajectory/test_r3o_h_inputs.py']
identities={p:sha(root/p) for p in paths}; evidence={}; archive=root/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
assert sha(archive)==h4v.h4.PINNED_ZIP_SHA256
with zipfile.ZipFile(archive) as z:
 members={i.filename:z.read(i) for i in z.infolist() if not i.is_dir()}
 source_hashes={k:hashlib.sha256(v).hexdigest() for k,v in members.items()}
 for lane,prefix,denom,mname,okey,ckey in [('r3o_lowz_smoke_002','source_h2',2,'source_manifest.json','original_members','compiled_members'),('r3o_h4_runs/start_002','source_extract',4,'source_manifest.json','original_member_sha256','modified_member_sha256')]:
  base=recovery/lane;m=json.loads((base/mname).read_text()); actual={}
  for name,data in members.items():
   if denom==2 and not name.startswith('HyRec/'):continue
   key=name.removeprefix('HyRec/') if denom==2 else name
   assert m[okey][key]==hashlib.sha256(data).hexdigest()
   if name=='HyRec/hyrec_params.h':data=data.replace(b'#define DLNA          8.49e-5',f'#define DLNA          (8.49e-5/{denom}.)'.encode())
   expected=hashlib.sha256(data).hexdigest();assert m[ckey][key]==expected and sha(base/prefix/key)==expected
   actual[key]=expected
  r=json.loads((base/'verification.json').read_text());deps=r.get('source_code_sha256',r.get('producer_and_dependency_sha256'))
  assert all(sha(root/k)==v for k,v in deps.items())
  evidence[lane]={'verification_sha256':sha(base/'verification.json'),'dependency_count':len(deps),'dependencies_match':True,'source_members_match':len(actual),'header_sha256':actual.get('hyrec_params.h',actual.get('HyRec/hyrec_params.h'))}
base=recovery/'r3o_lowz_smoke_002';r=json.loads((base/'verification.json').read_text());pairs=[json.loads(x) for x in (base/'accepted_pairs.jsonl').read_text().splitlines()]
assert len(pairs)==16
with np.load(base/'python_native_lowz.npz',allow_pickle=False) as a:
 assert a['global_iz'].tolist()==list(range(58389,58406))
 old=r['start'];maxima={'xe':0.,'Tm_K':0.}
 for j,e in enumerate(pairs):
  s=e['step'];assert s['input_iz']==58389+j and s['output_iz']==58390+j and s['model']=='EMLA2s2p'
  for lane in ('python','native'):
   prev=old[lane];new=e[lane]
   for field,mem,rhs in [('xe','hydrogen','hydrogen_rhs'),('Tm_K','thermal','thermal_rhs')]:
    derivative=s[rhs] if lane=='python' else new[mem+'_prev']
    assert new[field]==prev[field]+4.245e-5*(1.25*derivative-.25*prev[mem+'_prev2'])
    assert new[mem+'_prev2']==prev[mem+'_prev'] and new[mem+'_prev']==derivative
    k=field if lane=='python' else 'native_'+field
    assert a[k][j+1]==new[field]
   assert new['iz']==58390+j and new['peebles_event_iz'] is None
  old=e
 for lane in ('python','native'):
  key='checkpoint' if lane=='python' else 'native_checkpoint'
  assert json.loads((base/'checkpoint_00004.json').read_text())[key]==pairs[-1][lane]
assert sha(base/'python_native_lowz.npz')==r['history_sha256']
assert sha(base/'liboriginal_r3o_lowz.so')==r['native_binary_sha256']
assert sha(base/r['last_checkpoint']['path'])==r['last_checkpoint']['sha256']
for name in ('build_stdout.txt','build_stderr.txt'):
 assert sha(base/name)==r['native_build']['stdout_sha256' if 'stdout' in name else 'stderr_sha256']
raw=root.parent/'rec_raw_verified/full5210_stored'
for name,digest in r['inputs_before'].items():
 assert sha(archive if name=='source_zip' else raw/name)==digest
assert r['inputs_before']==r['inputs_after']
evidence['r3o_lowz_smoke_002'].update(accepted_pairs=16,endpoint=58405,python_and_native_recurrences='EXACT_ON_RETAINED_BINARY64_INPUTS',history_sha256=sha(base/'python_native_lowz.npz'),ledger_sha256=sha(base/'accepted_pairs.jsonl'),current_raw_inputs_match=True)
base=recovery/'r3o_h4_runs/start_002';r=json.loads((base/'verification.json').read_text())
assert all((base/k).stat().st_size==v['bytes'] and sha(base/k)==v['sha256'] for k,v in r['artifacts'].items())
assert all(sha(base/'producer_snapshot'/k)==sha(root/k) for k in h4v.H4_SOURCE_FILES)
native=h4v.parse_native(base/'native_oracle.stdout',8)
with np.load(base/'python_h4_full_start.npz',allow_pickle=False) as a:
 kw={k:a[k] for k in h4v.h4.QuarterFullStartHistory.__dataclass_fields__}
 for k,cast in [('full_evaluations',int),('dlna',float),('source_mode',str)]:kw[k]=cast(kw[k].item())
 full=h4v.h4.QuarterFullStartHistory(**kw)
 assert np.array_equal(full.final_predictor,np.array([full.helium_rhs_dln_a[-2:],full.hydrogen_rhs_dln_a[-2:]]))
 assert a['predictor_input_global_indices'].tolist()==[72898,72899]
 table=h4v._canonical_twophoton_table(archive)
 comparison=h4v.compare_full(full,native,h4v.h4.QuarterStartCosmology(),table)
 assert comparison==r['integrated_parity']
with np.load(base/'python_h4_helium.npz',allow_pickle=False) as a:
 assert a['iz'].tolist()==list(range(72893))
 for k,name in enumerate(('z','xe','xHII','xHeI','xHeII','xHeIII','Tm_K')):
  scaled=float(np.max(np.abs(a[name]-native['helium'][:,k])/np.maximum(1.,np.abs(native['helium'][:,k]))))
  assert scaled==r['helium_parity']['max_state_scaled_max1'][name]
evidence['r3o_h4_runs/start_002'].update(helium_rows=len(native['helium']),full_steps=len(native['steps']),memory_rows=len(native['memories']),endpoint=72900,full_checkpoint_sha256=sha(base/'python_h4_full_start.npz'),helium_npz_sha256=sha(base/'python_h4_helium.npz'),native_stdout_sha256=sha(base/'native_oracle.stdout'),saved_parity_recomputed_exactly=True)
trace=root/'research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001'; h=load_history(trace/'h_state_trace.json');h2=load_history(plotting.DEFAULT_H2)
assert adapter.input_hashes(trace/'producer_inputs')==adapter.INPUT_SHA256
with np.load(trace/'producer_inputs/independent_source_grid.npz',allow_pickle=False) as a:
 assert all(h.values[k].tobytes()==a[k].tobytes() for k in ('xe','Tm_K'))
assert h.global_iz.size==105859 and all(h.parity_abs[k] is None for k in ('xe','Tm_K'))
coverage=compare_histories([h,h2]);assert coverage['status']=='INSUFFICIENT_LEVELS' and coverage['levels_missing']==[2] and coverage['global_coverage'] is False
pb=trace.parent/'frontier_probes_001';probe=plotting.affine_probe();assert probe==json.loads((pb/'probe.json').read_text())
selection=json.loads((pb/'FINAL_PLOT_SELECTION.json').read_text());assert sha(pb/selection['selected_png'])==selection['selected_png_sha256'] and (pb/selection['revised_pdf']).stat().st_size==0 and selection['revised_pdf_status']=='NOT_COMPLETED_CPU_LIMIT'
new=(root/'scripts/plot_r3o_frontiers.py').read_bytes();old=new.replace(b'axes[1].legend(loc="upper right", frameon=False)',b'axes[1].legend(loc="lower left", frameon=False)')
assert new!=old and hashlib.sha256(old).hexdigest()=='63af5985535aa811f73e6ea250ad9e65e3e3402736b271dacd04b29710a4e500'
evidence['h_adapter']={'nodes':105859,'source_arrays_byte_equal':True,'nodewise_parity':'UNKNOWN','comparison':coverage['status'],'levels_missing':[2],'trace_sha256':sha(trace/'h_state_trace.npz'),'current_affine_probe_matches_saved_content':True,'legend_only_change_verified':True,'selected_png_sha256':selection['selected_png_sha256'],'revised_pdf_status':selection['revised_pdf_status']}
assert identities=={p:sha(root/p) for p in paths}
print(json.dumps({'kind':'RETAINED_PHYSICAL_EVIDENCE_READBACK_PLUS_MANUFACTURED_AFFINE_CONTROL','new_hyrec_steps':0,'source_hashes':{k:source_hashes[k] for k in ('HyRec/history.c','HyRec/hydrogen.c','HyRec/helium.c','HyRec/hyrectools.c','HyRec/hyrec_params.h','HyRec/two_photon_tables.dat')},'code_hashes':identities,'evidence':evidence,'actual_process_cpu_s':time.process_time(),'actual_wall_scope':'process execution reported by host','exit_if_all_assertions_hold':0},sort_keys=True))
PY
```

Raw host result:

```json
{
  "chunk_id": "689ee1",
  "wall_time_seconds": 1.853237018,
  "exit_code": 0,
  "original_token_count": 963,
  "output": "{\"actual_process_cpu_s\": 1.85737906, \"actual_wall_scope\": \"process execution reported by host\", \"code_hashes\": {\"scripts/c_harness/original_hyrec_r3o_h4_start_harness.c\": \"8b50858c0e0a3d1e6eef19e9f159673156162f70a7363b51945a9f238aa2ec8a\", \"scripts/c_harness/original_hyrec_r3o_lowz_harness.c\": \"d179b07d33562557924f763b85a58f5a2cec48ec2a78c4ab39a6702d82e88756\", \"scripts/plot_r3o_frontiers.py\": \"e952d0ca8f290d66ca61a645979a43bbdda1db085c72e2b3bacd2337b6c1b500\", \"scripts/prepare_r3o_h_history.py\": \"c5a938c0b37cae5ff8b1ec05099bb420fd2da9a17e719ef047c9192c52224cad\", \"scripts/verify_r3o_h4_start.py\": \"96e03f326342940606dba33dd44d8f172d5bb6a773dc15f404635babca6f4deb\", \"scripts/verify_r3o_lowz.py\": \"192f6ba070f35d7cede83fc03a96757064844f517f9b6c5910c2d7d305ddb193\", \"src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py\": \"6247e0681d74e5b6f26f9818faf4a49af4ce61e64e4970bfe3b7c21ad951fd10\", \"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py\": \"6f6cdfa281fc893f80334e43418a130cdd7526be8e14d9575eed74dcbd7edee6\", \"tests/trajectory/test_r3o_h4_start.py\": \"50dceee1c92e1ab3baa50c468955affac47c6639dcd3714a492e1bb542e43359\", \"tests/trajectory/test_r3o_h_inputs.py\": \"74004e931a004f313353fb92ee345519f9d358aab1b75c9363644dd2d6ca176d\", \"tests/trajectory/test_r3o_lowz.py\": \"05da1804d0cd1817030b27bb8b48d7c48b9f4085c38becfc278a7bcd72293893\"}, \"evidence\": {\"h_adapter\": {\"comparison\": \"INSUFFICIENT_LEVELS\", \"current_affine_probe_matches_saved_content\": true, \"legend_only_change_verified\": true, \"levels_missing\": [2], \"nodes\": 105859, \"nodewise_parity\": \"UNKNOWN\", \"revised_pdf_status\": \"NOT_COMPLETED_CPU_LIMIT\", \"selected_png_sha256\": \"519794aec35f4327ced762169865d4fd104be54d679f6bf2f9341f26aed5eb35\", \"source_arrays_byte_equal\": true, \"trace_sha256\": \"d46fb7eaeb6cc8792c5d929f28953d48684cf1e4f3305f33f6ba4f3393999fd3\"}, \"r3o_h4_runs/start_002\": {\"dependencies_match\": true, \"dependency_count\": 13, \"endpoint\": 72900, \"full_checkpoint_sha256\": \"40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef\", \"full_steps\": 8, \"header_sha256\": \"46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f\", \"helium_npz_sha256\": \"0b4e1911cb32c40f3bec6cefbc0c138ec635d4d25f2a0a6e504c812718529f93\", \"helium_rows\": 72893, \"memory_rows\": 9, \"native_stdout_sha256\": \"4e4c65f32b7ff091cf51ec025bd8cfcc002a82249f42096aba9d928bd7f28cfd\", \"saved_parity_recomputed_exactly\": true, \"source_members_match\": 26, \"verification_sha256\": \"6291598aae822e08be8c572437cbe04564b498b9e4c84279876dc7f82c66534e\"}, \"r3o_lowz_smoke_002\": {\"accepted_pairs\": 16, \"current_raw_inputs_match\": true, \"dependencies_match\": true, \"dependency_count\": 52, \"endpoint\": 58405, \"header_sha256\": \"e83d8031975c0a64cdb45a2b8ba03a4a0a75c85fac5cf2437aadc915e25751bf\", \"history_sha256\": \"2d6c54f448a5b109e21cb265f469b94860a2525ae2f777ef02b19bb05ffbc784\", \"ledger_sha256\": \"4924cdf71060a7eb8cfaeebaa94e39e5ad5f05112daf7b7f40f7ed5181f27013\", \"python_and_native_recurrences\": \"EXACT_ON_RETAINED_BINARY64_INPUTS\", \"source_members_match\": 19, \"verification_sha256\": \"0b6219008a9efb20f2f4913af039a7b45be8ceb03c6517090078d3eb047436f9\"}}, \"exit_if_all_assertions_hold\": 0, \"kind\": \"RETAINED_PHYSICAL_EVIDENCE_READBACK_PLUS_MANUFACTURED_AFFINE_CONTROL\", \"new_hyrec_steps\": 0, \"source_hashes\": {\"HyRec/helium.c\": \"1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece\", \"HyRec/history.c\": \"8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976\", \"HyRec/hydrogen.c\": \"421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b\", \"HyRec/hyrec_params.h\": \"cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2\", \"HyRec/hyrectools.c\": \"beb97b6cee3b80cf74d58264da7087301865881d266de1c17dd472a08665bb79\", \"HyRec/two_photon_tables.dat\": \"93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9\"}}\nACTUAL_PROCESS_CPU_S 1.85737906\n"
}
```

### C — controlled resource paths and terminal closure; exit 0

Working directory: `/workspace/scratch/afe554957b2e/rec_work`.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:scripts OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_CPU,(3,3))
import atexit,contextlib,copy,io,json,os,signal,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
atexit.register(lambda: print('ACTUAL_PROCESS_CPU_S',time.process_time()))
import numpy as np
import verify_r3o_h4_start as v
import verify_r3o_lowz as low
from full_bianchi_hyrec.trajectory import primordial_2012_refined_low_z as m
root=Path.cwd();observed={}
# Real Budget.run timeout, synthetic sleeping process tree, all output in RAM.
fds=[os.memfd_create('c9_stdout'),os.memfd_create('c9_stderr')]
class MemoryPrefix:
 name='c9_timeout_control'
 def __init__(self,fd=None):self.fd=fd
 def with_suffix(self,s):return MemoryPrefix(fds[0 if s=='.stdout' else 1])
 def open(self,mode):return os.fdopen(os.dup(self.fd),'wb',buffering=0)
child_pid=None;launched=[];original_popen=subprocess.Popen
command=[sys.executable,'-B','-c','import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(4)"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(p.pid,flush=True); time.sleep(4)']
def capture(*a,**kw):
 p=original_popen(*a,**kw);launched.append((p,kw));return p
try:
 budget=v.Budget(2,.4)
 try:
  with patch.object(subprocess,'Popen',side_effect=capture):
   budget.run(command,root,MemoryPrefix())
  raise AssertionError('expected synthetic timeout')
 except subprocess.TimeoutExpired as exc:
  os.lseek(fds[0],0,os.SEEK_SET);raw=os.read(fds[0],1000).decode().strip();child_pid=int(raw)
  stat=Path(f'/proc/{child_pid}/stat').read_text().rsplit(') ',1)[1].split();state=stat[0]
  observed['h4_timeout_control']={'classification':'SYNTHETIC_PROCESS_TREE_NO_HYREC','command':command,'timeout_s':exc.timeout,'driver_returncode':launched[0][0].returncode,'start_new_session':launched[0][1].get('start_new_session',False),'descendant_pid':child_pid,'descendant_state_after_timeout':state,'resource_contract_defect_reproduced':state not in ('Z','X')}
  assert launched[0][0].returncode==-signal.SIGKILL and state not in ('Z','X')
finally:
 if child_pid is not None:
  try:os.kill(child_pid,signal.SIGKILL);observed['h4_timeout_control']['reviewer_cleanup_sigkill']=True
  except ProcessLookupError:observed['h4_timeout_control']['reviewer_cleanup_already_exited']=True
 for fd in fds:os.close(fd)
# Execute the real main/finally; replace science, I/O and accounting with controls.
logical_cpu=[0.];zip_calls=[0];snapshots=[];ev=MagicMock(name='memory_evidence')
ev.resolve.return_value=ev;ev.iterdir.return_value=()
args=SimpleNamespace(evidence_dir=ev,mode='helium',steps=8,cpu_seconds=1,wall_seconds=60)
he=SimpleNamespace(**{k:np.zeros(1) for k in ('iz','z','xe','xHII','xHeI','xHeII','xHeIII','Tm_K','helium_rhs_dln_a','stage','update_method','post_saha')})
def controlled_sha(p):
 if p==v.ZIP:
  zip_calls[0]+=1
  if zip_calls[0]>=2:logical_cpu[0]=1.25
 return v.h4.PINNED_ZIP_SHA256
def save_in_memory(path,value):snapshots.append(copy.deepcopy(value))
with contextlib.ExitStack() as s:
 for target,name,value in [(v,'H4_SOURCE_FILES',()),(v,'DEPENDENCIES',()),(v,'sha',controlled_sha),(v,'json_new',save_in_memory)]:s.enter_context(patch.object(target,name,value))
 s.enter_context(patch.object(v.argparse.ArgumentParser,'parse_args',return_value=args))
 s.enter_context(patch.object(v.Budget,'cpu',staticmethod(lambda:logical_cpu[0])))
 s.enter_context(patch.object(v.Budget,'run',return_value={'returncode':0}))
 s.enter_context(patch.object(v.os,'sched_getaffinity',return_value=set()))
 s.enter_context(patch.object(v.resource,'setrlimit'))
 s.enter_context(patch.object(v.signal,'signal'));s.enter_context(patch.object(v.signal,'alarm'))
 s.enter_context(patch.object(v,'prepare_source',return_value=(Path('/c9-memory/source'),{'modified_member_sha256':{}})))
 s.enter_context(patch.object(v.subprocess,'run',return_value=SimpleNamespace(stdout='controlled compiler\n')))
 s.enter_context(patch.object(v,'parse_native',return_value={'memories':{-1:np.zeros((2,2))}}))
 s.enter_context(patch.object(v.h4,'integrate_helium_stages',return_value=he))
 s.enter_context(patch.object(v.h4,'source_native_derivative_seeds',return_value=np.zeros((2,2))))
 s.enter_context(patch.object(v,'save_npz_new',return_value='controlled_no_file'))
 s.enter_context(patch.object(v,'compare_helium',return_value={'status':'PASS_CONTROL_ONLY'}))
 with contextlib.redirect_stdout(io.StringIO()):code=v.main()
r=snapshots[-1]
observed['h4_finalization_control']={'classification':'SYNTHETIC_ACCOUNTING_AND_IO_NO_HYREC','main_returncode':code,'reported_status':r['status'],'allowance_cpu_s':r['resource_allowance']['local_total_cpu_s'],'reported_cpu_s':r['resources']['cpu_s_including_children'],'resource_contract_defect_reproduced':code==0 and r['resources']['cpu_s_including_children']>r['resource_allowance']['local_total_cpu_s']}
assert observed['h4_finalization_control']['resource_contract_defect_reproduced']
# R6 closure: six actual operator updates on manufactured terminal fixtures.
class NoEmla:
 def hydrogen_rhs_ln_a(self,**kw):raise AssertionError('unexpected EMLA')
base=root.parent/'rec_recovery/r3o_lowz_smoke_002';oracle=low.NativeLowZ(base/'liboriginal_r3o_lowz.so',base/'source_h2')
terminal=[]
for count in (1,2,3):
 cp=m.LowZCheckpoint(m.END_IZ-count,1e-4,.05,0.,0.,-.1,-.1,144931,'TR_MIN')
 r=m.continue_refined_low_z(cp,m.HyRec2012Cosmology(),NoEmla(),max_steps=count)
 assert r['checkpoint'].iz==m.END_IZ
 if count<3:assert r['status']=='SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL' and r['z0'] is None
 else:
  assert r['status']=='STOP_AT_SOURCE_Z0_CUBIC_STENCIL'
  for k in ('xe','Tm_K'):assert np.float64(r['z0'][k]['value']).tobytes()==np.float64(oracle.z0(r[k][-4:])).tobytes()
 terminal.append({'remaining':count,'status':r['status'],'z0_present':r['z0'] is not None})
observed['r6_terminal_closure_control']={'classification':'MANUFACTURED_STATE_ACTUAL_PEEBLES_THERMAL_OPERATORS','operator_updates':6,'new_physical_history_steps':0,'cases':terminal,'three_step_same_input_original_c_cubic_bytes':'MATCH'}
a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
observed['resources']={'actual_parent_cpu_s':a.ru_utime+a.ru_stime,'actual_reaped_children_cpu_s':b.ru_utime+b.ru_stime,'actual_cpu_s_including_reaped_children':a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime,'hard_parent_cpu_s':3,'new_physical_hyrec_history_steps':0}
print(json.dumps(observed,sort_keys=True))
PY
```

Raw host result:

```json
{
  "chunk_id": "924f91",
  "wall_time_seconds": 1.4050468139999999,
  "exit_code": 0,
  "original_token_count": 397,
  "output": "{\"h4_finalization_control\": {\"allowance_cpu_s\": 1, \"classification\": \"SYNTHETIC_ACCOUNTING_AND_IO_NO_HYREC\", \"main_returncode\": 0, \"reported_cpu_s\": 1.25, \"reported_status\": \"PASS_SAME_H_HELIUM\", \"resource_contract_defect_reproduced\": true}, \"h4_timeout_control\": {\"classification\": \"SYNTHETIC_PROCESS_TREE_NO_HYREC\", \"command\": [\"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3\", \"-B\", \"-c\", \"import subprocess,sys,time; p=subprocess.Popen([sys.executable,\\\"-B\\\",\\\"-c\\\",\\\"import time; time.sleep(4)\\\"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(p.pid,flush=True); time.sleep(4)\"], \"descendant_pid\": 7, \"descendant_state_after_timeout\": \"S\", \"driver_returncode\": -9, \"resource_contract_defect_reproduced\": true, \"reviewer_cleanup_sigkill\": true, \"start_new_session\": false, \"timeout_s\": 0.3996656290037208}, \"r6_terminal_closure_control\": {\"cases\": [{\"remaining\": 1, \"status\": \"SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL\", \"z0_present\": false}, {\"remaining\": 2, \"status\": \"SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL\", \"z0_present\": false}, {\"remaining\": 3, \"status\": \"STOP_AT_SOURCE_Z0_CUBIC_STENCIL\", \"z0_present\": true}], \"classification\": \"MANUFACTURED_STATE_ACTUAL_PEEBLES_THERMAL_OPERATORS\", \"new_physical_history_steps\": 0, \"operator_updates\": 6, \"three_step_same_input_original_c_cubic_bytes\": \"MATCH\"}, \"resources\": {\"actual_cpu_s_including_reaped_children\": 1.014092, \"actual_parent_cpu_s\": 0.990181, \"actual_reaped_children_cpu_s\": 0.023911, \"hard_parent_cpu_s\": 3, \"new_physical_hyrec_history_steps\": 0}}\nACTUAL_PROCESS_CPU_S 0.990182679\n"
}
```

