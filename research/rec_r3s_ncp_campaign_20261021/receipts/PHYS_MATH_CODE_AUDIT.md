# R3S independent PHYS-MATH-CODE / final code audit

## Verdict

**PASS_SCOPED_INDEPENDENT_CODE_AUDIT.** The reviewed finite coordinator, fixed command catalogue, resource and resume contracts, validation wrapper, workflow and plotting helper are consistent with the retained mathematical and numerical contracts. No open P1/P2 finding remains in this review scope after the absolute-deadline correction at `52f884b7b27814f808b9b4f7fd5ac9a3c6283e32` and its actual targeted return.

This is a code and local contract verdict. NCP execution is `NOT_RUN`; NCP hardware and current result ownership are unverified. New NCP numerical equivalence and acceleration have not been measured. Physical validity remains `HOLD` and production readiness remains `NOT_APPROVED`.

The reviewer, `/root/context_intake`, authored neither the coordinator/tests nor the validation wrapper, workflow, theory note or plotting helper. The separate mathematical audit precedes this final review. This document may support the PHYS-MATH-CODE and final independent-code DAG gates; it represents one final independent code review, not two additional independent reviewers or duplicated test evidence.

## Source identity and inspected scope

| Role | Commit | Tree |
|---|---|---|
| R3R delivery base | `bf6bb95c58182529ad3d773a1dd0ab4f0fc7c70b` | `64c5f41587733f7e2c05ae5f862bba3a6b753f29` |
| First R3S source and 45-case execution | `96e8b88d854d1606c6204cefe2f2920f46219dff` | `a4c5005fcf93bb98df31b4a39a3431dd01d7daed` |
| Deadline correction, five targeted cases and plot execution | `52f884b7b27814f808b9b4f7fd5ac9a3c6283e32` | `eb2108cfea0cd33577afed425389cbbce2de1189` |

The actual R3R numerical and benchmark source remains `1313b1f1b2c081d57bcce9c60e757ef79110df91`. It is prior evidence, not the R3S execution source. Later delivery metadata or CI commits must retain their own identities.

The reviewer read the complete new coordinator, test file, manifest, local validation wrapper, dedicated workflow, theory note and plotting helper. The two independent evidence readbacks resolved 114 source/input entries against actual Git objects for each validation source, including all 100 frozen entries. They checked actual stdout/stderr, JUnit, driver JSON, event streams, terminal receipts, guardian receipts and effective limit records. This is more than inspection of a `PASS` string. It does not claim a fresh line-by-line audit or execution of all frozen predecessor code.

Final runtime/artifact-code SHA256 identities are recorded in the companion JSON. In particular, the coordinator is `8e53d84479a6aa026cd80f15f8e0a22494cfce69e157a82635b731770df95221`; the tests are `82e11ce853bfd639b33920a9ccc621877199ecc42f25504cec20d3b6b06c1254`; and the plot helper is `47960422855ca4ff2b86e8645786597cb1fcbc8d9006cc688cc2fb9ed2a87427`. The plot helper has its own fixed Git-blob binding in the plotting receipt; it is not silently included in the 114-file test closure count.

## Mathematical contract to code

| Contract | Reviewed implementation | Finding |
|---|---|---|
| Accepted recurrence and causal/stage ownership | Frozen quarter-continuation source; existing public R3R launcher | No RHS, predictor, Planck, tolerance, stage or accepted-history change. |
| Independent jobs require fixed input and private output | `bind_source`, `input_hashes`, `make_job`, create-only directories | Inputs and selected code must match actual fixed Git bytes; outputs are separated. |
| Dependency paths execute in order | `CATALOG`, `validate_dag`, `selected_jobs`, `choose_ready` | The first ready width is two; timed jobs are exclusive within the campaign. |
| Same-physics pilot comparison | Existing launcher with `legacy`/`numpy`, fixed 16-step arguments; `verify_job`, `matched_outputs` | Both same-h/common-input gates and raw/NPY-member byte equality remain required. |
| No implicit new full-mode allocation | Five fixed argv builders, blocked manifest nodes | JSON cannot introduce an executable full solver, Rust build or later h4 stage. |
| Resource accounting survives retries | `resume_records`, allocation registry, stable header and runtime identity | Costs must be finite, monotone and linked to the same allocation; partial/unclosed work remains blocked. |

The public catalogue contains two existing R3R trace contracts, one saved-stream replay benchmark and two existing 16-step pilots. The benchmark and legacy pilot depend on both trace checks; the NumPy pilot depends on the legacy pilot. The retained launcher itself permits only 1–32 smoke steps, below the user's 128-step ceiling. R3S passes 16 explicitly. It introduces no event adapter, 128-step promise, new h4 stage or full5210 mode.

The work/span and conditional Amdahl statements are reviewed in `PHYS_MATH_AUDIT`. They are conditional models, not observations of NCP speedup. R3R's measured component speed ratio and 25,000-lane byte evidence are `complete_reused`. The R3S local suite does not rerun those scientific comparisons.

