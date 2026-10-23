# cosmosapjw-quantum/rec_bianchi 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "thermal/rec_bianchi_LONGTERM_CONTRACTS.json": {
    "schema": "longterm_pr_contracts.v1",
    "as_of": "2026-10-23",
    "repository": "cosmosapjw-quantum/rec_bianchi",
    "no_merge": true,
    "no_activation": true,
    "scientific_status": "scoped_only",
    "protected_holds": "All existing holds remain; no unit-completion percentage for total physical goal"
  }
}
```


## REC-LINE02

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/0`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-LINE02",
  "title": "Reuse completed exclusive native line source adapter",
  "depends_on": [],
  "status": "science_complete_scoped_final_delivery_receipt_pending",
  "entrypoints": [
    "research/rec_line_native_owner_20261023/FROZEN_CONTRACT.md",
    "research/rec_line_native_owner_20261023/LOOP_PROGRESS.json",
    "research/rec_line_native_owner_20261023/results/attempt001/SUMMARY.json",
    "research/rec_line_native_owner_20261023/code/native_line_owner.py"
  ],
  "inputs_domain": "one immutable z1099.99865 native313 source, direct Lyalpha+blue owner, unchanged virtual blocks",
  "equations_scope": "M*=M+delta_r eeT; s*=s+delta_rb e; Sherman-Morrison/Schur and conditional frozen-block JVP",
  "claim_gates": [
    "194 primary checks and same independent review complete, material blockers0; actual3PNGs inspected; final provider receipt separate",
    "rank/full5e-10; backward5e-12; JVP5e-9; conservation64eps scale"
  ],
  "pass_action": "Reuse completed frozen adapter; owner final delivery receipt remains separate; proceed to history-boundary contract without replay",
  "budget": "Primary already consumed; six historical review probes spent and not repeated; no new review/probe/replay",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate",
  "source_pin": "a7c46fd8338971e2cefa776f5dd7b25a46974990",
  "previous_pin": "a06dd8b876ba116aadde02a35a2cf8bb2daaa03a"
}
```


## REC-HISTORY

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/1`. 내부 선행: REC-LINE02. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-HISTORY",
  "title": "Native outgoing boundary and incoming/outgoing history owner",
  "depends_on": [
    "REC-LINE02"
  ],
  "status": "selected_next_not_run",
  "source_pin": "a7c46fd8338971e2cefa776f5dd7b25a46974990",
  "entrypoints": [
    "research/rec_line_native_owner_20261023/GLOBAL_DAG.json",
    "research/rec_line_native_owner_20261023/vendor/hydrogen.c",
    "research/rec_line_native_owner_20261023/THEORY.md"
  ],
  "inputs_domain": "Actual native boundary storage/interpolation; finite outgoing occupations and causal incoming history, same source/frame convention",
  "equations_scope": "Native history boundary flux and photon number/energy ledger; differentiate actual history map separately from frozen partial JVP",
  "claim_gates": [
    "Read and pin actual boundary/interpolation owner; exclusive outgoing/incoming ledger without source duplication",
    "Freeze finite physical acceptance and interpolation-error allocation before code; quantitative calibration obligation currently open",
    "No global/coupled history claim from LINE02 frozen194checks"
  ],
  "pass_action": "Admit finite history-boundary adapter into REC-FIELD/coupled dependency contract",
  "budget": "Theory/read-only first; no old campaign replay or new IVP; fresh bounded finite-case budget to freeze only after source owner known",
  "fail_action": "Preserve source ownership failure; repair affected map only",
  "review": "Independent changed-source review, science vs packaging separate"
}
```


## REC-C3

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/2`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-C3",
  "title": "Exact per-state primitive sharing design and implementation",
  "depends_on": [],
  "status": "planned",
  "entrypoints": [
    "research/rec_saved_diagnostic_reuse_20261023/NEXT_STAGE_C3.md",
    "research/rec_saved_diagnostic_reuse_20261023/FORMULA_CODE_MAP_KO.md"
  ],
  "inputs_domain": "Pinned PR126512 saved states from PR124; full63 state/model/branch identity",
  "equations_scope": "Context lifetime one exact input; share geometry7/network3/thermal2 duplicate evaluations; preserve independently formed gas-energy totals and all masks",
  "claim_gates": [
    "Design exact context ownership; no rounded/global cache key",
    "Reuse original parity/mask gates; freeze minimum affected comparison before coding",
    "Paired alternating timing only after equivalence; no assumed2x gain"
  ],
  "pass_action": "Accept implementation for saved-diagnostic consumers, then measure bounded identical-workload cost",
  "budget": "600s cumulative;81.3665s recorded spent; upper remainder518.6335s subject later ledger; newIVP0",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## REC-LI

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/3`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-LI",
  "title": "Admit source-resolved Li ionic/thermal yields",
  "depends_on": [],
  "status": "planned",
  "entrypoints": [
    "research/rec_rei_thermal_yield_20261022/NEXT_SOURCE_INPUTS.md",
    "research/rec_rei_thermal_compton_20261022/REPORT_KO.md"
  ],
  "inputs_domain": "Selected 5–200eV source domain; distinguish THERM02 from PR124 and in-band resonances",
  "equations_scope": "Exclusive final ionic charge/level/electron count + photon/electron energy per event",
  "claim_gates": [
    "Primary source labels, units, thresholds and energy ownership fixed",
    "Quantitative interpolation/source uncertainty currently UNCALIBRATED; obligation calibrate against independent same-domain witness before accepting physical error bound"
  ],
  "pass_action": "Implement only admitted channel adapter and recheck isotope/compact lift on affected frozen states",
  "budget": "No new IVP selected; inherit THERM ledgers, no reset; fresh input-admission cap must be frozen before numerical study",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## REC-FIELD

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/4`. 내부 선행: REC-LINE02. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-FIELD",
  "title": "Actual spectral radiation and thermal exchange ledger",
  "depends_on": [
    "REC-LINE02"
  ],
  "status": "planned",
  "entrypoints": [
    "research/rec_line_native_owner_20261023/THEORY.md",
    "research/rec_rei_thermal_compton_20261022/REPORT_KO.md"
  ],
  "inputs_domain": "Same normal frame, actual photon spectrum versus prescribed Planck bath; signed source",
  "equations_scope": "du_gas+du_rad+du_internal+du_reservoir=0; tensor injection independent from stored stress",
  "claim_gates": [
    "Exclusive line/reservoir owners; no passive debit treated as backreaction",
    "Source/model interpolation accuracy requires calibration obligation, separate from floating conservation gate"
  ],
  "pass_action": "Supply explicit residual/JVP for selected spectrum and thermal reservoir",
  "budget": "Theory + frozen-state affected tests only; no history replay; numeric scope/budget not yet admitted",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## REC-COUPLED

