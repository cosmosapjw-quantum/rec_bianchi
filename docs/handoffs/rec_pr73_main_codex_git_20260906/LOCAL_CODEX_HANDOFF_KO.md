# REC PR73 로컬 실행·자동 수리·Git 직접 반환 인계

ROLE=LOCAL_CODEX
TASK=REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY
RETURN_TARGET=MAIN_CONVERSATION

## 1. 단일 목표와 최신 지시

이미 작성된 `check_original.py`로 비공개 BASS의 고정 원본 radial.rs와 실제 ModeBState를 로컬에서 실행하고, 실제 Rust 출력→REC 쌍반응→COM 대조까지 끝낸다. 새 수학·보간법·물리 map을 만들지 않는다.

같은 디렉터리의 SHARING_PROTOCOL_KO.md를 먼저 읽는다. 별도 작업 스레드는 없다. 범위 내 진단 코드 결함은 자동 수정·재검증하고, 최종 결과를 새 REC 결과 branch와 Draft PR에 직접 게시한다. 주 대화에는 고정 반환문서 링크와 commit/tree를 돌려준다. 옛 '무조건 실행1회', '모든 수리 금지', '원격 push/PR 금지', 'ZIP 수동 업로드 필수'는 이 인계에 적용하지 않는다. 원본 component와 과학적 의미의 보호는 유지한다.

이 문서 작성 시 로컬 작업을 시작하거나 새 수치 결과를 얻은 것은 아니다.

## 2. 고정 기준과 시작 상태

REC 저장소: cosmosapjw-quantum/rec_bianchi.
기존 사용자 위치 후보: $HOME/Dropbox/bianchi/rec_bianchi.
고정 진단 출발 commit: f62d2495cac0c692f33f29f139e413dccbe7241e.
그 tree: f7673ae14e0ad391a303c169c792421b5dd0650c.
PR73: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/73.

BASS 저장소: cosmosapjw-quantum/bass.
기존 사용자 위치 후보: $HOME/Dropbox/bianchi/bass 또는 $HOME/bass.
고정 BASS commit: 9d1c702ddf58549a06b29965a3d1b790a0c23159.
그 tree: 12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c.

이 인계문이 게시된 정확한 commit을 DELIVERY_SHA로 기록한다. 인계 branch는 `coordination/rec-main-codex-git-handoff-20260906-r1`이고 고정 출발 REC 위에 인계 문서만 추가한다. branch의 나중 tip을 보지 말고 사용자가 전달한 고정 URL의 commit을 확인한다.

새 작업은 DELIVERY_SHA의 격리된 child에서 시작한다. 같은 고정 원본과 검사기로 이미 실행 중이거나 완료된 작업이 있다면 그 상태를 우선 수령한다. 인계 문서의 추가만을 이유로 계산을 다시 실행하거나 실제 tested SHA를 바꾸지 않는다. 기존 결과를 새 문서 branch에 보존할 때도 원래 tested commit/tree를 유지한다.

사용자 checkout의 HEAD가 다르다는 이유로 reset/checkout/stash/clean하지 않는다. 필요한 객체가 있으면 재사용하고, 없으면 기존 승인된 인증으로만 fetch한다. source-subset 복원은 전체 checkout으로 보고하지 않는다. 토큰·Authorization·credential이 포함된 URL과 환경 덤프를 기록하지 않는다.

## 3. 읽을 자료와 고정 파일

REC의 AGENTS.md, docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md, 기존 PR73 CLOSEOUT_KO.md와 OBSERVED_RESULT.json을 읽는다. root HANDOFF_PROMPT.md의 다른 과거 실행을 시작하지 않는다. 적용되는 로컬 전역 하네스는 기존 위치에서 읽되 설치·hook 변경·전면 검증을 새 선행 작업으로 만들지 않는다.

고정 검사기:
- docs/research/rec_modeb_original_runtime/check_original.py
  blob 929697b8c59fadb55ee2c2efcd19c00e3ce432e1
- docs/research/rec_modeb_original_runtime/radial_driver.rs.in
  blob 44f301650d39b6069660ef6dcd037175905c5397

관측 대상 원본:
- BASS bianchi/q/modeb.py
  4df8421ab81459a448fff174286a03d1d38423c3
- BASS _rustcore/src/kinetic/radial.rs
  ec946fced75e80201d516d1368c77eee87afd5b2
- BASS _rustcore/src/kinetic/comoving.rs
  a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84
- REC src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py
  26ddc41e24fadf0bdd19f1924e1a429d602d9c19
- REC src/full_bianchi_hyrec/trajectory/com_source_deposition.py
  a3662cf399f14b7148d880266825be12baf934a0

검사기와 template은 최초 identity를 기록한다. 정당한 수리 뒤에는 새 blob/commit으로 기록하며 옛 blob과 일치한다고 주장하지 않는다. 관측 대상 원본은 변경하지 않는다.

## 4. 실행과 보존