## Resource, process and failure contracts

The coordinator installs lower-only local CPU/AS limits and requires a supported Linux host, current source/result intake, explicit CPU assignment and the selected-job allocation before execution. The guardian starts from a stdlib bootstrap, sets its CPU affinity and lower-only 60 CPU-second/2 GiB process limits before importing project code. Native thread environment variables are bounded to one. The original R3R numerical and resource helpers are unchanged.

Per-job work guards retain cleanup and receipt reserves: the guardian observes its own and descendant CPU/RSS, while the parent records setup, reaped work and closeout. The 60/180 envelope applies to each whole selected job; 2 GiB is a per-process address-space ceiling. Recorded RSS is a sampled process-tree quantity, not an exact aggregate peak. Cgroup v2 ancestor CPU/memory limits and current available memory constrain launch width. Summed RSS is not added back to available memory. Unsupported cgroup v1/hybrid configuration is rejected.

Fresh host intake must name the actual hostname, source commit, selected jobs and assigned CPUs, include hashed raw inventory, be current, and exclude conflicting use. Matching completed work is not rerun; only hash-verified completions of the same campaign header can be reused on resume. A persistent allocation record prevents moving the same allocation identifier to a fresh output directory. This is a research coordinator for the fixed public catalogue, not a generic security container or proof of exclusive ownership of all host CPUs.

Cleanup uses Linux subreaper ownership and opened process-directory descriptors. Immediate PPID is checked through the same descriptor subsequently used by `pidfd_send_signal`; cleanup repeats after adoption of further descendants. It does not signal a numeric PID chosen from a child's innermost namespace. The all-TID child union and PPID-scan fallback are local R3S additions; the frozen helper remains unchanged. Process information is still sampled and conditional on the supported kernel interfaces.

The corrected `CampaignDeadline` retains an absolute hard end. First work expiry permanently marks the deadline exhausted and arms default-action SIGALRM only for the original remaining reserve. Later broad exception handlers cannot reset that reserve. Preflight and optional final identity, input, runtime, matched-output and full-hash callbacks check expiry before and after invocation. Cleanup is limited by the original hard end. Expired work produces HOLD/incomplete closeout; if the hard end terminates the process before a terminal receipt can be written, the unclosed attempt remains a blocker rather than a success.

The plotting helper likewise charges prior spend and process startup, retains lower inherited limits, reads only hash-bound raw inputs, uses a persistent charge receipt and preserves a final hard wall deadline. It imports Matplotlib only after limits are installed. The dedicated workflow invokes only the new R3S suite; its dependency installation is separate from the formal validation command's 60/180 measurement scope.

## Findings and closure

| ID | Severity | Original problem | Final disposition |
|---|---|---|---|
| G1 | P1 | A child's innermost `NSpid` can identify a different signal target in the caller's namespace. | Closed by caller-depth mapping and descriptor-bound cleanup; source and scope tests inspected. |
| G2 | P1 | A numeric PID can be reused between a stat check and a signal. | Closed by process-directory descriptor binding, descriptor-relative PPID checks and `pidfd_send_signal`. |
| G3 | Scoped P2 | Main-TID-only child enumeration can miss a child forked by another thread. | Closed for the supported fixed jobs by the local all-TID union/fallback and explicit sampling scope. |
| G4 | P2 | Catching a one-shot campaign alarm could permit a later full hashing pass without a wall deadline. | Closed at source `52f884b7…` by durable expiry/absolute hard end and actual targeted regression. |

The original early guardian snapshot and supplemental review remain in `prepublication_review`. `CODE_FINDINGS_HISTORY.json` preserves the problems, observed sources, classifications and correction links. G4 does not retroactively turn the original 45 passing cases into failures: those cases did not exercise that path. Its correction received two new specific tests and three repeated affected dummy scenarios.

Other addressed observations include preflight/final-hash accounting, conservative memory reservation, finite resume costs, fixed runtime identity, inherited pytest options and fresh-child test isolation. No additional physics or generic process-container feature was introduced to close them.

## Actual validation and cost evidence

| Execution | Actual result | New whole CPU seconds | New whole wall seconds | Interpretation |
|---|---|---:|---:|---|
| `local_validation_001`, source `96e8b88d…` | 45 PASS, 0 FAIL, 0 SKIP, exit 0 | 3.823868 | 3.818104 | First local R3S contracts, including three actual dummy process scenarios. |
| `local_validation_002`, source `52f884b7…` | 5 PASS, 0 FAIL, 0 SKIP, exit 0 | 4.105158 | 4.019102 | Two new deadline cases plus three repeated affected dummy cases. |
| Plot production, source `52f884b7…` | One figure in PNG/PDF/SVG, exit 0 | 1.834219 | 1.847889 | Existing synthetic receipts only; no test or solver rerun. |

