# selected-He Rust fixed-input port — 다음 실행점

Repository `cosmosapjw-quantum/rec_bianchi`, branch `forward/rust-he-sources-20260922`.

- 원 base: `5a09f3797210284f83a1a1adb0e0092d1ac48475`
- 실제 tested/reviewed dependency source: `d3cc6e0120061f113d28e7a3a55a2e3dd561e81e`
- 최신 evidence delivery: `git ls-remote origin refs/heads/forward/rust-he-sources-20260922`로 확인. Delivery SHA를 dependency source와 혼동하지 않는다.

F1은 수리되었다. `assemble_he_event_ledger`는 유한 입력의 산술 overflow를 `NumericalDomainUncertain`으로 반환한다. fmt, Cargo 76/76, frozen parity 251건·3027성분·111 expected typed errors가 author root와 별도 checkout에서 모두 PASS다. 새 읽기 전용 독립 리뷰는 runtime MATCH, 추가 finding 없음이다. Gate-P의 고정 입력 구현 리뷰 보류만 해제했다.

현재 근거는 `f1_repair/FINAL_DECISION.json`, `f1_repair/RERUN_RECEIPT.json`, `SOURCE_IMPORT_LOCK.json`, `SOURCE_DOMAIN_MANIFEST.json`이다. 원 이론 10파일과 source manifest 44파일의 hash를 확인했다. WU29/WU30/WU31-A1/T4 authority, Jacobs high q=1..1.4, D86 y=.025..975, below-threshold physical zero, outside-authority typed error는 그대로다. table stitching, rescale, 허용치 변경은 없다.

재현 명령(위 exact source에서):

```sh
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
```

다음 작업은 이 port 종료 또는 별도 승인된 다른 repo의 위 exact-rev integration으로 한정한다. `allow_consumer_integration=false`는 이 repo에서 consumer 실행을 승인하지 않았음을 뜻한다. full T4/Gate I/S4/S5/G10/E1C/history/observable/production PASS가 아니다. S3 accepted, S4 partial, S5 gated, G10 open, G11–G13 gated, D86 canonical, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized는 유지한다.

첫 formatting/BB-JVP 실패는 `task9/logs/initial/`, 이전 F1과 독립 리뷰는 `review_rebind/`에 보존한다. 최신 create-only 백업 결과는 `f1_repair/BACKUP_RECEIPT.json`을 확인한다. 업로드 검증은 복원 검증이 아니다.
