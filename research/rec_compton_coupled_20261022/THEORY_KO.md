# Compton을 결합한 full63 기체 열방정식

## 1. 이번 유도의 결과와 적용 범위

이번 단위는 기존 광이온화·RR·DR 기체 열방정식에 Compton 에너지 교환을
결합한다. native full63 좌표와 원래 원자 수율을 유지하면서 추가 RHS를
마지막 logT 성분 하나로 정리할 수 있다. 추가 Jacobian도 한 행이며,
전자 비율이 0인 한계에서 나눗셈 특이점이 없는 형태로 계산한다.

전자·전체 입자 비율과 복사 모멘트를 잠시 고정한 Compton 부분 문제는
정확히 dT/dt = −A_C T + B_C가 된다. 이 지수 완화식은 부호·열용량·
미분·에너지 전달을 검산하는 해석적 기준이다. 실제 결합 계산은
온도 의존 원자율, 팽창, 전자수 및 현재 복사 상태를 함께 진화시키는
full63 BDF이며, 이 국소식을 실제 시간 적분 알고리즘으로 대체하지 않는다.

실행 범위와 사례는 [FROZEN_CONTRACT.md](FROZEN_CONTRACT.md)가 정한다.
본 P1 작업은 원문 확인, 직접 유도, 실제 Wolfram 검산과 구현 연결을
수행했으며 ODE와 과거 계산을 실행하지 않았다. 작성자는 본 이론의
저자이므로, 뒤의 독립 물리 검토는 다른 검토자가 수행해야 한다.

이전 atomic network에서 선택한 초기 neutron/tritium inventory는 정확히
0이고, 채택한 photo/RR/DR 연산자는 이를 생성하지 않는다. 이것은 선택한
원자망과 초기 상태의 성질이다. 실제 핵반응 생성률이 물리적으로 0이라는
주장이 아니다. 최근 REI의 DD 및 수동 핵반응망은 다른 원천·열화·결합
계약을 가지므로 이번 Compton 단위에 수입하지 않는다.

## 2. 변수, 단위와 기존 에너지 저장고

독립변수 x = ln(a/a_ref), 시간 미분 dx/dt = H, 온도 좌표 ℓ = ln T를 쓴다.
a는 평균 척도인자다. 원자 population은 baryon당 수분율 Y_i이며

$$
n_b\propto a^{-3},\qquad
X=\sum_iq_iY_i,\qquad
n_e=n_bX,\qquad
w_i=1+q_i,\qquad
\eta=\sum_iw_iY_i,\qquad n_g=n_b\eta .
\tag{1}
$$

여기서 n_g는 같은 T를 공유한다고 가정한 원자·이온·전자 전체 입자수다.
충돌 없는 massive matter와 광자는 이 기체 열용량에 넣지 않는다.
기존 단일 온도 및 빠른 전자–기체 에너지 재분배 가정을 계승한다.

이온화 에너지 사다리 I_i와 baryon당 기체 저장량은

$$
u_g=\frac32 k_BT\eta+\sum_i I_iY_i .
\tag{2}
$$

기존 원자 수 소스를 F_i = dY_i/dt, 입자 소스를
\(\dot\eta_0=\sum_iw_iF_i\), 기존 병진열 소스를 Q_0라 놓으면

$$
\frac{d\ln T}{dx}
=-2+\frac{2(Q_0+Q_C+Q_{\rm UV,C})/(3k_BTn_b)-\dot\eta_0}
              {H\eta}.
\tag{3}
$$

Compton 산란은 이번 근사에서 이온·전자 수를 바꾸지 않으므로 새로운
입자 소스는 0이다. 그러나 계산된 T가 원자율을 바꾸고, 그 원자망에서
계산한 n_e가 기존 Thomson opacity를 바꾸는 결합은 그대로 남는다.
등방 기체 압력의 평균 팽창 일은 3H n_g k_BT다.

양수 Q는 기체가 얻는 에너지다. 공통 상수

$$
K_C=\frac{\sigma_Tc}{m_ec^2}=\frac{\sigma_T}{m_ec}
\tag{4}
$$

