# R5 — explicit incoming electron point field의 구성적 유도

중앙 DAG28/88(+0), 단위 내용5/20. R1–R4의 정의와 source identity를 따른다. 본 절의 정리는 고정된 coefficient point에 대한 조건부 실수 대수 명제이며, 뒤의 C단계가 그 source-equivalent binary64 구현을 검증한다.

## 1. Stable scalar source의 재구성

p=xHII, x1=1-p, D=xe*p-s*x1로 두고, 원래 interpolate_rates가 반환하는
a_i=Alpha_i(TM,TR), a_i^eq=Alpha_i(TR,TR),
DAlpha_i=a_i-a_i^eq를 사용한다. a^eq를 계산한 뒤 detailed-balance factor를 곱해 Beta_i를 만드는 원본 순서를 따른다. Beta_2p에는 추가1/3 degeneracy factor가 있다.

c_i=nH[s*x1*(a_i-a_i^eq)+a_i*(xe*p-s*x1)]
   =nH[a_i*xe*p-a_i^eq*s*x1].

두 표현은 실수 대수에서 같다. 첫 식은 원래 source가 nearly-cancelling equilibrium contribution을 분리하는 표현이며 구현에서는 원래 grouping을 보존한다. 이를 직접 대입하면

FH=-(c_0+c_1-Beta_0*xr_0-Beta_1*xr_1)/H.

nH*a는 s^-1, Beta도 s^-1이며 H로 나누므로 FH는 eta=ln(a)당 비율 변화이다. xr는 절대 level population이 아니라 equilibrium departure이다. xe와 p가 다른 경우에도 D=xe*p-s*x1을 쓰며 xe^2로 치환하지 않는다.

## 2. Incoming 의존성의 완전한 분리

원본 populateTS_2photon의 모든 incoming 사용 위치를 직접 대조한다. RLya=LYA_FACT(fsR,meR)*H/nH/x1,
k_beta=1.664786871919931로 두면

sr_0=c_0+3*RLya*x1*k_beta*u_Ly,1,
sr_1=c_1+3*RLya*x1*u_Ly,0.

virtual row b의 원 source는

sv_b=V_bb*x1*(1-omega_b)*u_v,b,

여기서 omega_b는 source의 one_minus_Pib이다. 실제 source는 tau_b>1e-6에서 1-(1-exp(-tau_b))/tau_b, 그 밖에서는 tau_b/2-tau_b^2/6을 사용한다. V_bb는 tau_b>0 조건의 별도 branch를 가진다. 이번 주장의 대상은 이 원 source의 이산 coefficient이며 branch를 새 expm1 근사로 바꾸지 않는다.

A=Trr, B_ib=Trv[i][b], C_bi=Tvr[i][b], V는 Tvv band로 만든다. Alpha,DAlpha,Beta,RLya,diffusion coefficients,tau,omega,A,B,C,V 중 어느 항도 incoming을 읽지 않는다. 이들은 P와 초기화된 tables 및 feature macros만 읽는다. sr와 sv의 위 세 위치가 incoming 전체 의존성이다.

따라서 S0=(c_0,c_1,0,...,0)^T이고 S=S0+G u이다. G의 real rows는 두 Lyman 항, virtual rows는 diagonal 계수 V_bb*x1*(1-omega_b)이다. 고정 P에서 M=[A B; C V]는 u 독립이다.

## 3. 정확한 block 방향과 elimination

원 source solve_real_virt의 Tvv_inv_Tvr[i][b]는 V^-1 C의 column i이고, Tvv_inv_sv는 V^-1 sv이다. 저장 배열 Tvr[2][311]은 수학적 block C[311][2]의 column들을 담는다. B와 C를 바꾸거나 대칭이라고 가정하면 다른 방정식이 된다.

V의 row b에서 lower=Tvv[1][b]=-Aup[b-1], upper=Tvv[2][b]=-Adn[b+1]이다. diffusion 밖의 미기입 항은 원래 calloc의0이다. Ly-alpha 사이의 연결은 upper[139]=lower[140]=0으로 끊기고 real2p를 통해 결합된다. solveTXeqB 호출은 (diag,Tvv[2],Tvv[1]) 순서이다. 이 원래80-bin diffusion solve와 나머지 diagonal division을 그대로 따른다.

