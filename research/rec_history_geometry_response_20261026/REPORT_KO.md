# REC-HISTORY-GEO01 연구 결과

2026-10-26 UTC. 판정: **PASS_SCOPED_CONTROLLED_PROPAGATION_PARTIAL**.
원래 313개 history query에 제어된 Bianchi I shear 전파를 결합하고,
입사 복사의 1차 사중극과 2차 단극을 계산했다. 저장된 scalar Ks에는
각도 평균만 입력했다. 독립 검토에서 선언된 범위의 중대한 미해결 지적은 0개다.
상위 REC-HISTORY는 PARTIAL이고 물리적 H5/H6/H7 의무는 아래와 같이 유지된다.
Git 게시와 외부 백업의 실제 상태는 delivery의 receipt를 별도로 따른다.

## 1. 최신 자료 조사와 재사용

접근 가능한 9개 저장소의 branch/PR 목록을 끝 페이지까지 열람했다.
실제 빈 terminal page를 포함한 branch 30쪽, PR 30쪽의 관측이며,
총 1,708개 branch와 1,595개 all-state PR이다. 상세 cutoff와 원응답은
provenance/SURVEY_INTAKE.json 및 SURVEY_INTAKE_KO.md에 있다.

| 저장소 | branch | PR |
|---|---:|---:|
| rec_bianchi | 156 | 138 |
| rei_bianchi | 278 | 235 |
| bass | 277 | 192 |
| bass_cr | 184 | 106 |
| BASS_HE | 107 | 102 |
| vigilode | 215 | 89 |
| WU088_HH | 159 | 150 |
| frame_flow_budget | 35 | 24 |
| htt_base | 297 | 559 |

이는 접근 가능한 저장소 메타데이터의 전수 열람이다. 모든 파일이나 모든 비공개
대화에 접근했다는 뜻은 아니다. 연결된 과거 대화 검색에서는 이용 가능한 내용을
얻지 못했으며, 확인 가능한 PR의 인계·담당자 receipt와 백업을 사용했다.
다른 repo 집합·시점의 1,334/1,629/1,633 집계는 별도 기록으로 보존했다.
역사적 bianchi_phase_r1 alias는 404였으므로 현재 repo로 추정하지 않았다.

현재 과학 기반은 REC PR138의
`4a8e541030ee2cbd02e26ba671083b705d309d49`다. recursive tree 7,189개 항목은
truncated=false이며 해당 경로에 적용되는 AGENTS는 없다. 중앙 AGENTS
`429a5a13ee75b1222bc50627f8d5973d01dd21c4`와 실제 중앙 HEAD
`a5db4bac9dafadae29685bbea3cec7f43ab990b2`를 읽었다. 실행 직전 두 HEAD를
다시 조회했으며 변동이 없었다. 기존 checkout을 새로 clone하거나 worktree를
만들지 않고 복구된 입력 snapshot과 connector 게시 경로를 사용했다.

| 재사용 단위 | 채택 내용과 현재 범위 |
|---|---|
| REC-LINE02 / PR129 | 완료된 194 checks, 202 rank queries를 재사용. 최종 담당자 receipt COMPLETE_SCOPED_RESEARCH_AND_EXTERNAL_DELIVERY를 별도 확인 |
| HISTORY01 / PR130 | history 경계와 JVP 계약, 608 primary+14 independent 근거 |
| ADM01 / PR131 | 입력·domain admission, 역사적 일부 raw 유실 상태 보존 |
| HISTORY02R / PR132 | characteristic 및 reference 법칙 재사용. 실제 제어는 다른 cosmology의 초기 h4 8개 cell에 한정 |
| REFINE01 / PR133 | represented-history envelope, physical epsilon=null |
| RESP01 / PR134 | 기존 K0 certificate와 종료된 gross 진단 수정 |
| THERMO01 / PR135 | stable Js, 25 RHS의 이미 완료된 결과; serialization failure와 분할 실행 보존 |
| KS01 / PR136 | 같은 source의 stable Ks 314×313, 실제 313-query admission, joint checks; 기존 639 large+10 small RHS 재실행 없음 |
| PB01 / PR137 | 626 endpoint fixed chart, query slope, pullback 및 interval. 원 primary exit2와 saved-vector 8/8 repair를 함께 보존; 수정한 전체 primary는 NOT_RUN |
| HD/H5 / PR138 | HD parser 25 PASS, source-frequency gate는 7/8 line FAIL. H5 실제 313 binding 완료지만 continuous bound coverage 0/313 |

