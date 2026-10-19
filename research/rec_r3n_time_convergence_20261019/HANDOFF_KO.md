# R3N 인계: 준비된 비교 코드와 남은 생산 입력

## 바로 쓸 코드

게시: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/108

전용 CI가 실제 실행한 코드 SHA는 `0e828e8ef7aa418a86b76f59c462457a66bbf4ee`다.
run `39235616621`에서 45 tests와 6 analytic controls가 통과했다. 수치 코드가 같은
문서/증거 commit `3c8baceb204448e751565a7b4cf437e6c385f5da`의 공통 push/PR CI는
각각 787 PASS, 4 SKIP, 14 subtests PASS다. 실행 장소는 GitHub Actions다.
샌드박스에서도 45 tests를 실행했다. 위 수는 서로 중복되며 새 물리 실험 수가 아니다.

작업 branch는 `research/rec-r3n-convergence-diagnostics-20261019`이며, 최종 HEAD와 CI는
PR Conversation 최종 receipt가 기준이다. 시작 전에 백업의 더 새로운 결과와 GitHub를
대조한다. PR107의 full U6 5210-step 같은-h 실행은 완료 노드로 재사용한다.

이번 단위의 비교기·원본 C 보간 시험·작은 ODE 제어 실행·실제 R3M 상태 adapter는 구현했다.
사용자가 파일을 준비할 필요 없이 저장소에 포함된 작은 trace로 바로 검사할 수 있다.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=src:scripts
python -m unittest discover -s tests/trajectory -p 'test_r3n_*.py' -v
python scripts/compare_r3n_time_grids.py analyze \
  --history research/rec_r3n_time_convergence_20261019/real_h2_trace_003/h2_state_trace.json \
  --evidence-dir /tmp/rec-r3n-analysis-new
```

같은 환경·코드로 이미 검증되었으면 위 검사를 반복할 필요는 없다. 새 실행자는 환경 차이의
경량 compatibility 확인에 사용할 수 있다. gcc는 unit test에서 원본 `hyrectools.c`만
컴파일한다. HyRec 시간 적분을 시작하지 않는다. 출력은 반드시 존재하지 않는 경로를 쓴다.
정상 h2 단독 분석의 JSON status는 `INSUFFICIENT_LEVELS`다. 이는 예상된 진단이며 PASS인
전체 수렴 실행을 뜻하지 않는다. `--require-complete`이면 이 상태의 exit code는 3이다.

## 실제 원자료에서 다시 추출할 필요가 생길 때

R3M full raw는 232,521,236바이트이며 SHA256은
`8cd5da29521b47d6b715dfa6889ae11d239ef430460deae97824ee32584b80b9`다.
Drive file ID `173QaPYquHnrWeS_Rxrb1rRPSk0VrGMmx`, Dropbox file ID
`id:BSpOijBcT10AAAAAAD_QGw`다. 최종 receipt의 경로를 사용해 실행자가 기존 연결로 직접
복구한다. 사용자에게 수동 다운로드나 SSH/SCP를 요청하지 않는다.

```bash
python scripts/compare_r3n_time_grids.py prepare-r3m \
  --raw-dir /absolute/recovered/evidence_full_001/full5210_stored \
  --evidence-dir /absolute/new/r3n-state-trace
