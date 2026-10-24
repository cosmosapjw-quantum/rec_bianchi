# REC-HISTORY-THERMO01 — 6개 primitive에 대한 국소 source Jacobian

## 결과와 주장 범위

원래 HyRec FULL source의 `z=1099.9986525171403` 보존 상태에서 `(xe, xHII, ln TR, ln TM, ln nH, ln H)`에 대한 **314×6 outgoing 미분, 313×6 대수 상태 미분, 이온화 source 및 단일 Lyα 사건의 수·에너지 미분**을 구현하고 동결한 A–F 수치 기준을 모두 통과했다. Incoming313, energy grid, source frame, geometry와 characteristic query 시각은 고정했다. 최종 독립 검토와 root 판정은 `evidence/independent_review/FINAL_REVIEW.md`, `CLAIM_GATES.json`을, 실제 게시·백업은 `delivery/PUBLICATION_STATE.json`과 후속 companion receipt를 따른다.

이번 결과는 H7의 **국소 thermodynamic coefficient block**이다. 실제 history의 물리적 오차 상한 H5, Bianchi 방향·frame·입사 trace H6, 전체 history/geometry/thermal-ODE 결합 Jacobian은 계속 열려 있다. 부모 `REC-HISTORY=PARTIAL`; Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false 및 최초 실패 REI raw의 HISTORICAL_LOCAL_ONLY를 유지한다. 전체 목표의 완료율은 null이다.

## 1. 최신 조사와 이번 문제의 선택

접근 가능한 owner 저장소51개 목록과 빈 마지막 페이지를 확인했다. 최초 관련8repo branch census는1629개였다. 환경 복구 뒤 최신 목록은 REC153 + 다른7repo1480 = **1633개**이며, REC의 추가1개는 이번 THERMO branch다. REC 기존152head 변경0·삭제0이다. 원래 REC134PR 전체 목록과 현재 새PR135를 구분했다. 다른 전체 비공개 대화나 모든 branch의 모든 파일을 읽었다는 의미는 아니다.

기존56개 REC source/input payload를 immutable Git identity로 복원했다. 다른 repo의 선택 원문17개는 환경 소실 후 원commit에서 다시 가져와17/17 blob을 확인했다. 후속 owner 원문7개도7/7 확인했다. 대화 검색, Dropbox direct116/recursive156 metadata, Drive 전용 폴더 목록과 과거 ACK, 첨부20개435180795bytes의 identity/선택 내용을 조사했다. Drive의 관측하지 못한 페이지와 과거 UNKNOWN upload는 성공으로 바꾸지 않았다. 상세범위는 SURVEY_SYNTHESIS_KO와 provenance/LATE_DEPENDENCY_SYNTHESIS 및 source_intake 기록에 있다.

새 HE99 finite-mass shell은 운동학 범위이고 physical amplitude/provider는 미정이다. HH145 atomic-to-bare remap은 conditional finite-window 결과이며 physical source CI·consumer admission을 발급하지 않는다. CR103의 EI energy finite-chain은 자신의 global_error_bound와 REC physical epsilon을 null로 유지한다. Vigil86은 고정 Riccati 제조모델의 Bernstein defect·inherited radius·query-rounding 인증을 완성했지만 actual REC source/Jacobian provider는 아니다. 이들 결과를 재실행하지 않고 현재 입력의 역할을 구별했다.

BASS B3C는 Git에 게시되지 않은 실제 백업도 추적했다. Dropbox `id:BSpOijBcT10AAAAAAD_9hw`의7021644bytes ZIP을1회 받아 SHA256 `0d3a911d7fc1b567c0e915cd655af94bff44495849bd0e7ce1bcb778a94bd1b2`를 확인하고 handoff/admission2파일만 읽었다. Cold/recoil-free detached f_plus=0 LINE01, diagonal BianchiI finite14cohort의 proper-clock·matter-rest tetrad·midpoint/newborn half-transport는 H6 설계에 재사용할 구체적 근거다. Native finite absorption incident trace와 full calibrated REC history는 명시적으로 NOT_ADMITTED다. Owner의12IVP는 이번 실행이 아니다.

