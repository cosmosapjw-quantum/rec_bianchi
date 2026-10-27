# 같은 pulse의 누적 경계를 affine 주입 이력으로 운반하는 정리

## 결과와 범위

근거 상태: **derived; independently reviewed**. 새 numerical execution은 없다.

CR PR109의 유한 이력 convolution과 REI PR240의 누적 interval·monotonicity 정보를 재사용한다. 이번 결과는 같은 source template·같은 bath의 비음수 affine 주입 이력에 대하여, 저장 horizon 사이의 미지 response를 유지하면서 유한 관측 window의 정확한 정보 하한과 supremum을 계산하는 식이다. 식의 평가에는 새 provider solve나 수치 quadrature가 필요하지 않다. 현재 PHYS02 100 K source와 CR108 10,000 K response는 실제 matching을 충족하지 않으므로 아래 정리를 그 두 자료의 물리적 결합 결과로 평가하지 않았다.

단위는 proper seconds, 같은 frame, 동일한 고정 proper volume 또는 이미 하나의 공통 기준부피로 pullback된 measure다. 시간에 따라 팽창하는 별도 worldtube density를 부피 이력 없이 합하지 않는다. Metric은 (-,+,+,+)이며 c, hbar, k_B를 생략하는 단위 관례를 새로 도입하지 않는다. 정리의 scalar F는 pulse count density 또는 kinetic-energy density다. 각 quantity의 원래 단위를 유지한다.

## 1. 재사용하는 두 입력

CR의 기존 식은 backward K와 reward r에서
f_h = integral_0^h exp(-K a) r da,
C(T) = integral_0^T j(s)^T f_(T-s) ds
이다. 이 convolution, proper-volume 변환, finite injection과 finite response horizon의 구별을 다시 새 성과로 세지 않는다.

같은 spectral pulse f0를 선형·시간병진불변 환경에 주입하고 j(s)=h(s) f0이면 scalar pulse cumulative response를 F(tau)=f0^T f_tau로 정의할 수 있다. 그러면

$C(T)=\int_0^T h(s)F(T-s)\,ds.$

이 감소는 동일한 f0와 response law를 모든 injection cohort에 사용한다. Source feedback, 시간가변 operator, 다른 spectral shape 또는 다른 bath에는 age-only F로 가는 별도 근거가 필요하다.

REI의 저장 horizon은
0=t_0<t_1<...<t_m.
기존 closure l_i=max(0,L_0,...,L_i), u_i=min(P_U,U_i,...,U_m)를 재사용한다. 새 코드는 closure를 다시 구현하지 않는다. 필요한 입력 조건은
l_0=u_0=0, 0<=l_i<=u_i<=P_U,
l_i<=l_(i+1), u_i<=u_(i+1).
원래 cap P_U와 exact source identities를 유지한다.

정보 집합 P는 [0,t_m] 위의 비음수·비감소·우연속 함수 F 중
F(0)=0, l_i<=F(t_i)<=u_i
를 만족하는 함수다. 단말 t_m에서의 값도 interval에 속하며 왼쪽 극한과 같을 필요는 없다. 이 집합의 원소가 모두 동일 fixed-K dynamics에서 실현된다는 전제는 없다.

## 2. 하나의 global history에서 window를 구성한다

주입 시작을 proper time 0으로 고정하고
h(s)=beta+alpha*s, beta>=0, alpha>=0
가 최소한 [0,B]에서 실제로 정의됐다고 하자.
[h]=s^-1, [beta]=s^-1, [alpha]=s^-2.
0<=A<=B<=t_m이고 source history 자체의 유효 끝점도 B 이상이어야 한다. h(s)ds는 절대연속 주입이다. 별도 Dirac pulse는 이 kernel의 입력이 아니다.

D_(A,B)=C(B)-C(A)라고 하면 변수 tau=T-s의 치환으로

$
D_{A,B}=\int_0^{t_m} w_{A,B}(\tau)F(\tau)\,d\tau,\qquad
w_{A,B}(\tau)=h(B-\tau)\mathbf 1_{\tau\le B}-h(A-\tau)\mathbf 1_{\tau\le A}.
$
함수 h는 위 indicator가 선택하는 비음수 argument에서만 사용된다.

거의 모든 tau에서

$
w_{A,B}(\tau)=
\begin{cases}
\alpha(B-A),&0\le\tau\le A,\\
\beta+\alpha(B-\tau),&A<\tau\le B,\\
0,&B<\tau\le t_m.
\end{cases}
$
따라서 w>=0이고 w는 적분 가능하다. C(B)와 C(A)의 각 cohort를 독립적으로 극값화하지 않고 하나의 F를 유지한 것이 핵심이다.

각 cell의 무차원 가중치 W_i=integral_(t_i)^(t_(i+1)) w(tau)d tau는 p(x)=max(x,0)를 쓰면


