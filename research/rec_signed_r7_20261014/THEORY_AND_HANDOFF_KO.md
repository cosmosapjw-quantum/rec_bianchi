# REC R7: finite signed-history parity

2026-10-14. Public scientific supplement. Private input rows and backup objects are not distributed in Git. These are three-case partial diagnostics, not full-history accuracy or physical detection.

## 2. 정의와 clock parity

Metric signature(-,+,+,+), 기체 proper seconds t를 사용한다. c, ħ, k_B를1로 두지 않는다.

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
\quad H=\dot a/a,\quad s=\dot b.
\tag{R7-01}
\]

선택 배경은

\[
s=qg(a),\quad H_q(a)=\sqrt{H_F(a)^2+q^2g(a)^2},\quad
\frac{dt_q}{dL}=H_q^{-1},\quad L=\ln a,
\tag{R7-02}
\]

이고 동일한 초기 slice에서 t_q=0이다. 따라서 모델의 정확한 clock은 t_+(L)=t_-(L)이며 b_+(L)=-b_-(L)이다. Clock은 zbar20 이후 경과 시간이지 절대 우주 나이가 아니다. 일반 Bianchi 모델, 독립적인 선원 clock, tilt 또는 다른 initial slice로 이 동등성을 자동 확장하지 않는다.

한 물리량 X의 finite-amplitude contrast를

\[
E_L(L)=\frac{X_+(L)+X_-(L)}2-X_0(L),\qquad
O_L(L)=\frac{X_+(L)-X_-(L)}2
\tag{R7-03}
\]

로 정의한다. E는 단순 even part가 아니라 기준을 뺀 even contrast다. O는 기준값을 전혀 포함하지 않는다.

같은 경과 proper time t_s=t_+(L)=t_-(L)에서의 비교는

\[
\boxed{E_t(t_s)=E_L(L)+X_0(L)-X_0(t_s),\quad
O_t(t_s)=O_L(L).}
\tag{R7-04}
\]

첫 식은 R6의 유한 clock identity를 두 signed case에 더한 것이고, 둘째 식은 그 차를 취한 것이다. **O_t와 O_L의 함수 인수가 같은 숫자라는 뜻은 아니다.** t_s(L)로 짝지은 사건에서 정확히 일치한다. Tgas로 재정렬하거나 서로 다른 시간 원점을 쓰면 이 논증이 적용되지 않는다.

일반적으로 clocks가 다르면 t_*를 정한 뒤 D_±=X_±(t_*)-X_±(L), D_0=X_0(t_*)-X_0(L)로 두어

\[
E_t-E_L=(D_++D_-)/2-D_0,\quad O_t-O_L=(D_+-D_-)/2
\tag{R7-05}
\]

를 사용해야 한다. 두 signed clock이 다를 때 코드가 R7-04를 강제하지 않는 negative test를 포함했다.


## 3. 실제 세 이력의 새 판별 결과

원본 PLUS/MINUS의200001개 accepted L과 proper-time 배열은 실제로 동일했다. 각도·물질 값의 동등성은 가정하지 않았다. 공통 t 질의는 각 L에서 세 실제 clock의 최소값으로 정했고, 이 자료에서는 signed clock이다. 원래 adjacent accepted rows 사이의 joint affine path를 평가했다. ln(a) 좌표와 입력 값의 binary64 target을 명시하고 별도 Decimal80 경로로 같은 target을 계산했다.

원본 공통 끝점의 값은 다음과 같다. 작은 숫자는 저장 경로의 산술 차이이며 물리적 정밀도 표시가 아니다.

| X | E_L | O_L | E_t | O_t |
|---|---:|---:|---:|---:|
| x_HII | -1.25675786739e-6 | 9.02056207508e-17 | 2.34431612547e-6 | 9.02056207508e-17 |
| x_HeII | -1.31577478896e-6 | 9.50628464835e-16 | 2.49338934311e-6 | 9.50628464835e-16 |
| x_HeIII | -6.89832122265e-10 | 2.91379333855e-19 | 1.57728556404e-9 | 2.91379333855e-19 |
| Tgas [K] | -2.65420225101e-2 | 5.82076609135e-11 | 6.49073391241e-2 | 5.82076609135e-11 |
| xe=ne/nH | -1.36384430483e-6 | 1.73472347598e-16 | 2.54728852032e-6 | 1.73472347598e-16 |
| ne [cm^-3] | -3.70509061340e-10 | 4.57397791517e-20 | -6.20853094785e-12 | 4.57397791517e-20 |
| J0 [eV/H] | -5.73816869671e-11 | -6.77626357803e-21 | 2.03733721865e-9 | -6.77626357803e-21 |
| J2 [eV/H] | 4.34471762712e-19 | -2.66717119708e-12 | 4.33585724645e-19 | -2.66717119708e-12 |