**실제 원래 history도 존재한다.** `data/pr05b2_source_history_v060.npz`, Git blob `de43b1a2642fa0aa049abbfd1b0a7d775d684b1b`,35239470bytes, 기록된 SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`를 찾았다. Provenance는 accepted7489,dlna8.49e-5,nvirt311,nlyman3를 기록하며, 별도 저장 ledger의 target z1099.9986525171403는 index5127/313queries다. 이번에는35MB 배열 자체를 로드하지 않았다. h/2 U4와 h/4 R3Q 등의 실제 finer 후보도 있다. 다만 target coverage와 source/cosmology가 다르거나 독립 reference/endpoint uncertainty·whole-cell curvature가 없으므로 same-h parity나 storage equivalence로 시간보간 오차를 인증하지 않았다.

그 결과 H5를 허위 완료 처리하지 않고, 이미 source가 결속된 H7의 국소 coefficient dependence를 이번 유한 작업으로 선택했다. 새 IVP와 과거 campaign은0이다.

## 2. 이론에서 코드로 연결한 식

대수 상태를 X=(xr2s,xr2p,xv0,…,xv310)라 쓰고, 고정 incoming을 u라 쓰면

$$M(\theta)X=s(\theta,u),\qquad M X_k=s_k-M_kX.$$

Outgoing map o=T X+P u의 미분은

$$o_k=T X_k+T_kX+P_ku.$$

단순히 이전 frozen incoming response를 다시 호출하면 M_k,T_k,P_k에 따른 변화가 빠진다. 이번 구현은 native interpolation rates, Saha·detailed-balance factors, line escape, 두광자/Raman 및 diffusion recurrence, gamma/tau, source와 outgoing의 모든 국소 coefficient 의존성을 함께 미분한다. Gamma는 native 코드처럼 Lyα 이웃139/140 coupling adjustment 전에 만든다.

온도율 table의 자연 좌표가 r=TM/TR,lnTR이므로

$$\partial_{\ln T_M}A=rA_r,\qquad
\left.\partial_{\ln T_R}A\right|_{T_M}=A_{\ln T_R}|_r-rA_r.$$

`DAlpha`는 A−Aeq이며 미분 기호가 아니다. xe와 xHII는 국소 source의 독립 ambient 인자로 다루며, physical pure-H tangent는 dxe=dxHII 제한으로 얻는다. 따라서 순수H의 물리적 이온화 방향은 두 열의 합이다. 독립6열을6개의 독립 우주론 궤적으로 해석하지 않는다.

x=1−xHII, S=C_S TR^(3/2)exp(−EI/TR), C_l=nH A_l xe xHII−S Aeq_l x라 두면

$$F=\frac{dx_{HII}}{d\ln a}=-\frac{\sum_l C_l-\sum_l\beta_lxr_l}{H},$$
$$F_k=-\frac{\sum_l C_{l,k}-\sum_l(\beta_{l,k}xr_l+\beta_lxr_{l,k})}{H}-F(\ln H)_k.$$

단일 Lyα 사건의 순광자율은 Rγ=G_N H(o311−u311), G_N=3e6·LYA_FACT m^-3이며

$$R_{\gamma,k}=G_NH\{o_{311,k}+(o_{311}-u_{311})(\ln H)_k\}.$$

동일 사건의 radiation energy는 +E21_J Rγ,k, atomic energy는 −E21_J Rγ,k다. Outgoing 저장을 두 번째 방사 source로 더하지 않는다. 이 장부는 전체 gas thermal equation이나 angular collision law의 완성을 뜻하지 않는다.

HyRec의 atom/radiation coupled source 배경은 [Ali-Haïmoud & Hirata 2011](https://arxiv.org/abs/1011.3758), 후속 구분은 [HyRec-2 2020](https://arxiv.org/abs/2007.14114)을 실제 원전으로 확인했다. SciSpace·Exa를 통해 원전을 찾고, Wolfram evaluator1회로 일반2×2 implicit derivative, escape derivative, temperature chain rule와 사건 energy 항등식을 확인했다. Provider의 symbol warning과 remote CPU UNKNOWN도 receipt에 보존했다. 일반 implicit differentiation을 새 정리로 주장하거나 strong no-go를 제기하지 않는다.

## 3. Native parity와 안정한 산술의 구분

실행 전 독립 검토에서 tau≈1e−6의 literal complex escape expression이 상쇄 오차에 취약함을 확인했다. `ARITHMETIC_ADDENDUM.md`는 원래 native branch를 유지하면서 두 관측을 분리했다.

1. A는 native literal 식과 보존 X0로 원래 값들을 대조한다. 이 경로에는 새 선형 풀이가 없다.
2. 새 primal/tangent/complex/FD는 동일한 안정한 산술을 쓴다. tau≤1e−6의 native quadratic은 그대로이고,1e−6<tau<.03에서는 p의10항 급수, 그 이상에서는 expm1을 쓴다. 첫 누락항과 도함수 remainder를 명시했다. 실제 구현된 다항식 자체를 미분한다.

이 선택은 숨긴 constant anchoring이나 tolerance 완화가 아니다. 다만 **새 represented matrix는 RESP01의 old native frozen matrix와 동일하지 않다.** 실제 normalized gap은 M≈1.049253e−9, 전체 s≈2.147336e−7, virtual sv≈2.930729e−6이고, stable solved outgoing과 stored native outgoing의 차이는1.4344654803842884e−13이다. 작은 출력값 차이로 matrix/operator 차이를 없던 것으로 만들지 않는다.

같은 map에 대한 미래 결합식은 δo=J_sδθ+K_sδu다. 이전 RESP01의 K0 norm interval [1.175627229227178,1.1756272292401924]는 그때의 frozen operator에 대한 결과다. K_s와 K0의 동등성·차이 상한을 별도로 결속하기 전에는 이 인증을 새 J_s나 새 K_s로 옮기지 않는다. `OPERATOR_BINDING_CLARIFICATION.md`에 이 제한을 명시했다.

## 4. 실제 수치 결과

다음 수치는 stable source에서 incoming을 고정한 국소 미분이다. 로그 좌표의 increment는 dimensionless이고, xe/xHII도 fraction의 additive increment다.

| primitive | ∂F/∂θ | ∂Rγ/∂θ [m^-3 s^-1] | ∂Qrad/∂θ [J m^-3 s^-1] |
|---|---:|---:|---:|
| xe | −49.2760921201 | 3.42169660329e−5 | 5.59110089096e−23 |
| xHII | −55.9995997200 | 4.00076806972e−5 | 6.53731189892e−23 |
| ln TR | 95.9736685326 | −6.73152839914e−5 | −1.09994130964e−22 |
| ln TM | 5.97411430232 | −4.26679432227e−6 | −6.97200257728e−24 |
| ln nH | −7.03123869999 | 4.96666314056e−6 | 8.11559817536e−24 |
| ln H | 1.39251420218 | 6.12850628893e−9 | 1.00140663960e−26 |

Base F=−1.502859370064622, Rγ=1.3726872952695042e−8 m^-3 s^-1, Qrad=2.2429905539313814e−26 J m^-3 s^-1이며 Qatom=−Qrad다. 순수H 제한에서 dF/dxH=−105.27569184006867, dRγ/dxH=7.422464673009079e−5, dQrad/dxH=1.212841278987731e−22이고 atomic derivative는 정확히 반대 부호다.

이 표는 fixed incoming에서 국소 source가 어떻게 변하는지를 나타낸다. Incoming radiation이 함께 변하는 실제 시간진화, 유한 perturbation의 nonlinear remainder, physical history uncertainty를 이 표만으로 예측하지 않는다. 전체314×6/313×6 배열과 Lyα/β/γ outgoing 열은 raw NPZ와 `results/continuation001/REPORTED_VALUES.json`에 있다.

## 5. 동결 기준과 실제 검증

| 기준 | 확인한 근거 | 실제 결과 |
|---|---|---|
| A literal reconstruction |21개 비교 그룹, 구조적0 별도 | 최대1.5551741193678365e−10≤5e−9 |
| B analytic vs complex |6축, 모든 coefficient/output/state 열, h=1e−20 | 최대1.6263934969885847e−11≤2e−8 |
| C implicit backward residual |primal313, tangent1878component | 최대1.6778326936217204e−15≤1024eps64 |
| D structural identities |9groups, pure-H 직접 shared-seed11checks 포함 | 모두512eps gross 또는 명시된 complex 기준 PASS |
| E mixed FD |2directions×3steps;12endpointRHS |6/6step PASS; outgoing최대7.197124258333325e−9, F최대7.7260e−8, R최대7.2031e−9≤2e−5 |
| F independent controls |Fraction Cramer제조3cases/6smallRHS,60자리 escape14depths,27refusals | 모두PASS; exact-toy 최대1.816728585750256e−16 |

Complex oracle는 동일 source 값 식을 공유하지만 plain complex arithmetic을 사용하여 Dual tangent propagation을 호출하지 않는다. 이는 미분 방법의 독립성이며 별도의 물리 source model 독립성을 뜻하지 않는다. 제조문제의 Fraction Cramer quotient derivative는 implicit RHS 공식을 그대로 다시 쓰지 않는 독립 reference다. 세 FD step만으로 asymptotic convergence를 주장하지 않는다. 고정밀 escape comparison은 물리적 불확실성·전체 transcendental interval enclosure가 아니다.

## 6. 원래 실패, 복구, 누적 비용

첫 primary는 base1+tangent6+complex6=13largeRHS 후 NumPy bool을 JSON으로 저장하다 exit1로 중단됐다. A/B와 C raw residual/gross arrays는 보존했다. 원래 실패를 성공한 invocation으로 고쳐 쓰지 않았다. Root가 원인을 진단하고 같은 독립 reviewer가 제한된 continuation을 검토한 뒤, 저장된 C를 읽고 아직 실행하지 않은 D/E/F만 수행했다. 새 E12RHS로 전체largeRHS는 정확히25다. Original13RHS replay0, old RESP01의627RHS/inverse/certificate replay0이다.

| 실행 | inclusive CPU[s] | execution wall[s] | 큰 RHS |
|---|---:|---:|---:|
| primary001, 원래 serialization 실패 |0.791030|0.808640620|13|
| continuation001, 미완료 부분만 |1.002246|0.976096903|12|
| figures001, 첫 PNG/PDF |4.240177|4.219067001|0|
| figures002, 저장자료 layout 수정 |2.329394|2.332832932|0|
| **합계** |**8.362847**|**8.336637456**|**25**|

최종 누적 값은 BUDGET_LEDGER.json과 실제4개 실행 receipt에 결속된다. 최초 그림에서 긴 ylabel clipping과 zero부근 tick overlap을 실제로 발견해 원본을 보존하고 저장자료만 사용하는 수정1회를 별도 승인했다. 원래 figure process count1을2로 명시적으로 수정하되, 기존 figure10CPU/30wall와 전체60CPU/180wall를 높이지 않았다. 최종 그림은 figures002, 최초 그림은 figures001에 유지한다. 최종2개 PNG도 root와 동일 reviewer가 실제 열람했고 presentation finding을 닫았다. 세로축은 **symmetric logarithmic(symlog)**이며 대괄호는 값의 배율이다. Sparse tick을 선형축으로 읽지 않으며 정확한 크기는 위 표와 REPORTED_VALUES/NPZ를 따른다.

한 thread,1GiB AS 제한을 적용했다. getrusage/wait4는 관측한 process-scope CPU/RSS이며 live namespace aggregate로 부르지 않는다. 환경 준비·provider I/O·포장·전체 대화 경과 시간은 이 실행 비용과 별도이고, 측정하지 않은 비용을0으로 바꾸지 않는다. 기존 H01/REFINE01/RESP01 비용과 과거 unknown을 원장에 유지했다.

또한 실제 과학 실행 전에 작업 환경이 사라졌다. Git S0의29문서를 복원해29/29 blob·크기를 확인하고, 준비된 코드·입력23파일은 원래 canonical SHA256 `adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54`와23/23 일치시켰다. 과학 결과 재실행은0이다. 원300member S0 ZIP은 업로드 전에 소실됐고 원bytes 복구를 주장하지 않는다. 별도 S0_RECOVERED와 완전한 S1을 게시·백업했다. 빠진 mpmath1.3.0은 공식 wheel536198bytes/SHA `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`를 승인된 다운로드 경로로 받아 격리 설치했다. 실패한 pip/default-network 시도도 보존했다.

## 7. 게시, 백업과 전체 DAG

Source parent는 REC `ccf2bd088972e952fbe8e7e6eb21ccc8a7275447`이다. 새 branch는 `research/rec-history-thermo-20261024`, Draft PR은 [135](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/135)다. S0 commit `0e3f6ead3bc42122a91edeaabe64ab498db399aa`, S1 commit `afa237a784974b07d26cf68900b29283166a62ec`가 실제 게시됐다. S1 원격 전체bytes/SHA/CRC와306payload가 확인됐고, S1F는 실패 당시의 정확한 evidence delta를 따로 보존한다. 이후 S2/central/final의 실제 IDs는 delivery 기록에서 확인한다.

각 R1–R10/C1–C10의 근거, 순서, DAG 위치, checkpoint와 실제 게시·백업은 STAGE_PROGRESS.json/.md에 기록한다. 유한 작업의20/20과 전체물리완료율은 다르다. 중앙은 fixed handoff `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, 원40contracts/7authorities/17edges를 유지한다. 최신38개 non-REC노드 전체를 보존하고 REC-LINE02/REC-HISTORY observations만 추가한다. Assembler/renderer 재실행은0이며 main merge/activation도 없다.

