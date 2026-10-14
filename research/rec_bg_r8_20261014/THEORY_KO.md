# REC-BG-R8: 양의 clock 증분 이론의 판정과 실제 AXBI accepted-step 오류 분리

2026-10-14, Asia/Seoul. 선택 단계 `R8`만 수행. 기준은 `REC_BG_INCREMENT_R7B_20261014/NEXT_LOOP.json`의 다음 미완료 이론 단계. 초기 비틸트 축대칭 Bianchi I, metric signature \((- + + +)\), 정상계 proper seconds \(t\). 이론의 배경은 고정된 \(a\in[1/21,1/5]\) 및 \(H^2=\sum_{p\in\{0,3,4,6\}}C_pe^{-pL}\), \(C_p\ge0\), \(L=\ln(a/a_r)\)이다. \(c,\hbar,k_B\)는 필요한 식에서 유지한다. 주된 산출물은 **이론 후보의 유효한 범위 판정**, **실제 저장 accepted-step의 상대 clock 오류 진단**, **생산 변경 전에 필요한 최소 실행 계약**이다. 새로운 native chemistry/Boltzmann solver 실행은 0회다.

## 결론과 게이트 상태

* **DERIVED/SCOPED_ACCEPT:** R7B의 positive-rate Hermite interpolation theorem(이상적 endpoint 값 및 slope)은 정해진 양의 지수 계수 family에서 유효하다. 구간이 짧아져도 상대 적분오차가 구간 길이의 역수로 증가하지 않는다. 양의 \(F=1/H\) 및 고정 부호 \(sF\)를 동일한 다항식에서 적분한다.
* **NUMERICALLY_CHECKED:** 종료된 세 실제 이력의 선택된 accepted step 102개에서 24개는 기존의 \(10^{-8}\) local short-interval 비교 기준을 초과했다. 가장 큰 상대차는 약 \(-1.81900864\times10^{-8}\). 가장 문제가 된 near-origin 차이를 기존 두 개의 \(\log(a/a_r)\)를 따로 평가해 빼는 계산으로 거의 전부 재현했다.
* **REI OWNER HOLD RETAINED:** 기존 실행 이력의 물리적 오류가 입증되었다는 의미는 아니다. 상대 clock 간격 오차는 이론·수치 관련 defect이지만, 실제 gas/photons/ledgers/convergence 영향은 측정하지 않았다. 별도 Codex의 signed 실행, baseline, source/IC 변형을 중단하거나 수정하지 않는다.
* **NEXT ACTION:** production short interval을 바꿀 권한이 별도로 발급되면 이미 구현된 `BACKGROUND_TABLE_001`의 **stable polynomial difference**를 우선 시험한다. R7B의 positive-rate Hermite는 독립적 대안이며 이상적 균일 bound가 있으나 새 source/method identity와 실제 node/roundoff 진단이 필요하다. `BACKGROUND_EXACT_CACHE_001`의 bit-preserving cache에는 interval method 변경을 섞지 않는다.

## 1. 실제 SOURCE/SSOT와 새 관측의 provenance

REI PR117의 2026-10-14 21:53:36 KST 게시 HEAD는 `45f166adee36d57cabe712ff66209926d1aa1556`였다. 별도 Codex 최신 STATE에서 AX07 ZERO 전체 z20→4는 조건부 scoped PASS, AX08 signed family는 진행 중, AX11/AX12는 PENDING이며 연구 전체 admission은 미발급이었다. 새로운 온도별 atomic rate table은 standalone NCP component에서 scoped PASS와 중위 wall ratio 약2.1525(rate)/1.3591(point)를 기록했으나 생산 전환·전체 driver speedup을 주장하지 않는다. BASS_HE의 다른 R8에서는 reducer source-pair와 exact knot-union 결합을 이미 구현하고 9개 synthetic test 및 electron-floor regression을 통과했다. 이 일을 반복 구현하지 않았다.

R7B의 원 background source SHA256 `65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254`와 본문 식 BI-03…BI-11을 그대로 두었다. `R7B` 804개 sample, 21 unit tests, xAct 3개 zero를 재실행하지 않았다.

새 진단은 **이미 종료된 원본**에서만 수행했다. ZERO canonical composed z20→4: 312238 rows, SHA256 `4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f`. 원본 PLUS/MINUS: 각각200001 rows, SHA256 `1f29ed5dd6a7cc0588eceb9cc8748a3f3ab78e94c482f3758fd585f8910c1587` / `1bf53b7b8e2477e3288f42591efd682ea77b96a7b1628904909ea57860ab36a6`. Read-only streaming으로 SHA256과 size/mtime before/after를 검사했으며, 기존 실행 파일/프로세스는 변경하지 않았다.

