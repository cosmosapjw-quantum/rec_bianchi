# REC 다중 bin의 affinity·합성 미분 연구

작업: REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH.
고정 부모는 PR78 a1acf4037f68131ac4c6068eb0d450ef7e51bc97 / tree
c1de61d9fe9d0e0cd92228071346b818749778a8이다. PR77/78의 완료 검사를
재실행하거나 다시 구현하지 않는다. 기존 source와 전체 이전 연구는 불변이다.
이번 다중-bin 합성은 연구 디렉터리에만 추가하고 생산 코드에 연결하지 않는다.

## 입력과 연구 선택

원본 archive 및 기본/hires 표의 바이트는 기존 INPUTS.json에 고정되어 있다.
기본 2s 140행과 hires 408행의 에너지 및 A2s만 소비한다. parse_table과
기존 base loader를 재사용한다. 원래의 통계/원본 C/history 실험은 실행하지
않는다. 원시 계수와 원래 8.2206 s^-1 정규화 계수를 구분한다. 에너지비
u=E/E21를 계산하되 원래 에너지 눈금은 eV->J의 정확한 SI 정의를 쓴다.
원자 API의 h는 6.62607015e-34 J s이며 자연단위로 바꾸지 않는다.

제조 target은 u=(2^-30,1/4,1/2,3/4,1-2^-30),
mu=(2,4,8,4,2) m^-3, nH=8 m^-3, H=4 s^-1다.
이 mu는 물리 셀 적분으로 추론한 값이 아니다. 하나의 각도 슬롯은 스칼라
연구 축이며 물리 각도 구적이나 편광 인증이 아니다. 실제 photon cell과
분배 권위는 미결정으로 유지한다.

각 source 에너지에서 두 이웃 target의 비음수 선형 에너지 분율 B를 만든다.
각 열은 sum B=1, sum E_i B=E_s를 만족해야 하고 외삽/재정규화하지 않는다.
두 읽기는 (i) 같은 B로 chi=ln(1+1/f)를 읽는 후보와
(ii) 같은 두 이웃의 ln E에서 ln f를 선형 보간하는 별도 대조다.
둘 다 하나의 nodal 상태를 사용하며, 원본 BASS radial을 재실행한 것은 아니다.

모든 bin은 원본 PhysicalTwoPhotonRamanBin.paired_rates/net_action/jvp를
호출하고, 기존 COMSourceDepositionPlan.apply/jvp가 두 다리를 한 번씩
합산한다. 이 합성층에 원본 pair/deposition 공식을 복제하지 않는다.
독립 고정밀 reference는 비교용 primal에만 그 공식을 별도로 쓴다.

## 검증할 다중-bin 항등식

고정 양의 B,mu,nH와 g=1에서

    D_ib=B_i,tb+B_i,cb,
    A_sc,b=ln(xu/xg)+sum_i D_ib chi_i,
    A_read,b=ln(F_b/R_b), Delta_b=A_read,b-A_sc,b,
    sigma=sum_b Gamma_b A_sc,b
         =sum_b Gamma_b A_read,b-sum_b Gamma_b Delta_b.

sigma는 S/(N_H k_B)의 초당 변화율이다. 각 Gamma_b A_read,b가 비음수여도
실제 nodal sigma가 비음수인 것은 아니다. 모든 Delta_b=0은 다반응에서도
충분하지만, 한 반응의 필요조건을 고정 계수 합에 그대로 적용하지 않는다.

제조 thermal nodal 상태 chi_i=lambda*u_i, lambda=2에서는 모든 A_sc,b가
eta=ln(xu/xg)+lambda다. 읽은 값으로

    P=sum_b a_b(1+fc_b)(1+ft_b), Q=sum_b a_b fc_b ft_b,
    Delta_eff=ln(P/Q)-lambda

를 정의하면

    sigma=xg*Q*eta*(exp(eta+Delta_eff)-1).

이 특별한 고정 thermal 상태에서 모든 양의 원자 ratio에 대해 총 sigma>=0일
필요충분 조건은 Delta_eff=0이다. 각 Delta_b=0까지 필요하다는 명제가 아니다.
단일 연산에서 Delta_eff>0이면 -Delta_eff<eta<0에 음의 sigma가 생긴다.
두 표의 비교 상태를 같게 유지하기 위해 eta_common=-min(Delta_base,
Delta_hires)/2를 양쪽에 공통 적용한다. 이는 사전에 정한 반례 구성 규칙이고
우주론 상태 fit이나 물리 입력 승인이 아니다. 계수 전체의 양의 정규화는
Delta_eff를 바꾸지 않고 sigma만 그 배율로 바꾼다.

