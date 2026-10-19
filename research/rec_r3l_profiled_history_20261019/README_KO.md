# REC R3l: U6 단계별 비용과 무손실 history 저장

## 결과와 재개 위치

PR105 `3eb34b6a322d86d580b94f8f4bacfcadd33938ef` 이후의 구현 단위다. PR105에 게시된 실제 U5 pair16/pair128 및 3-step owned/C smoke 실행 receipt를 재사용한다. 이번 세션은 해당 적분을 반복하지 않았다. 새 결과는 비용 계측 실행기, 선택적 ZIP_STORED history 출력, 작은 U5 복구 capsule 추출기와 그 구현 검증이다.

현재 세션의 실제 Python/C++ probe는 각각 PYTHON_PASS/CPP_PASS다. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0에서 새 계약 테스트 42개가 통과했다. 실제 U4 checkpoint를 읽은 저장 실험은 3개의 교차 순서 쌍에서 5개 배열과 압축 해제된 NPY member가 모두 바이트 일치했다. 새 U5/U6 적분과 원본 C 과학 실행은 0회다.

실행 근거와 의미를 다음처럼 구분한다.

| 대상 | 근거 | 현재 사용 |
|---|---|---|
| 기존 R3k 37 tests, 실제 U4 세 상태 | PR104의 GitHub Actions 기록 | 유지된 source 근거 재사용 |
| 실제 U5 pair16/pair128 | PR105 `EXECUTION_001.json` | 게시된 실행 receipt 재사용; raw 독립 대조는 미완료 |
| 실제 U5 owned/C 3-step smoke | 같은 receipt의 `PASS_PENDING_REVIEW` | 1875 fields/939 links, 21.577521 process-tree CPU s라는 보고를 유지 |
| 새 계측·저장·복구 도구 | `LOCAL_TEST_EXECUTION.json`, `LOCAL_TESTS.log` | implementation-verified, 42 tests |
| 실제 U4 저장 형식 | `STORAGE_BENCHMARK.json` | numerically checked: 파일 내부 NPY 및 배열 바이트 일치 |
| 새 U5 profiled pilot, 실제 recovery capsule 추출 | 실제 입력 전송 의존성 | NOT_RUN |
| 전체 5210-step U6, production speedup | 부족한 실행·비용 근거 | NOT_RUN / NOT_MEASURED |

## 입력과 물리·수치 계약

- 원본 HyRec ZIP SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- 검토된 U5 checkpoint SHA256: `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`.
- 원본 U5 raw SHA256: `8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c`.
- 현재 간격은 `d ln(a)=4.245e-5`로 원본 격자의 h/2다. q=0, 기존 원자·열 연산자, H/T 두 단계 predictor tail, RT 시작 36446, U6 시작 53179와 경계 58389를 유지한다.
- V6 manifest SHA256 `f02f4e0b39dfafbb7656704cee59b8d95c976e9b55e840141d333be15b452585`와 그 109개 파일 해시를 현 세션에서 모두 대조했다. 원본 verifier, C harness와 owned integrator는 수정하지 않았다.
- 원래 U5 h 평균광자 `HOLD_9_FAIL`, h/2 `HOLD_8_FAIL`, 닫힌 과거 비용, REI activation=false를 유지한다.
- 기존 원본 C 같은-h 판정과 원래 평균광자/별도 roundoff-aware gate는 기존 verifier가 그대로 수행한다. full U6에서는 첫 EMLA 평가를 하지 않는다.

## 무손실 저장이 연산을 보존하는 이유

입력 배열 A의 dtype, shape, element bytes를 고정하고 그 NPY 표현을 N(A)라 하자. 두 NPZ 표현은 각각 DEFLATE(N(A))와 ZIP_STORED(N(A))다. 압축 해제한 member가 같으면 N(A)의 헤더와 데이터가 같고, `allow_pickle=False` 복원에서 dtype, shape, 각 element의 비트열이 같다. 원본 파일 전체 SHA와 새로운 파일 전체 SHA는 별도로 기록한다.

새 writer는 dtype cast, clip, finite-value 교정이나 원자·열 연산을 수행하지 않는다. object dtype는 파일을 만들기 전에 거절한다. 비교 실험은 dtype/shape/logical C-order bytes 외에 압축 해제된 NPY member 전체의 해시도 확인한다. 따라서 +0/-0, subnormal과 인접 binary64 값도 구별된다.

기존 verifier에서 history 저장은 owned integration이 반환된 뒤에 일어난다. NumPy proxy는 그 모듈의 `savez_compressed` 호출만 위임하며 다른 모듈의 NumPy 함수는 바꾸지 않는다. integration callback의 인수·반환 객체와 평가 순서를 유지하고 종료 시 binding을 복원한다. 완료된 실행에서 이 변경은 시간 적분 점화식의 입력이나 연산 순서를 바꾸지 않는다. 실제 전체 U6의 수치 정확도는 해당 실행의 같은-h 검증에 남아 있다.

## 실제 저장 측정

