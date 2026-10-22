# REC thermal moments: 온도 방정식과 원자 에너지 소유권

이 단위는 REC PR119의 저장된 상태를 초기값으로 사용하여, **기존 광이온화·재결합 수반응률을 유지한 채 온도를 새로운 동역학 변수로 닫는다.** 이전 계산의 처방 온도를 자체 일관된 열 이력으로 바꾸었다고 주장하지 않는다. 새 적분은 저장된 노드 $z=7.963732801243163$에서 시작하며, 그보다 이른 $z=20$부터의 상태와 누적 시간·광학깊이는 기존 결과를 계승한다.

주 RR 열손실은 Mao, Kaastra & Badnell (2017)의 전자 에너지 손실 인자와 기존 수반응률을 곱한 **Mao-factor hybrid**이다. 별도의 대안은 기존 수반응률 피팅식을 미분하여 얻는 열손실이다. 두 모델은 동일한 수반응률을 사용하지만 동일한 미시적 단면적에서 나온 에너지 순간이라고 주장할 수는 없다. 그 차이는 선택한 원자 열폐쇄에 대한 민감도이며 전체 물리 오차의 상한이나 신뢰구간이 아니다. [S1–S5]

## 1. 좌표, 단위, 물리적 범위

독립변수와 바리온 수밀도는

\[
x=\ln(a/a_{z=20}),\qquad 1+z=21e^{-x},\qquad
\dot n_b=-3Hn_b,\qquad \dot x=H.
\]

물리 상태는 기존 geometry/radiation 40, native isotope/ion 21, 누적 Thomson 광학깊이 1, 새 $\ell=\ln T$ 1의 합인 **63차원**이다. 21개 원자 좌표에는 n, H1 I–II, D I–II, T I–II, He3 I–III, He4 I–III, Li6 I–IV와 Li7 I–IV가 포함된다. 개수는 $1+2+2+2+3+3+4+4=21$이다. 각 $Y_i=n_i/n_b$는 바리온 하나당 핵종·이온의 수이며, 해당 원소 내 이온화 비율과 다르다. 수밀도는 m$^{-3}$, 시간은 s, 에너지는 J, 온도는 K를 사용한다.

이번 물리 부분공간에서는 n와 T의 재고가 정확히 0이다. 동위원소별 핵 수와 $A\cdot Y=1$이 보존되고, 원자 반응만으로는 핵의 총수가 변하지 않는다. 기존 동위원소 간 원자 계수의 공유도 그대로 유지한다. 새 단위가 동위원소별 질량 이동이나 미세한 원자 동위원소 효과를 새로 검증한 것은 아니다.

이온 전하 벡터를 $q_i$, 누적 이온화 에너지를 $I_i$라 쓰면

\[
n_e=n_bq\cdot Y,\qquad
\eta=(1+q)\cdot Y,\qquad n_g=n_b\eta.
\tag{1}
\]

$n_g$는 중성 원자·이온·자유 전자의 열운동 입자 수밀도이다. 전하중성 조건은 별도의 자유 전자 ODE 없이 식 (1)로 적용된다. 실제 저장 상태에는 양성, 보존, 정확한 n/T 영값 검사를 적용한다. 암시적 적분기의 Newton 시험점과 Jacobian 유한차분에서는 부호 있는 $Y$의 매끄러운 수치 확장을 허용한다. 이 확장을 음의 밀도나 비영 핵반응에 대한 물리적 폐쇄로 해석하지 않는다.

비틸트 LRS Bianchi I에서 팽창 스칼라는 $\theta=3H$이다. 이 열모델의 바리온 기체는 공통 온도를 갖는 비상대론적 단원자 이상기체이며, 바리온 비등방 응력은 별도로 닫지 않는다. 따라서 기체의 에너지 방정식에 추가적인 shear-work 항을 삽입하지 않는다. 기하·복사계의 기존 shear와 부호 있는 응력 정의는 그대로 유지된다.

## 2. 입자 수가 변하는 기체의 온도 방정식

물리적 초 단위의 원자 반응식을

\[
\dot Y=F(Y,T,x),\qquad w=1+q,\qquad \dot\eta=w\cdot F
\]

로 쓰자. 열운동 에너지와 압력은

\[
u_{\rm th}=\frac32 k_BTn_b\eta,\qquad
p=k_BTn_b\eta.
\]

열운동 에너지로 들어오는 순 체적 전력을 $Q_{\rm kin}$이라 하면

\[
\dot u_{\rm th}+3H(u_{\rm th}+p)=Q_{\rm kin}.
\tag{2}
\]

$\dot n_b=-3Hn_b$를 대입하여 정리하면

