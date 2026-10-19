# REC R3O 연구·실행 인계

## 먼저 확인할 정체성

- 저장소: https://github.com/cosmosapjw-quantum/rec_bianchi
- PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/109
- 브랜치: `research/rec-r3o-grid-frontiers-20261019`
- 실제 새 Cargo 빌드·수치 검증 코드: `4512b19e5615fabcb80e0860dbf3bb3086fe01fb`
- 최신 게시 HEAD와 최종 ZIP 보존 영수증: PR109 Conversation의 마지막 R3O receipt. 문서·백업 ACK 커밋을 실행 코드 SHA와 구분한다.
- 읽을 파일: `EVIDENCE.json`, `DAG.json`, `BACKUP_ACKS.json`, `receipts/RESUME_INTAKE.json`, `receipts/RUST_CI.json`, `review/C9_RUST.md`, `review/C9_RUST_P3_CLOSURE.json`, 이 문서와 `CODEX_HANDOFF_KO.md`.

새 연구 전에 마지막 관측 이후 관련 GitHub/백업을 다시 조회한다. 완주한 계산을 인계 문구가 오래되었다는 이유로 재실행하지 않는다. PR104의 NOT_RUN은 후속 PR105/107의 실제 결과보다 우선하지 않는다. PR107에서 원본 h2 U6 5210-step이 수행되어 PR108/R3O에서 재사용되었다.

## 이 루프에서 완료한 것

| 노드 | 실제 결과 | 한계 |
|---|---|---|
| 백업 우선 재개 | 초기 및 확장 조회, 중단 후 127 REC/148 VigilODE 브랜치와 109/72 PR 대조, Dropbox 12페이지 끝까지, Drive 지정 루트 30개 폴더, Library 최근 목록 확인 | 명시된 시각·루트의 목록 완주. 모든 타 프로젝트 압축파일의 전체 본문을 읽었다는 뜻은 아님 |
| h2 low-z | 검토된 U6 경계 58389부터 실제 16 EMLA step, 독립 원본 C 같은-h 검사 통과 | 전체 153327-step NOT_RUN |
| h4 독립 시작 | 자체 72893 He 행과 8 FULL step을 별도 원본 C와 대조 | h4 전체 연속 적분 NOT_RUN |
| 원본 h 입력 어댑터 | 기존 105859개 상태를 바이트 보존하여 비교기에 연결 | nodewise C parity UNKNOWN, 세 격자 수렴성 미승인 |
| Rust 고정 predictor | 17상태×6스칼라=102개 원본 C 바이트 일치; Python 별도 같은-h 검사 | 원자·열 물리는 원본 C 연산자 재사용 |
| VigilODE RODAS5P | 실제 비자율 EMLA 16 수용 step, 17 직접 출력, 225 source callback | EXPLORATORY_METHOD_COMPARISON; 원본 방법 동등성 아님 |
| faer | 실제 초기 Jacobian의 2×2 LU 잔차 1.2507140131633662e-16 | RODAS 내부 LU는 InPlaceZeroSkipping; 성능 우위 주장 없음 |
| 코드 검토 | core R6/C9, Rust 독립 C9 세 P2 종료; 부모의 한 단계 CLI P3 수정·거절 검사 종료 | 전체 upstream 기능에 대한 감사 아님 |
| 새 GitHub 소스 빌드 | 4512b19e, Cargo 1.94.1, build 153.660120 CPU초, numerical 1.743074 CPU초 | NCP 실행이 아님 |
| CI | 일반 836 PASS/20 SKIP/72 subtests PASS; Rust 전용 17 PASS/0 SKIP | 일반 CI의 16 Rust skip은 전용 검증기 환경에서 실제 수행됨. 나머지 4개는 상속된 skip |

GitHub 원격 실행 ZIP은 946881 bytes, SHA256 `37ed9a21c00f6c6a934358c22f5df3ebf2776de3accbd05ba4bb3a2f9076958d`이며 전체 readback이 GitHub artifact digest와 일치했다. 로컬 현행 소스 67개와 산출물 200개 해시도 실제 대조했다. CI가 보고한 실행 파일 SHA는 `27c918ecc6d8f7e36409d11f68e358cff09d25c3b6dc4aae4e6232438c27b29a`다. 실행 파일 자체는 artifact에 포함하지 않았으므로 그 바이너리의 별도 원격 전체 readback은 NOT_RUN이다.

샌드박스의 앞선 build_002는 이전 소스 일치 라이브러리를 연결했고, 새 CI는 의존 라이브러리를 소스에서 컴파일했다. 두 증거를 별도 보존한다. 실패한 샌드박스 링커 실행과 첫 GitHub build.rs 누락 실패는 수치 물리 실패로 표시하지 않는다.

## 반드시 유지할 과학적 조건

원본 HyRec Oct2012 ZIP SHA256:
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
기준 간격 h2=4.245e-5, h4=2.1225e-5. atomic/thermal 연산자, 입력 시각의 stage guard, stage boundary 소유권, 원본 same-h 허용값을 유지한다.

원본 predictor는 `Y[n+1]=Y[n]+h*(1.25*F[n]-0.25*F[n-2])`다. checkpoint는 상태 xe/Tm만이 아니라 네 미분 메모리와 입력 인덱스·흡수적 Peebles 사건 기록을 포함한다. 다른 단계의 연산자로 과거 메모리를 다시 만들지 않는다. h4 시작에 h2 checkpoint나 C 궤적을 Python 초기조건으로 주입하지 않는다.

