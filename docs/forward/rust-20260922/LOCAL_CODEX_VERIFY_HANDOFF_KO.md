# selected-He source: local transport and verification handoff

현재 Git branch의 Task8 dispatch commit은 **문서·인계만** 게시한다. Task1–7의 새 source 전체가 Git에 반영됐다고 해석하지 않는다. 실제 source candidate/tested SHA는 아직 없다.

먼저 `task8/TRANSPORT_DISPATCH.json`의 source package 이름·SHA-256·provider ID와 source-content manifest digest를 읽는다. 기존 Dropbox 동기화 디렉터리나 이미 받은 동일 파일을 우선 사용한다. 없으면 승인된 provider로 취득한다. 동일 파일을 불필요하게 다시 다운로드하지 않는다.

1. 기존 `rec_bianchi`의 origin/branch/AGENTS/dirty state를 읽고 현재 remote ref를 확인한다. 새 worktree, reset, stash, clean, force-push, merge, release는 하지 않는다.
2. package SHA-256, ZIP CRC와 `PACKAGE_MANIFEST.sha256`의 모든 항목을 검사한다. package의 `candidate/`가 Task1–7 누적 코드·시험·원문과 Task8 메타데이터다.
3. dispatch의 code base `49d64b2660f227f6e4d888d6c02ead266d97a138` 이후 변경을 확인한다. 현재 branch가 dispatch보다 앞서면 다른 변경을 덮지 말고 좁은 path별 diff로 판단한다.
4. `candidate/`를 적용하기 **전에** 대상 path의 staged/unstaged/untracked·symlink 충돌을 검사한다. 무관한 변경은 보존하고 겹치는 파일만 보류한다. `.git`, runtime cache, 사용자 설정은 복사하지 않는다.
5. 적용한 `task8/SOURCE_CONTENT_MANIFEST.sha256`을 repo root에서 검사한다. 원 T4 정적 대응 검사를 실행한다. package가 아닌 실제 Git tree를 source candidate C1로 commit하고 SHA를 기록한다. 이 시점 이전의 dispatch SHA를 C1로 쓰지 않는다.
6. 동일 C1에서 아래 세 명령을 실제 실행한다. 각 command/cwd/start/end/exit/stdout/stderr를 원문으로 보존한다.

```bash
rustc -Vv
cargo -V
python --version
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
```

`rec_microphysics`만 대상이며 `bianchi_rustcore`, vendor 전체, scientific full-suite, eigensolve, trajectory, whole-grid를 실행하지 않는다. Cargo.lock을 재생성하거나 cargo update하지 않는다. 네트워크 차단을 위해 CARGO_NET_OFFLINE=true를 사용할 수 있으며 실제 환경을 로그에 남긴다.

75개 작성된 Rust 시험과 251개 고정 입력/3,027개 참조 성분은 **예상 계약**이다. 실제 실행 개수·결과를 읽고 원 T4 Gate P 11개 의무 및 audit rows를 판정한다. 작성된 함수/시험 이름, Python self-test, 과거 Python CI는 Rust parity 증거가 아니다.

실패는 compile/type, format, numerical, physics/formalism, dependency, runtime/service로 구분한다. 최소 수리는 가능하지만 source table/4096eps 허용치/transpose·conjugation/측도/비제공 구간을 바꾸어 green을 만들지 않는다. 코드 변경 후 실제 시험한 SHA를 새로 고정한다. 새 물리가 필요한 함수만 MissingAuthority/HOLD로 남긴다.

세 필수 gates와 Gate P가 실제로 닫힌 뒤만 LOCAL_VERIFIED_SELECTED_HE_MATERIAL_SOURCE를 사용한다. Gate I의 normal/material adapters, G10/E1C/S4/S5 및 기존 physical HOLD는 승격하지 않는다.

증거-only C2에 원로그·실패 이력·source/acceptance digest·review·반환을 보존한다. C1/tested source SHA와 C2/delivery SHA를 구분한다. 변경 파일만 commit하고 기존 feature branch에 fast-forward push한다. `git ls-remote origin refs/heads/forward/rust-he-sources-20260922`와 delivery SHA 일치에서 R1 검증을 종료한다. create-only Drive/Dropbox 백업은 실제 provider 성공 응답이 있는 것만 완료로 보고한다.

반환: repository, original base, dispatch, source candidate, tested, delivery SHA; changed paths; 각 명령 exit와 원로그; Gate P/I; domain/MissingAuthority/HOLD; remote ref; provider별 ID/size/checksum와 upload/restore 구분. 다음은 별도 exact-rev consumer integration 또는 이 port 종료뿐이다.
