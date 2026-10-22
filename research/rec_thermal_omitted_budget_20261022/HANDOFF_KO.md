# REC 누락 열과정 예산 재개 지점

## 현재 단위와 완료 범위

현재 연구 단위는 `research/rec_thermal_omitted_budget_20261022`, 로컬 branch는
`research/rec-thermal-omitted-budget-20261022`다. 기존 thermal8의 immutable
상태109점씩872개를 후처리한 과학 계산·16개 집중 테스트·독립 검토2건·그림
검토가 완료됐다. 새 ODE 및 기존 IVP 재실행은0회다.

현재 runtime identity:
`88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c`.
물려받은 thermal runtime identity:
`dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e`.
변경하지 않은 기존 thermal release:
`cdf7e04518bde936206054c33413ab2b1fc300c5`, tree
`503fa14793f385a1e235763818251c5d34987842`.

1. `REPORT_KO.md`, `THEORY_KO.md`, `FROZEN_CONTRACT.md`를 읽는다.
2. `results/budget_v1/RESULT.json`에서 source·output identity를 확인한다.
   `INPUTS.json`의8개 NPZ/receipt hashes와 이전 source lock을 재사용한다.
3. `REVIEW_PHYSICS_KO.md`, `REVIEW_IMPLEMENTATION_KO.md`,
   `evidence/PHYSICS_FIGURE_AUDIT.json`의 적용 범위를 읽는다.
4. 현재 그림은 `figures/v3`다. v1/v2는 실패·교정 이력이므로 채택하지 않는다.
5. `NEXT_UNIT_CONTRACT.md`의 Compton-first full63 coupling 계약으로 넘어간다.
   해당 미래 IVP는 이번 단위에서 실행되지 않았다.

## 과학 판단

네 기본 궤적의 actual-U hot Compton은 −2.576∼−2.592 eV/baryon으로, 기존
photo-primary 가열의 약30%다. 현재 직접 logT 강제항 적분 약−1.03을
새 ΔlnT나 온도 예측으로 해석하지 않는다. CI kinetic/binding은 내부 이동이고,
새 전자에 따른 particle 항이 존재한다. Planck 기준장과 실제 Bianchi 에너지
모노폴은 분리된 owner다. He I CE/metastable·Li CI/CE는 미공급이다.

physical HOLD, production NOT_APPROVED, global convergence NOT_RUN,
REI_activation=false, U5 CLOSED_HOLD_NOT_RESET을 유지한다. 이번 원문 분석은
추가 스펙트럼 구성이나 결합 모형의 불가능성을 주장하지 않는다.

## 실행과 증거 재사용

수치 후처리는 sibling donor와 thermal unit이 같은 `research` 디렉터리에 있으면
오프라인으로 실행할 수 있다. Python3.12.14와 `requirements.txt`의 실제 버전을
기록했다. 일반 재개에서는 결과를 읽고, 소스/입력이 변했거나 새 판별 질문이 있을
때만 아래 create-only 명령을 새 output 경로로 실행한다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -u code/postprocess_omitted.py --output results/budget_recheck
MPLCONFIGDIR=/tmp/rec_omitted_mplconfig PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 -u code/plot_budget.py --output figures/recheck
```

두 명령 모두 ODE를 풀지 않는다. 기존 `budget_v1`이나 `figures/v3`를 덮어쓰지
않는다. 독립 검산 스크립트는 `evidence/independent_physics`에 보존돼 있다.
기존126+8 IVP나 이전 테스트 전체를 단순 재승인 목적으로 반복하지 않는다.

## 로컬·원격 전달 상태 읽기

사용자는 이번 턴에서 백업·게시와 다음 연구 루프 권한을 명시적으로 승인했다.
이전 thermal archive 안의 차단 기록은 그 이전 시점의 기록이다. 현재 전달
상태는 `DELIVERY_STATUS.json`과 그 파일이 가리키는 provider receipt를 따른다.
최종 ZIP 자체의 SHA·원격 업로드 확인은 자기참조를 피하기 위해 ZIP 밖의
integrity/publication sidecar에 기록한다. ZIP 안의 pre-delivery checkpoint를
나중의 실제 provider 응답과 혼동하지 않는다.

GitHub 앱의 commit 생성은 원래 로컬 author/time 헤더를 보존하는 기능이 없으므로
게시 commit SHA가 로컬 SHA와 달라질 수 있다. 그때는 **root tree의 정확한 일치**와
local↔remote 매핑을 확인한다. 로컬 commit history는 Git bundle에도 보존한다.
Git push 자체의 인증 실패와 연결 도구 목록 갱신 중 발생한 요청 실패는 환경
문제이며 사용자의 승인 부족으로 분류하지 않는다.

새 작업에 앞서 최근 REC/REI head가 현재 intake 이후 바뀌었는지 필요한 범위만
확인한다. 이번 실제 intake의 REI219는 a7bff87…, REI220은8be7533…이며 이를
근거로 REI coupled production이나 U5를 활성화하지 않았다.
