# LINE01 — 선 방출원의 에너지 장부와 정확한 국소 thick 갱신

작성일: 2026-10-23, Asia/Seoul. 게시: [REC PR128](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/128).
직전 기준은 REC PR127 `5185c396b7e07076565ca2f5044a5ccd193e6ee1`이다.
최종 게시 pin·파일 동일성·백업 확인 범위는 delivery 영수증과 PR128 최신 반환을 따른다.

## 결과와 이번에 닫은 범위

**조건을 명시한 하나의 bound–bound source에서 population, 광자 수,
원자 내부에너지, 복사 에너지와 각도 텐서 주입을 연결했다.** 기존 ANGULAR01의
탈출확률 모멘트 B,Q와 REC114의 실제 Einstein source class를 재사용했다.
고정 배경의 광학적으로 두꺼운 국소 source 단계는 Lambert W의 주가지로 풀리며,
실제 구현에서는 동치인 단조 대수근 하나를 계산한다. 이 부분에 시간 적분 IVP가
필요하지 않다. 전체 경로의 최소 광학깊이로 유한-opacity 해와의 차이도 제한했다.

새 source36, 검증용 local map27, 직접 source 비교6, finite-opacity 기준근2,
그림용 analytic map243개를 완료했다. 첫 attempt의 성공source36/map25는 그대로
보존·재사용했다. 뒤이은 끝점 반올림 수리로 누락map2와 아직 실행하지 않은 후속
블록만 생성했다. 최종 수치 판정은 **PASS_AFTER_TARGETED_ROUNDING_REPAIR**,
총704개 수용 check 중 실패0이다. 704는 기존616의 재사용과 새88의 합이다.
독립 검토는 한 번의 pass에서 PASS_AFTER_TARGETED_REPAIR로 종료했고 열린 지적0이다.
최종 전달의 정확한 상태는 delivery 영수증과 DAG에 있다.

이 결과는 detached effective line의 조건부 폐쇄다. 저장된 native scalar 상태와
별도로 공급한 shear를 사용했고, cosmological history·native runtime·local IVP를
새로 실행하지 않았다. 이론식이 정확하다는 것은 선택한 모형 안에서의 진술이다.
원자자료, 유효선 근사, Sobolev 가정 및 이후의 물리적 결합 오차는 따로 남는다.

## 1. 최신 반환·원전·기존 코드의 결합

REC119/REI220의 최신 반환은 ANGULAR01 완료와 다음 source-owned line 단위를
가리켰다. 이번에는 과거407 branch/347 PR 목록을 다시 생성하지 않고, 갱신된
관련 PR과 고정 source 경로의 delta를 확인했다. 관련 HEAD는 유지됐다.
과거 대화 전체나 접근되지 않은 저장소를 이번에 전수 열람했다고 표현하지 않는다.

실제 재사용 대상은 다음과 같다.

| 근거 | 재사용한 내용 | 정확한 한계 |
|---|---|---|
| REC127 ANGULAR01 | finite B,Q, thick gate, tensor 규약 | prior405-grid 재실행0; Q는 확률 모멘트 |
| REC114 `df95a074...` | `IsotropicEinsteinLineSource`, population 복원 경로 | 원본 class AST를 그대로 호출; native 전체 전달계 실행0 |
| 동일 pin의 native saved CSV | z=1099.9986525171403의 population/H/nH/TR/Dfplus | 완전한 실제 scalar input1개; angular field는 저장되지 않음 |
| NIST H I persistent table | 두 fine-component A와 wavelength, J | 표에 수치 불확도가 제시되지 않음 |
| Hirata–Forbes §II.B 식1–3 | stimulated source, blue-side occupation, Sobolev opacity | Bianchi tensor 및 exact local map은 이번 직접 유도 |
| Wolfram context1/evaluator2 | source·phase-space·평형·W0 미분 잔차 확인 | 도구의 feasibility/precision 경고 원문 보존; interval proof로 승격하지 않음 |

Exa와 SciSpace는 실제 원전 탐색에 사용했고, 최종 물리식은 primary source에
고정했다. NIST의 전체 n=2 shell 표(g_u=8,A=4.699e8)는 2s를 포함하므로
collapsed2p population에 넣지 않는다. 원본 native A2p_up/down 역시 spontaneous
A21가 아니라 virtual-bin diffusion 계수다.

