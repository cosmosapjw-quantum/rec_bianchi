# REC R6: finite clock and conserved-current identities

Public theoretical extract. Native inputs and backup receipts remain private. Derived and symbolically checked; no full-history convergence or physical detection claim.

## 2. 유한 전단의 정확한 clock 분해 [RC6-01]

서명은 (-,+,+,+), c는 유지한다. 비경사 배경의 기체 proper time t와 L=ln(a)를 사용한다. 시작 slice는 a_r=1/21이고, t=0은 그 slice 이후 경과 시간이지 절대 우주 나이가 아니다. H>0인 구간에서 각 모형의 t_j(L)는 단조 증가한다.

기준과 후보를 각각0,q로 쓰자. 선택한 후보 사건 L에서

\[
 \Delta_LX(L)=X_q(L)-X_0(L),\qquad
 L_*(L)=t_0^{-1}(t_q(L))
\]

로 정의한다. 같은 proper time의 차이는

\[
 \boxed{\Delta_tX(t_q(L))=\Delta_LX(L)+C_X(L)},\qquad
 C_X(L)=X_0(L)-X_0(L_*(L)).                 \tag{RC6-01}
\]

이는 동일한 두 항을 더하고 뺀 정확한 항등식이다. q의 작음, 반응률의 선형성, Planck spectrum 또는 Peebles closure를 가정하지 않는다. 이번 구현은 (L,t,X)의 동일한 piecewise-affine 경로를 사용한다. 한 cell 안에서는 t도 X도 L의 affine 함수이므로, t를 역으로 풀고 X를 대입한 값은 동일한 원래 두 노드의 t-선형 보간과 같다. 별개 grid나 보간법으로 clock와 X를 섞지 않는다.

기준 경로를 실제 시간의 함수로 표시하면

\[
 C_X=-\int_{t_0(L)}^{t_q(L)}\dot X_0(u)\,du.
\]

따라서 t_q<t_0이고 X_0가 이 구간에서 증가하면 C_X>0이다. C_X가 음의 Delta_LX보다 크면 같은-time 차이의 부호가 바뀐다. 이 조건을 다른 시기·species에 무조건 전파하지 않는다.

직전의 q²·q³ 전개는 이 항등식의 작은-q 한계다. 현재 두 case만으로 X1,X2,X3를 분리하지 않았다. 원래 q=0,±q,±q/2의 다섯 case 계약은 보존한다. 이번 ionizing J0는 연속 방출·흡수가 있는 실제 비열적 photon stock의 에너지 모멘트이며, 이전의 collisionless Planck J4와 같은 물리량이 아니다. 여기서는 model-independent clock 대응식만 사용한다.


## 4. 전자분율과 전자밀도의 부호가 다른 이유 [RC6-03]

공통 비교 시간에서 ne=nH xe를 사용하면

\[
 \boxed{\Delta n_e=n_{Hq}\Delta x_e+x_{e0}\Delta n_H}. \tag{RC6-03}
\]

정확한 물리 변수에 대해서는 단순한 곱의 항등식이다. 현재 저장 경로를 변수별로 affine 보간할 때는 P(ne)와 P(nH)P(xe)가 반드시 같지는 않으므로, 둘을 비교할 때 해당 표현 차이도 남긴다. 실제 끝점의 분해는

\[
\begin{aligned}
 n_{Hq}\Delta x_e &=+6.92009692999\times10^{-10}\ {\rm cm}^{-3},\\
 x_{e0}\Delta n_H &=-6.98219193371\times10^{-10}\ {\rm cm}^{-3},\\
 \delta_{\rm representation}&=+9.69469865714\times10^{-16}\ {\rm cm}^{-3}.
\end{aligned}
\]

그 합은 직접 보간한 Delta_ne=-6.20853090211e-12 cm^-3와 일치하며 binary64 대수 잔차는6.87e-22 cm^-3다. 같은 시간의 후보 nH=2.7166521869515924e-4 cm^-3, 기준 nH=2.716717043400212e-4 cm^-3다. 분율 증가는 양수지만 후보의 더 큰 희석 효과가 이를 상쇄한다. 이 작은 cancellation 결과도 정확성 인증은 아니다.

두 scalar A,B를 같은 weight w로 보간하는 경우

\[
 P(AB)-P(A)P(B)=w(1-w)(A_1-A_0)(B_1-B_0)\tag{RC6-04}
\]

이므로 표현 차이를 바로 계산할 수 있다. 원본 자체의 floating arithmetic 반올림도 별도로 남는다. 이를 source conservation failure나 새로운 물리 효과로 해석하지 않는다. Baryon-normalized Ye=(1-YHe)xe는 이 선택된 H/He 모형에서 xe와 부호를 공유하지만, proper ne는 그렇지 않다. 따라서 abundance 그림과 opacity/electron-column 입력을 서로 대신하지 않는다.


## 5. 조건부 오차 전달 정리 [RC6-05]