There are **47 unique new R3S cases**, with 50 local case executions because three affected cases were repeated. CI repetitions add no new unique cases. The previous R3R/R3P cases are not included in these counts.

All three stages use `REC_R3S_LOCAL_VALIDATION_20261021_001`. The exact prior receipt SHA and CPU/wall values are carried forward, without resetting the allowance. Cumulative validation plus plotting is **9.763245 CPU seconds / 9.685094512009528 wall seconds**, within 60/180 and with the recorded 2 CPU-second/3 wall-second final-write reserve. The second validation's effective process CPU limit is 56 seconds, reflecting the first run's spend; it is not raised back to 60. The plot records its own further reduced soft/hard CPU limits.

The first and second validation commands measured sampled test-tree RSS of 110,886,912 and 111,079,424 bytes respectively. Plot self and reaped-child RSS peaks are separately reported. These are measurement scopes, not proof of exact simultaneous process-tree peaks. The local environment is Python 3.12.14 on Linux 6.18.55, hostname `6a4240d1fd44`, with observed affinity CPUs 0–8. These facts identify the local evidence and do not identify an NCP 64-CPU/128-GB host.

The actual three process scenarios show: (1) two independent supervisor lifetimes overlap and the exclusive job starts after both predecessor terminal events; (2) a leader leaving a new-session child produces the expected blocked/HOLD result and complete owned-child reaping; and (3) a killed guardian produces the expected adopted-descendant failure and cleanup. Source hashes and effective limits are linked to those actual driver and terminal bytes. The two new deadline tests use mocked clock/signal functions; they do not claim a new real-time stress run or execute scientific work.

The independent readbacks execute no tests, solver or benchmark. Their JSON records contain the actual fixed object and raw-file inventories, JUnit names, source/tree identities, allocation chain and the distinction between unique and repeated cases.

## Figure review and hostile interpretation checks

The reviewer directly viewed the generated PNG at original resolution and read all 429 lines of its source. Nine input hashes, the plot-data file, terminal/event values, source Git blob, logs and all three output-file hashes were independently checked. The figure shows every job in the selected successful dummy case, with zero-origin cost axes, explicit seconds/MiB units, legible annotations and no observed clipping or overlapping labels.

The first two supervisor lifetimes overlap by 0.6324724809965119 seconds. This is an event-order observation, not a measured serial/parallel speed ratio. The visible title and footer identify sleeping dummy commands and exclude an NCP/solver-speedup interpretation. Setup, guardian and closeout are included in the intervals. The separate expected failure cases remain in raw receipts and this audit; they are not silently recast as successful science.

`VISUAL_REVIEW.json` closes the direct PNG review. The producer's original `COMPLETED_SYNTHETIC_PLOTS_PENDING_VISUAL_REVIEW` and `NOT_RUN_REQUIRES_DIRECT_REVIEW` fields remain unchanged in its original bytes. PDF/SVG byte identity was checked; direct visual review is claimed only for the PNG. This is an internal scheduling-contract figure, not a new physical residual/convergence result.

## Separate final claim gates

| Claim | Verdict |
|---|---|
| Mathematical correctness | PASS for the fixed-job independence conditions, retained recurrence contract, conditional work/span and Amdahl algebra. |
| Numerical equivalence | R3R evidence is `complete_reused`; new NCP equivalence is `NOT_RUN`. No new numerical payload implementation is introduced by R3S. |
| Implementation correctness | PASS for reviewed source and local contract evidence, including the deadline correction; conditional host gates remain. |
| Measured acceleration | `NOT_MEASURED` for R3S/NCP. R3R's component audit ratio remains separately scoped prior evidence. |
| Memory and resource behavior | Local observed limits/accounting and selected dummy cleanup PASS; RSS scope is sampled and NCP behavior is unverified. |
| Physical validity | `HOLD`; original U5 failures and missing global convergence evidence remain. |
| Production readiness | `NOT_APPROVED`. |

NCP access/current-host result intake, actual target hardware, explicit fresh campaign allocation, pending scientific DAG stages, final delivery CI and external preservation are separate gates. This audit does not claim their completion. The original h/h2 U5 holds, `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, global h/h2/h4 convergence `NOT_RUN`, and absence of a new full5210 allocation are preserved.

## Primary interface sources

- Linux `pidfd_send_signal(2)`, https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html — inspected documentation supports using an opened process-directory descriptor and explains the PID-reuse distinction. The reviewed page identified man-pages 6.19, manual date 2026-02-08.
- Linux proc filesystem documentation, https://www.kernel.org/doc/html/latest/filesystems/proc.html — inspected process namespace, per-task child-interface and RSS semantics. Concurrent proc observations and sampled RSS are not exact snapshot/aggregate-peak guarantees.
- The repository source and actual receipts identified above are the primary evidence for this implementation. No external solver was transplanted into HyRec.