입력은 이미 완료된 U4의 SHA `7ad1476c78d08218e42ac616dc43d03dd8eb232c44bfb66a8f20a237dcce6943`인 NPZ다. photon 배열은 (311,2006), (311,2006), (3,2006)이고 states/steps 문자열 배열을 함께 저장했다. 1 CPU affinity에서 compressed/stored 순서를 교차하며 3회씩 측정했다. 두 모드 모두 flush/fsync한 동일한 실험이다.

| 형식 | 파일 bytes | 저장 CPU 중앙값 | 관측 범위 CPU s |
|---|---:|---:|---:|
| 압축 NPZ | 9,645,700 | 0.362180466 s | 0.354356634–0.387406379 |
| ZIP_STORED NPZ | 11,939,450 | 0.016110076 s | 0.010675172–0.018181954 |

차이는 이 파일의 저장 CPU 0.346070390 s와 크기 2,293,750 bytes(+23.7800%)다. 22.4816이라는 비는 이 저장 동작의 중앙값 비다. U6 전체 solver 성능비로 사용하지 않는다. 실제 profiled verifier의 compressed 모드는 원래 NumPy 호출의 durability 동작을 유지하고, stored 모드는 명시적 fsync를 더한다. 향후 두 `history_write` 측정에서 이 차이를 함께 읽어야 한다.

3쌍 저장 근거는 예외 처리 수정 전의 저장 구현에서 얻었다. 이후 변경은 계측/closeout 예외와 실행 위치 metadata에 한정되며 `write_stored_history`의 배열 직렬화는 유지됐다. 당시 파일 identity는 `SOURCE_AT_STORAGE_BENCHMARK.json`, 최종 구현 identity는 `SOURCE_SHA256.json`에 나뉘어 있다.

## 60 CPU초 판단에 필요한 비용 분해

PR105 owned integration 타이머 두 점을 조건부로 `T(N)=A+B N`에 맞추면

```
A = 0.18494928157142856 CPU s
B = 0.0011253352767857164 CPU s / step
T_hat(5210) = 6.0479460736250115 CPU s
```

이는 두 점의 기술적 외삽이다. 상한, 불확실성 구간이나 full 실행 허가를 제공하지 않는다. 별도 3-step smoke의 process-tree 비용 21.577521 s는 native 전처리, 검증·저장 비용을 포함한다. 이 한 점을 3으로 나누어 5210에 비례시키거나 Python 타이머에 그대로 더하면 비용 소유 범위가 맞지 않는다.

원본 검증의 기존 prefix는 P=16733 columns, 314P=5,254,162 values다. 새 구간에는 625N spectral values와 313N causal links가 추가된다. 전체 N=5210에서 추가 spectral values는 3,256,250개다. 포렌식 발생 수와 저장/검증 비용도 별도로 다루어야 한다.

새 phase ledger는 source closure, checkpoint load, source extraction, 두 C build, owned integration 및 nested callbacks, NPZ write, native run, native-stream audit를 측정한다. self CPU와 reap된 child CPU를 분리하고 직접 자식의 inclusive 시간을 빼서 exclusive 시간을 계산한다. inclusive 합을 전체 비용으로 쓰지 않는다. 남는 비용은 unattributed에 남긴다.

측정 구간은 profile summary의 시계 표본까지다. 이후 profile read/hash/write/fsync, 마지막 journal/console output, 전송·복구는 제외된다. 이 tail은 실제 복구 reserve에 남겨야 한다. 시계나 journal 오류가 있으면 accounting을 invalid로 표시한다. 계측/closeout의 이차 오류는 먼저 발생한 검증기 예외를 대체하지 않는다.

## 실행과 복구

`scripts/run_r3l_u6_profiled.py`는 기존 exact git HEAD/clean tracked tree 검사를 사용하고 두 새 adapter가 tracked 상태인지도 확인한다. capsule 디렉터리의 HEAD를 가장하지 않는다. CPU60s/wall180s/address2GiB/BLAS1의 기존 verifier 한도를 유지한다.

다음 새 과학 입력 실행은 `--mode pilot --pilot-steps 128 --history-container stored`다. 목적은 새 I/O 선택과 단계별 비용을 실제 U5에서 확인하는 것이다. 기존 pair16/pair128 캠페인을 재개 항목으로 재등록하지 않는다. full 모드는 원래 5210-step 호출을 제공하지만 유효한 할당, reserve와 실측 근거에 따른 실행자 판단이 먼저 필요하다.

현재 U5 raw 308,069,518 bytes의 Drive 다운로드는 268,435,456-byte 한도로 거절됐다. `extract_r3l_reviewed_u5.py`는 원본 raw 전체 hash, 안전한 member, 검토된 NPZ hash를 확인한 뒤 checkpoint와 manifest만 담은 <256 MiB 전달 ZIP을 만든다. 이번 실행 검증은 명시적 합성 archive에 대한 11 tests이며 실제 U5 추출은 NOT_RUN이다. NCP/owner는 이미 있는 원본을 우선 사용하고 그 작은 capsule을 게시·백업하여 다음 세션의 입력 의존성을 해소한다.

자세한 재개 명령과 반환 항목은 `HANDOFF_KO.md`, 상태와 근거는 `DAG.json`, `EVIDENCE.json`, 저장 확인은 `BACKUP_ACKS.json` 및 PR Conversation의 후속 아카이브 receipt를 읽는다.
