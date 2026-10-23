# LINE01 단일 독립 검토 — PASS_AFTER_TARGETED_REPAIR

2026-10-23 KST. 검토자 `/root/line01_review`는 이번 단위의 원전 조사,
유도, 구현을 작성하지 않았다. 부모가 제공한 맥락과 현재 산출물을 읽었으며,
blind replication이나 독립 원자 데이터 측정을 주장하지 않는다. 자식 검토자를
추가하지 않았고, R6 수학 검토 → C9 코드·저장 결과·그림 검토를 한 pass에서
완료했다. 최종 열린 BLOCK_NOW/FIX_SOON 지적은 0개다.

## 1. 판정 범위

**선택된 유효 단일선 모델과 고정 배경의 국소 thick source step은 수용한다.**
원 production attempt001은 FAIL로 보존되며, 계산된 source36/map25를 다시
실행하지 않고 잃어버린 floating-point root bracket만 고쳐 남은 작업을
완료한 resume001을 수용한다. 이 판정은 전체 우주론적 history, 실제 겹친
Lyα doublet의 전달 등가성 또는 production activation을 승인하지 않는다.

검토 입력은 FROZEN_CONTRACT.md, THEORY.md, source cards와 collapsed-source
추가문서, original donor와 입력 provenance, code/line_source.py,
code/run_line01.py 및 code/resume_line01.py다. 사용한 skill은
physmath-research-loop 1.3.0 및 POLICY_INTEGRATION/THEORY_LOOP/CODING_LOOP다.

## 2. 독립적으로 확인한 물리와 수학

**Source 규약.** 실제 저장 상태는 collapsed 2p population이므로 최종 g=3
effective coincident-line card를 적용하는 것은 명시한 closure와 일치한다.
1:2 sublevel split 및 공통 frequency/profile/f_plus를 가정하면 emission
계수는 A_eff n_u, stimulated opacity는 A_eff(3n_l−n_u)로 합쳐진다.
이는 별도 fine component의 escape 확률 두 개를 더한다는 주장이 아니다.
전체 n=2 shell의 g_u=8 및 평균 A를 사용하지 않는 입력 제한도 확인했다.

Native xr[1]을 실제 population으로 오인하지 않고
x_2p=xr[1]+3x_1s exp(−E21/TR)로 복원한다. Dfplus 역시 total occupation이
아니므로 full Planck baseline을 별도로 더한다. Native compressed action과의
동일성을 주장하지 않는 표기는 필요하고 현재 유지된다. 이 국소 모델의
N=n_l+n_u는 두 준위 pool이며 native 전체 n_H와 다르다. 코드의 물리적
밀도 및 reference n_H 사용은 이 구분과 맞는다.

**각평균 및 장부.** Profile-average source를 대입하면 D=n_u−Δf_plus,
Δ=g n_l−n_u이고 R=ABD가 된다. 광자 phase-space crossing의
2ν²/c³와 redward speed Hqν를 조합하면 방향률 ADβ/(4π)를 얻으므로
8π normalization이 맞는다. Number/PSTF source A D Q와 energy source
E A D Q의 단위도 맞는다. R의 부호는 흡수에서 반전되지만 gross down/up은
각각 비음수다. Bound–bound 항의 free-electron/ionic yield 및 recoil-free
kinetic heating의 0을 전체 열역학적 폐쇄로 확대하지 않는다. Tensor 결과는
복사 주입률/packet이며 저장된 radiation stress 자체가 아니다.

**국소 해.** F=1+(g+1)f_plus, x_eq=g f_plus/F, d0=g/F로 두면
thick ODE는 dy/dt=−a y/(d0−by)다. 분리 적분으로
d0 log|y/y0|−b(y−y0)=−at를 얻는다. z0=−by0/d0>−1에 대해 W0가
초기조건과 단조 접근을 만족하며 W−1은 물리적 분기가 아니다. 동치인
u+z0 expm1(u)+ω=0의 도함수는 1+z0 exp(u)>0이고 문서의 유한 bracket
끝점 부호가 맞는다. expm1으로 packet을 구하는 것은 작은 시간에서 endpoint
차감을 피한다. A는 thick drift에서 소거되지만 validity gate에서는 남는다.

