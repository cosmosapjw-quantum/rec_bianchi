# Task3 진행 ledger

Plan: docs/forward/rust-20260922/IMPLEMENTATION_PLAN_KO.md

- Parent Task2 archive hash/size/manifest99/99/CRC를 현재 실행에서 확인했다.
- 승인 범위: Task3만. Rust compile/red-green은 local 소유이고 여기서는 fixture/코드 작성과 작은 독립 toy에 한정한다.
- Pre-flight: Task2의 Mat2/Mat3/validate_screen/SpectralMeasure를 Task3가 그대로 소비한다. Task4/5의 pair/BF 구현은 변경하지 않는다.
- Ruling: 0.1 BB signature 변경은 승인 계획에 따른다. Legacy isotropic test input만 명시적 caller helper로 이행하며 production broadcast wrapper를 만들지 않는다.
- Ruling: Angular diagnostics의 full flag는 두 기하 moment만 뜻한다. Partial stencil을 invalid로 만들지 않으며 renormalization도 하지 않는다.
- Ruling: 예전 26개 test의 이름과 의미를 보존하되 BB API를 사용하는 call8개와 spectral assertion은 바뀐다. Byte 보존과 semantic migration을 구분한다.
- Ruling: finiteness post-check는 BB arithmetic fail-closed만 보강한다. 모든 float underflow/rounding이나 PSD의 exact proof를 주장하지 않는다.
- 입력/허용치/독립 rational reference 고정 후 테스트12개를 먼저 작성했다. 그 뒤 source block과 call11곳을 수정했다.
- Exact toy4 fixtures, vacuum identity와 LTE9 modes를 실행했다. Rust는 미호출이다.
- 현재 코드작성 종료, 검증 미완료. Git commit/push는 Task8. 다음 Task4.