\[
\dot T=-2HT-T\frac{w\cdot F}{\eta}
       +\frac{2Q_{\rm kin}}{3k_Bn_b\eta},
\tag{3}
\]

따라서 구현된 새 행은

\[
\boxed{\frac{d\ell}{dx}
=-2+\frac{2Q_{\rm kin}/(3k_BTn_b)-w\cdot F}{H\eta}.}
\tag{4}
\]

첫 항은 단원자 기체의 단열 냉각이다. 두 번째의 입자 수 항과 마지막 열원 항은 독립적으로 필요하다. 예컨대 열운동 에너지를 외부로 빼지 않고 입자 수만 증가시키면 입자 하나당 에너지가 감소한다. 재결합으로 평균보다 낮은 에너지의 전자가 제거될 때에는 총 열운동 에너지가 감소하더라도 남은 입자의 온도가 상승할 수 있다. 그러므로 재결합 사건마다 무조건 $3k_BT/2$를 냉각량으로 배정하거나, 재결합 냉각을 넣었다는 이유로 $w\cdot F$를 없애면 안 된다. 이러한 입자 수 항은 우주론적 온도 방정식의 기존 처리와도 맞는다. [S6]

코드는 식 (4)를 `thermal_sources.temperature_log_rhs`에 두고 `ThermalSystem.rhs`의 63번째 좌표로 연결한다. 원래 62개 방정식도 같은 시험점의 동적 $T=e^\ell$로 재평가한다. 온도 변화는 재결합률, $n_e$, Thomson opacity를 통해 계승한 기하·복사계와 다시 연결된다.

이전의 처방 온도 $T_*(x)$를 그대로 유지하는 데 필요한 열입력은

