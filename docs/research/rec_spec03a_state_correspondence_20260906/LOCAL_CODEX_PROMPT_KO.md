# local Codex — 실제 ModeB 로그 읽기·source 좌표 호환성의 제한된 검산

## 역할과 작업

이번 단일 작업: `REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY`.

이미 승인된 한 복사장·두 광자 full Bose 연구의 진단이다. source-map과 직접 유도는 같은 디렉터리의 SOURCE_MAP_AND_RESEARCH_KO.md가 고정한다. 그 문서를 전체 읽는다. 새 생산 함수나 실제 B·mu·각도 kernel을 구현하지 않는다.

REC 부모는 작업 스레드가 전달한 DELIVERY_SHA다. 그 인계의 부모는 PR70 `84205ab6a9b4e6d51097a82ec15da4deedfefc41` / tree `6f89ef4b871015912596200ba9aec3f2b2999c63`이다. BASS source 기준은 `9d1c702ddf58549a06b29965a3d1b790a0c23159` / tree `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c`이며 읽기 전용이다.

사용자 checkout을 삭제·stash·reset하지 않는다. REC 새 격리 worktree와 BASS 읽기용 격리 snapshot을 사용한다. 사용자의 기존 수학 환경을 사용하고 설치·업그레이드·라이선스 변경·다른 커널 종료를 하지 않는다. 원격 push·PR·Atlassian은 작업 스레드가 한다. local은 소스 commit과 원본 결과 bundle을 반환한다.

## 먼저 읽기

REC AGENTS.md, docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md와 이번 인계 세 문서를 읽는다. 옛 root HANDOFF_PROMPT.md의 REC-NEXT-03 전체 실행은 이번 대상이 아니다. 기존 full Bose 및 COM 함수를 재사용한다. BASS modeb.py, q/comoving.py, source_adapters.py, radial.rs, qevolve.rs에서 이번 대응 부분을 실제 읽고 문서의 blob과 대조한다.

절대 운동량 눈금과 scalar occupation 정규화의 실제 공급자가 기존 코드에 있으면 그 위치와 수식을 기록한다. 이 한 연결 범위만 조사한다. 못 찾으면 저장소 전체 부재라고 주장하지 말고 `OWNER_BINDING_NOT_IDENTIFIED_IN_INSPECTED_SCOPE`로 남긴다. 이 미결정은 아래 제조 진단을 막지 않는다. production에서1 J 또는 어떤 온도로 고정하는 행위는 금지다.

에너지 적분 J 계층과 주파수별 F_Aell(q) 계층을 혼동하지 않는다. 후자의 실제 저장/소유 경로를 이미 확인할 수 있으면 같은 대응표에 기록한다. 없다는 전면 주장을 하거나, 이 미결정 때문에 이번 한 ModeB 진단을 무한 확장하지 않는다. REC의 세 번째 photon backend를 만들지 않는다.

## 허용 경로와 실행 경로

새 파일은 `docs/research/rec_spec03a_modeb_diagnostic/` 아래에만 둔다. 작동하는 검사기, 사례 정의, 필요한 작은 Rust 호출기, 수치 CSV/JSON, 결과 설명, 그림과 원본 해시 목록 정도로 제한한다. logs/cache/build는 Git 밖 전용 디렉터리에 둔다. 기존 production/tests/archive/증거는 그대로다.

주 수학 축은 Fraction·SymPy·mpmath다. 로컬 Wolfram은 이미 가능한 실행 경로로 신규 항등식만 한 번 검산할 수 있다. 모든 설치 패키지를 의무적으로 돌리지 않는다. 이 스칼라 문제에 xAct 활성화는 필요 없다.

기존 radial.rs는 표준 라이브러리만 사용하는 독립 파일이다. 필요한 경우 작은 연구 Rust driver가 `#[path = "실제 고정 snapshot 경로"] mod radial;`로 기존 파일을 호출하도록 컴파일한다. 출력은 Git 밖에 두고 실제 source SHA를 기록한다. crate 전체·PyO3 wheel·BASS 전체를 빌드할 필요는 없다. 이를 전체 Rust backend 검증이라고 부르지 않는다. rustc도 사용할 수 없다면 Python 전사를 native 실행으로 위장하지 않고 실제 미실행 축을 표시한다.

ModeBState 저장/pack 검사는 실제 고정 module을 import하여 실행한다. native sphere가 필요하지 않은 형태의 크기 fixture를 사용한다면 그것을 실제 물리 각도 격자라고 부르지 않는다. 실제 physical frame/rate 공급자 검증과 배열 layout 검증을 구별한다. 기존 require_native를 우회·수정하거나 untrusted native payload를 승인하지 않는다.

## 사전 고정 사례

### A. 로그 보간과 Jacobian

q=(1,4), lnq=(0,ln4), lnf=(0,ln4), 질의 q*=2. 실제 shift_stencil/apply_shift_log를 order2, dln=ln2로 호출하면 결과의 마지막 노드가 이 질의에 대응한다. 첫 노드의 외삽값을 이 내부 질의 증거에 섞지 않는다.

정확한 결과 f*=2, L=(1/2,1/2), df*/df=(1,1/4), 행합5/4다. Fraction/SymPy로 derivative와 합을 독립 검산한다. 같은 source를 단순 Jacobian 전치로 분배하는 가정의 photon-number 잔차1/4를 기록한다. 실제 COMSourceDepositionPlan에 이런 부정합 행렬을 강제로 허용하지 않는다.

### B. Planck 읽기와 쌍반응

