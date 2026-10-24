# REC-HISTORY-02R 연구·구현 결과

2026-10-24. physmath-research-loop built-in1.0.0 / 승인 설계v0.2.
이 파일은 이번 유한 연구 단위의 결과이며 원 LINE02 handoff와 고정 중앙
authority를 대체하지 않는다. 최종 전달 상태는 delivery/PUBLICATION_STATE.json과
companion receipt의 실제 Git/provider readback을 따른다.

## 1. 채택할 결과

**REC-HISTORY-02R = COMPLETE_SCOPED_CHARACTERISTIC_ADAPTER / PASS_SCOPED.**

Positive-rate constant-shear Bianchi I의 retarded source event, source direction,
native-Wien reference conversion, retained fixed-cell history tangent, 기존 local
boundary와 single-event ledger 합성을 구현했다. Frozen127case rows와776named
numerical comparisons가 모두 통과했다. 같은 한 차례 독립 검토에서 별도6probe
rows/10adapter calls도 통과했다. 원 그림2개와 배치 수정 그림2개를 실제로 확인했다.

부모 REC-HISTORY는 PARTIAL이다. 동일 target 매개변수의 실제 history
reference uncertainty, endpoint uncertainty 또는 정당화된 curvature bound는
여전히 필요하다. H5는 INPUT_DEPENDENT_UNCALIBRATED이며 전체 물리 완료율은null이다.
현재 결과의 ledger는 지정된 represented direction에서의 국소 대수와 단위를
검증한다. 전체 비등방 angular integral의 물리적 공급자·measure·quadrature는
후속 입력 의무다.

근거: results/primary002/SUMMARY.json, raw_rows.jsonl,
evidence/independent_review/FINAL_REVIEW.md/.json,
evidence/independent_review/probe_results/.

## 2. 최신 자료 종합으로 선택한 실행

R1시점 관련8개 저장소의 전체 branch metadata1609개를 페이지 끝까지 조사했다.
REC는149branches와전체상태PR131개(open97/closed34), 다른7개는1460branches였다.
최근 관련PR32개, 대화 검색의 관련 단서, Dropbox직접98/재귀138개,
Drive기존폴더16/root310과이름검색, 최근 지속파일115개와첨부20개를 확인했다.
모든 branch 본문이나 접근할 수 없는 대화까지 완전 열람했다는 뜻은 아니다.
세부 coverage·identity는 SURVEY_SYNTHESIS_KO.md 및 provenance/survey/에 있다.

복구한 HISTORY02 Stage A ZIP은 SHA256
ca748e1e9e3ee1c9fe2c82418221f0230998b97223b38d91c558ae3924a077da이며,
14payload/CRC15가 확인됐다. 당시 계약·유도는 있었고 구현/raw/review는 그
archive에 없었다. 원 snapshot 이후 owner활동·지출은 미관측이다.
원 Stage A60CPU/180wall 잔여를 사용했다고 기록하지 않고02R 별도경로와
현재30CPU/90wall allocation으로 구현했다.

다른 결과는 해당 의존성에 맞춰 통합했다. BASS B3a의 invariant event source,
HE-ANG의 실제 source/catalogue intake, CR의 finite collision/source bridge,
HH의 nuclear/thermal ownership 계약, REI의 prescribed-background angular
trajectory 결과를 비교했다. 어떤 것도 REC target history의 독립 uncertainty로
전용하지 않았다.

마지막 중앙 readback에서 orchestration이8b6e741...에서
3fba7cd91f84b4687cf6356f87400056ca32e37e로 진전한 것을 확인했다.
새 CR C23E D43K source binding(PR100)과 HE-ANG DDCS20 measured-window(PR94)
observation을 읽었다. 둘은 source-qualified 전체 provider와 REC matching
history의 의무를 닫지 않으며, 그 완료된 자식 상태는 중앙 갱신에서 보존한다.
AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4는 동일했다.

## 3. 이론에서 구현까지

Metric(-,+,+,+), eta=ln(a), normal-frame propagation direction n을 사용한다.
관측방향은 -n이다. beta_i=b_i eta+constant, sum b_i=0,
a_i=1+b_i>0에서 conserved spatial momenta가 다음을 준다.

