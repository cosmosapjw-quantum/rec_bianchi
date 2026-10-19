# Independent review and closure

Reviewer: actual native agent `Einstein`, id `01a15280-ce1a-7586-980b-2de4a8a57089`.
The main worker and reviewer ran separate probes; this record does not claim an external human review.

## Initial review disposition

The initial review found two blocking implementation defects: diagnostic finalization could mask the primary exception and leave a phase frame, and launcher receipt/profile closeout could mask a verifier failure. Both were fixed before publication. The initial reviewed adapter hashes were `7e4ec6bd7668c315d005a24aab09bcdcd206bb389e7053b59abba5275a676b6d` and `7a5198371ebc3e65ec0ee553fb480ccc8e26dc7953b77c81e22a12893088d8e6`.

The reviewer independently reread storage benchmark pair 0: the container hashes, five unique uncompressed NPY members and their receipt hashes matched; compressed/stored ZIP methods were 8/0. The reviewer independently checked the unchanged verifier, C harness and V6 manifest identities, not all 109 closure files. The two-point cost fit was accepted only as a descriptive extrapolation; full-run cost and the missing PR105 detailed raw evidence remained unresolved. There were no scientific runs or campaign reruns by the reviewer. The extractor and benchmark pairs 1/2 were outside that initial independent scope.

## Narrow closure report (verbatim)

**Both exception-handling findings are closed for the updated revisions I reviewed.** I read both source files and all five added regression-test definitions. I also completed five independent, memory-only fault-injection probes against the imported implementation. All five passed.

### Closure findings

**1. `PhaseLedger.measure()` preserves the primary exception and clears its frame.**  
In [r3l_u6_cost.py](../../scripts/r3l_u6_cost.py), `PhaseLedger.measure()` at line 62 now removes the frame before diagnostic finalization. Failures in the ending clock or end-event emission are recorded in `profiling_errors`, invalidate the accounting, and attach a note to an existing primary exception. My probes confirmed that the original exception object survives, the stack is empty, and the summary reports `INVALID_PROFILING_ERROR`.

**2. `execute()` preserves verifier failures through closeout.**  
In [run_r3l_u6_profiled.py](../../scripts/run_r3l_u6_profiled.py), `execute()` at line 51 retains the primary exception and its traceback through receipt handling, profile output, and journal closeout. Secondary failures are recorded separately. My probes confirmed preservation of the original `SystemExit` object and its verifier traceback origin, together with restoration of `sys.argv` and every instrumented verifier binding.

### Independently checked fault cases

| Injected fault | Observed result |
|---|---|
| Invalid ending clock while the measured body raises | **PASS:** original exception preserved; stack empty; accounting invalid. |
| Failed end-event emission while the body raises `SystemExit` | **PASS:** same `SystemExit` preserved; stack empty; diagnostic failure recorded. |
| Malformed raw receipt after verifier failure | **PASS:** same primary exception preserved; raw contents unchanged; SHA-256 retained; `UNREADABLE_PRESERVED` and the parsing error recorded. |
| Failed profile output after verifier failure | **PASS:** same primary exception preserved; `profile_save` failure recorded in the final journal event. |
| Successful verifier followed by a receipt parsing failure | **PASS:** the profiling operation raises `JSONDecodeError`; the closeout failure is not silently accepted. |

The five regression definitions in [test_r3l_u6_cost.py](../../tests/trajectory/test_r3l_u6_cost.py) cover these cases. **I read those tests; I did not execute the repository’s filesystem-writing unittest suite.** My independent probes used an in-memory output filesystem and simulated verifier bodies, so they establish exception and restoration behavior, not physical disk durability.

I also confirmed the timing summary explicitly places its endpoint before profile closeout and names the excluded tail. That resolves the measurement-boundary ambiguity within this change.

### Reviewed revisions and scope

| File | SHA-256 prefix |
|---|---|
| `r3l_u6_cost.py` | `5be50dd40e895a9b` |
| `run_r3l_u6_profiled.py` | `e8f6c08425cdd4d6` |
| `test_r3l_u6_cost.py` | `7b31c0de38d27310` |

**No residual blocker remains from these two findings.** This was a narrow closure review: no writes, scientific executions, campaign reruns, or broad audit. Source binding, serialization parity, the extractor, and scientific/budget evidence were not reassessed in this pass; the earlier cost-model limitation and PR105 raw-link evidence gap remain unchanged.
