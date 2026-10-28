# C8 — 저장 primary의 독립 검증과 incoming controls

판정: **PASS_SCOPED_C8_NUMERICAL_VALIDATION_PENDING_C9**.
C7의 실제 게시와 이중 백업 완료 뒤 root가 승인한 명령을 정확히 한 번 실행했다.

    python3 code/run_stage.py C8

C8 validation과 plot은 별도 bounded child로 실행했고 모두 exit0/PASS였다. 저장된132개 primary output을 검증했으며 C7 primary를 다시 실행하지 않았다. 새 native 호출은 사전 지정한9개 incoming controls뿐이다. C9의 fresh nonauthor review와 C10 delivery는 아직 별도 단계다.

## Authoritative132-point 결과

| 항목 | 실제 결과 |
|---|---:|
| Decimal80 source parity |132/132 PASS|
| Decimal80 normalized block residual |132/132 PASS|
| FH bitwise equality |132/132|
| xr bitwise equality |264/264|
| xv bitwise equality |41052/41052|
| 최대 FH 차이 |0|
| 최대 normalized block residual |1.4989401807314334141864726397129907364020290746224123282844433828703052691264866E-15|
| Frozen residual threshold |9.094947017729282379150390625E-13|

Parity gate512eps64*S_F와 zero-scale 규칙을 바꾸지 않았다. 독립 Python validator는 C solver의 residual 값을 사용하지 않고 저장된 exact binary64 hex의 A/B/C/V/sr/sv/X를 Decimal80으로 재구성했다. Mathematical C_bi=Tvr[i][b], lower=Tvv[1], upper=Tvv[2] 방향을 직접 적용했다. 이 작은 residual은 source-point 방정식 검산이며 forward-error, inverse-gain 또는 physical tube의 증명이 아니다.

## Precision과 판별 controls

대표 writer indices0,66,131에서40/80 decimal digits를 비교했고 세 점 모두 두 precision에서 parity/residual gate를 통과했다. 최대 normalized-residual absolute 변화는2.5769650151011323266901170048753563056383703581454498761E-40다. 이는 represented binary64 자료를 재구성하는 working-precision 민감도 관측이며 rigorous interval enclosure라고 주장하지 않는다.

Saved-output mutation3개가 모두 frozen residual gate에 의해 검출되었다.

| Mutation | 실제 최대 normalized residual | 검출 |
|---|---:|---|
| B/C swap |0.99990312752916344564289793563103153690080144877964461808802803044517497364847351|PASS|
| Lower/upper band swap |0.028414080638977023819574007113899091088337245404030627756163158543483284527113568|PASS|
| Changed solution |0.33333333333333332221835141676455656304701547851285575228012659961636027568341380|PASS|

위 mutation은 저장 output만 바꿔 검증했으며 추가 solver 호출0이다.

Native incoming controls는 대표3점 각각 zero, signed-negative, doubled incoming으로9회 실행했다. Status0/residual/input nonmutation/table nonmutation/472events가 모두9/9이며 zero/nonfinite/overflow divisor는0이다. Control 최대 normalized residual은9.6312743890901472353366003010134686636325941413327759275425596864909445941422351E-16다. 실제 FH response는 각 점에서0이 아니어 incoming 누락을 구별했다. 수정된 incoming의 FH를 원 saved-native FH와 parity PASS로 비교하지 않았다. Affine second difference는 실제 hex로 보존했으며 새 numerical affinity gate를 만들거나 exact floating-point affinity를 주장하지 않았다. Signed departure의 허용은 임의 radiation spectrum의 물리적 positivity 주장이 아니다.

## 실제 자원

| Child | CPU seconds | Wall seconds | Maximum RSS KiB |
|---|---:|---:|---:|
| Validation와9 controls |0.888929|0.9011615139970672|75336|
| Saved-data plots |2.251386|2.263842983993527|130600|

Validation20CPU, plot10CPU, 각30wall/512MiB/single-thread 조건을 지켰다. Watchdog 중단은없다. 이번 C8 child 합계는3.140315CPU s다. 최초 C6 실패·resource 진단·재시도와 R7 reported remote0.06227을 모두 포함한 known 합계는 **4.704676 /60CPU s**, known 잔액은 **55.295324CPU s**다. 전체 new source-point calls는 **143 /146**, unfinished API attempt는0이다. Parent/network/model/metadata/packaging 비용의 미관측 부분은 UNKNOWN_NOT_ZERO다.

## 실제 그림과 결과 위치

- FH/parity PNG: `/workspace/scratch/6b0500b5ac99/research_next_20261028/electron_field/execution/C8_PLOTS_attempt001/figures/fh_parity.png`
- Normalized residual PNG: `/workspace/scratch/6b0500b5ac99/research_next_20261028/electron_field/execution/C8_PLOTS_attempt001/figures/normalized_residual.png`
- 두 page PDF: `/workspace/scratch/6b0500b5ac99/research_next_20261028/electron_field/execution/C8_PLOTS_attempt001/figures/validation_plots.pdf`

그림은 저장 primary와 독립 검증 결과만 사용했다. Root가 실제 PNG를 열어 시각 확인할 예정이며 worker는 추가 렌더나 이미지 재생성을 하지 않았다. 정확한 그림 bytes/SHA는 coding/C8_VALIDATION_SUMMARY.json에 있다.

원본 결과는 execution/C8_VALIDATE_attempt001/과 execution/C8_PLOTS_attempt001/, compact 요약은 coding/C8_VALIDATION_SUMMARY.json, 누적 비용은 execution/RESOURCE_LEDGER.json에 보존했다. Primary와 old histories/oldtests/producer/reference/BGJET audit/QSS03 certificate를 재실행하지 않았다. 원격 mutation0이다.

Canonical28/88+0, separate REI33/88, reference313/313, physical0/313 및 physical query/K/M2/defect/L/tube/e0/epsilon/outgoing null, H6/H7OPEN,L4false,REIactivationfalse를 유지한다. 새 결과는 He-neutral source-point Fe 성분의 검증이며 whole-cell continuous physical defect나 full-state physical tube를 공급하지 않는다.
