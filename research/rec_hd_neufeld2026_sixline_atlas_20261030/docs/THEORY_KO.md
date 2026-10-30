# Neufeld 2026 HD 여섯 회전선: source extrapolation discriminant의 구성적 유도

## 1. 컨벤션과 물리 입력

고정된 독립 비LTE 분자모형은 HD 기저 진동상태의 회전준위 \(J=0,\ldots,14\), \(g_J=2J+1\), Neufeld(2026) 공개 Zenodo v2의 표준·대안 LAMDA 원본이다. 원본 `.dat/.fits` 4개 파일의 SHA-256은 `checkpoint/INHERITED_SOURCE_LOCK.json`과 `src/sixline_atlas.py`에 적혀 있다. 배경복사는 \(T_b=2.72548(1+z)\,\mathrm K\)인 등방 CMB, 에너지 단위는 J, 주파수는 Hz이며 \(h,c,k_B\)는 SI로 유지한다. 가스와 분자의 운동온도는 원본 제공 \(T_g\) 표본을 사용하고 H₂ ortho fraction은 3/4로 고정한다.

원래의 CDMS *2011 v2* owner-spectrum 35 Hz `FAIL7/8`과 Neufeld(2026)의 15준위 입력은 서로 다른 소스 권한이다. 후자의 모델 계산은 전자에 대한 source switch/production 승격을 허용하지 않는다.

## 2. 마스터 방정식 → 광자 에너지

원본 표준/대안 계수 \(s\in\{\mathrm{std},\mathrm{alt}\}\)로 생성자 \(L_s\)를 구성한다.

\[
C^s_{u\ell}=n_{\mathrm{H}_2}\frac{q^s_{u\ell,\mathrm{para}}+3q^s_{u\ell,\mathrm{ortho}}}{4},\qquad
C^s_{\ell u}=C^s_{u\ell}\frac{g_u}{g_\ell}\exp\!\left[-\frac{hc\,100(E_u-E_\ell)}{k_BT_g}\right].
\]

여기서 \(E_j\)는 \(\mathrm{cm}^{-1}\), \(100 E_j\)는 \(\mathrm{m}^{-1}\)이다. \(\bar n=(e^{h\nu/k_BT_b}-1)^{-1}\)와 Einstein 계수로

\[
R_{u\ell}=A_{u\ell}(1+\bar n),\qquad R_{\ell u}=\frac{g_u}{g_\ell}A_{u\ell}\bar n,
\quad L_s p_s=0,\quad \sum_jp_{s,j}=1.
\]

광학적으로 얇아 선 광자가 빠져나가는 정상상태에서 선 \(R(J)\equiv (J+1)\to J\)의 분자당 **배경 대비 순복사 에너지 출력**은

\[
F_J^{(s)}=h\nu_{J+1,J}A_{J+1,J}\left[p_{s,J+1}(1+\bar n)-\frac{g_{J+1}}{g_J}\,p_{s,J}\bar n\right],\quad [F]=\mathrm{W\,HD^{-1}}.
\]

양수는 가스의 순복사 냉각, 음수는 순가열이다. 이 출력은 관측된 flux가 아니라 분자당 에너지 전이이며 절대 플럭스는 원통 시선에 있는 HD column, 공간기하, 먼지 감쇠, 광학깊이, 운동학 및 도구 응답을 추가로 요구한다.

## 3. 여섯 선 대비량 및 품질 제한

원본의 R(4)에서 R(9)까지, 즉 upper \(J=5,\ldots,10\) 중 \(\binom 62=15\)개 선쌍 각각에 대해 같은 온도·밀도·적색편이에서

\[
\mathcal R_{a/b}^{(s)}=\frac{F_a^{(s)}}{F_b^{(s)}},\quad
\delta_{a/b}=\frac{\mathcal R_{a/b}^{\rm alt}}{\mathcal R_{a/b}^{\rm std}}-1,
\quad \Delta_{a/b}=\ln\mathcal R_{a/b}^{\rm alt}-\ln\mathcal R_{a/b}^{\rm std}.
\]

모두 \(F_a,F_b>0\)인 양의 warm emission 조건에서만 로그를 평가한다. 원천 강도 근사 필터는 동일 조건의 여섯 선과 두 소스에서 최대 출력 \(F_*=\max_{s,j\in[4,9]}F_j^{(s)}\)을 구하고, 비교에 쓰이는 네 출력 모두에 대해 \(\min(F_a^{\rm std},F_b^{\rm std},F_a^{\rm alt},F_b^{\rm alt})/F_*\ge\eta\)를 요구한다. \(\eta=0.001,0.01,0.05\) 등을 모두 공개하며 **이는 실측 신호대잡음 또는 JWST 검출 임계값이 아니다**.