같은 q 노드와 질의에서 f(q)=1/(2^q-1), f(1)=1, f(4)=1/15다. E=E_*q, E21=3E_*, k_B T=E_*/ln2는 제조 조건이며 실제 우주론 선택이 아니다. 코드 API에 SI가 필요하면 E_*=2^-60 J를 제조 눈금으로 명시하고 h,c,k_B를 제거하지 않는다.

로그 보간 tracked f=1/sqrt15, 정확한 f(2)=1/3, companion f(1)=1. xg=1/2, xu=1/16, a=1 s^-1로 기존 PhysicalTwoPhotonRamanBin을 호출한다.

정확한 Γ=0. 보간값을 넣은 Γ=(1-3/sqrt15)/8 H^-1 s^-1. 각 rate의 정·역항 크기를 함께 기록한다. 이 반례를 물리 source를0으로 고치는 요구로 바꾸지 않는다.

추가 고정 작은 해상도 진단: order8, lnq 범위[ln(1/2),ln8], n={32,64,128}, q질의={1,2}. 같은 Planck 함수를 사용해 기존 읽기 연산과 고정밀 값을 비교한다. 이미 배운 power-law control을 실제 스텐실 호출의 방향/부호 검사로만 사용한다. 큰 전체 수렴 연구로 확대하지 않는다. 보간오차 자체의 크기에 새 물리 허용오차를 사후 지정하지 않는다.

### C. 상태 좌표와 시간 JVP

eta=1 s^-1, kappa=0, f=2, H=4 s^-1, dy=1/4, dH=1 s^-1, deta=dkappa=0.

C=3, dC=1/2, G=C/(Hf)=3/8,
dG=dC/(Hf)-G*(dy+dH/H)=-1/8.

Fraction/SymPy로 정확값과 일반 미분식을 확인한다. H 또는 f로 나누는 항을 누락한 후보가 같은 결과를 내지 않음을 한 번 보인다. 실제 evolve 루프나 시간 적분은 실행하지 않는다. C를 lnf 배열에 그대로 더하는 코드를 production에 작성하지 않는다.

### D. 기하 좌표의 같은 물리 에너지

M=diag(2,1,1/2), qhat=(1,0,0)와(0,0,1), 상대속도0, E_source=2E_*에서 질의 q는 각각1과4다. 원자 에너지에 같은 q index를 쓰는 방법이 틀림을 검산한다. 이 두 방향은 구면 구적 인증용 격자가 아니라 방향별 좌표 항등식 fixture다.

w_phys=w_com*abs(detM)/r^3 및 number/energy 구적의 r cancellation을 기호로 확인한다. 실제 각도 평균의 합이나 물리 target cell 수를 두 방향으로 인증하지 않는다. E_*·편광 계수·4pi·원자계 시간 변환은 조건부로 남긴다.

## 검증과 실패 분류

기존 state/보간 호출, 독립 정확한 유도, 고정밀 반올림 비교를 구분한다. 기본/hires 표를 다시 읽어 9개 field 연구를 반복하지 않는다. PR70 checker/pytest/80/120자리 전체 재실행 없음. 새로운 전면 RED 하네스나 repository 전체 검증도 없음.

새 계산을 실행할 source commit/tree와 실행 명령·환경을 먼저 고정한다. compiler/import/environment 실패와 실제 수치 잔차를 구분한다. 스텐실 수치 잔차 비교의 기준은 실행 전에 conditioning·binary64 eps·고정밀 계산에서 정하고, 결과를 보고 넓히지 않는다. 중간 실패와 한 번의 표적 수리는 원본 로그로 보존한다. 같은 원인의 실패를 두 번 넘게 반복하지 않는다.

이 문서의 반례는 생산 결합이 아직 없다는 사실과 양립한다. 기대한 비영점 잔차를0으로 만들기 위해 기존 source/평형/tail을 바꾸지 않는다. 로그 보간의 기하평균과 선형 occupation 평균을 같은 연산으로 합치지 않는다. local이 발견한 source-map 오류는 근거와 수정 제안으로 돌려주되 BASS를 직접 변경하지 않는다.

## 반환과 종료

반환물에는 실제 사용한 source blob/파일 SHA, source commit/tree, 명령·종료 코드·패키지/컴파일러 경로, 정확한 값과 수치 잔차 표, 작은 그림(실제 렌더링 확인 여부 별도), 원본 logs, manifest와 복원 bundle을 담는다. 테스트 수는 실제 관측한 값으로만 보고한다. 이전125개/7개/22개 결과를 새 검사 수에 합산하지 않는다.

가능하면 읽기 전용 독립 검토 한 번과 표적 수리 한 번 뒤 checkpoint한다. 동일 작성자의 수학·코드 관점 점검을 독립 reviewer 두 명으로 부르지 않는다. 물리 단위 눈금과 주파수별 PSTF 소유 경로가 미확인이라면 그 정확한 남은 연결만 남긴다.

로컬 원격 게시 없음. 작업 스레드가 bundle과 소스/결과를 받아 새 child·Draft PR 및 REC Atlassian append를 수행한다. 결과 child는 수치 실행 source와 구분한다. 이번 한 진단 후 종료하며 B·mu·보간법 변경이나 production source 연결을 자동으로 시작하지 않는다.

최대 상태: `PASS_BOUNDED_MODEB_READ_SCATTER_DIAGNOSTIC`.
물리 인증·provider·BASS 연결은 false이며 `NO_PASS_REC_PHYSICAL_SPLIT`을 유지한다.