의 SI 단위는 m³/(J s)다. 따라서 K_C U는 s⁻¹,
K_C n_e k_B T U는 W/m³이며 모든 추가 g = d lnT/dx 항은 무차원이다.
상수는 이전 [compton_budget.py](../rec_thermal_omitted_budget_20261022/code/compton_budget.py)
소유자를 그대로 따른다: c = 299792458 m/s,
k_B = 1.380649×10⁻²³ J/K, h = 6.62607015×10⁻³⁴ J s,
σ_T = 6.6524587051×10⁻²⁹ m², m_e = 9.1093837139×10⁻³¹ kg.
여기서 σ_T는 원래 Bianchi 소스와 같고, 별도 Planck 상수는
\(a_R=8\pi^5k_B^4/(15h^3c^3)\)이다.

## 3. 두 복사장 분기와 공통 UV 항

### 3.1 actual_hot: 현재 광자 에너지 모노폴

이번 부분은 비기울어진 국소 프레임의 등방 비상대론 Maxwellian 전자와
Thomson 광자에 대한 leading thermal Compton 모멘트다.
이전 원문 검증에서 사용한 Sazonov–Sunyaev의 각도별·각도 적분 kernel
모멘트가 그 출처다.[S1] 입사 광자장이 비등방이어도 이 열운동 항을
등방 전자에 대해 적분하면 광자 에너지의 방향 모노폴이 남는다.

$$
U_\gamma(x,y)=C_\gamma(x)E_{\gamma,0}(y),\qquad
C_\gamma(x)=\frac{\rho_{\rm crit,J}\Omega_\gamma}{a^4},
$$

$$
Q_{\rm hot}=-4K_Cn_ek_BT U_\gamma .
\tag{5}
$$

E_gamma,0는 0-based native state index 4의 현재 값이다. 이전 저장 궤적을
재생한 값이나 전체 photon+neutrino 에너지를 넣지 않는다.
복사장의 photon number·energy angular moments만으로 일반적인 recoil과
induced scattering 전체를 지정할 수 없으므로, 이 분기는 식 (5)의
식별 가능한 leading thermal 성분을 추가한다. Thomson 조건은 채택한
근사의 전제이며, 에너지 모노폴만으로 모든 미지의 고에너지 꼬리를
제한했다고 해석하지 않는다.

### 3.2 planck_reference: 별도로 지정한 등방 Planck bath

이 분기는 명시적으로

$$
T_r=\frac{2.7255\ {\rm K}}a,\qquad U_r=a_RT_r^4,\qquad
Q_{\rm P}=4K_Cn_ek_BU_r(T_r-T)
\tag{6}
$$

를 선택한다. T_r의 redshift 법칙과 U_r는 이 기준 bath의 소유물이다.
실제 Bianchi 광자의 스펙트럼을 추론하거나 그 에너지 정규화를 교체하는
절차가 아니다. 기준 bath를 Einstein 에너지 밀도에 추가하지 않는다.
기존 actual-U 정규화와 a_R의 미세한 상수 반올림 차이도 유지한다.

식 (6)은 등방 Planck 분포의 recoil·induced 항과 thermal 항을 합친
leading-order 순교환이다. 동일한 상태에서 두 후보의 차이는

$$
Q_{\rm P}-Q_{\rm hot}
=-4K_Cn_ek_BT(U_r-U_\gamma)+4K_Cn_ek_BU_rT_r .
\tag{7}
$$

첫 항은 bath 에너지 밀도 교체, 둘째는 Planck 기준의 recoil·induced
기여다. 이 차이 전체를 actual photon field의 오차막대로 붙이지 않는다.
각 궤적은 두 후보를 진단값으로 기록하되 선택한 한 분기만 RHS에 넣는다.

### 3.3 공통 외부 UV: 이미 지정된 71개 bin

원래 5–200 eV, 71개 bin의 photon number flux Φ_j는
등방 관례 Φ = c n_gamma를 따른다. 같은 bin 중심 에너지 ε_j와
처방된 UV 진폭을 사용해

