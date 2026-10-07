# Local Codex Task3 검증 세부사항

현재 문서는 최종 candidate가 아직 없는 중간 체크리스트다. 독립 dispatch로 착각하여 branch49d64b26을 Task3 구현이라고 시험하지 않는다. Task8의 실제 candidate full SHA 및 executable/source lock을 받은 뒤 사용한다.

1. he_bb_source 4-argument API와 kernel을 실제 compile한다. 전 repository caller search로 stale 5-argument call을 찾아 기계적으로 이행한다. 기존 Python/C solver를 변경하지 않는다.
2. 새 test12개와 기존 test들을 실행한다. actual count/exit/log를 기록하며 작성된 38개를 관측 PASS 수로 바꾸지 않는다.
3. BB full Re/Im reference를 bb_reference_task3.json과 독립적으로 대조한다. b_shell 자체 누락도 검출해야 한다. reference_gross 기반4096eps를 완화하지 않는다.
4. std::f64::consts::PI 및 식 재배열로 legacy FD JVP 진단이 달라져도 tolerance를 늘리거나 과거 0을 복사하지 않는다. Task6의 analytic derivative/negative controls와 실제 오차를 함께 보고한다.
5. full-stencil vacuum과 arbitrary partial stencil을 구별하고 moments 통과를 일반 angular convergence로 승격하지 않는다. 서로 다른 screen의 J/C matrix 직접 합산은 금지다.
6. Cargo fmt/test/정식 Python parity의 명령별 exit/원로그를 남긴다. compile/type/format 최소 수리는 별도 diff로 보존한다. 과학 full suite/history는 실행하지 않는다.

필수 명령은 최종 local handoff의 3 gates 그대로다. 이 Task3 파일은 그 결과를 미리 채우지 않는다.
