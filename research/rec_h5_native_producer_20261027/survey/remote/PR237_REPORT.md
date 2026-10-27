# REI 조건부 열적 결합 연구 결과 — 2026-10-27

## 결과와 승인 범위

**기준밀도와 에너지 소유권을 동결한 25변수 국소 source를 구성·구현했고, 새 검사 118개가 모두 통과했다.** 저장된 PW19 HeII 배경의 광이온화 source에 native REC RR/DR 냉각, Planck-reference Compton, fast 전자의 수·에너지 동시 열적 편입을 결합했다. 실제 변경 없는 HE caloric caller의 결과와 새 온도 source가 일치한다. 독립 수치 검토와 그림 검토의 차단 사항은 0개다.

채택 판정은 **PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE**다. 실제 배경 위에 구성한 fast pool과 지정된 에너지 독립 완화율을 쓰는 국소 구성 결과다. 이 완화율을 실제 물리 stopping provider로 승격하지 않는다. 원본 DAG의 **working 32/88, central 27/88**을 보존하고, REC-COUPLED는 PARTIAL로 둔다. 이번 완료수 증분은 0이다. 연구 루프 R1–R10 및 코딩 루프 C1–C10의 이번 유한 단위와 원본 DAG 완료수는 서로 다른 집계다.

과학적 승인 근거는 [ADMISSION.json](ADMISSION.json), [C9 독립 검토](review/C9_REVIEW.md), [보존 원자료](implementation/attempt01/stdout.json)에 모았다. 게시·백업의 실제 commit·ZIP digest·provider ACK는 [최종 전달 영수증](delivery/FINAL_DELIVERY_RECEIPT.json)에 별도로 기록한다. 이전 단계 파일의 PENDING 표시는 당시 상태이며, 그 역사적 기록을 사후 성공으로 고쳐 쓰지 않는다.

## 1. 최신 자료 조사와 baseline 선택

고정 인계서 [78f7ac58의 HANDOFF_KO.md](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/78f7ac5864d5817ceb79b48cb5e298cc30006510/research/program_expansion_20261025/HANDOFF_KO.md)를 출발점으로 삼았다. 이후 PR236의 실제 최신 HEAD **ee94bef85b56d879dc38f184856a5c613575e9e1**과 source ZIP을 복구하여 현재 기준으로 정했다. 복구 ZIP은 3,477,069 bytes, 307 entries, CRC PASS, SHA256 **1b80efed0892f3368dc307e3cd6757b93dc444a4d7d2d186b352b926e230648a**다. Dropbox 실제 bytes와 Drive의 동일 크기 metadata를 대조했다.

| 조사 대상 | 실제 조사 범위 | 확인 한계 |
|---|---|---|
| REI | 278 branch metadata, 235 PR metadata; 최근 15 PR의 파일 목록 1,783개 언급/1,735개 고유 경로 | 모든 과거 branch의 모든 source 본문을 읽었다는 뜻은 아니다 |
| 6개 공급자 | WU159, REC156, CR184, HE107, BASS277, VigilODE215: 합계 1,098 branch metadata | 총 7 repo 1,376 branch metadata를 입장 시점에 페이지 끝까지 조사 |
| 최근 공급자 PR | Oct25 이후 갱신 20 PR의 범위와 필요한 실제 source | 최신 50개 정렬이 이전 날짜까지 도달했음을 확인 |
| 보존본 | REI Dropbox folder 최초 181 entries; 뒤이어 상위 백업 트리 185 entries와 pagination 종료 확인 | 두 숫자는 서로 다른 범위·시점이며 합산하지 않는다 |
| 최근 파일·대화 단서 | Oct25 이후 파일 metadata 319개 전 페이지; 관련 연구 metadata 67개; 두 번의 대화 문맥 검색 | 대화 전체 export는 아니다. 기억은 실제 source/receipt로 확인한 항목만 채택 |
| Drive | 원 영수증의 정확한 file ID로 metadata 재확인 | keyword 검색만으로 모든 Drive 파일을 조사했다고 주장하지 않는다 |
| native desktop | cosmosapjw offline 관측 | 게시되지 않은 local dirty state는 UNOBSERVED다 |