$$
U_v=\sum_j\frac{\Phi_j\epsilon_j}{c},\qquad
M_v=\sum_j\frac{\Phi_j\epsilon_j^2}{c},\qquad
Q_{\rm UV,C}=K_Cn_e(M_v-4k_BT U_v)
\tag{8}
$$

를 계산한다. M_v의 단위는 J²/m³다. UV=1의 U_v와 M_v는 한 번 계산해
두고 매 RHS에서 기존 UV 진폭만 곱할 수 있다. 이는 선택한 bin 표현에
대해 정확하며, 연속 스펙트럼이나 새 bin으로 원래 원자 계산을 바꾸지 않는다.

이전 단위가 확인한 연속 power law 최대 점유수는 UV=1에서
6.0801643681×10⁻²⁰이고, ε_max/(m_e c²)는 3.9139023618×10⁻⁴다.
따라서 지정된 희박 UV에서 stimulated 항을 버린 식 (8)을 사용한다.
이 수치와 전제는 [기존 출처 기록](../rec_thermal_omitted_budget_20261022/provenance/SOURCES.json)을
재사용한다. M_v/(4k_BU_v) = 91741.68649 K는 이 UV의 Compton 기준 온도다.
UV=0이면 두 모멘트와 식 (8)은 함께 0이다.

## 4. 열용량을 적용한 계산식과 full63 Jacobian

앞으로 \(\mathcal B\)는 s⁻¹ 단위의 열항 bracket을 뜻한다.

$$
\mathcal B_{\rm h}=-\frac83K_CU_\gamma,\qquad
\mathcal B_{\rm P}=\frac83K_CU_r\left(\frac{T_r}{T}-1\right),\qquad
\mathcal B_v=\frac23K_C\left(\frac{M_v}{k_BT}-4U_v\right),
$$

$$
g_C=\frac{X}{H\eta}\left(\mathcal B_{\rm selected}+\mathcal B_v\right)
    =\frac{X\mathcal B}{H\eta}.
\tag{9}
$$

n_e/(n_b η) = X/η로 묶었기 때문에 추가 항에는 n_b가 명시적으로
남지 않는다. 고정 x에서 n_b는 상태변수에 의존하지도 않는다.
이 형태가 코드의 compton_logT_rhs에 해당한다.

기존 63×63 Jacobian에 추가되는 것은 0-based 행 62뿐이다.
원자 좌표는 y_(40+j) = Y_j/d_j이고 d_j는 기존 isotope scale다.
T, H, x와 복사 모멘트를 고정하고 식 (9)를 몫 미분하면

$$
\frac{\partial g_C}{\partial y_{40+j}}
=\frac{\mathcal B}{H}\,
 \frac{q_j\eta-Xw_j}{\eta^2}\,d_j .
\tag{10}
$$

X로 나누지 않으므로 X=0, η>0에서도 값이 유한하다. 이때 g_C 자체는
0이지만 전하를 추가하는 population 방향의 미분은 일반적으로 0이 아니다.
Compton의 photon-energy 모노폴 미분도 E_gamma,0로 나누지 않고 C_gamma를
직접 사용한다. 이 추가 식이 E_gamma,0=0에서 대수적으로 유한하다는 사실은
기존 full63 기하학의 양의 photon monopole 입력 조건을 없애지 않는다.

고정 x에서 \(h_k=\partial\ln H/\partial y_k\), k<40라 놓으면

$$
\frac{\partial g_C}{\partial y_k}
=-g_Ch_k
-\mathbf1_{\rm actual\_hot}\delta_{k4}
 \frac{8K_CXC_\gamma}{3H\eta}.
\tag{11}
$$

기존 [geometry.py](../rec_rei_hheli_sandbox_20261021/code/geometry.py)의
h_k에서 0이 아닌 성분은 다음과 같다.

$$
h_1=-\frac{3h_0^2\Pi_{\rm matter,norm}}{H^2},\quad
h_2=\frac{h_{\rm ref}^2y_2}{H^2},\quad
h_4=\frac{h_0^2\Omega_\gamma}{2H^2a^4},\quad
h_{22}=\frac{h_0^2\Omega_\nu}{2H^2a^4}.
\tag{12}
$$

