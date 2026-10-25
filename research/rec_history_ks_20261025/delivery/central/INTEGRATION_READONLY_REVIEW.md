# REC-HISTORY-KS01 중앙 additive patch 독립 읽기 검토

## 판정

**PASS_SCOPED_ADDITIVE_CONTENT — latest42f의 DAG와도 동일한 source 위의 제한된 관측 추가임을 확인했다.**

검토 당시 prepared bundle의 base metadata는 a28ba였다. Root의 publication 직전 조회가 새 HEAD42f5984a78f123ce26950cec0e0b8505da3e7ce4를 발견했고 create_tree 전에 중단했다. 아래 검토는 actual latest42f를 추가 실독한 결과다. **Publication parent/tree와 준비 guardrail의 provenance를42f로 결속하는 것은 필요하며 coder가 별도 수행한다.** 기존 additive DAG content의 재생성이나 과학 재실행은 필요하지 않다. 이 문서는 원격 게시/readback 완료를 주장하지 않는다.

## 최신 source와 변경분 증거

| 항목 | 실제 identity |
|---|---|
| 최신으로 전달받아 실제 읽은 commit | `42f5984a78f123ce26950cec0e0b8505da3e7ce4` |
| Parent | `a28ba343bb85addf1a7e9e58e75816ed3b75cd3b` |
| Tree | `67626987bc03fa60a1f340aaf8b5c6a63ba022d2` |
| Compare | ahead1 / behind0 / total_commits1 |
| 변경 파일 |75개, 모두 `research/rei_source_pair_binding/hi_massive_stress_20261025/` 아래 새 파일 |
| DAG blob | `1dff0d1770815c6a9a19ccb828c02ebff29c0e8f`,405253bytes |
| DAG SHA256 | `5bf7ef173a3501df4e476321a9bcdb23e7b7a989e5be61f157d546b01ebfc5e2` |
| DAG와 a28ba의 관계 | raw UTF-8 bytes 전체 동일 |
| Root AGENTS blob | `429a5a13ee75b1222bc50627f8d5973d01dd21c4`,9351bytes |
| Fixed REI handoff blob | `b7282c1d88dbb7622853c697d5787d43b12fe8ef`,19988bytes |

따라서 latest42f의 tree를 부모로 사용하면 새 REI75개 파일을 보존하면서 같은 REC additive content를 게시할 수 있다. a28ba tree로 게시하면 이 최신 sibling payload를 잃으므로 parent/tree를 구별해야 한다.

원문 증거의 절대 경로:

- `/workspace/scratch/0b47675c7a06/rec_history_next_20261025/survey/github/central_source_reads/current_42f598_DAG.json`
- `/workspace/scratch/0b47675c7a06/rec_history_next_20261025/survey/github/central_raw_current_42f_commit.json`
- `/workspace/scratch/0b47675c7a06/rec_history_next_20261025/survey/github/central_raw_compare_a28_to_42f.json`
- `/workspace/scratch/0b47675c7a06/rec_history_next_20261025/survey/github/central_raw_current_42f_assembly.json`
- `/workspace/scratch/0b47675c7a06/rec_history_next_20261025/survey/github/central_raw_current_42f_root.json`

원격 source: https://github.com/cosmosapjw-quantum/rei_bianchi/commit/42f5984a78f123ce26950cec0e0b8505da3e7ce4

## 준비된 content를 독립적으로 비교한 결과

검토 대상은 `prepared/PUBLIC_UTF8_BUNDLE.json`이다. 검토한 bundle raw SHA256은 `3edad29930d96e29c8d5b80237e9167f1f47d36a667bd442d64f553a702f3ffe`다. 이 hash는 **42f metadata rebinding 이전 bundle**의 식별자이며 이후 guardrail metadata가 바뀐 bundle과 구별한다.

검토한 proposed DAG는442848bytes, SHA256 `30454062e7d4d677877f05acc7e00eb793c060e6029bb5af925ff613cdbeb596`, Git blob `2108154f33b7bc6ea4a434158d4bdc112e059aff`다.

