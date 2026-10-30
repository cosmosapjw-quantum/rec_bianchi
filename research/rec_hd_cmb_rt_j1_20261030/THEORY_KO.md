# HD J=1→0 복사-충돌 정상상태로부터 CMB 선 밝기까지: 실제 원천계수와 얇은 슬래브

연구 단위 `REC_HD_CMB_RT_J1_20261030`; 기준은 REC PR #167 HEAD `434c7b66b382eda230e9c2f728c937da28c47a1b`이다. 시공간 팽창을 동역학적으로 풀지 않으며 각 적색편이에서 주어진 등방 흑체 CMB 온도 `T_R(z)=2.72548(1+z) K`를 외부 bath로 사용한다. 정지된 광학적으로 얇은, 등온 HD 슬래브를 가정한다. 준위 에너지는 2021 LAMDA의 2011 CDMS v2 표기 준위 값에서 얻고 `c,h,k_B`는 SI로 명시한다. 단일 J=1→0 transition에만 **원래 35 Hz source gate PASS**, 나머지는 **FAIL7/8**이다.

## 1. 정의

`J=0,1`에서 `g_0=1, g_1=3`, `ν=(E_1−E_0)/h=100c(89.227931611 cm^-1)`, `A_10=5.442×10^-8 s^-1`. 분자량은 LAMDA에서 주어진 명목 `3 u`를 사용하고 `1u=1.66053906660×10^-27 kg`이다. 상하 준위 점유수 `p_0+p_1=1`. 2021 Flower(1999) 충돌률 표기값은 `T_g=50,100,200 K`에 한정한다. 적색편이는 `z=0,10,30,50`으로 선택한다. 선폭은 **충돌압력/마이크로터뷸런스 없이 열속도에 의한 Gaussian**으로 정의한다.

정상상태 인구는 앞선 PR167의 원본을 복사한 `src/hd_cmb_balance.py`와 정확히 동일한 `twolevel` 계산에서 가져온다. 즉, `nbar=[exp(hν/k_BT_R)-1]^-1`,
`R_10=A_10(1+nbar)`, `R_01=3A_10 nbar`, `C_10=n_H2 q_10(T_g)`, `C_01=3C_10 exp[-hν/(k_BT_g)]`와 `p_1=(C_01+R_01)/(C_01+C_10+R_01+R_10)`. 기체 밀도 `n_H2` 단위는 cm^-3, `q`는 cm^3/s. `n_H2>0`만 정식 계산에 허용한다.

## 2. 방사전달과 광학깊이

주파수 `ν` 부근에서 스펙트럼 함수가 `∫φ_{ν'}dν'=1`인 정규화 line shape라고 하자. 고정된 population 슬래브에서 방출계수와 흡수계수는

\[
 j_{ν'}=\frac{hν}{4\pi} n_{HD}p_1 A_{10}\phi_{ν'},\quad
 \alpha_{ν'}=\frac{c^2 A_{10}}{8\piν^2}n_{HD}(3p_0-p_1)\phi_{ν'} .
\]

공명 중심의 좁은 선 근사를 사용하여 Planck/source factor를 중심 ν에서 평가한다. 따라서 `N_HD`가 실제 **HD 분자 자체의 수주밀도**(m^-2)일 때

\[
 \tau_{ν'}=\frac{N_{HD}c^2A_{10}}{8\piν^2}(3p_0-p_1)\phi_{ν'},\quad
 S_ν=\frac{2hν^3}{c^2}\frac{p_1}{3p_0-p_1},\quad B_ν(T_R)=\frac{2hν^3}{c^2}\bar n.
\]

이 수식에서는 PR165의 HITRAN natural-isotopologue-weighted `S_296`를 사용하지 않는다. 그 값을 `N_HD`에 중복으로 곱하지 않는다.

이후 주어진 고정 준위점유수에 대한 균일 슬래브의 formal solution은

\[
 \Delta I_{ν'}^{(e)}=[S_ν-B_ν(T_R)](1-e^{-\tau_{ν'}}),\quad
 \Delta I_{ν_o}^{(o)}=\frac{\Delta I_{ν_e}^{(e)}}{(1+z)^3},\qquad ν_o=ν_e/(1+z).
\]

여기서 `(e)`와 `(o)`는 각각 슬래브 위치와 관측자이며 마지막 식은 FRW 적색편이에 대한 진공 Liouville 방정식 `I_ν/ν^3=const`를 가정한 조건부 투영이다. `ΔT_RJ,o = c²ΔI_{ν_o}/(2k_B ν_o²)`는 **RJ 밝기 환산**이지 CMB thermodynamic temperature 자체가 아니다.

열 Gaussian은 `b=√(2k_BT_g/(3u))`, `Δν_D=ν b/c`, `x=(ν'−ν)/Δν_D`, `φ=(√π Δν_D)^−1 exp(−x²)`로 지정한다. `N_HD=10^14,10^16,10^18 cm^-2`를 사용한다. 모든 계산된 `τ_0<0.1`인 경우만 채택하고, 광학깊이 자체가 상태 점유수를 바꾸는 self-consistent transport는 풀지 않는다.

