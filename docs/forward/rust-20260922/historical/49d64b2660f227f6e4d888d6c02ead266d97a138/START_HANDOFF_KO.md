# rec_bianchi selected-He Rust forward-port handoff

다음 실행 지점은 `forward/rust-he-sources-20260922`의 branch tip이다. 이 branch의 목적은 `rec_microphysics` fixed-input pure-Rust source parity이며 E1C/G10 continuation이 아니다.

확인 명령:

```bash
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
cargo clippy --manifest-path rust/rec_microphysics/Cargo.toml --locked --all-targets -- -D warnings
```

다음 허용 작업은 둘 중 하나다.

1. 다른 repo/consumer에서 이 branch tip exact revision을 pin하여 integration test를 수행한다.
2. 이 forward-port를 여기서 종료한다.

자동으로 E1C split-domain replacement, dynamic macro/history, S4/S5 promotion, G10/G11-G13로 넘어가지 않는다. P/S low numerical authority를 발명하거나 Bhatia-low/Jacobs-high를 이어붙이지 않는다. D86 band 밖을 0으로 바꾸지 않는다.
