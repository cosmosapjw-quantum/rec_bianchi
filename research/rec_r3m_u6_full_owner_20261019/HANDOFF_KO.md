# REC R3m 이후 인계

사용자가 파일을 준비하거나 수동 다운로드, SSH/SCP를 할 필요는 없다.

## 완료되어 재사용할 노드

이 노드들을 재개 항목으로 다시 등록하지 않는다.

- R3l 42 tests: GitHub Actions와 owner 환경 모두 통과.
- U5 checkpoint capsule:
  - 파일 `REC_R3L_REVIEWED_U5_CHECKPOINT.zip`, 79,241,895 bytes, SHA `3b469781e937fa6a543a007088b73fb5b01a420261e9c4daa2d454cb3ae88106`.
  - 안의 checkpoint SHA는 `7aeec545…`다.
  - Drive 위치: `gdrv:rec_bianchi_research_backups/R3M_U5_CHECKPOINT_20261019_7aeec545/` (file ID `1oYwz16SYxVEV8PW44aygw8yE4X9CCX2I`).
  - Dropbox 위치: `dbx:bianchi/rec_bianchi/20261016/R3M_U5_CHECKPOINT_20261019_7aeec545/`.
  - 256 MiB 미만이므로 단일 파일 전송 한도 안에서 바로 회수할 수 있다.
- pilot128 stored raw:
  - 파일 `REC_R3M_PILOT128_STORED_OWNER_RAW_001.tar.gz`, SHA `137c2e5b…0872`.
  - 위치는 `R3M_PILOT128_OWNER_20261019_d0e534b1/`다.
- full 5210 U6 raw:
  - 파일 `REC_R3M_FULL5210_STORED_OWNER_RAW_001.tar.gz`, 232,521,236 bytes, SHA `8cd5da29…80b9`.
  - 위치는 `R3M_FULL5210_OWNER_20261019_d0e534b1/`다.
  - 결과: `PASS_PENDING_INDEPENDENT_REVIEW`, 독립 재계산 `REVIEW_PASS`.
- PR105 pair16/pair128/smoke3 raw 재감사도 완료했다.

## 아직 승인되지 않은 것

- Python h/h2/h4 U6 수렴. 같은-h parity는 수렴을 보이지 않는다. U5 h `HOLD_9_FAIL`과 h2 `HOLD_8_FAIL`도 그대로다.
- Bianchi/REI/CMB 예측. REI activation은 false다.
- production speedup은 측정하지 않았다. stored 대 compressed의 full 비교는 하지 않았다.

## 다음 최소 행동 후보

1. 수렴 연구 계약을 따로 작성한다. 대상 h 격자, 동일 operator·boundary, 원본 C의 같은-h 기준과 수렴 판정의 분리, 그리고 비용을 정한다. 실행 전에 할당과 reserve를 새로 기록한다.
2. 비용 개선이 필요하면 `native_stream_validation`(21.4 / 37.6 s)부터 본다. 판정식을 바꾸지 않고 행 처리를 vectorize하는 방식이 후보다. 동일 판정 결과의 bit 일치를 테스트로 고정해야 한다.
3. 선택 사항: PR105 receipt 최상위 `NATIVE_SMOKE_PASS` 표현의 정정(erratum).

과거 비용 ledger는 `CLOSED_HOLD_NOT_RESET`이다. cap을 올리지 않는다.