조사 자료는 [REI 조사](intake/rei/SURVEY_KO.md), [공급자 조사](intake/suppliers/REPORT_KO.md), [수급 호환성](intake/suppliers/SUPPLIER_COMPATIBILITY.json), [88개 노드별 집계 근거](intake/rei/CANONICAL_COMPLETION_LEDGER_20261027.json)에 보존했다. 완료수는 status 문자열 접두어를 세어 얻지 않았다. working의 추가 5개 인정 노드와 중앙의 27개 인정 노드를 각각 보존했다. H5의 실제 bound 0/313은 PASS_DERIVED만으로 완료 처리하지 않는다.

### 세션 중 도착한 최신 반환

중앙 HEAD는 **12f6007a83a40d76f80574e41a5402676e81fc7a**로 진행했다. BASS의 midpoint/final transport 반환이 세 원본 노드의 부분 관측을 바꿨고, 완료수는 27/88을 유지했다. 이 세 관측을 working DAG에도 그대로 이식하고 REC-COUPLED의 이번 조건부 결과만 추가했다.

- **WU bfdeed6766…**: EXFOR He4(gamma,d)D를 포함한 원래 28방향의 source-reference coverage가 28/28이다. registry coverage를 rate·Q·consumer admission으로 바꾸지 않는다.
- **BASS af14fc72d9…**: 같은 저장된 제조 모델의 512 midpoint/final map과 2개 최종 geometry RHS, 10개 focused check를 재사용했다. 새 IVP는 0이다. physical geometry radius는 null, native finite absorption은 0, calibrated geometry는 열린 상태다.
- **CR 1c88ba4b0f…**: 게시 직전 확인한 고정 HEAD에서 HeIII ground-state tagged-fast 포획은 R10·C6까지 16/20 단계다. 실제 변경 controls 36/36(소규모 fixture 56 RHS와 analytic 5 RHS)이 통과했고, C7의 primary 224 RHS 및 C9 consumer 채택은 아직 남았다. 이 사건은 fast 전자와 ionic charge를 함께 1개 줄이고 retained photon을 만든다. thermal number·thermal heat·external transfer ledger 변화는 0이다. retained photon은 별도 port를 필요로 한다. 실제 export의 nb와 source rate·exposure·instantaneous RHS는 null이다. native RR capture hazard λ(E)를 이번 thermal assimilation ν로 바꾸지 않는다. 자세한 고정 HEAD 근거는 [최종 CR delta](intake/FINAL_CR_DELTA.md)에 있다.
- **VigilODE V6**: 1,223,513-byte source ZIP의 SHA256과 Dropbox 실제 bytes를 확인했고, 늦게 도착한 Drive ACK도 정확한 file ID로 확인했다. Git 게시 ACK는 여전히 owner 측에서 확인되지 않았다. actual-point binding 결과를 새 25변수 열적 source의 certificate로 재사용하지 않는다.

자세한 원문·소유권·예산 경계는 [최신 공급자 delta](intake/PRE_RUN_SUPPLIER_DELTA.md)와 [늦은 병렬 반환](intake/LATE_PARALLEL_RETURNS.json)에 있다. 이들은 기존 main·new83·HE·CR·V6 예산을 재설정할 근거가 아니다.

## 2. 동결한 정규화와 실제 입력

21개 이온/핵종 abundance와 네 부가 좌표를 사용한다.

\[
Z=(Y[21],\zeta,w_{\rm nt},w_{\rm ext},\ell),\qquad
Y_i=n_i/n_b,\quad
\zeta=n_{\rm nt}/n_b,\quad
w=u/n_b,\quad \ell=\log(T/{\rm K}).
\]

에너지 좌표의 단위는 J/baryon이다. \(w_{\rm ext}\)는 signed external radiation transfer ledger이며, 별도로 진화하는 radiation energy density와 동일시하지 않는다.

\[
r=n_{\rm ref,0}a^{-3},\qquad n_b=\beta r,\qquad
x=\beta Y,\quad \xi=\beta\zeta,\quad \omega=\beta w .
\]

