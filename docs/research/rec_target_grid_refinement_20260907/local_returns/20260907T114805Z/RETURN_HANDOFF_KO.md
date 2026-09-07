# 고정 reference measure target-grid 첫 약형 진단 반환

STATUS=COMPLETED_BOUNDED_WEAK_DIAGNOSTIC_WITH_RESULT_AND_VISUAL_REVIEW
TASK=REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE
SLICE=FIRST_WEAK_CONSISTENCY_PROBE
REPOSITORY=cosmosapjw-quantum/rec_bianchi
RESULT_BRANCH=results/rec-grid-weak-20260907T114805Z

**첨부문에 고정된 균일 측도판의 최초 실행을 완료했다.** 실제 numerical process
exit 0, 288개 moment 행, 8개 독립 discrete-primal/JVP 비교, 6개 표/상태 직접
reference를 얻었다. 수치 실행은 한 번이며 원래 PR79 7개/84방향 및 보충
4개/16방향은 재실행하지 않았다. 288행은 독립 unittest 288개가 아니다.

## 계약 선택과 갱신된 전역 하네스

사용자의 최신 첨부 prompt SHA256은
`a7d7b8ec271fea05e24db474a9dd4ea00b9752892170716fb5cf2c17ad45d6bf`다. 기준은 수용된 `59dafbd34bc21b1b885c716b7b8cc899636bbd60`
/tree `c0d6a862567e111cfe92a6fd5a3c30051180e38e`다. 그 위에서 첨부 Python block을
바이트 그대로 저장했다. [원래 실행 source](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/4a16d7c0f79408e08c8be57923881cd4120c012a/docs/research/rec_target_grid_refinement_20260907/refinement_probe.py)는 후속 표시 수리에서도 변경하지 않았다.

원격 조사 중 `research/rec-target-grid-refinement-20260907-r1` /
`dcea5acec4bf74d7687f57c3680f12ab6997e8aa`의 별도 후속 초안을 확인했다.
그 초안은 `8(1+u^2)du`, 576행 등으로 첨부 계약과 다르고 당시 미실행이었다.
이를 현재 첨부문에 조용히 대입하지 않았다. **이번 결과를 그 후속 비균일
측도판의 실행·수용 결과로 사용하면 안 된다.** 해당 branch는 수정하지 않았다.

현재 설치된 전역 policy authority는
`02ceeb6dc2e0568cefede48b6f9928799e61ac74`다. AGENTS/global execution/local router/
mixed worker/device 문서를 읽고 적용했다. 별도 CODEX_ONLY/BUDGET_FIRST를
요청하거나 동결하지 않았으므로 기본 MIXED 범위다. 제공된 exact code를
추출하는 결정적 작업에는 새 생성 모델이 필요 없어서 Host가 직접 저장·실행했다.
수학/범위/최종 검증 판단은 Host가 유지하고, 별도 최종 independent read-only
review 1회를 수행했다. 예방적 구현 guidance, 새 local inference, runtime smoke,
모델 설치/상주 변경은 하지 않았다. 비용 절감이나 토큰 절감은 측정하지 않았다.

## 실행·표시·게시 identity

| 역할 | Commit | Tree |
|---|---|---|
| 실제 수치 실행 및 최초 렌더 | 4a16d7c0f79408e08c8be57923881cd4120c012a | 603966984d089f8fb402e1d04419a5b5043c2de8 |
| 최종 저장자료 후처리·표시 | 14fb29000e8014c1db9f0c08d068cf92f5676ed4 | ad8f14bddb3a54cb8a3c571f4abec6360a303268 |
| 원격 확인한 source/evidence 게시 | 7aa39474ddffab5359f95fdea56c4e3ff54ac216 | 52bed4b4b3bd5ad069dca4d75307daa4390734f8 |

이 반환문은 evidence 게시의 문서 child다. 최종 반환문 게시 commit/tree는
최종 응답과 이 문서의 immutable URL에 별도로 고정한다. 문서 child를 수치
실행 commit으로 부르지 않는다. 원격 evidence commit/tree 및 source/evidence
51개 blob을 대조했고, PROCESS/RESULT/원본 CSV wrapper/후처리 receipt/summary
5개 파일을 Contents API로 재수령해 실제 바이트 일치를 확인했다.
[REMOTE_EVIDENCE_READBACK.json](REMOTE_EVIDENCE_READBACK.json)에 기록했다.

