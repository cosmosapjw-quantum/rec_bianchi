# R1 related-repository branch metadata inventory

현재 작업: R1 inventory만 수행. R2–R10/C1–C10 완료를 주장하지 않는다. 구현·과학 실행·외부 변경 0.

7 repos, 총 1,460 branches. rei_bianchi 264, bass 270, bass_cr 177, WU088_HH 151, htt_base 297, vigilode 203, BASS_HE 98. root가 저장한 page1은 다시 읽지 않고 파일을 재사용했고, 여섯 repo의 page2 onward를 REST로 끝(<100 rows)까지 읽었다. BASS_HE는 98-row page1으로 완결. 각 후속 page는 API 요청 전후 UTC 시각을 기록한다. inherited page1 파일에는 readtime 필드가 없어 해당 시각을 만들지 않았다. 서로 다른 시각의 page snapshot을 합친 inventory이며 단일 atomic repository snapshot이라고 하지 않는다. branch 이름 중복은 없었다.

RELATED_BRANCHES_COMPLETE.json: 전체 branch names/SHAs/protected 및 page source/time.
RELATED_BRANCH_TOPIC_MAP.json: branch name에 20261022–24 또는 characteristic/geodesic/history/thermo가 있는 61 rows. 날짜 문자열은 commit timestamp가 아니다.
RELATED_RECENT_PR_TOPIC_MAP.json: root의 32 recent PR snapshot 중 title/body/URL keyword가 맞는 28 rows. 원 body는 RELATED_RECENT_PR_SNAPSHOT.json에 보존. 이름·문구 연결이며 scientific dependency 판정이 아니다. REC branch/PR inventory는 다른 executor 담당이므로 여기 중복하지 않았다.

## Built-in 1.0.0 20 stages

Package: e1/skill-6aa0657100b08191b7d67482d1f97c1d
Root: /root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d

- R1 연구 위치·계약
- R2 근거·재사용
- R3 주장·전제 정렬
- R4 가설·표현 탐색
- R5 구성적 유도
- R6 독립 검증
- R7 판별 검증
- R8 결과 판정
- R9 정식 결과·코딩 연결
- R10 종료·재개
- C1 목표·baseline
- C2 식–데이터–코드
- C3 수치 설계
- C4 실행 DAG·자원
- C5 구현
- C6 구현 검증
- C7 과학 검증
- C8 수치·재현성
- C9 독립 검토
- C10 판정·인계

Full reference paths relative to that root:

- references/RESEARCH_POLICY.md
- references/THEORY_LOOP.md (R1–R10)
- references/CODING_LOOP.md (C1–C10)
- references/EVIDENCE_AND_HANDOFF.md
- references/RUNTIME_AND_LEGACY.md

정책·단계명 확인을 위해 RESEARCH_POLICY/THEORY_LOOP/CODING_LOOP를 source read했다. 현재 단계만 inventory로 기록했다. 다음 실행 계약과 물리 판정은 root가 고정한다.