Primary sources:
[NIST persistent lines](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3.htm),
[NIST shell convention](https://physics.nist.gov/Pubs/AtSpec/node18.html),
[Hirata–Forbes](https://arxiv.org/pdf/0903.4925),
[Chluba–Sunyaev](https://arxiv.org/pdf/0810.1045).
원전 위치·반환형식·제한은 provenance/LINE_SOURCES.json에 있다.

## 2. Population과 source 계약

Native `xr[1]`은 x2p 그 자체가 아니다. 저장 departure에서

\[
x_{2p}=x_{r,2p}+3x_{1s}\exp(-E_{21}/T_R)
\]

로 복원한다. 여기의 E21,TR은 native eV 단위이며 E21=10.198714553953742 eV다.
청색 경계의 total occupation은 이번 detached 모형에서

\[
f_+=\frac1{\operatorname{expm1}(E_{21}/T_R)}+Df^+_{\rm Ly\alpha}
\]

로 명시했다. `Dfplus`는 distortion이고 full occupation이 아니다.
Native의 Wien population 복원은 full Planck detailed balance와 양립한다.
다만 native compressed departure 식과 이번 full stimulated standalone source가
완전히 같은 runtime이라는 주장은 하지 않는다.

실제 저장 population은 collapsed2p이므로 primary card는 g=3의 **유효 coincident
line**으로 고정했다. 두 fine population의1:2 분배, 같은 profile/frequency/f_plus를
가정하고 Aeff=(A1/2+2A3/2)/3를 쓴다. E는 native 값을 유지하고 λ=hc/E로 일관되게
변환한다. 별도 NIST fine cards는 각각 g=1,2와 자신의 λ,A를 유지한다. 이 집계는
실제 overlap doublet 전달과의 등가성을 증명한 것이 아니다.

N=n_l+n_u는 **이번 두 준위 pool**이다. Native 전체 수소핵 밀도 n_H와 구분한다.
물질 정지계·물리 부피·SI 단위를 사용하고 c,h=2πℏ,k_B를 식에서 유지한다.

## 3. 에너지와 ionic ledger

\[
\Delta=g n_l-n_u>0,\quad
D=n_u(1+f_+)-g n_l f_+,
\quad t=\frac{A\lambda^3\Delta}{8\pi H}.
\]

S=σ/H, q(n)=1+S_nn>0에서 기존 kernel의

\[
B=\langle\beta(t/q)\rangle,\quad
Q_{ij}=\langle(n_i n_j-\delta_{ij}/3)\beta(t/q)\rangle
\]

를 사용하면

\[
R=ADB,\qquad \dot\pi^{\rm inj}_{\gamma,ij}=EADQ_{ij},\qquad
E=h\nu=\frac{2\pi\hbar c}{\lambda}.
\]

R은 signed net rate다. 흡수에서는 음수가 된다. Gross down/up 채널은 각각
AB n_u(1+f_+), ABg n_l f_+로 비음수이며, 이를 net과 별도 보존한다.
Photon phase-space crossing에서 같은 ADβ/(4π)를 직접 얻어8π 정규화도 확인했다.

| 장부 | 해당 선의 변화율 |
|---|---|
| upper/lower | -R, +R |
| 광자 수 | +R |
| 원자 내부에너지 | -ER |
| 복사 에너지 | +ER |
| kinetic thermal energy | 0, recoil-free narrow-line 가정 |
| 이온/자유전자 yield | 0, bound–bound 과정의 상태 변화 |

열 항과 ionic yield의0은 이 선에 대한 물리적 결론이다. Li 최종 charge/state yield,
핵반응 daughter·electron·neutrino·recoil·stopping 문제의 답으로 대체하지 않는다.
finite source36개는 B,Q의 quadrature reference 경로로 평가했다. Exact thick map의
270개 출력은 해석적인 angular shape를 사용한다.
PSTF 결과는 복사응력의 **주입률 또는 적분 packet**이며 실제 저장 radiation stress나
matter stress에 동일시하지 않는다.

## 4. 물리에 따른 계산 단순화

Thick 한계에서 B0=1/t, Q0=2S/(15t)이므로 R0의 bare A가 정확히 소거된다.
고정 N,H,S,f_+의 source substep에서

\[
b=g+1,\quad F=1+b f_+,\quad
x_{\rm eq}=g f_+/F,\quad d_0=g/F,\quad y=x-x_{\rm eq},
\]
\[
a=\frac{8\pi H F}{N\lambda^3},\qquad
\dot y=-\frac{a y}{d_0-b y}
\]

를 얻는다. Population에 따른 opacity 변화는 이 식에 남아 있다.
z0=-b y0/d0>-1, ω=aΔt/d0라 두면

\[
y_1=-\frac{d_0}{b}W_0[z_0\exp(z_0-\omega)].
\]

수치 구현은 u=log|y1/y0|의 유일한 근

\[
u+z_0\operatorname{expm1}(u)+\omega=0
\]

를 사용한다. 도함수가 양수이고 유한 bracket이 알려져 있다. 큰 exp와 작은
endpoint 차감 대신

\[
\Delta n_\gamma=-N y_0\operatorname{expm1}(u),\quad
\Delta u_\gamma=E\Delta n_\gamma,\quad
\Delta\pi_\gamma=E\Delta n_\gamma\,2S/15
\]

를 계산한다. 이 방법은 국소 source 문제의 시간 적분을 하나의 대수근으로 줄인다.
새 global history의 성능 향상을 측정한 것은 아니며, cosmological dilution과
경계 occupation의 시간 변화는 이 고정 배경 substep 밖에 있다.

### 전체 경로의 유한 오차

초기값과 평형 사이에서 최소 opacity를 구한다.

\[
T_{\rm path}=\frac{A\lambda^3N[g-b\max(x_0,x_{\rm eq})]}{8\pi Hq_{\max}},
\qquad \delta=e^{-T_{\rm path}}.
\]

Tpath≥log1p(1/1e-8)를 요구하면 모든 중간 상태에서 B/B0∈[1−δ,1]이다.
따라서 실제 finite-opacity local 해는 thick 해 Φt와 Φ(1−δ)t 사이에 있다.
두 값의 폭 w는 population 절대오차, ENw는 에너지오차를 제한한다.
K=2S/15로 쓰면 tensor packet에는 별도의 상한

\[
\|\Delta\pi_f-\Delta\pi_0\|_F
\le EN\left[\|K\|_F w+|x_0-\Phi_t|\frac{\delta}{1-\delta}
\left(\sqrt{2/3}+\|K\|_F\right)\right]
\]

이 성립한다. 이는 선언한 모형 안의 truncation 경계다. Float 계산 자체를 interval
certificate로 표현하지 않는다. 매우 큰 optical depth의 exp underflow는 logδ를
보존하며, 출력0을 정확한 물리오차0으로 바꾸지 않는다.

## 5. 실제 저장 상태에서 얻은 값

저장된 z≈1100 상태에 S=diag(-0.4,0.1,0.3)를 **새 fixture로 공급**한 결과다.

| 양 | 값 |
|---|---:|
| n_l [m^-3] | 2.1392718888977095e8 |
| n_u [m^-3] | 4.936450092318387e-6 |
| f_plus | 7.672046131261377e-15 |
| τ0 | 5.783539371373901e8 |
| B | 1.7290450289827392e-9 |
| net R [m^-3 s^-1] | 1.3726869299191238e-8 |
| 복사 에너지 주입률 [J m^-3 s^-1] | 2.2429899569436661e-26 |
| η [s^-1] | 1.0832178932405694 |
| ω=1의 국소 Δt [s] | 0.923175296715591 |
| 해당 Δn_gamma [m^-3] | 8.010425553821858e-9 |
| 해당 Δu_gamma [J m^-3] | 1.3089149227293898e-26 |
| logδ_path | -444887643.9518387 |

동일 상태의 등방·triaxial·회전 fixture에서 이 매우 두꺼운 scalar rate는 같고,
텐서 주입은 shear 방향을 따른다. 이 수치의 유효 자릿수는 코드 검증을 위한 것이며
원자자료나 근사 모형의 물리적 정확도와 같지 않다. Native scalar state의 실제
anisotropic 환경을 측정하거나 복원한 결과도 아니다.

## 6. 유한 검증, 원래 실패 및 그림

| 검사 묶음 | 수량 / 관측 결과 |
|---|---|
| source matrix | 36, 부호·gross positivity·number/energy/ionic ledger 통과 |
| local map +90자리 W0 기준 | 27, 최대 endpoint 절대오차3.34e-17 |
| 원본 Einstein class/phase-space/full-sphere | 6; phase/gross 최대6.52e-16, B 상대차2.11e-15, Q_F/B 차7.37e-14 |
| finite-opacity separable root | 2; 두 endpoint 모두 증명한 bracket 안, integral residual5.55e-17 |
| 잘못된 입력의 명시적 거부 | 18, 물리 행과 별도 집계 |
| 그림용 새 analytic map | 3×81=243, 별도 local output |
| 독립 off-grid review | 6/6 PASS: 새 source1, map3, 거부2; production 재실행0 |

처음 attempt001은 native ω=1에서 중단됐다. z0=-7.898205430874699e-17이고
수학적 두 bracket 끝점이 binary64의-1로 합쳐져 residual 부호 검사에 실패했다.
원래 코드/runner, FAIL traceback, source36/map25 및616 PASS check를 보존했다.
`nextafter`로 아래/위 끝점을 각각 한 ULP 바깥으로 넓힌4줄 수리는 식·가정·수용
허용오차를 바꾸지 않는다. Failed ω=1은 한 번 재시도했고 ω=5는 처음 계산했다.
완료된 source/map prefix는 재계산하지 않았다.

계산 기록의 wall time은 첫 attempt0.413s, continuation9.602s다. 이는 이 유한
실행의 기록이며 기존 solver 대비 speedup benchmark가 아니다. Cosmological IVP,
local IVP, native runtime 및 완료 campaign 재실행은 모두0이다.

그림은 각각 population의 평형 접근, signed escaping photon packet, 서로 반대인
복사/원자 내부에너지, PSTF tensor packet의 네 패널을 담는다. Constructed 방출과
흡수는 f_plus=0.1의 검증 fixture이며 native 그림만 실제 저장 scalar 입력을 쓴다.

- [실제 저장 상태의 국소 source 갱신](figures/line01_native_saved_state.png)
- [구성한 방출 예제](figures/line01_emission.png)
- [구성한 흡수 예제](figures/line01_absorption.png)

각각 PNG/PDF와 원자료 CSV를 제공하며 PLOT_MANIFEST가 SHA256을 연결한다.
Root는3개PNG를 실제로 열어 축·단위·부호·caption을 확인했다. PDF는 같은 Matplotlib
figure에서 저장했다. 별도 PDF raster readback을 수행한 것으로 표현하지 않는다.

## 7. 전체 목표와 다음 leaf

이번 LINE_MAP은 detached effective line의 범위에서 닫는다. 다음 LINE_NATIVE_OWNER는
현재 열려 있다. 한 저장 상태에서 native Lyα real diagonal·feedback·diffusion·Tvv의
소유권을 분해하고, 어떤 항을 독점적으로 넘길지 source 계약을 먼저 고정해야 한다.
그 뒤 residual/JVP와 number/energy ledger를 같은 기준으로 연결한다. 현재 native
항을 유지하면서 이번 source를 더하는 방식은 API에서 거부한다.

Li final charge/state/energy-resolved ionic yield는 MISSING_EXACT_INPUT이다.
Actual-field spectral backreaction과 핵반응 daughter/electron/neutrino/recoil/stopping
입력도 열려 있다. 따라서 전체 self-consistent atomic/spectral/thermal/metric 결합,
global convergence 및 production 승인으로 넘어간 상태가 아니다.

Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET,
global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false 유지.
REC119의125main+1control=126, REI220의127main+2oracle=129, warm729,
THERM02의별도8IVP와 이번 표본 수를 합산하지 않는다. 첫 실패 REI raw의
historical local-only 보존 범위도 유지한다. 모든 핵종의 완전한 핵망이나 완전한
열역학/Bianchi 재결합 폐쇄가 완료됐다고 표현하지 않는다.