이전 대화에서 실행 전이던 HISTORY02·JOINT01 준비는 각각 PR132·PR136으로
대체됐다. 새 계산으로 다시 세거나 실행하지 않았다. LINE02 인계의 과거 pending
flag는 최종 owner comment와 receipt에서 해소됐음을 확인했다.
원 comment: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/129#issuecomment-6360118229
현재 읽은 receipt blob은 `bde496ee603c6bcdf0c502f741d06a3c3a2383ad`다.
이는 현재 receipt 재열람이며 LINE02 archive의 새 전체 다운로드 검증은 아니다.

REI PR233/236과 BASS PR192의 실제 문서도 비교했다. REI의 최신 국소 response는
선택된 보간 상태와 처방된 history에 관한 것이며 original z≈1100 source와 일치하는
물리적 H6 trace를 제공하지 않는다. BASS의 512 birth/514 endpoint 자료는 cold,
non-tilted, recoil-free, detached fplus=0인 제조된 모형의 기하이다. split-midpoint
birth beta가 빠져 있고 H/S는 beta 자체가 아닌 미분을 준다. 따라서 기존 기하
관례의 근거로 사용하되 original REC target의 물리적 supplier로 승격하지 않았다.

## 2. 새 단위의 수학적 대상

부호는 (-,+,+,+), 시간은 eta=ln(a), target 에너지는 eV, native TR=k_B T는 eV다.
기존 isotropic source history·보간 endpoint·target primitive·scalar collision source를
고정하고 방향별 팽창률을 1+lambda v_i, sum(v_i)=0으로 택한다. 관측 방향 n은
target orthonormal frame에서 단위벡터이고 각도 평균은 dOmega/(4pi)이다.
W(x)=exp(-x)는 native Wien reference다. 저장된 u는 total occupation이 아닌
departure이며 f=W+u로 복원한다.

각 query에 Lambda=ln(E_source/E_target)>0, w_i=n_i²를 정의하면 delay Delta는

`Delta + (1/2) ln(sum_i w_i exp(2 lambda v_i Delta)) = Lambda`

를 만족한다. 부동소수점 native clock의 기존 값을 보존하기 위해

`q(lambda)=q_native+Lambda-Delta(lambda)`, `delta=q-q_native`

로 고정한다. q_native와 eta_target-Lambda의 산술 차이는 최대
8.881784197001252e-16이고 별도로 저장했다. 두 clock을 조용히 대체하지 않았다.

고정 cell의 slope를 g, x=E_target/TR라 하면

`Delta u = g delta + exp(-x) expm1[-x expm1(delta)]`.

기존 history 값 자체를 다시 진화시키지 않고 query와 reference 변화만 연결한다.
이 정의는 특정 geometry/source 조합에 대한 전파 편미분을 만든다.

`A=sum_i w_i v_i`, `C=sum_i w_i v_i²`, `S2=sum_i v_i²`,
`h_j=g_j-x_j exp(-x_j)`, `k_j=(x_j²-x_j)exp(-x_j)`라 하면

`q'=Lambda A`,

`q''=-2 Lambda A²+2 Lambda²(C-A²)`,

`u'=Lambda h_j A`,

`u''=h_j q''+k_j Lambda² A²`.

source direction tangent는 `n'_source,i=Lambda n_i(v_i-A)`다.
단위구 평균의 `<A>=0`, `<A²>=2S2/15`, `<C>=S2/3`를 적용하면

`<u'>=0`,

`Q'_ij=(2/15) B_j diag(v)_ij`, `B_j=Lambda_j h_j`,

`m2_j=<u''>=S2[h_j(-4Lambda_j/15+2Lambda_j²/5)+k_j(2Lambda_j²/15)]`.

