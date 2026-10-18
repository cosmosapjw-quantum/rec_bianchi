# REC R3k 실행 인계 및 새 대화 복구

## 최신 결과

PR104: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/104
브랜치: `research/rec-r3k-owned-u6-validation-20261018`.
계산·테스트 코드 기준 SHA: `42ed7b5d1de1218b8e943dd4b376ec1744014510`.
부모는 PR102 `e0cfdf76a6e8bf04110715d14efaad7077aeff8b`; PR103의 128단계 duplicate-scan-only 결과는 읽고 재사용했으며 덮어쓰지 않았다.

GitHub Actions run 39127381978에서 37 PASS (3.87 s). 실제 U4 세 상태에서 313-link owned gather가 기존 함수와 바이트 동일하고, 그 입력의 Python FULL 원자 결과가 새로 컴파일한 원본 h/2 C와 기존 기준으로 일치했다. 최대 같은-input RHS 정규화 차이 2.603472992745992e-13, 최대 평균 spectrum 허용오차 비율 2.0300159967437363e-5. 합성 source에서 두 실제 integrator를 실행하는 3-step 비교와 오염/미완료 거절 검사는 통과했다. 이것은 실제 U5 초기조건의 시간 적분 결과나 U6 전체 결과가 아니다.

샌드박스는 백업 회수 뒤 ClientError/ServerError로 중단되어 새 코드 검증은 GitHub CI에서 수행했다. 새 xAct 계산과 native subagent 실행은 하지 않았다. Wolfram으로 affine interpolation, 정수 causal index 및 검사량 합을 확인했다. 원본 참고: Ali-Haimoud & Hirata, PRD83 043513, arXiv1011.3758. 원본 물리 및 old U5 photon-mean tolerance는 변경하지 않았다.

## Codex에 그대로 전달할 프롬프트

$physmath-research-loop를 사용해 REC PR104의 다음 bounded 실행을 수행하라. 사용자에게 다운로드, SSH, 압축 해제를 요구하지 말고 직접 확보하라.

1. 먼저 GitHub와 `dbx:bianchi/rec_bianchi/`, `gdrv:rec_bianchi_research_backups/`의 새 백업을 읽어 이후 진행된 동일 노드를 재사용하라. PR104 최신 HEAD와 `research/rec_r3k_owned_validation_20261018/{EVIDENCE.json,DAG.json,BACKUP_ACKS.json,HANDOFF_KO.md}`를 읽어라. 이미 완료한 R3f 97-case, U4 및 U5를 재실행하지 마라. 원본 checkout/다른 REI 작업은 보존하고 fresh clone을 사용하라.

2. 테스트된 Python source는 이미 게시되어 있다. NCP에서 새 기능을 다시 구현하는 것이 아니라 컴파일, 환경 차이에 대한 작은 수정, 실제 입력 검증과 실행을 수행하라. 원본 HyRec ZIP SHA256은 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`이다. U5 checkpoint SHA256은 `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`이다.

3. 먼저 owner PC의 기존 U5 사본을 hash로 찾는다. 없으면 다음에서 직접 회수한다:
`gdrv:rec_bianchi_research_backups/20261016/R3I_H2_U5_THERMAL_20261018_001_916cedd/REC_R3I_H2_U5_THERMAL_RUN_001_RAW.tar.gz`
또는 동일 접미사의 `dbx:bianchi/rec_bianchi/20261016/` 경로.
원본 raw archive SHA256은 `8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c`이다. 안전한 경로/member 검사 후 hash가 일치하는 NPZ를 선택하고 allow_pickle=False로 읽는다. coarse-grid/C stdout으로 대체하지 마라.

4. 공개 문서 밖의 사용자 제공 SSH 접속 정보와 기존 `/home/cosmosapjw/.ssh/ncp_key`로 NCP에 직접 접속하라. 서버 주소나 키 내용은 공개 PR에 기록하지 않는다. 64 CPU/128 GiB는 이전 관측값이므로 현재 affinity와 다른 작업을 다시 확인한다. old budget `CLOSED_HOLD`는 보존하고 새 실행 할당과 전송/복구 reserve를 별도로 기록하라. 새 allocation-id는 승인이나 예산 자체를 생성하지 않는다. 실행 한도는 비교 runner 및 기존 verifier의 1 CPU, BLAS1,2GiB,60CPU s,180wall s를 유지한다.

5. fresh clone에서 현재 exact git HEAD를 `SHA`로 확보하고, 검증된 checkpoint를 `CP`, 새 evidence root를 `EV`, 실제 할당 label을 `ALLOC`로 자동 설정한 뒤 실행한다. archive capsule에는 .git이 없으므로 source_binding을 속이지 말고 실제 Git checkout을 사용한다.

```bash
PYTHONPATH=src:scripts OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python3 -m pytest -q tests/trajectory/test_owned_flrw_history.py \
 tests/trajectory/test_primordial_2012_refined_u6_rt_boundary.py \
 tests/trajectory/test_r3k_backend_comparison.py tests/trajectory/test_r3k_pair_driver.py
