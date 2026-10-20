# R3R 후속 연구 — 단계 1: 최신 반환 복구와 후보 선택

## 실제로 새로 반환된 결과

2026-10-20 원격 조회에서 PR110의 마지막 HEAD는 `888d56d72579d1e1fd30f66abe02d9f91809a767`로 유지되었으나, 후속 draft [PR111](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/111)에 새 NCP 반환이 있었다. 이 연구의 base는 `5b44bb21ce0599e55e0848e5e3ff320c9e8ca172`, tree는 `9403d3778d0a81e9632cea58e42e59ed9581e980`이다. NCP 실행 source `1ad0380110621446c42df9d995fd85db3a6c7e7a`, 결과 게시 `2236c19ff71b2706696e1985d968b2b841fd55bc`, 보존 메타데이터 HEAD 5b44를 구별한다.

Google Drive와 Dropbox의 `REC_R3Q_NCP_REVIEWED_RESULTS_20261020.tar.gz`를 각각 전체 다운로드하여 SHA256 `5219995db41dfebf8d0ceafa445402f9125e01321241a34a54fd9f4592c513e2`가 일치함을 확인했다. 실제 NPZ와 명령·검증·감독 receipt를 읽었다. 생략된 native CSV, stdout/stderr 및 일부 partial 파일은 기존 해시와 독립 검토를 재사용했으며, 새 전체 raw 재감사로 세지 않는다.

- h4: 새 accepted 1,511 / FULL 평가 6,044, He cutoff 74,409 및 H_ONLY 두 단계 뒤 74,411. 기존 검토 `PASS_SCOPED_H4_FIRST_EVENT_PLUS_TWO`; 감독 CPU 31.315760764 s, wall 31.46869331 s, exit 0.
- h2: 새 accepted 153,327, 저장 상태 153,328개. 기존 reviewed same-h PASS 및 `STOP_AT_SOURCE_Z0_CUBIC_STENCIL`. 기존 실행 CPU 60.755865 s, wall 62.63294565 s는 당시 600/900 allocation의 결과다. 이번 60/180 한도의 새 실행으로 세지 않는다.
- h2 z=0 원문 C 보간은 마지막 네 실제 상태 211713–211716을 사용한다. “네 개 필요, 세 개만 있음”이라는 기존 후속 문서 해석은 소스와 맞지 않는다. receipt 원문은 보존하고 `receipts/intake/endpoint_correction.md`에 독립 유도와 교정 해석을 추가했다. 추가 음의 z RHS step은 요구되지 않는다. 이것은 전역 수렴성 통과를 뜻하지 않는다.
- Library의 R3P 보존 폴더 및 최신 목록에서는 새 REC 반환을 찾지 못했다. 이전 대화 조회는 실제 SERVICE_ERROR였다. 이 조회 범위 밖의 부재를 주장하지 않는다.

## 계약

원래 HyRec2012 atomic/thermal operator, predictor recurrence, causal/stage boundary 및 same-h tolerance를 유지한다. REI는 false, 원래 U5 h/h2 실패는 HOLD_9_FAIL / HOLD_8_FAIL, 역사 비용 장부는 CLOSED_HOLD_NOT_RESET이다. 전역 h/h2/h4 convergence와 production speedup은 승인되지 않았다.

이번 실행의 상한은 60 CPU seconds, 180 wall seconds, process당 2 GiB, 새 pilot 최대 accepted 128이다. 이전 NCP event/full allocation은 재사용하지 않는다. R3P의 R1–R10/C1–C10, 저장 full5210 감사, smoke16 및 CI를 complete_reused로 연결한다.

## 최대 세 후보와 실제 선택

| 후보 | 현재 근거 | 이번 판정 |
|---|---|---|
| A: 선택된 common-input 이벤트만 owned snapshot 생성 | 이론적 누적 복사량 절감 가능. 현재 32-step profile observer 0.006126 s | 보류. 현재 측정된 지배 비용으로 입증되지 않음 |
| B: 실제 spectral stream 감사에 exact bounded NumPy ratio 연결 | profile comparator 0.252768 s, 그중 exclusive 0.146398 s. 기존 R3P lane 식/연산 순서를 재사용 가능 | **선정**. 파싱·할당 포함 end-to-end 감사 시간과 binary64/진단 동등성 검증 |
| C: 다음 NCP h4 단계 또는 플랫폼 pilot | h4 event+2 반환 이미 있음. 현재 스레드 Python/C++ 실제 실행 가능 | 이번 노드에서 선택하지 않음 |

cProfile의 기본 경과시간 timer를 사용했다. 위 수치를 exclusive process CPU나 비프로파일 benchmark로 해석하지 않는다. integrator 누적 경과시간은 0.290664 s였다. 새 acceleration claim은 아직 없다.

## 이번 단계의 새 경량 실행과 실패 보존

`REC_R3R_DIAGNOSTIC_PROFILE32_20261020_001` allocation에서 첫 시도는 inherited RLIMIT_CPU hard limit보다 높은 값을 요청하여 accepted 0 상태에서 실패했다. cProfile CLI가 SystemExit를 삼켜 outer exit 0을 만들었지만 worker FAIL을 그대로 보존한다. failed/execution.json의 new_accepted_steps=32는 요청값이며 실제 accepted 값이 아니다.

동일 allocation에서 새 profile shim이 soft/hard 각각을 inherited limit 이하로 clamp하고 SystemExit를 전파하도록 하였다. 고정 solver/worker source는 변경하지 않았다. 두 시도 누적 CPU는 4.739403 s로 60 s 내이며, 복구된 실제 32 accepted / 128 FULL 평가는 same-h PASS, common-input 9 sampled evaluations PASS, status SMOKE_ONLY다. 새 전역 물리 주장은 없다. 실제 raw는 단계 백업에 보존한다.

현재 Python 3.12.14는 실제 실행 PASS, g++는 실제 compile+run PASS, rustc는 실제 호출에서 COMPILER_MISSING이다. 이번 NumPy 후보는 Rust가 필요하지 않다.

## 다음 단계

별도 opt-in comparator를 작성하고 고정 source closure 100개를 유지한다. bounded buffer, 원래 scalar expm1, 개별 binary64 곱셈·덧셈·나눗셈, per-tag 순서 및 최초 실패를 보존한다. 전체 저장 stream의 differential benchmark, 예외·guard 경계 반례, source-bound 제한 pilot, 독립 PHYS-MATH/CODE 검토와 plot 직접 검토 후 실제 근거 범위에서만 최종 판정한다.