Python은 `/home/cosmosapjw/cosmo_lab/.venv/bin/python`의 3.12.3이다.
NumPy 2.3.5, SciPy 1.18.0, SymPy 1.14.0, mpmath 1.3.0, Matplotlib 3.11.0을
설치/업그레이드 없이 사용했다. [SYNTAX_ENVIRONMENT.log](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/SYNTAX_ENVIRONMENT.log)는
실제 module 경로, 기존 paired/COM import 경로와 syntax PASS를 보존한다.
수치 실행은 UTC 2026-09-07 11:48:59.701950–11:49:08.131706, 약8.43초다.

[PROCESS.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/PROCESS.json)의 실제 argv/cwd/exit와
[RESULT.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/payload/RESULT.json)의 script exit를 각각 확인했다.
stdout/stderr는 같은 디렉터리에 그대로 있다. 원본 raw 실행 경로는
`/home/cosmosapjw/research_runs/rec_grid_weak_ki08hq1_`다.

## 약형 결과와 보존·미분

N=`5,9,17,33,65,129`, 구간 `[2^-30,1-2^-30]`,
`dmu=20/(1-2eps) du m^-3`, node measure는 hat 적분이다.
총 measure 20, 첫 measure moment 10, 양의 node masses를 확인했다.
이 새 제조 측도는 이전 5-node의 `(2,4,8,4,2)`도 물리 density-of-states도 아니다.

동일 연속 chi와 perturbation, 동일 원자 population을 사용해 방출·흡수·affine
상세균형 대조를 각각 두 표/두 읽기/여섯 grid/네 시험함수 `1,u,u^2,u^4`에 적용했다.
원본 paired/COM API의 count 형태, `mu/nH*(dC-C*dnH/nH)` density 연쇄법칙,
수·에너지 장부, signed read/scatter/cross 분해를 모두 통과했다.

독립 고정밀 비교의 최대 scaled primal 오차는 `1.0255644258692255e-17`,
JVP 오차는 `5.135036607930968e-18`이다. 고정 허용치는
`4096*epsilon = 9.094947017729282e-13`; 80/120 precision `<1e-60` 및
h=`2^-32`/`2^-36` 중앙차분 차이 `<1e-16`를 바꾸지 않았다.
[ORACLE_CHECKS.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/payload/ORACLE_CHECKS.json) 참조.
rate reference는 고정밀로 검산하고, 저장된 moment/reference 벡터와 행렬곱은
binary64다. 전체 결과를 120자리 구현 정확도라고 부르지 않는다.

저장된 CSV에서 재합산한 분해 잔차는 moment `3.435904447242344e-16`,
JVP `3.677613769070831e-16` s^-1다. 첨부 유리수 대조도 별도 정확 산술로
`9/16 - 17/32 = 1/32`임을 확인했다. 이는 이전 검사의 replay가 아니다.
[SAVED_ANALYSIS.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/SAVED_ANALYSIS.json)에 있다.

chi의 조건부 primal weak bound는 모든 해당 행에서 통과했다. curved 상태의
최대 `abs(error)/bound`는 `0.04672407707618724`다. 적용 조건은 양의 C2 chi,
고정 유한 atomic 표/원자 population, 선형-energy interpolation이다.
log-control에는 이 bound를 적용하지 않았다. JVP는 분해와 독립 비교·관측오차를
확인한 것이며, 이번 코드가 별도 analytic JVP envelope를 증명한 것은 아니다.

## 실제 오차 감소와 해석 한계

아래는 그림과 같은 curved-emission / psi=u² 사례의 값이다.
전체 상태·함수·grid별 값은 [MOMENTS.csv](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/payload/MOMENTS.csv),
모든 구간 기울기는 [LOCAL_SLOPES.csv](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/LOCAL_SLOPES.csv)에 있다.

