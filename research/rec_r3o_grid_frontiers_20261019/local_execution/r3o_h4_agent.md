# R3O independent h4 start — implementation handoff

## Outcome and ownership

**Implemented; actual bounded original-C/Python same-h start comparison PASS; independent review is pending with the parent.**

Workspace: `/workspace/scratch/afe554957b2e/rec_work` is a restored source capsule, **not a Git checkout**. Supplied parent identity: PR108, `23e0a3a6c439a1f015aa8f7380f4eedf0b569df7`. No local Git HEAD is claimed. This assignment performed no GitHub, remote backup, Library, or parent DAG mutation. Parent owns intake reconciliation, independent review, publication and backups. The requested implementation files and local evidence are ready for those actions.

Applied skill: `physmath-research-loop` canonical 1.0.0, resuming implementation stages using the existing source contract. C9 is assigned to the parent by the explicit current task; the checks below are implementation verification and independent **code-path** C/Python comparison, not an independent human/agent review. No additional agent was launched or represented as executed.

## Files to publish

All paths below are relative to the source capsule. Every file is new and owned by this h4 task. No existing shared module was edited; no shared-module patch is needed for this implementation.

| File | Bytes | SHA256 |
|---|---:|---|
| `scripts/c_harness/original_hyrec_r3o_h4_start_harness.c` | 5,786 | `8b50858c0e0a3d1e6eef19e9f159673156162f70a7363b51945a9f238aa2ec8a` |
| `scripts/plot_r3o_h4_start.py` | 4,610 | `cb365f36c299334e45c56ae5fd4d6ca65e742dab4346459f2233f42bf8f9eabd` |
| `scripts/verify_r3o_h4_start.py` | 25,224 | `96e03f326342940606dba33dd44d8f172d5bb6a773dc15f404635babca6f4deb` |
| `src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py` | 18,618 | `6247e0681d74e5b6f26f9818faf4a49af4ce61e64e4970bfe3b7c21ad951fd10` |
| `tests/trajectory/test_r3o_h4_start.py` | 11,533 | `50dceee1c92e1ab3baa50c468955affac47c6639dcd3714a492e1bb542e43359` |

The Python core subclasses only the original frozen cosmology parameter object to override `izH0` and `redshift`. It reuses reviewed clock-free Saha, helium rate, steady-temperature and atomic source formulas. Its He and FULL integration loops are separate, explicit h4 loops. It neither rebinds h2 globals nor loads h2 checkpoint data. The original C ABI wrapper is reused as source text only and compiled with the same temporary h4 header as the native reference.

## Source identity and equations

Frozen ZIP:

`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`

SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

All extracted member hashes and the exact diff are in `r3o_h4_runs/start_002/source_manifest.json`. The source change is confined to one active header token in a fresh temporary extraction:

```diff
-#define DLNA          8.49e-5
+#define DLNA          (8.49e-5/4.)
```

The full original line comments, all other header bytes, the original `history.c`, `helium.c`, `hydrogen.c`, rate tables and frozen ZIP remain unchanged. The modified temporary header SHA256 is `46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f`. Hashes were checked again after the run; source/input mutation check PASS.

Original source identities include:

- `history.c`: `8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976`.
- `helium.c`: `1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece`.
- `hydrogen.c`: `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`.
- Original `hyrec_params.h`: `cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2`.

The quarter-step clock is `DLNA = 2.1225e-5`, binary64 `0x1.6418ae4caf054p-16`. Accepted states use `z_i = 8001 exp(-DLNA*i)-1`. The original floor expression gives `izH0=72892`. The post-Saha helpers use their original multiplicative endpoint `(1+z_in) exp(-DLNA)-1`; accepted output rows then use the absolute grid clock. These two floating-point expressions are retained in their original roles.

HeIII evolves through `rec_xesaha_HeII_III` Saha closure until `xHeIII <= 1e-8`. The HeII stage preserves the source post-Saha finite differences, the `DXHEII_MAX=1e-5` switch and the source predictor `y_next = y + DLNA*(1.25*F_current - .25*F_prev2)`. Hydrogen is Saha-closed during He; matter temperature follows original source steady state. FULL H+He preserves the joint helium update, neutral-hydrogen post-Saha solve and `DXHII_MAX=3e-4` switch. `XHEII_MIN=1e-6` is unchanged.

The source `DLNA` dependency in the FULL atomic path is through accepted-time ownership and `fplus_from_fminus` / `interp_Dfnu` two-neighbor history interpolation. The instantaneous original atomic matrix, escape factors, outgoing spectra and average `v/x1s` formula have no additional DLNA parameter. The same original table supplies all 311 virtual bins and three outgoing Lyman bins. Native memory allocation is bounded to the requested photon prefix plus one scratch column; the original `param.nzrt` value is retained.