python3 scripts/compare_r3k_u6_backends.py --checkpoint "$CP" \
 --evidence-dir "$EV/pair16" --expected-commit "$SHA" \
 --allocation-id "$ALLOC" --steps 16
python3 scripts/run_r3j_u6_owned.py --checkpoint "$CP" \
 --evidence-dir "$EV/native_smoke" --expected-commit "$SHA" \
 --new-allocation-id "$ALLOC" --mode smoke
```

6. paired runner는 두 독립 Python 경로의 바이트 동등성만 검사한다. 원본 C 동일-h gate는 다음 native smoke에서 따로 확인한다. CPU/전송/복구 잔여량을 확인하고 필요할 때만 같은 비교를 128단계로 확대한다. 한 번의 wall 비율을 성능 확정으로 보고하지 마라. 필요한 checkpoint/OOM/수치 실패는 첫 raw 기록을 보존한다.

7. 비교, 같은-h C smoke, 유효한 자원·복구 예산을 모두 충족한 경우에만 `run_r3j_u6_owned.py`의 `--mode full`을 새 evidence path로 실행한다. 목표는 5210 FULL steps, global 53179->58389이며 첫 EMLA 계산은 이 노드에 포함하지 않는다. old U5 h/h2 평균 gate HOLD_9_FAIL/HOLD_8_FAIL과 별도 roundoff-aware 판정을 유지한다. 전체 h/2 및 h/4 수렴성이나 REI activation으로 승격하지 마라.

8. 각 의미 있는 완료 단계마다 실제 code/result/DAG를 commit하고 archive를 create-only로 Dropbox와 Drive에 업로드한다. 이번 R3k 기존 백업은 provider ACK만 확인되었으므로 양쪽 전체 readback SHA256을 검증해 추가 receipt로 보완한다. 새 결과는 PR104 이후 stacked draft PR로 게시하고 합병은 하지 않는다. 보고에는 실제 steps, 같은-h state/RHS/spectrum 오차, byte identity, timings, 비용 범위, 실패/미실행, 두 클라우드 readback과 PR을 포함한다.

## 새 ChatGPT 스레드에 그대로 전달할 프롬프트

rec_bianchi 연구를 이 스레드에서 이어간다. $physmath-research-loop를 사용하고 백업의 새 실행 결과를 먼저 확인한 뒤 최신 GitHub와 대조하라. 기준은 PR104와 `research/rec-r3k-owned-u6-validation-20261018`; 테스트 코드 SHA는 42ed7b5d1de1218b8e943dd4b376ec1744014510이다. 먼저 위 EVIDENCE.json, DAG.json, BACKUP_ACKS.json, HANDOFF_KO.md를 실제로 읽어라.

R3k는 원본 HyRec q=0/h2의 소유권 기반 이력 저장을 검증했다. GitHub CI 37 PASS, 실제 U4 세 상태에서 owned gather 바이트 일치 및 C atomic625-field parity, 합성 source에서 두 실제 U6 recurrence와 비교 실행기 오염검사 PASS. 실제 U5 checkpoint의 owned 시간 적분과 전체5210-step U6는 NOT_RUN이며 성능향상은 미측정이다. R3f, U4/U5의 기존 완료 결과를 반복하지 않는다.

업로드된 테스트 source/evidence ZIP은 BACKUP_ACKS의 Drive/Dropbox/Library ID로 찾는다. producer SHA256과 원격 업로드 ACK는 있고 전체 원격 readback SHA256은 NOT_RUN이다. 현재의 샌드박스 동작은 새로 확인하되 과거 ServerError를 테스트 PASS나 새로운 물리실패로 해석하지 마라. native subagent를 가장하지 마라. 여기서 가능한 코드 수정·경량 검증은 직접 수행해 push하고, NCP에서는 컴파일·작은 수정·실제 실행만 남겨라. 필요한 Codex 인계는 파일 다운로드 요구 없이 본문에 복사 가능한 형태로 제공하라. 단계마다 실제 백업/게시/DAG 상태를 갱신한다.

핵심 제약: 원본 ZIP과 검토된 checkpoint identity, DLNA, source stage, C/Python 같은-h 기준, old 평균광자 HOLD_9_FAIL/HOLD_8_FAIL, 닫힌 누적 budget, REI activation=false를 보존한다. 다음 최소 결과는 실제 U5 checkpoint에서 legacy/owned16-step 바이트 비교와 원본 C smoke이며, 이를 통과하고 충분한 할당이 있을 때만 fullU6로 진행한다.