| 표 / 읽기 | N=5 moment 오차 | N=129 moment 오차 | N=5 JVP 오차 | N=129 JVP 오차 |
|---|---:|---:|---:|---:|
| base / chi | 7.490007559201206e-3 | 1.7786672119601832e-6 | 8.046298739792401e-3 | 2.168260833407265e-6 |
| base / log control | 2.2446960413030126e-2 | 7.966116807256451e-6 | 7.5852710339372464e-3 | 9.11962961658297e-6 |
| hires / chi | 7.488519581519193e-3 | 7.12058332696941e-6 | 8.044544515979274e-3 | 7.572710468473076e-6 |
| hires / log control | 2.2439281009885514e-2 | 1.781870346195813e-5 | 7.579428937099036e-3 | 5.489880663317459e-6 |

hires/chi의 인접 구간 moment 기울기는 약
`2.009,2.009,1.998,1.945,2.078`, JVP는 `2.020,2.012,2.000,1.950,2.070`이다.
이 유한 사례는 조건부 2차 감소와 정합적이다. base/chi의 마지막 기울기는
moment `4.480`, JVP `4.260`으로 앞 구간과 다르므로 일괄 2차라고 요약하지 않는다.

log-control JVP의 base 기울기는
`1.636,2.087,2.328,2.707,0.942`, hires는
`1.634,2.074,2.262,2.329,2.132`다. 예상 차수를 강제하거나 마지막 구간을 제거하지 않았다.
예를 들어 base/log-control JVP는 N=65에서 읽기항 `-5.992509953839209e-5`와
분배항 `+4.240673491723613e-5`, N=129에서 `-1.1299393594853348e-5`와
`+2.180071544843758e-6`이 합쳐진다. signed 상쇄와 그 상대 크기가 달라지므로
총 절댓값 기울기를 단일 단계의 보편 차수로 볼 수 없다. 원인을 그 하나로
완전히 규명했다고 주장하지 않는다.

chi affine_balance의 primal은 최대 약 `7.18e-17` 차이로 반올림 수준이다.
그 영역의 raw slope는 수렴 차수로 해석하지 않는다. 이 상세균형 상태에서도
주어진 perturbation은 상세균형 접방향으로 한정되지 않아 JVP는 일반적으로
0이 아니다. 로그 대조의 양수/음수 entropy 관측을 물리 엔트로피 정리로
확장하지 않는다.

## Atomic 표 차이와 measure 비식별성

[DIRECT_REFERENCES.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/payload/DIRECT_REFERENCES.json)은
각 atomic 표 자신의 bin 에너지에서 같은 연속 상태를 직접 읽은 6개 기준이다.
[TABLE_REFERENCE_CONTRAST.csv](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/TABLE_REFERENCE_CONTRAST.csv)는
두 표의 차이 12개를 별도로 보존한다. curved emission psi=u²에서
base moment=`0.26486758044716874`, hires=`0.26487225732177133`,
hires-base=`4.676874602593806e-6` s^-1다. 해당 JVP 차이는
`3.2216281048713657e-6` s^-1다. 이는 target-grid 오차나 atomic truth 오차가 아니다.

N=17 curved-emission의 두 표·두 읽기에서 measure를 2배로 한 음성대조는
`2*C2=C`와 동일 weak moment를 고정 허용치에서 통과했다. 값별 residual은
초안이 별도로 저장하지 않았으므로 없는 숫자를 만들지 않는다. 근거는
원본 해당 assert와 실제 exit0이다. moment의 mu 소거 자체가 measure 물리
권위를 인증하지 못한다는 한계를 드러낸다.

[PEAK_C.csv](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/PEAK_C.csv)는 grid마다 달라지는 점별
occupation action의 peak를 별도로 둔다. 예를 들어 base/chi curved emission은
N=65의 `0.4186654499026522`에서 N=129의 `0.8373567072979486`으로 커지면서도
weak moment 오차는 감소했다. 이를 강한 수렴의 실패나 물리적 발산으로
분류하지 않는다. 유한 atomic photon packet source를 더 작은 hat mass에
분배하는 관측이며, atomic continuum 또는 시간 적분 극한은 실험하지 않았다.

## 그림의 실제 검토와 보존한 표시 결함

