# 저장된 여덟 궤적의 누락 열과정 예산

## 1. 이 단위가 계산하는 양

이 단위는 REC thermal moments의 완료된 full63 궤적 8개, 각 109개 저장점을 재사용한다. 구간은 실제 재시작점 \(z=7.963732801243163\)부터 \(z=2\)까지다. 원래 \(z=20\)부터 누적된 시간과 광학깊이의 초기값은 계승되지만, 이 문서의 새 적분은 재시작점에서 시작한다. 새 배경·화학·열 ODE를 풀지 않는다.

질문은 “현재 궤적에서 빠진 과정의 순간 소스와 누적 강제항이 얼마나 되는가”다. 계산 대상은 실제 Bianchi 광자 에너지에 대한 hot-electron inverse Compton 항, 별도의 등방 Planck 기준선, 기존 UV장의 leading-order Compton 교환, H/He 충돌 이온화(CI), H I/He II 충돌 여기(CE)다. 이 항들을 포함한 새로운 온도·이온화 궤적이나 전체 누락오차의 상한을 계산하는 것은 아니다.

본 문서는 물리 담당자가 원문과 기존 코드의 정의를 대조하고 유도해 작성했다. 이후 다른 담당자가 작성한 구현과 결과를 검토할 수 있으나, 저자가 이 문서를 작성한 사실 자체를 독립 이론 검증으로 세지 않는다. 원문, 실제 읽은 PDF의 해시, 원문 위치, 기존 코드 소유권은 [SOURCES.json](provenance/SOURCES.json)에 기록한다. 논문 전문은 연구 단위에 재배포하지 않는다.

## 2. 공통 장부와 온도 강제항

부호는 gas가 얻는 에너지를 양으로 잡는다. 계량 부호는 \((-+++)\), \(x=\ln(a/a_{\rm ref})\), \(dx/dt=H\)다. 모든 밀도는 proper SI 밀도다. 각 원자·이온 수를 baryon 수로 나눈 \(Y_i\), 이온 전하 \(q_i\), 누적 이온화에너지 \(I_i\)를 사용한다.

\[
n_b\propto a^{-3},\qquad n_e=n_b\sum_iq_iY_i,\qquad
\eta=\sum_i(1+q_i)Y_i,\qquad n_g=n_b\eta .
\tag{1}
\]

여기서 \(\eta\)는 원자핵/원자 입자와 자유전자를 합친 gas 입자수다. 현재 neutron/tritium inventory는 정확히 0이다. 기체는 비기울어진 국소 tetrad에서 공통 Maxwellian 온도 \(T\)를 가진다. 병진에너지와 전자 결합 저장고는

\[
u_{\rm kin}/n_b=\frac32k_BT\eta,\qquad
u_{\rm ion}/n_b=I\cdot Y .
\tag{2}
\]

단위부피당 병진에너지 소스 \(Q_{\rm kin}\)에 대해

\[
\frac{d\ln T}{dx}
=-2+\frac{2Q_{\rm kin}}{3k_BTn_bH\eta}
 -\frac{\dot\eta}{H\eta}.
\tag{3}
\]

따라서 저장된 \(Y,T,n_b,H\)를 고정한 새 과정의 직접 강제항은

\[
\delta g(x)\equiv\delta\!\left(\frac{d\ln T}{dx}\right)_{\rm fixed\ path}
=\frac{2\,\delta Q_{\rm kin}}{3k_BTn_bH\eta}
 -\frac{\delta\dot\eta}{H\eta}.
\tag{4}
\]

\(\int\delta g\,dx\)는 무차원 고정 경로 강제항이다. 이를 \(\Delta\ln T\) 또는 \(T_{\rm old}\exp(\int\delta g\,dx)\)라는 예측으로 바꾸지 않는다. 실제 \(T,Y,n_e\)가 변하면 기존 photo/RR/DR 소스와 새 소스도 변하고, opacity를 통한 기존 방사·기하 결합도 달라지기 때문이다. \(-2\)는 이 단위에서 추가되는 항이 아니므로 새 강제항 적분에 다시 넣지 않는다.

에너지 예산은 별도로

