# R3P 단계 1 — 정확 산술을 보존하는 감사 가속

PR110의 Stage0에서 최신 GitHub 및 관련 REC 백업을 먼저 대조했다. 완료된 R3M 전체 h2 U6 5210-step 적분과 R3O의 실제 검증을 재사용한다.

새 구현은 Python의 열별 온도·동일 단계 V/A Planck 캐시, 불변 인과 geometry, Rust/Rayon의 독립 prefix 열 검증이다. 원래 시간 적분, atomic/thermal 연산자 및 단계 경계는 유지한다. 새 `rec-stream-audit` crate, 고정 Cargo.lock, 라이선스와 오프라인 vendor를 포함했다. rustc 1.94.1로 실제 오프라인 빌드와 Rust 18개 테스트 및 C ABI 검사가 통과했다.

저장된 R3M 전체 raw를 새로 원격 복구하고 원래 SHA와 대조했다. 세 pilot 감사는 8,510,412개 prefix/spectral field와 모든 control 행에서 verdict·native history·diagnostic 해시가 같았다. 기존 21.4372, Python 캐시 19.9689, Rust 1-thread 9.78686 CPU초는 단회 pilot이다. 반복 비용 측정과 독립 코드 검토, 새 source-bound 16-step smoke는 진행 중이다. 신규 전체 물리 적분은 0회다.

입력 계약 강화: Python prefix의 NaN/Inf를 명시적으로 거절한다. Rust는 원래 생성기의 네 필드 ASCII 문법만 받는다. 잘못된 문법의 우연한 예외 문자열까지 원래 parser와 같다고 주장하지 않는다. 정상 검토 입력의 전체 비트/판정을 대조한다.

후속 순서: 코드 독립 검토 → 동일 입력 3-round legacy/cached/Rust 1·2·4 비교 → exact-source U5 16-step 원본 C 같은-h smoke → 현재 코드 CI → 최종 백업/게시/DAG.

원본 source ZIP, U5 checkpoint identity, h=4.245e-5, U5 h HOLD_9_FAIL / h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI=false를 유지한다. 새 production speedup, 전역 h/h2/h4 수렴, Bianchi/REI/CMB 예측은 승인하지 않았다. 상세 상태는 EVIDENCE.json, DAG.json, BACKUP_ACKS.json과 receipts를 따른다.
