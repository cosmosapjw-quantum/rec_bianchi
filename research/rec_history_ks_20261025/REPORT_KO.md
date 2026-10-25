# REC-HISTORY-KS01 결과 보고서

## 1. 이번에 닫은 연구 단위

**동일한 안정화 source의 입사응답 \(K_s\), 그 represented-operator 구간 인증,
원 history 실제 payload·causal prefix·313 query 결속을 완료했다.**
독립 최종 판정은 `PASS_SCOPED_SAME_SOURCE_KS_AND_ACTUAL_HISTORY_ADMISSION`이다.
이 문서는 과학 S2의18/20 snapshot이다. R10/C10의 실제 전달 완료는
`delivery/PUBLICATION_STATE.json`과 최종 handoff가 기록한다.

기존 THERMO01의 \(J_s\)는 수치 검증된 314×6 국소 primitive derivative다.
RESP01의 native \(K_0\) norm을 이 \(J_s\)에 옮겨 쓰지 않고, 같은 stable
coefficient에서 새로운 \(K_s\)를 직접 계산·인증했다. 또한 이전에는 로드하지
않았던35,239,470-byte 원 history를 실제로 읽어 source와 입력 domain을 연결했다.

이 성과는 REC-HISTORY의 내부 유한 단위다. 부모 REC-HISTORY=PARTIAL,
Physical HOLD와 생산·활성화 제한은 그대로다. H5의 물리적 interpolation
uncertainty, H6의 actual incident/frame, H7의 전체 history/retiming/geometry/
thermal-ODE pullback은 여전히 열린 의무다.

## 2. 최신 조사에서 반영한 변경

접근 가능한51개 owner repo의 모든 branch metadata2,254개를65pages 끝까지
조사했다. 관련9repo의 최신 PR96records 및 핵심 claim/report 원문을 읽었다.
이것은 접근 가능한 metadata 범위의 전수조사이며 모든 branch의 전체 본문을
읽었다는 뜻은 아니다. 대화는 indexed search로9개 관련 결과를 확인했으며,
전체 비공개 대화 archive를 열거하는 기능은 없었다.

Dropbox direct folder5pages/761entries(중복 포함),keyword14results,
Drive3folderlists/123entries와 검색12results를 조사했다. 원 THERMO S2와
companion은 인계 identity와 일치했다. 새 REC_HISTORY02 C5 archive는 복구해
원문을 읽었다. 그 상태는 IMPLEMENTATION_PRESENT_VERIFICATION_PENDING이며,
Bianchi-I retarded characteristic/retiming을 다른 owner가 구현 중이었다.
따라서 이번 KS01은 그 구현을 중복하지 않았다.

중앙 canonical은 조사 중14976…에서a28ba343bb85addf1a7e9e58e75816ed3b75cd3b로
전진했다. 최신 CR 전달과 기존 HE/HH 관측을 유지한 채 REC 관측만 더하도록
계획을 갱신했다. BASS188,HE100,CR104,HH146,Vigil87의 최신 scoped 성과는
현재 actual REC history uncertainty 또는 stable \(K_s\)의 공급자가 아니었다.
상세 identity와 적용 판정은 SURVEY_SYNTHESIS.md에 있다.

## 3. 식과 인증 대상

고정된 primitive,source stencil,branch에서
\[
 M_sX=c_s+B_su,\qquad o=T_sX+P_su,
 \qquad K_s=T_sM_s^{-1}B_s+P_s .
\]
\(u\)는311개 virtual channel과 Lyα/Lyβ의313개 Wien-departure 입력이고,
\(o\)는311개 virtual channel과 Lyα/Lyβ/Lyγ의314개 출력이다.
\(M_s,B_s\)는313×313, \(T_s,P_s\)는314×313이다.

원 source에서 \(B_s\)의 nonzero는 virtual311개와 real2개 계열로 직접 유도했다.
고정 primitive에서 source가 incoming에 affine이므로 이 response에는 incoming
방향의 고차 Taylor remainder가 없다. 물리 모델 및 trajectory 오차는 별도다.

근사 inverse \(Z\), response \(\widehat V\)에 대해
\[
 Q=I-ZM_s,\quad R=B_s-M_s\widehat V,\quad
 V-\widehat V=(I-Q)^{-1}ZR .
\]
기본 multiply/add를 nextafter로 바깥쪽으로 넓혀 \(Q,R,|Z||R|\)를 감싸고
\(\rho\ge\|Q\|_\infty,\rho<1\)을 확인했다. 각 column의 error bound와 \(T_s\)
row sum으로 \(K_s\)의 entry interval을 만들었다. BLAS residual을 증명으로
사용하지 않았으며, BLAS는 candidate solve 및 별도 진단에만 사용했다.

인증의 대상은 저장된 binary64 \(M_s,B_s,T_s,P_s\)가 정의하는 정확한 실수
선형대수다. source/libm 평가 자체의 오차·물리 모델 오차·history 오차까지
포함하는 인증은 아니다. \(J_s\)도 interval-certified로 승격되지 않는다.

