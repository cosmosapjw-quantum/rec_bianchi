# REC R3l: 파일 준비 없이 이어가는 실행 인계

다음 프롬프트를 Codex/실제 실행 환경에 그대로 전달한다. 사용자는 입력 다운로드, 압축 해제, 수동 SSH/SCP를 준비하지 않는다.

---

$physmath-research-loop를 사용해 rec_bianchi를 이어가라.

저장소: https://github.com/cosmosapjw-quantum/rec_bianchi
브랜치: `research/rec-r3l-profiled-history-io-20261019`
부모 PR105 HEAD: `3eb34b6a322d86d580b94f8f4bacfcadd33938ef`.
연구 경로: `research/rec_r3l_profiled_history_20261019/`.

1. 먼저 최신 PR/HEAD와 Drive `rec_bianchi_research_backups/`, Dropbox `/bianchi/rec_bianchi/`의 새 결과를 읽어라. README_KO, EVIDENCE, DAG, BACKUP_ACKS, PR Conversation의 최종 receipt를 확인한다. PR105의 U5 pair16/pair128와 3-step C smoke는 이미 보고된 실행이므로 반복하지 않는다. 원래 pair RESULT.json, smoke verification.json 및 원시 출력의 독립 대조가 가능한지는 별도 근거로 기록한다. 예전 37 tests는 GitHub Actions, R3l의 42 tests와 3쌍 저장 측정은 ChatGPT sandbox에서 수행됐다.

2. 현재 Python/C/C++/rclone/SSH 사용 가능 여부와 CPU affinity, memory, 동시 작업, 실제 비용 여유를 직접 확인한다. 과거 runtime 실패를 계승하지 않는다. 기존 인증을 사용하며 접속 주소·key 내용을 공개 코드/PR에 쓰지 않는다. 사용자에게 파일 준비나 수동 명령을 요구하지 않는다.

3. fresh git checkout을 확보한다. 대형 archive를 전부 받을 필요가 없으면 git의 정상 sparse checkout을 사용하되 src, scripts, 필요한 tests, research의 source manifests와 고정 원본 HyRec 입력을 포함한다. 현재 HEAD를 SHA로 읽는다. `run_r3l_u6_profiled.py`의 source binding은 실제 Git checkout, clean tracked tree와 committed adapter를 요구한다. source capsule에 가짜 HEAD를 부여하지 않는다.

4. 검토된 U5 checkpoint SHA256은 `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`다. 기존 owner/NCP 사본부터 해시로 찾는다. 없으면 기존 rclone 연결에서 아래 원본을 직접 회수한다. 이 raw SHA는 `8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c`다.

```
gdrv:rec_bianchi_research_backups/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz
dbx:bianchi/rec_bianchi/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz
```

원본 raw는 308,069,518 bytes이므로 ChatGPT 단일 파일 다운로드 한도를 초과한다. raw가 확인되면 `python3 scripts/extract_r3l_reviewed_u5.py --archive "$RAW" --output-dir "$NEW_RECOVERY_DIR"`를 실행하고, 출력 NPZ를 CP로 쓴다. 작은 `REC_R3L_REVIEWED_U5_CHECKPOINT.zip`과 recovery receipt를 원본 raw와 구별하여 create-only 게시/이중 백업한다. coarse-grid/C state로 Python checkpoint를 대체하지 않는다.

5. 여기서 구현을 다시 시작하지 않는다. 필요한 compiler/작은 compatibility 수정만 수행한다. 환경 차이가 생겼을 때 새 관련 테스트를 실행한다. 고정 원본 ZIP SHA `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27` 및 V6 closure를 검증한다. 과거 budget은 CLOSED_HOLD 그대로 보존한다. 새 allocation ID는 권한이나 예산을 생성하지 않으며 실제 할당과 전송/복구 reserve를 따로 기록한다.

6. CP, 실제 현재 SHA, create-only EV, 유효한 ALLOC를 스스로 설정하고 다음 새 profiled pilot을 실행한다.

```bash
REC_R3L_EXECUTION_LOCATION=ncp PYTHONPATH=src:scripts \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python3 scripts/run_r3l_u6_profiled.py \
  --checkpoint "$CP" --evidence-dir "$EV/pilot128_stored" \
  --expected-commit "$SHA" --new-allocation-id "$ALLOC" \
  --mode pilot --pilot-steps 128 --history-container stored
```

owner에서 실행하면 execution label도 실제 위치에 맞춘다. 기존 owned recurrence, 원본 C 재구성/같은-h gate, 60 CPU s / 180 wall s / 2 GiB / BLAS1을 유지한다. 이 pilot은 새 저장 경로와 단계별 비용의 실행이다. 원래 pair16/pair128의 재실행으로 기록하지 않는다.

7. verifier `verification.json`의 status/first_failure, actual steps, state/RHS/spectrum maxima와 원래 평균광자 및 roundoff-aware 판정을 읽는다. `.r3l_phases.jsonl`, `.r3l_profile.json`에서 exclusive CPU를 합하고 unattributed 및 제외된 closeout/전송 비용을 구분한다. 원래 예외와 secondary profiling/closeout 오류도 따로 기록한다. hard kill이면 마지막 durable phase/원시 partial 자료를 보존하고 실제 종료 코드로 분류한다.

8. 유효한 새 할당과 reserve, 보존된 pair 근거, 같은-h 결과 및 실측 비용이 5210-step 실행을 지지할 때만 `--mode full`을 새 EV로 호출한다. 2점 fit의 6.047946 CPU s 또는 저장 단계의 22.48 비를 전체 시간 상한으로 사용하지 않는다. 그 조건이 충족되지 않으면 비용이 큰 구체적 phase와 다음 최소 수정만 보고한다. 한도 상향, old ledger 초기화, 검사 생략을 하지 않는다.

9. 완료 단계마다 actual source commit, 명령, 환경, 종료 코드, all phase receipts, verifier 결과와 해시, checkpoint/output NPZ, native stdout/stderr와 raw first failures, allocation/reserve ledger를 반환한다. 새 raw 결과와 검토된 U5 checkpoint-only capsule을 독립적으로 내려받을 수 있게 분리한다. GitHub stacked draft PR과 Drive/Dropbox create-only 백업을 완료하고 provider ACK와 실제 readback SHA를 구분하여 기록한다.

보존 조건: h=4.245e-5, 원본 atomic/thermal operator, stage boundaries와 predictor memory, U5 h HOLD_9_FAIL/h2 HOLD_8_FAIL, 원래 같은-h 기준, REI activation=false. Python h/h2/h4 convergence, Bianchi/REI/CMB prediction은 별도 미완료 의무다.
