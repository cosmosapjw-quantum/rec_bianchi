# REC 다중 bin 연구 — 실제 실행 결과와 범위

## 1. 완료한 작업

PR77의 합성 JVP와 PR78의 단일 반응 affinity 연구는 이미 완료된 선행
결과로 재사용했다. 이번에는 원본 2s 기본표 140개 bin과 고해상도표 408개
bin을 명시적 제조 5노드 광자 상태에 연결하는 연구 코드만 작성·실행했다.
기존 BASS 원본 진단, PR70 비교, PR77/78의 시험은 재실행하지 않았다.

[Draft PR79](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/79)의
실제 실행 source는 `2e3b73972ee298d44efdfb10016e314f58b0bada`,
tree는 `471442ce757fde701340729cd1abde281fd0db01`이다.
직접 부모는 PR78 `a1acf4037f68131ac4c6068eb0d450ef7e51bc97`다.

[전용 실행 34087807264 / job 101635113796](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34087807264/job/101635113796)의
checkout, 명령, 원본 경로, 전후 blob, 정확한 TestID, 결과 수치와 업로드
로그를 직접 읽었다. 7개 unittest 모두 통과, 실패·오류·skip 0, exit 0이다.
시험 14.955초, 결과 작성·그림 포함 runner 16.80558112초였다. 단일 실제
실행이며, 첫 실행 후 과학 소스 수정이나 재실행으로 얻은 결과가 아니다.
새 생산 기능의 TDD RED->GREEN을 완료했다고 주장하지 않는다.

판정은 `PASS_BOUNDED_MULTI_BIN_AFFINITY_JVP`다. 수치 검증은 완료됐지만
PNG 직접 시각 검토와 archive의 별도 로컬 재해시는 미완료다. 생산 물리
인증 또는 모든 검토의 완료를 뜻하지 않는다.

`OBSERVED_RESULT.json`과 `COUNTEREXAMPLE_SUMMARY.csv`는 실제 job의
SUMMARY 구간을 읽어 구조화한 기록이다. 원본 RESULT/SUMMARY/CSV와 같은
바이트라고 주장하지 않는다. 원본 데이터는 아래의 별도 artifact에 있다.

## 2. 고정 입력과 실제 호출

원본 archive와 기본/hires member hash를 실행 중 확인했다. PR70의
`parse_table`만 재사용하고 그 파일의 전체 옛 실행기를 호출하지 않았다.
기본표는 기존 `OriginalHyRecTwoPhotonRamanTable`과도 대조했다.

| 원본 표 | 2s bin 수 | 원시 계수 합 [s^-1] | 정규화 계수 합 [s^-1] |
|---|---:|---:|---:|
| base | 140 | 8.2245807524349 | 8.2206 |
| hires | 408 | 8.224707551416 | 8.220599999999997 |

원래 E21=10.198714553953742 eV를 사용했다. eV->J와 h는 SI 값을
유지하며 자연단위로 치환하지 않는다. 양의 계수와 반쪽 에너지 영역은
원본 입력이다. 이 사실만으로 각 bin의 연속 적분구간이나 실제 photon-cell
측도와 물리 map까지 확정되는 것은 아니다.

제조 target은 u=E/E21에 대해

    (2^-30, 1/4, 1/2, 3/4, 1-2^-30),
    mu=(2,4,8,4,2) m^-3, nH=8 m^-3, H=4 s^-1.

mu는 물리적인 셀 적분에서 얻은 값이 아니다. 한 각도 슬롯은 스칼라
제조 연구용이다. 물리 각도 구적이나 편광에 대한 주장은 없다.
각 source 에너지를 감싸는 이웃 두 점의 선형 에너지 분율 B는 비음수,
열합 1, 에너지 재현을 만족한다. 외삽이나 사후 열 정규화는 없다.

각 bin에서 원래 `PhysicalTwoPhotonRamanBin.paired_rates`, `net_action`,
`jvp`를 호출했다. 두 다리의 Gamma 배열은 기존
`COMSourceDepositionPlan.apply/jvp`로 한 번씩 반환한다. 생산 source와
COM, 재사용 parser와 INPUTS 네 blob이 실행 전후 같고 working tree가
깨끗했다. 연구 합성층의 원본 함수 호출과 독립 reference 공식을 구별한다.

읽기는 두 가지다. 첫 후보는 chi=ln(1+1/f)를 B로 읽고 Bose 역함수를
취한다. 둘째는 같은 이웃에서 ln E에 대한 ln f 선형 보간을 사용하는
`log_control`이다. 두 읽기 모두 같은 nodal 상태에서 두 다리를 읽는다.
둘째는 원본 Rust radial을 새로 호출한 결과가 아니며, 첫 후보를 생산
기본값으로 바꾸지도 않았다.