저장된 scalar source가 incoming 값에 affine이므로 이 고정 모형의 각도 평균
2차 응답은 `o''=Ks m2`다. 방향별 값에 Ks를 적용해 방향별 collision 결과로
해석하지 않았다. 첫 사중극은 별도의 향후 angular collision 입력이다.

단일 Ly-alpha event의 순 광자 수 응답은

`R_gamma''=(3e6 LYA) H [(Ks m2)_311-m2_311]`,

복사 에너지 응답은 `E21_J R_gamma''`, 원자 에너지는 그 정확한 음수다.
입사 직접 항을 빼는 구조와 기존 saved event coefficient가 일치한다.

### 이론·문헌 확인

SciSpace로 관련 원전을 검색하고 Fleury–Pitrou–Uzan의 Bianchi I light-propagation
논문 및 Marcori 등의 direction/redshift drift 논문을 확인했다. 검색 메타데이터의
연도 오류는 원 arXiv의 출판 정보로 교정했다. Wolfram 실제 평가 결과
`{0,0,0,0}`는 crossing series, Wien 1차·2차 미분, second angular mean의 네
상징 잔차에 해당한다. 이 검증은 수치실행이나 물리적 history closure를 대신하지 않는다.
원 응답은 provenance/EXTERNAL_RESEARCH.json에 보존했다.

- Fleury, Pitrou, Uzan, Physical Review D 91, 043511 (2015): https://arxiv.org/abs/1410.8473
- Marcori, Pitrou, Uzan, Pereira, Physical Review D 98, 023517 (2018): https://arxiv.org/abs/1805.12121

## 3. 실제 계산과 새 결과

원래 z=1099.9986525171403, T0=2.728 K,
nH0=0.18745798773143102 m^-3, prefix 5127의 313 query/626 endpoint를 사용했다.
TR=0.25882399309326415 eV, H=4.969651222923834e-14 s^-1이다.
target energy 순서는 Ebin[0:311], E21, E31이다. source-column index와 구분했다.

두 shear v1=(1,-1/2,-1/2), v2=(1,-1,0)의 해석적 계수를 계산했다.
finite root는 v1에서만 실행했다. 6개 축 방향 각각 1/15, 8개 cube corner 각각
3/40의 14-ray 규칙은 필요한 4차까지의 구면 moment를 정확히 재현한다.
유한 lambda의 전 각도 적분 수렴을 증명한 것으로 해석하지 않는다.

최소 conservative cell margin은 5.278877512893132e-8이다. 모든 방향에 대한
`|delta|<=Lambda |lambda|V/(1-|lambda|V)`를 사용해 고정한 공통 step은
**h=9.758192586050367e-6**이다. 실제 최대 shift는 margin의
0.249992681284143이며 동일 cell과 strict prefix를 유지했다.

| 산출량 | 실제 저장된 결과 |
|---|---|
| B_j | 313개 모두 음수; -1.23749966262639e-9에서 -3.430059646376636e-21 |
| Q'11, v1 | 313개 모두 음수; -1.6499995501685197e-10에서 -4.573412861835515e-22 |
| m2/S2 | 313개 모두 양수; 9.141532790724385e-22에서 4.1005041298874486e-10 |
| m2, v1 | 1.3712299186086578e-21에서 6.150756194831173e-10 |
| Ks m2 | 314개 모두 양수; 2.1705132669636038e-23에서 6.15075617989756e-10 |
| R_gamma'' | -1.7197807608184382e-9 m^-3 s^-1 /lambda² |
| 복사 에너지 2차 응답 | -2.8101462107517614e-27 J m^-3 s^-1 /lambda² |
| 원자 에너지 2차 응답 | +2.8101462107517614e-27 J m^-3 s^-1 /lambda² |

마지막 세 값은 lambda=0에서의 **두 번째 도함수**다. 유한한 작은 lambda의
선도 2차 변화량은 (lambda²/2)를 곱한다. 모든 출력 성분의 m2가 양수여도
순 event 응답은 출력과 입사 직접 항의 차이이므로 음수가 될 수 있다.
이를 full thermal ODE의 물리적 가열률로 승격하지 않는다.

