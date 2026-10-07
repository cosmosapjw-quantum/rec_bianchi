# selected-He Rust forward-port 반환

STATUS=`FIXED_INPUT_SELECTED_HE_SOURCE_PARITY_PASS__DELIVERY_SHA_IS_BRANCH_TIP`

- repository: `cosmosapjw-quantum/rec_bianchi`
- base: `5a09f3797210284f83a1a1adb0e0092d1ac48475`
- target branch: `forward/rust-he-sources-20260922`
- source-code commit: `1bc9d9527deed4a153dbcb7edbb6c7b56016f668`
- exact delivery SHA: 이 문서를 포함하는 branch tip을 Git remote에서 확인하여 외부 반환에 기록한다. self-referential commit SHA는 파일 안에 고정하지 않는다.

구현된 callable API: `he_bb_source`, `he_p_bf_source`, `he_s_bf_source`, `he_two_photon_pair_source`, `assemble_he_event_ledger`.

검증: Rust 1.94.1에서 `cargo fmt --check`, `cargo test --locked` (15 tests), Python fixed-source parity runner, `cargo clippy --all-targets -- -D warnings`가 모두 exit 0이다. 상세 원로그는 `logs/`에 있다.

범위: material-frame fixed-input selected-He source parity만 닫는다. finite-tilt normal-frame screen/boost transport, E1C split-domain ownership replacement, full HyRec trajectory, S4/S5 promotion, G10, G11-G13는 미승격 상태를 유지한다.
