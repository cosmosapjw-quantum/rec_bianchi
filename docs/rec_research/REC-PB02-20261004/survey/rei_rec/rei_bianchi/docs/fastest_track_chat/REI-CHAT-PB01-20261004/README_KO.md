# PB01: FLRW Peebles C-factor 복원 우선 검증

사용자 요청으로 FT07 physical model error budget보다 이 검증을 우선한다. FT07은 deferred이며 완료하거나 폐기하지 않는다.

## 판정

1. 조건을 갖춘 retained n=2 원자계의 준정상 제거: PEEBLES_REDUCTION_DERIVED_AND_LIGHT_CHECKED.
2. 현재 FT03/FT05/FT06 Case-A instantaneous-escape 연구모형과 F00 합성 closure: 기하만 FLRW로 보내도 Peebles를 복원하지 않는다. MODEL_SCOPE_MISMATCH이며 수치 버그나 단순 미검증과 다르다.
3. 실제 production consumer의 source-bound regression과 재결합 history: NOT_RUN. 새로운 production recombination surrogate나 REC-owner 교체는 없다.

시작, 단계 경계 및 게시 직전 live HEAD는 dc931a67cd5ed25046a96eb5deb42186d72176da였다. runtime_inputs/closure_process_decision.json 및 rust/rei_microphysics/src/hydrogen_step.rs를 exact commit으로 읽었다. F00은 SYNTHETIC_CASE_A_ESCAPE이고 F02는 constant-rate scalar oracle다. 이 판정은 읽은 선택 경로에 한정하며 모든 repo branch에 대한 전수 부재 주장이 아니다. 기존 compatibility API, 원자 provider와 source lock은 수정하지 않았다.

## 축약식과 컨벤션

순수 H, proper nH, xe=xp, x1+x2+xp=1. 표준 단일 ODE에서는 x2<<1로 x1=1-xe. 우선 Tm=Tr를 고정한다. alphaB [cm3/s], Lambda2gamma [s^-1], per-2p Ralpha [s^-1], K [cm3 s], h=2*pi*hbar, E21=chi1-chi2=hc/lambda.

betaP=alphaB(Tr)*(2*pi*mu*kB*Tr/h^2)^(3/2)*exp(-chi2/(kB*Tr)); beta_shell=betaP/4.
A=nH*alphaB(Tm)*xe*xp; q=x1*exp(-E21/(kB*Tr)); Dg=(Lambda2gamma+3*Ralpha)/4.

retained shell: dx2/dt=A-beta_shell*x2-Dg*(x2-4q).
electron: dxe/dt=-A+beta_shell*x2.
QSS: x2*=(A+4Dg*q)/(beta_shell+Dg).

따라서 C=(Lambda2gamma+3Ralpha)/(Lambda2gamma+3Ralpha+betaP), dxe/dt=-C*(A-betaP*q)다.

opaque Sobolev에서는 Ralpha=8*pi*H/(3*lambda^3*n1), K=lambda^3/(8*pi*H)이므로
C=(1+K*Lambda2gamma*n1)/(1+K*(Lambda2gamma+betaP)*n1),
dxe/dz=C*(A-betaP*q)/(H*(1+z))를 얻는다.

beta_shell을 변환 없이 K-form에 넣지 않는다. shell 축퇴도4와 2p 축퇴도3은 별개의 인자다. fraction에 -3Hxe를 추가하지 않는다. helium 전자를 포함하면 재결합 source는 xe*xp이며 xe^2가 아니다. Lambda2gamma는 열화학 냉각계수와 단위부터 다르다.

필요한 축약 조건은 CaseB, n2 thermal inverse, Lyalpha trapping/escape, 2s two-photon, statistical shell redistribution, QSS, Wien 및 opaque approximation이다. 비열적 외부 source off는 thermal photon bath off가 아니다. Lyalpha blue boundary를 thermal로 두더라도 line core 전체를 Planck 분포로 강제하지 않는다. FT03의 30000~110000K guard를 재결합 온도로 외삽하지 않는다.

## 새 검산과 반례

Saha 평형은 임의의 양의 C에서 같은 근을 가질 수 있으므로 C-factor 복원의 충분조건이 아니다. C~1인 후기 꼬리만 비교하는 것도 불충분하다. A=1,q=1/1000,betaP=100,Lambda=1,R=1/3의 추상적 양의 계수 반례에서는 C=1/51, Peebles RHS=-3/170, C 없는 RHS=-9/10이다. 외부에서 C를 강제로 주입한 scalar step은 기존 closure에서 유도한 복원의 증명이 아니다.