$
\begin{aligned}
W_i={}&\beta\big[(B-t_i)_+-(B-t_{i+1})_+-(A-t_i)_++(A-t_{i+1})_+\big]\\
&+\frac{\alpha}{2}\big[(B-t_i)_+^2-(B-t_{i+1})_+^2-(A-t_i)_+^2+(A-t_{i+1})_+^2\big].
\end{aligned}
$

A와 B가 grid knot일 필요는 없다. 식 자체가 cell을 정확히 자른다.
시간을 각 관측 window 시작으로 재설정하여 beta,alpha를 그대로 다시 쓰지 않는다. 그것은 다른 source history다.

## 3. 정확한 정보 하한과 상한

**정리.** 위 전제하에서

$
L_{A,B}=\sum_{i=0}^{m-1}W_i l_i,\qquad
U_{A,B}=\sum_{i=0}^{m-1}W_i u_{i+1}
$
라 두면 모든 \(F\in\mathcal P\)에 대하여
$L_{A,B}\le D_{A,B}[F]\le U_{A,B}.$
L은 minimum이며 U는 supremum이다.

**경계 증명.** t_i<tau<t_(i+1)이면 단조성으로
l_i<=F(t_i)<=F(tau)<=F(t_(i+1))<=u_(i+1).
w>=0이므로 cell별 적분하고 더하면 경계가 성립한다. Grid점의 값은 Lebesgue 적분을 바꾸지 않는다. w의 부호가 바뀌는 일반 source에는 이 sharpness 논증을 그대로 적용하지 않는다.

**하한 달성.** F_lo(tau)=l_i for t_i<=tau<t_(i+1), F_lo(t_m)=l_m으로 둔다. 모든 grid 값과 cap을 만족하는 비감소·우연속 함수이며 D[F_lo]=L이다.

**상한 접근.** 0<epsilon<1, epsilon_i=epsilon*(t_(i+1)-t_i)로 두고,
F_epsilon(tau)=u_i for t_i<=tau<t_i+epsilon_i,
F_epsilon(tau)=u_(i+1) for t_i+epsilon_i<=tau<t_(i+1),
F_epsilon(t_m)=u_m
으로 정의한다. 각 grid에서 값은 u_i이고 전 구간에서 단조·우연속이며 cap을 만족한다. 거의 모든 cell 내부에서 F_epsilon(tau)->u_(i+1). 또한 0<=F_epsilon<=u_m이고 w in L1이므로 지배수렴정리에 의해 D[F_epsilon]->U다. 따라서 U는 정확한 supremum이다. 이것은 수치 convergence 관측이 아니라 해석적 증명이다.

F(0)=0에서의 우연속성과 초기 cell의 양의 weight가 양립할 때 상한 계단 envelope가 P 안에 없을 수 있다. 그러므로 일반적인 U에 maximum 또는 attaining witness를 붙이지 않는다.

이 정리는 P 안에서 sharp하다. 알려진 response smoothness, fixed-K semigroup, count/energy correlation 또는 source support 조건을 추가하면 정보집합이 좁아질 수 있다. 그러한 조건이 없이 좁아진 물리 오차를 주장하지 않는다.

## 4. 여러 window의 공통 극값과 정확한 가법성

F_lo와 F_epsilon의 정의는 A,B에 의존하지 않는다. 동일한 P와 하나의 global h를 사용하는 임의의 유한 window 집합에서 모든 하한이 동시에 달성되고 모든 상한은 같은 접근열로 동시에 접근된다.

A<=B<=C에 대해
w_(A,C)=w_(A,B)+w_(B,C),
W_i(A,C)=W_i(A,B)+W_i(B,C).
따라서

$
L_{A,C}=L_{A,B}+L_{B,C},\qquad U_{A,C}=U_{A,B}+U_{B,C}.
$

검토 중 초안의 "개별 window 극값은 동시에 달성되지 않는다"는 문장을 교정했다. 그것은 원 PR240의 signed endpoint difference 문제에서는 relevant하지만 이번 비음수 affine-history functional에는 해당하지 않는다. 동일한 lower staircase/upper sequence가 위 결과를 직접 보인다. 서로 다른 response/source 대안, 다른 global history, signed weight를 이 결론에 섞지 않는다.

## 5. 독립 해석 예제와 극한

단위 시간을 1 s로 하고
t=(0,1,2), l=(0,1,3), u=(0,2,4), P_U=4,
A=1, B=2, beta=0, alpha=1
을 택하면 W=(1,1/2), L=1/2, U=4다.

F_lo=0 on [0,1), 1 on [1,2), F_lo(2)=3이면 D=1/2.
F_epsilon=0 on [0,epsilon), 2 on [epsilon,1+epsilon), 4 on [1+epsilon,2]이면
D[F_epsilon]=4-4epsilon+epsilon^2 ->4.
이 예제에서 상한은 우연속성 때문에 달성되지 않는다.

