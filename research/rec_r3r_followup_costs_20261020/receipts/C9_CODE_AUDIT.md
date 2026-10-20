# R3R independent C9 code and evidence audit

## Verdict and independence

**PASS_SCOPED; no remaining P1 or P2 in the inspected implementation and local execution evidence.** The auditor is the separate context_intake agent, which authored neither the comparator, launcher, benchmark, plot generator nor regression tests. This review binds the earlier PHYS-MATH and PHYS-MATH-CODE inspections to the subsequently committed and actually executed source. It also independently reconstructs the saved results from bytes. Publication, remote preservation, global convergence and physical admission are separate gates.

The actual successful execution source is **1313b1f1b2c081d57bcce9c60e757ef79110df91**, tree **97423cad509a9604269740132a6ad850faf8f19a**. The earlier failed test-fixture attempt used **65ec195ec32cfcc4e918d1dd86b711fdeb5709ad**. The metadata base for this implementation review is **46ebb765d2c5c8af6d53c5b59ade1a405d4551be**. Later removal of terminal blank lines does not change which source was executed. Source hashes in the companion JSON are hashes of the executed Git blobs, not a later working tree.

## Inspected changes and binding

The source/test/workflow delta from that base contains ten additions: four scripts, two test modules, three retained-stream fixture files and one dedicated workflow. No original file under src, no R3Q worker, no C harness and no R3P solver/audit implementation is changed. The mathematical kernel, comparator control flow, launcher, benchmark and plot generator were read directly; the C9 pass also reread the final test sources and the cache-fixture correction. The 100 frozen closure files were verified by byte identity against the executed commit; this is not a claim that all 100 files received a new mathematical derivation.

The launcher requires the full expected commit, checks the frozen closure and new runtime bytes against Git, rejects symlinks, and binds the checkpoint. The before/after worker records and supervisor record agree for all **104 files**. The independent C9 readback used Git blobs at 1313b1f to check all 104 recorded SHA256 values again. The actual worker bound the NumPy backend and recorded exactly one complete stream comparison. A pass is not inferred merely from the existence of these records: the verification, comparator verdict, native binaries, extracted C source, input/output files and command logs were checked through their hashes.

The runtime uses empty, create-only Python cache prefixes before project imports. Both supervisor and worker disable bytecode writes. This addresses the real same-size/same-mtime stale-cache counterexample: -B alone stops writes but can still read an old cache. The worker's observed entry limits and cache state are recorded, rather than inferred from a fork-local preexec list. The original comparator remains the default for the opt-in launcher.

## Physics, arithmetic and failure semantics

The new comparator audits a saved native stream. It neither advances an accepted state nor changes the HyRec atomic/thermal operator, predictor recurrence, causal/stage boundaries, timestep or same-h tolerances. For a photon lane it retains the original scalar Planck expression and scalar math.expm1, followed by the same separately rounded subtraction, absolute values, products, sum and division. The relative and absolute terms remain 1e-7 times the larger occupation magnitude and 1e-10 times the blackbody occupation. There is no replacement vector exponential, fused multiply-add or reassociation of a sum.

Batching is justified by lane independence. The array path uses ordinary binary64 inputs, a pure source redshift function and inputs stable between synchronous guards. A finite accepted maximum is selected from already computed lane ratios, so no new summation error is introduced. An initial positive zero and the outer Python max preserve the reference zero tie behavior. On a nonfinite ratio or failed gate, the entire block is replayed in original scalar order. Nondefault NumPy floating-error policies take the scalar path. NaN, infinity, extreme finite values, subnormals, signed zero and immediate tolerance neighbors are covered by the new adversarial tests.

Metadata is parsed in original record order. Pending arithmetic is drained before a control record, the original 8192-line guards, EOF, or propagation of a later read/parse/metadata error. Earlier numerical failures therefore retain their diagnostic priority. Cache and array references are invalidated before each original guard, permitting the guard to mutate inputs for subsequent records. Per-tag order and arbitrary valid V/A/L interleaving are retained. The ignored HE fast path recognizes exactly the reference tag and preserves record counts and positions.

This conditional equivalence covers verdicts and exception class/message in the stated input domain. Warning locations and emission timing, asynchronous external mutation, custom impure redshift reads and allocation-failure timing are outside the equivalence claim. The record schedule of CPU guards is preserved; the actual CPU-cap outcome can change when the cost of computation changes. These limits are stated in the implementation and are not hidden by the numerical pass.

## Actual tests, failed attempt and correction

The first formal attempt is preserved with its stdout, stderr, JUnit XML, command receipt and source identity. It reported **60 passed and one failed**. The failure was solely the stale-cache test fixture: pytest itself had a private pycache prefix, while the deliberately stale subprocess looked in the default prefix and therefore read the changed source. No benchmark or pilot followed that failed attempt.

