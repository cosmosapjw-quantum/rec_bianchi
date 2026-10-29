# REC HD: Sung et al. 실측 회전선 4개와 기존 실측 제약 5개의 cycle 이론

**이론 단위:** `REC_HD_SUNG2022_CYCLES_20261030`  
**원본 보호:** PR163 `65c5c4c9105c9957418ff014d34e007e53a63b3b`, Draft/HOLD; 2021 LAMDA term-energy/printed-photon 35 Hz gate FAIL7/8 유지.  
**Source:** Sung et al., *JQSRT* 295 (2023) 108412, https://doi.org/10.1016/j.jqsrt.2022.108412, 2022-11-04 온라인 선공개. 원문 Table 4의 멀티스펙트럼-피팅 line center 4개와 296 K H₂ pressure broadening/shift 계수. 이 세션에서 **공개 논문의 렌더된 텍스트**를 확보했으나 원본 PDF 바이트/실험 원자료는 확보했다고 주장하지 않는다.

## 1. 실험 정의와 단위

HD `v=0`, 회전 양자수 `J=0,...,8`, `R(j)`는 `J=j+1 -> j`의 순수 회전 전이다. Sung의 296 K 기준 선중심 파수 `\tilde ν_j`와 피팅 괄호 오차는:

|R| `\tildeν_j` (cm⁻¹) | line-fit reported error (cm⁻¹) | H₂ collisional HWHM slope (cm⁻¹ atm⁻¹) | H₂ pressure shift slope (cm⁻¹ atm⁻¹) |
|---|---:|---:|---:|---:|
|R(0)|89.22792|0.00003|0.0120(4)|+0.00017(35)|
|R(1)|177.84141|0.00003|0.0114(1)|+0.00141(22)|
|R(2)|265.24055|0.00003|0.0104(1)|+0.00106(13)|
|R(3)|350.85401|0.00004|0.0097(2)|−0.00108(17)|

**핵심 주의:** 이 오차는 다중 스펙트럼 피팅의 오류다. 논문에서 calibration 정확도는 `better than 0.0001 cm⁻¹`라 기술하지만, 전체 systematic errors가 fitting errors를 초과한다고 명시한다. 서로 다른 전이/논문 간 완전한 joint covariance는 미확보. 계통오차나 historical CDMS catalog covariance를 추측하여 `σ`, `χ²`를 생성하지 않는다.

단위 환산은 `f=(100 c)\tildeν`, `c=299792458 m/s`; `h=6.62607015×10⁻³⁴ J s` 유지.

## 2. 측정 그래프와 정확 rank

PR163의 실측 엣지 순서는 `[(2,0),(3,1),(4,3),(6,5),(7,6)]`: 2022년 Cozijn 초정밀 준위차 두 개와 1984년 Essenwanger–Gush 직접 회전선 세 개이다. Sung의 **새로운 원문 측정 엣지** `[(1,0),(2,1),(3,2),(4,3)]`를 추가한다. 따라서 9개의 입력 `y`와 9개의 회전준위 에너지 `E=(E_0,...,E_8)`에 대해

\[
 y=D E/h,\quad D_{e,J}=\delta_{J,u(e)}-\delta_{J,l(e)},\quad
 \operatorname{rank}(D)=6,\quad \ker D=\operatorname{span}\{\text{three component constants}\}.
\]

연결 성분은 `{0,1,2,3,4}`, `{5,6,7}`, `{8}`. 그러므로 8개 인접 회전 전이 전체를 실측만으로 유일하게 결정할 수 없다. 새 4개 관측행은 기존 5행보다 **rank +1**의 증가와 **독립 cycle 3개**를 제공한다. 이는 개별 측정들이 통계적으로 독립이라는 뜻이 아닌 incidence rank이다.

독립 폐회로 행렬 `C`를

\[
 C=\begin{pmatrix}
 1&0&0&0&0&-1&-1&0&0\\
 0&1&0&0&0&0&-1&-1&0\\
 0&0&1&0&0&0&0&0&-1
 \end{pmatrix},\quad CD=0,
\]