## 3. 총 엔트로피가 음수가 되는 다중-bin 반례

고정 nH,mu와 g=1에서 D_ib=B_i,tb+B_i,cb 및

    A_sc,b=ln(xu/xg)+sum_i D_ib chi_i,
    A_read,b=ln(F_b/R_b), Delta_b=A_read,b-A_sc,b

를 둔다. 수소 원자당 k_B로 나눈 엔트로피의 물리 시간 변화율은

    sigma = sum_b Gamma_b A_sc,b
          = sum_b Gamma_b A_read,b - sum_b Gamma_b Delta_b.

이는 실제 nodal 상태의 엔트로피 방향을 수축한 식이다. 반응률 자체의
양수식 sum Gamma_b ln(F_b/R_b)는 서로 다른 affinity로 읽고 반환할 때
실제 nodal entropy rate를 대신하지 못한다.

모든 bin의 Delta_b=0이면 총 sigma>=0이라는 충분조건은 유지된다.
반면 한 반응의 필요조건을 고정 계수 다중-bin 합에 그대로 적용하지 않는다.

이 연구의 thermal nodal 상태 chi_i=lambda*u_i, lambda=2에서는 에너지
재현으로 모든 A_sc,b=eta=ln(xu/xg)+lambda다. 고정된 읽기값을 사용하여

    P=sum_b a_b(1+fc_b)(1+ft_b), Q=sum_b a_b fc_b ft_b,
    Delta_eff=ln(P/Q)-lambda

라 쓰면 대입만으로

    sigma=xg*Q*eta*(exp(eta+Delta_eff)-1)

을 얻는다. 따라서 이 특별한 공통-affinity 상태에서는 모든 양의 원자
ratio에 대해 총 sigma>=0일 필요충분 조건이 Delta_eff=0이다.
Delta_eff!=0이면 eta=-Delta_eff/2에서 두 부호가 반대다. 이 집계 조건은
개별 leg 또는 모든 bin의 map 동일성보다 약하다.

실제 log_control의 Delta_eff는 base 0.02238493049350998,
hires 0.02237953745029886이다. 실행 전에 명시한 규칙
`eta_common=-min(Delta_base,Delta_hires)/2`로 하나의 공통 원자 상태를
구성했다. eta=-0.01118976872514943, xu+xg=9/16이다. 두 표마다 별도로
상태를 조절한 것이 아니며, 실제 우주론 상태를 적합한 것도 아니다.

| 양 [수소 원자당 k_B로 정규화한 s^-1] | base | hires |
|---|---:|---:|
| 일치한 chi의 실제 sigma | +0.00028173611409276625 | +0.00028167186474992016 |
| log_control의 실제 sigma | -0.0002603135345552853 | -0.0002601446373071536 |
| log_control의 양수 대조 sum Gamma A_read | +0.0005270804852294076 | +0.0005284552517908059 |

양쪽에서 광자수 변화 2 nH sum Gamma와 광자에너지 변화
nH E21 sum Gamma의 장부를 허용오차 안에서 확인했다. 음의 sigma를
숨기려고 반환 map, 계수, source 부호 또는 expected를 바꾸지 않았다.

원시/정규화 계수도 같은 상태에서 검사했다. 양의 공통 계수 배율은
P/Q와 Delta_eff를 바꾸지 않고 모든 source와 sigma에 그 배율만 준다.
원본 표를 140개에서 408개로 바꾼 두 결과가 가깝다는 것과 이 고정 target의
읽기 결함이 없다는 것은 다르다. 이것은 실제 재결합계의 엔트로피 감소
예측이 아니라 제조된 이산 연결의 반례다.

## 4. 전체 합성 JVP와 독립 기준

고정 B,mu,에너지에서 저장 y_i=ln f_i에 대해

    delta chi_i=-delta y_i/(1+f_i),
    delta f_s=-f_s(1+f_s) sum_i B_is delta chi_i.

이를 두 다리에 모두 적용하고 원본 pair JVP와 COM JVP를 호출한다.
밀도 미분과 G_i=C_i/(H f_i)의 H 및 로그 분모 미분도 포함한다.
추가 entropy 출력은 delta sigma=sum(delta Gamma A_sc+Gamma delta A_sc)다.

정규화 계수에서 두 표, 세 상태, 두 읽기, 일곱 방향의 84개 벡터 대조를
수행했다. 독립 reference는 실제 binary64 B/L/a를 고정밀로 올린 전체
nonlinear primal이며, 원래 JVP/API를 그 안에서 호출하지 않는다.
80/120자리 중앙차분 h=2^-32를 비교했고 혼합 방향에는 h=2^-36도 사용했다.
이는 적응형 증명용 interval bound가 아니라 고정밀 독립 수치 대조다.

    최대 scaled JVP 오차 = 6.4310422961310704e-15
    최대 scaled primal 오차 = 3.9470123103446857e-16
    척도 = abs(error)/(1+abs(reference))
    사전 고정 허용치 = 4096*epsilon = 9.094947017729282e-13