선택 규칙은 `code/audit_saved_steps.py`가 기록한다. ZERO에서40개, PLUS/MINUS에서 각각31개, 총102개 saved accepted neighbor를 선택하였다. Source constants는 원 Rust `h0_per_s = 67.4*1e5/3.0856775814913673e24`, \(\Omega_m=.315, \Omega_r=9.2\times10^{-5}, \Omega_\Lambda=1-\Omega_m-\Omega_r\), \(s=qH_F(a_r)(a_r/a)^3\)이다. Binary64 literal/CSV values는 실제 값으로 해석하여 mpmath60 자리의 독립 local \(\int d\ln a/H\)를 계산했다. 이 비교는 directed interval certificate가 아니다. 원시102-row CSV, log-cancellation diagnostic, source-identities, xAct stdout는 별도 private Dropbox `REC_BG_R8_NATIVE_STEP_EVIDENCE_20261014.zip`에 보존했다.

## 2. 관측된 구간 오류와 직접 원인 판별

다음은 실제 accepted step #100, PLUS q=+0.01에서의 원 저장값이다.

\[
 a_1=0.04761905043465769,\quad
 a_2=0.04761905047098814,\qquad
 \Delta L\simeq7.6293945783848863\times10^{-10}.
\]

\[
 \begin{split}
 \Delta t_{\rm saved}&=6\,446\,090.361918509\;\mathrm s,\\
 \Delta t_{\rm exact\ dyadic\ model}&=6\,446\,090.4791734519898088\ldots\;\mathrm s,\\
 r_{\Delta t}&=-1.8190086434893404\times10^{-8},\\
 \Delta t_{\rm ref}-\Delta t_{\rm saved}&=0.1172549429898\ldots\;\mathrm s.
 \end{split} \tag{R8-N01}
\]

Native `point_at_scale`는 각 a에서 `span=(a/a_ref).ln()`를 독립 평가하고, `clock=Simpson(0,span)[F]`를 계산한다. 짧은 실제 step에 대해서는

\[
 r_L=\frac{\mathrm{fl}(\log(a_2/a_r))-\mathrm{fl}(\log(a_1/a_r))}
 {\log1p((a_2-a_1)/a_1)}-1
 =-1.8189893480347052\times10^{-8}.\tag{R8-N02}
\]

관측된 \(r_{\Delta t}-r_L=-1.92954546\times10^{-13}\). 세 case의102 sample에서 24개가 \(|r_{\Delta t}|>10^{-8}\)였고, 모두 각 case의 초기 인접 구간에 있었다. 그24개에 대해 \(|r_{\Delta t}-r_L|\)의 최대가 \(1.93\times10^{-13}\)였다. 즉 부동소수점 중간 `log(a/a_ref)` 두 수의 차가 실제 오류를 지배한다는 것을 강하게 지지한다. 단일 관측을 전체 grid의 supremum이라고 하지 않는다. 작은 오류가 역사적으로 승인된 결과의 물리적 차이를 유발했는지 별도 비교 없이 주장하지 않는다.

이 오류는 **signed q를 뒤집어도 동일한 even clock 구조**에서 나온다. 물리적 \(q^3\) scalar response와 혼동하지 않는다. `log1p((a_2-a_1)/a_1)`로 실제 구간 폭을 형성하는 것은 source convention을 바꾸는 것이 아니라 같은 supplied binary64 endpoints의 올바른 독립 증분을 구하는 것이다. 그러나 생성된 \(\Delta t\)가 gas·photon 계산에 들어가므로 생산 교체는 numerical-method identity 변화다. Exact memoization과 같은 bit-preserving 최적화가 아니다.

## 3. 조건부 전구간 clock 오차: positive increments와 누적 반올림

