# REC R3j U6 실행 인계

## 최신성과 범위

PR #102, branch `research/rec-r3j-u6-owned-history-20261018`를 직접 읽고 최신 HEAD 및 CI를 확인한다. 기준 부모는 PR #101의 `b2ae286274fea1fbe24a8c981fc84456e0f181ae`다. 중단 전 U4 개발 요청은 이미 U4/U5 실행으로 대체되었다. U4/U5를 재구현하거나 재실행하지 않는다.

새 코드: `owned_flrw_history.py`, `primordial_2012_owned_u6.py`, `scripts/run_r3j_u6_owned.py`. 기존 U6 적분기와 verifier, atomic/thermal RHS, 311-bin grid, h=4.245e-5, thermal latch, predictor tails, Schur 및 spectral 허용치는 수정하지 않았다. 새 경로는 명시적인 opt-in이다.

목적은 53179부터 58389까지 5210개 FULL 입력을 계산하고 첫 EMLA 평가 전에 종료하는 것이다. 원본 C oracle은 같은 h/2에서 z=8000부터 독립적으로 실행한다. Python은 검증된 자신의 U5 checkpoint에서만 재개한다. h-grid checkpoint 재보간은 금지한다.

## 수치적 동등성의 근거와 남은 확인

원래 U6는 매 단계 growing prefix의 유한성을 직접 검사하고 causal 함수도 같은 prefix를 다시 검사한다. 새 객체는 prefix를 한 번 복사·검사하고, 625개 전체 candidate fields를 모두 검사한 뒤 한 열을 commit한다. 수용된 j개 열이 finite라는 귀납적 불변식과 k+1<=j-1 조건으로 동일한 검사를 유지한다. retarded 시간과 두 이웃 가중합의 원본 binary64 연산 순서를 유지했다. 외부 입력 배열 변경이 소유 이력에 영향을 주지 않는다. readonly view는 신뢰된 observer용이며 NumPy .base를 악의적으로 조작하는 코드에 대한 보안 경계가 아니다.

validation scan의 계산량은 O(B*(J*N+N^2))에서 O(B*(J+N))로 줄어든다. 이는 이 부분의 연산량 유도이지 전체 적분 속도 실측이 아니다. 전체 C text 검증과 atomic solve의 비용은 남는다.

CI는 manufactured signed spectra의 313-link 바이트 동등성, h/h2/h4, clock rejection, atomic append, 입력 alias 차단, synthetic source를 사용한 U6 3단계 recurrence 동등성을 검사한다. 이 검사는 실제 U5 checkpoint의 새로운 science parity나 전체 U6 PASS를 뜻하지 않는다. 새 실제 checkpoint smoke가 먼저 필요하다.

## 입력 직접 확보

사용자에게 다운로드나 명령 실행을 요구하지 않는다. 별도 fresh clone을 사용한다. 원본/dirty checkout, 기존 NCP 프로세스와 checkpoint는 보존한다.