## 비열적 영모드 및 평형 선형화

하나의 transition에서는 chi(u)+chi(1-u)만 읽는다. 따라서
chi(u)=lambda*u+h(u), h(1-u)=-h(u), chi>0와 원자 LTE ratio는 모든
bin의 Gamma=0을 허용한다. 이 h는 연속 또는 구간 선형 스펙트럼의 실제
형상 자유도이며, 모든 bin의 영점이 Planck 유일성을 뜻하지 않는다.
검산은 h=alpha*u*(1-u)*(2u-1), alpha=1/8의 nodal 값을 대칭 target에서
구간 선형으로 읽는다. alpha 방향 JVP도 검사한다.

count w=(xu,xg,mu_i*f_i/nH), v_b=(-1,1,D_:b),
W=diag(1/xu,1/xg,nH/[mu_i*f_i*(1+f_i)])라 두면 공통 상세균형에서

    J=-V diag(R_b) V^T W.

WJ는 대칭 음의 준정부호, rank J=rank V다. 대칭 5노드의 D는
D0=D4, D1=D3, sum D=2이므로 rank V<=3이다. 실제 두 원본 표의
source 좌표를 유리수로 lift한 격자의 Gaussian 소거에서 rank=3을 검사하고,
별도로 실제 API의 7방향 JVP로 수치 J를 구성해 위 식과 비교한다.
유리수 rank와 반올림된 수치 matrix를 같은 바이트/같은 exact rank로 부르지
않는다. 7개 count 변수에서 4개 영모드가 있으므로 bin 수만 늘려서는 이
제조 target의 평형 유일성을 얻지 못한다. 실제 우주론의 모든 충돌을 포함한
연산에 같은 rank를 주장하지 않는다.

## 실행·오차 범위

7개 unittest 그룹. 두 표 x 두 읽기 x 원시/정규화 x 네 nodal/population
사례를 검사한다. 합성 JVP는 정규화 계수, 세 상태, 두 읽기, 일곱 방향의
총 84개 방향 비교다. 독립 전체 primal을 80/120자리에서 h=2^-32 중앙차분하고
혼합 방향에는 h=2^-36도 비교한다. 이산 B/L/a는 실행한 binary64 값으로
lift한다. 본체 API/JVP를 reference 안에서 호출하지 않는다.

수치 허용치는 기존 PR77과 같은 4096*epsilon의
abs(error)/(1+abs(reference))다. 80/120자리 차이는 1e-60 미만,
혼합 방향 차분 step 비교는 1e-16 미만으로 실행 전에 고정한다.
미세 오차를 보편적인 해석적 error bound로 승격하지 않는다.

기존 전체 테스트·원본 radial·원본 C/history는 재실행하지 않는다.
실패가 있으면 최초 로그를 보존하고 같은 scope의 구현/캡처 문제만 수정한다.
기대값·물리식·원본 표·허용오차를 PASS에 맞춰 바꾸지 않는다.
stdout의 SUMMARY는 전체 RESULT의 축약본이고, bin별 값 및 JVP 각 행은
별도 CSV와 RESULT에 보존한다. 그림 생성과 실제 시각 검토를 구분한다.
이 단계는 source-first 연구 판별기이며 새 생산 기능의 RED->GREEN 주장이 아니다.

## 문헌 역할과 비목표

Maas & Mielke (2020), doi:10.1007/s10955-020-02663-4의 상세균형 gradient
구조는 방법론 비교다. 그 mass-action 결과를 Bose source의 구현 증명으로
대체하지 않는다. Markowich & Pareschi, Numerische Mathematik 99 (2005)
509-532, arXiv:1009.2748은 수/에너지·entropy·BE 정상상태를 따로 보존하는
수치 연구다. 이 자료는 특정 B나 mu 또는 본 프로젝트의 입증을 제공하지 않는다.

https://link.springer.com/article/10.1007/s10955-020-02663-4
https://arxiv.org/abs/1009.2748

첨부 TEFF I/II는 정적 상태공간/entropy 기하의 연구 입력이다. 여기의
pair source, 물리 deposition, 시간 적분을 그 논문의 결과로 주장하지 않는다.

NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false;
provider_admitted=false. 움직이는 map/measure, 실제 시간 적분, 다른 원자
채널, angular/polarized kernel, 생산 BASS 연결, merge/ready는 범위 밖이다.
