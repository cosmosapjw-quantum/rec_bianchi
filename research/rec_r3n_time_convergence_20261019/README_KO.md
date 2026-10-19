# REC R3N: 저장 이력의 시간 격자 비교와 predictor 검증

PR107 `328f3723948979f74ae6c19474f45cb1882fb7b9`에서 이어진다.
새 연구 전에 R3M 코드 ZIP과 full 원자료를 Drive에서 전체 회수해 각각의 producer SHA와
대조했다. PR107의 5210-step owner 실행과 same-h 독립 검토를 재사용한다.

## 새 결과

- 기존 `R3I-CONVERGENCE-v1`의 원본 4점 보간, 부호 차이, 오차 바닥, scale 및
  sensitivity/contraction 기준을 실행 가능한 비교기로 구현했다.
- 원본 predictor의 국소 결함과 스칼라 안정 구간을 유도하고 독립 검토했다.
- 해석해가 있는 작은 ODE에서 원래 memory는 약 2.01차, 잘못된 이전 한 단계 memory는
  약 0.99차다. 세 격자의 공통 1% 초기 편향은 약 2차 차이에서도 남는다.
- 원본 C `rec_interp1d`를 새로 컴파일해 세 출력 격자의 18개 값에서 비트 일치를 확인했다.
  이것은 h4 HyRec 적분 실행이 아니다.
- 검토된 full U6로부터 5211개 xe/Tm 상태와 실제 same-h 절대 차이를 담은 117KB 정도의
  상태 trace를 만들었다. 실제 h2 trace 하나를 비교기에 넣으면 `INSUFFICIENT_LEVELS`다.
- 새 경량 테스트 45개 PASS. 독립 C9 검토의 경계 provenance·좌표 상쇄·동시 출력 문제 세 건을 모두 수정하고 closure를 받았다. CI와 최종 코드 identity는 `EVIDENCE.json` 및 PR receipt 참조.

구체적인 유도는 `THEORY_KO.md`, 실행·보존 상태는 `EVIDENCE.json`, `DAG.json`,
`BACKUP_ACKS.json`, 독립 검토는 `review/`에 있다.

## 코드와 입력

```bash
python -m unittest discover -s tests/trajectory -p 'test_r3n_*.py' -v
python scripts/probe_r3n_predictor.py --evidence-dir /tmp/rec-r3n-probe-new
python scripts/compare_r3n_time_grids.py analyze \
  --history research/rec_r3n_time_convergence_20261019/real_h2_trace_003/h2_state_trace.json \
  --evidence-dir /tmp/rec-r3n-saved-new
```

출력은 아직 존재하지 않는 새 디렉터리여야 한다. 원자적인 mkdir로 한 실행만 그 경로를
확보하고, JSON/NPZ/그림 파일도 기존 파일 교체를 거절한다. 분석은 실행 성공과 과학 판정을 구별한다.
정상적인 불완전 입력 진단은 exit 0과 `INSUFFICIENT_LEVELS`를 남긴다.
자동화에서 전 구간·세 격자 존재를 요구하려면 `--require-complete`를 붙인다.
이 경우 입력 격자/영역이 불완전하면 exit 3이다. 입력 손상은 exit 2다.

세 독립 trace가 준비되면 `--history`를 세 번 넘긴다. descriptor/NPZ 형식과 복구 명령은
`HANDOFF_KO.md`에 있다. C 이력이나 재보간 checkpoint를 Python grid로 대체하지 않는다.

## 실패와 교정

첫 실자료 연결에서 샌드박스의 추출 CSV 사본이 83,034,112바이트로 잘린 것을 hash gate가
거절했다. 원격 tar 전체와 tar 내부의 299,795,855바이트 CSV는 올바른 SHA였다.
원본 tar member를 별도 파일로 직접 스트림 복구하고 fsync/전체 readback hash를 확인해
입력 의무를 닫았다. 최초 추출 사본이 잘린 원인은 미확정이다. 원본 receipt나 gate를 바꾸지
않았다. `real_h2_trace_001/failure.json`, `receipts/INTAKE.json`에 보존했다.

첫 unit test는 coarse 오차가 커지면 contraction이 실패해야 한다는 잘못된 기대를 가졌다.
이는 수식상 반대다. fine-grid 경계 spike가 D12에서 누락되지 않는 검증으로 바로잡았고
그 검사는 통과했다. 원래 생산 적분기의 결함으로 해석하지 않는다.

## 판정 범위와 다음 의존성

full U6의 같은-h 검증은 PR107 owner 실행을 재사용한다. 새 코드는 저장 상태의 시간 격자
비교에 필요한 구현이며 전 구간 세 격자 실행 결과를 만들어 내지 않는다. R3M trace는
z≈836.041…669.959의 h2 자료다. h/h4의 해당 독립 이력, h2의 낮은 z 후속 이력 및
각 격자의 stage/checkpoint provenance가 연결되어야 기존 z8000…0 계약을 닫을 수 있다.
이미 끝난 원본 h 노드는 identity를 확인해 재사용한다.

원본 ZIP, U5 checkpoint SHA, h2=4.245e-5, atomic/thermal operator, stage boundary,
predictor memory, same-h 기준은 수정하지 않았다. U5 `HOLD_9_FAIL`/`HOLD_8_FAIL`,
`CLOSED_HOLD_NOT_RESET`, REI=false를 유지한다. Bianchi/REI/CMB 예측이나 production
speedup을 이 단위에서 승인하지 않는다.

## 게시 후 공통 CI의 형식 교정

전용 코드 CI는 첫 게시 SHA에서 45 tests/6 controls를 통과했다. 공통 CI는 이전 실패
로그 `tests_007`의 원문 줄 끝 공백을 발견해 pytest 전에 중단했다. 원문을 손실 없는
`receipts/tests_007.log.gz`로 보존하고 압축 해제 바이트 일치를 확인했다. 수치 코드나
whitespace gate 정책은 수정하지 않았다. `receipts/CI_FORMAT_CORRECTION.json`을 참조한다.

공통 CI 재검증도 성공했다: `3c8baceb`의 push/PR run은 각각 787 PASS, 4 SKIP,
14 subtests PASS다. 전용 CI의 45개 테스트를 포함한 수다. 최종 문서 HEAD와 보존
ZIP의 생산자 SHA 및 저장소별 전체 회수 검사는 PR108 Conversation receipt에 기록한다.
