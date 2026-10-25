# 전체 목표 DAG와 PB01 — 중단 후 재구성

> Recovery classification: **RECONSTRUCTED_FROM_RECOVERED_SOURCE_AND_PRELOSS_RECORD**. 원문 raw25개는 functions.store에서 회수했고 current census는 소실전 SHA256과 일치했다. 이 문서는 소실전 생성 문서의 exact-byte 복원이 아니며 새 복구 설명이다. Source cut은03:06UTC로 유지했고 새 GitHub 조회/과학 실행은0이다.

## 현재 상태와 역사적 snapshot

Canonical8e946와 PR228donor256a152를 기준으로 원40node/17integrationedges/7authorities를 보존한다. Globalphysicalcompletion=null. 소실전 GLOBAL_PROGRESS 작성입력은 R1–R5+C1–C4=9/20local, S0publication/backupPENDING, scienceadmissionPENDING이었다. 복원된 STAGE_PROGRESS도 그 historicalsnapshot을 보존한다. 이후 실제S0Gitcommit9637191388afe79b16d22ed76edd6a9493f9a14c는 root가 확인했고 원S0ZIP은 upload전소실/ACK없음으로 별도기록한다. Root가 최신recovery단계전달축을 갱신한다. PB01science는root확인상아직0이며 이 문서에 실행결과숫자를 선기입하지 않는다.

기존KS01은REC136f9ed… 실제20/20완료다. PR228KS관측의309776…/18/20은immutableS2이므로그대로carry하고final20/20과구별한다. THERMO01도기존20/20완료이며새PB단계로합산하지않는다. HH90scopedchild와actualconsumerACKnull/parentPARTIAL을유지한다.

## plan_status 정확한 집계

| Status | Count |
|---|---:|
| PROPOSED | 34 |
| COMPLETE_SCOPED | 2 |
| PARTIAL | 2 |
| OWNER_DELIVERY_PENDING | 1 |
| SOURCE_INPUT_PENDING | 1 |

## 40행: 기존 nodes 배열 순서

원배열은globaltoposort가아니다. REC-LINE02(row13)→WU_SPECTRAL_GEOMETRY_COUPLING(row6)의조건부edge가역순이다. 아래층은소실전동일DAG에대해유도한31local+17integration+2internalconditional=50links의5층19/9/6/4/2를재사용한다. 새assembler/renderer/topology실행은없다. 모든조건을동시에요구하는실행계획이아니며externalinput은별도로남는다.