80/120자리 차이와 혼합 방향 차분 step 변화는 사전 조건을 통과했다.
84개는 7개 unittest 내부의 방향 대조 수이지 84개의 독립 테스트 엔진이
아니다. 이번에 SymPy는 dependency로 설치됐지만 새 symbolic-engine
검증 횟수로 세지 않는다. exact rank는 Fraction, 고정밀 primal은 mpmath다.

## 5. 비열적 영점은 bin 증가로 제거되지 않았다

하나의 두 광자 transition은 chi(u)+chi(1-u)만 제한한다. 따라서

    chi(u)=lambda*u+h(u), h(1-u)=-h(u), chi(u)>0

이면 적합한 원자 ratio에서 모든 bin의 affinity가 0일 수 있다.
이 연구에서는 h(u)=alpha*u*(1-u)*(2u-1)의 nodal 값, alpha=1/8을
대칭 target에서 구간 선형으로 읽었다. 이 함수는 thermal 직선이 아니지만
보간된 h의 반대칭성은 유지된다. 실제 최대 상대 nodal occupation 변화는
0.06666666653007192다. 이는 최대값이며 모든 에너지에서 같은 변화라는
뜻이 아니다.

| 관측 | base | hires |
|---|---:|---:|
| max abs(Gamma_b)/(F_b+R_b) | 2.883786839040029e-16 | 3.4120651288607145e-16 |
| sum Gamma [H^-1 s^-1] | 2.3809079707781677e-16 | 2.529443668408682e-16 |
| alpha 영방향 max abs(delta Gamma) | 3.698154551649891e-18 | 8.638191335494512e-19 |

즉 비열적인 nodal 상태가 반올림 수준에서 모든 bin의 영점이고 그 방향
미분도 영점이다. 이것을 유일한 Planck 열화의 확인으로 읽어서는 안 된다.

count 상태 w=(xu,xg,mu_i f_i/nH)와 v_b=(-1,1,D_:b),
W=diag(1/xu,1/xg,nH/[mu_i f_i(1+f_i)])를 쓰면 공통 상세균형에서

    delta Gamma_b=-R_b v_b^T W delta w,
    J=-V diag(R_b) V^T W.

따라서 WJ는 대칭 음의 준정부호이며 rank J=rank V다. 대칭 5노드의
D0=D4, D1=D3, sum D=2가 rank<=3을 주고, 두 원본 표에서 exact rational
소거가 rank=3을 주었다. count 변수 7개에서 영공간 차원은 4다.

원본 API의 7방향 JVP로 별도 구성한 수치 J와 위 식의 최대 scaled 차이는
base 3.0691398850882635e-16, hires 3.1949519454564116e-16이었다.
세 뚜렷한 감쇠 고유값 [s^-1]은 각각

    base:  -47.36255821943287, -6.399384196320392, -1.310172049041244
    hires: -47.34718052407841, -6.397114331496724, -1.3091598548379755.

나머지 네 수치 고유값의 미세한 부호는 반올림 잔차로 구분한다. 그중
작은 양의 값을 물리 불안정률이라고 부르지 않는다. exact rank는 반올림
전 유리수 보간에 대한 값이고, raw floating matrix가 exact rank 3이라고
주장하지 않는다. 실제 모든 원자 채널·수송이 포함된 재결합계의 영공간에
이 차원을 옮길 수 없다.

## 6. 두 축의 자체 검토

PHYS-MATH: 단위, 두 photon 다리, 수·에너지와 entropy의 구분,
단일 반응 필요조건/집계 필요조건의 범위, 비열적 영점, 고정 nH/mu의
count Hessian을 점검했다. 원자 총합과 2xu+광자수, 에너지의 선형 장부를
검사했다. nH 방향 JVP는 순간 source parameter 미분이며 팽창하는 부피의
전체 entropy evolution이라고 주장하지 않는다.

PHYS-MATH-CODE: 원본 API 호출, 두 leg의 공통 nodal input, source coefficient,
population/density/H 미분, 독립 nonlinear reference, bool/complex/shape/
nonfinite/zero/격자 밖 거부와 caller 상태 불변을 확인했다. 사용한 정상
범위 밖의 전역 conditioning 또는 모든 유한 입력의 안정성은 인증하지 않는다.
두 검토는 같은 작성자의 서로 다른 관점이며 새 제3자 독립 감사는 0회다.

적대적 대조는 보존적인 log_control의 음의 entropy와 비열적 영점이다.
새 source mutation 다섯 개 등을 별도로 실행했다는 주장은 없다. 이전
PR의 독립 감사나 mutant 성과를 이번 검사 수에 합치지 않는다.