이미 설치된 Python3.12의 적절한 환경, NumPy/SciPy/SymPy/mpmath/Matplotlib과 rustc를 사용한다. 실제 interpreter·compiler·package 경로와 버전을 기록한다. 설치·전역 upgrade·라이선스 변경·다른 서비스 종료를 임의 수행하지 않는다. 패키지 누락은 기존 다른 적절한 환경 선택으로 해결할 수 있지만, 실제 테스트를 실행하지 않는 fallback으로 PASS를 만들지 않는다.

Git 밖에 run-id별 host_logs, checker_output, mplconfig를 둔다. stdout/stderr와 process exit는 checker_output 밖에서 캡처하여 내부 SHA256SUMS 생성 중 파일이 변하지 않게 한다. PYTHONDONTWRITEBYTECODE=1과 -B를 사용한다. 로컬 실행에 가짜 GITHUB_WORKFLOW_SHA를 넣지 않고 execution_context=LOCAL_CODEX로 구별한다.

실제 핵심 명령:

```bash
cd -- "$REC_WT"
env -u GITHUB_SHA -u GITHUB_WORKFLOW_SHA -u GITHUB_EVENT_NAME \
  -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV \
  PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR="$RUN_ROOT/mplconfig" \
  timeout --signal=TERM --kill-after=10s 600s \
  "$PYTHON_EXE" -B docs/research/rec_modeb_original_runtime/check_original.py \
  --bass "$BASS_WT" --out "$RUN_ROOT/checker_output"
```

변수는 실제 조사 결과로 채운다. 외부 캡처에서 실제 process exit/signal/timeout을 기록하고 실패를 wrapper exit0으로 가리지 않는다. 첫 실행과 각 수정 후 실행은 별도 run 경로로 보존한다. 합리적인 전체 시간·자원 상한을 실행 전에 기록하고, 개별 호출의 기존 timeout을 결과를 숨기기 위해 늘리지 않는다.

check_rec_available.py의 독립 재실행, PR70 연구, 전체 pytest, Rust crate/PyO3 wheel rebuild, native sphere/evolve는 하지 않는다. 기존 checker의 8개 연결 검사는 그대로 수행한다. 과거 부분검사6개와 더해 새14개라고 보고하지 않는다.

## 5. 검사 의미와 자동 수정 범위

기존8개 TestID를 유지한다:
1. test_01_exact_log_time_jvp
2. test_02_actual_modeb_layout
3. test_03_original_radial_order2
4. test_04_actual_paired_api
5. test_05_original_order8_roundoff
6. test_06_geometry_and_measure
7. test_07_read_scatter_exact_counterexamples
8. test_08_actual_com_conservation_does_not_restore_null

ModeB pack 길이31·photon offset25·방향 우선 배치와 q=(1,2,4)를 실제 class로 검사한다. shape carrier의 n=2는 native sphere 인증이 아니다. Rust template은 변경하지 않은 radial.rs를 참조해 작은 실행 파일만 컴파일한다. 2점 stencil의 offsets=(-1,0), weights=(1/2,1/2), 내부 질의의 값2 및1/sqrt15를 실제 stdout으로 얻는다. 총8개 JSON 행은8개 Rust unit test라는 뜻이 아니다.

REC 쌍반응에는 새 Rust 출력의 실제 값을 전달한다. 폐형식 수치로 대체하지 않는다. 정확한 Planck control의 순률0과 보간 사례의 (1-3/sqrt15)/8 H^-1 s^-1를 구별한다. 비영점 반례를0으로 고치지 않는다.

8점 보간의 n=32,64,128 및 q=1,2에 대해 dot-product 반올림오차와 Planck 함수 근사오차를 분리한다. 고정된 gamma 경계와80자리 기준은 유지한다. 전체 보간오차가 작아야 하는 새 사후 tolerance나 수렴 승격은 만들지 않는다. 로그/Q시간 fixture는 C=-3/4,dC=31/16,G=-3/32,dG=133/512다.

같은 목표와 이 의미를 유지하면서 검사기·Rust 호출기·경로/import·캡처·로그·그림·반환물의 관측된 결함을 격리 child에서 자동 수정할 수 있다. 수정마다 최초 오류와 원인, diff, 새 소스 identity, 직접 관련 회귀검사를 보존한다. 수정 없이 같은 실패를 반복하는 재시도와 수정 후 재검증을 구분한다. 사소한 수리마다 재승인을 요구하거나 편집1회로 중단하지 않는다.

관측 대상 원본, 물리식·단위·부호·경계조건, oracle·기대값·허용오차, 원본 표와 과거 evidence는 수정하지 않는다. mock/전사본/skip/xfail로 원본 호출을 대체하지 않는다. 그 경계의 변경이 필요하면 원본 실패와 최소 수정 제안을 주 대화에 반환한다.

수리가 필요하면 변경 가능 경로는 두 진단 파일과 `docs/research/rec_modeb_original_runtime/local_returns/<run-id>/`의 직접 관련 검사·결과로 한정한다. 기존 CLOSEOUT_KO.md와 OBSERVED_RESULT.json은 역사적 기록이므로 덮어쓰지 않는다. workflow 또는 타 저장소 source를 임의 수정하지 않는다.

