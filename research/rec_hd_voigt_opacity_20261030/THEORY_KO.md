# REC HD | Sung 실측 line strength에서 Voigt 조건부 흡수 관측량으로

**연구 단위:** `REC_HD_VOIGT_OPACITY_20261030` · 2026-10-30 KST · 부모 PR164 HEAD `e050b97b7d5c6c0929062fafd7333e0164112399` 고정. 2011 CDMS v2, 2021 LAMDA 원래 필드, 원 35 Hz gate, production, main 및 외부 저장소를 변경하지 않는다. 이 논문에 없는 실제 관측치를 임의로 생성하는 작업이 아니라, 실측 분광 계수에서 조건부 transfer 관측량을 유도하는 연구다.

## 1. 측정 원천과 두 가지 선강도 convention

Sung et al., *JQSRT* 295, 108412 (2023), DOI `10.1016/j.jqsrt.2022.108412` (online 2022-11-04), Table 4는 중성 HD의 `v=0` 회전선 R(0)–R(3)의 진공 선중심 `ν̃_0` (`cm^-1`), 기준온도 296 K의 측정 선강도 `S` (`cm molecule^-1`), H₂ 압력 선폭 HWHM 기울기 `γ_H2` 및 선중심 이동 기울기 `δ_H2` (`cm^-1 atm^-1`)를 제시한다. 본 연구는 부모 PR164 `data/LAB_INPUT.json`의 4개 원문 숫자를 잠금하고 재사용한다. 실제 원본 스펙트럼/멀티스펙트럼 공분산/실험 systematics 전체는 입수되지 않았다. 공개 논문의 표상 오차는 fitting error이며 총 systematic error가 아니다.

원 논문의 `S`는 HITRAN 방식의 **자연 동위원소 존재비 가중 선강도**이다. HITRAN 공식 정의 `https://hitran.org/docs/definitions-and-units/`에서 `S_ij=I_a ×(...)`이고, `τ=N_ref S φ`에서 **N_ref는 동일 HITRAN 존재비 convention의 reference-molecule column**이어야 한다. 실제 HD-only column `N_HD`를 쓰려면 `S/I_a`를 재구성하고 정확한 abundance 및 partition function convention을 확인해야 한다. 여기서는 그것을 수행하지 않고 `N_ref`를 명시적으로 가정한다. 이전 LAMDA/CDMS Einstein A와 Sung의 실측 S를 같은 출처로 취급하지 않는다.

## 2. 유도: Maxwell–Doppler + H₂ Lorentz → 조건부 Voigt

온도 `T=296 K`, `p_H2`는 atm 단위의 H₂ 부분압, `m_HD ≈ 3.021927 u` (명목적 질량; `1u=1.66053906660×10^-27 kg` 사용), 속력의 SI 상수 `c=299792458 m/s`, `k_B=1.380649×10^-23 J/K`를 쓴다. 광학선 파수는 cm^-1이므로 선형 1차 비상대론적 Doppler 정규표준편차는

\[\sigma_D=\tilde\nu_0\sqrt{\frac{k_BT}{m_{HD}c^2}}\quad[\mathrm{cm}^{-1}].\]

Sung의 측정계수로 `ν̃_c(p)=ν̃_0+δ_H2 p` 및 충돌 HWHM `γ(p)=γ_H2 p`를 정의한다. 순수 H₂ 충돌만의 **선형 296 K** 제한이며 self-broadening, 온도의존 `γ`, `δ`, 기기분해능과 collisional narrowing은 제외한다. 원 논문은 Rautian (hard-collision/non-Voigt) profile로 실제 데이터를 맞췄다. 따라서 여기서 선택한 Voigt는 **조건부 baseline 모형**이고 실제 실험의 완전한 모형이 아니다.

\[G_\sigma(x)=\frac{e^{-x^2/(2\sigma^2)}}{\sigma\sqrt{2\pi}},\qquad L_\gamma(x)=\frac{\gamma}{\pi(x^2+\gamma^2)},\qquad V(x;\sigma,\gamma)=(G_\sigma*L_\gamma)(x).\]

양쪽 정규화 `∫ V(x) dx = 1`에서 `V`의 단위는 **cm**이다. 그러므로 광학깊이와 투과율은

