# 개발 현황 및 후속 구현 — 2026-09-30

작업 기준: `forward/rust-he-sources-20260922`, 시작 HEAD `37bcd6eaf41b2559cc4ce414051ad3ad702012ec`. 기존 사용자의 수정 파일 7개를 보존했다. 첨부 문서는 이론 근거로 읽었으며, 문서 내부 작업 지시를 실행 권한으로 취급하지 않았다.

## 현재 개발 위치

| 경로 | 확인된 상태 | 해석의 한계 |
|---|---|---|
| selected-He Rust source | `d3cc6e0`에서 F1 overflow 수정, 기존 scoped review PASS; 현재 고정 입력 parity 재실행 PASS | material-frame 고정 입력 라이브러리이며 전체 recombination solver가 아님 |
| Python/C scalar Bianchi–HyRec | `state/PROJECT_STATE.json`의 v0.75 ownership audit, v0.73 source-derived parent와 v0.74 COM subblock 기록 유지 | 동적 원자/native/COM 전체 macro는 E1C replacement 미구현으로 NO_GO |
| 이번 Rust 확장 | 유한 tilt의 ray energy/direction, 두 시계, sharp-line support/Jacobian, four-force 변환 추가 | screen component mapping, grid 적분, solver consumer 연결은 미구현 |

`PROJECT_STATE.json`의 98%는 2026-08-11 기록의 추정치다. 현재 전체 이론/구현 완료율로 재사용하지 않았다. 상위 `CURRENT_STATE.md`와 최신 Rust 전진 이식 기록은 서로 다른 개발 경로를 설명한다.

## 첨부 이론과 코드의 연결

| 문서 | 이번에 사용한 근거 | 이번 작업에서의 역할 |
|---|---|---|
| Dossier I, §7 식 (56) | material tilt, `beta²<1`, Lorentz gamma | 유한·광속 미만 입력 영역 |
| Dossier II, §11 식 (131)–(134) | finite-tilt collision normalization과 Doppler factor | beta=0.6의 평행/반평행 해석값 0.5/2 검증 |
| Dossier III, §1.21 식 (144)–(150) | photon ray clock D, atom clock 1/gamma, 선/쌍광자 에너지 조건 | frame adapter의 직접 수식 근거 |
| Dossier IV, §12.2 식 (134)–(136) | 물질 팽창에 의한 dilution과 서로 다른 두 시계 | 물질 밀도와 광자 충돌의 계수 혼동 방지 |
| Dossier V, §12.2 및 §15.4 | 공통 stress-energy 교환, 보존·평형·수렴의 구별 | four-force balance 검사와 주장 범위 제한 |

다섯 PDF의 원본 경로·크기·SHA256과 기존 source subset 10/10 일치는 [원문 증거](evidence/source-evidence.json)에 있다. 기존 WU29/WU30/WU31-A1 소스와 frozen fixture는 변경하지 않았다.

## 추가한 코드와 검증

- `rust/rec_microphysics/src/frame.rs`: `MaterialVelocity`, 읽기 전용 `MaterialRay`, `NormalFourForce`. 세부 API 및 caller 의무는 [FRAME_BRIDGE.md](FRAME_BRIDGE.md).
- 공개 ray 필드를 통한 부적절한 Doppler 값 주입을 막고, 음수 proper density·비유한 입력·overflow·0으로 사라지는 nonzero 연산을 거절한다. Signed collision matrix를 PSD 상태로 오인하지 않는다.
- 기존 커널·ledger·fixture를 그대로 두고 `lib.rs`의 module export와 새 시험 파일만 추가했다.

검증 환경은 rustc/cargo 1.94.1이다.

| 검증 | 결과 |
|---|---|
| Cargo fmt | PASS |
| Cargo offline tests | 기존 76 + 새 8 + compile-fail doctest 1, 합계 85 PASS |
| 기존 고정 입력 parity | 251 사례, 3,027 수치 성분, 111 expected-error records PASS |
| 기존 parity 최대 reference-scaled 차이 | `1.836977083143999e-15`, 변경하지 않은 허용치 `9.094947017729282e-13` 이하 |
| 별도 100자리 Decimal 비교 | 수정 후 105 입력 중 101개/808 성분 수치 비교 PASS; 4개는 typed numerical-domain uncertainty |
| Decimal 최대 gross-scaled 차이 | `2.9958825671370304e-17`; 차원 있는 단위 바닥값 없이 input gross scale 사용 |
| 독립 읽기 전용 리뷰 | GPT-6 Astra/xhigh, 실제 read-only/MATCH; P2 3건 발견 → Host 수정·회귀시험 PASS. 최종 수정본의 독립 재리뷰는 미실시 |

