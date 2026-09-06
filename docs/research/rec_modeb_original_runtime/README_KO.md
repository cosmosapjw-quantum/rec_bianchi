# ModeB 원본 함수의 제한된 실행 검증

부모 PR72 `823cf1c25abda5343be6020bbf0b5bedb131fc3e`, tree `3f01f944ab8a89582b324e9fae37c760f893a80b`.
BASS 읽기 기준 `9d1c702ddf58549a06b29965a3d1b790a0c23159`.

목표는 앞서 유도한 식을 다시 문서화하는 것이 아니라, 변경하지 않은 radial.rs를 작은 표준라이브러리 Rust driver로 컴파일·호출하고, 실제 ModeBState와 PhysicalTwoPhotonRamanBin을 import하여 지정된 제조 입력에 적용하는 것이다. 실제 COMSourceDepositionPlan도 한 고립된 두 광자 반응의 회계 반례에서만 사용한다. 생산 연결이나 time evolution은 하지 않는다.

현재 대화의 container/Python은 각각 한 번 시작 전 ClientError, WolframContext는 평가 전 HTTP404였다. 같은 실패를 반복하지 않는다. 기존 사용자 승인 범위의 제한된 읽기 전용 GitHub workflow를 이 대화에서 직접 시작한다. 다른 작업 스레드/local Codex 인계는 없다. 기본/hires 비교와 과거 검산은 재실행하지 않는다.

새 변경은 이 디렉터리의 checker·driver·이 설명과 해당 branch에만 반응하는 workflow 하나다. 원본 src/tests/archive, PR71/72 문서와 BASS 저장소는 변경하지 않는다. GitHub runner의 전용 임시 venv를 사용하며 사용자 로컬 환경은 접근하지 않는다.

## 사전 고정 검사와 오차 구분

1. Fraction/SymPy로 G=C/(Hf)의 두 미분과 -3/32,133/512 fixture를 확인한다.
2. 실제 ModeBState의 생성·pack/set_from·q 배열을 호출한다. n=2만 제공하는 shape carrier는 물리 구면 격자가 아니며 native sphere/evolve를 호출하지 않는다. require_native를 수정·우회하지 않는다.
3. 원본 radial.rs의 order2, q=(1,4), shift=ln2를 실제 호출한다. 내부 출력 i=1에서 offsets=(-1,0), weights=(1/2,1/2)를 검사한다. tail 선택은 이 내부 결과에 영향을 주지 않아야 한다.
4. 제조 Planck 입력의 실제 읽기값1/sqrt15를 기존 paired API에 넣어 (1-3/sqrt15)/8과 대조한다. 정확한 f_t=1/3의 영점도 비교한다.
5. 동일 원본 order8을 n=32,64,128, lnq=[ln(1/2),ln8], q=1,2에서 호출한다. 선형합 산술오차는 실제 binary64 입력의80자리 dot 기준 및 gamma_(2K+2)*sum|w*y|로 판정한다. Planck 함수 근사오차는 관측값으로만 보고하며 사후 tolerance나 수렴 claim을 만들지 않는다.
6. 고정 M=diag(2,1,1/2)의 같은 에너지 질의와 조건부 measure 상쇄를 SymPy로 확인한다.
7. Jacobian 전치/로그 stencil 전치의 수·에너지 반례와 조건부 Bose 변수 읽기의 충분조건을 정확 대수로 점검한다. 새 생산 보간법을 선택하지 않는다.
8. 기존 COM에 제조 B=[[2/3,1],[1/3,0]], mu=(1,2), 목표E=(E0,4E0), sourceE=(2E0,E0)를 주고, 같은 비영점 Gamma 두 다리를 분배해 총수2Gamma와 에너지3E0*Gamma를 실제 대조한다. 이 제조 B는 실제 물리 map이 아니다.

작은 fixture의 일반 산술 허용치는 실행 전에 128*binary64_epsilon*max(1,|expected|)로 고정한다. order8의 log-dot에는 별도의 위 gamma 경계를 쓴다. 근사오차 자체를 이 산술 경계와 혼동하지 않는다. 실패가 있으면 expected/tolerance를 넓히지 않고 원본 로그를 남긴다.

실제 함수 실행을 위한 source 식별정보·실행 명령·exit code·환경·unittest 결과와 실패를 RESULT.json 및 raw logs에 남긴다. 원본 함수를 전사해 native 실행이라고 부르지 않는다. 그림은 생성과 렌더링 검토를 구분한다. 새 코드 source는 실행 전에 commit하며 결과 문서 child는 실행 commit이 아니다.

현재 이 문서 작성 시 실제 검사 결과는 아직 없다. 성공한 실행에서만 `PASS_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC`를 사용한다. 전체 BASS Rust crate/PyO3 wheel/native sphere/evolve, 물리 B·mu·unit owner·source/provider 인증, 이동 격자, accepted-state 갱신, 전체 repository pytest는 이번 범위 밖이다. `NO_PASS_REC_PHYSICAL_SPLIT` 유지.