| # | Node | plan_status | 관측/범위 | local dependencies | 재사용층 |
|---:|---|---|---|---|---:|
| 1 | `WU_CE83_OWNER_COMPLETION` | PROPOSED | observed_completion: REUSED_COMPLETE_SCOPED | — | 1 |
| 2 | `WU_LI_SOURCE_UNCERTAINTY` | PROPOSED | canonical부가관측없음 | — | 1 |
| 3 | `WU_HE_LI_CX_STATE_ENERGY` | PROPOSED | canonical부가관측없음 | — | 1 |
| 4 | `WU_D_PI_RR_MATCHED` | PROPOSED | canonical부가관측없음 | — | 1 |
| 5 | `WU_NUCLEAR_PARTICLE_OWNERSHIP` | PROPOSED | observed_completion: PARTIAL_CONDITIONAL_BARE_CHILD_COMPLETE; HH90conditionalcellchildPASS;actualconsumerACKnull | — | 1 |
| 6 | `WU_SPECTRAL_GEOMETRY_COUPLING` | PROPOSED | canonical부가관측없음 | WU_CE83_OWNER_COMPLETION, WU_HE_LI_CX_STATE_ENERGY, WU_D_PI_RR_MATCHED, WU_NUCLEAR_PARTICLE_OWNERSHIP | 2 |
| 7 | `CR_N4_C23B_CUTOFF_BINDING` | COMPLETE_SCOPED | observed_completion: COMPLETE_SCOPED | — | 1 |
| 8 | `CR_N4_STOPPING_KERNEL` | PARTIAL | observed_progress: PARTIAL | CR_N4_C23B_CUTOFF_BINDING | 2 |
| 9 | `CR_N5_ATOMIC_ISOTOPE_COVERAGE` | PARTIAL | observed_progress: COMPLETE_SCOPED | — | 1 |
| 10 | `CR_N6_CONSERVATIVE_COUPLING` | PROPOSED | canonical부가관측없음 | CR_N4_STOPPING_KERNEL, CR_N5_ATOMIC_ISOTOPE_COVERAGE | 3 |
| 11 | `CR_N7_NEW_PARCEL` | PROPOSED | canonical부가관측없음 | CR_N6_CONSERVATIVE_COUPLING | 4 |
| 12 | `CR_BETA_FULL_OWNER` | PROPOSED | canonical부가관측없음 | — | 1 |
| 13 | `REC-LINE02` | OWNER_DELIVERY_PENDING | canonicalobs없음;PR228SOURCE_OWNED_UNCHANGED/finalreceiptfound | — | 1 |
| 14 | `REC-HISTORY` | PROPOSED | canonicalobs없음;PR228KS01complete;final20/20;parentPARTIAL;PBhistorical9/20local | REC-LINE02 | 2 |
| 15 | `REC-C3` | PROPOSED | canonical부가관측없음 | — | 1 |
| 16 | `REC-LI` | PROPOSED | canonical부가관측없음 | — | 1 |
| 17 | `REC-FIELD` | PROPOSED | canonical부가관측없음 | REC-LINE02 | 2 |
| 18 | `REC-COUPLED` | PROPOSED | canonical부가관측없음 | REC-LI, REC-FIELD, REC-HISTORY | 3 |
| 19 | `HE-X1` | COMPLETE_SCOPED | observed_completion: COMPLETE_SCOPED | — | 1 |
| 20 | `HE-ANG` | SOURCE_INPUT_PENDING | observed_completion: SOURCE_INPUT_PENDING | HE-X1 | 2 |
| 21 | `HE-EXCHANGE` | PROPOSED | canonical부가관측없음 | — | 1 |
| 22 | `HE-RESERVOIR` | PROPOSED | canonical부가관측없음 | — | 1 |
| 23 | `HE-CLOSURE` | PROPOSED | canonical부가관측없음 | HE-ANG, HE-EXCHANGE, HE-RESERVOIR | 3 |
| 24 | `HE-FEEDBACK` | PROPOSED | canonical부가관측없음 | HE-CLOSURE | 4 |
| 25 | `B1-G1B-recover` | PROPOSED | canonical부가관측없음 | — | 1 |
| 26 | `B2-G1B-curved` | PROPOSED | canonical부가관측없음 | B1-G1B-recover | 2 |
| 27 | `B3-fourforce-owner` | PROPOSED | canonical부가관측없음 | B2-G1B-curved | 3 |
| 28 | `B4-production-restart` | PROPOSED | canonical부가관측없음 | B3-fourforce-owner | 4 |
| 29 | `B5-domain-validation` | PROPOSED | canonical부가관측없음 | B2-G1B-curved, B3-fourforce-owner, B4-production-restart | 5 |
| 30 | `V1-affine-native` | PROPOSED | canonical부가관측없음 | — | 1 |
| 31 | `V2-session-fatal` | PROPOSED | canonical부가관측없음 | — | 1 |
| 32 | `V3-affine-quotient` | PROPOSED | canonical부가관측없음 | — | 1 |
| 33 | `V4-causal-polynomial` | PROPOSED | canonical부가관측없음 | — | 1 |
| 34 | `V5-sphere-production` | PROPOSED | canonical부가관측없음 | V1-affine-native, V2-session-fatal, V4-causal-polynomial | 2 |
| 35 | `REI-L0` | PROPOSED | canonical부가관측없음 | — | 2 |
| 36 | `REI-L1` | PROPOSED | canonical부가관측없음 | REI-L0 | 3 |
| 37 | `REI-L2` | PROPOSED | canonical부가관측없음 | — | 2 |
| 38 | `REI-L3` | PROPOSED | canonical부가관측없음 | — | 3 |
| 39 | `REI-L4` | PROPOSED | canonical부가관측없음 | REI-L0, REI-L1 | 4 |
| 40 | `REI-L5` | PROPOSED | canonical부가관측없음 | REI-L4 | 5 |

## 재사용한5개 선행층

| 층 | 개수 | Nodes |
|---:|---:|---|
| 1 | 19 | WU_CE83_OWNER_COMPLETION, WU_LI_SOURCE_UNCERTAINTY, WU_HE_LI_CX_STATE_ENERGY, WU_D_PI_RR_MATCHED, WU_NUCLEAR_PARTICLE_OWNERSHIP, CR_N4_C23B_CUTOFF_BINDING, CR_N5_ATOMIC_ISOTOPE_COVERAGE, CR_BETA_FULL_OWNER, REC-LINE02, REC-C3, REC-LI, HE-X1, HE-EXCHANGE, HE-RESERVOIR, B1-G1B-recover, V1-affine-native, V2-session-fatal, V3-affine-quotient, V4-causal-polynomial |
| 2 | 9 | WU_SPECTRAL_GEOMETRY_COUPLING, CR_N4_STOPPING_KERNEL, REC-HISTORY, REC-FIELD, HE-ANG, B2-G1B-curved, V5-sphere-production, REI-L0, REI-L2 |
| 3 | 6 | CR_N6_CONSERVATIVE_COUPLING, REC-COUPLED, HE-CLOSURE, B3-fourforce-owner, REI-L1, REI-L3 |
| 4 | 4 | CR_N7_NEW_PARCEL, HE-FEEDBACK, B4-production-restart, REI-L4 |
| 5 | 2 | B5-domain-validation, REI-L5 |