전체 계수·대표 index 값은 results/SAVED_VALUES.json 및 raw NPZ에 있고,
그림은 figures/figures001의 PNG/PDF 두 쌍이다. Root와 독립 검토자가 실제 PNG를
모두 확인했다. 부호를 보존한 symlog 축과 수치/물리적 범위 표기가 읽히며 수정은
필요하지 않았다.

## 4. 검증과 한계

| 검증 | 결과 |
|---|---|
| ordinary scalar roots | 17,528개, 각 root 최대 3회 iteration |
| stable root residual | 최대 5.68221161163024e-14; 고정 한계 5.684341886080802e-14 이하 |
| Decimal80 bisection | 96 roots, 160 iterations/root; 24 configuration×2 step의 first/second 쌍 48개 |
| 고정밀 first 오차/gross | 최대 1.5505132806082325e-10; 한계 2e-7 |
| 고정밀 second 오차/gross | 최대 1.400080738875983e-10; 한계 2e-7 |
| 독립 Decimal90 Newton | query37/289의 별도 ray에서 8 roots, production import 없음 |
| 독립 first/second 오차/gross | 1.767175659167328e-11 / 1.5648758129079072e-11 |
| angular identity | 35 exact monomials, 두 shear의 moment gate PASS |
| quadrupole/second roundoff 지표 | 최대 1.6575435680669e-16 |
| source direction tangent | n dot n' 지표 0 |
| 새 domain guard | 10개 모두 잘못된 입력 거부 |
| 추가 Ks 연산 | 5 matvec, exact represented-vector interval action 1회 |
| RHS / IVP / inverse / native replay | 모두 0 |

예상값의 크기를 지워버리는 max(1, occupation) 기준을 사용하지 않았다. 각 연산의
gross로 정규화했다. 313개 저장된 baseline과 4×313×14개 유한 표본의 total
occupation은 모두 양수이며 최솟값은 4.078751185933352e-19다. 전 방향 positivity
certificate는 별도로 주장하지 않는다.

일반 binary64 방향별 2차 차분의 최대 상대 진단 오차는 h에서
5.8492439229747817e-8, h/2에서 1.4698878190823586e-7로 증가했다.
이는 작은 step의 상쇄 영향을 보여준다. 이 진단을 독립 derivative acceptance로
사용하지 않았고, 고정밀 oracle의 고정 기준을 변경하지 않았다. incoming mean의
같은 진단은 1.3676448503280355e-10, 8.198712179082837e-11이었다.
첫 monopole의 이론값이 0이므로 그 상대오차를 정의하지 않았다.

기존 Ks interval과 represented binary64 m2의 exact Fraction dot으로 얻은
314개 구간은 순서와 outward 직렬화를 확인했다. 저장 point output 314개 모두가
구간 안에 있다. 폭은 1.5064985165291447e-28에서 1.228829838491025e-22다.
이 구간은 **표현된 m2에 대한 Ks 전달**을 감싼다. 새로운 exp/log 계수 평가의
엄밀한 오차나 실제 history 오차는 이 구간에 포함되지 않는다.

새 scientific failure와 실행 후 repair는 0회다. 실행 전 발견된 Decimal bracket
끝점의 false FAIL 가능성과 실패 prefix 저장 문제는 C5 동결 전에 수정·검토했다.
실행 기준·물리 모형·실제 허용 query domain을 넓히지 않았다.

## 5. 예산과 실패 보존

| 실제 subprocess | CPU초 | 실행 wall초 |
|---|---:|---:|
| primary001 | 1.597416 | 1.621934662 |
| figures001, 저장 결과만 사용 | 3.285980 | 3.325148428 |
| 독립 probe 8 roots | 0.082455 | 0.115258899 |
| 위 3개 합계 | 4.965851 | 5.062341989 |
| 저장 결과 요약 readback child | 0.154822 | 0.167809258 |
| 독립 검토 readback 관측 부분 | 0.075704751 | 0.075714149 |

