# REC R3m: 검토된 U5에서 profiled pilot128과 전체 5210-step U6 실행

## 결과

PR106(R3l) 문서 HEAD `d0e534b1f5b4bb20fe19875f6d502681b833470d` 위에서 새 과학 실행 두 건을 수행했다. 실행 코드는 R3l에서 테스트된 `98a21a7972afa8d01fe79b60b4d207a5f346ef5b`와 동일하다. 두 commit 사이 차이는 research 문서뿐이다. 구현은 바꾸지 않았다.

| 단계 | 결과 | 근거 |
|---|---|---|
| U5 checkpoint 복구 | `PASS_CHECKPOINT_CAPSULE_ONLY`, SHA `7aeec545…` | `receipts/U5_RECOVERY_RECEIPT.json` |
| 소유자 환경 테스트 | 42 tests OK | `receipts/LOCAL_TESTS_owner_001.log` |
| profiled pilot128 stored | `SMOKE_ONLY`, 같은-h `PASS_PENDING_REVIEW`, first_failure 없음 | `receipts/pilot128_stored/` |
| 원본 C 비용 진단 | N=128 2.91 s, N=5210 3.67 s CPU | `receipts/c_cost_diag_001/` |
| 전체 U6 허가 | `ADMIT_ONE_FULL_ATTEMPT` | `receipts/FULL_U6_ADMISSION_001.json` |
| 전체 U6 5210 stored | `PASS_PENDING_INDEPENDENT_REVIEW`, `RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION` | `receipts/full5210_stored/` |
| 독립 재계산 | `REVIEW_PASS` (같은-h parity 한정) | `INDEPENDENT_REVIEW.md`, `review/` |

결론: Python 소유 U6 적분이 같은 h=4.245e-5에서 U6 전 구간 5210 step 동안 원본 HyRec C와 원래 판정 기준 안에서 일치한다. 이것은 구현 충실도 검증이다. Python h/h2/h4 수렴성, 오차 한계, Bianchi/REI/CMB 예측은 이번 결과로 승인되지 않는다.

## 실행 위치와 환경

모든 실행은 owner workstation의 로컬 Claude Code 세션에서 수행했다. NCP나 sandbox가 아니며 native subagent 실행도 아니다. execution label은 `owner`다. SSH로 원격 호스트에 접속하지 않았다. 백업에만 기존 rclone 연결을 사용했다.

- Linux 7.0.0, Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0, gcc/g++ 13.3.0, rclone 1.60.1.
- 24 core, 시작 시 load average 약 6.5. 관련 없는 desktop 부하가 있었다. core별 사용률은 12–29%였다.
- 실행은 `taskset -c 4`로 core 4에 고정했다. verifier는 affinity[0]=4를 사용했다.
- 메모리 가용 16 GiB, 디스크 여유 17 GiB.

R3l sandbox(Python 3.12.14, NumPy 2.3.5)와 환경이 달라 42개 R3l 테스트를 이 환경에서 다시 실행했다. 모두 통과했다.

## 입력

- 원본 HyRec ZIP SHA `48cd5975…1d27`, V6 manifest SHA `f02f4e0b…2585`, 109개 source 파일 모두 일치.
- U5 raw `REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz`, 308,069,518 bytes, SHA `8d18bd22…3c3c`. owner에 이미 있던 사본을 사용했다.
- owner의 기존 checkpoint 사본 두 개도 같은 SHA였다. 실행에는 준비된 extractor 출력만 CP로 사용했다. coarse-grid나 C state로 대체하지 않았다.

## 할당

`R3M-OWNER-20261019-001`은 이번 세션의 사용자 지시에 근거한 owner 할당이다. ID 문자열 자체는 권한을 만들지 않는다. 과거 NCP 누적 예산은 `CLOSED_HOLD_NOT_RESET`으로 유지했고 재사용하거나 초기화하지 않았다. 실행별 한도는 기존과 같은 60 CPU s / 180 wall s / 2 GiB / BLAS1이다. 허가된 시도는 pilot 1회와, 조건을 만족할 때만 full 1회다. 디스크 reserve 4 GiB와 전송·복구 reserve를 별도로 기록했다.

## pilot128 결과

- 128 step, 80,000 spectral fields, 40,064 causal links, 원래 평균광자 gate 실패 0.
- maxima: virtual 1.77e-5, average 1.90e-4, lyman 7.95e-6, xe 1.32e-13, Tm 2.0e-16, H RHS 2.79e-14, T RHS 6.32e-13.
- process-tree CPU 17.377 s, wall 22.09 s. accounting VALID. 이차 profiling/closeout 오류는 없었다.

exclusive CPU 상위 phase(parent+child):

| phase | CPU s |
|---|---:|
| native_stream_validation | 12.546 |
| native_run (원본 C) | 2.548 |
| native_build + common_build | 1.113 |
| checkpoint_load | 0.476 |
| owned_integration (exclusive) | 0.286 |
| check_one_source (2회) | 0.163 |
| history_write (stored) | 0.081 (wall 2.13, fsync 포함) |
| unattributed | 0.068 |

