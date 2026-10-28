# 다음 대화 인계: cosmosapjw-quantum/rec_bianchi

PROJECT=cosmosapjw-quantum/rec_bianchi
UNIT=REC-H5-THERMO-BRIDGE01
SCOPE=132 source-locked ambient xe JVP + exact common nH/H scaling for represented real-prefix model
BASE_COMMIT=f5e049ecc20ee7b20c4fcf89003d5d12d86bdcfa
PREDECESSOR_PR=https://github.com/cosmosapjw-quantum/rec_bianchi/pull/147
OTHER_SOURCE_PR135_HEAD=52226bb8d3ac99e7de2bd7934ab30e6fb3f257fe
PREDECESSOR_SOURCE_SHA256=f94fc8df8b8c523177183a2e56c09adac2d93284f5439b9304ef4ae14229e0f6
PREDECESSOR_MODULE_SHA256=ce47a2bc204c58c29cc0962aa78c2130e7381279953a78198d6de3fb693649ac
CENTRAL_CANONICAL=28/88;DELTA=0
PHYSICAL=0/313
H5_PHYSICAL_ERROR=null;H6=OPEN;H7=OPEN;L4=false;REI_activation=false

이번 node가 완료한 것은 ambient xe 열과 공통 nH/H 스케일 방향 하나다. 여섯 개 독립 primitive 열의 전체 결합, pure-H tangent, 시간/방향/frame/JVP, QSS continuous certificate는 미완료다. 독립 SciPy/Decimal 검증 PASS_SCOPED, native blind subagent NOT_RUN. 최초 120자리 검산의 80자리 adjoint 관련 threshold 오류와 초기 시각화 오류는 원본을 보존하고 좁게 수정했다.

다음 작업: PR135의 stable-source J_s와 PR136의 stable-source K_s를 동일 source/branch/table/thermodynamic input identity에서 결합하는 유한 세 점 시험을 먼저 수행하라. Native prefix J와 안정 source J_s를 섞지 말 것. 이후 H5 calibrated incoming error and history pullback, H6 incident trace/geometry, H7 thermal ODE coupling으로 확장하라. 새 IVP/old campaigns/main merge/REI activation 금지. 중복 조사 금지, 원장과 기존 backup 재사용.

재현: 먼저 고정 SOURCE ZIP을 복원하고 SHA256 검증, 그 ZIP의 `electron_response/code/incoming_response.py`를 추출한다. 본 패키지 code/thermo_bridge.py를 --source/--module/--out으로 실행한다. 다음으로 code/independent_validate.py를 --source/--module/--points/--out으로 실행한다. code/plots.py는 --points/--out으로 저장 데이터만 읽는다. 입력 오염, source code hash 변화, nonfinite/out of-domain, 동일 point 순서 이탈 시 통과시키지 말라.

Git 결과 브랜치/PR 및 새 백업 ACK는 과거 값에서 추정하지 말고 이 파일의 후속 전달 기록과 provider 실제 ACK로 확인하라. 원격 전체 다운로드 SHA256은 수행한 경우에만 PASS로 적는다.
