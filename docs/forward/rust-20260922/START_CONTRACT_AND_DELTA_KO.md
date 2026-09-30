# rec_bianchi selected-He forward-port 계약과 실행 방식 변경

기준일: 2026-09-23. Branch 이름과 원자 source의 20260922 표기는 그대로 유지한다.

## 권위

최초 사용자 START의 목표는 selected-He 확정 식을 실제 호출 가능한 pure Rust rlib `rec_microphysics`로 옮기는 것이다. 전체 재결합 solver, G10, Ly-alpha E1C split-domain을 완성하는 작업이 아니다.

원 요청의 repository는 `cosmosapjw-quantum/rec_bianchi`, 원 base `5a09f3797210284f83a1a1adb0e0092d1ac48475`, branch `forward/rust-he-sources-20260922`이다. 이번 read-only 조사에서 PR #81은 open/unmerged, head `49d64b2660f227f6e4d888d6c02ead266d97a138`로 조회됐다. 재실행 시 이 head에서 이어가며, 이미 존재하는 library를 다시 생성하지 않는다. Remote head가 바뀌면 차이만 조사한다.

원자 권위는 A7 안 A6 subset의 WU29 RESULT, WU30 RESULT, WU31-A1 amendment와 T4 interface/coverage/ledger/test matrix이다. WU29에 남은 옛 CHIANTI 두 광자 수치는 WU31-A1의 명시적 supersession에 따라 D86로 대체한다. 그 외의 WU29 tensor/measure/conjugation 규약은 유지한다.

A7: `BASS_ATOMIC_A7_T5_THEORY_READY_FINAL_20260922T1704KST.zip`
SHA256 `9ef3929dd1164c482cb200a7c1a10e57e1e0a78c6ab47c9cc8dfd8f5fc23ce6a`, 8541005 bytes.
Drive ID `1fyG41Cl1SzjPpPZRU6r3zoShDDO1bwSn`.
A6 SHA256 `d8a5f4afe2ab619407f55e9ac9f5b0c9e5196689301b78c1cc98138e9c18a628`.

## 최신 사용자 지시 원문

> 이제 맨 처음 프롬프트에 따라 코드 이식/변경을 하고 push하는 계획안을 작성해줘. 여기서 컴파일할 필요 없어. 필요하면 toy로 검증한 후 바로 이식하고 검증은 local codex에 인계홰줘.

이번 산출물은 계획안, 구체적 보완 항목, 재현 가능한 작은 반례, 실행/반환 handoff이다. 이번 계획 작성 중 repository 파일 변경, commit, push, PR 수정은 하지 않았다.

후속 실행의 역할은 다음으로 고정한다.

- 이 스레드: 확정 원문 복원, 필요한 작은 대수/스칼라 toy, scoped Rust/Python/test 코드 작성, 정적 diff 점검, 미검증 feature-branch 게시, local Codex dispatch.
- Local Codex: exact candidate 복원, 실제 compiler/toolchain probe, 빌드/단위시험/독립 parity, 제한된 기존 회귀, 필요한 최소 구현수정, raw evidence와 tested SHA 반환.
- Local Codex가 이론을 새로 만들거나 G10/E1C/전체 history 실행으로 이동하지 않는다.

최초 START의 '세 시험을 통과한 뒤 push'는 최신 지시에 따라 두 단계로 나눈다. 첫 push는 **unverified candidate publication**만 허용한다. 실제 시험 뒤에만 **verified delivery**가 된다. 최종 acceptance의 세 명령은 삭제하거나 완화하지 않는다. '컴파일을 여기서 안 한다'를 '컴파일할 수 없다'로 기록하지 않는다.

## 고정 물리/구현 경계

- Metric (-,+,+,+), c, h, hbar, k_B 명시, proper densities, material-frame photon occupation.
- W_P: 3x3 Hermitian PSD orbital density, tr W_P=n_P. F: 2x2 Hermitian PSD occupation, tr I2=2.
- 584와 IR은 동일한 W_P를 사용하며 채널 에너지/A/lower population만 다르다.
- BB sharp-line shell coefficient와 spectral delta-distribution을 분리한다. 실제 line profile나 임의 폭을 만들지 않는다.
- BF: 같은 source-family/table handle을 정·역에 사용. common material/electron frame, isotropic nondegenerate Maxwell electron만 허용한다.
- D86: half-grid 20개 j/40 원수치, y->1-y, band 내 linear interpolation. Full-total rescale과 추가 독립 total loss 금지.
- Jacobs high: P s/d partial 및 별도 S family, q=1,1.2,1.4. Bhatia와 splice 금지.
- Positive subthreshold energy의 physical zero와 above-threshold 미제공 영역을 구분한다. NaN, infinity, negative energy는 physical zero가 아니다.
- Atomic pair factor 1/2, 두 photon tag, quadrature weights는 각 지정 위치에서 한 번만 적용한다.
- 기존 Python/C solver 수식과 state/PROJECT_STATE.json은 수정하지 않는다.
- 새 runtime dependency를 Python package default에 추가하지 않는다. 기존 Rust external dependency 0개를 유지한다.
- 기존 작업공간/AGENTS/dirty state 확인, 사용자 변경 reset/stash/clean 금지, worktree 자동 생성 금지.
- Feature branch push만 수행. Default merge/release/force push/auto-merge/workflow_dispatch 금지.
- S3 accepted / S4 partial / S5 gated / G10 open / G11-G13 gated / D86 canonical / P0 physical OPEN / HOST4 physical HOLD / HH propagation unauthorized 유지.

## 소유권 및 근거 상태

`SOURCE_RESTORED`, `TOY_CHECKED`, `CODE_WRITTEN_UNCOMPILED`, `CODE_PUSHED_UNVERIFIED`, `LOCAL_VERIFIED`, `DELIVERY_PUBLISHED`를 구분한다. 하나의 PASS flag로 합치지 않는다.

과거 PR 설명과 repository의 PASS 로그는 보존한다. 이번 계획은 그것을 현 구현의 전체 권위 충족이나 새 실행으로 재사용하지 않는다. 새 known-gap record와 pending-local 상태가 현재 branch의 인증 범위를 정의한다. 기존 science ledger는 건드리지 않는다.
