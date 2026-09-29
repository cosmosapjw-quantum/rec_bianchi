# Task6 진행 기록

Task6: 작성 완료, Python self-test32 통과, Rust 검증 대기. Source input과 acceptance 사전등록 후 reference 계산 및 observable adapter를 작성했다. Parent Task5는 immutable이다.

Ruling: frozen_inputs_v2.json과 acceptance_v2.json은 이미 Task2 domain 계약이므로 덮어쓰지 않고 source_inputs_task6.json/acceptance_task6.json을 추가한다. reference_values_v2.json은 새 full-source reference다. 비용은 파일2개 증가이며 기존 domain provenance를 보존한다.

Ruling: third-party Rust JSON dependency를 추가하지 않는다. 작은 strict token stdin과 strict JSON stdout을 사용한다. 실제 parser/type correctness는 local에 남으며 end-to-end verified라고 쓰지 않는다.

Ruling: 이 단계는 Task6에서 종료한다. Task7은 original T4 mapping, Task8은 Git 게시다. compilation은 승인된 역할 분리에 따라 local Codex에 맡긴다. 기존 scientific HOLD와 unverified candidate 상태는 유지한다.

Python regression red: inherited close의 Inf/tiny-source false acceptance 및 새 comparator 부재로 3 failures. 현재 32개의 검사에서 해당 기능과 negative output/exception 경로를 검사했다. 다른 API가 사전 작성되었다는 사실을 Rust-red/green으로 부르지 않는다.

Collection ruling: Python self-tests require explicit fixture/evidence binding via --self-test. HarnessTests.__test__=False prevents accidental collection by the pre-existing pytest job. Actual 32-test rerun passed after this metadata-only guard.
