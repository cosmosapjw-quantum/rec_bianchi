# 고정 map에서 단일 광자 상태를 읽고 반환하는 합성 JVP

작업: `REC_FIXED_MAP_SINGLE_FIELD_READ_SCATTER_JVP`.

출발점은 REC PR76의 commit `67a1900b4f5e9c8cdda11d950c6c70488f573f0b`, tree `256083bf54abeed11cd9fce963edefaea23cdbfa`다. 이 파일은 실행 전에 작성한 연구 구현·기준식·검산기의 설명이다. 실행한 테스트 수와 결과는 실제 RESULT.json으로만 결정한다. 의미 있는 RED를 실행했다고 주장하지 않는다. 기존 src/tests, BASS 원본, PR70/75 결과는 변경하지 않으며 생산 기본값이나 공급자도 추가하지 않는다.

## 다른 저장소의 최신 결과와 구분

직전 전달된 HTT PR457의 13통과/1실패는 역사적 기록이다. 최신 PR458 및 MAIN 댓글5564296516에는 승인된 seed/coverage 수정, 90개 로컬 테스트 통과, 실제 객체 재현2회와 MAIN 수용이 이미 있다. 그 수리·승인을 반복하거나 HTT source에 쓰지 않는다. PR284의 수학적 CAS conflict·DEFERRED, 정본30/후보40 경계는 유지한다. REC에서 완료된 BASS 원본8개 호출도 반복하지 않는다.

## 가정과 기호

같은 수소 정지계, 서명(-,+,+,+), 고정 에너지·분배B·측도mu, 양의 f,H,nH 및 population을 사용한다. 상대 boost, 각도·편광 kernel, redshift, 이동 map/event, 수송과 시간 적분은 제외한다. h=2*pi*hbar를 유지하며 원본 주파수 API에는 E_J/h를 전달한다.

기존 제조 두 노드를 사용한다.

- E0=2^-60 J.
- E_target=(1,4)E0.
- source 열 순서=(tracked2E0, companionE0).
- B=[[2/3,1],[1/3,0]].
- mu=(2,4)m^-3.

이들은 실제 HyRec/BASS target의 선택이 아니다. 한 각도 평균 슬롯은 스칼라 fixture이며 물리 각도 구적 인증이 아니다.

입력 z=(y0,y1,xu,xg,a,nH,H), y=ln f다. a의 단위는s^-1, nH와mu는m^-3, H는s^-1이다. g=1은 이 제조 원자 두 상태의 고정 통계가중치 규약이다. 현재 paired class의 정의역은 a>0이며, a=0을 임의로 통과시키지 않는다.

## 합성 연산과 JVP

chi_i=ln(1+1/f_i), chi_s=sum_i B_is chi_i,
f_s=1/expm1(chi_s).

고정B에서 dchi_i=-dy_i/(1+f_i)이므로

df_s=f_s(1+f_s)sum_i B_is dy_i/(1+f_i).

같은 원상태 y와 같은 방향 dy에서 tracked·companion을 모두 읽는다. 기존 PhysicalTwoPhotonRamanBin.net_action/jvp를 호출해 Gamma,dGamma를 얻는다. 두 다리에 R=(Gamma,Gamma), dR=(dGamma,dGamma)를 공급하고 기존 COMSourceDepositionPlan.apply/jvp로 C,dC를 얻는다. 마지막 좌표변환은 다음과 같다.

G_i=C_i/(H f_i),
dG_i=dC_i/(H f_i)-G_i(dy_i+dH/H).

원자 반환은(-Gamma,+Gamma)/H이며 같은 시간변환 미분을 포함한다. 출력은(xu,xg,y0,y1)의 tau당 변화율이다. 시간 적분은 수행하지 않는다. 기존 source·분배 공식은 재작성하지 않고, 독립 기준 계산에서만 따로 전개한다.

`log_control`은 이전 두점 log-f 읽기 L=[[1/2,1],[1/2,0]]를 수식으로 평가하고 같은B로 반환하는 대조 조건이다. 새 Rust 원본 실행이 아니다. chi 후보의 성질을 검사하는 것과 생산 보간법을 채택하는 것은 별개다.

## 고정 정확 fixture: 직접 유도

평형 nodal f=(1,1/15), xu=1/16,xg=1/2,a=1,nH=8,H=4.
방향은 dy=(1/4,-1/8),dxu=1/64,dxg=-1/32,da=1/8,dnH=2,dH=1이다.

chi 재구성은 ft=1/3,fc=1을 준다.

```text
dchi_t=-17/384       dchi_c=-1/8
dft=17/864           dfc=1/4
Gamma=0
dGamma=1/24+1/96-1/48-17/2304=55/2304 H^-1 s^-1
```

원자·로그상태의 합성 방향미분은 정확히

```text
(-55/9216, 55/9216, 275/6912, 275/4608)
```

이다. dnH,dH,da의 일부 항은 평형에서 Gamma=0이라 사라진다. 이 fixture 하나만으로 그 항을 검증할 수 없으므로, 두 비평형 상태와 일곱 좌표 방향·혼합 방향도 고정했다. 완료된133/512 좌표변환 검사는 다시 집계하지 않는다.

## 평형의 원자–광자 Jacobian 구조