For the physical `Tm=Tr` post-Saha limit, the Python adapter retains the reviewed h2 inclusive-table binary64 `nextafter(Tm,0)` treatment before the K-to-eV multiplication. This rounding convention is recorded rather than silently replaced. No atomic or thermal fit, altered stage threshold or source operator was introduced.

## Units and predictor ownership

Public temperatures are K, H is s^-1, nH is m^-3, abundances are per H nucleus, and derivatives are with respect to dimensionless ln(a). The original hydrogen source consumes nH in cm^-3 and temperatures in eV; photon departures are dimensionless occupation numbers.

He history output row `i` stores the RHS evaluated at input row `i-1`. Initial predictor arrays have rows `[He,H]` and columns `[prev2,prev]`. The initial input indices are `[72890,72891]`. Hydrogen seeds use original central differences of **independently evolved h4 xe**, divided by `2*DLNA`, minus the corresponding He derivative. A test changing the denominator to h2 detects the difference.

At the accepted endpoint `iz=72900`, `final_predictor` owns RHS input indices `[72898,72899]`. The source consumes `prev2` in its next update. Both derivative columns are retained even while hydrogen remains post-Saha. Trial post-Saha derivatives are not stored as accepted predictor memory. Only current-state FULL outputs become committed photon columns; trial outgoing fields are discarded. Diagnostic C callbacks receive detached read-only copies of past columns and return comparison data only.

## Actual local results

Execution location: **ChatGPT sandbox Linux**, not NCP and not GitHub Actions. Runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, gcc 13.3.0, Linux x86_64/glibc 2.39. Compilation flags include `-O2 -fno-fast-math`; one CPU affinity and single-thread numerical library settings were used by the CLI.

`start_002/verification.json` reports `PASS_SAME_H_START`:

| Check | Actual scope/result |
|---|---|
| Independent He history | 72,893 rows: 30,858 HeIII Saha + 42,035 HeII rows |
| He state discrepancy | max scaled xe difference `2.2080761383365098e-16`; z and Tm differences zero |
| He common-input RHS | max `1.6653345369377348e-16`, limit `2e-10` |
| He trajectory RHS | max `3.3306690738754696e-16`, limit `2e-10` |
| FULL start | 8 accepted steps; 9 state nodes; 32 Python FULL evaluations |
| Common-input C source | all 32 evaluations; max RHS scaled difference `2.0511717324644962e-13` |
| Integrated FULL states | xHII, xe and Tm differences zero; max absolute xHeII difference `5.421010862427522e-20` |
| Integrated H RHS / memory | max scaled discrepancy `2.219023576000012e-13`, limit `2e-7` |
| Integrated He RHS | max scaled discrepancy `4.5102810375396984e-17` |
| Outgoing virtual photon ratio | maximum `6.131840645486276e-6` of allowed tolerance |
| Average virtual photon ratio | maximum `7.883083461150054e-6` of allowed tolerance |
| Lyman photon ratio | maximum `4.192518230086996e-6` of allowed tolerance |
| Matrix residual | maximum `2.8638673618951863e-16` |
| New lightweight unit tests | **12 PASS**, standard unittest; existing h2 defaults exercised as invariant assertions |

The frozen photon tolerance remains `1e-7*max(abs(Python),abs(C)) + 1e-10*fBB`. Existing state, RHS, matrix and ledger tolerances were reused.

Endpoint:

```json
{
  "Tm_K": 4640.930888457957,
  "iz": 72900,
  "post_saha": true,
  "xH1s": 0.0007169778568651695,
  "xHII": 0.9992830221431348,
  "xHeII": 0.00019578778159580303,
  "xe": 0.9994788099247306,
  "z": 1701.783106428126
}
```

The saved photon prefix has `virtual_out[311,8]`, `average_virtual[311,8]` and `lyman_out[3,8]`. Python checkpoint SHA256 is `40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef`, 43,904 bytes. The complete independent He NPZ SHA256 is `0b4e1911cb32c40f3bec6cefbc0c138ec635d4d25f2a0a6e504c812718529f93`, 2,680,322 bytes. Native raw stdout is 14,799,940 bytes. Load NPZ with `allow_pickle=False`.

The CLI supports an isolated He-only mode; its He algorithm was exercised within the successful start run. A separate `--mode helium` CLI execution was not needed or performed. No h4 continuation beyond this eight-step prefix was run.

## Runtime accounting and preserved attempts

External driver receipts sum to **12.862082 CPU seconds**, including Python startup, native compiler/execution children and plotting. This is below the requested approximate 30 CPU-second lightweight allowance. The successful start driver used 4.353667 CPU seconds and 4.478078859 wall seconds. Its internal execution-body measurement is 3.335698 CPU seconds and begins after Python imports. These are distinct scopes. Peak Python RSS for the successful start was 126,550,016 bytes.