## 8. 다음 실제 입력 의무

다음 스레드는 현재 actualHEAD·AGENTS·병렬변경·actualbackup을 확인하고 완료된 현재25RHS를 반복하지 않는다. H5에서 원래 PR05B2 history payload의 eta/prefix/source/frame/query coverage를 실제 바이트로 결속하고, 동일 target의 independent reference/endpoint uncertainty 또는 정당화된 whole-cell curvature를 확보해야 한다. 실제 finer 후보의 존재와 admission은 구별한다.

H6에서는 B3C의 clock/frame 설계를 재사용하되 현재 native313 incoming/314 outgoing과 실제 incident trace·selected geodesic/direction/frame owner를 연결해야 한다. H7에서는 J_s와 같은 arithmetic/source identity의 incoming K_s, 실제 history pullback/retiming, geometry 및 thermal evolution derivative가 필요하다. 다음 유한 실행의 입력·오차 allocation·누적 budget은 이들 증거가 정해진 다음 동결한다. 이 인계는 새 IVP나 과거 campaign 실행 승인이 아니다.

## 최종 실제 전달 — S3 metadata

유한 작업은 실제 S2 Git/백업과 중앙 additive 게시 확인 후 **20/20 완료**다. S2 과학 snapshot은18/20 당시의 불변 archive로 유지한다. S2 commit `95d0b62daef5bc0b522c5b5a579b33bef15fc6f2`, tree `2cb78e13646ff145f455015ce99e7324c845ac80`, Draft PR135의152/152path readback이 통과했다. Dropbox `id:BSpOijBcT10AAAAAAD_9ng`, rev `65e9aa99574930af03d47`의5,842,521bytes/SHA256/ZIP CRC와485payload가 모두 확인됐다. 중앙 commit `2cc58d209e149847e7d8545d26ef7bcc944229fa`, tree `2bcd7b59ea749a53cf6a93b504240e82bf1444f3` 및 보존 검사는 실제 receipt를 따른다.

S2 CI는 run40123100446/job120958707398에서 verify_repo.py --quick whitespace/EOF로 실패했고 pytest는 skipped다. inherited 및 보존한 owned 경로261진단을 포함한다. 동결 source를 재포맷하지 않았으며 green CI나 재실행을 주장하지 않는다. A–F scoped scientific admission과 CI 상태를 구별한다. 최종 S3 HEAD의 CI는 게시 후 companion에 실제 관측으로 남긴다.

자기 commit/tree는 external final companion에서 실제 S3 readback과 연결한다. companion의 자기 upload ACK는 별도 actual receipt로 남기며 archive를 반복 수정하지 않는다. H5/null, H6 trace, full coupled H7 및 J_s/K_s 공통 operator binding은 열린 의무로 유지한다.

중앙 CI도 run40123420615/job120959665670에서 cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check 단계가 실패했다. 이번 중앙 projection은4개 문서/관측 경로만 바꿨고 Rust 변경은 없다. 수동 CI 재실행은0이며 두 저장소의 red CI를 scoped scientific PASS와 구별한다.
