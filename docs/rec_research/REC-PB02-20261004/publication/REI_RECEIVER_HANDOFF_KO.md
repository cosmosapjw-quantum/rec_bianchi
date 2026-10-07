# REC-PB02 → REI 수령 및 다음 adapter 작업

이번 전달은 `rec_bianchi`의 실제 Rust 수소 재결합 reference 모듈과 검증 증거다. 현재 `rei_bianchi`에 호출 경로를 연결한 반환은 아니다. `REI_RECEIVER_TASKS.json`의 각 작업은 완료된 REC 증거와 아직 실행하지 않은 REI 작업을 분리한다.

## 최신 동시 진행 상태

이 인계 작성 중 REI는 `67957715cf3336b89c27c1e59c33ca23098f8934`에서 `c1d7f89c8abc90a6adf971390f2bce7ae7530a23`(tree `98c48f7885414922123fbbbe2733181b09b6ef5e`)로 전진했다. 최신 F03의 `hhe_events.rs`, `thermal.rs`, `microstep.rs`는 static homogeneous synthetic Case-A H/He 결합 모형을 실제 구현한다. 공개 반환은 63개 crate tests, 세 단계 refinement, transaction rejection과 event/energy 검사를 기록한다. 원 controlled fixture와 그 residual/source-site를 유지한다. 이 기록은 수령 증거이며 이번 REC 작업의 새 시험 수로 재집계하지 않는다.

최신 REI 인계의 우선 작업은 chat `REI-CHAT-FLRW02_SOURCE_BOUND_THREE_EQUATION_REGRESSION`, Codex `REI-F04`다. PB02와 FT07이 deferred인 상태를 이번 REC 게시가 덮어쓰지 않는다. 본 REC-PB02는 그와 병행 가능한 수소 reference 공급자 작업을 닫았으며, REI의 deferred PB02 전체를 완료 처리하지 않는다.

F03가 복원하는 국소 광이온화–재결합식과 Peebles C-factor 식은 별도 closure다. F03의 `MISSING_PEEBLES_CLOSURE_AT_CONSUMER`는 그대로다. H=0 static map에는 Lyα Sobolev escape의 H>0 입력을 넣을 수 없으며, 임의의 양의 H나 외부 C-factor를 주입해 기존 fixture가 Peebles를 복원했다고 표시하지 않는다.

## 이번 실제 구현과 증거

REC source parent는 `5694a5c7ef487adc969f38ae9112b796396216ca`다. 새 게시 commit은 최종 publication receipt의 실제 remote ACK에서 읽는다. 이 문서에 예측 SHA를 적지 않는다.

| 역할 | REC 저장소 경로 |
|---|---|
| public Rust 모듈 | `rust/rec_microphysics/src/hydrogen_peebles.rs` |
| 공개 export | `rust/rec_microphysics/src/lib.rs` |
| native 시험 | `rust/rec_microphysics/tests/hydrogen_peebles.rs` |
| 독립 입출력 probe | `rust/rec_microphysics/examples/peebles_probe.rs` |
| 이론·source 계약 | `docs/rec_research/REC-PB02-20261004/theory_reference/PB02_SOURCE_CONTRACT.json` |
| upstream 고정 기록 | `docs/rec_research/REC-PB02-20261004/theory_reference/SOURCE_LOCK.json` |
| native 실행 | `docs/rec_research/REC-PB02-20261004/coding/NATIVE_IMPLEMENTATION_STATUS.json` |
| 독립 비교 | `docs/rec_research/REC-PB02-20261004/evidence/INDEPENDENT_PARITY_RESULT.json` |
| 조건부 각도 검산 | `docs/rec_research/REC-PB02-20261004/evidence/ANGULAR_STUDY_RESULT.json` |

`hydrogen_peebles`는 SI 입력의 retained n=2 shell, 표준 collapsed Peebles RHS, 고정 escape에서의 유한 shell QSS와 정확한 pointwise closure defect를 제공한다. source profile은 `HYREC2_TLA_2020_PEEBLES_FUDGE1`, upstream commit `09e8243d0e08edd3603a94dfbc445ae06cafe139`의 TLA 원식·반올림 상수다. 수정하지 않은 upstream C 함수와 384점 비교, 독립 70자리 shell oracle 24점 비교가 통과했다. native 신규 20개 및 전체 108개 tests가 통과했다. 이는 기록된 finite regression domain의 구현 증거이며 원자율의 물리 오차 인증이나 전체 history 인증이 아니다. rustfmt는 실행 환경에 없어 미실행으로 남겼다.

별도 local Sobolev angular 연구는 42점/95검사를 통과했다. 전 방향 h(n)>0, 등방 source/population, local coefficient, 고정 n1, 동일 Sobolev closure 아래의 조건부 결과다. 일반 Bianchi Lyα 수송이나 현재 Rust의 각도 소비자 구현을 뜻하지 않는다.

## PB03의 최소 REI adapter 계약