## 4. 실제 결과와 판별 기준

|검사|실제 관측|동결 기준/판정|
|---|---|---|
|Source identity|원 canonical23개 및 전체 현재 manifest38개 일치|before/after/verified 일치|
|Stable represented coefficients|M,s,T,P,p,Tvv,Beta 모두 exact equality|PASS|
|\(\rho\)|3.458800151575591×10⁻¹²|<1|
|\(\|K_s\|_\infty\) 하한|1.17562722922718|rigorous represented bound|
|\(\|K_s\|_\infty\) 상한|1.1756272292401908|rigorous represented bound|
|Norm 상대 interval 폭|1.1067031540253658×10⁻¹¹|≤10⁻⁶|
|V componentwise backward residual|2.1996442957690597×10⁻¹⁵|≤4.547473508864641×10⁻¹³|
|입사 affine 검사 최대 normalized error|1.8555728462562315×10⁻¹³|≤2×10⁻⁹|
|Joint local 검사 최대 normalized error|6.684273687479512×10⁻⁸|≤2×10⁻⁵|
|독립 exact Fraction 사례|2×2,3×3의 exact K/norm 모두 구간 내부|PASS|
|거절 controls|rho≥1,nonfinite,negative epsilon,다른 cosmology,latest endpoint|PASS|

Norm 최대 row는0이다. 따라서 고정 represented map에서 uniform incoming box
\(\|\delta u\|_\infty\le\epsilon\)가 정당하게 주어지면
\[
 \|\delta o\|_\infty\le1.1756272292401908\,\epsilon
\]
을 사용할 수 있다. 아직 physical \(\epsilon\)는 주어지지 않아 실제 물리
error bound는 null이다. Norm은1보다 크며 contraction/global convergence
보증으로 쓰지 않는다. Ionization·number·energy는 각기 단위가 있는 별도
response row를 써야 하며 이 outgoing norm 하나로 모두 감싸지 않는다.

기존 \(J_s\)를 재계산하지 않고
\[
 \delta o=J_s\,\delta\theta+K_s\,\delta u
\]
를 두 고정 direction, 두 step으로 검사했다. 네 check는 모두 통과했다.
더 작은 step에서 일부 error가 증가한 원자료도 보존했다. 네 점을
asymptotic convergence evidence로 해석하지 않는다.

## 5. 동일 사건의 ionization·number·opposite energy

Ionization source의 입사 response는
\[
 \partial_uF=\beta^\top V_{0:2,:}/H
\]
이며 proper-time response는 \(H\partial_uF\)다.
Lyα 한 사건의 number response는
\[
 \partial_{u_j}N=3\times10^6\,{\rm LYA}\,H
 (K_{311,j}-\delta_{311,j})
\]
다. Incident subtraction의 Kronecker 항을 포함했다.
Radiation과 atomic energy는 같은 number event에 \(E_{21}{\rm eV_J}\)를
곱한 값과 그 음수다. 후보와 interval endpoint의 opposite 관계가 보존됐다.
이 부호 일치는 이 동일 사건의 bookkeeping 검증이며 full thermal/geometry
energy closure로 확대되지 않는다. 실제 배열은 EVENT_RESPONSE.npz에 있다.

## 6. 원 history admission의 새 결과

원 payload SHA256:
d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1.
전체7489knots, \(h=8.49\times10^{-5}\),
\(z_{\rm start}=1700.4825068138662\)다.
Target \(z=1099.9986525171403\), index5127에서는 prefix5127개,
즉0..5126만 사용할 수 있다.

4개 retained raw-member hash, energy grid, source hash, eta/index, 실제
source/target channel owner를 확인했다. Cosmology는 NPZ가 자체 저장하는
metadata가 아니므로 기존 input.dat/producer provenance와 scalar-density
consistency를 통해 \(T_0=2.728\)K,
\(n_{H0}=.18745798773143102\,{\rm m}^{-3}\)에 연결했다.

313개 query 모두 prefix 안의 linear cell에 있었다. 실제 cell range는
4770..5125이며 thermal prehistory query는0개다.
최소 upper-domain margin은
\(5.278877512893132\times10^{-8}\) in eta다.
향후 retiming perturbation은 이 매우 가까운 domain 경계를 고려해야 한다.
Latest knot 자체는 거절했고 마지막 cell 내부는 허용했다.

Stored incoming과의 최대 절대 차이는2.9030081312133234×10⁻²⁸,
공통 incoming scale9.018235185579106×10⁻¹⁴로 정규화한 최대 차이는
3.219042386314642×10⁻¹⁵다. 정확한 zero error8개도 그대로 보존했다.
이것은 discrete payload·query convention의 일치이며 독립 reference와의
physical error가 아니다. Different-cosmology finer trajectory를 넣는
경로도 거절했다.

