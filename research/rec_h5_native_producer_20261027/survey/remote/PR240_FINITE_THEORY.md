# 유한 주입 cohort의 정확한 누적응답 정보 경계

## 결과

같은 pulse의 누적응답 F에 대한 closed interval·monotonicity 정보와 기록된 유한 주입 cohort h_C가 주어졌다고 하자. 아래 전제에서 선택 cohort의 시간창 반환량은
\[
D_{A,B}[F]=\int_{(0,t_m]}K_{A,B}(\tau)\,dF(\tau),
\quad K_{A,B}(\tau)=G(B-\tau)-G(A-\tau)\ge0.
\]
각 response cell의 closed-kernel min/max를 q_i^-/q_i^+라 하면 정확한 정보 경계는
\[
\inf_{F\in\mathcal P}D_{A,B}
=\min_{x\in\mathcal X}\sum_iq_i^-(x_{i+1}-x_i),\qquad
\sup_{F\in\mathcal P}D_{A,B}
=\max_{x\in\mathcal X}\sum_iq_i^+(x_{i+1}-x_i).
\]
이 LP는 유한 수준 V={0,l_1,u_1,...,l_m,u_m} 위 prefix DP로 정확히 계산된다. 양 끝은 원래 F-space에서 infimum/supremum이며 달성 여부는 별도다.

## 1. 전제와 source 해석

0=t_0<...<t_m. F는 [0,t_m]에서 비음수·비감소·우연속이고 F(0)=0이다. closed bounds는 0=l_0=u_0, 비감소 l/u, 0<=l_i<=u_i<=P_U를 만족한다. \(\mathcal P\)는 이 knot bounds를 만족하는 F들의 집합이다. t_m 뒤 constant extension으로 기존 all-time cap을 유지할 수 있다.

선택 cohort C=[0,S]의 h_C는 nonnegative piecewise-affine이며 finite partition에서 제공된다. cohort 밖의 zero는 선택 연산이다. 전체 물리 source가 S 이후 꺼졌다는 가정은 하지 않는다. 물리 source 전체의 반환량을 원하면 전체 history를 별도로 결속해야 한다. 현재 CR109 history는 [0,10^10]s에만 알려져 있다.

\[
G(x)=\int_0^{\min(\max(x,0),S)}h_C(s)\,ds,\qquad
C_C(T)=\int_0^{\min(T,S)}h_C(s)F(T-s)\,ds.
\]
\(F(t)=0\) for t<0으로 정의하면 같은 식을 전체 source support 위에 쓸 수 있다. Query는 0<=A<=B<=t_m이다.

Convolution 자체는 CR109 THEORY_KO.md의 기존 결과다. 같은 spectral template f0, 동일 frozen linear stationary response, bath/state/frame/clock, fixed proper volume 또는 이미 결속한 common-volume pullback을 유지한다. 시간변하는 operator나 feedback에 대한 결과를 포함하지 않는다.

## 2. Stieltjes 표현

우연속 monotone F와 F(0)=0으로부터 유한 양의 measure \(\mu\)를 \((0,t_m]\)에 정의하여
\[
F(t)=\mu((0,t])
\]
로 쓴다. 0에는 atom이 없다. Tonelli로
\[
\begin{aligned}
C_C(T)
&=\int_0^S h_C(s)\int_{(0,t_m]}{\bf1}_{\tau\le T-s}\,d\mu(\tau)\,ds\\
&=\int_{(0,t_m]}G(T-\tau)\,d\mu(\tau).
\end{aligned}
\]
따라서 \(D_{A,B}=C_C(B)-C_C(A)=\int K_{A,B}\,d\mu\)다. G가 비감소라 K>=0이고 B<=t_m이므로 K(t_m)=0이다.

\(w(\tau)=h_C(B-\tau)-h_C(A-\tau)\)라 하면 거의 모든 곳에서 K'=-w다. 원래 F-integral의 signed weight와 Stieltjes kernel의 비음수성을 구별한다. h_C의 jump가 있어도 G/K는 연속이다.

## 3. Cumulative-chain LP

\[
x_k=F(t_k),\quad m_i=x_{i+1}-x_i=\mu((t_i,t_{i+1}]),
\]
\[
\mathcal X=\{x_0=0,\ l_k\le x_k\le u_k,\ x_{k-1}\le x_k\}.
\]
\(x=l\)이 feasible이고 모든 coordinate가 bounded이므로 \(\mathcal X\)는 nonempty compact polytope다.

연속 K에 대해
\[
q_i^-=\min_{[t_i,t_{i+1}]}K,\qquad
q_i^+=\max_{[t_i,t_{i+1}]}K.
\]
어떤 fixed chain x에 대해서도
\[
\sum_iq_i^-m_i\le\int K\,d\mu\le\sum_iq_i^+m_i.
\]
각 m_i는 비음수이므로 signed K에서도 이 부등식은 유지된다.

