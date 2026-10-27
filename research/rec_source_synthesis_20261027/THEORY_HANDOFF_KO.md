# R10 — 구성적 이론 결과와 실행 인계

## 확정한 결과

원래 HD 자료의 준위 에너지와 주파수가 어긋날 때, 동일한 온도의 Boltzmann 개체수와 Planck 복사를 함께 넣은 진단은 일반적으로 열평형의 두 조건을 동시에 만족하지 않는다. 준위와 주파수를 수정하지 않고 그 차이를 직접 정량화한다. 정확한 원자료 유리수로
`delta = h [100 c (Etilde_u - Etilde_l) - 10^9 nu_GHz] / (k_B T)`
를 만들면, 위·아래 양의 복사 전이율의 정규화 차이는 `I=tanh(delta/2)`, 소스 함수의 Planck 대비 편차는 `D=expm1(-delta)/[-expm1(-x_E)]`이다. 두 양의 부호는 반대다. R6 독립 유도와 R7 Wolfram 검산을 통과했다. 다음 실행은 원래 8개 선 × 50,100,200 K의 24개 진단이다. 원래 35 Hz 비교와 7/8 실패 판정은 유지한다.

실제 저장 history를 native 식 `t_k=eta0+k*dlna`의 정확한 실수 연산 표현으로 재구성하면, 각 선형 구간 안의 이동 나머지는 0이며 knot를 넘는 나머지는 slope jump의 유한 합으로 정확하게 표현된다. 양·음 이동은 출발점의 방향 미분을 사용하고 출발 atom을 제외한다. chord 나머지는 음의 Peano kernel jump 합이다. 절댓값 jump 합이 정확한 표현상의 상계를 준다. 이 유도는 유한 piecewise-C2 partition의 조건으로 확장했다.

R6에서 실제 마지막 인과 셀에 놓인 12개 query를 찾아 right-crossing을 `SKIP_CAUSAL_PREFIX`로 남기고, chord의 한쪽 끝은 현재 셀 안의 midpoint로 정의했다. 예상 실행 수 1,240 retiming, 313 chord, 12 skip은 다음 runner에서 실제 자료로 다시 유도한다. 이 값들은 검증 전에 통과 결과로 간주하지 않는다.

## 재사용한 근거와 현재 한계

- 이론: `THEORY.md`, SHA256 `6b1952f382164c760479f5c3b8bef09803bcddc86343433225f052840c6ea5f1`.
- 독립 R6 판정: `review/THEORY_DECISION.json`, SHA256 `431fe1e98557b6521154d6eb4e0728d3445d639adddf0941126e3daa8d776753`; 두 구체적 finding을 모두 수정해 종료했다.
- R7 기호 결과: `evidence/WOLFRAM_R7.json`; thermal 두 식과 kernel 질량의 잔차 0, 양·음 hinge 검산 일치.
- 실행 계약: `CODING_CONTRACT.md`, SHA256 `7dd2e930cad8bf919a9dbbf90a0426f76ea00eaf6eabf16f3d677b8726d1364e`.
- 저장된 실제 history와 query binding은 복구 후 원래 SHA256이 일치했다. GEO01의 기존 결과와 전달 복구는 재사용하며 새 roots/matvec을 실행하지 않았다.
- H5 물리 defect·tube·stability·curvature에 필요한 입증 입력은 이번 represented-history 정리로 생기지 않는다. `physical_epsilon=null`, 물리 coverage `0/313`, `L4_ready=false`를 유지한다.
- p/o-H2 collider는 원자료 그대로 분리하고 50,100,200 K 밖으로 외삽하지 않는다.

## 중단 복구와 다음 실행

R9 Git commit은 `eb3b390eb59a4c48b5aa2d3bec928465b9c35f2e`다. 그 게시 이후 작업 공간이 비어 있는 현상을 관측했으며 원인은 확인되지 않았다. Git의 고정 소스와 필요한 입력만 복구했다. R9 ZIP은 8,690 bytes, SHA256 `6c4089455d800d3a6b336569d1234a841283e36c82518cc3b7771d642bac10c9`로 정확히 재생성했고 Dropbox·Drive ACK를 받았다. 과학 실행은 반복하지 않았고 이전 예산을 초기화하지 않았다. 기존 계약의 'local index is original base' 문구는 중단 전 상태를 가리킨다. 현재 복구 checkout의 실제 HEAD는 R9이며 API 게시 HEAD는 후속 receipt를 따른다.

이번 재개에서 스킬의 현재판 1.3.0을 읽었다. 이미 선택한 전체 R1–R10/C1–C10 범위, 사용자 원래 구성, 동결 과학 기준과 총 한도 1,020 CPU초는 그대로다. 새 단계 선택이나 새 루프를 시작하지 않는다.

다음 C1–C4는 이미 동결한 식·입력·허용 오차를 실제 코드 경로와 실행 배치에 연결한다. C5에서는 lower-tier worker가 `hd_joint/`, `history_remainder/`를 분리 구현하고 각각 최대 60/120 CPU초 primary를 수행한다. 단위 누적 한도는 각각 360 CPU초이며, 테스트·그림·수정 비용도 포함한다. C6–C8은 한 번의 성공한 실제 결과를 단계별로 해석하고 필요한 표적 검사만 추가한다. C9는 구현에 참여하지 않은 reviewer의 한 번의 독립 검토다. C10에서 실제 결과, 한계, 예산, 소스 ZIP, 이중 백업과 중앙 반환을 전달한다.

중앙 최신 shared의 CR_N5 추가 반환은 보존한다. 기존 88개 원계약을 기준으로 완료 수는 working **32/88**, shared **27/88**다. 이번 두 진단의 완성만으로 원 프로그램의 노드 수를 늘리지 않는다.