- U5 archive: `gdrv:rec_bianchi_research_backups/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz`
- 동일 Dropbox: `dbx:bianchi/rec_bianchi/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz`
- Archive SHA256: `8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c`
- U5 checkpoint SHA256: `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`
- 원본 HyRec ZIP SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`

기존 owner/NCP 파일이 동일 SHA로 존재하면 재다운로드하지 않는다. 없다면 rclone으로 직접 회수한다. 아카이브 멤버를 검사해 절대경로, '..', 심볼릭링크를 거부하고 별도 디렉터리에 안전하게 추출한다. checkpoint의 이름을 추정하지 말고 NPZ 후보의 SHA를 검사하여 유일한 일치 파일을 찾는다. `SOURCE_MANIFEST_V6.json`에 필요한 선행 코드/입력이 빠졌으면 기존 백업에서 동일 SHA 멤버만 복구한다. manifest를 느슨하게 바꾸거나 누락 검사 자체를 제거하지 않는다.

## 새 자원 배정

이전 450 CPU초/750 wall초 allocation의 HOLD를 변경하거나 시계를 0으로 되돌리지 않는다. 현 요청의 새 bounded U6 작업은 별도 allocation ID로 기록한다. 제안하는 새 전체 배정은 준비·smoke·full·회수를 합쳐 180 CPU초/600 wall초이며, 실제 자원 현황과 정책이 허용하는지 실행 전에 확인한다. 회수용 최소 30 CPU초/120 wall초를 남긴다. 기존 실행기 자체의 60 cumulative process-tree CPU초, 180 wall초, 2 GiB, 1 CPU, BLAS/OMP 1 thread는 그대로다. 이 배정이 적절하지 않으면 새 실행 전에 typed HOLD를 기록하고 제한을 몰래 늘리지 않는다.

## 실행

1. 최신 HEAD를 `PIN`으로 기록하고 fresh clone에서 `PYTHONPATH=src:scripts python -m pytest -q tests/trajectory/test_owned_flrw_history.py tests/trajectory/test_primordial_2012_refined_u6_rt_boundary.py`를 실행한다. 필요한 설치는 해당 clone의 venv 안에만 한다.
2. 사용자가 제공한 NCP SSH 대상과 로컬 키를 사용해 직접 접속한다. 기존 작업/CPU affinity/RAM, Python/GCC를 확인한다. 공개 저장소나 receipt에 키 내용, 토큰, 개인 연결 정보를 저장하지 않는다.
3. NCP 새 namespace에 fresh clone 또는 .git identity가 유지된 소스 트리를 둔다. script가 `git rev-parse HEAD`와 tracked diff를 검사하므로 source manifest만 넣은 비-Git 폴더로 실행하지 않는다. 원본 source closure를 검사한다.
4. 먼저 아래를 실제 실행한다. CHECKPOINT와 OUT은 executor가 찾은 경로다.

```bash
python scripts/run_r3j_u6_owned.py \
  --checkpoint "$CHECKPOINT" --evidence-dir "$OUT/smoke_001" \
  --expected-commit "$PIN" --new-allocation-id "$ALLOCATION" --mode smoke
```

5. 새 smoke의 모든 same-h state/RHS/313-link/625-field 조건, raw evidence와 sidecar journal을 확인한다. 가능한 범위에서 legacy U6 3-step 결과와 직접 비교해 상태/스펙트럼의 수치 동등성과 실제 wall/CPU를 측정한다. manufactured CI 결과로 이 단계를 대신하지 않는다.
6. 같은 allocation에서 예상 full 비용과 회수 reserve를 만족할 때만 다음을 실행한다.

```bash
python scripts/run_r3j_u6_owned.py \
  --checkpoint "$CHECKPOINT" --evidence-dir "$OUT/full_001" \
  --expected-commit "$PIN" --new-allocation-id "$ALLOCATION" --mode full
```

7. output status만 보고 전체 PASS를 선언하지 않는다. 정확히 5210개 accepted inputs, 최종 global index 58389, FULL 평가수5210, 첫 EMLA 미평가, all-field same-h C/Python 검사를 확인한다. 새로운 평균 photon 차이는 기존 검증기 원본 gate와 제한된 Decimal80/IEEE gate로 각각 기록한다. h의 HOLD_9_FAIL과 h/2 U5의 HOLD_8_FAIL을 바꾸지 않는다.

## 보존과 다음 DAG

매 의미 있는 완료 단위에서 source/결과/raw first failure/DAG를 게시하고 create-only archive를 Dropbox와 Google Drive의 새 R3j 폴더에 백업한다. 두 provider에서 전체 raw archive를 다시 읽어 SHA256과 byte count를 확인한다. source package와 실행 결과의 identity를 구분한다. 이전 raw archive는 보존한다.

이번 full U6가 실제 검증되면 그다음은 h/2 EMLA continuation이다. h/4, 전체 primordial time convergence, Bianchi 재결합, REI 광학깊이와 CMB는 이번 결과에 포함되지 않는다. REI production과 activation=false는 변경하지 않는다.

반환: 정확한 실행 commit, CI/local/NCP 별도 테스트, 실제 U5 smoke와 full 여부, old/new resource ledger, same-h 오차, 측정된 CPU/RSS/wall 범위, 최초 실패, 양쪽 백업 SHA 및 별도 draft evidence PR. 코드의 주개발을 NCP에서 새로 시작하지 말고 게시된 경로를 실행·검증한다.