| 입력 | 동결값/의미 |
|---|---|
| 선택 source | PW19 z2.479 HeII exclusive; He3II/He4II 전이의 isotope 전자는 기존 조건부 동일성 유지 |
| 실제 저장 배경 | \(z=2.479,\ T=14919.863839279506\ {\rm K}\) |
| baryon density | \(n_b=10.669321142818111\ {\rm m^{-3}}\) |
| reference density | \(r=8.033643390985384\ {\rm m^{-3}}\) |
| 정규화 비율 | \(\beta=1.328080003500061\) |
| clock | \(H=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\) |
| photon/primary support | 54.42…50000 eV / 0…49945.58 eV |
| 제조 fast pool | \(\zeta=(q\cdot Y)/4=0.2191163469802296\), \(w=7.010531745782858\times10^{-19}\) J/baryon |
| 지정 완화율 | \(\nu=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\), H와 수치만 같고 미분에서는 독립 |
| atomic/Mao 공동 온도 범위 | 100…\(10^6\) K |
| nuclear 비활성 행 | neutron/tritium index 0,5,6 및 그 tangent가 정확히 0 |

source moments와 배경은 기존 bytes를 재사용했다. spectrum 재구성, quadrature, donor interpolation, source history integration을 하지 않았다. 두 fast moment를 정했다고 monoenergetic 분포를 가정한 것도 아니다.

밀도량인 처음 24행만 \(n_b\) 또는 \(\beta\)로 곱한다. logT 행은 이 곱셈에서 제외한다. \(\eta\) clock에서는 25행 모두 \(1/H\)를 적용하고 그 미분을 포함한다. reference 입력의 reservoir tangent까지

\[
\delta Y={\delta x-Y\,\delta\beta\over\beta},\quad
\delta\zeta={\delta\xi-\zeta\,\delta\beta\over\beta},\quad
\delta w={\delta\omega-w\,\delta\beta\over\beta}
\]

로 전달한다.

변하는 일반 physical reference의 연속방정식을 \(\dot r+3Hr=R_r\), 물리 밀도의 연속방정식을 \(\dot n+3Hn=S\)로 쓰면, \(x=n/r\)의 quotient는

\[
F_x={S-xR_r\over r},\qquad
\delta F_x={\delta S-R_r\delta x-x\delta R_r\over r}
           -F_x{\delta r\over r}.
\]

두 연속방정식의 공통 dilution 항이 상쇄되어 위 식이 나온다. 따라서 고정 comoving reference \(r=n_{\rm ref,0}a^{-3}\)에서는 \(R_r=0\)이다. 이 보정과 미분을 명시적인 algebra control로 구현·검증했다. 이 식의 통과가 expansion pressure work나 전체 Bianchi evolution을 새로 계산했다는 뜻은 아니다.

## 3. 구성적 결과: 수와 에너지를 함께 넘기는 국소 source

\(q\)를 이온 전하 벡터, \(I\)를 native binding-energy 벡터라 하자.

\[
g=q^TY-\zeta,\qquad
\chi=(1+q)^TY-\zeta,\qquad
n_{e,\rm th}=n_bg,\qquad
U_{\rm th}=c_vn_bT\chi,\quad c_v=3k_B/2.
\]

비열적 전자는 이미 ionic charge가 요구하는 전체 자유전자 안에 속한다. \(\zeta\)를 다시 전하에 더하지 않는다. native thermal RR/DR 및 Compton에 쓰는 전자밀도는 \(n_bq^TY\)가 아니라 \(n_bg\)다.

에너지에 무관한 지정 \(\nu\ge0\)에 대해

\[
(\partial_t\mu_{\rm nt})_{\rm A}=-\nu\mu_{\rm nt}
\]

를 선택하면, 임의의 양의 유한 count measure와 유한 first moment에 대해 정확한 두 transfer moment는

\[
j=\nu\zeta,\qquad h=\nu w
\]

다. 수와 에너지를 fast store에서 빼고 bath에 동시에 준다. 이 조건 아래 고정된 두 moment만으로 transfer가 닫힌다.

native photo \(P,e_\gamma,k_\gamma,a_\gamma\)를 재사용하고,

\[
e_\gamma=q^TP,\quad {\bf1}^TP=0,\quad
I^TP+k_\gamma-a_\gamma=0
\]

를 유지한다. thermal RR/DR은 공급자의 기존 coefficient helper로