```

adapter는 NPZ, verification JSON, native stdout의 알려진 SHA를 모두 검사하며,
입력 변경도 검사한다. 원본 C stdout은 299,795,855바이트,
SHA `57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38`다.
이번 샌드박스에서는 최초 추출 사본이 잘려 거절되었고, tar 내부 member를 별도 파일에
스트림 복원해 정상 hash를 회복했다. 같은 증상이면 gate를 완화하지 않고 추출 사본을
검사한다. 원래 아카이브와 실패 로그는 보존한다.

## 미래 세 격자의 파일 계약

각 그리드 descriptor schema는 `rec.r3n.history.v1`이다. `level=0,1,2`는 각각
`8.49e-5`, `4.245e-5`, `2.1225e-5`다. origin은 `-log(8001)`이다.
descriptor와 같은 디렉터리에 NPZ를 두고 전체 SHA256으로 결합한다.

NPZ 필드:

- `global_iz`: 실제 source-grid 전역 정수 인덱스, 연속 순서.
- `redshift`, `xe`, `Tm_K`: 같은 인덱스의 실제 Python 상태, xe는 n_e/n_H, Tm은 K.
- `regime`: 비어 있지 않은 실제 stage label. 단지 file chunk 이름으로 대신하지 않는다.
- `parity_abs_xe`, `parity_abs_Tm_K`: 그 격자에서의 실제 같은-h C/Python 절대 차이.
- `quantization_abs_xe`, `quantization_abs_Tm_K`: 추가 출력 반올림 half-unit. binary64 NPZ
  직접 저장에는 추가 decimal quantization=0이 가능하다. 근거가 없으면 필드를 생략한다.

provenance는 source commit, 원본 ZIP, 동일 cosmology/atomic/thermal/stage/predictor
physics contract의 digest, q=0, REI=false, `checkpoint_resampled=false`를 담는다.
boundary 목록과 별도로 `boundary_coverage_lna=[lo,hi]`에 경계 목록이 검토된 범위를
기록한다. 비교점 ±4hcoarse의 halo를 덮지 못하면 p는 `BOUNDARY_COVERAGE_UNKNOWN`이다.
known-empty와 unknown을 혼동하지 않는다. 각 grid는 자체의 독립 Python 시작 이력과
검토된 accepted checkpoint를 가져야 한다. photon prefix와 두 RHS tail도 그 생산자의
원자료/receipt로 추적되어야 한다. 이 상태 비교기만으로 그 생산 경로를 인증하지 않는다.

```bash
python scripts/compare_r3n_time_grids.py analyze \
  --history /absolute/h/history.json \
  --history /absolute/h2/history.json \
  --history /absolute/h4/history.json \
  --evidence-dir /absolute/new/three-grid-diagnostic --require-complete
```

원래 four-point cubic, z8000…0 전 구간 및 지정 창·report point를 유지한다.
부분 구간의 유효한 수치 결과는 남기되 빠진 stencil/구간을 승인으로 채우지 않는다.
NumPy/SciPy 환경, 실제 명령, 종료 코드, CPU/wall/RSS, descriptor/NPZ hash와 결과를
반환한다. 결과·실행 기록 파일은 실행자가 바뀌어도 동일한 의미를 가진다.

## 다음 최소 과학 작업

이번 단위에서 h4 생산 적분기나 h2 낮은 z 후속 단계까지 새로 구현·실행했다고 주장하지
않는다. 이들은 기존 DAG의 별도 생산 의무다. 다음 단위는 기존 원본 h 노드를 identity로
연결하고, 독립 h4 시작과 h2의 U6 이후 경로 중 가장 이른 미충족 입력을 구체화해야 한다.
기존 full U6/pilot/pair parity를 다시 실행하는 단계로 돌아가지 않는다.

실제 생산 실행에는 그 실행의 유효한 할당, 측정에 근거한 비용, 복구·전송 reserve가
필요하다. 과거 `CLOSED_HOLD_NOT_RESET` 비용을 초기화하거나 이미 끝난 owner 할당을
새 NCP 예산으로 재사용하지 않는다. 이번 R3N에는 NCP 생산 실행을 새로 제출하지 않았다.

보존 조건: 원본 ZIP/U5 identity, h2=4.245e-5, 원본 operators·stage·predictor·same-h
기준, U5 h `HOLD_9_FAIL`/h2 `HOLD_8_FAIL`, REI=false. 이 단위의 형식적 2차/반례/구현
검증으로 Bianchi/REI/CMB 예측, 전체 Python 수렴이나 production speedup을 승인하지 않는다.