## 7. 독립 검토·그림·실패 보존

같은 독립 reviewer가 식·source mapping·실제 code·raw arrays·PNG를 검토했다.
Preexec에서는 small RHS에서 Fraction oracle 비용을 빠뜨린 집계와,
중간 계산 완료 후 저장이 늦는 위치를 교정했다. 수정 전 코드와 diff를
보존했고 새 계산이나 허용오차 변경 없이 닫았다.

Primary는 첫 과학 실행에서 PASS했다. 첫 history residual 그림은 정확한
zero를1e-300으로 치환해 약300decade 축을 만든 표시 결함이 있었다.
원본을 보존한 채 saved data만으로 한 번 수정했다. 최종 그림은 실제 zero
8개와 symlog 선형 구간1e-20을 명시한다. Root와 같은 reviewer가 실제 PNG를
열어 최종 PASS를 기록했다.

- results/figures001/row_gain_norm.png — 최종 채택.
- results/figures002/joint_history_residuals.png — 최종 채택.
- results/figures001/joint_history_residuals.png — 최초 그림 보존.
- evidence/independent_review/FINAL_REVIEW.md — 독립 최종 판정.
- evidence/ROOT_FIGURE_REVIEW.json — root의 최초 표시 finding.

Wolfram generic inverse-residual/chain identities는3개 모두 True였다.
초기 symbol warning도 원 응답에 보존했다. 직접 증명과 독립 Fraction
검산이 따로 존재하며 CAS만을 성공 근거로 삼지 않았다.
문헌 도구와 읽은 범위는 LITERATURE_AND_CAS.md에 기록했다.

## 8. 실제 비용

|구간|Inclusive CPU s|Execution wall s|
|---|---:|---:|
|Primary1회|3.583830|3.625799492001534|
|최초 saved-data figures1회|2.128907|2.173025782991317|
|Saved-data layout 수정1회|1.817882|1.821194611999090|
|**Controlled science/figure child 합계**|**7.530619**|**7.620019886991940**|
|별도 measured saved-evidence readback|0.518211486|0.065538123002625|

Controlled child는1thread,RLIMIT_AS1GiB이며 최대 process RSS115188KiB다.
Large RHS639,small RHS10(numeric5+Fraction5),new IVP0,native runtime0,
old campaign replay0. Scientific repair/retry0.
측정된 review overhead를 보수적으로 합하면8.048830486CPU s다.
이는 full-turn elapsed나 모든 준비/도구IO 시간을 측정했다는 뜻이 아니다.
Remote CAS CPU와 더 오래된 미측정 비용은 UNKNOWN으로 유지한다.
기존 알려진 lineage24.120157CPU s도 그대로 이어받는다.

## 9. 전체 목표의 DAG와 남은 실제 의무

원40contracts/17integration edges/7authorities를 보존했다.
중앙 a28ba snapshot의 plan_status는 PROPOSED34,COMPLETE_SCOPED2,
PARTIAL2,OWNER_DELIVERY_PENDING1,SOURCE_INPUT_PENDING1다.
이 숫자를 전체 물리 목표의 완료율로 바꾸지 않았다. 기존 node 배열은
저장소별 묶음이며 global topological order가 아니다. 설명용 dependency
union은 local31+integration17+internal conditional2=50links이고,
cycle 없이19/9/6/4/2개의5층으로 정렬된다.
40개 row와 각 layer/status는 GLOBAL_PROGRESS.md에 있다.

실제 REC 선행 경로는 REC-LINE02→REC-HISTORY→REC-COUPLED,
REC-LINE02→REC-FIELD→REC-COUPLED,REC-LI→REC-COUPLED다.
선택된 native line/actual spectrum 조건에서는 REC-LINE02 또는
REC-FIELD→REI-L1→REI-L4→REI-L5로 연결된다.
H5/H6/H7은 REC-HISTORY 내부 의무이며 새 중앙 node를 만든 것이 아니다.

다음 연구는 같은 source/cosmology의 독립 reference와 uncertainty 또는
정당화된 whole-cell curvature/defect+endpoint bound를 확보해야 한다.
다른 owner의 H6 retiming 최신 결과를 먼저 읽고 중복 없이 actual trace/
frame owner를 붙여야 한다. 그 뒤에 국소 [J_s,K_s]와 실제 history pullback,
retiming/geometry/thermal-ODE를 합성한다. 입력·가설·오차 allocation·acceptance·
누적 budget을 새로 동결해야 하며, 이 인계가 새 IVP/native/merge/activation
승인은 아니다. 자세한 조건은 NEXT_INPUT_CONTRACT.md에 있다.

Physical HOLD,REC_U5 HOLD_9_FAIL/HOLD_8_FAIL,CLOSED_HOLD_NOT_RESET,
global_convergence NOT_RUN,production NOT_APPROVED,REI_activation=false,
첫 실패 REI raw HISTORICAL_LOCAL_ONLY를 유지한다.

