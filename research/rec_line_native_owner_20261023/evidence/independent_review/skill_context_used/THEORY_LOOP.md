# R1–R10: theory / mathematical physics

Maintain exactly ten stages; stage labels are a navigation structure, not a requirement to produce ten documents. The actual science, not length of the ledger, defines completion. For any reused result, check definitions, assumptions, units, dependency identity and scope.

## 7. 이론 10단계에 반영

| 단계 | 수행할 일 | 이번 정책의 적용과 완료 근거 |
|---|---|---|
| R1 연구 위치·계약 | 현재 질문, 탐색/수렴, 가정, 자료, 실행 범위를 확인 | 잘못된 정책 충돌을 식별하고 필요하면 최소 교정; 현재 연구 단위와 완료 기준 |
| R2 근거·재사용 | 원전과 기존 유도·데이터·코드를 확보 | 실제로 사용할 조건을 적고 미입증이라는 이유만으로 유용한 자료를 폐기하지 않음; 재사용 연결 |
| R3 주장·전제 정렬 | 정의·범위·출처·직접 유도를 구별 | 명시된 가정 아래 결론을 직접 기술; 사실상 동일한 주장과 새 기여의 대응 |
| R4 가설·표현 탐색 | 후보, 잠정 정의, 근사와 판별량 구성 | watchdog이 구체적 사상·예제·유도로 연결; 탐색할 표현과 최소 실행 |
| R5 구성적 유도 | 증명·계산·반례를 실제 수행 | 열린 의무를 실제 수학 작업으로 처리; 완성된 유도 또는 정확한 미완료 부분 |
| R6 독립 검증 | 물리·수학적 조건과 논증 확인 | 과잉 정식화 지적에 구체적 근거를 요구; no-go 후보는 증명·비자명성·범위를 확인 |
| R7 판별 검증 | 허용된 기호·경량 계산 또는 실행 계약 | 관찰된 결과를 정확한 범위로 기록; 미수행 항목은 구체적인 다음 실행 |
| R8 결과 판정 | 근거 상태와 다음 행동 결정 | 새로운 strong no-go는 NG1–NG7을 모두 확인; 일반 연구 의무는 구성적으로 계속 |
| R9 정식 결과·코딩 연결 | 이론 문서와 계산식 계약 작성 | 결과·가정·증거를 직접 서술; 반복되는 수사적 부정 제거 |
| R10 종료·재개 | 산출물과 바뀐 가정·의무 보존 | override의 짧은 기록, 재사용 가능한 근거, 다음 실행점 |

## Execution-grade completion contracts

- **R1:** State a narrow calculable question and current user-locked scope while keeping broader alternative landscape during exploration.
- **R2:** Read verified primary papers and preserved user outputs. Record formula/theorem location, data/coordinate conventions and reuse applicability. A source list alone is insufficient when synthesis was requested.
- **R3:** Separate established literature, direct derivation, numerical observation and hypothesis. Identify the precise extra assumptions needed by any transported claim.
- **R4:** Write actual candidate equations / maps / observables; keep competing constructions when scope remains exploratory. Verify first representative example.
- **R5:** Perform the derivation/proof, including nontrivial lemmas. Make analytic simplification, constructive solution or counterexample a first-class product; preserve partial derivations with exact remaining obligations.
- **R6:** Check sign, tensor/phase conventions, symmetry, dimensions, constraints, boundary and degenerate limits, regularity, exactness of approximation, and possible counterexamples. Identify the independence level of every check.
- **R7:** Execute allowed CAS/Python sanity checks when material to the claim. Classify heavy simulation explicitly and prepare an executable handoff when necessary.
- **R8:** Decide per claim what has been proved, supported, numerically checked, adopted for further work or held. Strong no-go must satisfy NG1–NG7; do not promote from an unproved absence.
- **R9:** Write a concise mathematically reusable statement/lemma and computational contract with variables, units, IC/BC, approximation, domain and validation targets.
- **R10:** Compact to durable evidence and next executable work. Separate storage acknowledgement from restoration and scientific verification.

## Selection and delegation binding (1.2.0)

Only execute the selected stages under ../STAGE_SELECTION.md. Existing prerequisites
may be read and stage-local checks performed; other stages are not implicitly
completed or replayed. Native delegation follows SUBAGENT_MODE.md. A completed
selected stage ends the invocation unless another selected stage remains. Shared
POLICY_INTEGRATION.md governs checkpoints, review bounds, repair convergence and
typed identity. A stage-specific plan or requested audit is an objective output.

