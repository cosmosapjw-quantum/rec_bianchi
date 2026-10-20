# REC R3R 후속 스레드 인계

## 먼저 읽을 현재 결론

R3P 이후의 최신 원격 결과는 **PR111의 R3Q NCP h4 event+2 및 h2 low-z 반환**이었다. 이를 실제 Drive/Dropbox archive에서 복구해 분석한 뒤 R3R을 열었다. 이번에 선택·완료한 연구는 **후보 B: 실제 spectral stream 감사에 bounded exact NumPy ratio를 연결**하는 작업이다.

새 코드를 작성하기 전에 최신 PR112/111/110과 반환 receipt를 다시 읽어 이후 새 NCP 결과가 있는지 확인하라. 현재 완료된 R3P/R3Q/R3R benchmark·smoke·CI를 새 증거 없이 반복하지 말라.

- Repository: https://github.com/cosmosapjw-quantum/rec_bianchi
- R3R draft PR112: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/112
- Branch: `research/rec-r3r-followup-costs-20261020`
- Base branch: `research/orchestration-20261020-next-loop` (PR111 draft)
- Merge: 수행하지 않음
- SSOT: `research/rec_r3r_followup_costs_20261020/`
- 마지막 게시 identity/CI/보존 상태: `DELIVERY.json`, `BACKUP_ACKS.json`, 최신 `receipts/*PUBLICATION*.json`
- 실행 source와 final metadata HEAD는 다르다. 아래 executed SHA를 보고서 HEAD로 대체하지 말라.

## 정확한 base/source/snapshot 역할

| 역할 | SHA |
|---|---|
| R3P actual U5 source |e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d|
| R3P complete code/evidence snapshot |0b80913bf1c665cc4cfab6dfaa3ea35f815a482f|
| R3P final metadata HEAD |888d56d72579d1e1fd30f66abe02d9f91809a767|
| 새로 복구한 R3Q NCP actual source |1ad0380110621446c42df9d995fd85db3a6c7e7a|
| R3R base |5b44bb21ce0599e55e0848e5e3ff320c9e8ca172|
| R3R base tree |9403d3778d0a81e9632cea58e42e59ed9581e980|
| R3R first formal attempt (fixture failure) |65ec195ec32cfcc4e918d1dd86b711fdeb5709ad|
| **R3R successful tests/benchmark/pilot actual source** |**1313b1f1b2c081d57bcce9c60e757ef79110df91**|
| **Successful actual source tree** |**97423cad509a9604269740132a6ad850faf8f19a**|

후기 EOF 정규화는 `receipts/TEXT_NORMALIZATION.json` 및 C9가 original1313 bytes와 연결한다. comparator/benchmark의 bytes는 같고 launcher/test AST(location 포함)는 같다. report/metadata 확장은 별도 배송이며 새 solver 실행 source라고 주장하지 않는다.

## 우선 읽을 증거

1. `DELIVERY.json`, `EVIDENCE.json`, `DAG.json`, `BACKUP_ACKS.json`.
2. `REPORT_KO.md`, `EQUATION_TO_CODE.md`.
3. `receipts/intake/github_intake.json`, `endpoint_correction.md`, `literature_support.json`.
4. `receipts/profile32/PHASES.json`: 첫 시도 accepted0/worker FAIL과 복구된32-step를 구별.
5. `receipts/formal_validation_001/validation.json`:60PASS/1 fixture-context FAIL, benchmark/pilot NOT_RUN.
6. `receipts/formal_validation_002/validation.json`, `benchmark/benchmark.json`, `pilot/supervision.json`, `pilot/R3R_BINDING.json`, `pilot/worker/verification.json`.
7. `receipts/SAME_OUTPUT_CHECK.json`, `PHYS_MATH_AUDIT.json`, `PHYS_MATH_CODE_AUDIT.json`, `C9_EVIDENCE_READBACK.json`, `C9_CODE_AUDIT.json`.
8. `figures/PLOT_GENERATION.json`, `receipts/VISUAL_REVIEW.json`, `receipts/ci/`.
9. `receipts/FORMAL_RAW_LOGS.tar.gz`와 stage1/stage2 보존 archive의 실제 raw. repo의 receipt 경로만 존재하는 것으로 재실행·독립 검증을 주장하지 말라.