V의 해당 divisors가0이 아니고 Q=A-B V^-1 C의 determinant가0이 아니면

q=sr-B V^-1 sv,
xr=Q^-1 q,
xv=V^-1 sv-V^-1 C*xr.

역대입하면
C*xr+V*xv=sv,
A*xr+B*xv=(A-B V^-1 C)*xr+B V^-1 sv=sr.
따라서 M X=S이며 해는 유일하다. 이는 source의 실제 Schur 순서와 일치한다. 전체313x313 inverse를 새로 계산할 필요가 없다.

Nonzero divisor와 determinant 조건은 각 실제 point에서 확인할 적용 조건이다. 이 유도는 모든 scalar domain에서 diagonal dominance, coefficient-box nonsingularity 또는 inverse gain을 증명한 것이 아니다.

## 4. Affine incoming 정리와 그 실제 사용

앞의 조건하에서
X(u)=M^-1 S0+M^-1 G u.

e=(Beta_0,Beta_1,0,...,0)^T, c=c_0+c_1이면
FH(u)=-c/H+e^T M^-1 S0/H+e^T M^-1 G u/H.

따라서 u→FH는 실수 대수에서 affine이다. 두 incoming u,v와 실수 t에 대해
FH((1-t)u+t v)=(1-t)FH(u)+t FH(v).
P를 함께 바꾸면 일반적으로 성립하지 않는다. Binary64 output의 exact affinity도 주장하지 않는다. 이 결과는 radiation 누락/clipping을 식별할 control과 독립 block residual reconstruction에 사용한다.

Signed departure를 허용해야 한다. u<0 자체는 이 대수 명제의 금지 조건이 아니며0으로 clipping하면 원래 G u를 바꾼다. 이 사실이 임의의 u에 대한 물리적 spectrum positivity를 증명하지는 않는다.

## 5. Point API의 source-equivalence와 purity

원 FULL 함수의 순서는 dispatcher scalar rescale, history에서 incoming 생성, block assembly, solve, FH scalar, history writes이다. explicit-incoming API는 정확히 같은 scalar prelude를 한 번 적용하고, 이미 계산된 incoming311+2를 받아 동일한 assembly/solve/scalar 순서를 실행한다.

History interpolation을 외부 입력 경계로 옮겼으므로 주어진 incoming 자체를 생성할 전체 radiation history가 필요하지 않다. FH 계산 뒤의 outgoing/average history write는 이미 산출된 FH에 역방향 의존성이 없으므로 생략 가능하다. Fresh local blocks를 사용하고 원래 read-only tables를 유지하면 caller의 incoming·state·tables·history를 수정할 이유가 없다. 이 구조를 C단계에서 실제 API와 nonmutation 검사로 구현한다.

Tables 초기화는 별도 context 생성 단계이다. read_twog_params의 A2s normalization 및 macros를 포함한 native initialization을 사용한다. Point evaluation은 files를 열거나 tables를 다시 초기화하지 않는다.

## 6. Total electron 해석과 적용 한계

원 history H_STEADY branch는 He-neutral이며 rec_get_xe_next1_H가 xe를 xe와 xHII 양쪽 인자로 전달한다. 따라서 primary132 final writers에서 실제 equality와 phase를 확인하면 Fe=dxe/deta=dp/deta=FH이다. H_STEADY는 Tm steady closure를 가리키므로 FH=0이라는 뜻이 아니다.

이 구성은 명시적 incoming을 가진 source-point component이다. Incoming history의 autonomous evolution, continuous whole-domain coupled F, model discrepancy, e0, full-state norm, positive tube는 별도 의무로 남는다. Saved native point와의 parity 및 작게 측정된 linear residual만으로 그 의무를 닫지 않는다. Central28/88,physical0/313은 그대로이다.

## 7. 독립 검토와 구현에 넘길 항목

Fresh nonauthor R6는 원본 source에서 별도 유도한 block, charge accounting, rescale path, table initialization, signed departures, source parity 조건과 이 문서를 대조한다. C3는 연산 순서를 바꾸지 않는 최소 internal divisor observation을 정한다. C7/C8은132 actual writer binding,source parity,independent residual,nonmutation,적절한 mutation controls를 수행한다. 이 단계까지 새 native/scientific field 호출은0이다.