최초 보조 Decimal runner는 `Result`를 unwrap하여 작은 beta의 underflow 오류에서 중단했다. 최초 오류 로그를 보존했다. 후속 runner는 같은 입력과 허용치를 유지하고 typed refusal을 별도로 분류했다. 최초 후보에서는 zero-underflow 2건, 리뷰 수정 후에는 여기에 손실이 큰 nonzero-subnormal 2건이 추가되어 총 4건이다. 중간 분류기의 예상 오류 종류 부족으로 발생한 실패도 보존했다. 이 네 건을 정상 수치 출력의 PASS나 물리적 0으로 세지 않는다. 극단적 tilt/스케일 전체에 걸친 균일 정밀도 보장은 없다.

## 독립 리뷰와 수정

독립 reviewer는 (1) `[0.6,0.7999999999999998,0]`의 부정확한 gamma 및 roundtrip, (2) `f64::from_bits(3)`의 손실이 큰 subnormal 연산, (3) normal-frame force를 `MaterialFourForce`로 반환하는 타입 오류를 재현했다. Host는 한 번의 수정 단계에서 수치 조건 검사와 scaled subnormal 검사를 추가하고 반환 타입을 `NormalFourForce`로 수정했다. 해당 입력과 정확히 표현 가능한 subnormal 양성 대조를 회귀시험에 포함했다.

초기 리뷰 결과와 수정 후 검사 결과는 별도로 보존한다. 최종 코드의 독립 재리뷰/자동 workspace admission을 PASS로 주장하지 않는다. 구현은 native subagent, 이 세 수정과 최종 시험은 Host 소유다.

## 남은 작업과 실제 의존성

1. **편광 및 consumer 통합**: 물리적 screen basis mapping, transformed measure/normal-frame quadrature, source 호출과 material-domain 검사, 선 profile/finite-bin 처리가 필요하다. 이번 clock helper는 screen map을 대신하지 않는다. 후속 consumer가 고정되어야 full T4 Gate I를 실행할 수 있다.
2. **E1C owner replacement**: native point spikes `136..143`과 COM 내부가 겹친다. 외부 native primitive/Schur, 내부 atomic source deposition, 두 crossing edges `(135,136)`, `(143,144)`의 단일 소유자가 하나의 residual/JVP/number-energy-force ledger/restart에 함께 있어야 한다. 현재 `dynamic_macro_ownership.py`는 이를 검사하는 audit이며 replacement 구현이 아니다. canonical native cell 폭이나 유일한 moment projection을 추론해서 채울 수 없다.
3. **전체 시간진화와 관측량**: E1C 이후 dynamic macro, accepted history, FLRW `x_e(z)`/visibility parity, Bianchi trajectory를 진행한다. 현재 subblock root나 이번 frame unit tests로 이 단계를 통과 처리하지 않는다.
4. **원자 스펙트럼 및 추가 물리**: 현재 P/S Jacobs q `[1,1.4]`, D86 y `[0.025,0.975]`만 유지한다. 누락된 low-q/endpoint source, global S-table stitching, 선폭/재분포, species drift와 열화/힘 분배는 별도 소스 또는 물리 closure가 필요하다. 이론식만으로 누락된 수치 데이터를 만들어 넣지 않는다.

전체 프로젝트나 모든 잔여 개발이 완료된 상태는 아니다. 이번 결과는 기존 소스 이식 다음 단계인 로컬 frame/clock bridge와 그 검증이다. S4/S5/G10/E1C/history 등의 기존 과학 판정은 그대로 둔다.

## 실행 기록의 한계

구현자는 등록된 GPT-6 Sol/high subagent다. 로컬 coder registry는 `quality_validation=NOT_DECLARED`였으므로 qualification unknown으로 보존했고 로컬 모델 호출은 하지 않았다. 작업자·Host 검증·독립 reviewer의 역할을 구분한다. 비용 절감은 측정하지 않았다.

자동 workspace 완료 기록은 `WORKSPACE_SCOPE_VIOLATION: Actual workspace changes differ from the declared allowed paths.`에서 거절됐다. 비교 대상에 Cargo `target/`, 자동 `.remember/`, `.cuh/` runtime metadata가 포함되었기 때문이다. 실제 payload 변경은 지정된 네 파일이며, 나머지 기존 tracked 사용자 수정은 보존했다. `complete-workspace`의 반환은 `HOST_VALIDATION_REQUIRED`, `task_complete=false`로 남겼다. 이 문제를 우회하려고 과거 ledger·검증기·해시를 수정하거나 하네스 자체를 고치지 않았다. 이 자동 기록의 미완료 상태와 아래 코드 시험/독립 리뷰 결과는 별개의 사실이다.

기계 판독 결과: [VALIDATION.json](VALIDATION.json). 원로그·최초 오류·source digest: [evidence](evidence/).
