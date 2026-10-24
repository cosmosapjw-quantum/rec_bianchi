# 게시 직전 고정 delta — c40d287

## 종료 기준과 결과

**c40d287874f72519103e68267e659fc022eba188**를 이 publication-preservation delta의 마지막 pin으로 고정했다. 이후 HEAD를 다시 조회하지 않는다. 전체 저장소·branch·Library 조사, 새 과학 실행, source code 수정, provider/Git write는 모두 0이다.

`PUBLICATION_BASE_METADATA.json`은 이 pin으로 갱신했다. 기존 fca metadata는 `PUBLICATION_BASE_METADATA_fca9a31.json`, 기존 DAG는 `DAG_latest_fca9a31.json`에 그대로 보존되어 있다.

| 항목 | 최신 고정 값 |
|---|---|
| expected parent / commit | c40d287874f72519103e68267e659fc022eba188 |
| commit의 parent | e69b01457f1f27e11806ad724a925a1f723d0c24 |
| base tree | 70cf91195bff1cfe5b457f8f90f6a6bf56a879d1 |
| DAG Git blob | dafa825788e959c1ae07f4dd01d8eb6b43ce06f5 |
| DAG bytes | 244479 |
| DAG SHA256 | 3aeb68c335bd3676aec75138b74c4faac1a45348e022f1c36f7d66c4527126ae |
| 원문 파일 | DAG_latest_c40d287.json |

예정 새 draft branch `research/rec-history-refinement-observation-20261024`의 404는 root의 사전 관측으로 기록했다. Worker가 이 branch를 다시 조회하거나 생성하지 않았다.

## 필요한 변경만 읽음

fca9a31 이후 두 commit이다.

1. `e69b01457f1f27e11806ad724a925a1f723d0c24`: HE-ANG TDCS54 sparse source 관측 추가.
2. `c40d287874f72519103e68267e659fc022eba188`: REI selected-HI consumer의 publication/recovery closeout. 기존 science와 pressure 미실행 상태 유지.

중앙 DAG 외에 세 문서만 원문으로 읽었다.

- `assembly/returns/BASS_HE_HEANG_TDCS54_ANCHORS_20261024.json`
- `hi_primary_20261024/NEXT_PRESSURE_STATUS.json`
- `hi_primary_20261024/publication/PUBLICATION_READBACK.json`

새 source 원문 네 개의 bytes를 계산한 Git blob은 **4/4 일치**한다.

## 중앙 보존

40개 original contract와 plan_status, 17개 integration edge, authority와 dependency field가 모두 동일하다. 바뀐 node는 **HE-ANG.observed_completion 하나**다. 나머지 39개 node, HE-X1, CR N5, REC node들은 exact match다.

HE-ANG 내부 변화도 기존 관측을 보존한다.

- 기존 evidence 12개는 동일한 순서와 값으로 유지하고 4개를 append했다.
- `next.sparse_joint_status`를 추가했다.
- `tdcs54_anchors_subunit`을 추가했다.
- 기존 CCC/DDCS 관측의 값을 바꾸거나 지우지 않았다.

따라서 다음 REC patch의 “다른 38개 node 보존” 기준은 **c40d287의 node objects**다. 오래된 fca DAG를 전체로 올리면 새 HE 관측이 사라지므로, 준비된 최신 원문을 base로 사용해야 한다. PR224의 observations donor와 REFINE01 새 관측을 REC-LINE02/REC-HISTORY에만 합치고, contract·plan_status·authority·dependency와 다른 38개 node를 그대로 유지한다.

## REC H5에 미치는 영향

HE의 science pin은 **60cacdb740fa4dadcdcbff43b7ffcb52566e077d**, draft PR96이다. 새 결과는 54.4 eV incident/5 eV slow-electron 조건의 **두 source-located H1s reported TDCS 좌표**와 nominal common-scale/shape 진단이다. 실제 sparse source data가 추가된 사실을 인정한다. 이 데이터는 이미 reported TDCS이므로 추가 spin/exchange count factor를 적용하지 않는다고 명시되어 있다.

현재 return의 판정은 COMPLETE_SCOPED, R6 PASS, C9 PASS_AFTER_FIGURE_CORRECTION이며 source stage는 19/20, C10 delivery pending이다. B1 dual upload/metadata readback 확인과 B2 pending도 구분되어 있다. 이 worker는 backup bytes나 원 논문의 수치 전체를 재검증하지 않았다.

**physical_provider_admitted=false**, **full_joint_law_admitted=false**, parent **SOURCE_INPUT_PENDING**은 유지된다. full source-consistent joint law, count/spin/support/frame/recoil/uncertainty 입력이 여전히 요구된다. Sparse TDCS 좌표는 REC 원래 target의 same-parameter history, endpoint/reference uncertainty 또는 temporal curvature bound를 공급하지 않는다. 따라서 **원래 REC H5의 INPUT_DEPENDENT_UNCALIBRATED 상태에는 변화가 없다.**

HI publication readback은 기존 fca9a31 science/source와 pressure 준비의 실제 게시를 확인하는 owner record다. Pressure 상태는 DERIVED_PASS_SCOPED/PREPARED_PASS_STATIC_SCOPED, **numerical_validation NOT_RUN, scientific_children 0, physical EOS/stock closure NOT_ADMITTED, L4_ready=false**다. 새 execution proposal도 NOT_AUTHORIZED다. 별도 history uncertainty 입력은 생기지 않았다.

## 이어서 사용할 파일

- `PUBLICATION_BASE_METADATA.json`: 현재 c40 fixed pin과 exact DAG path.
- `PRESERVATION_CHECK_c40d287.json`: 40/17/authority/owner 보존 및 source byte identity.
- `REC_PRIOR_OBSERVATION_DONOR.json`: PR224의 원래 REC observations만 추출한 자료.
- `COMPARE_fca9a31_c40d287.json`: 두 commit의 실제 changed-file metadata.
- `COMMIT_METADATA_c40d287.json`: commit/tree/parent 원 응답.

Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다.