여기서 h_0와 h_ref는 기존 소스의 Hubble 정규화 상수다.
neutrino 좌표의 식 (11) 기여는 H 분모를 통한 기하학적 효과이며
neutrino에 Compton 소스를 넣는 것이 아니다. 이 네 성분을 직접 조립하면
추가 열행 때문에 기존 40열 tangent 계산 전체를 다시 수행할 필요가 없다.

마지막 온도 좌표에 대해서는

$$
\frac{\partial g_C}{\partial\ell}
=\frac{X}{H\eta}
 \left[
 -\frac{2K_CM_v}{3k_BT}
 -\mathbf1_{\rm planck\_reference}\frac{8K_CU_rT_r}{3T}
 \right],
\qquad
\frac{\partial g_C}{\partial y_{61}}=0 .
\tag{13}
$$

actual-hot 자체는 Q_hot∝T인 반면 열용량 변환에 1/T가 있으므로
고정 조성·기하학에서 logT 미분이 정확히 0이다. 공통 UV recoil과
Planck intercept만 식 (13)의 역온도 미분을 만든다. 각 항의 명시적
x 의존성은 RHS 함수의 시간 의존성이며 상태 Jacobian에 추가하지 않는다.

전체 추가 행을 rᵀ라 하면

$$
J_{\rm new}=J_{\rm old}+e_{62}r^{\mathsf T}.
\tag{14}
$$

따라서 같은 현재 상태에서의 차이는 rank≤1이다. 이 사실은 조립 구조의
단순화이며 이전 궤적의 Jacobian이나 인수분해를 다른 상태에서 그대로
사용해도 된다는 뜻은 아니다. 기존 온도 의존 원자율의 62번째 열은
원래 thermal Jacobian 소유자가 계속 계산한다.

식 (9)–(13)은 H>0, η>0, T>0에서 signed population trial에도 매끄럽게
이어진다. Newton/유한차분 trial에 별도 전자율 clipping을 넣지 않는다.
물리적 부호·source 범위·정확한 n/T=0 조건은 초기 및 명시한 검사 상태에서
확인한다. off-manifold trial에 핵에너지 또는 음의 입자수 해석을 부여하지 않는다.

## 5. 정확한 국소 완화와 계산 단순화

Compton 부분만 떼어 조성 X/η와 bath 모멘트를 고정하면

$$
\left.\frac{dT}{dt}\right|_C=H T g_C=-A_C T+B_C,
\tag{15}
$$

$$
A_C=\frac{8K_CX}{3\eta}(U_{\rm selected}+U_v),\qquad
B_C=\frac{8K_CX}{3\eta}
 \left[\mathbf1_{\rm planck\_reference}U_rT_r+\frac{M_v}{4k_B}\right],
\tag{16}
$$

이며 U_selected는 actual_hot에서 U_gamma, planck_reference에서 U_r다.
A_C의 단위는 s⁻¹, B_C는 K/s다. 양의 물리적 상태에서 두 계수는
음이 아니다. A_C>0이면 T_* = B_C/A_C이고

$$
T(t+\Delta t)=T_*+(T(t)-T_*)e^{-A_C\Delta t}.
\tag{17}
$$

이는 integrating factor를 곱해 적분하면 바로 얻어진다. 식 (17)의
미분을 다시 식 (15)에 넣으면 잔차가 0이고 Δt=0에서 초기값을 회복한다.
T(t)>0, Δt≥0인 경우 T_*와 초기값의 양의 가중 평균이므로 양성을 유지한다.

A_C가 작은 경우에도 안정적인 동치 표현은

$$
T_{\rm new}=T_{\rm old}+(B_C-A_CT_{\rm old})\Delta t\,
 \phi_1(-A_C\Delta t),\qquad
\phi_1(z)=\frac{\operatorname{expm1}(z)}z,\quad \phi_1(0)=1 .
\tag{18}
$$

일반 affine 식의 A_C=0 연속 한계는 T_new = T_old+B_C Δt다.
현재 물리적 Compton 소스에서 X=0이면 A_C=B_C=0이며 T가 그대로다.
UV의 U_v=0이면 M_v=0이라는 기존 모멘트 조건도 함께 지킨다.
H까지 고정한 x 부분 문제에서는 Δt=Δx/H로 바꿀 수 있다.

