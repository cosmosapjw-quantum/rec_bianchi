# 다음 한 단계: full-P coefficient derivative provider의 수학 명세

작성: `/root/incoming_theory_review`. **후속 구현 명세이며, 이번 연구의 실행 성과나 활성화된 새 노드로 계상하지 않는다.** 새 계산·native 호출·저장된 캠페인 재실행은 수행하지 않았다. 현재 결과는 고정 coefficient point의 incoming response를 제공한다. 다음 단위의 목적은 같은 point에서 thermodynamic 방향을 coefficient jet으로 전달하는 것이다.

## 1. 먼저 고정할 미분 대상

현재 관계는 M X=a+G u, F=d+q^T X, M^T lambda=q, J=G^T lambda다. Exact-real M이 가역이고 선택한 coefficient map이 미분 가능하면

\[
\delta F=\delta d+(\delta q)^TX
+\lambda^T[\delta a+(\delta G)u-(\delta M)X]
+J^T\delta u.
\]

P=(xe,p,nH,H,TM,TR,fsR,meR)를 쓰되 이번에 이어받을 manifold는 He-neutral, xe=p, fsR=meR=1이다. 따라서 허용 방향은 delta xe=delta p, delta fsR=delta meR=0이다. 온도 좌표는 원 dispatcher 입력인지 rescale 이후 coefficient 입력인지 반드시 선언하고 그 prelude의 Jacobian을 한 번만 적용한다. Native binary64 온도 roundtrip과 real 식의 항등변환을 같은 것으로 취급하지 않는다.

**고립된 132개 coefficient snapshot만으로 P 방향의 미분은 정해지지 않는다.** 다음 작업은 P↦(M,a,G,q,d)의 주변 연장부터 선택해야 한다. 기존 G_real과 G_prefix 중 하나를 이름으로 고르는 것만으로 이 연장이 정의되지는 않는다.

특히 현재 prefix 모델은 **각 고정점에서 incoming u에 대해 정의한 실수 affine 연장**이다. P를 바꾸어 binary64 prefix를 다시 계산하는 map의 ordinary derivative를 제공하지 않는다. 따라서 지금의 J_prefix를 곧바로 P로 미분하는 것으로 full-P provider를 얻을 수 없다. Coefficient 생성의 real formula 또는 지정한 smooth local extension을 공급하고, native arithmetic까지 연결하려면 그 연장과의 rounding-error enclosure를 별도 제시해야 한다.

| 선택 | 다음 provider가 명시할 내용 |
|---|---|
| Source-real 연장 | 초기화된 table 값·상수의 represented lift를 고정하고 원 coefficient 식을 실수 함수로 구성한다. 새 M(P*)가 저장 M과 다르면 그 차이와 source bridge를 보존하고 새 baseline의 X/lambda를 구해야 한다. |
| Prefix 값에 맞춘 smooth local jet | P*에서 기존 represented/prefix 값을 유지하면서 어느 smooth source 식의 미분을 채택할지 별도로 정의한다. 이는 명시적인 local model이며, 원 rounding map의 미분으로 부르지 않는다. 값의 일치만으로 그 jet의 정확성이 따라오지 않는다. |

Binary64 rounding과 host exp를 포함한 원 프로그램을 P의 smooth 함수로 간주하거나, rounding의 미분을 설명 없이 1로 두어서는 안 된다. 원 G_real의 source-bridge 실패와 G_prefix 결과는 각자의 기존 지위를 유지한다.

## 2. 최소 공급 계약: coefficient JVP

새 API `coefficient_jvp(P*, deltaP, model_id)`는 source/table/branch/clock identity와 함께 **M0,a0,G0,q0,d0 및 deltaM,deltaa,deltaG,deltaq,deltad**를 반환해야 한다. M의 A/B/Cstored/V band 방향, G의 311 virtual+Ly0+Ly1 순서, 단위는 현재 계약을 따른다. 변화하는 Vbb와 optical depth를 서로 독립된 외부 값처럼 취급하지 않고 동일 source 식의 chain rule로 연결한다.

원 scalar에서 ci=nH(s*x1*DAlpha_i+Alpha_i*Delta), x1=1-p, Delta=xe*p-s*x1이므로

\[
\delta x_1=-\delta p,\qquad
\delta\Delta=2p\,\delta p-x_1\delta s+s\,\delta p,
\]
\[
\delta q_r={\delta\Beta\over H}-{\Beta\over H^2}\delta H,
\qquad
\delta d=-{\delta c_0+\delta c_1\over H}
+{c_0+c_1\over H^2}\delta H.
\]

Source-real branch를 택하면 virtual gb=Vbb*x1*pi(tau)의 jet은

