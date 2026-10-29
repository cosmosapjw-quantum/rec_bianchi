# REC HD: 1984 실측 고회전 선과 2022 실측 조합차의 관측 제약 그래프

**연구 단위:** `REC_HD_1984_LAB_GRAPH_20261030`, **기준 부모:** PR162 `4d60f74db02d7435add062eaefb15739e68c4b55` (DRAFT/UNMERGED). 원형 source/gate/production은 변경하지 않는다. 이론 먼저, 코딩 다음. 원래 물리 목표는 실측 자료를 확보해 native HD 전이 자료의 관측 제약을 강화하는 것이다.

## R1–R3: 출처·정의·물리 계약

- 신규 실제 실험 원전: P. Essenwanger and H. P. Gush, *Rotational spectrum of HD at low pressures*, Canadian J. Phys. **62** 1680–1685 (1984), DOI 10.1139/p84-213. 출판사 원초록에서 저압 3–500 Torr diode-laser pure rotational lines R(3)=350.852±0.002, R(5)=514.656±0.001, R(6)=591.9327±0.0003 cm^-1를 직접 전사. 2011년은 온라인 재게시 날짜이지 인쇄 출판 연도가 아니다. R(J)은 v=0, J+1→J 로 해석한다. 원문 전체의 raw bytes 미확보. 보고된 ±의 신뢰수준/공동 공분산 미확보.
- 상속·재사용: PR160의 2022 HD v=0 J2−J0=8,006,533,168(26) kHz 및 J3−J1=13,283,245,098(30) kHz (DOI 10.1140/epjd/s10053-022-00552-x / 10.1103/PhysRevA.105.062823); PR161의 2021 LAMDA 8개 photon νP/A와 원본 35Hz fail; PR162의 2011 CDMS v2 `.egy` **인쇄값 전사본**. 이 자료들은 각자 provenance가 다르다. 원본 LAMDA 2289바이트 및 CDMS 2011 원본 `.fit/.par/.cat/.lin/.egy`는 이번에도 raw re-acquisition 하지 못했고 원 피팅 covariance는 null이다.
- SI 단위, h=6.62607015×10^-34 J s, c=299792458 m/s, k_B=1.380649×10^-23 J/K 정확값. 양의 상향 준위차를 ν_{u l}=(E_u−E_l)/h, 수직 방향/에너지 측정 오차/물리적 모델 오차를 구분한다. 광자 방출 ν>0. 유도하는 LTE는 *가정*이지 천체 관측값/실제 9준위 non-LTE 해가 아니다.

## R4–R5: 새로운 실측 그래프와 식별성 정리

9개 회전준위 에너지(주파수 단위) \(e=(E_0/h,\dots,E_8/h)^T\)에 대해 다섯 실측 관측량은 \(y=D e\) 이고, D의 행은 \(e_2-e_0, e_3-e_1, e_4-e_3, e_6-e_5, e_7-e_6\)를 취하는 incidence 행이다. 첫 두 측정은 2022 조합차, 나머지 셋은 1984 전이다. 무향 실측 그래프의 연결 성분은 \(\{0,2\},\{1,3,4\},\{5,6,7\},\{8\}\). \(Dx=0\)이면 각 관측된 edge 양쪽에서 x의 값이 같으므로 각 연결 성분에서 x는 상수, 그 역도 성립한다. 따라서 \(\dim\ker D=4\), \(\mathrm{rank}(D)=9-4=\mathbf{5}\). 이것은 측정 공분산의 독립성 주장이 아니라 **관측 방정식의 선형 대수적 식별성**이다.

2011 historical 1→0 **nominal source frequency** ν10=2,674,986,094,000 Hz를 조건부로 단 하나 추가하면 연결 성분은 \(\{0,1,2,3,4\},\{5,6,7\},\{8\}\), rank 6, nullity 3이다. 에너지 영점 하나를 고정해도 계열 {5,6,7}의 전체 offset과 J8의 offset이 남는다. 2011 source 1→0의 불확도 미지이므로 실측 rank-5와 nominal-anchored rank-6 결과를 혼합하지 않는다. 이 데이터만으로 전체 8개 개별 실험 선을 규정했다는 주장은 부정된다. 통신을 완결할 표적 측정은 5→4와 8→7의 독립 준위차이며, 이것은 현재 2011 nominal 1→0 앵커가 진짜 독립 실험 인증을 받는다는 조건이다.