측정 구간 진입 전 CPU는 0.694 s다. profile 기록/hash/fsync, journal 끝, tar, 업로드, readback은 측정에서 제외되며 cap 밖이다.

## 전체 실행 허가 근거

두 점 fit의 6.047946 s와 저장 비율 22.48은 상한으로 쓰지 않았다. 대신 phase별로 추정했다.

- 원본 C 비용은 pilot와 같은 binary로 N=5210을 독립 실행해 직접 측정했다. 3.67 CPU s였다. N=128 출력은 pilot의 C 출력과 바이트 일치했다.
- stream 검증의 prefix 행당 비용은 2.336 µs였다. 새 spectral 행 3,261,460개는 prefix 행과 같은 비용이면 36.3 s, 두 배면 43.9 s로 추정했다.
- 59 s를 넘으려면 spectral 행이 prefix 행보다 3.98배 비싸야 한다.
- 실측되지 않은 위험도 기록했다. 평균광자 gate 실패 시 forensic 비용(pilot 0회)과 부하 중 wall이다.

여기에 pilot 같은-h 통과, PR105 pair parity(이번 세션에 raw 재감사), 디스크·전송 reserve를 합쳐 1회 실행을 허가했다.

## 전체 5210-step U6 결과

- 종료 코드 0, verifier `PASS_PENDING_INDEPENDENT_REVIEW`, first_failure 없음.
- Python `RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION`, 5210 step, rt_stop_iz 58389. C END도 같은 상태이며 coupled 5212, steps 5210이다. 첫 EMLA 평가는 하지 않았다.
- 3,256,250 spectral fields, 1,630,730 causal links, 원래 평균광자 gate 실패 0.
- maxima: virtual 1.769e-5, average 1.016e-2, lyman 1.769e-5, xe 1.32e-13, Tm 4.4e-16, H RHS 2.79e-14, T RHS 6.32e-13.
- 공통 입력 표본 42회 PASS.
- process-tree CPU 37.57 s (cap 60), wall 42.0 s (cap 180), peak RSS 435 MB (verifier 프로세스만).
- accounting VALID, unattributed 0.18 s, 이차 오류 없음.

| phase | exclusive CPU s |
|---|---:|
| native_stream_validation | 21.409 |
| owned_integration | 5.837 (inclusive 10.597) |
| check_one_source (42회) | 3.662 |
| native_run | 3.461 |
| builds | 1.203 |
| checkpoint_load | 0.509 |
| causal_link_count | 0.438 |
| callbacks | 0.660 |
| history_write | 0.135 (wall 2.76) |

실측 37.59 s는 사전 추정 범위 36.3–43.9 s 안에 있다. spectral 행 비용은 prefix 행의 1.19배였다. full 실행의 C 출력 SHA `57ebca01…`는 독립 C 진단 출력과 같다.

## 독립 검토

1. PR105 raw 재감사: pair16/pair128 byte identity, smoke의 1875 fields/939 links/21.577521 s 등 receipt의 모든 수치가 owner의 raw와 정확히 일치했다. receipt 자체에는 raw 파일 hash가 없다. 최상위 `NATIVE_SMOKE_PASS` 표현은 raw의 `SMOKE_ONLY`/`PASS_PENDING_REVIEW`보다 강하다.
2. full U6 재계산: 별도 agent가 verifier 비교 함수를 쓰지 않고 numpy로 모든 V/A/L 행의 원래 gate를 다시 계산했다.
   - 세 maxima가 bit 단위로 같았고 ratio>1인 행은 0개였다.
   - state, RHS, iz 순서와 종료 상태도 맞았다.
   - pilot 앞 16,861 열은 바이트 일치했다.
   - partial bin과 NPZ 열도 일치했고, 모든 hash와 phase 합계가 맞았다.
   - 판정은 `REVIEW_PASS`(같은-h 한정)다. 평균광자 채널 ratio 1e-2는 rounding 민감도에 따른 method 특성으로 보이며, gate 대비 약 100배 여유가 있다.

## 보존 조건

h=4.245e-5, q=0, 원본 atomic/thermal operator, stage boundary(RT 36446, U6 시작 53179, 경계 58389), predictor memory와 원래 같은-h 기준을 바꾸지 않았다. U5 원본 h `HOLD_9_FAIL`과 h2 `HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, REI activation=false를 유지한다.

## 백업

`BACKUP_ACKS.json`에 정리했다. U5 checkpoint capsule, pilot raw, full raw를 각각 별도 폴더에 create-only로 올렸다. 각 항목은 Drive와 Dropbox의 rclone 종료 상태, metadata 크기, 생산자 SHA, 전체 원격 readback SHA를 구분해 기록했다. 세 항목 모두 두 provider에서 readback이 일치했다. 코드·증거 최종 ZIP은 docs commit 뒤 PR Conversation receipt에 기록한다.
