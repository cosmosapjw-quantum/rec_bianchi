# 원 이론방 반환

F1 출력 overflow를 typed error로 차단했고 새 source를 전체 고정 입력 시험과 fresh read-only 독립 리뷰로 재검증했다. 새로운 물리나 consumer 통합은 수행하지 않았다.

```text
REC_REVIEW_STATUS=PASS_SCOPED_F1_REPAIR
REVIEWED_SOURCE_SHA=d3cc6e0120061f113d28e7a3a55a2e3dd561e81e
DEPENDENCY_CANDIDATE_SHA=d3cc6e0120061f113d28e7a3a55a2e3dd561e81e
REVIEW_DELIVERY_SHA=RESOLVE_GIT_COMMIT_CONTAINING_THIS_RETURN
REMOTE_BRANCH_TIP=VERIFY_WITH_GIT_LS_REMOTE_AFTER_PUSH
FMT=PASS_EXIT_0
CARGO_TEST=PASS_76_OF_76_EXIT_0
PARITY_RERUN=PASS_251_CASES_3027_COMPONENTS_111_EXPECTED_ERRORS_EXIT_0
GATE_P_SCOPED_REVIEW=PASS_FIXED_INPUT_IMPLEMENTATION_REVIEW_ONLY
SCIENTIFIC_GATES_UNCHANGED=YES
FIRST_BLOCKER_IF_ANY=NONE_IN_SCOPED_REPAIR
NEXT_ACTION=CLOSE_PORT_OR_SEPARATELY_AUTHORIZED_OTHER_REPO_EXACT_REV_INTEGRATION
```

Repository: `cosmosapjw-quantum/rec_bianchi`; branch: `forward/rust-he-sources-20260922`; base: `5a09f3797210284f83a1a1adb0e0092d1ac48475`; source import: `0ef9968c1dcfa17ba63072965902c86d3b59d9ad`. 이전 tested source `2ee3760870f9ac47eaab518a4c4a907f1a3f6f85`는 F1 때문에 dependency 후보에서 교체되었다.

수정 경로: `rust/rec_microphysics/src/ledger.rs`, `tests/forward.rs`(동일 crate), 기계적으로 갱신된 `task7/T4_COVERAGE_MAP.json` 및 `task8/SOURCE_CONTENT_MANIFEST.sha256`; 새 증거는 `f1_repair/`, 다음 실행점은 `START_HANDOFF_KO.md`와 `FORWARD_STATUS.json`이다. 원로그와 command/exit는 `RERUN_RECEIPT.json`; source domain 검토는 `SOURCE_SCOPE_AUDIT.json`; 실제 리뷰는 `native/review.txt`와 binding이다.

Git push는 `.github/workflows/verify.yml`의 push trigger 대상이다. 로컬에서 실행한 범위는 위 세 시험이며 CI 결과를 로컬 PASS로 대체하거나 CI 0회라고 주장하지 않는다. full T4, Gate I, S4/S5/G10/E1C/history/observable/production은 SKIPPED/기존 상태 유지. P0 OPEN, HOST4 HOLD, HH unauthorized 유지. 백업은 create-only provider 성공응답과 R1 metadata 기준이며 restore는 수행하지 않았다.
