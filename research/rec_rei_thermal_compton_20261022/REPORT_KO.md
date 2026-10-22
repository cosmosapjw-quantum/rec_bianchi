# THERM02 — 현재 상태에 결합한 RR·Compton 열 진화

작성: 2026-10-23 KST. 연구 규약: physmath workflow 1.0.0 / approval v0.2.
연구 단위: `research/rec_rei_thermal_compton_20261022`, REC Draft PR125.

## 1. 확보한 결과와 그 범위

**새로 고정한 8개 초기값 문제를 sandbox에서 한 번씩 완료했다.** 5개 nominal
compact34, hot/Planck 각각의 tight34, Planck full63 oracle이다. 모든 적분은
z20→2, 193개 비교 시각, 5–60 eV 외부 UV를 사용한다. 세 정밀도/좌표 비교와
고정된 유한 수용 기준은 모두 PASS다. 누적 과학 실행·진단·저장 시간은
92.951497908 s였다. 완료된 과거 cohort를 다시 적분한 횟수는 0이다.

Mao-factor hybrid를 고정한 split seed에서 Compton off→actual-hot 변경은
z=2의 온도를 6573.376838 K에서 5609.584328 K로 낮췄다. 독립적으로 지정한
Planck reference는 5610.699960 K였다. Planck−hot 차이의 구간 최대는
7.194733 K이며, 두 branch에서 관측된 nominal/tight 온도 변화보다 크다.
반면 shear·matter stress·neutrino stress 차이는 그 정밀도 변화보다 작아
이 유한 비교에서 분해되지 않는다. 수용 시험의 통과와 각 물리량의 branch
차이 분해 여부는 별개의 판정이다.

현재 결과는 **21-population conditional atomic/thermal test-fluid 계산**이다.
온도는 이 새 단위에서 진화시키지만 UV는 prescribed이다. Li resonance의
완전한 final ionic yield와 실제 광자장의 spectral recoil/induced 및
radiation-energy/Einstein backreaction은 닫히지 않았다. 완전한 핵반응망이나
완전한 열역학적 폐쇄를 주장하지 않는다. 최종 게시·백업의 실제 ACK와 검증
범위는 `delivery/`의 receipt가 기록한다.

근거: `results/SCIENCE_SUMMARY.json`, `results/VALIDATION_COMPARISONS.json`,
`results/PHYSICS_COMPARISONS.json`, `results/PHYSICS_TABLE.csv` 및 독립 검토
`evidence/independent_review/REVIEW.md`.

## 2. 재사용 경계와 source 확인

| 근거 | 고정 identity / 범위 | 이번 사용 |
|---|---|---|
| REC PR119 복구 | `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`; 125 main + 1 control = 126 | 완료 상태와 복구 경계를 계승; 재실행 없음 |
| REI PR220 | `8be7533cc97b3302bf42608699d6e8313ed6af8a`; 127 main + 2 oracle = 129; 62→33 | 정확한 restriction/lift와 donor를 계승; REC 행·계수·실행 수와 합치지 않음 |
| THERM01 / REC PR120 | `7c4af579be508cccf203d3e2a3a5aa16a4b28e38`; 8개 완료 | compact34, thermal coordinate, source adapter와 2개 저장 baseline 재사용 |
| REC PR121 | `892aad5c3e9fb0b2abd021154b62a42c39277125` | Mao 6개 행, 원본 calc/pars, source lock 6파일을 byte 그대로 재사용 |
| REC PR124 | `e6ecef7624e39bee66b39e09d99fe355f76e2eae`; 별도 restart 8개 완료 | 동시 연구의 5–200 eV/full63/logT 결과를 읽음; 이번 결과와 합산·속도 비교하지 않음 |

`provenance/REUSED_FILES.json`의 70개 입력은 byte count, SHA-256와 Git blob
identity로 고정했다. 독립 검토도 이 일치를 확인했다. 원래 REI 첫 실패 raw의
역사적 보존 범위는 **local-only**로 유지한다. 새 THERM02 raw의 보존은 이를
소급해 변경하지 않는다. PR124의 109-node restart와 이번 193-node 전체 구간은
`provenance/CONCURRENT_PR124_INTAKE.md`에서 별도로 대응한다.

