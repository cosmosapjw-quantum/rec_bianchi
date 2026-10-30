# HD 15준위 비LTE 정상상태: Neufeld(2026) 원본과 CDMS(2011) source-qualified benchmark

**선택 범위:** REC_HD_NEUFELD2026_V2_SOURCE_BENCHMARK_20261030. 이전 PR #168(`d2b1592f1b3f02e7db721fb89b57e19868532f07`)을 변경하지 않는 독립 연구 브랜치. 2026 Neufeld 물리모델의 정식 재현 및 2021 Flower 입력과 구별하는 비교. 2011 CDMS 생산소스 전환은 금지한다.

## 정의와 모형

준위 인덱스 `J=0..14`, `g_J=2J+1`, `E_J`는 원본 `hd_lamda.dat`의 cm^-1 term energy. `A_{ul}`와 `nu_{ul}`도 같은 파일에서 얻는다. 충돌 상대는 para-H2(번호 2) 및 ortho-H2(번호 3), 동일한 원본 온도 격자 `100,200,300,400,600,1000,2000,3000,4000 K`를 사용한다. `n(H2)>0`, OPR=3 -> `(x_para,x_ortho)=(1/4,3/4)`. 광학적으로 얇고 외부 복사장은 없는 무충돌 포획(non-trapping) 모델, 시간독립 정상상태를 선택한다. 분자종 총수는 보존되며 CMB/우주론 동역학/진화 IVP/화학반응은 포함하지 않는다.

원본으로 주어진 하향 충돌률 `q_ul(T)`의 단위는 cm^3 s^-1이다. 혼합 충돌률은

\[
 C_{u\to l}=n_{H_2}[\tfrac14 q^{(p)}_{ul}(T)+\tfrac34 q^{(o)}_{ul}(T)],\qquad
 C_{l\to u}=C_{u\to l}\frac{g_u}{g_l}\exp[-hc\,100(\widetilde E_u-\widetilde E_l)/(k_BT)] .
\]

여기서 100은 cm^-1→m^-1 변환이고, SI 정확 상수 `h=6.62607015e-34 J s`, `c=299792458 m/s`, `k_B=1.380649e-23 J/K`를 사용한다. 참고로 원본 2026 FITS의 표준격자 재현에서 `hc*100/k_B = 1.4387768775039336 K cm` 대신 `1.4388 K cm`를 사용하면 직접 비교한 100 K 5조건의 일치가 크게 개선된다. 이는 데이터가 지시하는 **재현 컨벤션 후보**이지 Neufeld 소스코드가 실제 이 상수를 사용했다는 확증이 아니다. 두 물리 결과를 서로 구분해 전부 계산했다.

전이 생성자 `L`은 열 `j`에서 행 `i`로 이동률 `L_ij = W_{j→i}`를 넣고, `L_jj=-sum_{i!=j}W_{j→i}`로 정의한다. 따라서 `1^T L=0`. 준위 확률 `p=(p_0,...,p_14)`는

\[Lp=0,\quad \mathbf1^Tp=1,\quad p_J\geq0.\]

등식 `p_0=1`을 임시로 두면 미지수 `w=(p_1/p_0,...,p_14/p_0)`는

\[-L_{TT}w=L_{T0},\quad p_0=(1+\mathbf1^Tw)^{-1},\quad p_T=p_0w.\]

`-L_TT`는 양의 역행렬을 가진 비특이 M-matrix(ground state로의 방사 붕괴에 의해 접근 가능)이고 비음수 RHS를 가진다. 따라서 float64 정규화 행 직접 치환보다 양의 점유수를 유지하는 구조적 계산식이다. 각 단계에서 피벗 양성, 점유수 비음성, 정규화, generator residual을 검사한다. 이런 M-matrix 이론은 알고리즘 수렴성 주장이 아니라 **물리 제약의 정확한 보존**을 위한 구조적 정의이다.

외부 복사장이 0이므로 방출복사 출력은

