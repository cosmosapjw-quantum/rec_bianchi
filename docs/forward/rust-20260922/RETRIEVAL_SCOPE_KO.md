# selected-He Rust forward-port source retrieval scope

이 forward-port는 `rec_bianchi@5a09f3797210284f83a1a1adb0e0092d1ac48475`와 별도 A7/A6 atomic authority를 결합한 fixed-input port다.

- A7 actual bytes: SHA-256 `9ef3929dd1164c482cb200a7c1a10e57e1e0a78c6ab47c9cc8dfd8f5fc23ce6a`, 8,541,005 bytes, manifest 26/26 verified.
- A6 nested source: SHA-256 `d8a5f4afe2ab619407f55e9ac9f5b0c9e5196689301b78c1cc98138e9c18a628`, manifest 26/26 verified.
- adopted subset: WU29 RESULT, WU30 RESULT, WU31-A1 amendment, T4 interface/coverage/ledger reports+schemas and T4 test matrix.
- 각 raw member의 SHA-256과 size는 `SOURCE_IMPORT_LOCK.json`에 고정한다.
- raw subset bytes는 최종 create-only durable backup artifact에 포함한다. Git tree에는 connector-local binary ingestion 제약 때문에 raw archive를 중복 저장하지 않고 hash lock을 authority로 둔다.
- September weak/JVP 결과는 oracle 의미·허용치만 참조하며 재실행/승격하지 않는다. `study.py@59dafbd34bc21b1b885c716b7b8cc899636bbd60` / blob `f1ad5926de6090e8317961c6cc58914cfd5c8ba3`는 pin만 기록하고 실행하지 않는다.

이 port의 PASS는 selected-He material-frame fixed-input source parity만 뜻한다. E1C split-domain owner replacement, full HyRec trajectory, finite-tilt normal-frame transport, S4/S5 promotion, G10/G11-G13는 그대로 열린 상태다.
