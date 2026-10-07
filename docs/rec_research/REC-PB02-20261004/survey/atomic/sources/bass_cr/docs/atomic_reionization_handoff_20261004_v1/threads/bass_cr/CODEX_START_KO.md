# bass_cr: Codex 바로 시작

이 packet은 CR-off fastest track의 원자자료 의존성 제거와 원자 lane 보존을 끝낸 선행 연구다. `TASKS.json`을 먼저 읽고 `CR-F0`의 아직 끝나지 않은 receiver binding만 수행한다. legacy·CR-on nodes는 자동 시작하지 않는다.

## 최소 읽기 (순서대로)

1. 현재 repo `AGENTS.md`와 이 packet `REPO_SNAPSHOT.json`.
2. `TASKS.json`의 CR-F0, `PREWORK_KO.md` §2–5, `VERIFICATION.json`.
3. 대응 rei_bianchi packet의 CR-off binding task. 원자 ledger가 이뤄져야 Rust consumer 전체가 검증됐다고 추정하지 않는다.
4. 원자 연구를 요청받았을 때만 `LEGACY_LANE.json`과 `legacy_sources/.../r4ao_finite_cell/NEXT_DAG.json`을 읽는다.

## 환경과 exact source

아래 명령의 repo는 실제 checkout에서 실행한다. source ancestor pin이며 publication HEAD가 다를 수 있다. root `PUBLICATION_RECEIPT`의 실제 게시 commit을 읽고 현재 branch와 관계를 확인한다. 기록되지 않은 unrelated 변경을 reset/rebase/overwrite하지 않는다.

```bash
CR_PACKET="$PWD/docs/atomic_reionization_handoff_20261004_v1/threads/bass_cr"
git branch --show-current
git status --short
git rev-parse HEAD
git merge-base --is-ancestor b263cbe3b7ab10e1a5fee919def22938ab7515cd HEAD
python -m json.tool "$CR_PACKET/TASKS.json"
```

명령은 read-only다. 원격 pin read 뒤 branch가 더 진행됐다면 변경된 파일만 비교하며 gate를 보존한다. 검증 reference가 그대로이면 이미 통과한 10개 시험을 반복하지 않는다. 환경/코드가 바뀐 경우에만:

```bash
PYTHONPATH="$CR_PACKET/reference" python -m unittest discover -s "$CR_PACKET/tests" -v
```

이 검사는 0.0x초 규모의 단위회계만 수행한다. Atomic native, existing full suite, CR propagation, old one-shot pilot을 호출하지 않는다. reference/cr_contract.py를 실제 external σ provider로 등록하지 않는다.

## Fastest 종료

rei_bianchi의 실제 CR off dispatch가 optional supplier를 호출하지 않는지 focused integration으로 확인하고 `CR_OFF_ACCEPTANCE.json`에 receiver commit, observed zero source, no provider callback, source/prompt identity를 남긴다. 원자 physics 완료 상태를 올리지 않는다. 그다음 rei_bianchi nonlinear consumer/첫 이력 task를 진행한다. bass_cr에서는 추가 atomic calculation을 baseline requirement로 만들지 않는다.

## 원 연구 즉시 재호출 (읽기만)

```bash
git show b263cbe3b7ab10e1a5fee919def22938ab7515cd:research/convergence_20261004/r4ao_finite_cell/NEXT_DAG.json
git show b263cbe3b7ab10e1a5fee919def22938ab7515cd:research/convergence_20261004/r4ao_finite_cell/SCOPED_RESULT.json
git show b263cbe3b7ab10e1a5fee919def22938ab7515cd:docs/roadmap/RESEARCH_PLAN_KO.md
```

Git 불가이면 같은 문서들이 legacy_sources/에 있다. source-resume는 R4AP부터이며 실제 native 실행은 그 새 계약이 준비되고 허용될 때만 한다. R4AO SCOPED_RESULT는 원 raw evidence 자체가 아니라 hash index다. 원 raw를 사용할 때는 `BASS_CR_R4AO_FINITE_CANDIDATE_CELL_PACKAGE_20261004_v1.zip`의 실제 object+SHA를 가져와 검증한다. 현재 packet은 그 archive를 다운로드/restore했다고 주장하지 않는다.

## 반환 계약

공통 `../../common/RETURN_CONTRACT.schema.json`을 따른다. 필수 envelope는 `task_id`, `state`(completed/partial/blocked), `input_identity`, `changed_paths`, `commands`, `artifacts`, `claim`, `next_task`다. `commands`의 각 원소는 `{command, exit_code, evidence_path}` 객체이며 주석이나 실행 조건을 shell 문자열에 붙이지 않는다. `claim`에는 `basis`와 `ceiling`을 넣는다. source commit/tree/file hashes는 `input_identity`에, 추가 tests/physics_calls/native_calls/receiver_commit/publication_receipts/backup_receipts는 `extensions`에 둔다. `PREWORK_RETURN.json`은 실제 완료 범위의 partial 반환이다. 이 작업의 native_calls는 0. 실패는 `blocker` 객체에서 THEORY/NUMERICAL/IMPLEMENTATION/RUNTIME/PROVENANCE/PERMISSION으로 분류한다. Drive/Dropbox 각각 실제 ACK/ID/size가 있어야 dual backup complete, metadata 확인은 RESTORE_VERIFIED 아님.