R7B의 계산된 이상적 uniform Hermite bound를 \(\varepsilon_h\)라 하자. 정확한 노드 \(F_i,F_i'\)에 대해서

\[
 |P-F|\le \varepsilon_h F,
 \qquad \varepsilon_h=\frac{30537}{384}e^{3h}h^4.\tag{R8-E01}
\]

노드 함수값 절대오차가 \(e_F\), \(L\) 미분의 오차가 \(e_{F'}\) 이하이면 두 endpoint data의 Hermite basis에서

\[
 |\widetilde P-P|\le e_F+\frac{h}{4}e_{F'},\qquad
 \varepsilon_{\rm nodal}\le\frac{e_F+h e_{F'}/4}{\min_I F}.\tag{R8-E02}
\]

여기서 \(H_{00},H_{01}\)은 비음수이고 합이1, \(|H_{10}|+|H_{11}|=u(1-u)\le1/4\)다. 반대로 노드 오차나 local integral의 floating evaluation 오차를 0이라 가정하면 안 된다. 계산된 양의 각 증분 \(\widehat d_i\)가 참 증분 \(d_i>0\)와 \(|\widehat d_i/d_i-1|\le\eta\)를 만족한다고 **조건부로** 가정하자. N개 양의 증분을 표준 binary64 순차 합산한다면 unit roundoff \(u=2^{-53}\)와 \(\gamma_{N-1}=(N-1)u/[1-(N-1)u]\)에 대해

\[
 \boxed{\frac{|\widehat t_N-t_N|}{t_N}
 \le\eta+(1+\eta)\gamma_{N-1}}.\tag{R8-E03}
\]

양의 합이므로 오차를 각 구간의 길이로 나누거나 무조건 N을 곱할 필요는 없다. 이 식은 interval errors의 부호와 상관없이 성립하나, **계산된 \(d_i\)의 상대상계 \(\eta\) 자체가 확립되었을 때만** 실제 수치 certificate가 된다. `N=312237`은 현재 ZERO 이력의 accepted-step 수이지 새 table solver가 실행한 횟수가 아니다.

| 표본 격자 | 이상적 \(\varepsilon_h\) | node/적분 평가 오차를 0으로 가정한 조건부 전구간 상대상계 | 저장된 ZERO 끝시각을 곱한 조건부 절대 크기 |
|---|---:|---:|---:|
|1024|\(3.08073094\times10^{-10}\)|\(3.42738254\times10^{-10}\)|\(1.46674464\times10^7\,\rm s\), 약0.465년|
|2048|\(1.92140062\times10^{-11}\)|\(5.38791659\times10^{-11}\)|\(2.30575305\times10^6\,\rm s\), 약26.7일|

사용한 저장된 ZERO 끝시각은 \(t_{\rm end}=42\,794\,891\,441\,558\,000\,\rm s\)이며, cosmic absolute age가 아니라 z20부터 경과한 proper seconds다. 이 수치는 실제 history time이고 위의 **조건부 오차값은 새 solver의 실제 오류를 측정한 값이 아니다.** 작은 기하 clock 상대오차가 곧 동일한 abundance/visibility 상대오차라는 주장도 아니다. Wolfram15.0.1에서 basis residual0, slope weight1/4, 공식과 \(\gamma_N\)의 exact-real 산술을 대조했다. Cloud test는 보수적 \(\gamma_N\), portable code는 적절한 \(\gamma_{N-1}\)을 사용해 한 번의 불필요한 roundoff를 제외했다.

## 4. 별도 chemistry와 optical readout: 어떤 오차는 아직 닫히지 않았다

동일 scale factor와 초기 nuclear inventory의 바리온 보존 \(\nabla_a(n_H U^a)=0\)에서는 \(n_H(a)=n_{H,r}(a_r/a)^3\). 이는 같은 \(a\)에서 background clock의 재매개화만으로 바리온 희석 law가 변하지 않는다는 뜻이다. **전자 fraction은 외부 ionization source로 진화하므로 이 관계만으로 고정되지 않는다.**

\[
 \tau=\sigma_T c\int n_H(L)x_e(L) F(L)\,dL
 \qquad(F=dt/dL>0).\tag{R8-P01}
\]

고정된 \(n_H(a)\)에서 \(F\mapsto F+\delta F, x_e\mapsto x_e+\delta x_e\)이면

\[
 \boxed{\delta(n_H F x_e)=n_H(F\delta x_e+x_e\delta F+\delta F\,\delta x_e)}.\tag{R8-P02}
\]

따라서 \(|\delta F|\le\eta F\)일 때

\[
 |\delta\tau|\le \sigma_Tc\int n_HF\left[(1+\eta)|\delta x_e|+\eta|x_e|\right]dL.\tag{R8-P03}
\]

\(\delta x_e=0\)로 **고정한 readout 시험에서만** \(|\delta\tau|\le\eta\tau\)다. 실제 결합 기체·광자 source가 달라질 때는 \(\delta x_e\) 또는 해당 tangent/Jacobian/empirical-refinement 오차가 필요하다. \(\tau\)의 전체 observer-tail과 지난 reionization history는 이번 식으로 입증하지 않았다.

실제 local Wolfram15.0.0+xTensor1.3.0에서 4D \((-+++)\) 부호로 baryon-current product, electron-fraction current product, optical integrand의 두 인자 perturbation의 세 residual이 **정확히0**이었다. 이 검산은 대수적 product rule이며 실제 source closure/Einstein/transport를 독립적으로 해결한 것이 아니다. xCoba는 사용하지 않았다.

## 5. R8 채택 결정과 다음 행동

1. **기존 배경 table의 stable primitive 우선**: `BACKGROUND_TABLE_001`에서 이미 `log1p` interval과 factored polynomial increment가 component 검사를 통과했다. 동일한 단계·출력 계약을 그대로 두고 다른 numerical identity로 bounded native-step overlap를 시험하는 방법이 가장 작은 변경이다. `point_at_scale(a2).time-point_at_scale(a1).time`가 actual tentative의 모든 호출에서 제거됐는지 검사해야 한다. 기하 \(\Delta b\)도 같은 사건·같은 background family에서 계산한다.
2. **R7B positive-rate F-Hermite는 독립 대안**: 이상적 균일상계 및 양성은 더 나은 수학적 제어를 제공한다. 하지만 노드/roundoff·새 method identity와 production performance를 별도로 검사한다. 무조건 기존 table을 교체하는 최종 선택은 하지 않는다.
3. **Exact cache는 다른 lane**: 연속 두 시각의 잘못된 뺄셈 bits까지 보존하는 bit-identical cache는 속도 최적화이지 clock correction이 아니다. 동시 진행 중인 cache-only 계약을 혼합 수정하지 않는다.
4. **REI AX08 live owner와 AX11/12**: 현재 실행 중인 original signed case를 중단하거나 재시작하지 않는다. 이번 결과는 새 run을 발행하는 허가가 아니라 이미 관측된 문제의 원인·새 method 비교 계약 준비다. AX11/12 result가 `PENDING`인 이유를 이 packet 출판으로 없애지 않는다.

실행 가능한 최소 변화 테스트는 (a) 본102개 실제 native step 중 같은 supplied-a endpoint의 \(\Delta t\) gate `1e-9`를 source-compatible local quadrature에 대조, (b) 초기/후기 실제 saved step의 gas/photons/ledgers 및 geometry 사상 overlap와 refinement 평가, (c) 실패 case를 포함한 source hash/config/checkpoint 보존, (d) 새 code identity, new output namespace, 독립 변경면 검토다. 새 table을 원래 checkpoint와 같은 executable이라고 속이거나, `HOLD_SHORT_STEP_SUBTRACTION`을 문서상으로만 PASS 처리하면 안 된다. Numerical relative discrepancy \(1e-8\)는 물리적 abundance 검출한계 또는 전 시간구간 오차가 아니다.

### 현재 claim 상태

- **THEORY_ACCEPT_SCOPED**: 양의 지수 배경의 Hermite bound와 two-factor optical perturbation identity.
- **NUMERICALLY_CHECKED**: 기존 accepted 102개 sample, 24개 gate 초과, near-origin log-cancellation source diagnosis, Wolfram/xAct algebra, 12 Python tests.
- **READY_FOR_OWNER_FINITE_CONTRACT**: `REC_R8_NATIVE_CLOCK_DIAGNOSTIC_INGEST`, `REC_R8_FINITE_INCREMENT_CONTRACT_INPUT`.
- **HOLD_PRODUCTION_NATIVE_ADOPTION**: 결합 solver 수정 및 new-method test 미실행.
- **UNRESOLVED**: 실제 gas history 오류·5case signed response·AX11 refinement/source IC uncertainty·full observer optical readout.
- **R9/R10**: 이번 호출에서는 실행하거나 완료 처리하지 않는다.

## 문헌·근거

- D. Goldberg, *What Every Computer Scientist Should Know About Floating-Point Arithmetic*, 1991. Source: https://docs.oracle.com/cd/E19957-01/816-2464/ncg_goldberg.html . Cancellation 및 이전 오차 증폭 일반 원리의 출처.
- N. J. Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002, 특히 양의 sum과 \(\gamma_n\) 형태의 통상적 floating-point 반올림 분석. https://doi.org/10.1137/1.9780898718027 . 여기서 실제 bound와 case 숫자는 별도로 유도·검산한 것.
- R. L. Dougherty, A. S. Edelman, J. M. Hyman, *Nonnegativity-, monotonicity-, or convexity-preserving cubic and quintic Hermite interpolation*, Math. Comp. 52 (1989), 471–494. https://www.ams.org/journals/mcom/1989-52-186/S0025-5718-1989-0962209-1/ . Positivity-preserving Hermite 문헌 맥락이며 현재 exponential-mixture 특정 bound는 우리 직접 유도.
- P. Fleury, C. Pitrou, J.-P. Uzan, *Light propagation in a homogeneous and anisotropic universe*, PRD 91 043511 (2015), https://arxiv.org/abs/1410.8473 . 기존 finite Bianchi I photon map의 출처.
- D. Viswanath, *Global errors of numerical ODE solvers and Lyapunov's theory of stability*, IMA J. Numer. Anal. 21 (2001), 387–406, https://doi.org/10.1093/imanum/21.1.387 . Local clock coefficient precision alone에서 global nonlinear IVP error가 곧장 나오지 않는다는 일반 맥락.

모든 인용은 알려진 문헌 방법/맥락과 이번에 직접 유도한 결과를 구분한다. 이 결과의 문헌 최초성은 검증하지 않았으며 독립 출판 심사도 수행하지 않았다.