## 3. 에너지 ledger를 방사전달에 연결하는 정리

고정된 회전준위에서 PR167의 분자당 순복사 유출은

\[
 \ell=hνA_{10}\big[p_1(1+\bar n)-3p_0\bar n\big].
\]

`S_ν`와 `τ_{ν'}`를 대입하면 exact algebraically

\[
 (S_ν-B_ν)\tau_{ν'}=\frac{N_{HD}\ell}{4\pi}\phi_{ν'},\qquad
 \int \Delta I_{ν'}^{(e)}dν'\xrightarrow[\tau\to0]{}\frac{N_{HD}\ell}{4\pi}.
\]

이 등식은 thin line approximation에서 파장 적분이 원본 복사/충돌 에너지 ledger와 일치해야 한다는 강력한 재현성 조건이다. 멀리서의 적분 스펙트럼은 `(1+z)^−4` 배만큼 감쇠한다. 이론식은 Wolfram exact simplification에서 잔차 0으로 재검산했다.

## 4. Gaussian 포화 적분과 유한 τ

`τ_{ν'}=τ_0 e^{-x²}`인 경우 적분 formal slab result를 첫째 차수의 정확 적분값과 비교하면

\[
 \mathcal F(τ_0)\equiv\frac{1}{τ_0\sqrt\pi}\int_{-\infty}^\infty[1-e^{-τ_0e^{-x^2}}]dx
 =\sum_{k=1}^\infty\frac{(-1)^{k+1}τ_0^{k-1}}{k!\sqrt{k}}
 =1-\frac{τ_0}{2\sqrt2}+\frac{τ_0^2}{6\sqrt3}-\frac{τ_0^3}{48}+\cdots .
\]

따라서 고정된 J1 population과 source function 아래에서 `∫ΔI^{(e)}dν'=N_HDℓ F(τ_0)/(4π)`. 이 보정은 장거리 다중 산란이나 포획이 점유수에 미치는 영향을 포함하지 않으므로, `τ_0<0.1` 조건에서만 **frozen-population one-pass prediction**으로 해석한다. 14항 계산과 SciPy adaptive quadrature 12개의 독립 적분 비교를 수행했다.

## 5. 물리적 의미와 원본 계보

- 실제 원천: PR161에서 byte-locked한 **공식 LAMDA 2021 화면 전사**의 9준위, 8 Einstein A, 54개 para/ortho H2 계수. 원본 `hd.dat` 바이트는 이번에도 미획득. 원본 CDMS 2011 SPFIT `.fit/.par/.lin/.cat/.egy`와 full covariance도 미획득.
- Sung(2023) 4개 측정선은 PR164 원본 전사로 보존했으나 **본 J1 프로파일에서 주파수/광도 계수로 사용하지 않았다**. 선중심과 H2 압력이동 계수를 서로 대체하지 않았다.
- Neufeld(2026), ApJ 1007,16, DOI 10.3847/1538-4357/ae851a의 Zenodo v2 (10.5281/zenodo.21165907)는 Wan et al.(2019) 충돌률과 100–4000 K, n=10²–10¹² cm⁻³의 비LTE 모델을 제공하지만 원본 `.dat/.fits` 다운로드 실패. 이번 모델의 입력 또는 독립 검산으로 사용한 적 없다.
- **출력은 실제 계수에 묶인 물리 예측**이지 실험 측정값, 천체 관측, primordial BBN abundance 혹은 우주 thermal-history IVP가 아니다. 온도/밀도/column은 지정된 외부 파라미터다. 9준위 35 Hz FAIL7/8을 해결하지 않고도 J1 scoped 결과를 생성할 수 있으나, 전체 REC physical DAG promotion은 불가능하다.

## 6. 결과 및 claim gate

`3(T_g)×4(z)×4(n_H2)×3(f_ortho)×3(N_HD)=432`개의 해석-수치 연결 상태, 321 점/상태에서 `138672`개의 주파수별 스펙트럼을 생성했다. 최대 τ_0=0.09798333062755982, 최대 Gaussian integral 상대오차=5.0953379033178166×10⁻¹², 최소 포화인자=0.9662622325010021. Python 회귀 20/20 normal, 20/20 `-O`, compileall PASS; SciPy 다른 알고리즘 적분 12/12, 최대 절대차 4.44×10⁻¹⁶; Wolfram symbolic exact residual=0. **다른 저자 R6/C9는 NOT_RUN**이다.

원래 canonical **28/88 (+0)**, REC physical **0/313 (+0)**, REC-EXP-SPECTRAL **PARTIAL** (9 measured relationships, rank6, cycles3), 원래 35 Hz **FAIL7/8**, H5 epsilon=null, H6/H7 OPEN, L4=false, REI activation=false, production HOLD, AUTO_NEXT_NODE=false. 새 연구용 J1-slab auxiliary **1/1 SCOPED**, 전체 REC DAG 완료로 취급 금지.