유한 2s/2p mixing m의 2x2 제거, m->infinity의 C 복원, 유한 mixing의 서로 다른 branching probability, QSS initial layer와 lag bound를 유도했다. 큰 m은 수학적 redistribution 극한이며 실제 거대한 충돌률을 주장한 것이 아니다.

Bianchi->FLRW에서는 a_i=a*exp(epsilon*b_i)를 시간 구간 전체에서 C1 의미로 등방화한다. 국소 정지 Sobolev, 전 방향 h_parallel>0, 등방 방출, uniformly thick 조건에서는 escape rate를 먼저 각도 평균한 뒤 C를 형성한다. 일반적으로 average(C(R))와 C(average(R))는 다르다. 이것은 임의 shear의 Lyalpha 복사수송 해가 아니다.

n2를 명시적으로 유지하면 binding/H=chi1*xp+E21*x2다. continuum->n2의 chi2와 n2->ground의 E21을 분리하고, instantaneous CaseA escape의 chi1 전액을 동시에 기록하지 않는다.

## 실제 경량 실행

기호 항등식19개, scalar135점, Saha4점, finite mixing6점, forced linear QSS4회, Sobolev7점, anisotropic-to-isotropic4개, invalid-input reject7개를 검사했다. C의 binary64 대비 80자리 기준 최대 상대차는 4.440892098500626e-16이다. Unit test2개와 최종 2단계 runner는 exit0이었다. 4개의 선형 연구 ODE 외에 우주론 history 적분은 없으며 전체 Rust/Grackle/HyRec/RECFAST 실행은 0회다. 같은 assistant의 검토이며 독립 reviewer를 dispatch하지 않았다.

진단 profile은 SSS1999 alphaB fit의 F=1, 순수 H, Tm=Tr와 명시적 반올림 상수다. T=3000K,nH=250cm^-3,H=5e-14s^-1,xe=.1에서 alphaB=6.685412343969990e-13cm3/s, betaP=515.1356456521823s^-1, Ralpha=1.036591374156080s^-1, C=.02152896485520501, dxedt=-3.590939780015216e-14s^-1이다. 이는 scalar 진단점이며 실제 우주론 history나 atomic accuracy certificate가 아니다.

## 원전과 비교 범위

Peebles1968 DOI10.1086/149628 Eqs24-31; Ali-Haimoud와 Hirata2011 DOI10.1103/PhysRevD.83.043513 SecIIA Eqs1-11; Seager, Sasselov와 Scott1999 DOI10.1086/312250 Eqs1,3,4를 사용했다. 현대 HyRec PDF p3을 시각 확인했다. Peebles1968 원 PDF는 parsed text를 읽었으며 screenshot 실패를 별도 기록했다. SSS1999의 literal Tm 처방과 현대 Tr 처방을 two-temperature에서 혼동하지 않는다. 보정된 기본 RECFAST 또는 full multilevel HyRec와 unmodified Peebles의 무조건적 exact equality를 요구하지 않는다.

## 재현 패키지와 다음 단계

REI_CHAT_PB01_20261004.zip: 52662 bytes,32 entries.
SHA256=e3307e86fa76070744bc67c425d4bca724cf08a9292e5277d0019ea9982fcafe.
Drive: https://drive.google.com/file/d/1WrUX-47C1ezwjCx0ulpiYK6T-vhBi5CJ/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_PB01_20261004.zip
전체 보고서 REPORT_KO.md, Python scalar/linear oracle, 상세 JSON, negative control, 로그와 manifest는 ZIP의 rei_chat_pb01_20261004/ 아래에 있다. 이 저장소 폴더에는 요약, 계약, 결과집계, 반환, 인계문과 백업 영수증만 추가했다.

다음 작업은 REI-CHAT-PB02_SOURCE_BOUND_REDUCTION_CONTRACT다. 기존 REC-owner 또는 구현된 level residual을 실제 commit/path/blob에 연결한다. 연결 대상이 없으면 MISSING_PEEBLES_CLOSURE_AT_CONSUMER를 유지하며 현재 F00을 소급 치환하지 않는다.

기존 strict local<2e-4/public width<2e-3, [160,161] FAIL=2.1245050576368385e-4와 tick160 prefix를 보존한다. Physical admission, 새 branch, merge, force push는 없다. 백업의 R1 metadata 확인과 원격 byte restore는 별개다.