### Sharpness의 구성

고정 x에서 cell별 kernel minimum location \(a_i^-\)를 선택한다. \(a_i^->t_i\)이면 해당 위치에 atom mass m_i를 둔다. \(a_i^-=t_i\)이면 \(a_{i,n}^-=t_i+(t_{i+1}-t_i)/n\), n>=2처럼 cell 안의 점으로 접근한다. Zero mass cell은 아무 atom도 두지 않는다. 이렇게 얻는 \(\mu_n\)은 모든 n에서 동일한 x_k를 정확히 유지한다.

K의 연속성과 유한 cell 수 때문에
\[
\int K\,d\mu_n\longrightarrow\sum_iq_i^-m_i.
\]
Maximum에도 동일하게 적용한다. LP의 최적 chain을 선택하면 주장한 전체 inf/sup가 된다. 정보집합 \(\mathcal P\)의 모든 knot/monotonicity/cap 조건을 보존하는 구성이다.

LP 쪽 min/max는 달성되지만 원래 measure의 cell 왼쪽 endpoint는 제외돼 있다. 그러므로 최적 chain의 존재를 원래 F의 minimum/maximum 존재로 바꾸지 않는다. API의 atom locations는 closure witnesses다.

## 4. 유한 수준 lemma

\(\mathcal X\)의 모든 vertex coordinate는
\[
V=\{0\}\cup\{l_k,u_k:1\le k\le m\}
\]
에 속한다.

증명: 어떤 maximal constant plateau의 값 c가 V 밖이라고 하자. x_0에 닿는 plateau라면 c=0이므로 모순이다. 나머지 plateau의 모든 lower/upper constraint에는 양의 여유가 있다. 양쪽에 다른 plateau가 있으면 그 값과도 양의 간격이 있다. 따라서 충분히 작은 epsilon으로 plateau 전체를 함께 올리거나 내려도 feasible하다. 원래 점이 두 다른 feasible point의 midpoint가 되므로 vertex일 수 없다.

선형 objective는 compact polytope의 vertex에서 최적화되므로 V의 finite chains만 탐색하면 충분하다. 이는 p-box extreme-level 선행 결과의 variable-total finite-chain 적용이다. 일반 vertex 성질에 문헌 신규성을 주장하지 않는다.

## 5. Exact prefix DP

Cell coefficient c_i를 q_i^- 또는 q_i^+로 둔다. 초기 state는 \(M_0(0)=0\), 다른 값은 unreachable이다. 최소화의 recurrence는
\[
M_k(v)=c_{k-1}v+
\min_{\substack{y\in V\\y\le v}}
\{M_{k-1}(y)-c_{k-1}y\},
\qquad l_k\le v\le u_k.
\]
최대화는 min을 max로 바꾼다. 마지막 feasible state들의 최적값을 취한다. Sorted V를 순회하면서 prefix best를 유지하면 단계마다 O(|V|), 전체 O(m|V|) exact arithmetic이다. Parent pointers가 endpoint witness chain을 복원한다.

Kernel extrema 구성과 sorting은 이 DP 비용 밖이다. Rational 분자/분모 bit length에 따라 각 산술 연산 비용이 달라진다. 실행 성능을 측정하지 않았으므로 wall-time speedup을 주장하지 않는다.

## 6. Piecewise-affine kernel의 유한 candidate

각 source piece \([s_j,s_{j+1}]\)에서
\[
h_C(s)=\beta_j+\alpha_js
\]
이고 양 끝값이 비음수다. alpha_j는 음수여도 된다. Source partition이 [0,S]를 빈틈 없이 덮으며 zero gap은 explicit segment다.

G는 연속 piecewise quadratic이다. Response cell을 다음 점에서 분할한다.

- cell 양 끝
- 안에 들어오는 \(A-s_j\), \(B-s_j\), source의0과S 포함

각 open subpiece에서
\[
K'(\tau)=h_C(A-\tau)-h_C(B-\tau)=p+q\tau.
\]
q!=0이면 root \(-p/q\)가 subpiece 안에 있을 때 candidate에 더한다. q=0인 constant derivative에는 추가 내부 candidate가 필요 없다. q=p=0이면 K가 constant다. 전체 candidate에서 정확히 K를 평가하면 q_i^-/q_i^+와 deterministic tie location을 얻는다. Rational inputs이면 모두 rational이다.

이는 quadrature approximation이 없다. 정확성은 제공된 rational coefficients에 대한 수학적 정확성이며 source measurement/model error가0이라는 뜻은 아니다.

## 7. 여러 창의 공동 관측량