식 (17)은 단일 bath의 의미도 분명히 한다. UV를 끈 actual_hot은
선택한 hot 성분만 있으므로 T_* = 0인 냉각 문제이고,
UV를 끈 Planck 분기는 T_* = T_r로 완화한다. actual_hot의 0은
실제 CMB와의 완전한 열평형 온도라는 뜻이 아니라 recoil을 공급하지 않은
해당 성분의 수학적 고정점이다. UV를 포함하면 식 (16)의 가중 기준
온도가 정해진다.

고정 조성·부피, 팽창을 제외한 이 부분 문제의 적분된 기체 열변화는
\(\Delta u_{\rm kin}=\frac32 k_B\eta(T_{\rm new}-T_{\rm old})\)이며 bath는
그 반대 에너지를 받는다. 이것이 pointwise source ledger와 별개의
해석적 검산 기준을 제공한다.

실제 계산의 H, X/η, 복사 모멘트 및 원자 Q_0는 계속 변한다. 특히
재결합 계수와 병진열 손실은 T에 의존한다. 그러므로 이 부분 해를
full63의 정확한 전체 시간 전진이나 즉시 열평형 조건으로 사용하지 않는다.
채택한 구현의 단순화는 UV 모멘트 사전 계산, 식 (9)의 스칼라 연산,
식 (10)–(13)의 해석적 행에 한정한다. 전체 문제의 BDF·정밀화 비교는
계약서의 별도 수치 의무다.

## 6. FLRW 기준식과 새 원문 교차 확인

새로 확인한 Scott–Moss의 arXiv:0902.3438v2 식 (1)–(2)는

$$
(1+z)\frac{dT_m}{dz}
=\frac{T_m-T_r}{H t_C}+2T_m,\qquad
t_C^{-1}=\frac{8\sigma_Ta_RT_r^4}{3m_ec}
          \frac{x_e^{(H)}}{1+f_{\rm He}+x_e^{(H)}} .
\tag{19}
$$

라는 형태다.[S3] 그 전자분율은 hydrogen nuclei로 정규화한다.
H/He 조성에서 \(X=x_e^{(H)}n_H/n_b\),
\(\eta=(1+f_{\rm He}+x_e^{(H)})n_H/n_b\)이므로 그 열용량 비율은
정확히 X/η다. 우리 식은 같은 입자수 원리를 native 동위원소·Li 좌표까지
직접 적용한다. 별도의 근사 mean molecular weight를 끼우지 않는다.

dz/dt = −(1+z)H를 적용하면 식 (19)의 Compton 부분은
\((8K_CU_rX/3\eta)(T_r-T)\)이고, adiabatic 부분은 −2HT다.
이는 UV=0인 식 (3), (6)의 해당 두 소스와 일치한다.
다른 원자 가열·냉각·입자수 항을 그 논문에서 가져와 교체하지 않는다.

T=T_r에서는 Compton 순항이 0이다. 팽창하는 전체 방정식의 정지해라는
뜻은 아니다. 유한한 결합률에서 T_r∝a⁻¹을 따라가려면 팽창 냉각과
맞서는 온도차가 생긴다. Scott–Moss의 초기 tight-coupling 근사나
RECFAST의 전환 알고리즘은 이번 가열된 z≈8→2 pilot에 채택하지 않는다.
T=T_r 항등식은 Compton 소스의 대수적 검사이며, 이 구간의 낮은 T_r를
기존 원자율의 허용 온도 구간으로 확대하지 않는다.

Exa로 새로 확인한 Seager–Sasselov–Scott 1999의 원래 RECFAST 논문도
§3에서 물질 온도의 adiabatic·Compton 항을 함께 풀도록 제시한다.[S2]
이 비교에서 가져온 것은 열용량·계수·부호다. 논문 고유의 재결합 처방,
case-B 계수, cosmological parameter와 T_0 값은 현재 소스를 대체하지 않는다.

## 7. 국소 에너지 원장과 test-fluid 소유권

원래 photo/RR/DR 소스는