이는 현재 미확인 오차를0으로 선언하기 위한 식이 아니라, 추후 어떤 입력이 실제로 필요한지 정하는 정리다. 같은 compact L 구간에서 true reference clock은 t0'(L)>=m>0이고 |X0'(L)|<=M이라고 가정하자. 근사 경로 hat_Xj,hat_tj가 각각 uniform errors epsilon_Xj,epsilon_tj를 가지며 두 inverse query와 그 사이가 이 구간 안에 있다고 하자. 계산한 inverse 위치를 hat_L*=hat_t0^{-1}(hat_tq(L)), 참 위치를 L*=t0^{-1}(tq(L))라 쓰면

\[
 |t_0(\widehat L_*)-t_0(L_*)|
 \le\epsilon_{t0}+\epsilon_{tq},\qquad
 |\widehat L_*-L_*|\le\frac{\epsilon_{t0}+\epsilon_{tq}}m.
\]

첫 식은 approximate clock 식을 넣고 삼각부등식을 쓰면 나오고, 둘째 식은 true clock의 양의 derivative 하한에 따른다. 따라서

\[
 \boxed{\left|\widehat\Delta_tX-\Delta_tX\right|
 \le\epsilon_{Xq}+\epsilon_{X0}
   +\frac{M}{m}(\epsilon_{tq}+\epsilon_{t0})}.\tag{RC6-05}
\]

L은 무차원, m은 s, M은 X 단위이므로 마지막 항의 단위도X다. arbitrary fixed t*에서 양쪽 inverse를 모두 쓰는 경우에는 각 모형의 (Mj/mj)epsilon_tj를 각자의 epsilon_Xj에 더한 뒤 합한다. 유효구간 경계를 넘어가는 query, H=0 근처의 clock 전환, 단조성을 잃는 온도축에는 이 정리를 그대로 적용할 수 없다.

cell 안의 true X가 C²이고 |X''|<=M2, 노드 오차가 e_i,e_{i+1} 이하라면, h=L_{i+1}-L_i, w=(L-L_i)/h에 대해

\[
 |X(L)-P\widehat X(L)|\le(1-w)e_i+w e_{i+1}
 +\frac{M_2}{2}(L-L_i)(L_{i+1}-L)
 \le(1-w)e_i+w e_{i+1}+\frac{M_2h^2}{8}.\tag{RC6-06}
\]

이는 true nodal interpolant의 표준 두-node remainder와 approximate nodal errors를 분리한 결과다. 계수 branch나 nonsmooth event를 건너면 먼저 적절한 구간을 구분해야 한다. 원본 a에서 계산한 binary64 ln(a)의 좌표 오차도 true-coordinate bound에서는 노드 오차/좌표 항에 포함해야 한다.

현재 비교에서 m,M,M2 및 accumulated history error를 실제로 인증하지 않았으므로 결과 파일은 evolution_error=null, interpolation_error=null을 유지한다. 80자리 대조는 산술 구현을 검증하지만 이 두 null을 채우지 않는다. 이 rigorous bound를 기존 point/empirical-refinement 연구의 새 전역 선행조건으로 추가하지 않는다. 원래 계획된 empirical convergence는 그 근거 수준을 명시해 그대로 진행할 수 있다.


## 6. 오차 입력에 연결되는 공변 미분 [RC6-07]

기체의 physical four-velocity를 U^a, U.U=-c²로 두고 dot=U^a nabla_a를 사용한다. 핵종 수를 바꾸지 않는 선택된 원자 H/He 모형에서

\[
 \nabla_a(n_HU^a)=0,\qquad
 \nabla_a(n_Hx_sU^a)=R_s
\]

이면 product rule로

\[
 \dot x_s=R_s/n_H.\tag{RC6-07a}
\]

여기서 Rs는 proper cm^-3 s^-1, nH는 proper cm^-3이며, expansion dilution은 분율의 동일한 기준 전류를 나누는 과정에서 정확히 상쇄된다. 이는 proper density 자체의 dilution을 버리는 근사가 아니다.

일반 scalar에 대해

\[
 \ddot X=U^aU^b\nabla_a\nabla_bX
       +(U^a\nabla_aU^b)\nabla_bX,
\]

그리고 H>0에서

\[
 \boxed{X_{LL}=H^{-2}\ddot X-H^{-3}\dot H\dot X}.\tag{RC6-07b}
\]

따라서 M2를 물리 RHS에서 공급하려면 full coupled state와 clock을 미분해야 한다. 온도 의존 atomic coefficient 한 항만 미분하거나 source/photon feedback를 생략한 값으로 대체할 수 없다. 비경사 geodesic 특수화에서는 acceleration 항이 사라지지만, xAct 검산에서는 일반 항을 먼저 보존했다.

Wolfram15.0.0+xTensor1.3.0에서 기준 current product, second convective derivative, proper-time→ln(a) second derivative의 세 잔차가 모두 정확히0이었다. 이는 abstract tensor calculus 검증이다. xCoba 성분 계산, Einstein-solved trajectory 또는 독립 agent review를 실행했다고 부르지 않는다. cloud Wolfram15.0.1에서는 composition 계수, midpoint curvature factor, 유한 clock 반례와 density split을 추가 대조했다.