RODAS와 원본 predictor의 xe 차이는 기존 같은-h 허용값의 최대 **2.530216356188792배**다. Tm은 0.014734335610808365배다. 따라서 RODAS의 출력·callback 검사가 통과한 결과는 원본 방법의 same-h parity를 통과했다는 뜻이 아니다. 같은 간격 바이트 일치는 전역 물리 수렴성이나 연속 해의 정확도 순위를 증명하지 않는다.

원본 h U5 `HOLD_9_FAIL`, h2 U5 `HOLD_8_FAIL`, 비용 `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`를 유지한다. Python h/h2/h4 물리 수렴성, production speedup, Bianchi/REI/CMB 예측은 미승인이다.

## 중단 중 새로 읽은 관련 결과

VigilODE PR71 `64b98521...`의 달성 오차 정합 비교는 문제별 비용 순위가 다르다. 기존 SciPy C VODE 경로 관측을 원본 Fortran VODE 순위로 가져오지 않는다. source·메트릭·출력·타이밍 계약을 맞춰야 하며, 이 비교도 HyRec production 가속의 근거가 아니다.

개발 tip은 `b56bb19ce85bc28a021138ee29689701a81bc4f0`로 전진했다. 새 triage·비유한 ShiftedOperator 오류 전파 수정을 읽었다. R3O가 사용하는 fast 직접 LU 경로와 별도 faer probe는 해당 ShiftedOperator를 구성하지 않는다. 현행 검증은 재현 가능한 `a21d573...` 고정 소스에서 닫는다. matrix-free/shifted 경로를 후속으로 추가하면 최신 수정 적용 및 별도 검토가 필요하다. 최신 tip 전체가 이번에 빌드·검증되었다고 표시하지 않는다.

HE29는 새 96 Python 검사와 3 Rust 합성 smoke가 있으나 원래 native reference pairs는 0/4다. REI LRS V14 C11은 실제 NCP 19개 경우의 반환이 있으며 Rust 1.99 환경과 1.94.1 샌드박스 결과를 구분한다. 해당 결과는 이 재결합 checkpoint가 아니며 REC 노드 완료나 REI 활성화에 합산하지 않는다. 읽은 원격 archive·본문·범위는 `receipts/resume_related/`에 있다.

## NCP에 남은 최소 실행

NCP의 현재 파일·프로세스·반환을 먼저 읽어 중복 실행을 피한다. 사용자가 파일을 준비하거나 명령을 실행하도록 요구하지 않는다. 기존 NCP toolchain을 전역 변경하지 말고, 이 경로에는 Rust 1.94.1을 병렬 설치/선택하거나 검토된 기존 1.94.1 경로를 사용한다.

1. 현재 게시 소스에서 `scripts/build_r3o_rust.py`로 빌드하고 `scripts/verify_r3o_rust.py --steps 16`을 수행한다. 작고 봉인된 boundary packet이 포함되어 있어 전체 생산 raw 다운로드 없이 실행할 수 있다. 각 결과 디렉터리는 새로 만든다.
2. `scripts/verify_r3o_h4_start.py --mode start --steps 8`은 원본 ZIP만으로 독립 h4 시작을 확인한다. 이미 동일 호스트·동일 소스의 결과가 있으면 재사용한다.
3. h2 full low-z를 진행하려면 검토된 실제 R3M raw를 해시로 찾고, 현재 source SHA에 대한 `verify_r3o_lowz.py --mode smoke --steps 16`을 먼저 충족한다. 다른 호스트의 smoke를 새 NCP 예산으로 재해석하지 않는다.
4. full은 실제 현재 CPU/wall/memory/recovery 여유와 유효한 allocation receipt가 있을 때만 수행한다. 샘플 숫자로 유효 예산을 꾸미지 않는다. 이전 U6 allocation은 이미 닫혔다. full h4 및 최종 세 격자 입력 완성은 별도 후속 노드다.

full low-z CLI는 `--allocation-json`과 `--smoke-verification`을 요구한다. 끝에서 1~2개 step만 남은 checkpoint는 z=0 보간용 4개 상태가 모자라므로 불완전 stencil 상태를 정직하게 반환한다. CLI 자동 resume 기능까지 완성된 것으로 해석하지 않는다. 모든 실행에서 실제 before/after hash, 종료 코드, 자원, 실패·미완료 상태, 백업 ACK와 원격 전체 hash를 구분하여 DAG에 반영한다.

## 보존과 복원

현재 구현·필수 원본 입력·경량 실행 증거는 최종 CODE_EVIDENCE_HANDOFF ZIP으로 보존한다. 이는 과거 저장소의 모든 연구 자료나 400MB 전체 U6 raw를 중복 포함하는 Git 저장소 전체 복사본이 아니다. 완전한 Git 트리는 게시된 HEAD에서 자동으로 fetch하고, raw는 기존 생산자 hash와 백업 ID로 복원한다. 작은 derived packet은 full raw의 대체 원본으로 표시하지 않는다.

최종 ZIP을 만든 뒤 생기는 원격 보존 ACK와 최종 게시 HEAD는 분리된 CLOSEOUT_RECEIPTS ZIP 및 PR109 마지막 receipt로 연결한다. 자기 자신의 SHA256 또는 생성 후 upload ACK를 내부에 가졌다고 주장하지 않는다. 상세 provider별 상태는 `BACKUP_ACKS.json`과 detached 최종 receipt가 권위 있는 기록이다.