그림 `bin_affinity.png`, `aggregate_entropy.png`는 실행기가 생성했다.
두 번째 곡선은 고정된 nodal 읽기로 얻은 P/Q의 해석적 집계식이며 모든
그림 점을 새 API 호출로 세지 않는다. 현재 주 대화에서는 PNG를 열지
못했으므로 figure-based final audit는 NOT_PERFORMED다. 생성 성공만으로
가독성·겹침·축소 인쇄 PASS를 선언하지 않는다.

## 7. 원본 산출물과 별도 실패

[원본 artifact 10005808072](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34087807264/artifacts/10005808072)는
10파일, 533789 bytes다. 업로드 로그와 metadata가 보고한 ZIP SHA256은

    d57b26de66d26454733d7a29848fd37381cc86020115a90cdcd1efd0c1530694

로 일치한다. 만료는 2026-10-07T05:42:51Z다. Connector 다운로드는
성공했지만 주 대화 container의 process-start ClientError로 독립 ZIP
재해시·내부 manifest 검사·PNG 보기를 수행하지 못했다. 별도 Wolfram
artifact 접근도 kernel 전 MCP SSE404였다. 원본 수치는 원래 hosted job의
실행 근거로 지지되고, 이 환경 오류를 수치 실패로 바꾸지는 않는다.

현재 Git에는 실행 가능한 source, 구조화한 결과와 반환 인계가 남는다.
전체 raw CSV/RESULT/PNG의 영구 Git 복제는 아직 미완료다. 기존 결과를
재계산하지 않고 자료만 취득·검토·게시하는 절차는 RETURN_HANDOFF_KO.md에
별도 묶었다. 사용자가 직접 ZIP을 다운로드해서 다시 올릴 필요는 없다.

[일반 PR CI 34087830592 / job 101635176981](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34087830592/job/101635176981)의
새 전체 로그도 읽었다. 실제 checkout은 PR 검사용 merge ref
`d06b4c1705d9eb6062baa9673f2cb836eef7988e`이고 main 병합이 아니다.
package import smoke는 PASS, quick verifier의 committed_feature_range는
기존 일곱 경로 공백 오류로 FAIL, 전체 pytest는 SKIPPED다. 첫 경로는
기존 MUTANT_drop_density_jvp.log:6이다. 그 경로들은 이번 신규 다섯
경로에 없으며, source commit의 직접 부모 대비 공백 검사는 별도로 PASS다.
과거 evidence는 수정하지 않았고 repository-wide GREEN을 주장하지 않는다.
뒤의 문서 전용 child를 수치 재실행했거나 그 후속 CI를 감사했다고 쓰지 않는다.

## 8. 문헌 역할과 다음 과학 작업

SciSpace로 상세균형·entropy·영모드의 문헌을 탐색하고 다음 원 출처를
확인했다. Markowich/Pareschi의 arXiv 초록은 질량·에너지 보존, entropy
부등식, Bose–Einstein 정상상태를 별개의 보존 성질로 명시한다. Maas/Mielke의
원문 서론은 상세균형 mass-action의 logarithmic-mean Onsager 구조를 쓴다.
이 문헌들은 방법론 비교이지 본 Bose read/scatter 연산의 증명을 대신하지
않는다. 이번 정리와 수치는 위에 명시한 연구 모델에서 직접 유도·검산했다.

- https://arxiv.org/abs/1009.2748 (Numerische Mathematik 99, 509–532, 2005)
- https://link.springer.com/article/10.1007/s10955-020-02663-4

첨부 TEFF I/II는 정적 entropy·상태공간 연구 자료로만 취급한다. 그 논문이
본 source·수송·시간 적분을 제공한다는 주장은 없다.

다음 과학 작업은 `REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE`다.
원본 두 표를 그대로 두고 photon target의 해상도를 독립 축으로 변화시켜,
읽기오차와 약한 source 관측량·그 JVP가 어떻게 변하는지 비교한다. 한 개의
명시적 공통 reference measure에서 각 격자의 mu를 구성해야 하며, 노드 수에
따라 mu를 임의로 정해서 다른 operator들을 같은 수렴열로 부르면 안 된다.
서로 다른 차원의 raw C 벡터 대신 같은 비상수 시험함수의 source pairing을
비교한다. 반대칭 비열적 영모드는 보존 대조이며 그것을 강제로 감쇠시켜
Planck 유일성을 만들지 않는다. 새 과학 작업은 아직 실행하지 않았다.

NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false;
provider_admitted=false. 실제 target/map/measure 권위, 이동 map/event,
시간 적분, 각도·편광, BASS evolve, 다른 atomic channel, ready/merge는 미완료다.
