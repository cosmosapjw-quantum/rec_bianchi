# 다음 대화 인계 — REI causal-prefix consumer

이 문서는 source snapshot의 연구 상태를 담는다. source ZIP 자신의 SHA256와 백업 ACK는 archive 생성 후 delivery/FINAL_DELIVERY_RECEIPT.json과 별도 delivery ZIP에 기록한다. 이 문서의 포함 commit을 최신 HEAD로 추정하지 않는다.

## 복사할 재개 지시

$physmath-research-loop로 cosmosapjw-quantum/rei_bianchi 연구를 이어가라. SciSpace·Exa·Wolfram은 필요한 새 근거와 계산에 사용하고, 이미 완료한 계산을 장부 때문에 반복하지 마라.

먼저 고정 인계서를 읽어라:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/78f7ac5864d5817ceb79b48cb5e298cc30006510/research/program_expansion_20261025/HANDOFF_KO.md

현재 branch는 research/rei-causal-prefix-consumer-20261027이며 draft PR240은 https://github.com/cosmosapjw-quantum/rei_bianchi/pull/240 이다. Base PR239의 최종 commit은 c0e76fb13785dd6aab45e056ee54d2b318ca8f41이다. 새 unit 경로는 research/rei_expanded_event_consumer/causal_prefix_consumer_20261027이다. 실제 최신 HEAD와 AGENTS를 다시 읽어라. 이 작업의 AGENTS blob은6464cd96b7023e3e91e30246bc93650d4e435a10이었다.

### 확보한 결과

이론은 interval·monotonicity 정보 polytope의 구성적 정리다. 같은 pulse의 F_i를 유지하고 l_i=prefix max lower, u_i=all-time cap을 적용한 suffix min upper로 두면, 연속 window의 정확한 정보 경계는[max(0,l_b−u_a),u_b−l_a]다. 전체 feasible chain의 두 extremizer와 clipped two-endpoint polygon의 확장 증명이 있다. fixed-K 동역학 전체의 sharpness, 미공급 N/E 상관관계나 물리 모델 전체 오차를 인증한 것은 아니다.

CR PR108 containing commit2776752de6952f60d8d690a128f33fec4df2c57b의 finest2case×3source-z를 별도 대안으로 소비했다. raw4개는 입력 manifest의 exact Git blob/SHA256로 고정했고 큰 정수를 재직렬화하지 않았다. 6source,36canonicalbin,126sourcewindow,252scalarwindow,264interface derivative records를 저장했다.

C5 code commit cfc2115fa868595f6adcf45fe7083f95ee637b90; PREEXEC manifest SHA256 b6063f4b6e9fc31b22fd3753a076e367ff17dd0d4bf1e973ba9bc629ba2f54d5. 실제 raw 결과 commit4a82442ce5476ac10a6417f209fc74f1ff7c43ab. 단회실행 exit0,3189/3189checksPASS,stderr0bytes,재실행0회. 528저장FD 결과의 max relative residual2.7094758927889796e−10/기준2e−8,step2e−4·1e−4. 전체시간창 폭비 N약19823–23098,E약18013–18504는 공유prefix를 보존한 정보 범위 축소이며 물리 오차 감소 계수가 아니다.

### 정규화와 사건 소유권

rawN[cm^-3],E[eVcm^-3]에서 n=1e6N,e=1e6eV_J E를 정확히 한 번 변환한다. I_eV=2721/50,eV_J=801088317/5000000000000000000000000000이다. native25에서 ΔY11=n/b,ΔY12=−n/b,Δzeta=−n/b,Δw_nt=−e/b이며 다른 native행은0이다. photon port는(n/b,(e+In)/b),binding은−In/b다. 공통 N/E와 단일 event/energy 소유권을 보존한다. External injection을 capture의w_ext에 중복 계상하지 마라.

b미제공은 proper-volume 값과 null native projection을 유지한다. b=1.4e6m^-3와 b_i=b(1+i/20)는 fixture이며 actual recipientnb가 아니다. 변하는 reference는 s(F_b/b_b−F_a/b_a)=s(F_b−F_a)/b_b+sF_a(1/b_b−1/b_a)와 양쪽 b의 full quotient JVP를 쓴다. 양의 prefix a=1,b=6으로 누락항을 판별했다. 기존 continuous dotr+3Hr=R_r,F_x=(S−xR_r)/r와 미분은 유지한다.

Integrated event는 clock 불변이다. suppliedΔeta가 있어야 ΔT/Δeta로 평균을 바꾼다. manufactured eta=T/Tstar+(T/Tstar)^2,Tstar=1e7s이다. dΔT=.17ΔT와 dΔeta=−.09Δeta를 서로 다른 인자로 전달한다. C5의 shared-direction wrapper 결함은 실제 실행 전에 수리·검토됐다. source horizon derivative, max/min kink의 smooth Jacobian 또는 full Jacobian을 주장하지 마라.

### 판정·예산

독립 C9 판정은 numerical PASS_SAVED_RESULTS_WITHIN_INFORMATION_POLYTOPE_AND_INTERFACE_SCOPE, resource HOLD, overall HOLD_RESOURCE_NO_GLOBAL_OR_L4_PROMOTION이다. CR 공급자의 공개 final C9는 PENDING이다. 공개 C8 scoped PASS와 다른 대화의 미게시 C9 완료 주장을 구분하라.

실제 childCPU.192151,wrapper.074169,heldtail.02,총.286320은 예약.18을 넘었다. Planning 누적15.077490885가 임시14.99를 .087490885초 초과했다. 이 초과를 삭제하거나 사후 PASS로 바꾸지 마라. 새 local planning·과학 실행은 중단됐다. AGENTS는 원래10에서50%미만 임시 인상만 허용하므로 새로운 planning≥15 승인은 별도다. 이 작업의 광범위한 백업·게시 승인을 과학예산 인상으로 해석하지 마라.

