# REC PR73: 완료된 로컬 원본 호출의 Git 반환

작업은 `REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY`다. 로컬 최종 결과는
**PASS_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC**이며, 원래 8개 검사에서
failures 0 / errors 0 / skips 0, 실제 process exit 0이다.
**NO_PASS_REC_PHYSICAL_SPLIT**, physical_source_authenticated=false,
provider_admitted=false를 유지한다. 최종 수용·병합·Atlassian 판단은 원래 주 대화가 한다.

이 반환은 이미 완료된 원본 실행과 그림 수정 후 실행을 재사용한다. 인계 문서 추가나
Git 게시를 위해 계산을 다시 실행하지 않았다. 과거 독립 REC 부분검사 6개를 합쳐
14개라고 집계하지 않는다. 게시 상태와 게시 commit/tree는 Draft PR 본문과 Codex
최종 출력에서 별도로 확인한다.

## source와 결과의 관계

| 역할 | commit | tree |
|---|---|---|
| 고정 Git 인계 | `85a8c4632dd062ae201937c3647accd5d93f9733` | `7f223c2b184e100129b19e6aa6e96cc7826d8554` |
| 최초 실제 로컬 실행 | `f62d2495cac0c692f33f29f139e413dccbe7241e` | `f7673ae14e0ad391a303c169c792421b5dd0650c` |
| 수정 후 실제 실행 | `c813bfc32b23e4d3148e3ed9318ec9276a746e0b` | `2fbb5562333f5e86e615a401f1a177f35f11ccbc` |
| 변경 없는 BASS 원본 | `9d1c702ddf58549a06b29965a3d1b790a0c23159` | `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c` |

결과 branch는 인계 commit에서 시작했다. 첫 부모는 고정 인계, 두 번째 부모는
실제 tested commit으로 연결하여 그 실행 source도 Git에서 읽을 수 있게 했다.
인계와 반환 문서가 추가된 게시 commit 자체를 실행했다고 주장하지 않는다.
기존 main·PR73·인계 branch는 갱신 대상이 아니다.

[실제 실행한 검사기](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/c813bfc32b23e4d3148e3ed9318ec9276a746e0b/docs/research/rec_modeb_original_runtime/check_original.py)와
[원본 Rust 호출기](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/c813bfc32b23e4d3148e3ed9318ec9276a746e0b/docs/research/rec_modeb_original_runtime/radial_driver.rs.in)를
그대로 읽을 수 있다. [RETURN_IDENTITY.json](RETURN_IDENTITY.json)에 기준·실행 identity,
실제 명령·환경·exit, 전후 core 불변성, 결과 위치와 비공개 보존 범위를 기록했다.

## 최초 실패와 실제 수리

과거 GitHub 전체 실행은 비공개 BASS의 인증 없는 fetch에서 exit 128로 멈췄다.
[HISTORICAL_FAILURE.json](HISTORICAL_FAILURE.json)에 원본 job 링크, 오류 발췌와
보존 로그 SHA-256이 있다. 이 과거 실패는 그대로 실패이며 새 결과로 소급 변경하지 않았다.
로컬에서는 이미 있는 승인된 GitHub 인증으로 고정 BASS source를 확보했다.

최초 로컬 checker 실행은 수정 없이 8/8 PASS였다. REC .venv에는 numpy,
BASS .venv에는 matplotlib이 없어 기존 cosmo_lab Python 환경을 선택했다.
설치·전역 설정·라이선스·서비스·권한 변경은 없었다.

원본 PNG를 실제 열었을 때 `n=128,q=1`의 관측 오차 0이 설명 없이 `10^-18` 점으로
표시되는 결함을 확인했다. 수정은 `check_original.py`의 그림 block에 한정했다.
표시 하한을 제목에 쓰고 해당 점에 `0 (shown at display floor)`를 붙였으며 표시
metadata를 추가했다. [PATCH.diff](PATCH.diff)가 실제 변경이다.

`Checks` 클래스 전체 AST와 원본 Rust template bytes는 그대로다. 물리식·부호·단위·
원본 표·oracle·expected·허용오차·8개 검사를 수정하지 않았다. 원본/수정의 수치
`checks` 및 실제 Rust 8개 출력 행은 모두 동일하다. 직접 관련 확인 결과는
[REGRESSION_RESULT.json](REGRESSION_RESULT.json), [repair_scope_check.json](repair_scope_check.json)에 있다.
추가 과학 검사를 만든 것이 아니며 반복 횟수로 PASS를 선택하지 않았다.

## 실제 8개 검사와 수치

| TestID | 원본 실행 | 그림 수정 후 실행 |
|---|---|---|
| test_01_exact_log_time_jvp | PASS | PASS |
| test_02_actual_modeb_layout | PASS | PASS |
| test_03_original_radial_order2 | PASS | PASS |
| test_04_actual_paired_api | PASS | PASS |
| test_05_original_order8_roundoff | PASS | PASS |
| test_06_geometry_and_measure | PASS | PASS |
| test_07_read_scatter_exact_counterexamples | PASS | PASS |
| test_08_actual_com_conservation_does_not_restore_null | PASS | PASS |

[원본 RESULT](runs/initial_original/output/RESULT.json),
[수정 후 RESULT](runs/repaired_plot/output/RESULT.json),
[실제 unittest log](runs/repaired_plot/output/unittest.log),
[TestID별 결과](runs/repaired_plot/PER_ID_RESULTS.json)를 직접 읽을 수 있다.

- 실제 ModeBState 생성·pack·set_from·q: pack 31, photon offset 25, angle-major,
  q=(1,2,4). n=2 shape carrier이며 native sphere 인증은 아니다.