## R5: 실험 데이터로 계산 가능한 물리 관측량

1984 세 측정의 실제 실측 파수 \(\tilde\nu_J\)에 대해 \(\nu_J=100c\tilde\nu_J\) (Hz), \(E_{\gamma,J}=h\nu_J\) (J), \(\lambda_J=c/\nu_J\) (m). 2021 LAMDA의 해당 \(A_{J,J-1}\)를 별도 출처로 고정하여 조건부 광자 방출 전력 \(P_{\rm upper,J}=A_{J,J-1} h\nu_J\) (W/상향 준위 분자)를 계산했다. A는 새로운 1984 실측이 아니다. 조건부 LTE(같은 내부 핵스핀 가중, 원래 rotational g_J=2J+1)에서는
\[
\frac{n_J}{n_{J-1}}=\frac{2J+1}{2J-1}\exp\left[-\frac{h\nu_{J,J-1}^{1984}}{k_B T}\right]\quad(J=4,6,7;\ T=50,100,200\,\mathrm K).
\]
3개 광자 E/λ/P 행, 9개 LTE 행을 생성했다. 실제 non-LTE 점유율·냉각률·우주론 열역사는 구하지 않았다.

실측−2021 photon 주파수 잔차 (Hz) R3 −28,733,778.4, R5 +433,112,344.8, R6 +6,857.66. 각 1984 보고 오차를 Hz로 정확히 환산하면 각각 59,958,491.6, 29,979,245.8, 8,993,773.74. 특히 6→5의 큰 차이는 데이터간 중심값의 숫자 차이이며, 오래된 source fit covariance/원본 measurement covariance와 re-fit residual 없이 χ²·sigma/새 물리 주장을 하지 않는다. 2022 실험 조합차의 source 잔차 −14,877,400 / −45,034,200 Hz는 원래 그대로 유지했다.

조건부 2011 ν10 및 실제 2022/1984 저준위 측정 연결시 \(e_0=0, e_1=x, e_2=y_{20}, e_3=x+y_{31}, e_4=x+y_{31}+\nu_{43}^{1984}\)가 유일하게 주어진다. 이 상향 준위 에너지 합의 원래 photon cumulative 대비 차이는 J1 0, J2 −14.8774 MHz, J3 −45.0342 MHz, J4 −73.7679784 MHz이다. J5 이상을 강제로 추정하지 않는다. 논문간 전이의 실험 공분산이 없으므로 개별 오차막대는 null.

## R6–R10: 독립성·판정

- Wolfram exact rank/nullspace/Hz residual 검산과 Wolfram LTE/물리 단위 변환 수행: method-level exact independent check; 별개 저자 심사 R6 NOT_RUN.
- Python exact Fraction graph rank, 68-digit Decimal 값, 15/15 normal, 15/15 `python -O`, `compileall` PASS; C5 첫 CSV 출력 실패를 구현 오류로 분류·보존, fixed union CSV schema로 복구.
- 관측 근거 새 증분 3개(+1984 직접 측정); 기존 PR160 2개 재사용. 제안 `REC-EXP-SPECTRAL: 2022_TWO_COMBINATIONS_PLUS_1984_THREE_LINES_PARTIAL`, owner canonical DAG 완료 승격 아님. `28/88 (+0)`, REC physical `0/313 (+0)`, 원래 35 Hz `FAIL7/8`, H5 null, H6/H7 OPEN, L4/REI false, production HOLD. 본 루프 18/20 scoped, native separate-author R6/C9 NOT_RUN.

다음 owner 과학: 2011 CDMS v2 원본 분광 fit/covariance 실제 바이트 복원 및 1984 고회전 오차 provenance 검토, 이어 2022+1984 실험 joint model uncertainty 통합. CDMS 2019/2026 대체 금지. 자동 다음 노드 실행 금지.