최종 종료에서는 original policycap planning10/presentation30으로 복원하고 모든 누적을 유지한다. 실제 최종 presentation과 복원 여부는 BUDGET_STATUS.json 및 FINAL_DELIVERY_RECEIPT를 읽어라. Main595.225063/600,NO_MORE_IVPs,기존 예약과 foreign-owner budget을 보존하라. 미측정 tool/remote/LLM/tail은 UNKNOWN_NOT_ZERO다. Science를 presentation으로 이체하지 마라.

### DAG·공급자·다음 직접 연구점

원래 DAG 작업32/88·중앙27/88,원노드 증분0이다. 새20단계는88노드와 별도다. 기존88IDs/17edges 검증을 추가 문자열 제거 후 원문 복원 동일성으로 재사용했고 기존 계약·status를 보존한다. REC-COUPLED는 constructive partial,L4false,globalphysicalcompletionnull이다.

최종 selected-source refresh는2026-10-27 18:57:55–19:00:38 KST였다. WU late head dde0806dc6b22d20a93e8b904c4104e315a8b653은 비물리 R5 prototype이므로 selected scientificf949c21c pin을 유지한다. REC d6dbe39a…,HE ac6042a6…,BASS009a1238…,VigilODE adapter dda8d2f1…는 동일했다. 원전의 실제 유효범위와 별도 병렬 lane을 덮어쓰지 마라.

다음 과학 의존성은 공개 finalCR C9의 실제 도착 여부, source-matched injection/history 및 recipientnb, photon measure·REC finite opacity·BASS transport/absorption/error radii·HE physical stopping/thermalization/미분·REI nativeVigilODEclient/tube다. 변한 source만 먼저 조사하고 새 계산은 예산 gate를 해결한 뒤 별도 동결하라. 새83전구간,NCP,IVP,provider solve,projection,quadrature,oldfullsuite,attempt01 replay를 자동 실행하지 마라.

각 새 노드 전에 최신AGENTS·실제HEAD·병렬반환·이전백업ACK를 확인하라. 사용자가 필요한 게시·백업·자동 실행을 이미 명시적으로 승인했으므로 같은 권한을 다시 묻지 마라. 독립 검토와 expected-SHA/nonforce push, source ZIP, Drive/Dropbox 완료 ACK, DAG/인계 갱신을 유지하라. PR240은 draft이며 merge되지 않았다.

## 읽을 순서

1. REPORT_KO.md, ADMISSION.json, FROZEN_CONTRACT.md, BUDGET_STATUS.json.
2. theory/THEORY_KO.md, SOURCE_REUSE_KO.md, SYMBOLIC_CHECKS.json.
3. intake/ROOT_SURVEY.json, FINAL_SOURCE_REFRESH.json.
4. implementation/PREEXEC_MANIFEST.json, attempt01/CHECKS.json, OBSERVATIONS.json, RESOURCE_RECEIPT.json, BIN_TABLE.md.
5. reviews/C5_PREEXEC_REVIEW.json, C9_SAVED_RESULT_REVIEW.json, ROOT_RESOURCE_HOLD.json, DAG_TEXT_REVIEW.json.
6. delivery/DAG_APPLIED_RECEIPT.json, STAGE_BACKUP_RECEIPTS.json, FINAL_DELIVERY_RECEIPT.json, STAGE_LEDGER.json.

## 실제 source 전달 결과

- Source snapshot commit: 31d088bb0923d29147efa0d1b358c546fc7f68d3
- Source ZIP: REI_CAUSAL_SOURCE_SNAPSHOT_20261027_31d088bb0923.zip
- SHA256: 70fcb00fab1b5e45904179acc07a8157cb72c3c6b6d20942f05d7b798ad3712d
- Bytes: 525104; payload77files+archiveauthority1entry.
- Drive ID: 1w76UK3dfXnc4OQDfvKHye-9ahmnN1jPp
- Dropbox ID: id:BSpOijBcT10AAAAAAEDHSg
- Git readback:77file의blob·size일치. CRC는생성후1회결과를재사용했다.
- 원래20연구단계모두expected-SHA/nonforce게시와Drive/Dropbox완료ACK를확보했다.
- 최종metadataZIP의자기ACK와원래budgetcap복원은이후Git최종영수증에서확인한다. 새계산과기존attempt재현은중단상태다.

## 최종 metadata 전달·예산 복원

2026-10-27 19:26:03 KST에 전달을 닫았다. 별도 metadata commit은157a41919e5503ef8def183769a61167b2bd15b3, ZIP SHA256는615cb1c3e598b2a54e2f4ab1cf103ff1fc12f4f9153e73505a0f2d0096b4c5dd, 크기는37577bytes다. Drive1LeFi_waWp6YEhhcaaW1VILSMG1UOACMX,Dropboxid:BSpOijBcT10AAAAAAEDHTA의완료ACK를확인했다. 최종Git ACK는이metadata commit다음이며실제branchHEAD를조회하라.

Original policycap planning10/presentation30으로복원했다. 누적planning15.077490885와presentation실측·기존예약43.528719494+최종publication/tail예약.05=43.578719494를보존했다. ResourceHOLD이며새localplanning·과학실행을허용하지않는다. OriginalDAG작업32/88·중앙27/88·증분0,L4false다. Source와metadata ZIP을각각이중백업했고,20단계의44개전체archiveupload완료ACK(단계40+source2+metadata2)를확보했다. 수치검사와CRC를재실행하지않았다.