\[
R_s=n_{e,\rm th}G_s(T)Y,\qquad
L_s=n_{e,\rm th}Y^T\kappa_s(T),\qquad
R=\sum_sR_s,\quad L=\sum_sL_s
\]

로 계산한다. \(L_s-I^TR_s\)가 해당 재결합의 escaping-radiation partner다. Mao2017 RR kinetic factor × 기존 native rate의 hybrid 성격과 signed DR fit의 전체 positivity/mask 처리를 보존한다.

Planck reference는 \(T_r=2.7255/a\), 그 자체의 blackbody energy density를 사용한다. unrelated UV Compton을 합하지 않는다. source의 전체 식은

\[
\begin{aligned}
F_Y&=P+R,\\
F_\zeta&=e_\gamma-j,\\
F_w&=k_\gamma-h,\\
F_{\rm ext}&=-a_\gamma-q_C+L-I^TR,\\
F_\ell&={ (h+q_C-L)/(c_vT)-q^TR-j\over\chi}.
\end{aligned}
\]

여기서 \(q_C\)는 baryon당 Compton power다. 따라서

\[
\dot\chi=q^TR+j,\qquad
c_vT(\chi F_\ell+\dot\chi)=h+q_C-L
\]

이며,

\[
I^TF_Y+F_w+F_{\rm ext}
+c_vT(\chi F_\ell+\dot\chi)=0.
\]

결합에 따라 photo primary energy는 fast store로, assimilation heat는 bath로, binding energy와 escaping/CMB photon transfer는 지정 ledger로 각각 한 번만 이동한다.

### 실제로 추가한 caloric 항

고립된 assimilation의 온도 source는

\[
F_{\ell,\rm A}={\nu\,[w/(c_vT)-\zeta]\over\chi}.
\]

에너지만 추가하면 \(-\nu\zeta/\chi\)가 빠진다. 낮은 입자당 에너지를 가진 전자가 bath에 들어오면, 양의 에너지 전달과 동시에 평균 온도가 내려갈 수도 있다. 이는 caloric energy와 입자수의 곱 미분에서 직접 나온다.

JVP도 모든 source partner와 quotient에 적용했다. \(q_{\rm th}=h+q_C-L,\ c_{\rm th}=q^TR+j\)라 두면

\[
\delta F_\ell=
{(\delta q_{\rm th}-q_{\rm th}\delta\ell)/(c_vT)-\delta c_{\rm th}\over\chi}
-F_\ell{\delta\chi\over\chi}.
\]

전체 native rate·cooling·Planck a/logT derivative와 \(n_b,\beta,r,H,\nu\) 방향을 유지한다. 유도와 코드 대응은 [구성적 유도](theory/THERMAL_JOIN_DERIVATION.md), [동결 계약](theory/ROOT_FROZEN_CONTRACT.md), [thermal_join.py](implementation/thermal_join.py)에 있다.

### 조건부 closure의 정확한 한계

\(\mu_1=\delta_{2E_0}\), \(\mu_2=(\delta_{E_0}+\delta_{3E_0})/2\)는 count와 first moment가 같다. constant \(\nu\)에서는 두 transfer가 같지만 \(\nu(E)=\nu_0E/E_0\)에서는 energy transfer가 \(4\nu_0E_0\), \(5\nu_0E_0\)로 다르다. 이는 그 대안 closure에서 추가 에너지 moment가 필요함을 보이는 구체적 예다. 모든 물리적 축약을 배제하는 strong no-go나 새 문헌 novelty claim으로 채택하지 않는다.

Furlanetto–Stoever의 energetic-electron deposition 연구와 Mao–Kaastra–Badnell의 RR kinetic-loss 연구를 Exa·SciSpace로 원전 대조했다. 전자는 energy/ionization-dependent deposition 맥락을, 후자는 native kinetic cooling의 provenance를 제공한다. 어느 원전도 이번 임의 \(\nu\)의 전 PW19 support 물리적 보증으로 쓰지 않았다. 원전과 도구 기록은 [SOURCE_FINDINGS.md](theory/SOURCE_FINDINGS.md)에 있다.