434개 고정 격자점에서 max|O_L(x_HII)|=2.30718222305e-16, max|O_L(T)|=6.41193764750e-11 K다. 이는 각각 기존 abundance/T floors보다 훨씬 작은 저장값이다. 이를 물리적인 O=0 증명, 상계 또는 resolved null로 해석하지 않는다. Global evolution, angular/energy refinement, interpolation errors는 여전히 null이다. 반대로 E가 특정 floor보다 커도 총 수치 오차가 없으므로 물리 검출이라고 판정하지 않는다.

J2의 홀수 성분은 원본 끝점에서 J0의 약 -6.48516974902e-8배다. 이 비는 같은 에너지 단위의 저장 moment ratio이고, 온도 또는 abundance의 상대오차가 아니다.


## 4. J2를 방향 없는 scalar와 같은 대칭 검사에 넣지 않는다

J2=∫P2(mu) dU의 단위는J0와 같은 에너지/H다. 선택한 대칭축에 대한 rank-2 방사 moment 성분이며, 방향벡터 없이 정의되는 매끄러운 local rotational scalar가 아니다. 축대칭 압력 tensor를

\[
P^i{}_j=\mathrm{diag}\bigl((U-Q)/3,(U-Q)/3,(U+2Q)/3\bigr)
\tag{R7-06}
\]

로 쓰면 Q=P_parallel-P_perp=J2(동일 proper-volume 변환 포함)다. Tr P=U이고 Q=(3P_parallel-U)/2다. 따라서 전단의 일차 ℓ=2 forcing이 J2에 남는 것은 scalar abundance의 선형 소거와 모순되지 않는다. ∫P2 dmu/2=0, ∫P2² dmu/2=1/5를 실제 Wolfram에서 확인했다.

동일한 비교 frame에서 σ_±=±s S, Π_±=Π_E±Π_O라 하면 shear work W=σ:Π의 even/odd parts는

\[
\boxed{W_E=sS:\Pi_O,\quad W_O=sS:\Pi_E.}
\tag{R7-07}
\]

축대칭 S=diag(-1,-1,2)에서는 W_E=2sQ_O, W_O=2sQ_E다. 즉 홀수 사중극자와 홀수 전단의 곱은 짝수 에너지 work다. 같은 source와 unit 변환을 사용해야 하며, 이 국소 tensor 항등식 자체가 실제 full RT 에너지 residual이나 전체 물리 error를 인증하지는 않는다. 비경사 radiation work식은 proper energy density에 대해 dot U+4HU+σ:Π=collision/source로 쓴다. 코드의 U/H당 변수와 비교할 때 nH 및 eV→erg 변환을 먼저 한다.

서로 다른 시공간의 tensor를 그냥 빼는 연산은 정의하지 않았다. 원 source에서 사용하는 축이 정렬된 local orthonormal frame/사건 짝지음을 선언한 뒤 algebraic parity를 취한다. xAct 결과는 그 명시된 fibre에서의 tensor 항등식이다.


## 5. 홀수 비교에 필요 없는 기준 오차를 제거한다

고정된 같은 L 또는 같은 t에서 각 evaluated X의 유효 오차가 ε0,ε+,ε-라면 삼각부등식으로

\[
\eta_E\le\epsilon_0+(\epsilon_++\epsilon_-)/2,\qquad
\boxed{\eta_O\le(\epsilon_++\epsilon_-)/2.}
\tag{R7-08}
\]

기준 ZERO의 값과 오차가 O에서 정확히 상쇄된다. 따라서 ε±가 주어지고 ε0만 없을 때, odd의 조건부 오차 전달은 가능하고 even만 null로 남긴다. 이것은 새로운 covariance나 error independence 가정이 아니다. 전체 half-amplitude 연구가 완료되어야만 이미 있는 ±q 쌍을 후처리할 수 있다는 불필요한 의존성을 만들지 않는다.