**전체 경로와 오차.** Absorption에서는 x가 증가하며 opacity가 줄므로
초기 opacity만 검사하면 충분하지 않다. 최소 opacity를 max(x0,x_eq)에서
잡는 코드가 맞다. 전 경로에서 B/B0∈[1−δ,1]이므로 travel time을 비교하면
finite-opacity endpoint가 Φ_t와 Φ_(1−δ)t 사이에 온다. 이를 단순한 순간
rate 상대오차와 혼동하지 않았다. K=2S/15에 대해
||Q/B−K||≤δ/(1−δ)(sqrt(2/3)+||K||)이며, source의 부호가 경로 전체에서
고정되어 total variation을 population 이동량으로 바꿀 수 있다. 따라서
문서의 trajectory+angular-shape tensor packet 상한이 방출/흡수 모두에
성립한다. 코드의 log-domain coarse bound는 rounded bracket width와
구분되고 underflow를 exact equality로 표시하지 않는다.

## 3. 실제 새 검토 계산 — 6개만 실행

원 production 행이나 역사적 캠페인을 재실행하지 않았다. 원 script와
PROBES_RAW.json에 전부 보존했다. 고정된 kernel 함수와 별도로 90-digit
Lambert W 및 독립 1D LRS 각적분을 평가했다.

| 검토 case | 결과 | 수치 근거 |
|---|---|---|
| g=1, inversion 경계에 가까운 x0=0.49 | PASS | endpoint 절대차 8.81e−17, packet 상대차 4.73e−16 |
| g=2, f_plus=3 흡수 | PASS | endpoint 절대차 8.51e−17, packet 상대차 3.16e−16 |
| g=3, ω=1e−12 및 q_min=0.02 | PASS | packet 상대차 5.81e−17 |
| g=2, τ0=0.73, LRS finite source | PASS | B/Q/R 정규화 차 ≤4.87e−16 |
| 같은 native line owner 동시 활성 | PASS | map API가 명시적으로 거부 |
| 초기 gate40, 흡수 전체경로 gate10.526… | PASS | 전체경로 조건으로 거부 |

Independent map oracle는 y0,d0를 production row에서 복사하지 않고 원래
입력 scalar에서 다시 구성했다. LRS oracle는 production log-root나
ANGULAR donor의 oracle 함수를 호출하지 않았다. 총 새 model 호출은
source1/map3/거부2이며 IVP는 0이다. 원 core hash
139daa47b84e76f7730db372e0228d42ba8441f8cd59e02f2c1b5df59cdf8f1d에 대한
검토 결과임을 PROBES_RAW에 기록했다. 이후 4줄 bracket repair는 아래의
구조 검토와 해당 native 실패행의 보존된 oracle 결과로 표적 확인했다.

## 4. 관찰된 실패와 표적 수리

### F-01 — root bracket의 binary64 병합: CLOSED

생산자가 발견한 native ω=1 case에서
z0=−7.898205430874699e−17이고, 수학적 L=−1+z0와 U=−1이 모두
binary64 −1로 반올림된다. 따라서 F(L)>0 약5e−17이 되어 기존 코드가
잘못된 물리 영역이 아닌 representability 문제로 중단했다.

code/line_source.py의 lower를 nextafter(lower,−∞), upper를
min(0,nextafter(upper,+∞))로 바꾸는 4줄 diff를 확인했다. 수학식과 허용오차는
바뀌지 않았고, 이 실패에 필요한 floating endpoint 외향 반올림만 추가했다.
최종 core hash는
5ae9304b2ab8478b8371d65c2eed55074328b158ceddb2c3785b171ca45c0b2e다.
원 core와 runner bytes는 evidence/attempt001_code에 보존돼 있다.

