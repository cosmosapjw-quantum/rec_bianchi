# R1–R10 / C1–C10 실제 수행 대응

이 기록은 `physmath-research-loop`의 단계명을 현재 단위의 실제 증거에 대응시킨다. 단계를 새 문서나 실행으로 중복하지 않는다. 주장·검사·실행·전달 상태를 구분한다.

## 이론 루프

| 단계 | 실제 작업과 근거 | 상태 |
|---|---|---|
| R1 연구 위치·계약 | REC119 latest handoff/parent 확인; thermal moment와 full63 finite restart를 `FROZEN_CONTRACT.md`로 고정 | complete_scoped |
| R2 근거·재사용 | donor49 source lock, 기존126개 NPZ/receipt 검증; Mao 원표와 Verner/Badnell/Li 원전 연결 | complete_scoped |
| R3 주장·전제 정렬 | Maxwellian·공통T·고정 microscopic kernel·zero n/T·case-A escape·test-fluid·초기 prefix를 `THEORY_KO.md`에서 분리 | complete_scoped |
| R4 가설·표현 탐색 | fit derivative moment와 Mao-factor hybrid를 구성·비교하고 별도 source sensitivity로 채택 | complete_scoped |
| R5 구성적 유도 | 입자수 항이 있는 온도식, RR/DR moment, 결합/열/escape 원장, per-baryon expansion work, analytic63 Jacobian 유도 | derived |
| R6 독립 검증 | Wolfram 항등식, independent kernel quadrature, PHYS-MATH pre-run/result review; PM1–PM5 수정 | pass_scoped |
| R7 판별 검증 | 원표114점, mutation checks, 기존126 budget, 새8의 source/refinement 비교를 실제 수행 | completed |
| R8 결과 판정 | 선택된 모형의 열량·온도·이온화 응답 채택; stress source 신호와 전체 물리 정확도는 미확립; strong no-go 채택 없음 | scoped_decision |
| R9 정식 결과·코딩 연결 | THEORY 식1–22와 runtime4모듈·데이터 행·단위·정규화 대응, `REPORT_KO.md` 실제 결과 | complete_scoped |
| R10 종료·재개 | hash-bound source/results, local commits/archives, handoff와 다음 omitted-process budget 정의 | local_complete; external_delivery_blocked |

## 코딩 루프

| 단계 | 실제 작업과 근거 | 상태 |
|---|---|---|
| C1 목표·baseline | PR119 ad93fa1c, native62 baseline, 동일 UV/수반응률·기하, runtime Python/C++ 실제 probe | complete_scoped |
| C2 식–데이터–코드 | atomic rates→moments→ThermalSources→ThermalSystem RHS/J→runner→saved NPZ 경로를 추적 | complete_scoped |
| C3 수치 설계 | logT, native isotope scaling, BDF/analytic J, exact restart,100..1e6K domain, 고정 refinement gates | complete_scoped |
| C4 실행 DAG·자원 | 독립 source/implementation/REI intake 분담;8설정 serial,1BLAS thread,240s/1200s cap | complete_scoped |
| C5 구현 | runtime4모듈, saved126 postprocessor, analysis/plotter를 실제 입력에 연결 | implemented |
| C6 구현 검증 |9+10 고유 test methods,63column/24JVP,114sourcepoints, diagnostics regression; 실패 보존 및 최소 수정 | implementation_verified |
| C7 과학 검증 | source/caloric identities, zero n/T·baryon·isotope·charge·geometry·signed-vector sampled gates; 독립872상태 재구성 | pass_scoped |
| C8 수치·재현성 | 두 tolerance pair와 두 source pair; 실제8IVP71.976452s; dense evidence 한계와109point coarse check를 분리 | pass_scoped_with_evidence_limitations |
| C9 독립 검토 | PHYS_MATH_RESULTS_REVIEW와 IMPLEMENTATION_RESULTS_REVIEW, plot author와 root의 직접 시각 검사, report 수치 대조 | complete_scoped |
| C10 판정·인계 | 코드·원표·기존 입력·새 결과·그림·receipt를 local archive로 준비; external push 거절과 미게시 상태 명시 | local_complete; external_delivery_blocked |

## 실제 실패·교정과 영향

| 분류 | 관찰된 문제 | 조치와 유지된 근거 |
|---|---|---|
| 구현/검사 domain | full63 central FD가 legacy u=0 경계를 넘음 | 해당 column만4차 forward stencil; prior_runs 보존, 물리식·tolerance 유지 |
| 구현/진단 | parent diagnostics의 placeholder Tdx=0이 동적 열량을 잘못 표시할 수 있었음 | 실행 전 override; 독립 dT/dx balance 회귀검사0잔차 |
| 구현/실행 계약 | 초기 runner의 범용 code glob, donor RESULT/config identity 누락, dense postprocess deadline·geometry gates 누락 | 실행 전에 runtime dependency4개로 제한, receipt hash·deadline·계승 gate 보완; 최종 SHA로 독립 review |
| 구현/산출물 metadata | 열린 stdout 로그가 빈 hash로 figure manifest에 들어감 | 원본metadata/그림 보존; 명시적 output목록으로 수정;18hash binding PASS, 과학값 불변 |
| 수치/산술 비교 | independent reduction의 memory order·곱셈 결합으로 약1e-16 scalar 차이10개 | 원래 array order와 산술로 재현; gate 변경 없이 해소 |
| 증거 보존 한계 | dense513/1025 표본·보간자 미저장 | runner-reported integral과 독립 endpoint/109node 검사 분리; 다음 실행의 저장 의무로 연결 |
| 환경 | 최초 shell Git 읽기가 proxy 연결에 실패 | 승인된 read-only 접근으로 source intake 완료; 과학적 실패로 분류하지 않음 |
| 권한·정책 | 새 branch GitHub push가 자동 승인 검토에서 거절됨 | API 우회 없음; local 작업·검토·archive 완료 후 명시적 게시 승인 요청 |

닫힌 검토와 결과는 identity가 같으면 재사용한다. strong no-go, global convergence, 모든 물리 과정의 작음, remote upload 성공 중 어느 것도 새로 채택하지 않았다. R10/C10의 미완료 외부 전달은 과학 계산 실패와 구분한다.