\[
Q_{\rm required}
=\frac32 k_Bn_b\eta H(T_*'+2T_*)
 +\frac32 k_BT_*n_b\,w\cdot F.
\]

따라서 같은 원자 열폐쇄 아래 처방 온도가 숨기고 있던 추가 열원은

\[
Q_{\rm ext}=Q_{\rm required}-Q_{\rm kin}
=Q_{\rm required}-Q_{\rm primary}+Q_{\rm RR}+Q_{\rm DR}.
\tag{4a}
\]

그 누적값은 $\int Q_{\rm ext}\,dx/(n_bH)$이다. 음의 값은 해당 처방 이력을 유지하려면 순 열제거가 더 필요하다는 뜻이며, 기체 에너지나 입자 수가 음수라는 뜻이 아니다. 이 양은 기존 전체 $z=20\to2$ 경로의 조건부 잔여 열예산이다. 새 $z\simeq8$ 재시작 경로에서 실제로 제거한 열이나, 단순한 최종 온도 차이로 바꾸어 해석할 수 없다.

## 3. 전체 원자 에너지 장부

### 3.1 이온 결합 저장고

$I_i$는 해당 중성 원자의 바닥상태를 기준으로 한 누적 이온화 에너지이다. 이온 저장고는

\[
u_{\rm ion}=n_b I\cdot Y,\qquad
\dot u_{\rm ion}+3Hu_{\rm ion}=n_bI\cdot F.
\tag{5}
\]

이 정의에서는 재결합의 결합 에너지는 기체 열운동에서 직접 제거되는 양이 아니다. 전자 포획의 운동 에너지는 열 저장고에서, 이온화 에너지 차이는 식 (5)의 저장고에서 나온다. 두 항을 분리해야 재결합 광자의 전체 에너지와 기체 냉각을 동시에 맞출 수 있다.

### 3.2 현재 선택한 광흡수·방출 소유권

원래 광흡수 계산이 제공하는 총 흡수 전력, 일차 전자 운동 전력, 내부껍질 잔여 전력을 각각 $Q_{\rm abs}$, $Q_{\rm primary}$, $Q_{\rm core}$라 쓴다. 광원은 기존 외부 처방 UV이며 그 스펙트럼·시간 함수·유한 에너지 지지집합을 바꾸지 않는다. 현재 수반응 연산자는 흡수 사건당 한 단계의 전하 증가를 사용한다. [S3]

재결합 전 이온 $i$의 RR·DR 계수를 $\alpha_i^{\rm RR},\alpha_i^{\rm DR}$, 전자 운동 에너지 손실 계수를 $L_i^{\rm RR},L_i^{\rm DR}$라 쓰고, 아래 이온 상태까지의 이온화 에너지 차이를 $\chi_i^-=I_i-I_{i-1}$라 쓰면

\[
Q_{\rm RR}=n_bn_e\sum_iY_iL_i^{\rm RR},\qquad
Q_{\rm DR}=n_bn_e\sum_iY_iL_i^{\rm DR},
\]

\[
Q_{\rm bind,esc}
=n_bn_e\sum_iY_i\chi_i^-(\alpha_i^{\rm RR}+\alpha_i^{\rm DR}).
\tag{6}
\]

선택한 일차 전자의 국소 열평형화와 prompt optically thin/case-A 복사 탈출 조건 아래

\[
Q_{\rm kin}=Q_{\rm primary}-Q_{\rm RR}-Q_{\rm DR},
\]

\[
Q_{\rm esc}=Q_{\rm core}+Q_{\rm bind,esc}+Q_{\rm RR}+Q_{\rm DR}.
\tag{7}
\]

각 항의 소유권은 다음과 같다.

| 에너지 | 저장 또는 전달 위치 | 구현 |
|---|---|---|
| 일차 광전자 운동 에너지 | 공통 기체 온도로 즉시 전달 | `primary_kinetic_power_W_m3` |
| 광이온화의 이온화 문턱 에너지 | $n_bI\cdot Y$ 증가 | `ionization_energy_J`, `dY_dt` |
| Li I 내부껍질의 잔여 여기 에너지 | 조건부 prompt 복사 탈출 | `core_escape_W_m3` |
| RR/DR 포획 전자의 운동 에너지 | 열 저장고에서 제거되어 복사로 탈출 | `rr_cooling_W_m3`, `dr_cooling_W_m3` |
| 재결합의 결합 에너지 | 이온 저장고 감소 후 복사로 탈출 | `binding_escape_W_m3` |
| 팽창 일 | 기체의 $p\,dV$ | `work_J_per_baryon_per_x` |

이 소유권으로 얻는 대수적 항등식은

\[
\boxed{Q_{\rm abs}-Q_{\rm esc}
=Q_{\rm kin}+n_bI\cdot F.}
\tag{8}
\]

`ThermalSources.evaluate`는 식 (8)의 잔차를 네 항의 절댓값 합으로 나누어 기록한다. 이 검사는 원자 에너지 이중 계상과 누락을 검출한다. 그러나 같은 가정을 공유한 항들 사이의 항등식이므로, 누락된 실제 반응이나 복사 전달의 작음을 증명하는 검사는 아니다.

### 3.3 적분된 에너지 검사

바리온 하나당 기체 에너지를

\[
e_g=\frac32k_BT\eta+I\cdot Y
\]

로 정의하면 식 (2), (5), (8)에서

\[
\boxed{\frac{de_g}{dx}
=\frac{Q_{\rm abs}-Q_{\rm esc}}{n_bH}-3k_BT\eta.}
\tag{9}
\]

새 실행기는 별도의 에너지 ODE를 추가하지 않고, 얻은 dense solution을 513점과 1025점에서 평가하여 식 (9)의 우변을 Simpson 적분한다. 끝점 에너지 차이와 적분값의 차이를 총 에너지 처리량으로 정규화하고, 두 진단 격자의 차이를 별도로 기록한다. 대수적인 식 (8) 검사와 수치적인 식 (9) 검사는 서로 다른 실패를 검출한다. 이 유한 진단은 전 구간·전 매개변수에 대한 수학적 오차 상한은 아니다.

이번 실행 산출물에는 109개 공통 저장 상태와 dense 적분의 수치 영수증이 남고, 513/1025점의 상태 배열이나 BDF 연속 보간자는 남지 않는다. 따라서 독립 검토자는 저장된 끝점 에너지와 dense 영수증의 산술은 재검산할 수 있지만, 그 dense quadrature 자체를 저장된 바이트만으로 완전히 재현할 수는 없다. 109점으로 별도 적분한 진단은 다른 격자의 검사이며 1025점 판정을 대신하지 않는다.

기체 열·결합 에너지는 여전히 기하 방정식에 대한 test-fluid 처리이다. UV 공급원과 탈출 광자를 기존 photon hierarchy에 새로 넣지 않았다. 따라서 식 (9)를 닫힌 우주 전체의 에너지 보존식으로 읽어서는 안 된다. 계승한 trace-energy gate는 이 분리의 유한 진단으로 유지한다.

## 4. 재결합률의 Maxwellian 에너지 순간

### 4.1 고정 미시 커널에서의 항등식

비상대론적 Maxwell 전자, 고정 초기 이온 상태, 온도와 무관한 단면적 $\sigma(E)$, 적분과 미분을 교환할 수 있는 수렴 조건을 가정한다. 무거운 이온에 대한 통상적인 전자 에너지 정의에서는

\[
\alpha(T)=C(k_BT)^{-3/2}
\int_0^\infty E\sigma(E)e^{-E/(k_BT)}\,dE,
\quad C=\sqrt{\frac{8}{\pi m_e}},
\]

\[
L(T)=C(k_BT)^{-3/2}
\int_0^\infty E^2\sigma(E)e^{-E/(k_BT)}\,dE.
\tag{10}
\]

보다 일반적인 상대운동 에너지 정의에는 $m_e$ 대신 환산질량을 사용하며 같은 항등식이 성립한다. 본 모델은 전자 에너지 손실의 통상적 무거운 이온 근사를 사용하고 유한 이온 반동을 새로 해상하지 않는다. 식 (10)을 미분하면

\[
\boxed{L(T)=k_BT\left[\frac32\alpha(T)
                   +T\frac{d\alpha}{dT}\right]
=k_BT\left[\frac32\alpha+\frac{d\alpha}{d\ln T}\right].}
\tag{11}
\]

$\alpha$의 단위는 m$^3$/s, (L)의 단위는 J m$^3$/s이다. 평균 제거 에너지는 $L/\alpha$이며 Maxwell 기체 전체의 평균 $3k_BT/2$와 일반적으로 다르다. Mao et al.의 정의도 총 RR률과 전자 에너지 손실을 구분한다. [S1]

식 (11)은 가정한 **진짜 온도 독립 커널**에 대해서는 정확하다. 그러나 출판된 유한 정밀도 피팅식에 식 (11)을 적용하면 그 피팅식이 암시하는 순간을 얻게 된다. 함수값의 상대 오차가 작다는 사실만으로 미분값의 오차를 제한할 수 없다. 이온 준위 점유율, 밀도 억제, 유효 단면적 또는 컷오프가 온도에 따라 바뀌면 그 변화의 미분 항도 필요하다. 여기서는 그런 추가 물리를 공급하지 않는다.

### 4.2 RR 피팅식 미분의 구현

기존 Verner–Ferland/Badnell 형태를

\[
\alpha=\frac{A}{u(1+u)^{1-b}(1+v)^{1+b}},\quad
u=\sqrt{T/T_0},\quad v=\sqrt{T/T_1},
\]

\[
b=B+C_b e^{-T_2/T},\qquad
b_1=\frac{db}{d\ln T}=C_b(T_2/T)e^{-T_2/T}
\]

로 쓰면

\[
s\equiv\frac{d\ln\alpha}{d\ln T}
=-\frac12-\frac{(1-b)u}{2(1+u)}
-\frac{(1+b)v}{2(1+v)}
+b_1[\ln(1+u)-\ln(1+v)].
\tag{12}
\]

따라서 대안 폐쇄는 $L_{\rm RR}=k_BT\alpha(3/2+s)$이다. 기존 피팅 계수·원자별 선택·cm$^3$→m$^3$ 변환을 그대로 유지한다. `recombination_moments.py`는 식 (12), 그 곡률, $dL/d\ln T$를 해석적으로 계산한다. 수치 미분을 ODE 우변이나 Jacobian 안에서 반복하지 않는다. [S4, S5]

### 4.3 DR 피팅 순간

기존 DR률이

\[
\alpha_{\rm DR}=T^{-3/2}\sum_r c_r e^{-E_r/T}
\]

형태일 때 표의 $E_r$는 K 단위이며, 식 (11)은

\[
\boxed{L_{\rm DR}
=k_BT^{-3/2}\sum_r c_r E_r e^{-E_r/T}.}
\tag{13}
\]

를 준다. 식 (13)의 $c_r$는 SI로 변환한 계수이며, 원표의 cm$^3$ 기반 수치 계수를 직접 사용하면 $\alpha_{\rm DR}$와 $L_{\rm DR}$ 양쪽에 동일한 $10^{-6}$ 변환 인자를 곱해야 한다. 단면적을 정확히 이산 공명들의 합으로 나타낼 수 있는 경우에는 각 공명의 에너지 순간과 일치한다. 실제 사용 중인 $c_r$는 근사 피팅 계수이고 음수인 항도 존재하므로, 개별 항을 독립적인 양의 공명 확률로 해석하지 않는다. 부호를 지우거나 계수를 자르지 않고 총률과 총순간의 양성·유한성을 허용 온도 구간에서 검사한다. 지수 underflow로 수치적으로 0이 된 채널과 물리적으로 존재하지 않는 채널도 구분한다. [S5]

## 5. 주 RR 폐쇄: Mao-factor hybrid

Mao et al.의 무차원 인자와 Eq. (7)을 다음처럼 사용한다. [S1, S2]

\[
f=\frac{L_{\rm RR}}{k_BT\alpha_{\rm RR}},\qquad
t=\frac{k_B T}{1\,\mathrm{eV}},
\]

\[
f(t)=a_0\exp[-b_0\ln t-c_0(\ln t)^2]
       \frac{1+a_2t^{-b_2}}{1+a_1t^{-b_1}}.
\tag{14}
\]

입력은 **eV로 표현한 온도 에너지**이고 로그는 **자연로그**이다. 소스 표의 $s$는 재결합 **후** 이온의 전자 수이다. 기존 네트워크가 사용하는 재결합 **전** 이온 전하는

\[
q=Z-s+1
\tag{15}
\]

로 연결한다. 다음 여섯 행만 사용한다.

| 기존 초기 이온 → 생성 이온 | (Z,q,s) | $a_0,b_0,c_0$ | $a_1,b_1,a_2,b_2$ | 출판된 최대 편차 |
|---|---|---|---|---:|
| H II → H I | 1,1,1 | 8.655, 0.5432, 0 | 10.18, 0.5342, 0, 0 | 1.2% |
| He II → He I | 2,1,2 | 2.354, 0.3367, 0 | 62.8, 0.8875, 21.33, 0.5675 | 1.5% |
| He III → He II | 2,2,1 | 17.82, 0.5398, 0 | 20.61, 0.5318, 0, 0 | 0.9% |
| Li II → Li I | 3,1,3 | 4.166, 0.3110, 0.007567 | 65.17, 0.9634, 10.19, 0.7434 | 1.9% |
| Li III → Li II | 3,2,2 | 65.58, 0.6439, 0 | 78.78, 0.6317, 0, 0 | 1.3% |
| Li IV → Li III | 3,3,1 | 27.33, 0.5385, 0 | 31.43, 0.5309, 0, 0 | 1.1% |

CDS 계산표의 온도는 재결합 전 $q$에 대한 $q^2[10,20,50,\ldots,10^7]$ K의 19개 노드로 복원된다. ReadMe의 charge 설명을 문자 그대로 재결합 후 전하로 사용하면 중성 생성 이온의 온도 격자가 0이 된다. 식 (15)의 대응으로 모든 여섯 행, 114개 출판 값을 재현했으며 이 소스 표기 해석을 `mao2017_selected.json`에 명시했다. 자연로그 선택 역시 $c_0\ne0$인 Li I 행으로 독립 확인했다. 이 행에서 자연로그 식과 반올림 표의 최대 차이는 약 1.874%이고, 상용로그를 대입하면 약 22.829%로 커진다.

표가 소수 셋째 자리, 출판 최대 편차가 0.1 percentage point 단위로 반올림되어 있으므로, 재현 허용량은 사전 동결한

\[
|f_{\rm fit}-f_{\rm table}|
\le (\mathrm{mdp}/100+0.0005)f_{\rm table}+0.0005
\tag{16}
\]

이다. 식 (16)은 표의 유한 자릿수를 반영하며 실제 원자 물리 오차를 확장하거나 인증하는 규칙이 아니다. 실행은 모든 소스가 겹치는 **100–$10^6$ K**에 제한한다. 원표의 더 넓은 노드는 식과 인덱싱 검증에 사용했을 뿐 실행의 온도 지지집합을 확장하지 않는다.

주 폐쇄는

\[
\boxed{L_{\rm RR}^{\rm primary}
=k_BT\alpha_{\rm parent}(T)f_{\rm Mao}(T).}
\tag{17}
\]

이다. H/He의 기존 수반응률은 Verner–Ferland, Li의 기존 수반응률은 잠근 Badnell 자료를 그대로 사용한다. 따라서 식 (17)을 Mao 논문 자체의 총 손실률 자료와 완전히 동일하다고 부르지 않는다. `thermal_sources.mao_factor`는 식 (14)와

\[
\frac{d\ln f}{d\ln T}
=-b_0-2c_0\ln t
-\frac{b_2a_2t^{-b_2}}{1+a_2t^{-b_2}}
+\frac{b_1a_1t^{-b_1}}{1+a_1t^{-b_1}}
\]

를 구현하여 주 폐쇄의 Jacobian도 동일한 소스 정의에서 얻는다.

독립적인 1001점 로그 온도 격자에서

\[
|f_{\rm derivative}/f_{\rm Mao}-1|
\]

의 유한 최대값은 다음과 같다. 원표, 선택 행, 비교값은 `data/mao2017_selected.json`과 출처 검토 자료에 보존되어 있다.

| 재결합 전 이온 | 100–12000 K | 100–$10^6$ K |
|---|---:|---:|
| H II | 0.370% | 0.710% |
| He II | 2.265% | 12.862% |
| He III | 0.593% | 0.593% |
| Li II | 3.468% | 14.311% |
| Li III | 2.070% | 5.259% |
| Li IV | 1.264% | 1.264% |

여기서 1001점은 `evidence/INDEPENDENT_THEORY_SOURCE_REVIEW_KO.md`에 기록한 독립 원자료 검토의 구간별 로그 격자이며, 해당 최대값과 위치는 `data/mao2017_selected.json`의 `comparison` 필드에 보존되어 있다. 결과 그림의 `code/analyze_and_plot.py`는 공통 100–10^6 K 구간에서 별도의 801점 격자를 사용한다. 두 유한 격자의 최대값은 반올림 전에는 조금 다를 수 있다.

이 표는 두 폐쇄가 서로 다름을 정량화한다. 이 유한 격자의 최대값을 연속 구간의 엄밀한 상한, 천체 온도 오차, 혹은 전체 네트워크 정확도로 승격하지 않는다.

## 6. Li 내부껍질과 다중 전자 수율의 경계

기존 Li I 1s 부분 단면적의 유효 문턱은 64.39 eV이고, 단일 전하 증가에 사용하는 첫 이온화 문턱은 5.392 eV이다. 현재 사건 장부는 [S3]

\[
E=\underbrace{(E-64.39)}_{\text{일차 전자}}
 +\underbrace{5.392}_{\text{이온 저장고}}
 +\underbrace{58.998}_{\text{잔여 내부 여기}}
\quad[\mathrm{eV}]
\tag{18}
\]

이다. 58.998 eV의 잔여 에너지는 Li II에서 다음 전자를 떼는 75.64 eV보다 작다. 따라서 **이 사건으로 만들어진 고립된 잔여 이온이 그 잔여 여기 에너지만으로 한 번 더 자동이온화한다**는 해석은 에너지 보존과 맞지 않는다. 이것은 선택된 잔여 상태와 에너지 예산에 관한 판단이며, 고에너지 광자에 의한 직접 이중 광이온화나 shake-off 전체를 배제하는 정리는 아니다. 바닥상태에서의 이중 제거 문턱은 사용 중인 문턱값의 합인 약 81.032 eV이고, 그런 별도 채널에는 별도의 단면적·분기 자료가 필요하다.

Li$^+$(1s2s) 준위의 복사 완화 가능성은 실험적 metastable Li$^+$ 연구와 부합한다. Saghiri et al.은 triplet 준위의 약 52 s 수명과 singlet 준위의 훨씬 짧은 복사 수명을 논의한다. [S7] 여기서는 이런 완화가 동역학 시간에 비해 짧고 생성 광자가 탈출한다는 조건 아래 $Q_{\rm core}$를 복사 탈출로 배정한다. 고밀도 충돌 소거, 준위별 점유, 국소 재흡수 또는 광자의 후속 이온화는 이 계산의 새 예측이 아니다.

더 일반적인 다중 전자 사건에서 초기 이온 $i$, 최종 전하 증가 $m$, 광자 에너지 $E$에 대한 분기 $p_m(E)$를 도입하면

\[
\Gamma_{im}=\int \Phi(E)\sigma_i(E)p_m(E)\,dE,
\]

이고 수반응 연산자에 $i\to i+m$의 이동을 넣어야 한다. 자유 전자 수원은 $m\Gamma_{im}Y_i$, 이온 저장고 증가는

\[
[I_{i+m}-I_i]\Gamma_{im}Y_i
\]

이며 사건별 에너지 장부는

\[
E=I_{i+m}-I_i+E_{\rm thermalized}
+E_{\rm nonthermal}+E_{\rm escape}+E_{\rm residual}.
\tag{19}
\]

총 광흡수 단면적 또는 총 광이온화률만으로 $p_m$, 전자들의 에너지 분포, 열화율을 복원할 수 없다. 임의의 열량만 더하고 기존 한 단계 수반응 연산자를 유지하면 일반적으로 전하·입자·에너지 장부가 함께 맞지 않는다. 이번 단위는 그런 미결정 분기를 발명하지 않고 식 (18)의 단일 전하 모델과 조건부 복사 탈출을 명시적으로 사용한다.

## 7. 63차원 해석 Jacobian

기존 62차원 Jacobian을 동적 온도에서 재사용하고 새 온도 열·행을 추가한다. $D=\partial F/\partial Y$, $K=Q_{\rm kin}/n_b$, $N=2K/(3k_BT)-w\cdot F$라 쓰면 $g=d\ell/dx=-2+N/(H\eta)$이다. 단위 바리온당 광전자 전력의 선형 계수 벡터를 $P(x)$, 총 운동 손실 계수 벡터를 $L(T)$라 쓰면

\[
K=P\cdot Y-n_b(q\cdot Y)(L\cdot Y),
\]

\[
K_Y=P-n_b[(q\cdot Y)L+(L\cdot Y)q],\qquad
N_Y=\frac{2K_Y}{3k_BT}-w^\top D,
\]

\[
g_Y=\frac{N_Y}{H\eta}-\frac{Nw^\top}{H\eta^2}.
\tag{20}
\]

온도 편미분은

\[
K_\ell=-n_eY\cdot L_\ell,\qquad
N_\ell=\frac{2(K_\ell-K)}{3k_BT}-w\cdot F_\ell,
\]

\[
g_\ell=\frac{N_\ell}{H\eta}.
\tag{21}
\]

여기서 $F_\ell$는 하향 전이 행렬의 계수 $d(\alpha_{\rm RR}+\alpha_{\rm DR})/d\ln T$로 얻는다. 고정 (x,Y)에서 UV 광률은 온도에 의존하지 않는다. 기하 좌표를 $b$라 쓰면 현재 test-fluid 모델에서 (Y,T)에 대한 $H$의 직접 의존성이 없으므로

\[
g_b=-\frac{N}{H\eta}\frac{\partial\ln H}{\partial b}.
\tag{22}
\]

코드의 원자 좌표가 $Y_i/s_i$로 저장되므로 식 (20)의 열에는 $s_i$를 곱하고, 원자 RHS의 온도 열에는 $F_{\ell,i}/(Hs_i)$를 넣는다. opacity의 직접 온도 미분을 임의로 넣지 않는다. 고정 $Y$에서 $n_e$는 $T$와 독립이며 실제 온도 효과는 원자 방정식을 통해 전파된다.

`thermal_system_tests.json`은 특정 물리 상태에서 63개 열 전체와 추가 혼합 방향을 수치 차분으로 대조한다. 이 검사는 analytic Jacobian의 구현 일관성에 대한 증거이다. 전역 해의 정확도나 모든 물리 상태에서의 Jacobian 오차 상한을 대신하지 않는다.

## 8. 재시작과 유한 실행의 의미

네 개의 기존 완료 사례 `s00_m02_r02`, `s03_m03_r03`, `s04_m04_r04`, `s02_m04_r01`에서 저장된 84번째 노드의 62차원 값을 그대로 읽는다. 해당 노드는 $x=0.8513356902116996$, $z=7.963732801243163$이다. 새 온도의 초기값은 바로 그 노드의 기존 처방 온도 (1081.3197799717436) K이며 보간이나 앞 구간 재적분을 사용하지 않는다. 초기 열미분이 기존 처방 온도의 미분과 달라도 모순은 아니다. 서로 다른 열원 계약으로 전환한 새로운 초기값 문제이기 때문이다.

두 사례 `s03_m03_r03`, `s04_m04_r04`에 대해 허용오차·최대 스텝을 줄인 주 폐쇄 계산을 수행하고, 같은 두 사례에서 RR 미분 대안을 비교한다. 총 여덟 개의 서로 다른 새 구성만 허용한다. 기존 126개 궤적의 열원 재평가는 저장 데이터의 후처리이며 ODE 재실행이 아니다. 수치 기준과 계산 예산은 `FROZEN_CONTRACT.md`에 둔다.

`elapsed_Myr`는 기존 $z=20$ 원점부터 누적된 시간이고 재시작 후 경과 시간이 아니다. τ도 동일하게 누적된 기존 광학깊이를 계승한다. 재시작 이후 증가량이 필요하면 초기값을 명시적으로 빼야 한다.

실행 전 독립 PHYS-MATH 검토는 네 donor `RESULT.json`의 실제 바이트가 부모 커밋 `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`과 같고, 각 NPZ가 그 영수증의 SHA256과 일치하며, 저장된 isotope scale과 현재 모델의 scale이 정확히 같음을 확인했다. 이 검토에서는 ODE를 실행하지 않았다. 검토 대상 실행 코드·자료 해시, 해결한 결함, 범위 제한은 `evidence/PHYS_MATH_PRE_RUN_REVIEW.json`에 기록되어 있다.

## 9. 판정 범위와 다음 물리 과제

이 단위가 닫는 것은 주어진 광흡수·RR·DR 수반응과 선택한 열손실·복사 탈출 사이의 기체 열방정식이다. 다음 사항은 별도의 물리 입력 또는 검증을 요구한다.

- 일차 광전자의 유한 열화와 이차 이온화·여기, 이온별 다중 전자 분기.
- collisional ionization, charge exchange, collisional excitation, free-free와 분자 과정.
- Compton 에너지 교환. 기존 Thomson 산란 블록은 탄성 블록이며 열전달 계수의 대체물이 아니다.
- 준위별 cascade 지연, 재흡수, 광학적으로 두꺼운 복사 전달과 외부 UV의 역반응.
- n/T 활성화 시의 핵질량 결손, 전자·중성미자·감마선 에너지와 daughter 상태의 소유권.
- $z=20$부터의 자체 일관된 열 이력, 기체 열응력의 중력원 포함, 전역 수렴과 누락 과정의 크기 평가.

누락 과정이 작다는 가정을 이번 에너지 항등식에서 도출하지 않는다. 유한 소스 검증과 새 재시작 계산을 통과하더라도 **physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, REI_activation=false**는 유지된다. 이 노트는 실행 전 유도와 계약을 설명한다. 실제 궤적 결과와 refinement/source 비교의 판정은 해당 결과 영수증 및 결과 보고서가 담당한다.

## 원자료와 출처

**[S1]** J. Mao, J. S. Kaastra & N. R. Badnell (2017), *The electron energy loss rate due to radiative recombination*, A&A 599, A10. [논문](https://arxiv.org/abs/1612.01017), [출판 PDF](https://www.aanda.org/articles/aa/pdf/2017/03/aa29708-16.pdf), [DOI](https://doi.org/10.1051/0004-6361/201629708). RR 수반응률·전자 에너지 손실·무차원 $f$의 정의와 피팅식을 사용했다.

**[S2]** 위 논문의 [CDS 원표와 ReadMe](https://cdsarc.cds.unistra.fr/ftp/J/A+A/599/A10/), [calc.dat](https://cdsarc.cds.unistra.fr/ftp/J/A+A/599/A10/calc.dat), [pars.dat](https://cdsarc.cds.unistra.fr/ftp/J/A+A/599/A10/pars.dat). 보존된 SHA256은 `calc.dat`: `bf7ad20e10ff7045fc83b4c4c4148132c291f315213c5fc7b00ae820c76aa58a`, `pars.dat`: `a3c97fdf8101da6d33cc838f7fd4e142bcf3740c37b48d89e76c47ae91575d12`이다. `provenance/MAO_SOURCE_LOCK.json`이 이 파일과 선택 행을 잠근다.

**[S3]** D. A. Verner & D. G. Yakovlev (1995), A&AS 109, 125; D. A. Verner et al. (1996), ApJ 465, 487. [저자 광이온화 자료](https://www.pa.uky.edu/~verner/photo.html), [사용된 부분껍질 provider](https://www.pa.uky.edu/~verner/dima/photo/phfit2.f), [Verner et al. DOI](https://doi.org/10.1086/177435). 기존 부모 단위가 잠근 광흡수 계수와 Li 부분껍질 계약을 재사용한다. 흡수 단면적을 다중 전하 수율 자료로 해석하지 않는다.

**[S4]** D. A. Verner & G. J. Ferland (1996), ApJS 103, 467. [저자 재결합 자료](https://www.pa.uky.edu/~verner/rec.html), [DOI](https://doi.org/10.1086/192284). 기존 H/He RR 계수 및 함수 형태의 출처이다.

**[S5]** N. R. Badnell (2006), ApJS 167, 334, [DOI](https://doi.org/10.1086/508465); [저자 RR 자료](https://amdpp.phys.strath.ac.uk/tamoc/DATA/RR/), [저자 DR 자료](https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/). 부모 단위에서 잠근 실제 행·버전·단위는 `provenance/PARENT_SOURCE_LOCK.json`과 부모 `../rec_rei_hheli_sandbox_20261021/provenance/atomic_sources.json`을 따른다. 이 단위에서 저자 서버의 이후 수정본으로 수반응 계수를 바꾸지 않았다.

**[S6]** L. Hui & N. Y. Gnedin (1997), *Equation of state of the photoionized intergalactic medium*, [원논문](https://arxiv.org/abs/astro-ph/9612232). 온도 방정식의 입자 수 변화 항과 열계수의 구별을 비교했다. 해당 논문의 새로운 수반응·냉각 피팅을 현재 네트워크에 추가한 것은 아니다.

**[S7]** A. A. Saghiri et al. (1999), *Dielectronic Recombination of Ground-State and Metastable Li+ Ions*, [원논문 PDF](https://arxiv.org/pdf/physics/9907030). Li$^+$ metastable 준위의 복사 수명과 실험 상태를 참고했다. 특정 광이온화 사건의 singlet/triplet 분기비나 직접 이중 광이온화 수율을 이 논문으로부터 발명하지 않았다.

출판된 수치 자료의 저자·출처를 유지하며, 이 문서가 원자료 전체에 새 라이선스를 부여하지 않는다.