### 문헌이 제공하는 것과 이번 구현이 사용하는 것

Mao, Kaastra & Badnell (2017), A&A 599 A10의 전자 에너지 손실 factor는
`f = L/(k_B T alpha)`이다. 원전 식·선택 행과 기존 source lock을 대조하고,
`t=k_B T/eV_J`, 자연로그, `q_initial=Z-s_recombined+1`을 사용했다.
이번 RR loss는 `L_RR=k_B T alpha_donor f_Mao`이다. 수 재결합률은 기존 donor
값이므로 이것을 **Mao-factor hybrid**라고 부른다. 6개 electronic (Z,q)
factor를 13개 isotope RR channel에 대응하며, source-table 114점 검증은
기존 결과를 재사용했다. 새 검증은 이 mapping과 adapter를 겨냥했다.
Source fit의 오차를 hybrid 전체의 물리 오차로 옮기지 않는다.

Sazonov & Sunyaev의 비상대론적 Compton 전개를 사용해 thermal transfer의 부호와
recoil 항을 고정했다. Planck 평형의 회복에는 induced 항이 관여하므로 실제
grey monopole만으로 실제 spectrum의 유효 recoil/induced 항을 정할 수 없다.
Planck bath는 별도 외부 reference로 선언했다.

2026-03-09 출판된 Li 원전 PRA 113, 033105와 Data Availability를 확인했다.
이번 bounded Exa/SciSpace 검색에서 필요한 final-state/charge/energy partition
table을 공개 입력으로 확보하지 못했다. 이는 보편적 부재나 불가능성의 증명이
아니다. 60 eV cutoff는 64.39 eV 문턱의 직접 1s-hole continuum에 도달하지 않지만,
50–60 eV의 실제 공명까지 없애지 않는다. 현재 smoothed continuum에서 제외한
그 공명들의 final ionic yield는 `MISSING_EXACT_INPUT`으로 남는다.