\[\Lambda_{\mathrm{HD}}(T,n)=\sum_{u>l}p_u A_{ul}h\nu_{ul}\quad [\mathrm W /\mathrm{HD}],\]

단순한 보존적 복사 방출률이다. Neufeld(2026)의 오프셋 없는 optically thin model과 비교할 수 있지만 CMB를 포함한 PR #167/#168의 net cooling과는 같은 관측량이 아니다.

## 공통 원천 비교와 source fidelity

2021 LAMDA 표는 Flower(1999)에서 초래된 50/100/200 K 충돌률 9개 × para/ortho, 2026 표는 Wan et al.(2019) 계열 100..4000 K의 각 105개 × para/ortho 충돌률이다. 교집합 100/200 K에서 9×2×2 = **36개 원본 대응값**만 직접 비교한다. 2026 J>8 충돌률은 Neufeld의 외삽이며 실험적으로 측정된 15준위 전체 계수가 아님. 2021 모델에 들어 있던 양자역학 유도율도 laboratory measured collision rates로 바꾸어 부르지 않는다.

J=1→0으로 축소한 독립 2준위 모델에 대해 `q21` 또는 `q26`을 적용하면

\[p_1=\frac{3nq\exp(-\Delta E/k_BT)}{A_{10}+nq+3nq\exp(-\Delta E/k_BT)},\quad
\Lambda_{10}=p_1 A_{10}h\nu_{10}.\]

반면 15준위 전체는 상위 준위와 ΔJ>1 충돌채널을 포함하므로 단순 J1 결과와 동일하다고 해석하지 않는다. 에너지 상수 및 선 중심의 각 소스 버전을 별도 잠금한다.

## 원본 CDMS 2011 v2의 covariance 경계

원본 `HD.fit`에 6개 독립 파라미터의 인쇄 표준오차와 15개 인쇄 상관계수가 포함되어 있다. 인쇄 상관행렬의 최소 고유값은 `1.08486e-5`, 조건수는 `4.03721e5`로 매우 강하게 연관된다. 인쇄된 숫자로부터 `C_ij = sigma_i rho_ij sigma_j`로 만든 것은 **반올림된 6×6 근사 파라미터 공분산**일 뿐 원본 `.var`/`.unf` full-precision covariance와 동일하다고 주장하지 않는다. 2023 Sung 선중심 사이의 joint covariance와도 별개이다. 이것만으로 관측 sigma, chi-square 또는 H5 ε를 생성하지 않는다.

## 2026 FITS의 IEEE NaN 처리

원본 `hd_population_grids.fits` (15 levels × 111 densities × 161 temperatures)의 `LOGPOP=log10(f_J/g_J)`. NaN은 수치적으로 미해결된 미소 준위 점유수이다. Wolfram 기본 FITS Import가 일부 IEEE NaN을 수치 `0.`으로 읽는 사례를 발견했다. 0을 `LOGPOP=0`으로 간주하여 `g_J 10^0`로 바꾸면 정규화가 파괴된다. 원본 FITS HDU header의 `NANCOUNT=18868`에 근거해 결측을 명시적으로 마스킹한 100 K의 J=0..6 값만, 오프셋이 없는 15준위 solver와 직접 비교했다. 1.4388 변환에서 최대 점유수 절대차 `4.345084292367574e-10`, SI 정확 변환에서 `6.413771957425318e-6`이다. 이는 구현차의 교차검산이며 독립 저자 R6/C9 검증은 아니다.

## 판단

현재 15준위 결과는 **2026 원전 소스를 잠근 새로운 scoped research model**이다. 원래 2011 owner-source 35Hz 실패 7/8, H5 epsilon null, H6/H7 OPEN, production HOLD, canonical 28/88, REC physical 0/313은 그대로다. 이 연구 노드는 원본 대조 관측량과 source-qualified benchmark를 제공하지만 2011 원본 원천을 2026 자료로 자동 교체하거나 기존 DAG complete로 승격하지 않는다.