새 allocation은 60 inclusive child CPU초/180 execution wall초다. runner overhead,
원격 IO/CAS/model/packaging 비용은 ledger에서 별도로 기록한다. 미측정 비용은
UNKNOWN_NOT_ZERO이며 이 표를 대화 전체의 완전한 총비용으로 해석하지 않는다.
과거 PB lineage의 알려진 CPU subset 36.442061486초를 그대로 보존했다.
유실된 과거 HISTORY02 worker의 40CPU/90wall 보수적 upper charge도 유지한다.
실행되지 않은 JOINT01 준비를 실행 비용으로 꾸미거나 그 잔여 예산을 이관하지 않았다.

과거 PB primary 실패, THERMO serialization 실패, HD의 원래 35Hz gate 실패,
REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, 최초 REI 실패 raw HISTORICAL_LOCAL_ONLY와
오래된 off-grid raw 유실 기록은 성공한 새 단위와 함께 보존한다.

## 6. DAG, claim gate와 후속 순서

현재 중앙 DAG는 88 node/15 authority/17 integration edge이며 과거 40-node
snapshot은 역사적 근거로 유지한다. GEO01은 REC-HISTORY 안의 새 관측으로 추가하고
다른 owner의 원계약·상태를 변경하지 않는다. 중앙 PR232의 HD/H5 실행 관측은
canonical HEAD와 별도였으므로 원 snapshot과 실제 관측을 분리해 조정안을 만들었다.

1. LINE02 및 HISTORY boundary는 완료 근거와 최종 receipt를 재사용한다.
2. THERMO01 → KS01 → PB01의 완료된 chain에서 실제 fixed chart와 operator를 받는다.
3. GEO01은 이 chart에 controlled DQ와 reference 변화를 연결한다. 이 단위의 과학 범위는 완료됐다.
4. H5의 source-matched continuous error producer와 H6의 실제 geometry/frame/clock
   trace는 병렬 입력 의무로 남아 있다. H5 epsilon 및 physical outgoing bound는 null이다.
5. 실제 DY, DQ, Dtheta, endpoint retiming, thermal feedback 소유자를 결합한 H7은
   입력 계약을 충족한 뒤 별도 동결 예산으로 실행한다. 다음 구체 계약은 NEXT_INPUT_CONTRACT.md다.

R1–R9/C1–C9의 18개 의무는 근거가 있다. R10/C10의 결과·인계·DAG 내용은
마련하되 실제 게시와 백업 receipt가 충족될 때까지 외부 전달 완료로 세지 않는다.
각 단계의 evidence/checkpoint/실제 Git·Dropbox·Drive 상태는 STAGE_PROGRESS에 있다.
이 18/20은 작업단위의 workflow 진척이며 전체 물리 연구의 90%라는 뜻이 아니다.
전체 물리 완성도는 정의되지 않아 null을 유지한다.

**보호된 상태:** Physical HOLD; REC-HISTORY PARTIAL; H5 coverage 0/313;
H6 physical supplier OPEN; H7 total coupled OPEN; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; L4_ready=false;
REI_activation=false. 새 strong no-go 주장은 없다.

## 7. 보관과 게시 상태 읽는 법

S0 전체 입력 동결본과 S1 code/preexecution overlay는 immutable이다. 각각
Dropbox 실제 완료 응답과 size가 확인됐다. 원 archive 내부의 당시 상태를 사후
완료 상태로 고쳐 쓰지 않는다. 최종 전체 archive는 입력·코드·모든 새 raw·그림·
review·보고서·인계를 담고 실제 전달 receipt는 그 바깥에서 보완한다.

Git에 대형 donor 입력을 중복 게시하지 않는 경우 정확한 입력 identity와
delivery/restore_inputs.py 및 INPUT_RESTORE_MAPPING.json을 제공한다. 원 history
blob은 기존 repo에 있다. 완전한 복구 bytes는 전체 백업 archive에 보존된다.
Git/Drive 쓰기는 완료 응답 없는 환경 지연과 실제 readback을 분리해 기록한다.
권한 거부나 자동 승인 거절이라는 응답은 관측하지 않았다. 게시되지 않은 후보
commit/PR을 실제로 올라간 것처럼 표시하지 않는다.
