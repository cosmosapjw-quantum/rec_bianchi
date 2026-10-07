# Selected-He 원문–코드 대응표

코드 기준: `49d64b2660f227f6e4d888d6c02ead266d97a138`. 이 문서는 정적 대응표이며 구현 인증 또는 새 유도가 아니다. 원문의 byte/SHA와 적용 조건을 보존한다.

## M01 입력, matrix, screen, 밀도, 시계

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:19-34`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:13-25`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:458-550`

조치: Task2에서 finite/domain/PSD/screen guards 보완. Signed source 행렬에는 PSD를 강요하지 않음.
다음 담당: 계획 Task 2; T4: T4L03, T4L12, T4L15

## M02 공통 level energy registry

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:49-56`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:407-430`; `rust/rec_microphysics/src/he_singlet.rs:554-572`

조치: 독립 상수를 덧붙이지 않고 같은 energy cycle과 SI/eV 변환 위치 고정.
다음 담당: 계획 Task 2; T4: T4L02

## M03 BB 584/IR 같은 WP와 방향별 bath

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:74-106`; `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:109-111`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:35-63`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:575-634`

조치: 현재 단일 F broadcast. Pointwise kernel, per-mode F/V angular assembly와 sharp delta coefficient를 Task3에서 분리.
다음 담당: 계획 Task 3; T4: T4L03, T4L11

## M04 P BF inclusive transpose map

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:114-123`; `source_subset/sources/BASS_WU30_20260914_RESULT_v1.txt:88-105`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:756-812`

조치: T_E, F^T, W^T 순서를 그대로 유지. Photon source와 atomic source를 독립 성분 참조로 대조할 코드 작성은 Task4 이후.
다음 담당: 계획 Task 4; T4: T4L03, T4L10, T4L11

## M05 S BF와 net ionization 부호

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:126-132`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:90-98`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:814-844`

조치: Positive energy below threshold만 physical zero. j=-a_gamma E^2 trC, proper measure를 유지.
다음 담당: 계획 Task 4; T4: T4L02, T4L08, T4L12

## M06 Jacobs high P partial/S 표

원문: `source_subset/sources/BASS_WU30_20260914_RESULT_v1.txt:45-85`; `source_subset/reports/03_T4_COVERAGE_AND_MISSING_PHYSICS_KO.md:3-23`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:637-732`

조치: 이번 numeric admission은 high q=[1,1.4]. Raw T4 low-domain 서술을 삭제하지 않되 없는 partial rows를 만들지 않음.
다음 담당: 계획 Task 4; T4: T4L08, T4L12

## M07 D86 수치 band supersession

원문: `source_subset/sources/BASS_WU31_20260914_AMENDMENT_WU31_A1_v1.txt:21-29`; `source_subset/reports/03_T4_COVERAGE_AND_MISSING_PHYSICS_KO.md:25-36`

현재 코드: `rust/rec_microphysics/src/coverage.rs:47-91`

조치: 현 D86 원 node 유지. WU29 line143 legacy numerical choice만 A1로 대체. Endpoint/total rescale 금지.
다음 담당: 계획 Task 5; T4: T4L12, T4L13

## M08 두 photon 방향의 screen overlap

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:135-142`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:100-112`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:861-891`

조치: 현재 identity shortcut은 일반 T12=V1^T V2가 아님. Task5에서 V1/V2 입력으로 원문대로 구현. Material-frame 내부 문제로 consumer boost에 미루지 않음.
다음 담당: 계획 Task 5; T4: T4L03, T4L09, T4L13

## M09 Pair kernel/event/marginal/측도 분리

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:135-142`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:100-112`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:847-891`

조치: 1/2 atomic event, photon tag2, 1/(a_gamma E1^2 Delta), dy/dOmega를 각 소유 위치에서 한 번 적용. 현재 partial weights를 전체 marginal로 부르지 않음.
다음 담당: 계획 Task 5; T4: T4L02, T4L09, T4L13

## M10 He 사건 행렬과 핵수·전하

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:160-170`

현재 코드: `rust/rec_microphysics/src/ledger.rs:4-10`; `rust/rec_microphysics/src/ledger.rs:63-97`

조치: 기존 signed event matrix 보존. 새 quadrature assembly에서 integrated rates에 1/2나 2를 중복하지 않음.
다음 담당: 계획 Task 6; T4: T4L01, T4L13

## M11 독립 열·광자·내부에너지 및 material four-force

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:174-185`; `source_subset/reports/02_T4_CONSERVATION_EQUILIBRIUM_FRAME_AUDIT_KO.md:25-66`

현재 코드: `rust/rec_microphysics/src/ledger.rs:49-97`; `rust/rec_microphysics/tests/forward.rs:125-142`

조치: Task6에서 j_i,E,weights로 heat와 photon moment 독립 누적. Test의 constructed cancellation을 독립 물리검증으로 세지 않음. 총물질 force만, species partition은 scope 밖.
다음 담당: 계획 Task 6; T4: T4L02, T4L14

## M12 공통 Maxwell electron frame

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:30-34`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:228-238`

현재 코드: `rust/rec_microphysics/src/he_singlet.rs:451-468`; `rust/rec_microphysics/src/he_singlet.rs:540-550`

조치: 현재 inverse의 common material/electron restriction 유지. Drift 지원은 MissingAuthority, 추가 photon boost만으로 닫지 않음.
다음 담당: 계획 Task 4; T4: T4L15

## M13 독립 oracle, scale 및 nonfinite 비교

원문: `source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt:23-25`; `IMPLEMENTATION_PLAN_KO.md:1-30`

현재 코드: `scripts/check_rust_forward_parity.py:14-43`; `rust/rec_microphysics/tests/forward.rs:97-108`

조치: 현재 비교 바닥과 self-residual만으로 expression-level parity 인증하지 않음. 기존 4096eps 유지, reference scale 및 nonfinite negative controls는 Task6에서 구현.
다음 담당: 계획 Task 6; T4: T4L03, T4L10, T4L11, T4L12

## M14 원 T4 ID와 material/consumer 검증 범위

원문: `source_subset/plans/LOCAL_CODEX_T4_TEST_MATRIX.json:5-21`; `source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md:254-267`

현재 코드: 상태/검증 범위 문서

조치: 원 ID T4L01...T4L15를 그대로 유지. 전체 T4와 GateP를 구별; 이 단계의 원 T4 실행은 전부 NOT_RUN.
다음 담당: 계획 Task 7; T4: T4L01, T4L02, T4L03, T4L04, T4L05, T4L06, T4L07, T4L08, T4L09, T4L10, T4L11, T4L12, T4L13, T4L14, T4L15


## Task5 현재 구현 위치

위 M01-M14는 원래 baseline49d64b26의 정적 대응표로 보존한다. Task5 BF/ledger의 현재 line/hash 매핑은 `task5/API_SOURCE_MAP.json`에 있으며 Rust 실행 인증이 아니다.