## 완료 결과와 정확한 claim

- 로컬61개 고유 검사 PASS; formal 첫 실패와 fixture 수정 보존.
- 저장 native stream97,935 records, 새 accepted32/전체STEP40, spectral25,000.
- 모든 ratio native binary64 bytes에서 차이0개; maxima float.hex, verdict, guard 순서 동일.
- legacy CPU중앙값0.109308013s, NumPy0.080130212s; paired CPU중앙값1.3641298366배.
- legacy wall중앙값0.109321077s, NumPy0.080153802s; paired wall중앙값1.3638913471배.
- 각5회 warm-cache 전체 CSV 감사(open/parsing/allocation/callback/verdict 포함), warmup 제외. cold-cache/전체solver/새NCP플랫폼 성능 아님.
- fresh-process RSS88,875,008 vs88,887,296bytes는 interpreter/import/setup포함1회씩의 독립 process측정.
- 실제 NumPy pilot:32 accepted /128 FULL, common-input9개 PASS, same-h PASS, source104개 UNCHANGED, exit0.
- whole launcherCPU3.857951s,wall3.914853461s. baseline과 matched whole-solver speedup은 측정하지 않음.
- baseline/newpilot6개 raw byte동일,NPZ10개 payload shape/dtype/bytes동일.
- PHYS-MATH 및 PHYS-MATH-CODE PASS_SCOPED; C9 actual readback69raw/104source/12plots/25,000lanes,재적분0회.
- 비용·전체잔차·binary64차이·RSS 그림4종(PNG/PDF/SVG), root와독립reviewer직접검토.
- unique test수에 R3P의완료테스트나반복CI를더하지말라.

## 남겨야 하는 과학 상태

원래 reference h=4.245e-5, U5 h=HOLD_9_FAIL, U5 h/2=HOLD_8_FAIL, 역사 장부=CLOSED_HOLD_NOT_RESET, REI_activation=false를 유지한다. Global h/h2/h4 convergence=NOT_RUN, new production speedup=NOT_MEASURED, physical validity=NOT_ESTABLISHED, production readiness=NOT_APPROVED다.

이번 짧은 실행 grid는 이미 정의된 R3Q quarter-grid dlna2.1225e-5이며 native/Python 공통이다. 원래 reference h를 바꾸거나 cross-grid 수렴을 새로 통과시키지 않았다. 원래 worker의 SMOKE_ONLY/CAP_BEFORE_EVENT_PLUS_TWO를 보존했다. R3P의 SMOKE_ONLY/PASS_PENDING_REVIEW/HOLD_CAP_BEFORE_RT_BOUNDARY와도 구분한다.

h2 원문 z=0 cubic stencil은211713–211716의 네 상태가 모두 존재한다. s=1.4726230889209546을[0,1]로 clip하지 말라. 추가 음의 z RHS step이 필요하다는 과거 설명은 별도 교정 문서로 수정하고 원래 raw/receipt는 보존했다. 이를 global convergence 판정으로 승격하지 말라.

## 복구와 create-only 보존

Stage1은 intake와 실패·복구된 profile32 raw를 담는다. Stage2는 **R3P0b full snapshot 이후 code delta와 실제1313 formal raw/그림**이다. Stage2만으로 독립 full snapshot이라고 부르지 말라. 기준 ZIP은 `REC_R3P_CODE_EVIDENCE_HANDOFF_0b80913b_20261020.zip`, 122,092,525 bytes, SHA256 `edccebf552671489f91e3ec2c31357fb901b73f90e0230d0cbe24a0b1f524521`이다.

1. 연결된 GitHub branch에서 고정 commit/tree와 실제 receipt를 먼저 읽는다.
2. GitHub를 사용할 수 없으면 보존 ACK의 정확한 객체 ID로 기준 R3P full snapshot과 Stage2 delta를 복구한다.
3. archive entry의 안전한 경로, 각 entry SHA/Git blob, deleted 목록, 전체 tracked inventory를 확인해1313 tree를 재구성한다.
4. Stage1 profile32와 Stage2 formal raw를 원래 입력 receipt/hash에 연결한다.
5. 후기 final preservation을 읽어 최종 보고·C9·CI·backup ACK를 추가한다. 배송 HEAD를1313 실행 source로 바꾸지 않는다.