| Receipt | Outcome | CPU seconds, full subprocess tree |
|---|---|---:|
| `start_001_driver.json` | shared C build failed before native trajectory or Python integration | 2.229467 |
| `tests_001.json` | pytest unavailable; no tests collected | 0.012108 |
| `tests_002.json` | 12 unittest tests PASS | 1.720007 |
| `start_002_driver.json` | actual C/Python bounded h4 start PASS | 4.353667 |
| `plot_001_driver.json` | retained-data figure generation; no new integration | 4.546833 |

The first build failed because original `hydrogen.h` lacks include guards and the reused ABI wrapper caused a duplicate include. Only the new h4 harness conditional include was corrected. `start_001` preserves stderr, failure record, source manifest and the then-current new producer sources. The missing pytest attempt is an environment failure; the new test module was converted to standard unittest and then executed successfully. No pytest PASS is claimed and the existing pytest h2 suite was not rerun here. Previously validated h2 code behavior is preserved by unchanged source bytes and no global mutation.

## Self-checks and plot reading

The 12 tests cover all-row clock ownership, initial Saha closure, helium/electron ledgers, exact two-memory seed mapping, h2 denominator mutation, h2 input rejection, bounded step counts, 1- and 2-step prefix memory, immutable output arrays, callback isolation/nonfinite C rejection, source-cosmology mismatch, first active h4 causal photon edge/future rejection, exact temporary-source diff, incomplete/duplicate/contaminated native output, no-pickle checkpoint roundtrip and refusal to overwrite outputs. Parameterized subcases are included inside those 12 unittest methods.

Residual figures were generated from the retained actual C/Python outputs and visually inspected. The He panel's maximum state tolerance ratio is `1.1040380691682548e-4`; the FULL photon panel peaks at `7.883083461150054e-6`, both below the unchanged acceptance line 1. A graphical floor of `1e-9` is used; exact values including subfloor values are retained in `r3o_h4_plot_inputs.json`. The figure supports the same-h start comparison. It does not supply three-grid physical convergence or an independent review.

## Evidence paths

All local paths below are absolute:

- Machine-readable implementation evidence: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_implementation_evidence.json`.
- Initial/shared-input hashes: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_baseline.json`.
- Main actual receipt: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/verification.json`.
- Full checkpoint: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/python_h4_full_start.npz`.
- Complete He history: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/python_h4_helium.npz`.
- Original C raw output: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/native_oracle.stdout`.
- Original member hashes / exact header diff: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/source_manifest.json`.
- New producer code snapshot used for actual parity: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_002/producer_snapshot`.
- Failed first C attempt and snapshot: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/start_001`.
- Unit test log: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/tests_002.log`.
- Figure PNG/PDF and numerical plot inputs: `/workspace/scratch/afe554957b2e/rec_recovery/r3o_h4_runs/plot_001`.

Full hashes and sizes of all selected artifacts and all five new code files are in the machine-readable evidence JSON. The source ZIP, original h2 Python module, h2 CLI, h2 C harness, shared causal gather, shared atomic module and HMLA adapter were rehashed and match the initial capsule bytes.

## Runnable commands for the parent/NCP handoff

No checkpoint preparation, downloaded C trajectory, or external file handoff is needed. The repository/capsule contains the frozen source ZIP and all code. Output directories must be fresh; the CLI refuses an existing path.

```bash
cd /workspace/scratch/afe554957b2e/rec_work
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m unittest discover -s tests/trajectory -p test_r3o_h4_start.py -v
python3 scripts/verify_r3o_h4_start.py \
  --mode start --steps 8 --cpu-seconds 20 --wall-seconds 60 \
  --evidence-dir /tmp/rec_r3o_h4_start_fresh_001
python3 scripts/plot_r3o_h4_start.py \
  --evidence-dir /tmp/rec_r3o_h4_start_fresh_001 \
  --output-dir /tmp/rec_r3o_h4_plot_fresh_001
```

On NCP replace only the `cd` location with the restored repository location. Standard requirements are Python with the existing NumPy/SciPy dependencies, gcc and libm; plotting additionally uses matplotlib. The CLI compiles the reference itself from a temporary source copy. Its only accepted FULL extent is 1..8 steps.

## Parent DAG action and remaining scope

Parent can mark the independent h4 **start implementation and local same-h comparison** complete, attach these exact artifacts, then perform its independent review and publication/backups. The next production node starts from the independently produced h4 endpoint, its full accepted photon prefix and both H/He derivative memories. Existing h2 continuation modules have hardcoded h2 clock/index contracts and should not consume this h4 checkpoint.

Full h4 recombination, global z=8000..0 h/h2/h4 convergence, new production speedup and Bianchi/REI/CMB approval remain outside this completed bounded start. Existing U5 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, closed historical cost ledger and `REI activation=false` remain unchanged.
