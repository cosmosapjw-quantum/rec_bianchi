# 갱신: PR79의 완료된 7개 검사는 재사용한다

이 파일은 최초 authoring checkpoint 뒤에 확인한 실제 Git 상태를 반영한다.
최초 AUTHORING_STATUS.json과 SCIENCE_COMPLETION_KO.md의 미실행 표시는
그 작성 시점의 기록이다. 과거 파일을 소급 수정하지 않는다.

## 확인한 기준과 증거의 등급

PR79 head는 이제 0db9612b8c1fb2c6c8119f23138ff5efe54fcc06이고, 실제 계산
source는 여전히 2e3b73972ee298d44efdfb10016e314f58b0bada / tree
471442ce757fde701340729cd1abde281fd0db01이다. Git compare에서 child는
CHECKPOINT_KO.md, OBSERVED_RESULT.json, COUNTEREXAMPLE_SUMMARY.csv,
RETURN_HANDOFF_KO.md 네 결과/문서 파일만 추가함을 확인했다. 실행 코드,
원본 표, src/tests 및 비교 기준은 바뀌지 않았다. 이 대화가 PR79 branch를
갱신한 것이 아니며, 그 source를 새로 실행한 것도 아니다.

다음 실제 Git 파일을 읽었다.

https://github.com/cosmosapjw-quantum/rec_bianchi/blob/0db9612b8c1fb2c6c8119f23138ff5efe54fcc06/docs/research/rec_multi_bin_affinity_20260907/OBSERVED_RESULT.json

Git blob: a3244d115b7fc5f17b70a14af5aefc4c3b36aad3.
record_kind는 STRUCTURED_READBACK_OF_HOSTED_JOB_SUMMARY_NOT_ORIGINAL_RESULT_BYTES다.
이 구별을 유지한다. 현재 대화에서 Actions를 호출하거나 원본 job log,
ZIP 또는 전체 CSV/PNG artifact를 다시 가져온 것은 아니다.

## 재사용하는 기존 결과

구조화된 readback에는 7개 exact TestID 전부 PASS, failures/errors/skips0,
exit0, 84개 JVP 비교 최대 scaled 오차6.4310422961310704e-15와 실행 source/
tree/원본 blob 및 환경이 기록되어 있다. 기존 허용치는9.094947017729282e-13이다.
이 결과는 새 실행으로 합산하지 않는다.

동일 제조 상태에서 sigma=S/(N_H k_B)의 시간미분은 다음과 같이 기록됐다.

| 읽기 | base [s^-1] | hires [s^-1] |
|---|---:|---:|
| chi | +0.00028173611409276625 | +0.00028167186474992016 |
| log control | -0.0002603135345552853 | -0.0002601446373071536 |

read-proxy는 양수이며 보존 장부가 맞아도 실제 nodal entropy가 음수가 될 수
있다는 기존 다중-bin 결과다. 유리수 rank3 witness bin들은 base[0,1,16],
hires[0,1,34]로 기록됐다. 7변수의 이상적 nullity4와 새 명시적 네 보존량
유도는 정합적이다. 위 숫자를 이번 대화에서 새 계산한 것으로 부르지 않는다.

## 실행 인계의 변경

최종 인계는 LOCAL_CODEX_HANDOFF_V2_KO.md다. 이전 LOCAL_CODEX_HANDOFF_KO.md의
기본 all-lane 실행 지시는 이 업데이트로 대체한다.

- 원래7개 그룹과84개 비교는 재실행하지 않는다.
- 새4개 보충 그룹과16개 방향만 --only supplement로 실행한다.
- 새 plot_supplement.py는 보충 CSV를 읽어90mm/180mm 그림을 만들며 source나
  테스트를 재실행하지 않는다. 직접 시각검토는 별도로 수행한다.
- 과거 PR79 원본 artifact의 바이트 회수/전체 manifest 인증/원본 PNG 시각검토는
  아직 완료되지 않았다. Actions 금지를 우회하거나 새 그림을 옛 그림의
  복구본으로 표시하지 않는다. 기존에 로컬/Git에 원본이 이미 있으면 그것만
  읽을 수 있으며, 없으면 역사적 원본 자료 수령의 미완료를 그대로 남긴다.

추가 검사의 최초 실행 source는 최종 V2 인계의 고정 SHA를 따른다.
기존 wrapper의 --only supplement 성공명은 선택된 lane 성공이며 전체
repository/물리 solver PASS가 아니다. 현재 새4개와 새 renderer의 syntax/
runtime/시각검토는 여전히 미수행이다.

## 다음 과학 연구와 현재 보강의 의미

PR79가 열어 둔 다음 연구는 REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE다.
이번 보강은 그 전에 해상도 증가를 잘못 해석하지 않도록 현재 kernel의
의미와 JVP의 미검사 좌표를 명시하는 작은 연구 보완이다. 공식 DAG dependency나
새 물리 admission gate를 추가하지 않는다.

직접 유도되는 일반화: 대칭 N=2m+1 node에서 한 transition의 D는 m쌍의
대칭성과 sum D=2를 만족한다. atom-sum, composite count, m개의 pair-difference
행은 독립이므로 rank V<=m+1, count 차원 N+2에서 nullity>=m+2다.
해당 bound를 포화하는지는 실제 활성 bin의 rank를 확인해야 한다. 따라서
refinement 때 영모드 수의 증가 자체를 수치 불안정이나 물리 열평형 실패로
판정하지 않는다. 같은 reference measure와 보존량을 명시하지 않은 서로
다른 target 결과를 물리적 수렴 비교로 인정하지 않는다. 실제 격자 refinement
구현·실험은 이번 보강에서 수행하지 않았다.

NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false;
provider_admitted=false. 새 수치 실행0회, Actions 사용0회. 현재 갱신은
저장된 결과의 재사용 및 로컬 잔여 작업의 축소이지 새 PASS 인증이 아니다.