$$
Q_0+n_b\,I\!\cdot F=Q_{\rm abs}-Q_{\rm esc}
\tag{20}
$$

를 만족한다. Li core escape, recombination binding escape 및 병진열
탈출은 기존 소유권을 유지한다. 새 기체 source를 kinetic+binding으로
독립 조립하고, 원장을 다음과 같이 정의한다.

$$
\begin{aligned}
Q_{\rm gas}&=Q_0+Q_C+Q_{\rm UV,C}+n_b I\!\cdot F,\\
Q_{\rm C,bath}&=-Q_C,\\
Q_{\rm UV,bath}&=-Q_{\rm abs}-Q_{\rm UV,C},\\
Q_{\rm escaped}&=Q_{\rm esc}.
\end{aligned}
\tag{21}
$$

식 (20)을 사용하면 네 소스의 합은 0이다. source 검사는 같은 숫자를
반대 부호로 적는 것만으로 끝내지 않고, kinetic+binding에서 얻은
Q_gas와 radiation partition에서 얻은
\(Q_{\rm abs}-Q_{\rm esc}+Q_C+Q_{\rm UV,C}\)를 대조해야 한다.

식 (2)와 입자수 변화를 미분하면 적분할 기체 에너지 식은

$$
\frac{du_g}{dx}
=\frac{Q_{\rm abs}-Q_{\rm esc}+Q_C+Q_{\rm UV,C}}{n_bH}
 -3k_BT\eta .
\tag{22}
$$

코드의 gas_energy_source_J_per_baryon_per_x는 첫 항,
work_J_per_baryon_per_x는 마지막 항의 양의 크기다.
bath_minus_escape가 기존의 Q_gas−Q_abs를 뜻한다면 그 값은
Q_C+Q_UV,C−Q_esc다. 이번 adapter의 external_bath_W_m3 필드는
명시적으로 모델링한 총 Compton 기체 입력 Q_C+Q_UV,C를 기록한다.
새 원장에서 반대 bath 소스의 부호와 구별한다.

선택한 test-fluid 가정에서는 식 (21)의 bath 항을 photon hierarchy나
Einstein 방정식에 넣지 않는다. 새 전자수에 의한 기존 elastic opacity의
변화는 유지되지만 Compton 에너지 역반응은 동적으로 적용하지 않는다.
따라서 국소 원장 합이 0이라는 사실만으로 복사 스펙트럼과 Einstein
계까지 완전히 에너지 보존하는 결합계가 된 것은 아니다. 적분 원장에도
복사장의 anisotropic work와 redshift를 추가 진화하지 않는다.

\(|Q_C|/(HU_\gamma)\), 그 x 적분 및 기존 trace-energy 비율은
이 가정의 에너지 교환 규모를 판단할 자료다. 자동적인 엄밀 오차 상한이나
새로운 임의 승격 기준으로 사용하지 않는다. 관측된 크기와 finite
정밀화 결과가 후속 radiation-coupled 계약의 필요성을 판단하게 한다.

## 8. 실제 기호 검산과 구현 연결

[evidence/WOLFRAM_COUPLING.json](evidence/WOLFRAM_COUPLING.json)에 실제
제출한 Wolfram 코드와 반환 응답을 보존했다. source→g, 조성·기하학·logT
미분, 중성 한계, affine 식·초기값·A→0 한계, 계수·완화 가중치 부호,
기체/bath 원장, 가변 입자수 caloric 식, hydrogen↔baryon 정규화,
FLRW 계수와 redshift 부호의 26개 반환 검사는 모두 0 또는 true였다.
이는 직접 미분·대입 유도와 일치한다.

평가기는 Power::infy·Infinity::indet 경고도 반환했다. 한 번의 제한된
진단에서 A→0 limit, 같은 전개의 상수항, 중성 limit은 모두 0의 잔차를
반환했으나 경고의 내부 발생 지점을 특정하지는 못했다.
두 응답을 그대로 남기며 경고 없는 실행이라고 기록하지 않는다.
수학적 식은 η,H,T>0에서 사용하고 A=0은 식 (18)의 연속 가지로 정의한다.
WolframContext 호출은 internal error였고 LanguageEvaluator 호출은
실제로 수행됐다. CAS는 독립 물리 검토나 ODE 실행 증거가 아니다.