최초 4개 PNG를 모두 열었다. 자동 symlog 축이 음의 절대오차 영역까지
넓어져 데이터가 상단에 눌려 보이는 표시 결함이 있었다. 원본을 그대로
`evidence/attempt01/payload/`에 보존하고, 새 `postprocess_saved.py`가 저장 CSV만
소비하도록 했다. 첫 수정의 90mm에서 0과 1e-16 tick이 가까워지는 문제도
원본과 함께 보존하고, 겹치는 tick만 제거했다. symlog threshold는 변경하지 않았다.

최종 4개 그림:

- [Moment 90mm](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/absolute_error_90mm.png)
- [Moment 180mm](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/absolute_error_180mm.png)
- [JVP 90mm](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/absolute_jvp_error_90mm.png)
- [JVP 180mm](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/absolute_jvp_error_180mm.png)

네 장을 실제 열어 축·범례·잘림·겹침·가독성을 확인했다. 위 패널은 실제
양수 오차의 log detail, 아래는 실제0을 포함한 symlog 전체 범위다.
`|error|<=1e-16 s^-1` 선형 구간을 명시하고 floor로 데이터를 바꾸지 않았다.
서로 가까운 base/hires 곡선의 겹침은 CSV와 일치하며 marker/선형태로 표시한다.
[VISUAL_REVIEW.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/VISUAL_REVIEW.json)과
[POSTPROCESS_RECEIPT.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/postprocess/attempt02/POSTPROCESS_RECEIPT.json)을 구분한다.
raw RESULT/renderer의 당시 NOT_PERFORMED 필드를 소급 수정하지 않았다.

최초 numerical/syntax/import process 실패는 없다. 최초 결함은 위 표시
관측이며 numerical source는 수리하지 않았다. saved-output 후처리 2회만
추가했다. [SOURCE_CHANGES.diff](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/SOURCE_CHANGES.diff)는 후처리 추가 및 tick
수리 diff를 담고, 수치 probe가 변경되지 않았음을 Git으로도 확인할 수 있다.

## 원본 포장·독립 검토·미완료

원본 MOMENTS.csv는 CRLF이므로 가역 [MOMENTS.csv.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/evidence/attempt01/payload/MOMENTS.csv.json)에
정확한 UTF-8 문자열과 SHA256/byte 수를 보존했다. `content.encode('utf-8')`로
원본 바이트가 완전히 복원됨을 검증했다. 나란한 CSV는 LF 표시 사본이며,
모든 필드가 원본과 같은지 확인했다. 나머지 PROCESS/RESULT/로그/PNG는 원본
바이트 그대로다. [RAW_ENCODING.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/RAW_ENCODING.json)은 39개 raw 파일의
원본/저장 관계를 명시한다. raw 파일을 trim하거나 수치 재실행으로 바꾸지 않았다.
새 공백 gate 실패는 없으며 게시 diff check는 exit0이다.

[독립 read-only review](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/INDEPENDENT_REVIEW.md)는 1회 scoped PASS다.
FAIL은 없고, positive C2/fixed table 및 physical admission 등의 명시적 claim
한계를 남겼다. reviewer는 수치/그림을 재실행하지 않았고 Host의 시각검토와
구분한다. [VALIDATION_MATRIX.md](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7aa39474ddffab5359f95fdea56c4e3ff54ac216/docs/research/rec_target_grid_refinement_20260907/local_returns/20260907T114805Z/VALIDATION_MATRIX.md) 참조.

변경은 새 연구 디렉터리 내부뿐이다. 기존 src/tests/archive/이전 연구/
evidence/workflows와 dirty root를 보존했다. 자기 branch에 `[skip ci]` commit을
non-force 게시했으며 Actions 실행·조회·다운로드·dispatch, merge/ready,
force-push, 새 PR/Atlassian 쓰기는 하지 않았다.

NO_PASS_REC_PHYSICAL_SPLIT
physical_source_authenticated=false
provider_admitted=false

실제 photon measure/분배 authority, atomic continuum truth, 적외선 끝점까지의
균일 bound, 실제 재결합 시간진화, BASS 연결과 전체 solver 수렴은 미검증이다.
원래 PR79 raw artifact 회수도 이번 단계에서 하지 않았다. 현재 결과의
주 대화 수용과 후속 확대는 별도 판단이며, 이 실행에서 grid를 늘리거나
다른 연구판으로 넘어가지 않았다.
