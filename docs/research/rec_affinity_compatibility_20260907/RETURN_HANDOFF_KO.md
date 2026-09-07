# 주 대화 반환 — REC affinity compatibility

상태: PR77의 고정 map 합성 JVP 수용; 새 affinity 불일치 반례 실행 완료.

주 대화에서 원격 PR77의 실제 실행 source, 전체 job log, TestID와 출력값을
확인했다. 새 판별기는 현재 환경에서 직접 실행했다. 이전 BASS 원본8개,
PR77의10개, 다른 저장소의 시험은 재실행하지 않았다.

| 구분 | source commit | tree | 실제 결과 |
|---|---|---|---|
| 수용한 PR77 CI | 4125f7f39b29b710ad6ca673520ae46a426b564f | bc5d7f0dbf477ccb693084dd9cd72e4e54bde25e | 10/10, exit0 |
| 새 주 대화 실행 | 7eb64cb8d65c1fa22f49c019f3c8ce4fb1d22bdc | 09a39358a7da53f467fb4d889157174d1d40eaa8 | 3/3, subprocess exit0 |

실제 실행 commit과 그 뒤의 문서·그림·증거 게시 commit은 다르다.
소스 수리나 의미 변경이 필요한 실패는 발견되지 않아, 과학 코드는
처음 실행한 파일을 유지한다. 게시 commit의 source delta 검사로 확인한다.

검토 문서: [MAIN_REVIEW_KO.md](MAIN_REVIEW_KO.md).
새 결과: [RESULT.json](evidence/affinity_run_01/payload/RESULT.json).
외부 프로세스 영수증: [PROCESS.json](evidence/affinity_run_01/PROCESS.json).
기존 결과: [PR77 RESULT_EXTRACTED.json](evidence/pr77/RESULT_EXTRACTED.json).
기존 raw log와 별도 CI 실패 분류는 `evidence/pr77/`에 있다.

과학적 진전: 모든 양의 원자 population ratio에서 nodal entropy 생성이
비음수일 필요충분 조건은 쌍의 읽기 affinity 합과 분배 entropy 방향의
일치다. 각 leg의 읽기 map 개별 일치까지 필요하다는 주장은 하지 않는다.
기존 log-f 대조는 eta=-1/8에서 수·에너지를 보존하면서도 엔트로피를
감소시킨다. 일치한 chi 구성은 같은 상태에서 비음수다.

미완료: 실제 기본/hires 다중 bin과 물리 target의 read/scatter 호환,
이동 map·measure 미분, angular/polarized kernel, 원본 물리 source/provider,
BASS evolution 및 전체 물리 split. 일반 저장소 CI는 과거7개 경로의
공백 검사에서 FAIL이고 repository pytest는 skipped다.

다음 한 작업: `REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH`.
기존 고정 2s 기본/hires 표를 사용하고, 명시적 target B/mu와 같은 광자
상태에서 bin별 Delta_b, 총 entropy rate, 합성 JVP를 검증한다. 실제
target map의 권위가 없으면 제조 연구임을 명시하고 production에 연결하지
않는다. 표나 해시를 target map 인증으로 대체하지 않는다.

현재 local Codex에 맡겨야만 하는 실행은 없다. 다음에도 이 대화에서
가능한 유도·구현·실행을 먼저 수행하고 실제 로컬 기능만 Git 인계한다.
local 인계가 생기면 같은 목표·scope·불변식 안의 결함은 자동 수정·검증한
뒤 자기 branch의 non-force push와 Draft PR로 반환한다. 수동 ZIP 전달은
기본 절차가 아니다.

`NO_PASS_REC_PHYSICAL_SPLIT`; physical_source_authenticated=false;
provider_admitted=false. 기존 evidence와 branch는 변경하지 않고 Draft를
유지한다. merge/ready 및 공식 Jira dependency 변경은 수행하지 않는다.
