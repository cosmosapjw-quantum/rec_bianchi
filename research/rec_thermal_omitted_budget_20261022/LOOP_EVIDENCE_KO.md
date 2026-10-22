# 이론 R1–R10 / 구현 C1–C10 근거

Workflow1.0.0, approval design0.2, physmath-research-loop 적용.
상태는 실제 수행·재사용·미실행을 구분한다. 단계는 근거의 논리적 의존관계이며
서로 독립인 원문 분석·구현·전달 준비는 병렬 수행했다.

| 이론 단계 | 실제 작업과 근거 | 판정 |
|---|---|---|
| R1 연구 위치·계약 | 이전 thermal release·8개 trajectory·물리 범위 고정; FROZEN_CONTRACT | 완료 |
| R2 근거·재사용 | REC119/REI219/220 실제 최신 head intake; HG97·SS2000 원문; 기존126+8 IVP 재사용 | 완료 |
| R3 주장·전제 정렬 | actual-U hot/Planck reference, CI internal transfer, isotope equality, source domain 분리 | 완료 |
| R4 가설·표현 탐색 | Compton/CI/CE 우선순위 비교; 같은 N,U와 다른 recoil moment의 구성적 반례 | 완료 |
| R5 구성적 유도 | THEORY의 thermal·binding·particle 장부, angular average·UV moment·fit SI 변환 | 완료 |
| R6 독립 검증 | 실제 Wolfram symbolic identity/35자리값; 별도 원시NPZ 계산과 runtime 대조 | 완료 |
| R7 판별 검증 | 전체872점; 각 fit mask, quadrature109/55/Simpson, 기존 refined·RR대안 민감도 | 완료 |
| R8 결과 판정 | Compton 우선; fixed-path forcing을 새온도/오차상한으로 확대하지 않음 | 완료 |
| R9 정식 결과·코딩 연결 | provider+driver, REPORT, source-to-code map, NEXT_UNIT_CONTRACT | 완료 |
| R10 종료·재개 | 원자료·검토·그림·handoff·delivery receipts와 복구 가능한 archive | 과학 완료; 전달 상태는 별도 receipt |

| 구현 단계 | 실제 작업과 근거 | 판정 |
|---|---|---|
| C1 목표·baseline | immutable thermal8 runtime/NPZ/RESULT로 baseline 고정 | 완료 |
| C2 식–데이터–코드 | H/He source JSON, native21, actual photon monopole4, old THOMSON=σTc 소유권 | 완료 |
| C3 수치 설계 | strict domain 기본값+명시 continuation, 양의 trapezoid, 모든 integrand/mask 저장 | 완료 |
| C4 실행 DAG·자원 | DAG.json; 8×109 후처리, ODE0, numerical thread1, create-only outputs | 완료 |
| C5 구현 | Compton/collision providers와 postprocess; Stage B runtime identity 고정 | 완료 |
| C6 구현 검증 | Compton6+collision10 실제 테스트, 의미 있는 단위/원자/복사/입자 검증 | 완료 |
| C7 과학 검증 | 원시NPZ 독립 계산, 보존식, source-domain/부호/크기; physics review | 완료 |
| C8 수치·재현성 | retained-grid 비교·기존 궤적 비교, RESULTS·NPZ·source hashes, plot source arrays | 완료 |
| C9 독립 검토 | root 구현에 대한 physics 및 implementation review; 저자 역할 공개; 실제 PNG 검토 | 완료 |
| C10 판정·인계 | COMPLETE_SCOPED_FIXED_PATH_BUDGET, 다음 full63 계약, HANDOFF | 과학 완료; 전달 상태는 별도 receipt |

## 실행 및 수정의 분류

- **새 물리 결과:** Compton 직접 소스가 photo heat의 약30%; 현재 경로에서 공급된
  CI/CE는 더 작음. 총 물리 모형 승인이나 미공급 채널의 무시 가능성 증명은 아님.
- **계산 검증:** 첫 postprocess 실행 성공. CI 독립 gradient/particle 잔차는
  scaled1e−13 gate보다 작고, raw-NPZ 별도 계산과 약1e−14 수준에서 일치.
- **구현 교정:** 첫 실행 전에 CI 검증 분자를 구성상0 대신 독립 gradient residual로
  바꾸고, Planck 기준 저장 U를 그 식의 자체 radiation constant로 맞춤.
- **그림 교정:** v1 제목 겹침, v2 PNG02 truncation을 보존. v3 PNG 검증·시각 확인 PASS.
  과학 runtime과 원본 적분은 다시 실행하지 않음.
- **환경 처리:** Git CLI 인증 수단 부재, GitHub 도구 catalog 갱신 중 응답 실패를
  사용자 권한 부족이나 과학 실패와 구별. sparse checkout에서 빠진 기존 unit을
  다시 펼친 뒤8개 NPZ identity 확인. 기존 파일 내용 변경 없음.
- **미실행:** 새 full63 IVP, fullCMB spectral closure, REI coupled activation,
  production 승인, global convergence. 다음 단위 계약은 제안 상태.

기존 원문·명령 결과·입력/출력·검토를 다시 만들기 위한 반복 검사는 수행하지
않았다. 새 구현이 바뀌거나 새 질문을 판별할 때만 해당 dependency 범위의
검증을 실행한다. 라이브러리·논문 전수 탐색이나 지난 채팅 전문 전체의 열람을
주장하지 않는다. strong no-go는 제출하지 않았다.
