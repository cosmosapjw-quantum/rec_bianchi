# 다음 미완료 단계: C3 설계 선택

상태: **HANDOFF_ONLY — C3_NOT_EXECUTED**.

현재 C2에서 수식–데이터–코드 대응과 512점 baseline profile을 수행했다.
다음 일반적인 재개 요청의 단계 선택은 C3다. 한 단계 재개를 전체 cycle
또는 C4 이후 구현·benchmark의 자동 승인으로 확대하지 않는다. 사용자가
구체적인 단계 범위를 선택하면 그 범위를 따른다.

## 사용해야 할 완료 근거

- `C2_SCOPE.md`, `FORMULA_CODE_MAP_KO.md`, `REPORT_KO.md`.
- `evidence/profile/attempt_001/INPUT_MANIFEST.json`과 `CORPUS_MANIFEST.json`.
- 상태당 geometry 7회, number network 3회, thermal source 2회인 실제 호출 수.
- 열원 38.9614%, geometry 24.2282%, 원자망 19.9326%인 관측 비용 분포.
- 순서 검사에서 확인된 실행 시간의 큰 변동: 안정된 branch별 속도 차이는 미확립.
- 독립 검토의 실제 판정과 해당 source/result binding.

## C3가 해결할 설계 질문

같은 x·full63 입력과 동일 model/branch에서만 유효한 명시적 per-state
context를 어떤 최소 API로 제공해야, 기존 진단 소비자들이 primitive 결과를
공유하면서 두 gas-energy 합계의 독립성과 모든 source mask를 보존하는가?

후보는 measured 7/3/2 중복을 먼저 대상으로 삼되, dense513 reuse는 별도
provenance·quadrature 경계로 취급한다. UV moment는 이미 한 번 준비되므로
그 부분을 새 병목으로 가정하지 않는다. approximate cache key, 전역 last-state,
branch를 생략한 key, energy residual의 순환 정의는 계약에 맞지 않는다.

설계 출력에는 입력·출력·수명·owner, 같은 입력/중첩 격자의 동등성 기준,
상속된 gates와 앞으로 실행할 최소 비교를 명시해야 한다. 후보 API의 최종
선택, source 변경, 전체 same-input campaign, paired speedup은 아직 없다.

## 실행 제약과 이후 검증 위험

- 새 IVP 0, 기존 물리 RHS/Jacobian·rates·scales·tolerances 불변.
- 기존 source/results는 immutable; 새 단위 경로에서만 작업.
- 현재 evidence의 시간·입력·도구 결과를 먼저 재사용하고 완료한 profile을
  자동으로 반복하지 않는다.
- 실행 시간 변동을 고려해 향후 benchmark는 baseline/candidate의 교대 paired
  순서와 원시 반복값을 남겨야 한다. 고정된 2배 가속 목표를 임의로 추가하지 않는다.
- source/context ownership과 physics status를 별도로 기록한다.
- 후속 stage의 예산은 현재 cumulative budget receipt와 기존 600 s 계약을
  읽고 남은 범위를 명시한 뒤 설정한다.

현재 scientific status: physical HOLD; production NOT_APPROVED;
global convergence NOT_RUN; REI false; U5 CLOSED.