Resume는 성공한 source36/map25를 읽고 검증했으며 source를 다시 계산하지
않았다. 실패했던 native ω=1과 아직 미실행이던 ω=5 두 map만 추가했고,
각각 독립 W0 oracle와 원 기준을 통과했다. 이어 미실행이던 direct6,
finite reference2, 입력거부18, plot243을 실행했다. 새 코드에 대한 전체
물리 campaign rerun은 없었다.

### F-02 — 초기 source 선택 문구와 상대 링크: CLOSED

THEORY의 잔여 selected g=1 문구와 Wolfram receipt 상대 링크를 부모에게
전달했다. 현재 문서는 최종 g3 effective source와 최초 fine-card 추천의
역사를 구분하며, 링크도 provenance/ 경로로 수정됐다. 수치 재실행이
필요 없는 표현/추적성 수리다. StageA의 넓은 R4–R8 완료 표기는 부모가
정확한 개별 stage mapping으로 교정하기로 했으며, 독립 R6 근거는 이
검토 문서로 한정한다.

## 5. 저장 증거와 그림 검토

attempt001 manifest11개와 resume001 manifest14개의 bytes/SHA256을
읽어 모두 일치함을 확인했다. 고유 source36, 고유 map27도 확인했다.
최종 704 acceptance 항목에는 기존 616개가 포함된다. 둘을 더해 1320개의
독립 검증으로 세면 안 된다. 세부 saved-only 점검은
SAVED_EVIDENCE_REVIEW.json에 있다.

| 저장 결과 점검 | 관측값 |
|---|---:|
| W0 endpoint 최대 절대차 | 3.34e−17 |
| Direct Einstein phase-space 최대 gross 정규화 차 | 6.52e−16 |
| Direct angular B 최대 상대차 | 2.11e−15 |
| Direct angular Q Frobenius/B 최대차 | 7.37e−14 |
| 두 finite-reference endpoint의 bracket 이탈 | 0 |
| 두 travel integral residual 크기 | 5.55e−17 |

3개 actual PNG를 모두 열어 읽었다. 방출 곡선은 population 감소와 양의
광자 packet, 흡수 곡선은 population 증가와 음의 packet을 보인다.
두 경우 radiation/internal energy가 반대 부호이고 PSTF의 xx/yy/zz 부호가
shear 및 net exchange와 맞는다. Native 그림은 saved z≈1100 state와
supplied shear를 명시하고 국소 시간 ω를 사용한다. 현재 우주론적
history로 오해할 축이나 title은 없다. 선/축/범례/각주가 읽히며 clipping은
관찰되지 않았다. τ/qmax와 logδ, thermal0의 모델 범위도 표시한다.

각 그림의 PNG/PDF/CSV hash와 81개 CSV↔raw sample binding을 확인했다.
PDF는 PNG와 같은 Matplotlib figure에서 저장된 출력의 bytes만 확인했고
별도 PDF raster 검토를 했다고 주장하지 않는다. 선행 source uncertainty,
fine structure model error 및 numeric tolerance의 구분을 유지한다.

## 6. 다음 단계와 유지 상태

이번 판정으로 source-owned line ledger와 국소 thick map leaf를 닫을 수
있다. 후속 coupled owner replacement는 residual/JVP/history/feedback,
실제 복사 상태와 energy backreaction을 함께 넘기는 별도 연구 단위다.
열린 Li ionic-yield 및 다른 channel의 daughter/electron/neutrino/recoil
입력을 이번 bound–bound의 zero yield로 채우면 안 된다.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
기존 REC126/REI129/warm729/THERM02/ANGULAR405의 cohort 및 실행 수와
역사적 REI 첫 실패 raw의 local-only 범위를 유지한다. 백업/원격 게시의
최종 ACK 및 whole-byte 검증은 부모의 delivery 단계 책임이며, 이 검토가
그 후속 전달 확인을 대신하지 않는다.
