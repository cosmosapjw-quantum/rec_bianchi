# 저장된 8개 궤적 후처리 driver 구현 검토

판정: **PASS_NO_BLOCKING_IMPLEMENTATION_FINDINGS**.

## 검토 독립성

검토자는 충돌 provider와 그 집중 테스트·소스 JSON의 작성자다. Compton provider 및 postprocess_omitted.py는 root가 작성했다. 따라서 이 문서는 root driver에 대한 독립 구현 검토이며, 충돌 provider의 독립 물리 검증을 주장하지 않는다. 이론 및 원본 NPZ에서의 독립 수치 재계산은 thermal_physics가 별도로 맡는다.

## 확인한 실제 산출물

- 실행 source identity: `88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c`.
- 실행된 driver 및 source table의 실제 SHA256를 대조했다.
- RESULT.json에 묶인 20개 파일의 바이트 크기와 SHA256, 8개 NPZ의 CRC·배열 schema를 확인했다.
- 8개 원본 trajectory/receipt와 source lock의 identity를 확인하고, 복사된 11개 상태·진단 배열을 원본과 정확히 대조했다.
- 저장된 872개 상태의 support mask, summary node/interval counts, native unavailable mask 및 paired x-grid 일치를 확인했다.

## 구현 판단

- **단위와 부호 — PASS:** 부호를 가진 W/m³ source를 `nb*H*EV_J`로 나누면 baryon당 eV의 x 미분이 된다. 단열 일은 기존의 양의 work 정의에 음의 부호를 붙인다. CI 운동에너지 손실과 결합에너지 증가는 전체 기체 에너지에서 상쇄되며, CE는 음의 기체 에너지 source로 들어간다.
- **온도 forcing — PASS:** CI에는 `-particle_source/(H*eta)`가 포함되며 합산 forcing은 `ci_full`을 사용한다. 별도의 Planck 기준 곡선을 실제 photon monopole에 근거한 primary 합에 섞지 않는다.
- **복사 에너지 정의 — PASS:** 실제 photon normalization은 부모 `species_hierarchy.py`와 같은 `4*StefanBoltzmann/c*T0^4`를 사용하며, native raw-state의 4번 energy monopole에 연결된다. Planck 기준 에너지 밀도는 자체 `A_RAD_J_M3_K4*Tref^4`로 구성된다. UV는 부모의 bin-centre moments를 유지하고 연속 스펙트럼과의 차이 및 occupation을 기록한다.
- **출처의 지원 범위 — PASS:** 지원 구간은 양 끝 node가 모두 출처 범위에 속할 때만 포함된다. CI에 의존하는 forcing에는 CI support를 적용하며, 전체 기체 에너지 합에서는 정확한 결합에너지 교환 상쇄 뒤 CI support 의존성이 사라진다. 외삽·경계 구간의 기여를 별도로 보고하고 native unavailable mask를 저장한다.
- **저장 격자의 수치적분 — PASS:** 주 결과는 순서가 증가하는 109개 node의 양의 가중치 사다리꼴 적분이다. 두 node마다 추리는 55개 격자도 양 끝점을 포함하며 Simpson 결과는 진단값이다. 이를 연속 해의 오차 상한이나 새로 푼 온도 응답으로 해석하지 않는다.
- **출처 연결과 결과 생성 — PASS:** 기존 source identity와 COMPLETE trajectory receipt·실제 바이트를 사용 전에 확인한다. 결과 디렉터리는 새로 생성하며, source와 입력 trajectory 해시를 종료 전에 다시 확인한다. RESULT는 20개 출력 payload를 묶는다.
- **실행 전에 반영된 수정 — PASS:** 실제 실행본은 독립적인 CI gradient 잔차를 분자로 사용하고 particle-source balance를 확인한다. mask와 gradient를 저장하며 Planck 기준 에너지 밀도는 자체 상수를 사용한다.

## 범위

새 source 계산·적분 재실행·테스트 재실행·ODE는 수행하지 않았다. 현재 파일의 구현과 저장된 증거의 연결을 검토했다. 사전 테스트의 실제 출력은 evidence/COLLISIONAL_TESTS.json에 재실행 없이 보존했다.

정확한 파일 identity와 항목별 결과는 evidence/IMPLEMENTATION_REVIEW.json에 기록했다. root의 driver 또는 결과 파일은 수정하지 않았다.