| 유도 | 구현 대상 | 확인할 실제 동작 |
|---|---|---|
| (5)–(8) | 기존 compton_budget.py 및 새 _compton_state/compton_terms | 원래 상수·현재 photon index4·exclusive branch·동일 UV |
| (9) | ComptonFull63.compton_logT_rhs/rhs | 행62에만 추가; 다른 수·기하학 RHS 식 보존 |
| (10)–(14) | ComptonFull63.compton_jacobian_row/jac | isotope scale, H gradient, 직접 E0 열, tau=0, 중성 한계 |
| (15)–(18) | 국소 해석적 검산 기준 | 부호·열용량·완화/초기값·연속 한계; 실제 solver로 채택하지 않음 |
| (20)–(22) | ComptonFull63.sample/thermal_diagnostics/diagnostics 및 runner | 독립 gas source, 반대 bath, work 포함 적분, 진단 필드 소유권 |

구현 파일은 [code/compton_system.py](code/compton_system.py)이며 원래
[thermal_system.py](../rec_thermal_moments_20261022/code/thermal_system.py)를
상속한다. 이론 작성 중 해당 adapter를 읽어 식–함수 대응을 확인했다.
이것은 저자와 분리된 구현/결과 검토로 세지 않는다. 전체 63열 및
선택 방향 Jacobian 검사, 초기·저장/accepted 상태 admission, 513/1025
진단 배열, 8개 bounded IVP와 비교는 P2–P4의 별도 실행 근거를 따른다.

## 출처와 버전

[S1] S. Y. Sazonov & R. A. Sunyaev (2000),
The profile of a narrow line after single scattering by Maxwellian electrons:
relativistic corrections to the kernel of the integral kinetic equation,
ApJ 543, 28–55, DOI [10.1086/317078](https://doi.org/10.1086/317078).
[arXiv:astro-ph/9910280v3](https://arxiv.org/abs/astro-ph/9910280v3),
2000-09-14 수정본. 기존 단위에서 확인한 식 (18), (25) 및
Kompaneets 식 (6)을 그 적용 범위와 함께 재사용했다.

[S2] S. Seager, D. D. Sasselov & D. Scott (1999),
A New Calculation of the Recombination Epoch, ApJ 523, L1–L5,
DOI [10.1086/312250](https://doi.org/10.1086/312250).
[출판사 원문](https://iopscience.iop.org/article/10.1086/312250/fulltext/995324.text.html),
[arXiv:astro-ph/9909275v2](https://arxiv.org/abs/astro-ph/9909275v2),
1999-09-16 수정본. Exa 검색·본문 fetch와 arXiv metadata를 새로 확인했다.
publisher §3의 matter-temperature equation은 본문에서 식 (5)로 불린다.
HTML 변환본의 식 번호 불일치 때문에 정확한 식 (19)의 표시는 [S3]에서
직접 확인했다. arXiv v2 PDF의 한 web-open 시도는 DisabledError였다.

[S3] D. Scott & A. Moss (2009), arXiv metadata 제목
Matter temperature after cosmological recombination; PDF 제목은
Matter temperature during cosmological recombination.
[arXiv:0902.3438v2](https://arxiv.org/abs/0902.3438v2),
[원문 PDF](https://arxiv.org/pdf/0902.3438v2), 2009-04-21 수정본,
DOI [10.1111/j.1365-2966.2009.14939.x](https://doi.org/10.1111/j.1365-2966.2009.14939.x).
PDF 첫 페이지의 식 (1)–(2)를 직접 확인했다. SciSpace discovery의 2022
표시는 repository ingest metadata로 보이며 원문 출판년으로 채택하지
않았다. PDF의 후대 typesetting 날짜 역시 수정본 날짜와 구별했다.

출처별 재사용 범위, 실제 도구 호출과 선택한 응답, 코드 소유자 해시는
[provenance/COMPTON_SOURCES.json](provenance/COMPTON_SOURCES.json)에 있다.
긴 원문 인용과 논문 전체 재배포는 포함하지 않는다.

