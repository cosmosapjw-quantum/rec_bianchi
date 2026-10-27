# 현재 확보한 결과와 다음 실행 경계

현재 정본은87개 노드다. 기존40개 계약·17개 저장소 간 조건부 연결·7개 권위 원문과31개 반환 파일을 그대로 보존했다. 나머지47개는 새로 등록한 기존 결과, 확장 계약, 이번 유한 compiler 결과 및 준비된 HD 어댑터를 구분한다. 노드 수나 국소 R/C 단계 수는 전체 물리 모형의 완료율이 아니다. 전체 물리 완료율은 null, L4 준비는 false다.

이번에 실제로 더한 실행 결과는 REI-CHEM-LEDGER-01의 한 번의 유한 검사다.12개 합성 화학 event와1개 핵 bookkeeping event를 포함한249개 정확 산술/guard 검사가 통과했고, 원문·raw·실제 PNG를 새 독립 reviewer가 읽어 유한 isotope/molecule event interface를 PASS_SCOPED로 승인했다. 관찰된 scientific child CPU는0.088983s, wall은0.092082s다. 저장한 결과의 SVG/PNG까지 알려진 측정 합계는CPU0.352458s/wall0.362115s이며, 실패한 선택적 CairoSVG import의 추가 비용은 UNMEASURED_NOT_ZERO로 보존했다. 정확한 모든 process의 누적 cap 준수는 주장하지 않는다. 새 IVP나 과거 suite 재실행은 없다. 이 결과는 경험적 rate, 핵Q, 전체 분자망 또는 우주론 해를 승인하지 않는다.

두 번째 이론 결과는 REC-H5-DEFECT-BOUND01이다. 실제 source-matched defect와 동일 tube의 stability/Lipschitz 정보를 endpoint 오차, 보간 곡률 오차, 기존 frozen response 출력 경계로 연결하는 조건부 유도가 PASS_DERIVED_SCOPED를 받았다. 물리 defect·tube·curvature 입력, epsilon과 실제 history reference는 여전히 필요하다. 구현과 실행은 NOT_RUN이며 H5의 물리 완료를 뜻하지 않는다.

| 저장소 | 원 작성자와 검토자가 확인한 현재 범위 | 다음 구체적 경계 |
|---|---|---|
| WU088_HH | 원자 공급자 결과와 PHYS91의 scoped 결과를 재사용하고, 이번 유한 event/compiler의 canonical lead를 맡는다. | 구성 대상의 isotope/isomer·전하·상태·분자·음이온 registry와 실제 source/branch/에너지·불확실성 입력을 qualified row로 공급한다. 합성 fixture를 물리 rate로 바꾸지 않는다. |
| rec_bianchi | LINE02, history/response/PB01 등의 유한 결과를 재사용한다. H5 조건부 유도는 승인됐고 물리 epsilon은 미정이다. | 준비된 REC-HD-ADAPTER의 pinned HD 준위/line/collider 파서를 별도 예산 후 구현한다. H5/H6에는 실제 history·geometry·source 및 domain bound를 결합한다. |
| BASS_HE | inclusive PSD 및 DDCS/CCC/TDCS/유한질량 source-window 결과는 각 유한 범위로 재사용한다. HE101의 C8 export와 물리 full-joint provider는 열린 상태다. | 실제 calibrated differential/angular/finite-mass 충돌 공급자를 결합한다. 소진한 export 예산을 새 노드 이름으로 재시도하지 않는다. |
| bass_cr | source-frame·atomic coverage·stopping 계열의 현재 유한 반환값을 재사용하며 provider overlap/에너지 partition을 구분한다. | source-qualified He4 ground-state RR 소비 계약과 외부 photon/electron/baryon distribution·cascade·stopping을 단일 event owner 아래 결합한다. |
| bass | G1B와 유한 B3 하위 결과를 재사용한다. B3f의 인증/비인증 영역을 모두 남기며 실제 입력 오차와 cohort/history는 별도다. | B3g actual cohort, B3h finite absorption을 공급한 뒤 B3i geometry 결합으로 진행한다. G1C 오차 운반은 선언된 domain 안에서 따로 진행한다. |
| vigilode | native physical norm과 D1–D5 연구 gateway/domain/effect 결과를 재사용한다. 실제 모델 Jacobian과 dense-domain 인증을 혼동하지 않는다. | V6 actual physical RHS/Jacobian/domain, 선택한 recovery 의미에 필요한 V7, V8 whole-domain 공급자를 실제 client에 결합한다. |
| rei_bianchi | L0와 finite HI 하위 결과는 각 승인 범위로 남고 L1 actual history, L2 beta/daughter/stopping, L3 물리 transport, L4/L5 결합·관측량은 남아 있다. | 고정 comoving reference 또는 명시적 reference-source quotient를 택한 시나리오를 먼저 동결하고, 선택한 event·opacity·source/absorber만 qualified interface로 조립한다. |

상태와 다음 경계의 근거는 `authority/atomic/AUTHORITY_AUDIT_KO.md`, `authority/thermal/AUDIT_AND_SCOPE_KO.md`, `authority/numerics/THEORY_AND_PR_PLANS.md`, `authority/rei/AUDIT_KO.md` 및 각 원 TASK_ASSIGNMENT다. 계획의 독립 검토는 `PLAN_REVIEW_ATOMIC.md`, `PLAN_REVIEW_NUMERICS.md`, H5 검토는 `REC_H5_INDEPENDENT_REVIEW.md`, compiler의 정확한 최종 검토는 `review_compiler/FINAL_C9_REVIEW.json`이다. 이 파일들은 모두 `authority/` 아래 보존했다.

소스 조사 범위와 한계는 `authority/SOURCE_COVERAGE.json`,12개 molecular resource의 관계·포맷·단위·지원 영역·미검증 부분은 `authority/molecular/data_reuse_registry.json`에 있다. 논문 전체 본문, raw 개인 대화, 검색 payload와 무관한 계정 inventory는 전달물에 포함하지 않았다. pinned HD fixture와 이미 확보한 scalar 참고값은 새 network/adapter 실행의 증거가 아니다.

PR219 bootstrap의 현재 관찰값은 `authority/rei/PR219_BOOTSTRAP_REUSE_CLARIFICATION.json`에 별도로 보존했다. 현재 head는 `6a12f3865d9ea427c1391c41caed8bb7cb7ec00d`, payload는 `61e08967832363b611a8e5ba4167ba7b06c06b6b`이다. 앞선 소스의 저장한14개 검사와 최종 소스의 변경 budget-path5개 검사, 독립 PASS_SCOPED_BOOTSTRAP_ORCHESTRATION이 있으므로 옛13개 summary 오류는 scoped bootstrap 안에서 이미 대체됐으며 미해결 수리로 남기지 않는다. 새83-case 재현은 NOT_RUN, 옛83개는 재계산 없이 재사용했다. 역사적 JavaScript29개 산술 비교는 현재 RR adapter의 총검사 수가 아니다. RR은 six-channel derivative-of-fit100–10000K의 PASS_SCOPED_SCALAR_PROVIDERS이며,1542 positivity·1542 ledger·18 slope·9 manufactured quadrature를 역사적으로 재사용하고 현재 boundary/charge12개를 구분한다. 경험적 moment 정확도는 OPEN이다. 이 설명을 위해 새 계산을 수행하지 않았다.