Requirements는선택모델안에서AND이며모든물리공급자/수치옵션전체AND가아니다. REI-L4는L0+선택한L1pair+호환geometry/solver가필수이고L2/L3는선택확장이다. 실행시간자료가없으므로schedulecriticalpath는계산하지않는다.

## 17 integration 조건 (원문)

| # | From → To | Condition |
|---:|---|---|
| 1 | HE-X1 → REI-L0 | using angular-moment injection |
| 2 | HE-ANG → REI-L3 | selecting anisotropic baryonic scattering transport |
| 3 | HE-EXCHANGE → REI-L3 | selecting finite-mass baryonic pressure exchange |
| 4 | HE-CLOSURE → REI-L4 | selecting nonzero baryonic anisotropic stress |
| 5 | CR_N4_STOPPING_KERNEL → REI-L1 | claiming thermalization of supplied fast photoelectrons |
| 6 | CR_N6_CONSERVATIVE_COUPLING → REI-L4 | selecting CR coupled radiation/deposition pathway |
| 7 | WU_D_PI_RR_MATCHED → REI-L1 | claiming isotope-specific D PI/RR number and energy moments |
| 8 | WU_NUCLEAR_PARTICLE_OWNERSHIP → REI-L2 | activating nuclear daughters/fast products |
| 9 | CR_BETA_FULL_OWNER → REI-L2 | activating source-qualified beta partition and stopping |
| 10 | REC-LINE02 → REI-L1 | selecting native line source |
| 11 | REC-LINE02 → WU_SPECTRAL_GEOMETRY_COUPLING | selecting native line in WU spectral coupling |
| 12 | REC-FIELD → REI-L1 | selecting actual spectral radiation/Compton exchange |
| 13 | B3-fourforce-owner → REI-L4 | selecting BASS four-force geometry feedback adapter |
| 14 | B2-G1B-curved → REI-L5 | claiming curved Bianchi smooth-source domain |
| 15 | V1-affine-native → REI-L4 | using native reduced30/full33 affine adaptive client |
| 16 | V2-session-fatal → REI-L4 | using switching/restart driver |
| 17 | V5-sphere-production → REI-L5 | claiming its physical spherical transport scheme |

## REC의선행의무와PB01

REC-LINE02→REC-HISTORY→REC-COUPLED, REC-LINE02→REC-FIELD→REC-COUPLED, REC-LI→REC-COUPLED는localedge다. Native line/spectrum선택시REC-LINE02/REC-FIELD→REI-L1→REI-L4→REI-L5로이어진다. H5/H6/H7/PB01은REC-HISTORY내부의무이며새중앙node가아니다. 현재REC-HISTORY→REC-FIELD,REC-HISTORY→REI-L1,REC-COUPLED→REI-L4의명시적edge는없다.

| Obligation | 상태 | PB01관계 |
|---|---|---|
| H5 |Actualpayload/prefix/queryadmission완료,physicalepsilon/reference/endpoint/curvature/absoluteboundnull|조건부box/propagation이며physicalreference공급은별도|
| H6 |Actualtrace/geodesic/direction/frame/measure/volume/clock/source/queryownerOPEN|별도HISTORY02C5owner구현재실행없음|
| H7 |LocalJ_s/K_s완료,historypullback/retiming/geometry/thermalODEOPEN|Savedendpoint/querypullback→Ks,adjoint,bilinearremainder를새finite범위로검토;admissionpending|

<!-- ROOT_PB01_RESULT_START -->
현재PENDING_SCIENTIFIC_ADMISSION. Root가accepted결과,review,budget,actualGit/backupACK,잔여의무와현단계를추가한다. 실제PB01결과숫자는없다.
<!-- ROOT_PB01_RESULT_END -->

PhysicalHOLD;REC_U5HOLD_9_FAIL/HOLD_8_FAIL;CLOSED_HOLD_NOT_RESET;global_convergenceNOT_RUN;productionNOT_APPROVED;REI_activation=false;firstfailedREIrawHISTORICAL_LOCAL_ONLY. Globalphysicalpercent=null.

## Source

Current: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8e946b46aa44581f09141184f193223277f2ec88/research/orchestration_longterm_20261023/assembly/DAG.json

Donor: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/256a152eff42fdd6daf317e7bf7ea0daffad728d/research/orchestration_longterm_20261023/assembly/DAG.json

KSfinal: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4/research/rec_history_ks_20261025/CLAIM_GATES.json

원raw는survey/github/에서회수됐다. 원generatedGLOBAL_PROGRESSbytes는회수되지않아이파일은재구성본이다. Science0/providerreads0/assembler0/renderer0.