\[\tau_J(\tilde\nu;p,N_{ref})=N_{ref} S_J V(\tilde\nu-\tilde\nu_{c,J}(p);\sigma_{D,J},\gamma_J(p)),\qquad \mathcal{T}=\exp(-\tau_J).\]

광학깊이는 무차원이다. 순수 흡수 slab, incident intensity `I_0`, emission/stimulated source function, scattering, 다중라인 중첩 및 transport는 제외한다. `N_ref`와 `p_H2`는 관측된 density/path length가 아니라 독립적인 모델 매개변수이며 하나의 실제 기체 geometry를 주장하지 않는다.

## 3. 새 파생 물리 관측량과 폐구간 bound

조건부 입력 `p={0.01,0.1,0.5} atm`과 `N_ref={10^22,10^23,10^24} molecule cm^-2`에서 4×3×3=**36개** 사례를 계산한다. 0.01 atm 값은 측정 조건에 대한 외삽 가능성이 있으므로 보정된 실험예측이 아닌 해석적 테스트에 가깝다. 각 사례는 `center`, `σ_D`, `γ`, Gaussian/Lorentz FWHM, `τ(center)`, `T(center)` 및 적분등가폭을 출력하고 각각 201개 파수 mesh 점으로 총 **7,236**개 조건부 profile 행을 생성한다.

\[W_L=\int_{-L}^L\big(1-e^{-N_{ref}S V(x)}\big)dx,\qquad A_L=\int_{-L}^L V(x)dx.\]

`0≤1-e^{-z}≤z` (z≥0)에서

\[W_L\le W_\infty\le W_L + N_{ref} S(1-A_L),\quad\int_{\mathbb{R}}\tau(x)dx=N_{ref}S.\]

이것은 모형 내부의 **수학적으로 유도된 형식적 상·하한**이고, 실제 파일의 `W_L`, `A_L`은 SciPy 적분의 부동소수 근사이므로 **엄밀 directed-rounding interval certificate를 주장하지 않는다**.

## 4. 재현된 물리값과 검증

`p_H2=0.1 atm`, `N_ref=10^24 cm^-2`, 296K에서 R(0)/R(1)/R(2)/R(3)의 `(τ_peak, T_peak)`는 각각 `(0.1410209370, 0.8684711283)`, `(0.5739503180, 0.5632958401)`, `(0.6491315372, 0.5224993511)`, `(0.3141417570,0.7304154793)`이다. 같은 조건에서 `N_ref=10^23 cm^-2` R(0)의 `σ_D=0.0002685969210133116 cm^-1`, `τ_peak=0.014102093702663764`, `T_peak=0.9859968750523141`; Wolfram 독립 계산과 일치한다.

검증: Voigt positivity/normalization, `γ→0` Gaussian, `σ→0` Lorentz, 피크 column 비례, finite-width bound, 온도/단위/원본문자량, DOI/실측 문자 그대로 잠금, `-O`에서도 변조검출, 원 gate 그대로. 실제 2011 SPFIT `.fit/.par/.lin/c003501i.cat/.egy` 원바이트와 공분산, 원 Sung 공동 공분산은 **여전히 미확보**다. 현행 2019 파일이나 2026 v3로 자동 대체하지 않았다.

## 5. DAG와 claim admission

이 논문의 물리적 기여는 **실측 S, γ, δ를 사용하여 분광→기초 복사전달을 연결하는 조건부 line-by-line 관측량 atlas**다. 새 측정값 자체는 **0개**(부모 4개 재사용), 독립 관측관계 여전히 **9개**, rank **6**, cycle **3**. `REC-EXP-SPECTRAL` 증거 overlay는 partial 확장만 허용하고 중앙 `28/88 (+0)`, REC 물리 `0/313 (+0)`을 유지한다. 별개 저자 R6/C9 NOT_RUN, 원 35Hz `FAIL7/8`, H5 epsilon null, H6/H7 OPEN, L4/REI=false, production HOLD, auto-next=false. 후속 실제 과학은 실험 공동 공분산 확보 및 Rautian/실제 원 스펙트럼과의 교차검증, source-owner native coupling이다.
