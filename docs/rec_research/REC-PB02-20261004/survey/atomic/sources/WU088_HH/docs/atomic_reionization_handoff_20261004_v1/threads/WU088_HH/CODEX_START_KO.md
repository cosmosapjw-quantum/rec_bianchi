# WU088_HH Codex 시작 프롬프트

현재 연구 branch `research/r31ao-unequal-order-ladder-20260930`에서 작업한다. 이 문서가 포함된 publication successor를 기준으로 시작하되, REPO_SNAPSHOT.json의 원 science commit `4502a46c0111307d139aa0f0b9b2cd721e559a9d`와 publication commit을 구분한다. 원격 HEAD가 더 새로워졌으면 현재상태를 한 번 reconcile하고 additive로만 작업한다. 새 branch, main merge, force push는 하지 않는다.

1. repo의 AGENTS.md와 지정 root4문서를 읽는다. 이 패키지의 TASKS.json, PREWORK_KO.md, REPO_SNAPSHOT.json을 읽는다. 34 finite checks가 이미 실행됐지만 production provider가 아님을 유지한다.
2. 첫 실행노드는 HH-F1이다. rei_bianchi가 제공한 domain/observable budget이 아직 없으면 그 field를 명시해 `WAITING_ON_REI_DOMAIN`을 남기고 형식·출처·process mapping까지 완료한다. 임의의 10³–10⁶K나 audit fixture SED를 application authority로 만들지 않는다.
3. Grackle3.4.1 k57 LCS vs corrected KS를 named scenarios로 연결한다. k57의 artificial floor=1e-20 at units=1, T<=3000K이며 경계는 불연속이다. 관통 interval에 smooth derivative를 쓰지 않는다. source R=k*n_HI²에 추가1/2 없음, 열항 threshold 한 번, dnpart 포함.
4. HH-F2는 기존 rei Rust seam을 사용하고 solver복제 금지. 이 HH repo에는 provider specification·원전 pin·portable reference를 두며 실제 consumer 구현 위치는 rei가 확정한 path를 따라간다. TASKS의 proposed path를 기존 file로 가정하지 않는다.
5. paired numerical history의 단일 실행 owner는 REI-F09다. HH-F3는 `docs/atomic_reionization_handoff_20261004_v1/runtime_outputs/paired_atomic_sensitivity_v1.json`을 읽어 감도를 해석·수락하고 별도 campaign을 실행하지 않는다. 그 결과를 받기 전 HH-F4를 완료표시하지 않는다. old24/289, epsilon null을 새 rate 검증으로 바꾸지 않는다.
6. 이번 범위의 결과를 source hash, exact commands/exits, passed/failed checks, claim ceiling으로 반환한다. 같은 branch additive commit, 기존 PR #33 연결, Drive/Dropbox create-only ACK+metadata 이중백업. restore를 실제 하지 않았다면 RESTORE_VERIFIED=false다.

경량 참조 검산을 변경해 다시 확인할 필요가 있을 때 repo root에서:
```sh
python3 -B docs/atomic_reionization_handoff_20261004_v1/threads/WU088_HH/verify_prework.py /tmp/hh_prework_result.json
```

legacy를 요청받으면 LEGACY_LANE.json의 entry sequence를 따른다. FD2 네 callback은 이미소모됐다. 기존 command의 마지막 outdir만 바꿔 다시돌리는 행위는 새연구가 아니며 금지된다. 첫 조치는 저장raw/read-onlyreview이고 새과학실행scope는별도유한계약으로작성한다.

반환은 공통 `../../common/RETURN_CONTRACT.schema.json`을 따른다. 필수 최상위 field는 `task_id`, `state`, `input_identity`, `changed_paths`, `commands`, `artifacts`, `claim`, `next_task`다. exact input commit/hash, 실행 command/exit, artifact path/hash, 현재 claim ceiling을 넣는다. HH의 coverage24/289, epsilon null, B22와 FD2_consumed 상태는 `extensions.hh_legacy`에 넣을 수 있다. `next_task`에는 TASKS.json의 실제 ID 하나 또는 기다리는 외부 dependency를 반환한다. 미실행 명령에는 executed=false를 명시하고 실행성공 목록에 넣지 않는다.