단, 질의 시각 자체가 오차가 있는 baseline clock에서 만들어졌다면 그 위치 불확실성은 별도다. Baseline **value error**의 소거가 baseline-defined **query-time error**까지 소거하지는 않는다. R7-08의 ε는 필요한 이력·보간·inverse-clock·산술 오차를 포함한 유효 오차이고, 그것들의 입력 계약은 R6와 같다. 현재 source에서는 이 물리 오차들을 실제로 확보하지 못했으므로 결과표의 eta_E/eta_O도 null이다.

기체 current의 밀도 곱에서도 parity를 정확히 유지한다. n_H±=nE±nO, xe±=xE±xO라 하면

\[
(n_Hx_e)_E=nE xE+nO xO,\quad(n_Hx_e)_O=nE xO+nO xE.
\tag{R7-09}
\]

공통 사건에서 nO=0이면 O_ne=nH O_xe다. 그러나 ne,nH,xe를 각각 affine 보간한 경로는 P(nH xe)=P(nH)P(xe)를 자동 만족하지 않는다. 그 commutation defect는 R6의 정확한 w(1-w)ΔnHΔxe 항으로 따로 계상한다. 이번 native endpoint에서는 같은 source의 직접 밀도와 전자 census를 사용한다. 다른 T 또는 source의 warm He ratio를 복사하지 않는다.


## 6. 세 case에서 cubic coefficient를 발급하지 않는 이유

회전 불변 scalar의 충분히 매끄러운 continuum family라면 선형 응답은0이고 quadratic/cubic가 허용된다. 그러나 실제 finite-grid 계산에서는 linear leakage 여부도 확인해야 한다. 일반적으로

\[
O(q)=qA_1+q^3A_3+q^5A_5+\cdots.
\tag{R7-10}
\]

한 비영 amplitude에서 A1→A1-q²λ, A3→A3+λ로 바꾸어도 첫 두 항의 합은 같다. 이 정확한 null direction을 symbolic 및 unit test로 확인했다. 따라서 한 amplitude의 O/q³를 검증된 A3라고 부르지 않는다. 이는 유한 데이터의 대수적 식별성 조건이며 새로운 일반 no-go/문헌 최초성 주장이 아니다.

기존 다섯-case 공식은 그대로 보존한다. 실제 ±q/2와 각 case의 지원구간·오차가 도착하면 동일 clock에서 기존 원래 식을 사용한다. 그 전에는 half-case 값을 보간·반사·0으로 만들지 않는다. Q2는 rank-2 moment여서 scalar A1=0 검사의 대상에 넣지 않는다.


## 7. 실행 증거와 한계

실제 새 실행은 세 원본의 읽기·3362행 추출,3480행 parity 후처리1회,16개 unit test, Wolfram symbolic1회와 xAct tensor1회다. 원자계산·생산 cosmological solver·이전 R6 표 재실행은0회다. TDD 최초 stub의 실패를 보존하고 구현 후16/16,exit0을 기록했다.

독립 Decimal80의 barycentric arithmetic과 binary64의 최대 gross-scaled 차이는5.53989088404916e-17이다. Equal-clock identity의 최대 gross-scaled residual은1.49089080458814e-16이고 사전 산술 기준4096eps=9.09494701772928e-13보다 작다. 이는 작은 contrast 자체의 상대오차가 아니라 원 피연산자 규모로 정규화한 산술 검사다. Directed interval bound 또는 물리적 정확도를 뜻하지 않는다.

Wolfram15.0.0+xTensor1.3.0에서 even/odd shear work, even/odd product current 및 odd current divergence의5개 residual이 정확히0이었다. xAct stdout·stderr·script·JSON 원 bytes는 Dropbox에서 materialize해 SHA를 확인했다. Cloud15.0.1에서는 moment projection,work 및one-amplitude null direction을 확인했다. xCoba/component/Einstein 계산은 실행하지 않았다.

Native subagents와 외부 독립 agent review는 NOT_RUN이다. 작성자가 실제 읽은 원문·새 독립 산술·CAS를 구분하며, 도구 수를 독립 과학심사 수로 세지 않는다.
