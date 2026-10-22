# 다음 스레드: REC thermal moments

## 먼저 읽을 상태

이 단위는 `research/rec_thermal_moments_20261022`다. 현재 local branch는 `research/rec-thermal-moments-20261022`, parent는 REC119 `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`이다. 실행 코드가 고정된 commit은 `d9a3edfc4b80d7cb26dd6599b2b8685350576b84`다. 이후 commit은 결과·그림·문서·receipt를 추가한다. 최종 local commit과 archive identity는 실제 git 상태 및 외부 delivery receipt를 확인한다.

1. `DELIVERY_STATUS.json`과 최종 ZIP 옆 integrity receipt를 확인한다.
2. `REPORT_KO.md`의 실제 결과·증거 한계, `THEORY_KO.md`의 식·근거, `FROZEN_CONTRACT.md`의 범위를 읽는다.
3. `DAG.json`, `LOOP_EVIDENCE_KO.md`, 두 independent results review를 읽는다.
4. 실행 필요성은 source/data/config identity 변화와 새로운 판별 질문으로 정한다. 완료된 결과의 존재를 확인하기 위해 ODE를 재실행하지 않는다.

## 완료된 계산과 채택 범위

- 기존 REC125main+1opacitycontrol=126개: trajectory/receipt hash 확인 후24,318개 상태를 새 thermal budget으로 후처리. 기존 IVP 재실행0회.
- 새 full63:4Mao primary+2Mao refined+2rate-derivative alternative=8개 distinct 설정. 한 fresh invocation에서 모두 COMPLETE, 각109개 저장점, 총872상태. 실패·재실행0회. wall71.976452초, CPU합71.060064초.
- 시작은 parent 저장 index84, z7.963732801243163. 초기62좌표·tau·시간은 바이트 그대로 계승. T초기1081.319779971744K. 초기 n/T=0, 저장 상태에서도 정확히0.
- 기존 prescribed z20→2 경로의 순 추가 외부 요구량은−19.7207..−19.6551eV/baryon. 대표−19.716893939eV/baryon은 net sink다. 새 dynamic trajectory의 실제 열손실량이나 음의 gas energy로 읽지 않는다.
- 새 primary 저장 최고T14167.03..14177.03K(z4.976223), endpoint10116.85..10119.08K. 기존 endpoint11999.95565K. 구간 전체가 일률적으로 더 뜨겁거나 차가운 것은 아니다.
- prescribed-vs-dynamic 최대 conditional fraction차이~0.12035는 transient LiIV다. 희귀Li의 절대 electron density 기여가 가장 크다는 뜻은 아니다.
- nominal/refined max(delta lnT,deltaf,delta signed6,delta tau)=(4.1814e-7,3.4031e-8,4.9892e-9,3.4425e-11), 전부 사전gate통과.
- Mao-vs-derivative source차이는 T·ion·tau에서 관찰된 primary refinement 변화보다 크지만 확률적오차나 전체모형오차가 아니다. 대안 closure 자체의 별도 refinement는 없음. stress-only와 signed6 모두 source 신호가 대응 refinement보다 작다.

## 재사용 identity

Execution source identity:

```text
dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e
```

네 runtime 파일은 `run_thermal.py`, `thermal_system.py`, `thermal_sources.py`, `recombination_moments.py`다. 각 RESULT는 이 파일·원표·source lock, donor NPZ와 donor RESULT/config의 SHA를 기록한다. 보고서·plotter·test 파일은 실행 의존성이 아니므로 변경만으로 trajectory를 무효화하지 않는다. `provenance/PARENT_SOURCE_LOCK.json`은 donor49개 source/data/vendor 파일을 고정한다. 각 saved126 입력은 별도 `INPUTS.json`에 연결된다.

Python3.12.14/NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8을 실제 사용했다. 런타임 가용성은 다음 턴에도 실제 probe로 판단한다. 이번 CPU8 quota/RAM8GiB 확인을 미래 환경에 가정하지 않는다. 새8의 finite contract는 완료되었고 과거 U5 예산 CLOSED_HOLD_NOT_RESET은 그대로다.

## 남은 증거·물리 의무

Dense513/1025 quadrature는 실행 당시 계산했고 결과 산술/endpoint를 재검산했지만, 중간 상태와 BDF interpolant가 파일에 없다.1025표본 residualmax8.5452e-6은 **runner-reported**다. 독립 저장109표본 Simpson residualmax5.90787e-4는 별도 coarse diagnostic이며1025 gate를 재현한 것으로 세지 않는다. 다음 신규 실행에는 diagnostic grid arrays와 identity를 저장한다. 현재8개를 이것만을 이유로 다시 실행하지 않는다.

공통MaxwellianT, instantaneous primary thermalization, case-A/prompt escape, ground-state electronic rates, isotope electronic equality, test-fluid baryons, inherited earlyprefix의 조건을 유지한다. CI/CX·collisional excitation·secondary·free-free·Compton energy transfer·directmultiple photoionization·radiative transport·nuclear energy는 미공급이다. 현재 식이 맞는다는 사실은 누락 과정이 작다는 증명이 아니다.

Physical HOLD; production NOT_APPROVED; global convergence NOT_RUN; U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; REI_activation=false.

## 다음 과학 행동

다음 노드는 `THERMAL_OMITTED_PROCESS_BUDGET_ON_SAVED8`이다. 우선 현재 원시8개를 재사용해 Compton 에너지 교환과 collisional excitation/ionization의 primary-source 계수·단위·에너지 소유권을 확보하고, 기존 가열·냉각·팽창 work에 대한 크기·부호·시간 구간을 평가한다. 결과가 요구하는 경우에만 새 closure와 다음 finite 실행계약을 정한다. 이 handoff 자체는 새 ODE batch를 요구하지 않는다.

REI의 nuclear/daughter 활성화는 별개다. 현재 native21과 zero n/T를 임의로 compact33에 치환하지 않고, H fraction을 T에 복사하지 않으며, passive nuclear history를 coupled prediction으로 가져오지 않는다. 새로운 핵 공급을 도입한다면 nuclear energy와 daughter charge state부터 닫는다.

## 외부 전달의 유일한 현재 blocker

Git push는 실제 자동 승인 검토에서 거절되었다. 현재 메시지만으로 새 연구 코드·원자료·provenance를 외부 GitHub에 게시할 권한이 확인되지 않았다는 이유다. 다른 API로 우회하지 않았다. 새 remote branch와 PR은 아직 없고, 새 Dropbox/Drive 업로드도 NOT_RUN이다.

사용자가 명시적으로 승인하면 준비된 새 branch를 기존 `cosmosapjw-quantum/rec_bianchi`에 push하고 PR119의 branch 위에 draft PR을 만든다. merge하지 않는다. `DRAFT_PR.md`에 검토 가능한 제목·본문·base/head를 준비했다. 같은 완성 archive를 기존 REC Dropbox 위치의 새 이름으로 전달하고, provider acknowledgement/metadata/실제 bytes readback은 수행한 범위만 각각 기록한다. 업로드 후 새 receipt와 최종 handoff를 추가하며 기존 science 계산은 재실행하지 않는다.

최종 archive에는 두 research unit, source lock, 실제 결과, 원본 실패/metadata 수정 기록, 분석 데이터와5종 PNG/PDF가 포함된다. 최종 ZIP 자체의 SHA는 자기참조를 피하기 위해 ZIP 바깥 integrity receipt에 둔다. source/results 무결성은 ZIP 내부 MANIFEST의 파일별 SHA로 확인할 수 있다.