The final correction propagates the parent's cache prefix into the deliberately stale subprocess. The stale subprocess must still print 1, the fresh-prefix subprocess must print 2, and the fresh directory must remain empty. No assertion or source-binding gate was weakened. The comparator, benchmark and launcher implementation bytes were unchanged between the two formal attempts.

The successful actual command was the recorded Python interpreter with -B, a fresh -X pycache_prefix, and pytest -q -p no:cacheprovider on tests/test_r3r_stream_audit.py and tests/test_r3r_supervised.py. The raw stdout and JUnit XML independently agree on **61 passed, zero failures, zero errors, zero skips, 4.29 seconds**. The unmodified saved CSV regression was enabled by the actual worker-directory environment variable. CI can legitimately skip that optional external-raw case when only the retained fixture is present; its count must be reported separately. Repetition of these 61 tests, the first 60 passing cases, and prior R3P tests must not be added together as new unique coverage.

The suite tests full verdict/maxima-bit/guard equality, all 25000 lane bytes separately from maxima, valid arbitrary interleaving, malformed later records, earlier failures, guard exceptions and mutation, exceptional numbers, floating-error callbacks, exact HE tags, bounded block requests and source/step/resource contracts. Launcher tests reject 33, 129 and 8192 steps and event/full options before allocation, reject the wrong commit before launching a worker, and observe preservation of a real inherited CPU limit of 2/3 seconds. Earlier independent synthetic Git-binding probes are reused evidence, not rerun in C9.

## Measured acceleration and raw reconstruction

The formal benchmark audits the **unmodified 15434249-byte saved actual32 CSV**, linked to the original verification and Python history. It does not benchmark the compact HE fixture. The independent scalar lane trace and external NumPy divide trace are outside the timed trials. The measured scope includes open, parsing, allocation, callbacks, comparison and verdict assembly, with already loaded scientific inputs and a warm filesystem cache.

One warmup pair is excluded, then all five measured pairs alternate backend order. Every trial, both fresh RSS children and the lane trace have identical verdicts, binary64 maximum hex values and guard labels. C9 recomputed each pair ratio and all medians directly from the raw trial list:

| Backend | Median CPU | Median wall | Measured trials |
| --- | ---: | ---: | ---: |
| Frozen legacy | 0.109308013 s | 0.109321077 s | 5 |
| R3R NumPy | 0.080130212 s | 0.080153802 s | 5 |

The median paired legacy/candidate ratio is **1.3641298366 for CPU** and **1.3638913471 for wall**. The CPU ratios range from 1.2741042263 to 1.4095473211. All pairs remain reported, including their order and drift across this short run. The environment records Python 3.12.14, NumPy 2.3.5, an AMD EPYC 9V74, Linux x86_64/glibc 2.39 and four numerical-library thread variables set to 1. The interpreter executable has its own SHA256. Five local pairs establish a measured saved-stream audit improvement on this environment; they do not establish a platform-independent ratio, a SIMD-only effect, or a production integrator speedup.

C9 read both 200000-byte trace files directly and compared every eight-byte lane. Both SHA256 values are c174927905389fa933dc4bf5d3e89cfc32535e0721bbd58196101a1164c2bf3c; differences are **0/25000**. Independent CSV parsing reproduced the tag/j/bin encounter-order hash and all raw row counts. All ratios are finite and within the original gate; four are exactly zero and the largest is 1.5314944635351782e-5. No comparator or benchmark was rerun to produce this readback result.

## Pilot, memory and resource scope

The actual NumPy pilot completed **32 extra accepted steps and 128 FULL evaluations**, with 40 total STEP records including the eight-step prefix. It remains **SMOKE_ONLY**, with no transition event reached. Same-h parity passed, and the original common-input sample reported nine evaluations with maximum scaled RHS residual 1.1258008414394283e-13. The new pilot and the earlier profiled legacy run have identical native CSV, NPZ container, three partial binary arrays and accepted-step JSONL bytes. C9 also independently decoded the NPY headers and compared ten scientific payload fields, and checked the semantic verification fields. Timing and other execution metadata are explicitly outside that same-output comparison.

The pilot supervisor measured 3.857951 CPU seconds and 3.914853 wall seconds. A whole-solver acceleration ratio is not available because the earlier legacy run was profiled. The combined formal allocation reports 21.365609 CPU seconds and 21.497515 wall seconds, including the preserved failed test attempt and final identity hashing. Wall accounting sums supervised execution intervals and excludes intervening editing. Those figures do not purport to measure this entire research conversation or later plot/audit work.

The public launcher exposes only 1..32 steps, preserving the frozen worker's stricter smoke limit within the user's 128-step ceiling. No full/event allocation is exposed. CPU 60 seconds, wall 180 seconds and 2 GiB per-process address space remain upper bounds; inherited lower limits are clamped downward. The actual pilot worker entered with CPU 41/42 seconds and 2 GiB address space, and its later 62/63-second request was clamped to those inherited limits. Frozen Budget provides process-tree monitoring, reserve and closeout behavior. A per-process address-space bound and sampled descendant RSS are not a mathematical bound on exact simultaneous tree peak.