원본: `thermal/rec_bianchi_LONGTERM_CONTRACTS.json/nodes/5`. 내부 선행: REC-LI, REC-FIELD, REC-HISTORY. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "REC-COUPLED",
  "title": "New self-consistent selected-scope control",
  "depends_on": [
    "REC-LI",
    "REC-FIELD",
    "REC-HISTORY"
  ],
  "status": "input_dependent",
  "entrypoints": [
    "research/rec_line_source_20261023/GLOBAL_DAG.json",
    "research/rec_rei_thermal_compton_20261022/DAG.json"
  ],
  "inputs_domain": "Explicit selected atomic/nuclear/thermal source manifest and retained-array inputs",
  "equations_scope": "Atomic/spectral/thermal/Einstein source-reservoir coupling; extra nuclear channels conditional on daughter admission",
  "claim_gates": [
    "All selected source gates closed; predeclare error allocation and independent oracle",
    "Global convergence remains separate; prior U5 holds never reset"
  ],
  "pass_action": "Only after source closure approve genuinely new bounded control; subsequent global convergence and production each independent",
  "budget": "NOT_SCHEDULED; no newIVP authorized by plan; reuse completed cohorts",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `REC-LINE02` → `REI-L1`: selecting native line source. Consume completed owner result only; active owner reservation remains


- `REC-LINE02` → `WU_SPECTRAL_GEOMETRY_COUPLING`: selecting native line in WU spectral coupling. One native line owner; no detached/native double counting


- `REC-FIELD` → `REI-L1`: selecting actual spectral radiation/Compton exchange. Planck and actual-monopole baths remain distinct