| 독립 비교 | 결과 |
|---|---|
| Recursive semantic diff | `add /nodes/12/observations`, `add /nodes/13/observations` 두 개뿐 |
| Node IDs/order 및 count |40개 동일 |
| 최신42f의 다른38개 complete node objects |38/38 깊은 동일 |
| Fixed0f9d의 원 contracts |40/40 깊은 동일 |
| Fixed0f9d의 integration edges와 authorities |17/17,7/7 동일 |
| 최신42f의 root non-nodes fields |모두 동일 |
| 최신42f의 plan_status |40/40 동일 |
| REC-LINE02·REC-HISTORY non-observation fields |두 node 모두 동일 |
| Donor227 REC-LINE02 observation dictionary |8/8 fields 깊은 동일 |
| Donor227 REC-HISTORY observation fields |9/9 fields 깊은 동일 |
| 새 observation |REC-HISTORY의 `KS01` 하나만 추가 |
| KS01 content |DAG nested record, standalone REC_KS01_OBSERVATION.json, root-authored ROOT_KS01_OBSERVATION.json 깊은 동일 |
| UTF-8 byte insertion 비교 |JSON decoder로 두 observations 삽입 구간만 제거하면 latest42f 원 DAG bytes 전체 복구 |
| Bundle/projection 일치 |7/7 path의 UTF-8 bytes 일치 |
| 과거 THERMO return |3/3 원 source bytes 및 Git blobs 보존 |
| Protected path write |AGENTS 및 handoff path가 bundle에 없음 |

구조·원문 보존 assertion23개 모두 참이었다. Lowercoder가 기록한 guardrail 값만 신뢰하지 않고 최신 source JSON, fixed source, donor source, bundle 및 projection bytes를 별도로 읽어 비교했다. `REC_U5`의5개 nested hold fields도 donor 전체 deep equality에 포함된다.

## 최신 REI child의 REC 의존성 영향

최신 leaf의 `execution_20261025/ADMISSION.json`과 `CLAIM_GATE.json`을 headline/scope 수준으로 실제 읽었다. 판정은 `ADMITTED_SCOPED_NATIVE_HI_MASSIVE_STRESS`다. 실제4368 HI radial atoms, z2.479와 source-bound electron nominal mass에서 massive stress, declared-isotropic pressure injection, finite-support defect 및 fixed-atoms source JVP를 다룬다.

그 source 자체도 actual cohort history와 density/initial stock/geometry/collision supply를 OPEN_INPUT_DEPENDENCY로 남기고 physical secondary heat/global bound는 null, L4_ready=false로 기록한다. 이는 REC의 원 z1099.99865 history reference, actual incident trace 또는 full history/retiming/thermal Jacobian을 공급하지 않는다. **REC H5/H6/H7의 미완료 의무와 KS01 범위는 유지된다.** 이 내용은 새로운 full scientific audit 또는 새 REI 결과 재검증이 아니다.

원문: `survey/github/central_raw_42f_ADMISSION.json`, `survey/github/central_raw_42f_CLAIM_GATE.json`.

## 제한된 최신 REC PR 조회

REC PR 목록을 `state=all, sort=updated, direction=desc, per_page=3`으로 한 번 조회했다. 최신3개는 own KS01 PR136(head `309776ec263f10853a7ed4c404387c1474994e96`, draft/open), THERMO PR135, RESP PR134였다. 이 제한된 조회에서는 별도 H6 후속 PR을 발견하지 못했다. 이는 unpublished H6 checkpoint나 다른 대화의 부재를 의미하지 않는다. PR136 body의 S0 문구는 당시 snapshot이며 실제 현재 science progress의 판정에 사용하지 않았다.

## 범위

이 검토는 read-only integration review다. New science0, old campaign replay0, assembler0, renderer0, Git/provider mutation0. Canonical branch 쓰기를 승인하거나 실행하지 않았고, root는 최신 parent에 기반한 isolated draft branch로 publication한다. 실제 최신 HEAD 재확인과 이후 원격 blob/path readback은 publication 담당의 별도 단계다.