The comparator limits block length to 625; this run used 512. NumPy data payload is 25 bytes per persistent lane and a conservative 60 bytes per lane with temporaries, giving 30720 bytes for the actual block. This excludes Python objects, loaded history and interpreter memory. Separate fresh processes measured 88875008 bytes legacy RSS and 88887296 bytes NumPy RSS, a 12288-byte difference. Each is a single lifetime peak including imports, hashes and input setup; this supports no material memory-reduction claim. The formal wrapper's process-tree RSS samples have their own wider scope.

## Figures and independent byte audit

All four rendered PNGs were directly inspected by this auditor: cost, normalized photon residual, binary64 equivalence and fresh-process memory. Labels, all five timing pairs, zero-based cost/memory axes and scope notes are readable. The residual uses an explicitly labeled symlog axis with a linear core, retains the four exact zeros and displays the original gate. The equivalence figure displays exact zeros; its vertical padding is explicitly not a tolerance. All 25000 lanes are plotted. No cropping, misleading clipping or numerical floor was found.

C9 independently verified all twelve PNG/PDF/SVG hashes and their linkage to the benchmark and generator source. The original producer receipt remains PASS_GENERATED_PENDING_VISUAL_REVIEW with visual_review NOT_RUN. This audit and the separate VISUAL_REVIEW.json supply later direct visual review without rewriting that historical field.

The preserved c9_evidence_readback.py uses only the standard library and never imports solver or comparator code. Its actual command, exit code, stdout/stderr hashes and resource measurements are in c9_evidence_readback.execution.json. It completed on the first attempt with exit 0, **0.456176 child CPU seconds and 0.452139 wall seconds**. It independently checked 69 formal raw files, 104 executed source hashes, trial statistics, all lane bytes, same-output artifacts, twelve figure files, twelve text-normalization transformations and all seventeen archived log members. C9_EVIDENCE_READBACK.json records the results. This is a new evidence audit, not another numerical experiment or an added 69-test suite.

## CI, text normalization and preservation gates

The actual decoded log of GitHub run 39468980697, job 118787721170, was read directly. Its failure is new blank lines at EOF in twelve added files; the general pytest step did not execute. The dedicated run 39468980732, job 118787721568, completed with **60 passed and one skipped in 4.04 seconds**, using Python 3.12.15 and NumPy 2.5.4. The single skip is the optional externally preserved unmodified-raw case; the retained-stream and other contracts ran. Both exact raw log hashes and their tar archive members were independently checked against ci/SOURCE1313_CI.json. These CI tests are the same unique cases as the local suite and do not supply an independent production timing result.

TEXT_NORMALIZATION.json records the original executed source and the exact before/after hashes. C9 independently reconstructed every proposed change from the executed Git blob as removal of surplus terminal newline bytes. For the three Python files, ASTs including source locations and their hashes are identical. The numerical comparator and benchmark bytes do not change. The normalized launcher hash is distinct from the executed launcher hash and must not be substituted into the historical pilot receipt.

Successful rerun CI and final delivery HEAD remain separate shipping evidence. The initial failed CI must stay recorded, and later successful CI is not another set of unique local tests. This C9 code acceptance does not itself attest to a completed Drive/Dropbox/Library upload or remote full readback. An aborted provider call with no ACK is not preservation. The parent must attach the actual final CI, upload ACK and independent full readback receipts, or retain the corresponding unresolved shipping status.

## Separate final claim gates

| Dimension | C9 judgment |
| --- | --- |
| Mathematical correctness | PASS for the stated independent-lane audit transformation and failure-order argument; prior PHYS-MATH derivation reused |
| Numerical equivalence | PASS on the actual 25000-lane trace, recorded adversarial suite and identical 32-step outputs; not a universal cross-platform proof |
| Implementation correctness | PASS_SCOPED for inspected code, source binding, actual command evidence and resolved findings |
| Measured acceleration | PASS for the saved-stream warm-cache audit on this environment; production acceleration NOT_MEASURED |
| Memory and resource behavior | PASS_SCOPED for bounded payload and observed supervised runs; exact unsampled tree peak not established |
| Physical validity | UNCHANGED / NOT_ESTABLISHED; original U5 HOLD, REI false and global convergence hold remain |
| Production readiness | HOLD; no production admission, no global matched-grid convergence claim, final shipping gates separate |

The actionable next platform step is limited to using the source-bound launcher and an explicitly allocated 1..32-step smoke on the target platform if platform validation is still desired. No further local integration, old R3P rerun or full5210 execution is required to close this C9 review.