\[
F(\Delta)=\log\left\|n_{ti}e^{a_i\Delta}\right\|-\Lambda=0,\quad
\Delta=\eta_t-\eta_s,\quad\Lambda=\log(E_s/E_t).
\]

\[
F'(\Delta)=q_s=\sum_i a_i n_{si}^2>0,\qquad
\frac{\Lambda}{a_{\max}}\le\Delta\le\frac{\Lambda}{a_{\min}}.
\]

따라서 선택된 domain에서 retarded root는 유일하다. Shifted log norm으로
큰 exponential과 zero direction component를 다루고 bracketed Newton/bisection을
구현했다. Lambda0, exact axis, FLRW는 exact value식으로 처리하며 일반 tangent는
그 shortcut에서도 보존한다. 경계의 q_t와 root Jacobian의 q_s를 구별한다.

Native source는 Wien departure d=f-exp(-x)를 저장한다. 따라서 prescribed
reference T_s=T_t exp(Delta)에 대해

\[
x_s=x_t e^{\Lambda-\Delta},\qquad
d_{\rm in}=H(\eta_s,n_s)+e^{-x_s}-e^{-x_t}.
\]

여기에 source time·source direction·history data·geometry tangent를 합성했다.
원 HISTORY01 source의 Git blob
1aa7f134c332bc4596372df18c7c47306260ecfc는 byte-identical로 재사용했다.
경계와 event ledger는

\[
d_{\rm out}=d_{\rm in}
+\left(\frac{x_{r,p}}{3x_{1s}}-d_{\rm in}\right)
[-\operatorname{expm1}(-\tau/q_t)],
\]
\[
R=G_{\rm native}H_tq_t(d_{\rm out}-d_{\rm in}),\qquad
(\dot u_{\rm atom},\dot u_{\rm rad})=(-E_{21}R,+E_{21}R)
\]

를 그대로 사용한다. Outgoing 저장은 이 동일 사건을 나타낸다.
Propagation redshift work의 geometry owner는 국소 원자 사건과 구별된다.

새 wrapper는 보존 prefix 이전·exclusive endpoint 이후·iz<2를 legacy
interpolator의 thermal fallback 전에 거부한다. Knot에서는 source-time tangent가
0일 때만 고정 셀을 유지한다. Signed departure는 허용하며 absolute occupation을
확인한다.

조건부 error allocation은
\[
\epsilon_\Delta\le\epsilon_F/a_{\min},\quad
\|\partial_\Delta n_s\|\le(a_{\max}-a_{\min})/2,\quad
|\partial_\Delta W_s|\le1/e
\]
로부터
\[
\epsilon_{\rm in}\le\epsilon_H+
[K_\eta+K_n(a_{\max}-a_{\min})/2+1/e]\epsilon_\Delta+
\epsilon_{\rm arithmetic}
\]
를 준다. Target boundary coefficients를 고정하면
epsilon_out<=T epsilon_in,
epsilon_R<=G_native H_t q_t A epsilon_in이다.
전체 query uncertainty tube에 유효한 입력 bound가 필요하다.

전체 유도와 assumptions는 THEORY.md, 식–함수–입출력 대응은
IMPLEMENTATION_MAP.md에 있다. 새 Wolfram call은 합성 미분식 차이와 variance
interval identity에 대해 각각0을 반환했다. 요청한 kernel limit5s와 실측
CPU/wall을 구별하며 후자는unknown으로 보존했다.

## 4. 실제 검증 결과

독립 oracle는 adapter/vendor를 import하지 않는 mpmath80자리 식이다.
Retarded root는300회 bisection, JVP는 사전 고정 step1e-25의 central difference를
사용했다. Case와 threshold는 실행 전에S1에 동결했다.

