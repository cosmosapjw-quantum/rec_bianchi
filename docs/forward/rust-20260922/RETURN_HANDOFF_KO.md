# 원 이론방 반환 — selected-He Rust fixed-input port

`rec_bianchi`의 `forward/rust-he-sources-20260922`에 `rec_microphysics` 실제 호출 가능한 source를 적용했다. 원 base는 `5a09f3797210284f83a1a1adb0e0092d1ac48475`, metadata dispatch는 `c99a3579064a9691ba33809fc062ddc0a35396b7`, source import는 `0ef9968c1dcfa17ba63072965902c86d3b59d9ad`, 실제 테스트한 source SHA는 `2ee3760870f9ac47eaab518a4c4a907f1a3f6f85`다. 최종 delivery SHA는 이 문서를 포함한 feature branch tip이며 `git ls-remote origin refs/heads/forward/rust-he-sources-20260922`로 확인한다.

A7 ZIP `9ef3929dd1164c482cb200a7c1a10e57e1e0a78c6ab47c9cc8dfd8f5fc23ce6a` / 8,541,005 bytes를 로컬 백업에서 회수했다. 내부 A6 `d8a5f4afe2ab619407f55e9ac9f5b0c9e5196689301b78c1cc98138e9c18a628` 및 양쪽 manifest가 맞다. WU29 RESULT, WU30 RESULT, WU31-A1, T4 interface/coverage/ledger/test matrix 원문 10개를 `source_subset/`에 byte-preserving 보존하고 `SOURCE_IMPORT_LOCK.json`으로 잠갔다. 9월 weak/JVP와 `study.py@59dafbd34bc21b1b885c716b7b8cc899636bbd60` blob `f1ad5926de6090e8317961c6cc58914cfd5c8ba3`는 oracle pin이며 연구 재실행/merge가 아니다.

실제 세 필수 검증은 모두 exit 0이다: cargo fmt check, cargo test --locked (75/75), Python Rust parity (251 cases, 3,027 numerical components, 111 expected typed errors; fixed implementation tolerance 4096 epsilon). 첫 source SHA의 format exit 1 및 BB lower-population JVP subtraction cancellation parity exit 1을 원로그로 남겼고, tested SHA는 affine BB 항을 직접 평가한다. T4 material Gate P의 11개 ID에 매핑된 시험이 모두 실행되었으나 독립 검토 lifecycle이 `RUNTIME_MISMATCH`여서 Gate P 최종 판정은 HOLD다. Gate I/full T4, S4/S5, G10, E1C, history/observable은 PASS라고 하지 않는다.

P/S BF는 Jacobs high q=1..1.4, pair는 D86 y=.025..975만 제공한다. 그 밖의 위문턱 자료는 MissingAuthority, pair outband는 typed error, BF below-threshold만 physical zero다. Bhatia/Jacobs stitch나 total-rate rescale은 없다. 기존 Python/C solver 수식과 PROJECT_STATE scientific PASS는 수정하지 않았다. consumer integration은 현재 허용하지 않는다.

원로그·범위·리뷰 보류: `docs/forward/rust-20260922/task9/EXECUTION_RECEIPT.json`, `FORWARD_STATUS.json`, `SOURCE_DOMAIN_MANIFEST.json`. 다음은 이 exact tested SHA의 독립 검토 binding을 해결한 뒤 다른 repo의 exact-rev integration, 또는 이 port 종료뿐이다.

동일 tested source/원문/원로그 ZIP `REC_BIANCHI_RUST_FORWARD_TESTED_2ee3760_20260929.zip` (424,424 bytes, SHA-256 `38bb7b9488d9569c813c73fd5d11f1c66b766f08aff204ac8026b7d7430257da`)은 create-only로 Dropbox `id:BSpOijBcT10AAAAAADv-Eg`, Drive `17yTxKPkvfOYn7M8KwPOwPXeXdE74ZhIr`에 업로드 성공했고 size/native hash R1이 일치한다. 이는 restore 검증이 아니다.