- Furlanetto & Stoever (2010), MNRAS 404, 1869–1878, [doi:10.1111/j.1365-2966.2010.16401.x](https://doi.org/10.1111/j.1365-2966.2010.16401.x).
- Mao, Kaastra & Badnell (2017), A&A 599, A10, [doi:10.1051/0004-6361/201629708](https://doi.org/10.1051/0004-6361/201629708).

## 4. 공급자 결합의 실제 의미와 유효범위

| 공급자/기존 결과 | 이번 unit에서 사용하는 것 | 유지하는 한계·소유권 |
|---|---|---|
| WU event | 기존 event/state/energy 계약, 비활성 n/T와 원본 event owner | registry source coverage는 미자격 rate를 활성화하지 않는다 |
| REC opacity·native thermal | GRID044 및 PR236 PW19 source bytes, native RR/DR kinetic coefficient, Planck Compton | H1 primary measure와 현재 HeII source를 혼동하지 않는다. isotope·fit·temperature 전제 유지 |
| CR external source | 기존 source provenance, 최신 tagged-fast capture를 별도 가능한 event로 분류 | retained photon은 thermal heat·external escape와 다르다. owner의 미완료 224-RHS 작업을 대신 실행하지 않는다 |
| HE degradation/caloric | 변경 없는 실제 monatomic_caloric/temperature_rhs: 21 ion + 1 thermal-electron row | 새 물리 stopping kernel은 없다. 두-Maxwellian 열교환 fit을 비열적 전 support로 외삽하지 않는다 |
| BASS transport | 기존 finite14/manufactured transport와 새 512 저장 map 반환을 partial observation에 결합 | finite-grid 일치와 continuum 일치 구별; physical radii/finite absorption/calibrated geometry 열린 상태 |
| VigilODE client | 기존 V6 actual-point binding·JVP protocol·저장 evidence 재사용 | 이번 source의 full Jacobian·history certificate가 아니다. native integration/V7/V8 열린 상태 |

실제 HE 호출은 공통 rest frame에서 이 source increment의 expansion·shear·divq를 0으로 둔다. ion source는 \(n_b(P+R)\), thermal electron source는 \(n_b(q^TR+j)\), thermal power는 \(n_b(h+q_C-L)\)로 전달한다. 서로 다른 stored scenario의 온도·밀도·에너지 support를 같다고 선언하지 않는다.

## 5. 새 실행과 검증 결과

동결 source·checker·runner·35개 입력 manifest를 C5 commit **20b91606493fb7bad015c62fd62e2faa971faee0**에 먼저 게시했다. C5 independent review와 Drive/Dropbox ACK 후 root의 [EXECUTION_GO](implementation/EXECUTION_GO.json)에 따라 딱 한 번 실행했다.

명령은 복원 repository root에서 다음과 같았다.

    /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/run_bounded.py

runner가 정확한 checker만 실행했다. Python 3.12.14, one worker, BLAS/OMP one thread, 1.5 CPU s / 8 wall s / 512 MiB 계약이었다. exit 0, stderr empty, 118 distinct checks PASS다. 재실행·repair·criterion 변경은 0이다.

| 검증 | 관측 최대 scaled residual | 동결 기준 |
|---|---:|---:|
| algebra/native/HE | \(3.3297273737548715\times10^{-16}\) | \(2\times10^{-14}\) |
| 네 map의 JVP 대 centered FD | \(1.373105919989494\times10^{-10}\) | \(2\times10^{-8}\) |
| 실제 HE \(Tdot/T\) 대 새 source | 0 | \(2\times10^{-14}\) |

FD 두 step은 같은 mixed direction과 사전에 정한 같은 row-unit analytic operand scale을 사용했다. max(1,tiny)로 작은 물리량을 덮지 않았으며, 정확한 zero 행 0,5,6은 별도로 판정했다.

| map | \(h=2\times10^{-4}\) | \(h=10^{-4}\) |
|---|---:|---:|
| proper time | \(8.539441405764767\times10^{-11}\) | \(5.833296609399081\times10^{-11}\) |
| physical density | \(1.373105919989494\times10^{-10}\) | \(1.0097271786836361\times10^{-10}\) |
| reference normalization | \(8.693577663494068\times10^{-11}\) | \(2.3294450982679987\times10^{-11}\) |
| eta clock | \(6.865869718517768\times10^{-11}\) | \(2.4467898344279536\times10^{-11}\) |

두 step의 통과가 보장하는 것은 이 state·direction에서의 판별이다. 모든 행이 factor-four로 감소한다는 점근 수렴률이나 전 상태 Jacobian 인증을 주장하지 않는다.

검사는 source-off, \(\nu=0\), empty fast pool, \(g=0\) 경계와 잘못된 owner·support·temperature·n/T 활성화 거부를 포함한다. 실제 \(T_r=9.4820145\) K의 Compton 평형은 Compton helper만 검사하여 REC의 100 K 하한을 침범하지 않았다. all-electron RR/DR/Compton 대입, caloric count 누락, logT 밀도 곱셈, reference/clock 미분 누락을 실제로 구별했다. 에너지 보존은 독립 transition-flux/physical caloric oracle과 실제 HE caller로 대조했다.

### 저장된 배경 + 제조 fast pool에서 관측한 값

| 양 | 값 |
|---|---:|
| thermal electron density | 7.013468020719699 m⁻³ |
| 전체 charge-derived electron density | 9.351290694292933 m⁻³ |
| photo primary → fast store | \(7.949751527088791\times10^{-37}\) W m⁻³ |
| fast store → bath | \(6.103746165608298\times10^{-35}\) W m⁻³ |
| RR kinetic loss | \(-4.0749095689223304\times10^{-36}\) W m⁻³ |
| DR kinetic loss | \(-3.9721389300608827\times10^{-50}\) W m⁻³ |
| Planck Compton | \(-8.60381044771227\times10^{-36}\) W m⁻³ |
| net thermal power | \(4.835874163944834\times10^{-35}\) W m⁻³ |
| thermal number source | \(-6.3066313402445626\times10^{-18}\) m⁻³ s⁻¹ |
| full proper logT source | \(1.0366275271463654\times10^{-17}\) s⁻¹ |
| 고립 assimilation의 정확한 logT source | \(1.1362647900564959\times10^{-17}\) s⁻¹ |
| heat-only 식 | \(1.2577296083838885\times10^{-17}\) s⁻¹ |
| 빠지는 count 항 \(j/\chi\) | \(1.2146481832739274\times10^{-18}\) s⁻¹ |

fast store가 현재 photo injection보다 큰 power를 내놓을 수 있는 것은 만들어 둔 저장 에너지가 있기 때문이다. 이 state의 과거 이력을 유도하지 않았다. 현재 source에서 RR에 의한 electron 제거가 fast-pool 수 편입보다 커서 thermal-number source는 음수다.

![저장된 결과의 power ownership과 FD 오차](delivery/figures/THERMAL_ASSIMILATION_LOCAL_SOURCE.png)

PNG/PDF와 plot data는 저장된 stdout만 사용한 별도 presentation 실행에서 만들었다. 실제 그림을 root와 독립 검토자가 열어 보았고 값·범례·조건부 범위·읽기성을 확인했다. [시각 검토](review/C9_VISUAL_ADDENDUM.md)는 과학 재실행 없이 완료했다.

## 6. 재사용과 예산 보존

PR219 bootstrap, 기존83, GRID044 opacity, PR221 조건부 ANGTHERM, PR233 source, PR235 normalization/moving-reference, PR236 native photo/JVP의 관련 identity가 유지되는 근거를 재사용했다. 기존 suite, 새83 전구간, NCP, 새 IVP, spectrum quadrature는 실행하지 않았다. PR236 CI의 cargo fmt 실패는 관련 없는 Rust 형식 변경으로 분류했고, skip된 tests를 과학 실패나 성공으로 세지 않았다.

| 항목 | 실제 비용·정책 |
|---|---|
| 새 과학 child | 0.511638 CPU s |
| wrapper | 0.053470553 CPU s |
| 측정 합 | 0.565108553 CPU s |
| 보수적 tail 0.02 포함 debit | 0.585108553 CPU s |
| wall / 최대 RSS | 0.543386674 s / 27080 KiB |
| 그림 측정 / tail 포함 | 2.222084095 / 2.252084095 CPU s |
| 그림 wall / 최대 RSS | 2.201134078 s / 87248 KiB |
| main | 595.225063/600 CPU s, NO_MORE_IVPs 유지 |
| planning | 원 cap10에서 일시14.9; unit 종료 후10으로 복원하며 누적 debit 보존 |
| presentation | 원 cap30에서 일시44.5; unit 종료 후30으로 복원하며 누적 debit 보존 |

현재 unit의 알려진 세부 비용은 [BUDGET_STATUS.json](BUDGET_STATUS.json)에 합산한다. 원격 도구·LLM·미측정 초기화/serialization tail 및 과거 미확인 비용은 UNKNOWN_NOT_ZERO다. 허용 cap 복원은 누적 사용량을 0으로 만드는 행위가 아니며, 복원 뒤 원 cap을 이미 넘는 알려진 누계도 그대로 남긴다. HE101 reserve0와 V6 closed lease를 유지한다. 최종 CR owner 영수증이 보고한 새 unit 누계는 0.701900185/30 CPU s이며, 이 비용·남은 reservation을 REI 예산으로 전용하지 않는다.

기계적 구현자는 thread-limit 이후 재사용한 기존 Astra agent다. 이를 lower-tier 실행으로 가장하지 않았다. root는 식·범위·GO·채택을 맡았고, 구현자와 다른 검토자가 code·원자료·그림을 검토했다. 배치나 계층 변화의 실제 경위는 policy 기록에 남아 있다.

## 7. DAG, 단계별 게시·백업과 재개점

원본 88개 ID, 17개 top-level edge, nested contract·dependency·authority·conditional gate를 보존한다. 변경은 REC-COUPLED의 이번 부분 결과와 중앙에서 도착한 BASS 3개 부분 관측에 제한했다. 기존 selectedRuntimeContract/photo 관측을 유지하고 thermalAssimilationContract를 별도 연결한다. [DAG_UPDATE_RECEIPT.json](DAG_UPDATE_RECEIPT.json)과 독립 scope review가 그 비교를 남긴다.

각 R/C 단계는 [STAGE_LEDGER.md](STAGE_LEDGER.md)에 완료 근거, **32/88**, 게시 commit, ZIP/Drive/Dropbox ACK를 연결한다. 서로 같은 immutable evidence를 사용하는 단계는 하나의 실제 검증된 checkpoint를 공유한다. 단계 수만큼 같은 과학 실행이나 같은 source archive를 반복하지 않는다. 최종 source와 뒤따르는 delivery metadata는 분리해 ZIP 자기 hash를 내부에 거짓으로 만들지 않는다.

다음 재개는 최신 HEAD·AGENTS·병렬 반환·이중 백업을 다시 읽는 intake에서 시작한다. 구체적인 열린 작업은 다음과 같다.

1. **물리적 finite-time transfer**: 실제 \(J_N[\mu],Q[\mu]\) 공급자와 대상 에너지 support·온도·밀도·오차·미분을 자격화한다. energy-dependent kernel이면 필요한 measure/moment를 그대로 들고 가며 임의 \(\nu\)를 empirical rate로 고쳐 부르지 않는다.
2. **CR retained-photon 연결**: owner가 완료한 tagged-fast capture 반환이 생기면 그것의 누적 count/energy를 그대로 받아 별도 photon port에 매핑한다. source duration/exposure가 없는 probability를 rate로 변환하지 않는다.
3. **BASS–VigilODE 실제 경로**: 동일한 scenario의 transport/geometry radii, retained radiation, native finite absorption과 새25-state source/JVP의 실제 client binding을 구성한다. 기존 V6 point certificate와 전체 경로 보증을 구별한다.
4. **whole-network/L4**: 모든 공급자 유효범위, rate/Q/escape/secondary channel, uncertainty transport, source-matched evolution과 관측량 gate를 독립적으로 닫은 뒤 판단한다.

이 unit의 닫힌 118검사나 원래 83을 자동으로 재실행할 이유는 없다. 관련 입력·식·code identity가 바뀌었을 때 영향받는 최소 검사부터 새 bounded 계약을 만들고, 누적 예산을 이어간다. 복사 가능한 다음 대화 지시는 [HANDOFF_KO.md](HANDOFF_KO.md)에 제공한다.