- 변경 없는 radial.rs를 rustc로 컴파일하고 실제 binary를 호출했다. order2 읽기는
  powerlaw=2, Planck read=0.25819888974716115이며 내부 질의의 두 tail 출력은 동일하다.
  8개 JSON 행은 8개 Rust unit test라는 뜻이 아니다.
- 실제 Rust read를 기존 REC 쌍반응에 전달했다. 정확한 Planck control의 net은 0,
  보간 입력의 net은 **0.028175416344814574 H^-1 s^-1**, tracked partial은 -0.375다.
  비영점 반례를 0으로 바꾸지 않았다.
- 실제 COM.apply의 number/nH=0.05635083268962915,
  energy/(nH E0)=0.08452624903444372다. 제조 분배의 회계 보존이 비영점 반응을
  제거하지 않는다는 결과이며 실제 물리 map 인증은 아니다.
- order8의 지정 6개 (n,q)에서 80자리 log-dot 기준과 고정 gamma 산술 경계를 통과했다.
  [ORDER8_OBSERVATIONS.csv](ORDER8_OBSERVATIONS.csv)의 Planck 근사오차는 관측값이다.
  이를 새 사후 tolerance나 일반 수렴 인증으로 해석하지 않는다.

## 실행 환경·명령·시각 확인

[ENVIRONMENT.json](ENVIRONMENT.json): Python 3.12.3, NumPy 2.3.5, SciPy 1.18.0,
SymPy 1.14.0, mpmath 1.3.0, Matplotlib 3.11.0, rustc 1.94.1 / LLVM 21.1.8.
사용한 interpreter·compiler·module 경로는 공개 사본에서 host prefix만 치환했다.
과거 GitHub runner와 동일 버전이라고 주장하지 않는다.

원본 실행은 2026-09-06T14:35:13.023119Z 시작, 약 5.954초, exit 0;
수정본은 14:36:52.650957Z 시작, 약 2.432초, exit 0이다.
실제 argv·cwd·환경 override·timeout은 각 run의
[COMMAND](runs/repaired_plot/COMMAND.json)와
[PROCESS_RESULT](runs/repaired_plot/PROCESS_RESULT.json)에 있다. 외부 stdout/stderr는
checker output 밖에서 캡처했다. fake GitHub workflow SHA를 넣지 않았으며 기록 값은 null이다.

이 실행들은 새 인계 전에 기존 내부 120초·외부 720초 제한으로 끝났다. 새 인계의
600초 예시로 과거 명령을 소급 바꾸지 않았다. 새 인계의 환경변수 unset 목록도
과거 wrapper가 명시적으로 수행했다고 주장하지 않는다. 인계의 완료 실행 재사용
조항에 따라 계산을 다시 실행하지 않았으며, 두 실행의 실제 시간은 600초보다 짧다.

두 컴파일 모두 원본의 사용하지 않는 코드에 관한 warning 4개와 exit 0을 남겼다.
원문 경고에는 비공개 BASS 코드 발췌가 있어 공개 파일은 명시적인 요약이다.
원본 stdout, stderr, process exit와 source/driver identity는 로컬에서 그대로 보존했다.

[원본 그림](runs/initial_original/output/native_order8_error.png)과
[수정 그림](runs/repaired_plot/output/native_order8_error.png)을 각각 실제 열어 확인했다.
수정 그림의 0 및 표시 하한 주석은 읽을 수 있다. Host Codex의 시각 확인이며 독립
review가 아니다. 원본 RESULT의 `visual_audit=NOT_PERFORMED`는 소급 수정하지 않았다.

## 공개 사본과 남은 경계

[PUBLIC_COPY_MANIFEST.json](PUBLIC_COPY_MANIFEST.json)은 공개 파일별 원본 hash,
공개 사본 hash, 치환·요약 여부와 미게시 자료의 이유를 구분한다. JSON의 수치,
TestID·결과, source blob, 허용오차 및 물리 인증 flags는 원본과 일치함을 확인했다.
공개 CSV의 CRLF는 LF로, 외부 stdout 사본의 끝 중복 빈 줄은 한 줄로 정리했다.
CSV 값과 로그 본문은 그대로이며 원본 bytes는 로컬에 보존했다. 이 공개 포장 수정은
Git 공백 검사에서 재현된 문제에 한정한다. 공개 사본이 원본 bytes와 같다고 표시한
파일은 실제 byte-identical인 파일뿐이다.
새 SHA256SUMS는 공개 payload를 대상으로 하며 과거 manifest를 상속하지 않는다.

비공개 BASS 원문, 컴파일된 binary, 원문이 포함된 raw 경고, 원래 로컬 ZIP은 공개하지
않았다. 원본은 보존돼 있으며 공개 source call-site·출력·hash만으로 비공개 component
본문의 독립 심사를 대신했다고 주장하지 않는다. 그 본문을 검토하려면 주 대화가 가진
기존 비공개 BASS 읽기 권한을 사용해야 한다.

전체 crate/PyO3 wheel, native sphere/evolve, 독립 REC 부분 checker, base/hires,
전체 repository pytest, source/provider/physical-map 인증을 새로 수행하지 않았다.
이 결과의 Git 게시는 일반 CI PASS 또는 최종 과학적 수용이 아니다. 기존 사용자
checkout·생산 코드·역사적 CLOSEOUT/OBSERVED_RESULT는 보존한다.

**주 대화의 다음 한 작업:** 이 고정 Git 반환문과 연결된 8개 원본 호출 결과를 읽고,
필요한 비공개 원문 확인을 포함하여 PR73 결과의 최종 수용·후속 게시 여부를 판정한다.