Stage2 파일은 `REC_R3R_STAGE2_CODE_EVIDENCE_1313b1f1_20261020.tar.gz`, 23,953,020 bytes, SHA256 `402e9a8a0d2f5e8cdbb1fbc2b2dea8e9556a48cc17224ef139c06ad3555dea5b`다. Producer는213개 entry 전체를 다시 읽고, 기준3,410개에서 target3,518개 tracked inventory와 canonical Git tree hash가 정확히 재구성됨을 확인했다. 코드114개 delta는 추가108개·수정6개·삭제0개다. 실패한 source65ec의 역방향 delta도 있다. 원래 기준 ZIP 전체 readback을 이번 packaging에서 새로 수행했다고 주장하지 않는다.

Drive/Dropbox/Library의 객체 ID, filename, size, producer SHA, upload ACK 및 독립 whole readback은 `BACKUP_ACKS.json`에 분리한다. Library 연구 경로는 `/rec_bianchi_recovery/R3R_20261020/`다. Drive folder 생성의 UNKNOWN/no ACK 같은 실제 실패를 성공으로 취급하지 말라. 같은 이름으로 다른 SHA를 덮어쓰지 말라. 과거 R3P 단계0/단계2 ZIP의 whole-readback NOT_RUN은 소급 수정하지 않는다.

SVG 원본4개는 `figures/ORIGINAL_SVG.tar.gz`, 원래 JUnit XML 두 개는 `receipts/FORMAL_JUNIT.tar.gz`에 bytes 변경 없이 보존했다. 각 member hash는 `figures/SVG_ARCHIVE.json`과 `receipts/FORMAL_JUNIT.json`에서 확인한다. 새 저장소 whitespace 정책 예외를 추가하지 않았다. 전체 원본은 Stage2에도 있으며 PNG/PDF와 검토 receipt는 직접 읽을 수 있다.

## 다음에 실제로 남은 연구와 최소 NCP 범위

이번 목표를 완료하기 위한 NCP 추가 실행은 필요 없다. 후보 A의 selected snapshot은 조건부 유도와 Wolfram 복사량 모델이 있지만, 이번 profile에서는 우선순위가 낮았다. 새로운 긴 실행의 profile에서 exclusive 비용이 입증될 때 별도 노드로 선정할 수 있다. R3P Rust ratio API의 전체 solver 이식이나 추가 thread의 이점은 이번 결과로 입증하지 않았다.

다음 연구 주제가 새 플랫폼 호환성이면 실제 Python/NumPy/C++/Rust 가용성을 서로 독립적으로 확인한다. 이 스레드의 rustc 미설치를 NCP에 전파하지 말라. 고정 source, 깨끗한 입력, 새 명시적 allocation, 새 evidence directory를 준비한 뒤 공개 `scripts/run_r3r_h4_supervised.py`에서 legacy와 NumPy의16 또는32-step 범위만 사용한다. 공개 max32를128로 늘리거나 event/full로 바꾸지 않는다.

60 CPU s / 180 wall s / process당2 GiB, closeout reserve와 더 낮은 inherited limit을 유지한다. 현재 full5210 또는 full h4 allocation은 없다. 더 큰 실행에는 실제 필요성, DAG 선행 검증, 복구 여유와 새 명시적 allocation이 필요하다. 사용자에게 과거 대화 복사·ZIP 재업로드·수동 SSH/SCP 또는 터미널 실행을 요구하지 말고 연결된 소스에서 직접 복구하라.

최종 판정은 수학 PASS_SCOPED / 수치 PASS_SCOPED / 구현 PASS_SCOPED / 감사 가속 PASS_SCOPED / 자원 PASS_SCOPED / 물리 HOLD / production NOT_APPROVED다. 각 판정은 서로 자동으로 전파되지 않는다.