1. **별도 이름과 입력 형식.** 새 receiver mode ID는 `PEEBLES_HYREC2_TLA_FUDGE1_ONE_T_SOURCE_V1`, retained 연구 state mode는 `PURE_H_RETAINED_N2_RESEARCH_V1`다. 기존 F00/F03 Case-A 이름·fixture·반환값을 유지한다. 비교 기준을 같은 실행에서 자동 바꾸지 않는다.
2. **시간·단위.** nH는 proper m^-3, α는 m^3/s, H·β·Λ·Rα는 s^-1, T는 K, 미분은 proper second다. REI cgs 경계에서는 `cm3_density_to_si`와 `cm3_rate_to_si`를 각각 정확히 한 번 적용한다. 분율에 -3H x를 추가하지 않는다. 적색편이 미분은 `to_redshift_rhs`; d/dln a는 별도의 H 나눗셈이며 같은 변환이 아니다.
3. **상수·온도 소유권.** 이번 native one-T 함수는 Tm=Tr를 요구하고 불일치를 오류로 반환한다. HyRec 원식 상수 profile과 현대 SI 상수 재계산 profile을 섞지 않는다. `PhysicalConstantsSI`를 선택하면 별도 profile ID와 독립 검증을 둔다. 원 rate fit의 100–10000 K 비교망은 수치 회귀 영역이며 물리 정확도 범위로 승격하지 않는다.
4. **실제 ground abundance.** retained state의 x1=1-xp-x2를 `RetainedState::ground`가 소유한다. 같은 actual state로 `hyrec2_one_temperature_source`를 다시 호출해 Rα∝1/x1를 조립한 뒤 `retained_rhs`를 계산한다. 표준 Peebles 비교는 x2를 버린 모형임을 명시하고 source 조립에도 `{xp,x2:0}`을 사용한다. 두 모형의 C가 달라지는 효과를 shell lag와 혼동하지 않는다.
5. **QSS 적용 범위.** `qss_at_fixed_ground`는 주어진 x1의 순간 target이다. `frozen_escape_qss`는 Rα를 고정한 유한-shell 근만 계산한다. Rα가 x2에 따라 달라지는 비선형 root나 시간에 따른 QSS 유효성을 대신하지 않는다. state마다 Rα를 갱신하거나 별도 root를 풀었다는 증거 없이 이 근을 physical trajectory에 재사용하지 않는다. lag·ground-depletion defect를 독립 기록하며, 오류를 지우기 위한 즉석 projection/clip·C fitting을 금지한다.
6. **source·에너지 소유권.** βshell=βP/4, D=(Λ+3Rα)/4, thermal inverse와 순수 H의 xe=xp를 유지한다. retained binding/H는 χ1 xp+E21 x2다. Case-A 즉시 방출 χ1과 Case-B ground recycling을 동시에 세지 않는다. 새 모듈은 열·방출 spectrum·diffuse ionizing photon count를 반환하지 않는다. 기존 F03 heat/escape 장부로 자동 연결하지 말고 그 연결이 필요하면 별도 물리 계약을 먼저 둔다.
7. **진짜 소비자 증거.** REI 함수에서 실제 REC 모듈을 호출하고 동일 입력의 C, βP, Rα, dxp/dt, dx2/dt, dx1/dt, closure defect를 export한다. 이 출력과 독립 기준을 비교해야 `REI_CONSUMER_POINTWISE_VERIFIED`를 줄 수 있다. fixture가 expected RHS를 그대로 반환하거나 외부 C를 강제 주입하는 경로는 수용하지 않는다.

## 다음 작업과 멈춤 조건

먼저 실제 REC publication commit·tree·source hash를 receiver manifest에 고정하고 live REI HEAD 이후 변경분을 읽는다. 완료된 전체 He/HH/CR 수치 suite와 기존 PB01/FT 유도를 반복하지 않는다. 변경된 adapter의 finite tests만 실행한다. 취소·오류 입력에서 source state나 기존 Case-A 결과를 쓰지 않는지를 확인한다.

그 다음에만 같은 α·상수·IC·H(z)·nH(z)·T(z)의 짧은 순수 H one-T FLRW history를 preregister한다. 시작·종료 z와 tolerance, 두 독립 적분기, near-Saha 비교 scale, error refinement를 실행 전에 고정한다. retained shell history는 강성을 다루고 순간 ground/Rα 갱신 및 QSS defect를 검사한다. 이 **실제 우주론 history는 아직 미실행**이다. 기본 full HyRec와 원 Peebles의 무조건적 일치나 일반 Bianchi/He history를 수용 기준으로 넣지 않는다.

old REI local error<2e-4, public width<2e-3, [160,161] FAIL=2.1245050576368385e-4 및 tick160은 그대로다. 새 point test PASS가 interval certification을 통과시키지 않는다. full cosmological/parameter sweep, 원자 적분, E1C native/COM 전체 실행, 외부 원본 전체 build를 다음 adapter의 자동 작업에 넣지 않는다.

원 HH·CR·BASS_HE 정밀 lane과 REC E1C·selected-He lane은 기존 identity/gate를 보존한다. 새 source가 필요한 온도·에너지·원자종·tilt·일반 선수송 범위에 실제로 진입할 때 별도 scope 결정으로 해당 lane을 호출한다. 순수 H 한 온도 reference를 위해 원자 연구 세 스레드나 E1C 완료를 기다릴 필요는 없다.