원본 270개 공통 CMB 조건에서 \(T_g\ge1000\,\mathrm K\)의 120개 상태를 사용하며 \(n=10^2,10^4,10^6,10^8,10^{10}\,\mathrm{cm}^{-3}\), \(z=0,10,30,50,73,100\)이다. 120×15=1,800 출력비, 1% 필터 통과 1,512개. 최대 1% 통과 변화는 R(9)/R(7), \(T_g=1000\,\mathrm K\), \(n=10^6\,\mathrm{cm}^{-3}\), \(z=30\), \(\delta=1.00980545096\)이다.

## 4. 저밀도·고밀도 소스 민감도 소멸의 충분조건

\(L_s(n)=R+nQ_s\)라 쓰자. 표준·대안 소스의 \(R\)은 동일한 Einstein A와 주파수로 결정된다. \(Q_s\)는 두 원천 모두 \(C_{\ell u}/C_{u\ell}=(g_u/g_\ell)e^{-(E_u-E_\ell)hc(100)/(k_BT_g)}\)의 상세평형을 따르며, irreducible 충돌망이라는 전제 아래 **동일한 유일 Boltzmann 정지분포**

\[
\pi_j(T_g)=\frac{g_je^{-100hcE_j/(k_BT_g)}}{\sum_m g_me^{-100hcE_m/(k_BT_g)}}
\]

를 가진다. 따라서 고정된 \(T_g,z\)에서

\[
\lim_{n\to0}p_s(n)=p_R,\quad
\lim_{n\to\infty}p_s(n)=\pi,\quad
\lim_{n\to0,\infty}[p_{\rm alt}(n)-p_{\rm std}(n)]=0.
\]

\(R\)과 \(Q_s\)의 각각 유일한 정지분포가 존재하고 비교 선출력이 극한에서 영이 아니라면 선비율 소스 차이도 두 경계에서 0으로 수렴한다. 이는 15준위에서도 성립하는 **조건부 생성자 극한 정리**이며 원본 인쇄된 \(\nu\)와 \(E\)가 ~44 Hz 어긋나는 현상을 무시해 정확한 \(T_g=T_b\) 총출력 0을 주장하는 것과 다르다. Wolfram에서 두 준위의 각 저밀도·고밀도 소스 차이 0을 기호 확인했고, 15준위 수치에서는 중간 밀도 최대 민감도를 관측했다.

## 5. 근사적 밀도–소스 퇴화와 held-out 비교

고정된 \(T_g,z=0\), 기준 대안 소스 밀도 \(n_0=10^6\,\mathrm{cm}^{-3}\)에서 밀도 \(n_{\rm eq}\)를

\[
\mathcal R^{\rm std}_{9/7}(T_g,n_{\rm eq},0)
=\mathcal R^{\rm alt}_{9/7}(T_g,n_0,0)
\]

의 양의 근으로 정의한다. 원래 Tabulated \(T_g=1000,2000,3000,4000\,\mathrm K\)에서 각기 bracket \([10^4,10^8]\,\mathrm{cm}^{-3}\)의 실제 수치근을 구했다. 밀도 비율 \(n_{\rm eq}/n_0\)은 각각 약 \(2.45788,2.12272,1.97527,1.85805\)이다. 이는 R(9)/R(7) 하나만으로 source extrapolation을 단정할 수 없음을 보여주는 **모형 내 퇴화 사례**다.

그 밀도에서 사용하지 않은 두 번째 비율의 잔차

\[
\epsilon_{9/4}=\frac{\mathcal R^{\rm alt}_{9/4}(T_g,n_0,0)}{\mathcal R^{\rm std}_{9/4}(T_g,n_{\rm eq},0)}-1
\]

는 각각 \(-21.75569\%,-8.53932\%,-5.09481\%,-3.69147\%\)로, 독립 두 번째 관측량이 **모형에 한정하여** 일부 퇴화를 구별할 가능성을 제시한다. 통계적 검출력은 flux 오차, 상관행렬, HD/H₂ joint fit 없이 결정할 수 없다.

## 6. 적용 영역과 결론

R(9) \(\lambda_0=12.47183\,\mu\mathrm m\), R(7) \(15.02195\,\mu\mathrm m\)로 local source는 JWST/MIRI-MRS(4.9–27.9 μm) 범위 안에 있다. 다만 실제 선은 관측적 적색편이 \(z\)를 겪으면 \(\lambda_{\rm obs}=(1+z)\lambda_0\)이고, 계산 중 \(z\ge10\)의 높은 CMB 모델 상태는 JWST/MIRI의 관측 주파수대가 아니다. 광학적으로 얇고 특정 gas source rates/OPR에 대한 조건부 예측이며 새로운 관측자료·HD abundance fitting·우주 열이력 IVP·owner CDMS 35 Hz 해결을 주장하지 않는다.

**신원/상태:** parent PR171 head `8e1f51397cc3019642668daf4b2f2c39ff5126d5`; 2026 표준/대안 source SHA pinned, 기존 REC canonical **28/88**, physical **0/313**, 35 Hz `FAIL7/8`, production `HOLD`. 다른 저자 R6/C9는 `NOT_RUN`.