| Group | Case rows | 검증 범위 |
|---|---:|---|
| Retarded root | 48 | FLRW,축/zero components,LRS/triaxial,Lambda0/작은값/큰값,positive-rate 경계 |
| Tangent | 12 | angular,shear,ratio,mixed 및 axis off-axis response |
| Wien | 16 | 양·음 offset,equality,near cancellation,x0,underflow,large transformed x |
| Composite | 12 | fixed-cell field와boundary/JVP/single-event number·energy |
| Actual h4 | 8 | 실제 retained prefix 내부의 독립 선형 보간 |
| Guard | 16 | shape,domain,nonfinite,prefix,knot,absolute positivity,missing bound |
| Conditional envelope | 12 | 알려진 analytic field와 supplied tube bounds |
| Deliberate defects | 3 | FLRW clock in shear,Wien correction omission,photon clock+1 |
| 합계 | 127 | 776 named numerical comparisons 포함 |

| 검사군 | 최대 error/scale | 고정 기준 |
|---|---:|---:|
| Root/direction/Killing | 1.5400333539011604e-13 | 5e-12 |
| Characteristic JVP | 1.793463415348147e-16 | 5e-9 |
| Wien extreme relative regime | 2.8564621486689194e-14 | 8e-12 + declared underflow floor |
| Composite value/ledger | 4.2231529496465644e-16 | values5e-12,JVP5e-9 |
| Actual h4 arithmetic | 9.167764104627694e-32 | 64eps scaled |

Scaled value의 scale은max(1,|actual|,|reference|)다.
Wien extreme은max(|reference|,1e-300)와5e-324 floor를 사용한다.
표의 actual h4 값은 동일한 저장 값에 대한 보간 산술의 비교이며
물리적 history 오차를 뜻하지 않는다.

12analytic envelope의 independent-error/bound 비율은
0.2459503151..0.3609786537였다. 세 의도적 결함은 모두 검출됐다:
선택된 shear 예제에서 잘못된 FLRW delay의 차이0.07873893346,
Wien 보정 누락의 차이0.02893711039, photon-clock+1의 cell 차이1이다.
이는 명시한 유한 control에서 차이를 판별하는 근거다.

독립 검토는6probe rows를 한 번 실행했다. Source-time tangent overflow 거부,
exact-axis off-axis response, shear derivative, tiny signed Wien correction,
strict-prefix/knot,missing uncertainty를 확인했다. Source-time guard의 정적 finding은
실행 전 최소 교정과 독립 exact regression으로 닫혔다.
최종 review는PASS_SCOPED이며 추가 probe는 요구되지 않았다.

## 5. 실제 자료와 물리적 오차 admission

실제 h2/finer 후보를 보존한다. h2U5는313/313 query를 덮지만,
T0=2.7255K,nH0=0.18971712352134673m^-3는
target2.728K,0.18745798773143102m^-3와 다르다.
h2U4,h4R3Q,h4smoke는각각target0/313이다.

이번8개 actual h4 query는 z=1701.2862323292372..1702.0632266451196의
자체 early retained domain에 있다. 실제 h4의24열이나 같은-h parity로
독립 endpoint/reference/M2를 만들지 않았다. Actual M2와 uncertainty는null이다.
다음 입력, query table과 error allocation 의무는 NEXT_INPUT_CONTRACT.md에 있다.

## 6. 실패·수리·원본 보존 및 자원

첫 primary001은 mpmath import 실패로 수치case0 상태에서 종료됐다.
원 stderr, command,source snapshot, resource receipt를 보존했다.
mpmath1.3.0만 project-local dependency로 설치했고 첫 network-denied 설치도
보존했다. Python3.12.14,NumPy2.3.5와 실제 package origin을 기록했다.
동일 source/cases로 primary002를 실행하여127개를 완료했다.

첫 figure의 tick crowding과 legend/footer 겹침은 실제 PNG에서 확인했다.
원 PNG/PDF2쌍을 남기고 한 차례 layout-only repair를 수행했다.
원 raw와 첫 figures의 hash는 그대로이며 재계산 없이 저장 행만 렌더했다.

