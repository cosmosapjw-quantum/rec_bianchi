# selected-He local transport/verification entry

이 commit은 **metadata-only dispatch**다. Task1–7 누적 Rust source가 이 Git tree에 적용됐다고 해석하지 않는다. 기존 49d64b26의 Rust 코드를 새 후보 대신 검증하지 않는다.

1. `task8/TRANSPORT_DISPATCH.json`의 package 이름·SHA-256·크기·provider ID를 읽는다.
2. 기존 Dropbox 동기화본 또는 동일 local package를 우선 사용한다. 없을 때만 승인된 provider에서 취득한다.
3. package SHA/CRC/manifest를 검증하고 안의 `LOCAL_CODEX_START_KO.md`를 실행 계약으로 읽는다.
4. 기존 repo의 origin/branch/AGENTS/dirty state와 dispatch 이후 diff를 확인한 뒤 `candidate/`를 적용한다. 사용자 변경은 보존하고 겹치는 path만 보류한다. 새 worktree/reset/stash/clean/force-push/merge/release는 금지한다.
5. 실제 source를 commit한 C1의 full SHA와 source-content manifest를 기록한 뒤 local 검증을 시작한다. 이 dispatch SHA는 source candidate나 tested SHA가 아니다.

```bash
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
```

원로그·exit·실제 개수·Gate P audit를 보존한다. local 최소 수리는 가능하지만 source/acceptance/tolerance를 바꾸어 green을 만들지 않는다. source 수리 뒤에는 실제 시험한 SHA를 새로 기록한다. dependency 0의 rec_microphysics만 대상이다. bianchi_rustcore/vendor 전체/scientific full-suite/trajectory는 실행하지 않는다.

세 필수 gate와 Gate P가 실제로 닫힌 후만 검증된 source라고 한다. 실제 source C1과 evidence-only C2를 구분하여 같은 feature branch에 fast-forward push하고 remote R1 및 create-only 이중 백업을 남긴다. 원래 T4 consumer 의무, G10/E1C/S4/S5 및 physical HOLD는 유지한다.
