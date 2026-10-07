# Local Codex Task6 확인

실제 Task8 candidate SHA를 기준으로 여기서 하지 않은 컴파일/실제 source parity를 실행한다. 새 입력은 251개(3027 numeric components)이며 expected error111개도 전부 비교한다. 숫자는 고정 계약 수이고 예상 PASS 개수가 아니다. 기존 Rust test70개는 Task6에서 변경하지 않았다.

`python scripts/check_rust_forward_parity.py`는 dependencies 없는 example을 한 번 호출한다. Args와 stdin은 input_wire_v2.py가 source_inputs_task6.json에서 만든다. source/fixture lock 확인 후 실제 output으로만 PASS를 판단한다. `--self-test` 32개 통과와 전체 Rust parity를 구분한다. 본 default runner를 이번 웹 스레드에서 실행하지 않았다.

실패 시 source/formalism, numeric, parser/type/compile, dependency/environment, service를 분리한다. 미세한 format/type/adapter 수리는 허용되지만 tolerance/scale 확대, reference를 actual로 대체, unknown을 0으로 변경은 금지한다. Rust adapter/parser 오류로 input이 거절되어도 physics failure로 오분류하지 않는다. 고정 reference generator 재생성이 필요하면 먼저 파일identity와 참조 식을 확인하고 변경/결과 provenance를 반환한다.

Raw subprocess record는 UTC/cwd/command/exit/stdin/stdout/stderr/SHA를 가진다. Caller의 exact tested SHA와 code-content manifest는 Task8/9 outer receipt에서 결합한다. 이 harness 단독 성공은 tested Git commit identity를 인증하지 않는다.
