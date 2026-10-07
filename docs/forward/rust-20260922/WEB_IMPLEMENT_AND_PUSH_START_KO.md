# Web-side source implementation start

ROLE=BOUNDED_SOURCE_PORT_IMPLEMENTER
REPO=cosmosapjw-quantum/rec_bianchi
ORIGINAL_BASE=5a09f3797210284f83a1a1adb0e0092d1ac48475
KNOWN_CONTINUATION_HEAD=49d64b2660f227f6e4d888d6c02ead266d97a138
TARGET_BRANCH=forward/rust-he-sources-20260922
PR=81
SCOPE=SELECTED_HE_MATERIAL_FRAME_FIXED_INPUT_ONLY
COMPILE_HERE=NO
VERIFY_FULL_PARITY_HERE=NO
VERIFY_OWNER=LOCAL_CODEX
PUSH_MODE=UNVERIFIED_CANDIDATE_ONLY
MERGE_RELEASE_FORCE_PUSH=NO

사용자의 최초 START와 최신 역할 변경에 따라 IMPLEMENTATION_PLAN_KO.md를 실행한다. 이미 있는 rec_microphysics를 새로 만들지 말고 현재 source gap를 보완한다. 새 계획을 다시 생성하며 멈추지 않는다.

먼저 actual origin/branch/AGENTS/dirty state와 GitHub branch/PR를 읽는다. 사용자가 소유한 변경은 reset/stash/clean하지 않는다. 새 worktree를 생성하지 않는다. 현재 head가 KNOWN_CONTINUATION_HEAD보다 앞서면 scope 내 diff만 비교해 충돌 없는 변경을 이어간다.

원문은 docs/forward/rust-20260922/source_subset에 실제 byte로 보존한다. 부족하면 이미 mount된 A7 또는 기존 exact backup에서 회수한다. A7 SHA256=9ef3929dd1164c482cb200a7c1a10e57e1e0a78c6ab47c9cc8dfd8f5fc23ce6a, bytes=8541005. Drive ID=1fyG41Cl1SzjPpPZRU6r3zoShDDO1bwSn. Existing exact bytes가 있으면 재다운로드하지 않는다.

수정 우선순위:
1. Pair T12=V1^T V2를 복원한다. V1/V2 identity shortcut을 일반 입력으로 취급하지 않는다.
2. BB per-mode F,V와 shell/delta convention을 분리한다. Same WP를 유지한다.
3. BF common Maxwell/material energy, real/complex transpose, invalid/zero/missing, density measure를 명시한다.
4. Independent photon/atom/heat/material-force moment로 signed event ledger를 조립한다.
5. Independent full-matrix oracle, reference gross scaling, nonfinite 및 zero/transpose/factor mutant 검출을 추가한다.
6. 원 T4L01-T4L15를 mapping하고 material gate P와 consumer gate I를 구분한다.

여기서는 Rust compiler, cargo build/fmt/test/clippy, scientific full suite, whole-grid/trajectory를 실행하지 않는다. 필요한 tiny Python rational/matrix toy만 실행한다. Toy PASS를 compiler-red/green 또는 source implementation PASS로 쓰지 않는다.

변경 파일은 최초 START의 rust/rec_microphysics, tests/fixtures/rust_forward, scripts/check_rust_forward_parity.py, docs/forward/rust-20260922와 HANDOFF_PROMPT.md scoped entry로 한정한다. 기존 Python/C solver 및 PROJECT_STATE science 상태는 유지한다.

새 physical authority가 필요한 함수는 MissingAuthority를 반환하도록 격리하고 나머지 확정 함수를 계속 구현한다. D86 rescale, unknown->0, Bhatia/Jacobs splice, 새로운 low-band 데이터 발명은 금지한다.

완료 시 CANDIDATE_LOCK.json에 parent SHA, executable/input/source-lock content hash와 role=local_verification을 쓴다. Candidate 자신의 SHA는 self-reference하지 않는다. FORWARD_STATUS는 CODE_WRITTEN_UNCOMPILED__AWAITING_LOCAL_CODEX, tested_commit_sha=null, allow_consumer_integration=false로 둔다. 과거 logs와 PASS claims는 historical evidence로 보존한다.

정적 scope/JSON/syntax/diff/secret 점검 뒤 candidate commit을 만들고 같은 feature branch에 fast-forward 게시한다. PR #81은 미검증 후보임을 명시한다. CI 자동 실행 여부/관측 결과와 Rust gate를 분리한다. 수동 workflow_dispatch는 하지 않는다.

게시된 실제 full candidate SHA, executable/source manifest와 local handoff를 출력한다. GitHub R1 ref equality 확인 뒤 중복 readback을 멈춘다. Local git이 실패해 connector를 사용했다면 실제 동작을 connector publication이라고 보고하고 git push/ls-remote가 성공했다고 하지 않는다.

이후 local Codex 검증 전에는 tested/accepted/production-ready나 consumer integration 허용을 기록하지 않는다. Read/write/download/upload는 기존 source와 create-only backup 범위에서 수행한다. Dual backup은 두 provider의 실제 성공응답이 있어야 완료다. 다음은 LOCAL_CODEX_VERIFY_HANDOFF_KO.md이며 G10/E1C가 아니다.