고정한 dimensionless weights \(\lambda_j\)에 대해
\[
D_\lambda[F]=\sum_j\lambda_jD_{A_j,B_j}[F]
=\int K_\lambda\,dF,\qquad
K_\lambda=\sum_j\lambda_jK_{A_j,B_j}.
\]
먼저 K들을 합친 다음 cell extrema와 LP/DP를 구한다. 음수 weight 때문에 K_lambda가 음수여도 앞 증명은 유지된다.

개별 window q_i^- 또는 q_i^+를 먼저 합하면 cell 내부 atom 위치의 공유 조건을 잃는다. 동일 endpointchain만 공유하는 방식도 충분하지 않다. Kernel-first 방법은 chain과 atom 위치를 함께 공유한다.

실제 D(F)는 인접창에 가법적이다. 일반 history에서 최적화한 scalar lower/upper가 가법적인지는 별도이며 일반적으로 성립하지 않는다. 다음 예제는 그 차이를 정확히 보인다.

## 8. 정확한 사례

단위시간1s, h_C=1 on[0,1], grid(0,2), l=u=(0,1),cap1을 사용한다. 총질량1이(0,2]에 있다.
\[
K_{01}=(1-\tau)_+,
\quad
K_{12}=
\begin{cases}\tau,&0\le\tau\le1\\2-\tau,&1\le\tau\le2,\end{cases}
\]
\[
K_{02}=K_{01}+K_{12}=
\begin{cases}1,&0\le\tau\le1\\2-\tau,&1\le\tau\le2.\end{cases}
\]
세 window의 정보 구간은 모두 [0,1]이다. 따라서 U01+U12=2>U02=1. 첫 window의 supremum은 mass가0에 접근할 때, 둘째의 maximum은 age1에 있을 때 나온다. 같은 하나의 mass를 두 위치에 동시에 배치할 수 없다.

하한 비달성 사례는 같은 h_C/window12에 grid(0,1,2), l=u=(0,1,1)를 둔다. 질량1이(0,1]에 있어 \(\int\tau\,d\mu>0\)이지만 delta_epsilon sequence가0에 접근한다. 따라서 infimum0,minimum없음,supremum1이다.

이 사례들은 주어진 잘못된 가법성 일반화의 국소 반례다. 새로운 strong no-go를 채택하지 않는다.

## 9. 이전 affine 정리로의 환원

h(s)=beta+alpha*s,alpha,beta>=0가[0,B]에서 유효하면 \(w\ge0\), K는 비증가다. 따라서 q_i^-=K(t_i+1),q_i^+=K(t_i)이고 W_i=K(t_i)-K(t_i+1)>=0이다. K(t_m)=0으로 telescoping하면
\[
\sum_iK(t_{i+1})(x_{i+1}-x_i)=\sum_iW_ix_i,
\]
\[
\sum_iK(t_i)(x_{i+1}-x_i)=\sum_iW_ix_{i+1}.
\]
각각 x=l,x=u에서 최적이므로
\[
L=\sum_iW_il_i,\qquad U=\sum_iW_iu_{i+1}
\]
을 복구한다. 기존 정리의 lower minimum과 shared staircase 구조도 이 조건에서 유지된다. 새로운 theorem은 그 저장 계산의 재실행을 요구하지 않는다.

## 10. 물리 연결과 남은 의무

[h_C]=s^-1, [G]=[K]=1이며 D는 F와 같은 proper count/energy density다. 새 SI 변환 또는1/H가 없다. 같은 source 대안을 고정하고 N/E 각 scalar의 product를 outer information set으로 유지한다. actual recipient nb가 없으면 native25 projection은 null이며 b fixture를 대신 쓰지 않는다.

CR108 finalC9, source-state/spectral matching, 실제 recipientnb, 선택된 photon/finiteopacity/transport/HEstopping/VigilODEclient 의무는 SOURCE_SURVEY/원계약에 기록한다. BASS203의 동일 scalar Lyalpha tube에서 이미 완료한 endpointstocks/opacity/commonvolume/represented photonreturn은 재사용하고, 실제 QSS/non-Lyalpha owner와 physical radii만 열린 상태로 둔다.

현재 판정: DERIVED_AND_INDEPENDENTLY_REVIEWED within interval-monotonicity information set.
Code/test sources는 별도로 작성·정적검토됐으며 runtime은 NOT_RUN_BUDGET_HOLD다.
원래 DAG 작업32/88·중앙27/88·증분0,L4false,globalphysicalcompletionnull.

## 원전

- CR109 THEORY_KO.md at8482ed83b14517b709ba6e801f6714cc333e720f: 기존 response convolution과 recorded source domain.
- REI affine THEORY_KO.md atfbb55bcd0c77990b62470862a9f4a70647d0c5c9.
- Utkin & Destercke, arXiv:0906.1260, https://arxiv.org/pdf/0906.1260 .
- Skulj, arXiv:2203.11634, Theorem1, https://arxiv.org/pdf/2203.11634 .