\[
\delta g_b=x_1\pi\,\delta V_{bb}+V_{bb}\pi\,\delta x_1
+V_{bb}x_1\pi'(\tau)\delta\tau,
\]
\[
\pi'(\tau)=
\begin{cases}
[(\tau+1)e^{-\tau}-1]/\tau^2,&\tau>\theta,\\
-1/2+\tau/3,&\tau\le\theta,
\end{cases}
\qquad
\delta g_\alpha=g_\alpha(\delta H/H-\delta n_H/n_H),\quad
\delta g_\beta=k_\beta\delta g_\alpha.
\]

이 식을 prefix rounding map의 도함수로 사용하지 않는다. Prefix 기준의 smooth jet을 선택하면 명시한 그 연장에서 각 항을 유도한다.

필요한 원시 jet은 effective Alpha/DAlpha/Beta·transfer rate, Saha factor, Lyman escape, diffusion coefficients, optical depth와 전체 A/B/C/V assembly의 미분이다. Table 보간 cell, feature switches, optical-depth branch를 고정하는 열린 근방을 지정한다. 경계에서는 한쪽 jet 또는 piecewise derivative를 구별한다. H_STEADY의 온도 closure를 물리적으로 유지하려면 그 closure 자체의 jet도 필요하다.

## 3. 최소 검증과 현재 결과의 재사용

독립적으로 M deltaX=deltaa+(deltaG)u+G deltau−(deltaM)X를 푸는 경로와 위 adjoint 식의 deltaF를 비교한다. 선택 모델이 같은 M0,q0를 갖는 경우에만 기존 lambda를 재사용할 수 있다. Coefficient JVP는 원식의 독립 미분 또는 고정 cell 안의 적절한 고정밀 방향 검산으로 확인하고 direction·step/precision·source residual을 보존한다. 기존 아홉 incoming control은 P 방향을 움직이지 않았으므로 이 검증을 대신하지 않는다.

이 단위의 완료 대상은 **pointwise full-P coefficient jet과 그 source binding**이다. 전체 history 적분, coefficient box 전체의 정칙성, 물리적 오차 tube는 완료 항목에 추가하지 않는다.

## 4. 시간 residual·초기오차·물리 L로 이어가기 위한 별도 입력

| 목적 | 아직 필요한 실제 자료·정의 |
|---|---|
| 실제 시간 미분 | 공통 eta로 변환한 P'(eta)와 u'(eta). H/nH의 source-bound background jet, TM/TR의 closure 또는 evolution jet, incoming의 방사 수송·history interpolation jet이 필요하다. Native clock과 geometric query clock의 변환도 보존한다. |
| Whole-cell defect | 연속 재구성 Y_tilde(eta), 그 미분, 같은 state/clock의 coupled F, 전체 구간에서 r=Y_tilde'−F(eta,Y_tilde)의 enclosure. Point scalar parity나 작은 block residual만으로 이 r을 공급하지 않는다. |
| 초기오차 e0 | 대상 물리해의 초기조건, 저장 trajectory 초기값과의 대응, 초기 radiation/history 차이, 같은 state norm에서 그 차이의 상계. 출력을 같은 값으로 초기화했다는 사실만으로 e0=0이라 두지 않는다. |
| 물리적 안정성 L | Electron·thermal·radiation과 필요한 memory/history state를 포함한 F의 state Jacobian, 공통 가중 norm, 양의 후보 tube 전체에서 Lipschitz 또는 logarithmic-norm bound. 이번 point 감도 norm은 그중 한 coupling row의 수치값이다. |
| Model discrepancy와 양성성 | 선택한 recombination/transport/closure/table 모델과 대상 물리 사이의 차이 상계, physical population·occupation으로의 복원 사상. Signed departure 자체에 대한 비음수 clamp는 양성성 조건을 대신하지 않는다. |

이 자료들이 같은 clock·norm·state domain으로 주어진 뒤에, 예를 들어

\[
\|e(\eta)\|\le e^{\int_{\eta_0}^{\eta}L}\,e_0
+\int_{\eta_0}^{\eta}e^{\int_s^{\eta}L}
\bigl(\|r(s)\|+\varepsilon_{\rm model}(s)\bigr)\,ds
\]

를 적용할 수 있다. 시간 의존 가중 norm이면 가중치 미분항도 L에 포함한다. Incoming이 history에 의존하면 필요한 memory state를 포함하는 계, 또는 해당 이력 공간에서의 추정을 먼저 정의한다. 새 point jet의 구현만으로 physical coverage, e0, L, defect, tube를 채우지 않고 기존 null과 QSS03의 별도 의무를 유지한다.

근거: 본 단위 `CONTRACT.md`, `THEORY.md`, `MODEL_COMPARISON_CONTRACT.md`, `reviews/R6_REVIEW.md`, `reviews/R6_PREFIX_REVIEW.md`. 이 문서는 후속 연구의 설계 입력이며 실행을 마친 derivative provider가 아니다.
