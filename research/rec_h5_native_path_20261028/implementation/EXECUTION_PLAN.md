# C4 execution plan — authorization pending

Current state: source/map/design prepared. No scientific code execution, build,
native capture, saved-data analysis, controls or figures has occurred. Root
publishes C1–C4 before releasing C5 implementation. Native build/run needs root's
separate RUN_READY after C5 source review. This document does not supply release.

## Proposed fixed CLI and sequence

Run from the existing repository root. Proposed runner interface is one mode
argument, with immutable internal ceilings and unique output directories:

```sh
python3.12 research/rec_h5_native_path_20261028/code/run_bounded.py --mode build001
python3.12 research/rec_h5_native_path_20261028/code/run_bounded.py --mode capture001
python3.12 research/rec_h5_native_path_20261028/code/run_bounded.py --mode analysis001
python3.12 research/rec_h5_native_path_20261028/code/run_bounded.py --mode controls001
python3.12 research/rec_h5_native_path_20261028/code/run_bounded.py --mode figures001
```

The root must adopt this concrete interface before execution; the mathematical
contract already fixes the modes and caps. Each mode creates an exclusive
results/<mode>/ attempt record. Native copied source is build/source and the
instrumented executable is a build artifact. No unique-directory override or
implicit retry is used to disguise a repeated capture.

| Mode | CPU ceiling | Wall ceiling | Planned action |
|---|---:|---:|---|
| build001 |30s |60s | Lock checks, canonical copy/instrumentation/diff, one GCC executable build |
| capture001 |60s |120s | One complete native trajectory, original stdin; detailed window only |
| analysis001 |60s |120s | One saved-capture source-parity/recurrence/313join pass |
| controls001 |30s |60s | One18-control pass with saved/small records |
| figures001 |20s |60s | Saved-data-only2PNG and1multipagePDF |

Every child has1GiB address-space limit, one-thread environment and process-group
wall timeout, with limits installed before child execution. The five normal
caps total200CPU seconds inside the implementation cumulative300CPU ceiling.
The remaining100CPU is reserved for root-authorized diagnosed repair, not
available for automatic retries. Independent review120CPU and packaging60CPU
remain separate. Previous-unit budgets are neither reset nor transferred.

## Planned native compiler/executable invocation

The root contract fixes GCC -O3 -D_DEFAULT_SOURCE, no fast-math, and -lm.
The intended build adds the observation macro/helper and uses the original
five translation units plus capture_support.c:

```text
gcc -std=c11 -D_DEFAULT_SOURCE -O3 -Wall -Wextra -Wpedantic
    -DREC_H5_NATIVE_PATH_CAPTURE
    hyrectools.c helium.c hydrogen.c history.c hyrec.c capture_support.c
    -lm -o <owned instrumented executable>
```

Execution cwd is build/source, stdin is its byte-identical original input.dat.
The main function continues its original full trajectory and ordinary stdout.
No separate canonical or guard-off run is scheduled. No prior reference, HD,
KS, PB, GEO, native admission tests or historical campaigns are rerun.

## Evidence and finite progression

Before child launch record exact argv, mode, source/diff/input hashes, Python/
compiler identity and thread environment. Preserve stdout/stderr, exit, CPU
user/system totals including child processes, wall time, peak RSS and timeout
status. After completion recheck immutable inputs and retain resulting data
identities. Code/model routing request and actual observed runtime metadata
remain distinct; model identity is not asserted observable.

Capture enforces global hydrogen call cap200000 and detailed-window cap40000,
preserving the event prefix on failure. Analysis consumes the saved capture and
locked old data only. Each subsequent mode is dependency-gated by prior raw
success and root's authorized progression. A failure returns its concrete
evidence to root; it does not trigger a second native capture to repair analysis.

Scientific completion requires source/diff/raw/figure review by an independent
Astra reviewer. The numerical pass is not inferred from the number of receipts
or from a smoke import. Publication, backup ACKs and final DAG return stay with
root. All physical operands remain null and physical coverage remains0/313.