원전: [Mao et al.](https://arxiv.org/abs/1612.01017),
[Sazonov & Sunyaev](https://arxiv.org/abs/astro-ph/9910280),
[Li PRA 113, 033105](https://journals.aps.org/pra/pdf/10.1103/l4xt-3sxy).
세부 source 위치·bytes·검색 범위·상수 대응은
`provenance/SOURCE_REUSE_MEMO_KO.md`, `SOURCE_REUSE_PROVENANCE.json`에 있다.

## 3. 물리에서 계산 단순화로의 연결

### 3.1 열 변수와 compact kernel

SI, metric (-,+,+,+), `x=ln(a/(1/21))`을 사용한다. baryon당 population과
전자 abundance 및 자유입자 수를

\[
Y_i=n_i/n_b,\qquad x_e=q\cdot Y,\qquad \eta=(1+q)\cdot Y
\]

로 두면, 열 변수와 물리 온도는

\[
w=\epsilon_{\rm th}/k_B=\tfrac32\eta T,\qquad T=\frac{2w}{3\eta}
\]

이다. 따라서 ionization에 따른 heat-capacity 변화를 현재 `eta`로 다룬다.
Compton source는 직접적인 ion/electron 수 source를 만들지 않는다. 공통 scalar
T, isotope별 동일 electronic rate, reflection-even LRS가 유지되므로 PR220의
restriction/lift에 w의 identity block을 붙여 full63→compact34를 재사용한다.
이것은 원래의 62→33 결과를 새 실행 수로 재명명한 것이 아니다.

한 RHS 안에서 현재 `T → RR/DR → n_e → Thomson opacity → photon monopole`을
연결한다. 기존 저장 궤적을 새 RHS의 입력으로 재생하지 않는다. 6개 distinct
RR factor의 vectorization, UV의 두 moment 사전 계산, 현재 상태 계산의 재사용이
이번 단순화다. 새 time-splitting이나 surrogate thermal table을 넣지 않았다.

### 3.2 두 광자 energy owner

\[
K=\frac{\sigma_Tc}{m_ec^2},\quad
U_\gamma=\rho_{\rm crit,J}\Omega_\gamma y_4/a^4.
\]

Donor의 `THOMSON`은 이미 `sigma_T*c`이므로 c를 다시 곱하지 않는다.
actual-hot는 현재 광자 monopole을 사용한다.

\[
Q_C^{\rm hot}=-4K n_e k_BT U_\gamma.
\]

이 branch는 실제 grey field의 leading thermal Compton 성분이다. 반면
독립 외부 Planck reference는

\[
T_r=2.7255/a,\quad U_r=a_RT_r^4,\quad
Q_C^{\rm ref}=4K n_e k_BU_r(T_r-T)
\]

로 지정한다. 두 source는 선택 가능한 서로 다른 모델이며 한 경우에 더하지
않는다. Planck reference의 energy density를 Einstein source에 추가하지 않는다.

외부 UV의 scalar photon flux는 `Phi=c*n_gamma`이다. 68개 threshold-split bin의
**실제 GL4 272개 node/flux**에서

\[
U_{\rm UV}=\frac1c\sum_j\Phi_j E_j,\qquad
M_{\rm UV}=\frac1c\sum_j\Phi_j E_j^2,
\]
\[
Q_{{\rm UV},C}=K n_e(M_{\rm UV}-4k_BT U_{\rm UV})
\]

를 구성한다. Unit amplitude에서 두 moment는 각각
`1.1416599128906846e-16 J/m^3`, `3.1681648628575677e-34 J^2/m^3`이다.
스펙트럼을 매 RHS에서 재적분하지 않고 prescribed amplitude만 곱한다.
5–200 eV 71-bin provider의 bin-center 가정을 이 배열에 적용하지 않았다.
off branch는 두 Compton source를 끄지만 기존 UV photoionization은 유지한다.

### 3.3 정확한 affine contraction

hot에서 `(U_*,R_*)=(U_gamma,0)`, reference에서 `(U_r,4 U_r T_r)`를 쓰면

\[
\Delta w'_C=B-Aw,\qquad
A=\frac{8Kx_e(U_*+U_{\rm UV})}{3H\eta},\quad
B=\frac{Kx_e}{H}\left(R_*+\frac{M_{\rm UV}}{k_B}\right).
\]

이 식은 고정된 모델 안의 대수적 축약이며 새로운 물리 근사가 아니다. 고정
계수의 `w'=-(2+A)w+B`는 `exp/expm1` 해를 가지므로 positivity와 semigroup의
독립 fixture로 사용했다. 실제 changing-Y/geometry/source 시스템은 coupled
BDF로 적분했다. Wolfram symbolic 반환의 identity/flow/semigroup/owner 합은 0이며,
context 도구의 실패 반환도 `provenance/WOLFRAM_CONTEXT_RETURN.json`에 남겼다.

## 4. 에너지 장부와 결합의 물리적 의미

Gas energy는 thermal과 ionic potential을 모두 포함한다.

\[
\epsilon=k_Bw+I\cdot Y,\qquad
\dot\epsilon+2H\epsilon_{\rm th}
=\frac{Q_{\rm abs}-Q_{\rm escape}+Q_C+Q_{{\rm UV},C}}{n_b}.
\]

RR/DR의 kinetic loss와 recombination binding escape를 분리했다. DR의 signed
coefficient 합과 resonance kinetic moment는 donor 의미 그대로 유지했다.
국소 energy owner는 다음과 같다.

| Owner | Gas를 기준으로 한 power 부호 |
|---|---|
| Gas | `Q_abs - Q_escape + Q_C + Q_UV,C` |
| CMB/reference bath | `-Q_C` |
| External UV bath | `-Q_abs - Q_UV,C` |
| Escaped photons | `Q_escape` |

네 source의 합은 0이다. bath debit은 passive ledger이며 radiation hierarchy나
Einstein energy를 진화시키는 spectral collision operator가 아니다.

GL8/GL16으로 저장한 다섯 column은 absorption, escape, adiabatic work,
CMB/reference, UV Compton이다. Signed integral을 각각 보존한다. 에너지 residual과
denominator는 실행 전에 다음으로 고정했다.

\[
R_E=\epsilon-\epsilon_0-I_{\rm abs}+I_{\rm esc}+I_{\rm work}-I_C-I_{\rm UV},
\]
\[
D_E=\max\left(|\epsilon_0|,|\epsilon|,
\sum_j\int |s_j(x)|\,dx\right).
\]

절댓값은 instantaneous source에 적용한 뒤 적분한다. 부호가 바뀌는 누적 교환의
최종 절댓값만 쓰면 cancellation 때문에 throughput을 잃을 수 있다.

### 실제 source feedback

Mao/off와 Mao/hot의 endpoint 적분은 다음과 같다. 단위는 eV/baryon이다.

| Ledger | off | actual-hot |
|---|---:|---:|
| Absorption | 55.30098134 | 64.92153226 |
| Escape | 32.64860854 | 40.86530820 |
| Adiabatic work | 6.21911014 | 4.54359838 |
| CMB/reference → gas | 0 | −3.29099118 |
| UV Compton → gas | 0 | +0.00002885 |

**해석:** Compton 냉각은 현재 T를 바꾸고, 재결합·population·광학깊이를 통해
흡수와 방출도 바꾼다. 이 측정은 −3.29 eV/baryon을 그대로 최종 온도 감소로
환산할 수 없다는 결론을 뒷받침한다. 표의 각 항을 함께 쓰는 first law가 필요하다.

actual-hot에서 `max |Q_C|/(H U_gamma)=9.1079701e-7`, 해당 x 적분은
`4.1632364e-7`이다. Planck branch의 자체 reference owner에서는 각각
`9.0920012e-7`, `4.1559385e-7`이다. 이 값들은 energy-exchange scale이다.
누락한 radiation backreaction의 오차 한계로 승격하지 않는다.

## 5. 계산 결과와 branch 판별

모든 새 경우는 T0=1000 K, UV multiplier=1이다. Split seed는
`Sigma_F=.15, matter_A=.6, radiation_A=.15`, isotropic seed는 모두 0이다.
다음은 nominal 5개 결과다.

| Case | z=2 T [K] | z=2 tau_T | z=2 x_e | CMB/reference 적분 [eV/baryon] |
|---|---:|---:|---:|---:|
| Split / Mao / off | 6573.376838 | 0.07179188797 | 0.8773784352 | 0 |
| Split / Mao / actual-hot | 5609.584328 | 0.07173438922 | 0.8773671477 | −3.290991184 |
| Split / Mao / Planck | 5610.699960 | 0.07173452340 | 0.8773671626 | −3.285963039 |
| Split / derivative / Planck | 5609.349741 | 0.07173449139 | 0.8773671446 | −3.285318131 |
| Isotropic / Mao / Planck | 5610.732813 | 0.07174287067 | 0.8773671630 | −3.286438696 |

Hot−off의 endpoint ΔT는 −963.792510 K이고 구간 최대 절대 차이는
5058.151678 K, 최대 상대 차이는 0.368174423이다. 이 상대량은 각 시각의
`max(|T_left|,|T_right|)`로 나눈 뒤 최대를 취한다. Max absolute와 max relative의
위치는 다르다. off에는 별도의 tight companion이 없으므로 이 대조 전체에
두 branch 수치 정밀도 분해 판정을 붙이지 않는다.

Planck−hot의 endpoint ΔT는 +1.115632 K, 구간 최대 |ΔT|는 7.194733 K
(z=7.87334464), 최대 상대 차이는 7.8252559e-4다. 최종 Δtau는
`1.341804711e-7`이다. Derivative−Mao/Planck의 endpoint −1.350219 K는
RR loss closure 민감도이며, 모델의 실제 물리 오차나 통계적 uncertainty가 아니다.
Isotropic−split/Planck의 endpoint +0.032853 K도 관측된 seed 대조로 남긴다.

### Matter와 radiation의 signed stress

Donor의 정규화는 `factor=sqrt(6)*KAPPA_T/H^2`이며,
`p_m=factor*Pi_m`, `p_r=p_gamma+p_nu`다. 비교 vector는

`[sqrt(6)*s/H, p_m, p_r, p_m+p_r, p_gamma, p_nu]`

이다. 물리 단위의 stress와 정규화된 값, matter와 radiation 및 합을 구분한다.
절댓값 합으로 대체하지 않는다. 저장한 split 궤적에서 radiation stress와
total은 부호를 바꾸므로 signed plot이 필요하다.

Planck−hot의 peak를 두 nominal/tight peak 중 큰 값으로 나눈 진단은 다음과 같다.
이 값은 관측된 유한 정밀도 변화 대비 비율이며 통계적 유의도나 전역 error bound가 아니다.

| 관측량 | Branch peak / max(two refinement peaks) | 이번 유한 판정 |
|---|---:|---|
| T의 절대 변화 | 74741.07 | 두 변화보다 큼 |
| Electron abundance | 912.37 | 두 변화보다 큼 |
| Scaled charge fraction | 6384.74 | 두 변화보다 큼 |
| tau_T | 1056.22 | 두 변화보다 큼 |
| Photon stress | 15.155 | 두 변화보다 큼 |
| Radiation stress | 8.897 | 두 변화보다 큼 |
| Total stress | 7.811 | 두 변화보다 큼 |
| Shear | 0.3058 | 분해되지 않음 |
| Matter stress | 0.00748 | 분해되지 않음 |
| Neutrino stress | 0.02536 | 분해되지 않음 |

독립 reviewer의 배열 재계산이 이 분류를 확인했다. Relative-T refinement
comparison과 절대-T peak의 비율을 혼용하지 않는다. Plot의 상대 T 패널은
명시된 right-case denominator를 사용하고, 위 수용/분석 표는 symmetric
denominator를 사용한다. 두 정의를 각각 라벨에 기록했다.

## 6. 유한 수용, 실행과 독립 검토

Nominal BDF `rtol=2e-9, max_step=.025`, full63 atol은 geometry 40성분
`2e-12`, population 21성분 `2e-11`, tau `2e-12`, w `2e-7 K`이다.
Compact에서는 같은 restriction으로 atol을 옮겼다. Tight는 모든 tolerance를
100으로 나누고 `max_step=.0125`를 썼다. 이 새 tolerance는 실행 전에 고정했다.
과거 THERM01와 잔차 여유가 달라진 것을 축약 알고리즘만의 개선으로 해석하지 않는다.

| 필수 대조 | Max relative T | Charge fraction abs | tau abs | Signed six-vector abs |
|---|---:|---:|---:|---:|
| hot tight34 / nominal | 1.3967462e-7 | 9.9662620e-9 | 1.2703788e-10 | 9.3956808e-10 |
| Planck tight34 / nominal | 1.4007600e-7 | 9.9623413e-9 | 1.2703684e-10 | 6.5035602e-10 |
| Planck full63 / compact34 | 3.4167474e-9 | 1.8718200e-9 | 1.0519807e-11 | 1.4853294e-10 |
| 고정 수용치 | 3e-5 | 3e-5 | 3e-7 | 3e-7 |

최대 normalized energy residual은 **3.7671763347e-7**이며 off case의
z=11.910551212에서 발생한다. 고정 `3e-6` 대비 여유는 **87.4427455%**다.
GL8/GL16 ledger 차이의 최대는 `8.9933966e-12`다. 국소 source/transfer 상대
잔차의 최대는 `5.5017905e-15`이며 `5e-12` 기준 안에 있다.
실제 관측된 온도 범위는 RHS trial guard를 포함해 424.368704–15538.296983 K로,
source domain 100–1e6 K 안에 있다.

저장 범위는 accepted BDF 6710개, 비교 시각 1544개, GL8 12288개, GL16
24576개이다. 이 수들의 합 45118은 평가 scope의 합이며 서로 다른 연속 상태의
개수나 continuum positivity의 증명이 아니다. Baryon residual 최대
`2.2204460e-15`, Einstein residual `5.7848827e-16`, signed tensor residual
`5.4210109e-20`, trace energy fraction `1.8768152e-8`이었다. Neutron/tritium와
decay 제외 좌표는 exact zero를 유지했다. 상세 gate와 실제 검사 scope는 각
`data/<case>/RESULT.json`에 있다.

실행 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8,
numerical thread 1개다. 실제 명령 `python -u code/run.py --run`은 exit 0,
`completed=8; new_this_invocation=8`을 반환했다. Case wall-time 합은
92.831601512 s, campaign cumulative는 92.951497908 s, 최대 한 case는
18.544282746 s였다. 180 s/case, 1200 s cumulative의 cooperative 한도 안이다.
동일 환경·입력의 benchmark가 아니므로 다른 PR 대비 speedup을 주장하지 않는다.

새 pre-ODE check 11그룹은 PASS다. 첫 check 실패와 수정 전 source를 보존했다.
원인은 이미 고정된 breakpoints에 비해 작은 QUADPACK subdivision limit와
donor가 허용하던 isotope roundoff admission의 누락이었다. 이를 교정한 뒤
같은 새 check를 통과했으며 cohort나 물리 gate를 완화하지 않았다.

독립 reviewer는 과학 모듈 import/RHS/ODE 없이 원자료 계산 1회를 수행했다
(exit 0, 2.316 s). 독립 `fsum`/Legendre accumulation으로 ledger를 재구성한
최대 잔차는 `3.7671763360e-7`, 저장 residual과의 차이는 최대 `7.9131e-16`이다.
Source/config/raw identity 및 11개 plotting CSV의 정확한 float64 round-trip을
확인했다. 판정은 `PASS_SCOPED_THERM02_WITH_VISUAL_REPAIR`다.

예외가 `solve_ivp` 반환 전에 발생하면 마지막 RHS trial은 보존할 수 있지만
내부 accepted-step history는 API에서 노출되지 않는다는 한계를 기록했다.
이번 8개 case는 모두 정상 반환했다. Global convergence는 수행하지 않았다.

## 7. 실제 그림과 재현 경로

세 그림은 실제 새 raw와 보존된 baseline을 읽어 작성했다. PNG와 PDF, 11개 CSV,
각 input/output hash는 `results/PLOT_DATA_MANIFEST.json`에 묶여 있다.

1. `figures/01_temperature_ionization_opacity`: T, xe, optical depth와 thermal contrasts.
2. `figures/02_signed_energy_transfer`: signed source, 누적 ledger와 energy residual.
3. `figures/03_signed_stress_branch_changes`: matter/radiation/total 및 branch/refinement 차이.

Root가 PNG를, reviewer가 PDF를 실제로 열어 확인했다. 최초 symlog 눈금 충돌과
범례 겹침은 표시만 수정했다. 수정 전 그림·코드·manifest를 `figures/v1/`와
`evidence/PLOT_V1_*`에 보존했고, 11개 CSV와 과학 input identity는 같았다.
해결 기록은 `evidence/VISUAL_FINDINGS.json`에 있다.

완료 계산을 재개할 때는 우선 `HANDOFF_KO.md`, `DAG.json`, `NEXT_DAG.json`과
receipt를 읽는다. `code/run.py --run`은 완료 source/config/artifact identity가
일치하면 cache를 재사용하고 partial/failed attempt를 자동 재실행하지 않는다.
현재 science를 다시 실행할 필요는 없다. `code/analyze.py`와 `code/run.py --plot`은
data-only 경로이며, 남은 결함이 없으므로 이 보고를 위해 반복하지 않았다.

## 8. 다음 물리 의존성과 유지 상태

N1은 Li의 final charge/state/energy partition provider다. 다음 0-ODE 작업은
에너지별 cross section, branching probability, Auger/secondary electron energy,
escaped photon energy, ionic-potential 변화의 단위·threshold·정규화·source identity를
한 contract에 묶는 것이다. Total cross section만으로 final charge를 추정해 넣지
않는다. 확보된 정확한 입력이 없으면 해당 channel을 활성화하지 않고
`MISSING_EXACT_INPUT`을 유지한다.

N2는 실제 anisotropic grey field의 spectrum을 제약하는 추가 moment/입력과,
그 spectrum에 일치하는 recoil·induced 및 radiation collision/backreaction의
구성이다. 현재의 external Planck reference나 passive energy debit으로 그
물리 의무를 닫지 않는다. 각 provider가 만족할 국소 number/charge/energy 및
수치 수용 기준을 먼저 고정한 뒤 영향받는 코드만 구현한다. 완료 cohort의 반복은
다음 단계의 선행 조건이 아니다.

**유지:** Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL;
CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED;
REI_activation=false. 이번 conditional thermal 단위의 수용과 이 상태들은
서로 다른 결론이다.
