# R3N: 원본 predictor와 세 시간 격자 비교의 조건

## 결과와 범위

이 단위는 기존 `R3I-CONVERGENCE-v1`을 실제 비교 코드로 옮긴다. 재사용하는 계약은
`research/rec_r3i_time_refinement_20261016/CONTRACT.json`, SHA256
`308aecdfb9fbe1eac292a5d6cc120ba60966b7988e6df82bd4e337d6598a6fa6`다.
비교기는 `xe=n_e/n_H`와 `Tm_K`의 저장된 Python 상태를 다룬다. 광자 스펙트럼 수렴은
이번 비교기의 판정 대상에 추가하지 않는다. 원본 same-h 625-field 기준은 그대로 남는다.

원본 predictor의 매끄러운 ODE에 대한 국소 결함, 스칼라 음의 실축 안정 구간,
공통 초기값 오차의 Richardson 차이 상쇄를 직접 유도했다. 이것은 전체 HyRec의
비선형·지연 이력·stage 전환을 포함한 수렴 증명이 아니다. 새 strong no-go를 주장하지 않는다.

## 1. 원전과 구현의 대응

Ali-Haïmoud–Hirata, Phys. Rev. D 83, 043513 (2011),
[arXiv:1011.3758v2](https://arxiv.org/abs/1011.3758), Appendix C Eq. (C1)는
같은 간격의 이전 도함수를 쓰는 적분식을 준다. Sec. V D의 Eq. (94)는 주파수 bin 사이의
지연된 광자 입력을 설명한다. 논문의 2011 stage 수치나 cosmology를 2012 source의 값 대신
사용하지 않는다. 이 프로젝트의 원본은 SHA `48cd5975…1d27` ZIP 안의 `history.c`,
`hydrogen.c`, `hyrectools.c`다.

| 식/계약 | 실제 코드 |
|---|---|
| x=ln a, y'=F=dot(y)/H | `primordial_2012_refined_start.py`, `source_thermal_rhs` |
| 현재 F와 F[n-2] memory | `primordial_2012_owned_u6.py::integrate_u6_owned` |
| 지연 광자 두 이웃 보간 | `owned_flrw_history.py::incoming` (이번에 수정하지 않음) |
| 저장 상태의 원본 4점 출력 보간 | `time_convergence.py::cubic_stencil`, `original_cubic` |
| 부호 차이, 오차 바닥, 경계 분류 | `signed_triplet`, `compare_histories` |
| 검토된 R3M 상태와 실제 C 차이 추출 | `scripts/compare_r3n_time_grids.py prepare-r3m` |

Convention은 FLRW q=0, metric(-,+,+,+), a=(1+z)^(-1)다. 이 단위에서 metric을
재정의하거나 c, hbar, kB를 1로 놓지 않는다. ln a와 h는 무차원이고 xe는 수소 원자핵당
전자 수, Tm은 K다. 원자 코드의 eV–K 변환과 물리 상수는 기존 구현을 그대로 사용한다.

## 2. predictor의 국소 결함과 memory

원본은

\[
y_{n+1}=y_n+h\left(\frac54F_n-\frac14F_{n-2}\right),\qquad
F_n=F(x_n,y_n),\quad x_n=x_0+nh.
\]

정확해를 대입해 F(x)=y'(x)라 쓰면

\[
F(x-2h)=F-2hF'+2h^2F''-\frac43h^3F'''+O(h^4).
\]

정확 증분에서 수치 증분을 뺀 **비정규화 국소 결함**은

\[
\delta_n=\frac23h^3y'''(x_n)-\frac7{24}h^4y''''(x_n)+O(h^5).
\]

따라서 매끄러운 해, 적합한 초기 이력, 일관된 RHS와 안정성 조건 아래 O(h^2) 전역 오차를
기대할 수 있다. 국소 Taylor 식만으로 현재의 전체 재결합 이력에 그 조건을 인증하지 않는다.
의도치 않게 F[n-1]을 쓰면 결함은
`h^2*y''/4 + 7*h^3*y'''/24 + O(h^4)`로 바뀌어 일반적으로 1차가 된다.

재시작 시 두 stored RHS에 오류 epsilon[-2], epsilon[-1]이 있으면 첫 두 갱신에 각각
`-h*epsilon[-2]/4`, `-h*epsilon[-1]/4`가 들어간다. 현재 RHS의 상태 의존성과
지연 광자 이력을 통해 이 오류가 이후에도 전파된다. 정확한 현재 xe/Tm 한 쌍만으로는
재시작 상태가 완성되지 않는다. R3M의 검토된 U5 SHA, 두 RHS tail, accepted photon prefix를
하나의 재사용 의존성으로 유지하는 이유다.

## 3. 스칼라 안정성: 조건부 결과

y'=lambda*y, z=lambda*h에 대해 특성다항식은

\[
P(r;z)=r^3-r^2-z(5r^2-1)/4.
\]

z=-q, q>0, r=(1+s)/(1-s)를 대입하고 분모를 곱하면

\[
(2-q)s^3+(4-2q)s^2+(2+2q)s+q.
\]

0<q<2에서는 모든 계수가 양수이며 cubic Routh 조건의 차이는
`(2-q)(4+3q)>0`다. 따라서 모든 r이 단위원 내부다. q=2에서는
`P(r;-2)=(r+1)^2(r-1/2)`여서 -1의 중근이 root condition을 위반한다.
q>2에서는 P(-1;-q)=q-2>0이고 r→-infinity일 때 P<0이므로 r<-1인 근이 있다.
z=0은 `r^2(r-1)`로 1이 단순근이다. 음의 실축에서 root condition을 만족하는 범위는
`-2<lambda*h<=0`이고, 엄격한 감쇠 안정 구간은 `-2<lambda*h<0`다.

이 결과를 원자 Schur solve, photon-history 결합, thermal branch 전체의 Jacobian 안정성으로
확장하지 않는다. 이번에는 그 spectrum을 계산하지 않았다. Wolfram의 정확 대수와
독립 스칼라 근 계산이 위 식을 검산했다.

## 4. Richardson 차이와 공통 편향

동일한 물리적 x에서
`P_h(x)=P(x)+B(x)+A(x)h^p+o(h^p)`라고 가정하면

\[
D_{01}=P_h-P_{h/2},\quad D_{12}=P_{h/2}-P_{h/4},\quad
\log_2|D_{01}/D_{12}|\to p
\]

이다. 그러나 B(x)는 두 차이에서 모두 상쇄된다. 공통으로 부정확한 초기값, 같은 근사식의
편향, 동일한 잘못된 closure는 이 검사로 배제되지 않는다. 또한 h 하나에서 Python=C가
성립해도 A, B, p가 결정되지 않는다.

직접 실행한 작은 반례는 `y'=-200y`다. 원래 목표 `y(0)=1`에 대해 세 격자 모두
`y(0)=1.01` 및 그 초기값에 맞는 정확한 두 과거 도함수로 적분했다. 이 경우
`B(s)=0.01*exp(-200s)`이며, 시간 이산화 오차는 줄어도 이 편향이 남는다.
`probes_004/result.json`에서 가장 미세한 격자의 참값 오차는 약 0.00338인데,
부호 있는 차이의 중앙 차수는 여전히 약 2.0135다. 이것은 실제 U5 checkpoint를
변조한 실행이 아니라 명시적인 manufactured ODE 반례다.

## 5. 두 종류의 보간과 전환 구간

출력 비교는 원본 `hyrectools.c::rec_interp1d`의 네 점을 쓴다. 그리드별
`N=floor(2+ln(8001)/h)`와 `i=min(max(floor((x-x0)/h),1),N-3)`를 사용한다.
부분 이력의 첫/끝을 새 clamp로 삼지 않는다. 필요한 전역 인덱스 네 개가 없으면
`NO_COVERAGE`로 남긴다. 원본 식의 곱셈·덧셈 순서도 유지한다.

가중치는

\[
(w_{-1},w_0,w_1,w_2)=
\left[-f(1-f)(2-f)/6,\ (1+f)(1-f)(2-f)/2,
 (1+f)f(2-f)/2,\ -(1+f)f(1-f)/6\right].
\]

노드별 절대 오차 e_j의 보간 후 상계는 `sum(abs(w_j)*e_j)`다. 음의 가중치로 오차를
서로 상쇄시키면 안 된다. 내부 f∈[0,1]에서 가중치 절대합은 `1+f-f^2<=1.25`다.
끝 clamp 구간까지 1.25를 적용하지 않는다. 예를 들어 f=-1/2에서 가중치는
`(5,15,-5,1)/16`, 절대합은 1.625다. 구현은 매 지점의 실제 절대합을 사용한다.

매끄러운 함수의 4점 출력 보간 잔차는 O(h^4)지만 RHS가 사용하는 광자 두 점 보간의
잔차는 일반적으로 O(h^2)다. 둘을 같은 보간으로 부르거나 4차 적분이라 해석하지 않는다.
고정된 lookback/h의 소수부 변화로 지연 보간 오차의 선도 계수가 격자마다 진동할 수 있다.
따라서 양의 수렴 차수를 모든 지점에서 강제하지 않는다.

stage 전환이 한 격자 칸 내에서 달라지고 양쪽 RHS에 유한한 차이가 있으면,
전환 위치 오차 O(h)가 적분값에 O(h) 항을 만들 수 있다. 두 branch가 더 높은 차수까지
일치하면 이 효과는 작아질 수 있다. 이번 계약은 기존 ±4*hcoarse 전환 이웃과
z=[1553,1573], [826,846] 창을 별도로 보고한다. 경계 근처 p를 보류해도 그곳의
D01/D12와 최대오차는 원래 수치 gate에 포함한다.

## 6. 기존 판정식의 구현

scale은 xe에서 max(abs(P_h4),1e-4), Tm에서 max(abs(P_h4),1K)다. D01과 D12는
부호를 유지한다. 각 차이에 대한 바닥은 원래 계약의 세 항을 사용한다:

`max(32*u*max(abs(a),abs(b),field_floor), 10*(e_a+e_b), 10*(q_a+q_b))`, u=2^-53.

여기서 e는 실제 same-h C/Python 절대 차이를 네 점의 abs(weights)로 전달한 값,
q는 추가 출력 양자화 half-unit의 동일한 전달이다. 계약의 "양쪽 격자 오차"를 삼각부등식의
합으로 구체화했다. 알 수 없는 e/q는 0으로 채우지 않는다. 이것은 측정된 오차를 이용한
판별 바닥이며, 실제 해에 대한 엄밀한 계산 오차 상계를 인증하지 않는다.

두 차이가 모두 바닥보다 크고 부호가 같을 때만 `p_observed`를 낸다. 분류는
`UNCERTAINTY_MISSING`, `STAGE_BOUNDARY`, `BOUNDARY_COVERAGE_UNKNOWN`, `ROUNDOFF_UNRESOLVED`, `NONMONOTONE`,
`RESOLVED_SAME_SIGN`이다. 원래 norm gate는 전역 및 각 regime에서
`||D12/S||inf<=1e-4`, `||D12/S||inf<=0.75||D01/S||inf`, `2||D12/S||inf<=1e-4`다.
마지막 2배 조건은 기존 감도 기준이다. 이번 결과에서 엄밀한 Richardson 오차 상계로
재해석하지 않는다. p≈2나 maxnorm 조건 하나만으로 자동 과학 승인을 만들지 않는다.

경계 목록의 빈 배열은 단독으로 "주변에 경계가 없다"는 근거가 아니다. descriptor의
`provenance.boundary_coverage_lna=[lo,hi]`는 경계 목록이 검토된 좌표 범위를 표시한다.
그 범위가 비교점의 ±4*hcoarse(물리 도메인 안)를 덮지 않으면 p를 보류한다. stage label은
bytes→Unicode 변환과 공백 제거 뒤 빈 값을 거절한다. inclusive 경계 창은 좌표 계산의
product/addition 반올림을 포함하도록 좌표 구성 항의 크기에 근거한 여유를 둔다.
\(\gamma_3=3u/(1-3u)\)일 때 그 여유는
\(2\gamma_3(|x_0|+|x-x_0|+4h)\)이며 마지막 연산은 outward nextafter로 감싼다.
최종 좌표의 두 ulp만 쓰는 이전 시도는 ln(a)≈0의 상쇄 때문에 부족했고, index 100015
반례를 독립 검토에서 확인해 수정했다. 이 보수적 mask는 원본 격자·보간·적분값을
바꾸지 않는다. clamp stencil과 미확인 경계 범위도 따로 보고한다.

## 7. 실제 입력이 지지하는 것

검토된 R3M full U6에서 5211개 상태와 해당 원본 C 상태 차이를 추출했다. 전역 인덱스는
53179…58389, z는 약 836.041…669.959다. 내부 receipt, NPZ, C stdout SHA를 모두
검사한 상태 추출이며 새로운 시간 적분은 0회다. 이 한 격자를 비교기에 넣으면
`INSUFFICIENT_LEVELS`, 빠진 level [0,2], global_coverage=false가 나온다.
이미 존재하는 원본 h 노드들은 다음 입력 연결에서 identity가 맞으면 재사용한다.
이번 선택 입력 묶음에 h/h4가 없다는 사실을 프로젝트 전체 h 실행의 부재로 확대하지 않는다.

실제 h4 독립 시작 및 후속 grid별 checkpoint/전체 이력과 h2의 낮은 z 후속 노드가
준비되어야 기존 z8000…0 계약을 닫을 수 있다. h2 U6가 끝난 상태를 h4 초기값으로
재보간하는 방식은 이 계약에 해당하지 않는다. U5 원본 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`,
과거 비용 `CLOSED_HOLD_NOT_RESET`, REI=false는 모두 유지된다.