| Invocation/class | CPU s | Execution wall s |
|---|---:|---:|
| primary001 failed import | 0.102801 | 0.115160093 |
| primary002 completed | 1.709545 | 1.720105198 |
| environment setup, separate class | 1.015991 | 8.647795849 |
| first figures001 | 1.799507 | 1.819794799 |
| layout repair figures002 | 1.661186 | 1.669109743 |
| independent review001 | 0.105953 | 0.115654082 |
| **new local combined** | **6.394983** | **14.087619764** |
| cap | 30 | 90 |

각 child는1thread, RLIMIT_CPU, address-space1GiB, wall timeout을 적용했다.
측정한 child RSS highwater는97252KiB다. 종료 후 inclusive getrusage와 실제
enforcing limits를 구별했으며 live aggregate monitor를 주장하지 않는다.
환경 setup은 별도 class로 유지하면서 combined total과 repair allocation에도
포함했다. Remote API 대기와 미계측 Wolfram 실행시간은 local execution-wall과
구별하여 기록했다.

HISTORY01 CPU4.848191/wall4.736567968과
ADM01 CPU5.928528894/wall6.09275194699876은 별도의 closed ledger로 보존했다.
새 IVP/native runtime/denseRHS/old campaign replay는 모두0이다.
ADM01 원 상세1252행·원 PNG 등의 PARTIAL_AFTER_WORKSPACE_RESET은
이번 새 원본 보존 상태와 구별하여 유지한다.

## 7. 단계·게시·백업·DAG

STAGE_PROGRESS.md/.json은R1–R10,C1–C10의20단계를 개별 기록한다.
각 단계의 science/execution/publication/backup/global DAG order를 구별하고,
공통의 누적 checkpoint를 참조한다. 단계마다 같은 과학 검증을 반복하지 않았다.

| Checkpoint | 내용 | 실제 Git commit | Dropbox ID |
|---|---|---|---|
| S0 | 조사·원 StageA·이론·precode review | dd60e597980e4ee0d60490012725bdeaa0e89233 | id:BSpOijBcT10AAAAAAD_8XA |
| S1 | code+127case plan, 실행 전 | 49610577fb53940db120fa8b6d8ee4f29198d1a2 | id:BSpOijBcT10AAAAAAD_8Yw |
| S2A | 최초 environment failure | 5864c8ed63e1e248735f51b2987a030d726a5358 | id:BSpOijBcT10AAAAAAD_8ZQ |
| S2 | 원 primary raw+환경 보완 | ca73220a4ac2293c32fb8057fe26faf19227ef12 | id:BSpOijBcT10AAAAAAD_8Zg |
| S3 | 최종 review+모든 그림+formal report | 4224a7be162c70e1cef222afaa546af7b4e2cd8a / PR132 | Dropbox id:BSpOijBcT10AAAAAAD_9HA; Drive partial |

REC는 draft PR132, branch research/rec-history-characteristic-resume-20261024다.
S0/S1/S2A/S2의 changed-blob readback은 각각40/40,21/21,25/25,31/31PASS다.
Dropbox는 실제 completed ACK와 current metadata를 확인했다.
즉시 whole-byte redownload는 수행하지 않았으며 확인 수준을 명시한다.

Drive S0는601.9s 뒤 root-requested interrupt 때까지 실제 completed ACK를 받지 못했다.
플랫폼 문구 'aborted by user'는 사용자의 연구 요청 철회를 뜻하지 않는다.
S0=UNKNOWN_ACK_NOT_RECEIVED, remote 존재/취소=UNKNOWN이다.
후속 Drive는 NOT_ATTEMPTED_PROVIDER_STALLED로 기록했다.
Dual-provider 완료를 주장하지 않는다. 최종 Git/중앙/backup 상태는 별도
PUBLICATION_STATE와 companion receipt의 실제 ID·readback을 기준으로 한다.

중앙의 원40nodes/17dependencies와
authority0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17을 보존하고
REC-LINE02/HISTORY observation만 추가한다. 새 CR_N5, HE-ANG measured-window,
HE-X1 및 다른 owner 상태를 유지한다. 전체 assembler/renderer 재실행,
merge,activation은 수행하지 않는다.