같은 입력의 [0,1] window는 W=(1/2,0), [L,U]=[0,1],
[0,2]는 W=(3/2,1/2), [L,U]=[1/2,5].
[0,1]+[1,2]의 두 endpoints와 weights가 [0,2]와 정확히 합치한다.

alpha=0,beta=1,A=1,B=2에서는 W=(0,1), [L,U]=[1,4].
A=B 또는 alpha=beta=0이면 모든 W와 경계가 0이다.
B=t_m은 허용하며 B>t_m는 response extrapolation이므로 지원하지 않는다.
alpha,beta가 음수인 입력을 거절하는 것은 이 bounded primitive의 정의역 선택이다.

[W]=1이므로 L,U,C,D는 모두 F와 같은 단위다. 새 SI 변환이나 1/H가 없다. 위 예제는 독립 수학 검토자가 직접 유도했으며 Python/CAS로 실행하지 않았다.

## 6. 사건·에너지·정규화에 연결하는 위치

N과 E의 각 cumulative response에 같은 h와 W를 적용한다. Joint N/E law가 없으면 결과 product는 outer information set으로 유지한다. 실제 source alternatives 6개는 여섯 별도 결론이며 합산하지 않는다.

같은 N/E pair가 기존 native25, photon, binding, fast-electron reservoir 사상의 단일 event를 소유한다. 이 primitive는 source injection event를 새 capture event로 바꾸거나 external energy를 중복 계상하지 않는다. 기존 SI 변환 n=1e6 N, e=1e6 eV_J E, event energy E_gamma=e+I*n과 native indices를 그대로 재사용한다. 이미 SI인 값은 다시 변환하지 않는다.

Actual recipient nb 미제공이면 proper-volume 결과와 null native projection을 유지한다. 정리의 적분량에는 1/H 또는 mean stopping time을 곱하지 않는다. Proper/eta 평균을 요청할 때만 명시적 DeltaT 또는 Deltaeta로 나누고, ddt와 ddeta는 독립 입력으로 유지한다.

변하는 reference의 endpoint state change,
s(F_b/b_b-F_a/b_a)
 =s(F_b-F_a)/b_b+sF_a(1/b_b-1/b_a),
및 양쪽 b의 quotient JVP는 기존 증명·검사를 재사용한다. 본 scalar history primitive는 이를 임의의 integral j(t)/b(t)dt로 대체하지 않는다. 현재 PHYS02의 absolute cell volume과 actual nb를 추정하지 않는다.

## 7. 현재 물리 입력과 다음 코드 검사

새로 공개된 CR109의 실제 Q_e(W,t)=t*A(W)는 저장된 source model이다. 그러나 100 K·HeIII=0이며, 현재 CR108 응답은 10,000 K·nHeIII=0.01cm^-3다. Spectral pulse template 동일성도 아직 결속되지 않았다. Q_e=t*A를 이 정리에 넣으려면 차원을 포함한 A(W)=alpha*f0(W)라는 실제 spectral identity가 필요하다. 총 N/E 비율만으로 alpha나 이 동일성을 정하지 않는다. 따라서 actual source-to-response join, 실제 alpha의 추출, 실제 count/energy history 수치는 이번 결과에 포함되지 않는다. 기존 pulse raw4와 PREEXEC bytes를 보존한다.

새 구현은 closed interval과 exact Fraction을 입력으로 받는 O(m) exact-rational arithmetic operations의 scalar map; 비트 복잡도는 분자·분모 길이에 의존한다. 이 map이다. 단위 변환, closure 재계산, raw 입력 파싱, provider solve, nb projection을 수행하지 않는다. Binding helper는 state/template/frame/volume/clock의 missing과 mismatch를 구분하되 identifiers의 물리적 진실성을 인증하지 않는다.

저장된 새 source code의 실행·수치 검증은 NOT_RUN_BUDGET_HOLD다. 예산이 별도 승인되면 새 stdlib unit tests만 단회 실행한다. 기존 attempt01·83·NCP·IVP·projection·quadrature·provider solve·old fullsuite는 실행 대상이 아니다.

## 원문

- REI PR240 THEORY: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a70d19b0a79c200d1e0b6a18ff69f856e8fef4c7/research/rei_expanded_event_consumer/causal_prefix_consumer_20261027/theory/THEORY_KO.md
- CR109 theory: https://github.com/cosmosapjw-quantum/bass_cr/blob/7f3ad7afeacb5f4d386e54fbc6b80a98d698bc22/research/cr_proper_injection_20261027/THEORY_KO.md
- CR109 contract: https://github.com/cosmosapjw-quantum/bass_cr/blob/7f3ad7afeacb5f4d386e54fbc6b80a98d698bc22/research/cr_proper_injection_20261027/CONTRACT.md

직접 증명 외의 새 문헌 novelty 또는 strong no-go를 주장하지 않는다. NG1–NG7 신규 채택 대상은 없다. SciSpace·Exa·Wolfram의 기존 source-qualified 조사·검산은 해당 원문 범위로 재사용하며 동일 계산을 다시 실행하지 않았다.

