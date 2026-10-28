# C7 — 132개 source-point primary 실제 실행

판정: **PASS_SCOPED_PRIMARY_CAPTURE_C8_NUMERICAL_ACCEPTANCE_PENDING**.
C6의 실제 게시와 이중 백업 완료 뒤 root가 승인한 명령을 정확히 한 번 실행했다.

    python3 code/run_stage.py C7

기존 C6 shared library와 code/input locks를 재사용했다. 새 compile이나 이전 history 재적분은 하지 않았다. 이번 C7는132개 final writer에 대한 새 FULL point kernel 호출이다. 아직 실행하지 않은 C8의 authoritative parity/residual 판단을 C7 PASS에 포함하지 않는다.

## 실제 결과

| 항목 | 실제 관측 |
|---|---:|
| Primary raw records |132|
| Unique call_id/slot |132|
| 새 kernel calls |132|
| Status0 |132|
| 472-events points |132|
| 전체 divisor value events |62304|
| Zero/nonfinite/overflow divisor |0/0/0|
| Caller input nonmutation |132/132|
| Initialized table nonmutation |132/132|
| 이번 table context initialization |1|

Writer index는0부터131까지 순서대로 기록되었다. C6에서 실제 결속한132writer/313query/626endpoint mapping을 재사용했고 원 geometric endpoints/query/exact alpha는 수정하지 않았다. CALLS dispatcher 입력과 WRITES coefficient temperatures를 구별했으며, primary의 실제 출력 coefficient temperatures는 각 저장 WRITES와 일치했다.

원 scalar, matrix/source, xr/xv,472divisor와 actual input을 hex로 보존했다. Raw API별 파일과 primary 분할 파일은 execution/C7_attempt001/에 있다. 각 분할 파일의 실제 크기는 coding/C7_PRIMARY_SUMMARY.json에 기록했다. 파일을 원래5MiB 제한 아래로 분할했다.

**132점의 FH parity, FH/xr/xv bitwise count와 independent Decimal80 block residual은 C8 PENDING**이다. C7의 status/finite/divisor/nonmutation 통과만으로 그 결과를 미리 주장하지 않는다. C6 baseline1점의 기존 검증과 C7의 전체132점을 구별한다.

## 실제 자원과 누적 비용

Worker userCPU는0.43660699999999997s, systemCPU는0.088887s이며 합계는 **0.5254939999999999s**다. Wall은0.5283391420016414s, maximum RSS는72656KiB다. 이번 clipped cap20CPU/30wall/512MiB/single-thread를 지켰다. Watchdog reason은없다.

Known scientific-child 누계는 **1.564361s/60s**, 잔액은 **58.435639s**다. R7remote0.06227과 C6의 최초실패·진단·재시도 비용을 모두 보존했다. C6 source calls2와 이번132를 합친 known native calls는 **134**이며 initial146cap 이하이다. Unfinished API attempt는0이다. Parent/network/model/metadata/packaging 미관측 비용은 UNKNOWN_NOT_ZERO다.

## 인계

- Actual RESULT와 raw: execution/C7_attempt001/.
- Resource receipt: execution/C7_attempt001/RESOURCE_RECEIPT.json.
- 실제 요약: coding/C7_PRIMARY_SUMMARY.json.
- 누적 비용: execution/RESOURCE_LEDGER.json.

C8은 아직 승인되지 않아 실행하지 않았다. 자동 재시도·원격 mutation0, old producer/reference/native full history/oldtests/BGJET audit/QSS03 certificate replay0이다. Canonical28/88+0, separate REI33/88, physical0/313과 physical query/K/M2/defect/L/tube/e0/epsilon/outgoing null, H6/H7OPEN,L4false,REIactivationfalse를 유지한다.