## 6. 반환자료를 Git에 직접 게시

동일 run의 원본과 수정 후 결과를 보존하고, 공개 가능한 최소 증거를 `docs/research/rec_modeb_original_runtime/local_returns/<run-id>/`에 추가한다. 원본 checker_output/RESULT.json과 로그를 사후 수정하지 않는다. 공개 사본이 필요하면 가공·비공개 제외 사항을 별도로 표시한다.

반드시 포함할 읽기 가능한 자료:
- RETURN_HANDOFF_KO.md: 목표, 실제 완료도, 최초 실패·수리, 변경 경로, 실행 TestID별 결과, 미해결 사항, 주 대화의 다음 한 작업.
- RETURN_IDENTITY.json: DELIVERY_SHA, REC/BASS 기준, 실제 tested source/tree, 수정본의 관계, 명령·환경·exit, core 불변성, 결과 상대경로, 공유하지 않은 증거의 이유.
- 실제 RESULT.json, unittest log, 수치와 필요한 작은 CSV/PNG, 수정 diff 또는 해당 커밋 파일.

checker의8개 검사 모두 통과하고 실제 원본 호출·exit0·원본 불변이 확인되면 PASS_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC를 보고할 수 있다. 추가 회귀검사는 따로 센다. 일부만 끝났으면 부분완료 그대로 게시한다. 수치 성공, 시각 검토, 게시 성공과 주 대화의 최종 수용은 별도다. NO_PASS_REC_PHYSICAL_SPLIT, physical_source_authenticated=false, provider_admitted=false를 유지한다.

PNG가 있으면 실제 열어 확인한다. 기존 표시용1e-18 floor를 측정값으로 읽지 않는다. 시각 검토는 별도 반환문에 쓰고 원본 RESULT의 visual_audit를 소급 고치지 않는다. 수치 실행을 재생하지 않고 파일/증거의 대응을 확인한다.

새 결과 branch 예: `results/rec-pr73-local-modeb-<UTC-run-id>`.
기본 부모: 정확한 DELIVERY_SHA.
이미 실행된 f62d2495 기반 작업이 있으면 그 actual tested SHA를 그대로 기록하고 문서 child에 결과를 보존한다. 문서 추가만으로 재실행하지 않는다.

기존 인증으로 해당 결과 branch만 non-force push하고, 인계 branch `coordination/rec-main-codex-git-handoff-20260906-r1`을 base로 Draft PR을 만든다. main, PR73 또는 인계 branch를 직접 갱신하지 않는다. 같은 작업 PR이 이미 있으면 중복을 피하고 자신이 소유한 결과 branch만 이어간다. 공개할 source diff와 evidence에 비공개 BASS 원문·토큰 등이 섞이지 않았는지 해당 파일만 확인한다. 전체 BASS clone/bundle/컴파일된 비공개 source를 공개하지 않는다.

remote commit/tree와 branch, 변경 경로, Draft·미병합 상태, 실제 반환 파일의 내용을 다시 읽는다. 결과 commit은 실행 source commit과 구별한다. 최종 게시 SHA를 같은 commit의 파일 안에 넣으려 무한 갱신하지 않는다. 그 SHA는 PR 본문과 최종 출력에서 전달한다.

Atlassian 변경과 최종 수용·후속 연구 결정은 주 대화가 한다. Codex는 merge/ready·권한·가시성을 변경하지 않는다. 실패 checkpoint도 정확한 상태로 같은 제한된 결과 branch에 게시할 수 있다. 게시 실패를 숨기지 않고, 기존 승인된 대체 게시 경로가 없으면 PUBLICATION_BLOCKED로 별도 보고한다. 사용자의 수동 ZIP 이동은 다른 전달 경로가 실제로 없을 때만 마지막 대안이다.

## 7. 주 대화에 전달할 최종 출력

아래 정보만으로 주 대화가 Git에서 자료를 읽을 수 있게 한다. 로컬 경로나 sandbox:/workspace 링크만 출력하지 않는다.

```text
작업: REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY
실행 결과: <실제 분류와 tests/exit>
수정: <변경 없음 또는 실제 수정 요약>
공유 상태: <PUSHED_READBACK_CONFIRMED 또는 구체적 blocker>
Draft PR: <실제 URL>
게시 commit/tree: <실제 SHA>
실행 source commit/tree: <실제 SHA>
반환 인계문: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/<게시 commit>/docs/research/rec_modeb_original_runtime/local_returns/<run-id>/RETURN_HANDOFF_KO.md
결과·증거: <고정 commit의 상대 파일 위치 또는 URL>
미해결: <구체적 항목>
NO_PASS_REC_PHYSICAL_SPLIT
```

최종 링크를 읽어 확인한 다음 이 한 작업에서 종료한다. 새 모델·실제 B/mu·provider·시간 진화로 자동 확대하지 않는다.