\[
\mathcal E_Q=\frac{1}{1\,{\rm eV}}\int_{x_0}^{x_1}
 \frac{Q(x)}{n_b(x)H(x)}\,dx
\tag{5}
\]

를 계산한다. 이는 eV/baryon 단위이며, 병진열 손실·결합 저장·광자 방출을 구별해야 한다.

## 3. H/He 충돌 이온화: 계수와 에너지 소유권

Hui–Gnedin의 Appendix A, PDF 인쇄면 27, 29–30의 CI fit을 채택한다. 해당 문헌이 제시한 정확도 범위는 세 채널 모두 \(10^4\le T/{\rm K}\le10^9\), 약 3%다. 이 숫자는 원 fit의 평가이며 현재 전체 모형의 오차막대가 아니다. [HG97 원문](https://arxiv.org/pdf/astro-ph/9612232v1)

\(t=T/(1\,{\rm K})\), \(\lambda_j=2T_j^{\rm rate}/T\)로 두면 원래 CGS 계수는

\[
C_j^{\rm cgs}
= A_j t^{-3/2}e^{-\lambda_j/2}
 \frac{\lambda_j^{p_j}}
 {[1+(\lambda_j/b_j)^{d_j}]^{f_j}}
\quad[{\rm cm^3\,s^{-1}}].
\tag{6}
\]

| 초기 상태 | \(T_j^{\rm rate}\) (K) | \(A_j\) | \(p_j\) | \(b_j\) | \(d_j\) | \(f_j\) |
|---|---:|---:|---:|---:|---:|---:|
| H I | 157807 | 21.11 | −1.089 | 0.354 | 0.874 | 1.101 |
| He I | 285335 | 32.38 | −1.146 | 0.416 | 0.987 | 1.056 |
| He II | 631515 | 19.95 | −1.089 | 0.553 | 0.735 | 1.275 |

SI에서는 \(C_j=10^{-6}C_j^{\rm cgs}\ {\rm m^3\,s^{-1}}\)다. 원문 계수의 \(K^{3/2}T^{-3/2}\)를 식 (6)의 무차원 \(t^{-3/2}\)로 썼다. H1/D/T 및 He3/He4에 대한 동일 전자계수 사용은 기존 ElementalElectronicEquality 가정을 계승한다.

초기 상태 \(i\)가 \(i+1\)로 이온화되는 사건의 baryon당 rate와 화학 소스는

\[
r_i=n_e C_i(T)Y_i,\qquad
F_{\rm CI}=\sum_i r_i(e_{i+1}-e_i),\qquad
\delta\dot\eta=(1+q)\cdot F_{\rm CI}=\sum_i r_i .
\tag{7}
\]

이는 자유전자를 사건당 하나 추가한다. 핵종별 원자핵 수와 baryon 수는 보존한다. 자유전자가 충돌 상대이므로 반응 rate에 \(n_e\)가 한 번 들어가고, 단위부피당 사건수에는 추가로 \(n_b\)가 들어간다.

이온화에너지 \(\chi_i=I_{i+1}-I_i\)는 기존 atomic_network.py의 결합 저장고가 소유한다. HG97의 rate threshold를 새 결합에너지로 덮어쓰지 않는다.

| 채널 | \(k_BT_j^{\rm rate}\) (eV) | 기존 \(\chi_j\) (eV) | \(\chi/(k_BT^{\rm rate})-1\) |
|---|---:|---:|---:|
| H I | 13.598755101 | 13.60 | \(9.1545\times10^{-5}\) |
| He I | 24.588267864 | 24.59 | \(7.0446\times10^{-5}\) |
| He II | 54.419752150 | 54.42 | \(4.5544\times10^{-6}\) |

이 작은 차이는 rate fit의 에너지 관례와 기존 저장고의 관례 사이 차이다. rate의 \(\lambda\)에는 원문 값을, 에너지 이동에는 동일한 기존 \(\chi\)를 써서 장부를 닫는다.

\[
Q_{\rm CI,kin}=-n_b\sum_i\chi_i r_i,\qquad
Q_{\rm CI,bind}=n_b I\cdot F_{\rm CI}
               =n_b\sum_i\chi_i r_i .
\tag{8}
\]

따라서 \(Q_{\rm CI,kin}+Q_{\rm CI,bind}=0\)이다. CI 순간에 잃는 병진열은 결합 저장고로 이동한다. 이를 총 gas 에너지의 방사 냉각으로 세거나, 두 항을 모두 독립 손실로 더하면 이중 계산이다. 후속 재결합 방출은 별개의 사건이며 여기서 미래 재결합을 가정해 추가하지 않는다.

식 (4)에 넣으면

\[
\delta g_{\rm CI}
=-\frac{1}{H\eta}\sum_i r_i
 \left(1+\frac{2\chi_i}{3k_BT}\right).
\tag{9}
\]

괄호의 1은 새 전자의 병진 자유도가 증가하는 효과다. 임계에너지 냉각만 넣으면 이 항이 빠진다. \(\int r_i/H\,dx\)는 현재 경로의 사건수/baryon 진단이며 새로운 최종 이온 분율이 아니다.

## 4. 충돌 여기와 지원 범위

HG97 Appendix A PDF 인쇄면 30의 두 에너지 계수는 다음과 같다.

\[
\Lambda_{\rm HI}^{\rm cgs}
=7.5\times10^{-19}
 \frac{\exp[-0.75\lambda_{\rm HI}/2]}
 {1+\sqrt{T/(10^5{\rm K})}},
\tag{10}
\]

\[
\Lambda_{\rm HeII}^{\rm cgs}
=5.54\times10^{-17}
 \left(\frac{1\,{\rm K}}{T}\right)^{0.397}
 \frac{\exp[-0.75\lambda_{\rm HeII}/2]}
 {1+\sqrt{T/(10^5{\rm K})}} .
\tag{11}
\]

단위는 \({\rm erg\,cm^3\,s^{-1}}\), SI 변환은 \(10^{-13}\ {\rm J\,m^3\,s^{-1}}\)다. 원문은 Black/Cen의 선여기 계수에 대한 약 10% 범위를 \(5\times10^3\)–\(5\times10^5\) K로 제시한다. [HG97 Appendix A](https://arxiv.org/pdf/astro-ph/9612232v1)

낮은 밀도의 ground-state 공급과 prompt radiative escape를 가정하면

\[
Q_{\rm CE,kin}=-n_en_b\sum_iY_i\Lambda_i(T),\qquad
Q_{\rm CE,escape}=-Q_{\rm CE,kin},\qquad F_{\rm CE}=0 .
\tag{12}
\]

이 경우 cascade 종료 후 이온 전하와 ground-state 결합 저장고가 변하지 않는다. 광자가 재흡수되거나 metastable population을 독립 상태로 다루면 식 (12)를 그대로 완결된 열소스로 쓸 수 없다.

이 공급자는 He I CE나 metastable closure를 제공하지 않는다. 다른 코드의 He I로 표시된 냉각식을 근거 없이 \(n_en_{\rm HeI}\)의 두 입자 과정으로 복사하지 않는다. Li CI/CE도 이 단위의 공급 범위 밖이다. 기존 Li CI 표의 최소 에너지 1/4/5 eV와 현재 \(k_BT\simeq0.0932\)–1.2217 eV를 비교하면, 모든 Li 채널을 현재 경로에 그대로 적용할 수 없다. 일부 Li I 점이 겹친다는 사실도 전체 Li 공급을 확보했다는 뜻이 아니다.

### 정확도 구간과 analytic continuation을 분리하는 방법

세 CI fit과 두 CE fit은 \(T>0\)에서 분석식으로 평가할 수 있지만, 원문이 검증한 온도 구간과 함수의 수학적 정의역은 다르다. 모든 저장점에서 원식의 값을 평가하고 source-domain mask를 함께 저장한다. 구간 밖의 값을 물리적으로 0으로 잘라내지 않는다. 미공급 채널, 구간 밖 continuation, 실제 부동소수 underflow는 서로 다른 상태다.

현재 8개 모두 109점 중 CI 구간 아래에 10점, CE 구간 아래에 3점이 있다. 적분의 supported 부분에는 양 끝점이 정확도 구간에 들어가는 저장 구간만 포함한다. 나머지는 continuation/boundary contribution으로 따로 합산한다. 이는 저장 격자 구간 분류이며 두 점 사이 연속 궤적의 추가 검증이 아니다. 채택식에서 continuation 기여가 작게 나오더라도 구간 밖 실험적 정확도가 새로 입증되는 것은 아니다.

## 5. 실제 Bianchi 광자장의 Compton 항

기존 geometry는 광자의 energy multipoles \(E_{\gamma,\ell}\)와 number multipoles \(N_{\gamma,\ell}\)를 각각 \(\ell\le8\)까지 저장한다. neutrino 블록은 별도다. photon source가 가진 \(T_0=2.7255\) K는 초기 에너지 정규화에 쓰이며

\[
U_\gamma(x)
=\rho_{\rm crit,J}\,\Omega_\gamma
  \frac{E_{\gamma,0}(x)}{a^4}
=a_R T_0^4\frac{E_{\gamma,0}(x)}{a^4},\qquad
a_R=\frac{4\sigma_{\rm SB}}c .
\tag{13}
\]

저장 raw_state의 4번 좌표가 \(E_{\gamma,0}\)다. 전체 radiation 밀도에 neutrino를 섞어 넣지 않는다. 현재 Thomson 연산자는 탄성이고 광자 에너지 소스는 없다. 기하의 shear work 때문에 \(E_{\gamma,0}\)는 일반적으로 1이 아니다. 실제 저장 범위는 약 0.9990427–1.0123976이다.

비상대론 Maxwellian 전자, 국소 bulk velocity 0, \(k_BT\ll m_ec^2\), \(E\ll m_ec^2\)일 때 Sazonov–Sunyaev의 산란 kernel moment는 leading order에서

\[
\langle\Delta E\rangle
=\frac{E}{m_ec^2}(4k_BT-E).
\tag{14}
\]

원문의 방향별 식 (18)에서 leading angular factor는
\(3(1-\mu)(1+\mu^2)/8\)이고, \(-1\le\mu\le1\) 적분은 1이다. 등방 전자분포에 대한 회전 대칭 때문에 각 입사 방향에 대한 총 에너지 이동은 같은 계수다. 따라서 입사 광자장이 비등방이어도, spontaneous scattering의 방향 적분은 에너지 모노폴로 수행된다. [SS2000, 식 (18), (25)](https://arxiv.org/pdf/astro-ph/9910280v3)

그중 식별 가능한 hot-electron 항은

\[
Q_{\gamma,\rm hot}
=-\frac{4\sigma_Tc\,n_e k_BT}{m_ec^2}U_\gamma .
\tag{15}
\]

이는 채택한 leading-order Thomson 근사 안에서 실제 \(U_\gamma\)로 결정되는 항이다. 모든 상대론 차수에서 정확한 식이나 완전한 CMB 순교환율이라고 부르지 않는다. CI와 달리 \(F=0\), \(\delta\dot\eta=0\)이므로 식 (4)의 에너지 항만 남는다.

완전한 순교환에는 recoil과 induced scattering이 필요하다. 낮은 점유수의 spontaneous recoil만으로도 추가 모멘트

\[
M_1=\int E\,u_E\,dE
\tag{16}
\]

가 필요하며 \(Q_{\rm recoil}=\sigma_Tc n_e M_1/(m_ec^2)\)다. 에너지·수 모노폴 둘만으로는 \(M_1\)가 정해지지 않는다. 예를 들어 같은 광자수와 평균 에너지를 가진 단색 분포와 대칭 두 에너지 분포는 에너지의 제곱 평균이 다르다. 이는 현재 저장 상태가 제공하는 정보의 범위에 관한 설명이지, 추가 스펙트럼 공급을 금지하는 정리가 아니다.

등방 occupation \(n(E)\)에 대해서는 Kompaneets 식 (SS2000 식 (6))을 에너지 적분하면

\[
Q_{\rm gas}
=\frac{\sigma_Tc n_e}{m_ec^2}\frac{8\pi}{h^3c^3}
\left[\int E^4 n(1+n)\,dE-4k_BT\int E^3n\,dE\right].
\tag{17}
\]

첫 적분에는 유도 산란이 포함된다. 일반 비등방장의 경우 원문 식 (2)의 서로 다른 입사·출사 방향 occupation이 필요하다. 주파수 적분된 \(E_\ell,N_\ell\)에 등방식의 \(n^2\)를 임의로 대입하지 않는다.

### 별도의 Planck 기준 비교

비교용으로만

\[
T_{\rm ref}=\frac{T_0}{a},\quad U_{\rm ref}=a_RT_{\rm ref}^4,\quad
Q_{\rm Planck,ref}
=\frac{4\sigma_Tc n_e k_BU_{\rm ref}}{m_ec^2}
 (T_{\rm ref}-T)
\tag{18}
\]

를 계산한다. Planck 분포의 \(\int E^4n(1+n)dE=4k_BT_{\rm ref}\int E^3n\,dE\) 관계로부터 얻는다. 식 (18)은 동일한 gas 궤적에 가정한 등방 Planck장의 비교이며, 식 (13)의 비등방 광자장이나 그 recoil을 복원한 결과가 아니다. 두 Compton 곡선을 동시에 총합에 더하지 않는다. \(U_\gamma\)를 \(U_{\rm ref}\)로 교체하는 것도 기본 hot 항의 정의를 바꾼다.

## 6. 외부 UV장의 별도 Compton 교환

기존 atomic_model은 외부 UV를 등방적인 local number flux로 정의하며 \(\Phi=c\,n_\gamma\) 관례를 명시한다. 채택 범위는 5–200 eV이고 실제 71개 bin의 \(\Phi_j\)와 중심 에너지 \(E_j\)를 그대로 재사용한다.

\[
U_{\rm UV}=\frac1c\sum_j\Phi_jE_j,\qquad
M_{\rm UV}=\frac1c\sum_j\Phi_jE_j^2,\qquad
Q_{\rm UV,C}=\frac{\sigma_Tc n_e}{m_ec^2}
 (M_{\rm UV}-4k_BT U_{\rm UV}).
\tag{19}
\]

UV recoil 가열과 thermal inverse Compton 손실은 저장하는 \(U_{\rm UV},M_{\rm UV},n_e,T\)에서 각각 복원할 수 있고, 순교환은 별도 소스 열로 보관한다. 이는 photoabsorption과 다른 산란 사건이다. UV bath는 기존의 prescribed optically-thin 공급이며 이 후처리에서 attenuation을 새로 풀지 않는다.

원래 연속 수 스펙트럼을 \(\epsilon=E/(1\,{\rm eV})\),
\(d\Phi/d\epsilon=\mathcal N\,\epsilon^{-2.5}\)로 쓰면
\(\mathcal N=3.3592465992832745\times10^{11}\ {\rm m^{-2}s^{-1}}\)이다. 등방 photon occupation은

\[
n_{\rm UV}(E)
=\frac{h^3c^2}{8\pi E^2}\frac{d\Phi}{dE}.
\tag{20}
\]

기존 source의 UV amplitude가 1일 때 최대값은 하한 5 eV에서
\(6.0801643681\times10^{-20}\)다. 저장 amplitude 최대는 0.99999627336으로 그보다 작다. 따라서 채택된 UV 스펙트럼 자체의 stimulated correction은 이 비교에서 무시할 수 있다. 미공급 다른 광자 스펙트럼의 occupation을 이 계산으로 알아낸 것은 아니다.

같은 bin 규칙으로 amplitude 1에서

\[
U_{\rm UV}=1.35220315295\times10^{-16}\ {\rm J\,m^{-3}},\qquad
M_{\rm UV}=6.85096798098\times10^{-34}\ {\rm J^2\,m^{-3}},
\]

\[
T_{\rm C,UV}\equiv \frac{M_{\rm UV}}{4k_BU_{\rm UV}}
=91741.68649\ {\rm K}.
\tag{21}
\]

따라서 현재 저장 \(T=1081.32\)–14177.03 K에서는 식 (19)가 가열이다. 실제 스펙트럼은 에너지 bin의 단색 모음이라는 새 물리 주장이 아니라, 기존 photo model이 채택한 유한 quadrature로 평가한다. 동일 power law의 연속 적분과 비교한 \(U,M\)의 상대 차이는 각각 \(2.5798\times10^{-4}\), \(2.5706\times10^{-4}\)다. 이 차이를 숨기기 위해 photo 쪽 스펙트럼 규칙을 바꾸지 않는다.

최대 photon energy 비는 \(E_{\max}/m_ec^2=3.91390\times10^{-4}\), 저장 전자온도 비는 \(k_BT/m_ec^2\le2.39078\times10^{-6}\)다. 식 (19)의 근사 차수와 이 무차원 수를 보고하되, 이 숫자 자체를 순교환의 엄밀한 상대오차 상한으로 해석하지 않는다.

## 7. 합산·수치 적분·검증 범위

기본 kinetic budget의 공급 성분은
\(Q_{\gamma,\rm hot}+Q_{\rm UV,C}+Q_{\rm CI,kin}+Q_{\rm CE,kin}\)다.
기본 total-gas source에는 CI binding 증가를 함께 넣으므로 CI가 상쇄된다.
Planck-reference 값은 기본 hot 항과 대체 비교한다. source별 signed integral과 absolute contribution을 모두 남겨 상쇄를 숨기지 않는다. 기존 photo/RR/DR 및 팽창 work와의 비율은 단위와 에너지 장부가 같은 양끼리 비교한다.

일차 적분은 원래 109개 점의 양의 가중치 composite trapezoid다. 55점 coarsening과 109점 Simpson은 보조 격자 진단이다. 이 차이는 저장 격자 적분의 민감도를 보여 주며, 존재하지 않는 dense output이나 연속 시간의 검증을 대신하지 않는다. supported 구간 합과 continuation/boundary 합은 합쳐서 전체 trapezoid를 정확히 재현해야 한다.

여러 성분을 합친 예산의 공통 support mask는 해당 합에 필요한 fit 구간의 교집합이다. 이 마스크 밖에서 CI fit을 continuation했다는 사실은 같은 구간의 식 (15) Compton 성분까지 구간 밖 계수로 바뀐다는 뜻이 아니다. 개별 과정의 support와 기여를 먼저 읽는다.

상태를 다른 RR closure 또는 기존 nominal/refined 궤적으로 바꿔 예산의 민감도를 비교할 수 있다. 이는 해당 여덟 궤적 사이의 비교이고 확률적 불확실성이나 전체 모형오차가 아니다. 특히 누락 과정이 크면 새 결합계의 필요성을 판단할 근거가 되지만, 이 단위에서 이미 그 새 계를 풀었다고 말하지 않는다.

| 식·소유권 | 구현 대상 | 핵심 검증 |
|---|---|---|
| (6)–(12), CI/CE 원문 계수·isotope map | code/collisional_budget.py | SI 변환, domain/continuation, 핵종 보존, 전하·입자수, kinetic+binding=0 |
| (13)–(21), photon/UV moment | code/compton_budget.py | photon만 사용, 실제 모노폴, Planck equilibrium, UV 부호·occupation, 0밀도 극한 |
| (4)–(5), 지원 구간 적분·비교 | code/postprocess_omitted.py | 입력 SHA, particle term, 109점 적분, 지원/경계 합, 배열 저장 |

현재 baryon 열·전자 결합·외부 UV 에너지는 test-fluid 진단이다. 고정 궤적 후처리는 기존 photon hierarchy나 Einstein 방정식에 새 에너지를 넣지 않는다. 향후 에너지 보존을 포함한 결합계라면 gas의 Compton 소스에 반대인 photon 에너지 소스와 필요한 angular/spectral 연산자를 함께 공급해야 한다. 지금 계산한 숫자만으로 이를 완료했다고 할 수 없다.

He I CE/metastable, Li CI/CE, free-free, charge exchange, secondary electrons, 여러 전자 photoionization, 복사수송, 핵 반응/붕괴 에너지 등은 이 유한 예산의 밖에 남는다. 기존 공통 \(T\), prompt escape, 전자계수의 isotope equality와 early-prefix 계승도 유지된다. 완료된 계산 범위와 별개로 Physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, U5 CLOSED_HOLD_NOT_RESET, REI_activation=false는 유지된다.
