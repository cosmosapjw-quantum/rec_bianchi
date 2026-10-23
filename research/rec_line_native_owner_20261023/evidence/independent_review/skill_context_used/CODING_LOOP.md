# C1–C10: scientific coding

The coding phases apply to actual implementation and numerical scientific work. Preserve acceptance, physics and numerical gates separately. Use continuous math-to-code traceability; changed scientific formulas invalidate affected tests even if unit tests are green.

## 8. 코딩 10단계에 반영

| 단계 | 수행할 일 | 이번 정책의 적용과 완료 근거 |
|---|---|---|
| C1 목표·baseline | 계산량과 수용 기준 확정 | 참조식과 정책의 오류를 교정하고 목표의 의미를 보존; 기준의 identity |
| C2 식–데이터–코드 | 실제 계산 경로와 영향 범위 확인 | 추상적 비판을 식·함수·단위 변환으로 특정; 대응과 수정 위치 |
| C3 수치 설계 | 연속식·closure·이산화·오차 연결 | 유용한 추상화는 유지하고 불필요한 구조는 구체적 계산식으로 단순화 |
| C4 실행 DAG·자원 | 의존성과 경량/외부 실행 배치 | 잘못된 순서·중단 정책 교정; 현재 환경에서 할 수 있는 준비를 완료 |
| C5 구현 | 입력부터 검증 가능한 출력까지 작성 | 최소한의 완결된 구현; 가설·surrogate·실제 입력의 provenance |
| C6 구현 검증 | 계약·오류 처리·회귀·실행 확인 | 생산적인 수정과 동일 입력의 반복을 구별; 새 진단에 따른 수정 |
| C7 과학 검증 | 코드와 의도한 물리의 대응 확인 | 정확한 오류 항과 교정 근거를 보고; 실수치 실패를 넓은 불가능성으로 확대하지 않음 |
| C8 수치·재현성 | 오차·수렴·안정성·자원 조사 | 주장하는 정확도와 비용의 실제 비교; 국소 실패 기작과 후속 조치 |
| C9 독립 검토 | 중요한 diff·과학·수치 위험 점검 | 근거가 있는 finding만 남기고 해결된 지적 종료; 의미 있는 수용 기준 유지 |
| C10 판정·인계 | 수행 범위와 재개 가능한 패키지 정리 | 직접적인 결과 서술, 수정한 정책 이력, 남은 실행과 근거의 전달 |

## Execution-grade completion contracts

- **C1:** Fix baseline/reproduction and acceptance in physical units; distinguish bug, algorithm, feature, refactor, speedup. User-locked tolerance stays unchanged.
- **C2:** Map theory formulas, normalization, time variables, IC/BC and closure to exact code functions and data inputs. Check source revision and authority first.
- **C3:** Convert continuous expression into usable computational formula and stable discretization; explicitly classify truncation, solver, interpolation and roundoff errors.
- **C4:** Choose bounded DAG, computational platform and checkpoints by actual feasibility; avoid duplicate numerical work, memory overcommitment and nested overthreading.
- **C5:** Implement a complete runnable feature path, not a skeleton, under authorized mutation scope. Keep mathematically meaningful errors explicit.
- **C6:** Actually run build/unit/integration tests and record command, environment, exit code and artifacts. `NOT_RUN` is not `PASS`; repeated failure with new diagnosis is productive evidence.
- **C7:** Check code solves the intended physical problem: conserved quantities, covariances/gauge, initial and boundary conditions, source history and closure, independent limiting solutions and scientific references.
- **C8:** Run target-specific convergence, numerical stability and reproducibility checks. Compare speed only at matched accuracy and grounded hardware/problem sizes; distinguish predicted complexity and empirical speed.
- **C9:** Review changed surfaces and dangerous assumptions. A model's second reading is not always independent. Fix highest-risk findings then selectively recheck affected portions.
- **C10:** Decide release readiness per version and claim; durable handoff with source hash, input identity, execution command, resources, expected outputs, return payload and remaining blockers.

## Selection and delegation binding (1.2.0)

Only execute the selected stages under ../STAGE_SELECTION.md. Existing prerequisites
may be read and stage-local checks performed; other stages are not implicitly
completed or replayed. Native delegation follows SUBAGENT_MODE.md. A completed
selected stage ends the invocation unless another selected stage remains. Shared
POLICY_INTEGRATION.md governs checkpoints, review bounds, repair convergence and
typed identity. A stage-specific plan or requested audit is an objective output.