로 잡으면 `Cy`는 모델에서 참된 동일 물리준위를 정확히 공유할 때 0이어야 한다. 출판된 실측 명목값으로 계산한 세 잔차는

- `2022 (J2−J0) − [Sung R(0)+R(1)] = −3.921711314 MHz`;
- `2022 (J3−J1) − [Sung R(1)+R(2)] = −17.890385768 MHz`;
- `1984 R(3) − Sung R(3) = −60.258284058 MHz`.

**측정 간 cycle residual**이며 2021 LAMDA 또는 2011 CDMS 모델 residual과 다르다. `Cov(Cy)=C Cov(y) Cᵀ`이지만, Sung·Cozijn·Essenwanger 원자료의 전체 상관/계통 오차가 없으므로 `Cov(y)=null`; 통계적 `σ`, 카탈로그 fit 배제, physical drift claim 불허.

## 3. 정확한 nominal 최소 보정량

`d_20,d_31`를 첫 두 cycle residual (Hz)로 둔다. Sung의 저준위 세 frequency correction `(δ_0,δ_1,δ_2)`가 두 2022 조합 nominal center를 정확히 만족하려면 `δ_0+δ_1=d_20`, `δ_1+δ_2=d_31`. 그러므로

\[
 \min_{\delta}\Vert\delta\Vert_\infty
 =\tfrac12\big[\max(0,d_{20},d_{31})-\min(0,d_{20},d_{31})\big]
 = \mathbf{8.945192884\ MHz}.
\]

증명: `δ_1`은 `[-t,t]∩[d_20-t,d_20+t]∩[d_31-t,d_31+t]`에 속해야 하므로 세 구간 중심의 폭이 `2t` 이하일 필요충분조건이다. 실제 도달 witness `(5.023481570, −8.945192884, −8.945192884) MHz`가 이 하한에 도달한다. 이는 **조건부 nominal 입력을 서로 맞추는 데 필요한 보정량 하한**이지 실제 calibration error 크기, 물리 변화, 공동 p-value가 아니다.

## 4. 실제 측정 pressure coefficients로 생성한 조건부 관측량

Sung Table 4의 `296 K` 기준 측정 parameter를 사용하여 **H₂ 단독 충돌 파라미터**의 선형 empirical model을 정의한다:

\[
 \tildeν_J(P)=\tildeν_J(0)+\delta_{H_2,J}P_{H_2},\quad
 \gamma_J(P)=\gamma_{H_2,J}P_{H_2},\quad
 \mathrm{FWHM}_{\rm Lorentz}=2\gamma_J(P).
\]

`P_H2`는 `atm`, `T=296 K`, `P={0.1,0.5,1} atm`의 **가정된 입력**이다. 원전의 4개 measured coefficient와 확정 SI 상수로부터 `4×3=12`개의 조건부 `line center, HWHM, FWHM, shift` 데이터 행을 생성했다. 이것은 천문 line profile, radiative-transfer solution, 실제 기체 history나 새로운 12개 실험이 아니다. 기존 2021 LAMDA Einstein A를 별개 역사적 소스로 붙인 `4`개의 광자 energy/wavelength/spontaneous-power 행도 제공하되, *새 실험으로 Einstein A를 측정했다는 주장 금지*.

## 5. 결과 판정과 원본 경계

이번 연구는 실제 laboratory source rows 4개를 신규 import하고 3개 measured cycle, 12개 조건부 source-bound pressure rows, 4개 photon rows를 생성한 연구 증거의 진전이다. `REC-EXP-SPECTRAL`을 **PARTIAL** 상태로 유지하고 canonical `28/88 (+0)`, REC physical `0/313 (+0)`을 고정한다. 원본 35Hz `FAIL7/8`, H5 ε null, H6/H7 OPEN, L4/REI false, production HOLD, AUTO_NEXT_NODE false. 별개 저자 검증 R6/C9 NOT_RUN.

원본 Dec-2011 CDMS SPFIT `.fit/.par/.lin/c003501i.cat`과 full covariance 및 Sung 원 실험 raw/covariance 여전히 확보 대상이다. CDMS v3(2026) 또는 2019 file을 자동 대입하지 않는다.