현재 dependency 순서는 LINE02→HISTORY, LINE02→FIELD와
HISTORY/FIELD/LI→COUPLED다. HISTORY의 H01/ADM01/02R 자식은 scoped complete이며,
부모의 error/source 의무는 열려 있다. COUPLED는 NOT_SCHEDULED,
global convergence는 NOT_RUN, production은 NOT_APPROVED다.

## 8. 참고 자료와 재개

SciSpace discovery10records에서 primary 자료를 확인했다.
Fleury/Pitrou/Uzan PRD91,043511(2015),SecIV A는 conserved spatial
wavevector/redshift의 근거다. HyRec PRD83,043513(2011)과
HyRec-2 PRD102,083517(2020)는 history-dependent radiative transfer와
time/frequency resolution의 관계를 확인하는 데 사용했다.
문헌의 accuracy를 이번 retained array의 bound로 가져오지 않았다.

- https://arxiv.org/abs/1410.8473
- https://arxiv.org/abs/1011.3758
- https://arxiv.org/abs/2007.14114

다음 thread에서는 NEXT_THREAD_HANDOFF_KO.md를 복사하고, 실제 HEAD/AGENTS와
변경된 R1/R2 입력을 확인해 재개한다. 동일 identity의02R 검증은 재실행하지 않고
NEXT_INPUT_CONTRACT.md의 actual matched-domain uncertainty admission으로 이어간다.


## Final publication companion — actual receipts

REC S3 science: `4224a7be162c70e1cef222afaa546af7b4e2cd8a`, draft PR132, tree `a52c342c1400d6ab72d986882af36527ca614f69`, changed blobs83/83PASS.
Central: `f0a92c2421ff186dabd20fac09378a97c195fd4f`, draft PR224, tree `c59fc20b55955f00924f28278c1d6f98c57066a5`, exactly2 changed files/readback2/2PASS from parent3fba7cd91f84b4687cf6356f87400056ca32e37e. Both PRs are open and unmerged. Central receipt: delivery/CENTRAL_GITHUB_RECEIPT.json.
S3Dropbox metadata ACK: id:BSpOijBcT10AAAAAAD_9HA, rev65e8da9d9926f0af03d47,2187080bytes, archiveSHA25683198452157b9360b10d59c0df4ef1e1eccbfa5aaa52bf73ec6e886f8e482aae. Whole-byteGET NOT_RUN. Backup axis PARTIAL_DRIVE_UNKNOWN: Drive S0 UNKNOWN_ACK_NOT_RECEIVED; later NOT_ATTEMPTED_PROVIDER_STALLED.
R10/C10 science/handoff COMPLETE_SCOPED; final delivery commit UNKNOWN_UNTIL_OUTER_RECEIPT. No self-hash or dual-provider completion is asserted. Correct global subset: LINE02→HISTORY,LINE02→FIELD,HISTORY/FIELD/LI→COUPLED. R9 is HISTORY leaf→parent PARTIAL; no HISTORY→FIELD edge is introduced.
Repository CI importsmoke success, verify_repo --quick whitespace failure across78 unique paths,including21 under this new unit; pytest skipped. Full diagnostic evidence and compact classification are in delivery/S3_CI_CLASSIFICATION.json. Scoped science PASS and repository-wide CI status remain separate. No scope-broad whitespace change or workflow rerun.

CI classification correction: the earlier26-total/zero-new-unit count was incorrect because only selected partial diagnostics were inspected. Complete S3 job120766417580/run40058413072/head4224a7be and final job120768837109/run40059205644/head3848a94 both show78 unique whitespace paths,including21 in this unit. New-unit failures are new blank lines at EOF in frozen contract/docs/copied provenance/source snapshots/receipts; no immutable evidence or source was changed to satisfy CI. The old compressed classification remains SUPERSEDED_INCOMPLETE_LOG_SELECTION. Full logs,complete diagnostic excerpts and all paths are bound in delivery/S3_CI_CLASSIFICATION.json and delivery/FINAL_DELIVERY_CI_CLASSIFICATION.json. Repository CI remains FAIL explicitly; scientific127/776 and independent6-row/10-call results remain retained. No scientific rerun,workflow rerun or broad whitespace fix.