고정 beta_i=mu_i/nH를 두고 count 상태를 w=(xu,xg,beta_i f_i)로 정의한다. 반응 벡터는 v=(-1,+1,D_i), D_i=B_it+B_ic이며 wdot=v Gamma다. 무차원 엔트로피를

s=-xu ln xu-xg ln xg+sum_i beta_i[(1+f_i)ln(1+f_i)-f_i ln f_i]

로 두면, 같은 분율을 읽기와 반환에 사용한 경우

A=v^T grad s=ln(xu/xg)+sum_i D_i chi_i=ln(F/R)

이다. 다른 읽기 연산을 유지한 채 이 등식을 적용해서는 안 된다.

W=-Hessian(s)=diag(1/xu,1/xg,1/[beta_i f_i(1+f_i)])는 양정치다. 상세균형 F=R=r>0에서

```text
dGamma = r dA = -r v^T W dw
J = -r v v^T W
WJ = -r (Wv)(Wv)^T
```

를 얻는다. 따라서 WJ는 대칭 음반정치이고 W^(1/2) J W^(-1/2)도 대칭 음반정치다. 한 반응의 rank는1이며 비영 고유값은 -r v^T Wv 하나다. 원자수·총에너지의 좌영벡터는 보존되는 선형함수다. 이는 비평형의 일반 Jacobian이 대칭이라는 주장이 아니다. 다른 영모드가 있으므로 이 반응만으로 유일한 Planck 상태에 수렴한다고 결론 내리지 않는다.

위 fixture에서는 beta=(1/4,1/2), v=(-1,1,5/3,1/3), W=diag(16,2,2,225/8), r=1/6이다. 물리시간의 비영 고유값은 -1921/432 s^-1, H=4 s^-1인 tau시간에서는 -1921/1728이다. 이는 직접 유도한 정확 기준이다. 검산기는 합성 JVP로 각 열을 생성해 이 행렬과 비교하고, 원자수 좌벡터(1,1,0,0) 및 E0로 무차원화한 에너지 좌벡터(3,0,1,4)를 확인한다.

로그 상태 q=(xu,xg,y0,y1)에서는 T=diag(1,1,beta_i f_i)이며 평형에서 J_q=T^-1 J T/H다. 비평형에서는 좌표변환의 추가항이 있으므로 이 similarity 식을 무조건 적용하지 않는다. 마지막 -G_i dy_i 항을 유지해야 한다.

## 실행·검증 범위

연구 합성함수는 composite_probe.py, 독립 기준과10개 unittest는 test_composite.py, 결과 캡처는 run.py에 있다. 새 코드는 이 연구 디렉터리 안에만 둔다. paired.jvp와 COM.jvp를 실제 호출하며 __file__ 및 두 원본 blob을 결과에 기록한다. 이번 실행은 비공개 BASS 원문을 필요로 하지 않는다.

독립 기준은 z(t)=z+t dz에 대한 mpmath.diff다. 세 고정 상태×여덟 방향에서80/120자리 결과 차이를1e-70과 비교한다. binary64 입력은 mp.mpf(float)로 정확히 고정한다. 작은 제조 영역의 합성 출력 비교 허용치는 사전에4096*machine_epsilon의(1+|reference|)척도로 정했다. 이는 특정 실험의 보수적 허용치이지 보편적인 초월함수 오차 증명이 아니며 결과를 보고 넓히지 않는다.

추가 검사는 density,H,로그 반환,companion 미분의 개별 누락을 검출한다. 희망값을 출력하는 검사가 아니라 원본 API를 소비한 잘못된 합성식의 차이를 확인한다. 완료된 PR75의8개나 HTT의90개를 새 검사 수에 합산하지 않는다.

현재 대화의 container와 Python은 각각 실행 전 ClientError였다. 제한된 read-only workflow의 실제 결과 확인 전에는 새 PASS가 없다. 호스팅이 시작 전에 막히면 그 상태를 보존하고, 작성된 동일 코드의 로컬 실행·범위 내 수리만 Git으로 인계한다. 그림, 전체 저장소 pytest, 제3자 독립 심사는 이10개 검사의 일부가 아니다.

## 문헌과 남은 경계

SciSpace 검색에서는 직접 관련된 원 논문을 확보하지 못해 반환 자료를 채택하지 않았다. 웹으로 확인한 Markowich/Pareschi arXiv:1009.2748의 초록은 보존·엔트로피·Bose 평형을 별개 구조로 다룬다. Mielke/Maas의2020 detailed-balance gradient 연구는 방법론적 배경이다. 위 유한모형의 공식·정확 fixture는 직접 유도이며, 문헌이 이번 구현을 인증하는 것은 아니다. 그 논문에서 새 물리 kernel이나 생산 수치법을 채택하지 않았다.

https://arxiv.org/abs/1009.2748
https://publications.imp.fu-berlin.de/2658/

최대 성공 표시는 PASS_BOUNDED_FIXED_MAP_SINGLE_FIELD_COMPOSITE_JVP다. 이는 제조 고정 map의 합성미분 검증일 뿐이다. NO_PASS_REC_PHYSICAL_SPLIT, physical_source_authenticated=false, provider_admitted=false를 유지한다. 실제B/mu/p_star,원자자료,각도·편광,source소유권,BASS시간진화,이동map/event,정본승격과merge는 미승인이다.
