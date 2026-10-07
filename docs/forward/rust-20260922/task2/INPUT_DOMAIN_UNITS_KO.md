# Task 2: 입력 domain·단위 계약

## 원문과 범위

승인된 IMPLEMENTATION_PLAN_KO.md Task2를 구현한다. WU29 §2 Eq.(1)은 F=F†≥0, WP=WP†≥0, proper densities, real V^T V=I2와 dnγ=aγ E²trF dE dΩ를 고정한다. WU29 §5 및 T4 §2.3-2.4는 BF occupation C와 spectral event/atomic density를 구별한다. 수치 허용치와 uncertain 정책은 원 논문의 새 물리 결과가 아니라 승인 계획의 f64 구현 계약이다.

원문 10개는 Task1과 byte-identical하다. Table 수치, D86 수치/보간, collision transpose/conjugation 수축식, canonical energy 값, signed EVENT_MATRIX는 변경하지 않는다.

## 작성한 공개 경계

`Mat2::validate_occupation`, `Mat3::validate_population`, `SourceState::validate`, `HeConstants::validate`, `HeEnergies::validate`, `validate_screen`, `material_energy_j`, `energy_width_j`를 작성했다. BB/PBF/SBF/pair/ledger의 현재 진입점에 필요한 검사를 연결했다. BB에는 없는 T/ne를 임의로 추가하지 않는다. 향후 Task3의 WeightedBbMode와 Task4의 PairInput은 동일 validator를 각 실제 V/F에 적용해야 한다.

모든 component는 finite여야 한다. Matrix scale은 max(|Re entry|,|Im entry|)이며 +1 바닥이 없다. Zero matrix는 그대로 허용한다. 2×2의 3개, 3×3의 7개 principal minor를 모두 검사한다. 행렬을 대칭화하거나 clip/project하지 않으며 입력 byte를 수정하지 않는다. Hermitian 상대허용치는 1e-12이고 scaled minor의 허용치는 4096eps=9.094947017729282e-13이다. Minor<-tol이면 InvalidInput, -tol≤minor<0이면 NumericalDomainUncertain이다. 하나라도 명확히 invalid이면 다른 uncertain보다 우선한다. 정규화 시 nonzero entry가 underflow로0이 되는 경우도 uncertain이다. 근접 Hermitian 입력의 원래 entry로 determinant를 계산하고, 무시할 수 없는 imaginary determinant는 uncertain이다. 이것은 exact/outward PSD proof가 아니다.

Screen은 real finite 3×2이며 V^T V=I2를 1e-12로 검사한다. Optional direction e가 주어지면 e.e=1, V^T e=0도 검사한다. Screen/방향을 rescale하거나 Gram-Schmidt하지 않는다. Complex screen이나 normal-frame boost를 지원한다고 주장하지 않는다.

HeConstants는 모두 finite/positive이고 ΔP=ΔS+epsilonIR, IHe=ΔP+chiP=ΔS+chiS를 검사한다. Canonical constants와 테이블 family는 기존 owner를 유지한다. 이 coherence 검사가 임의의 다른 atomic constants에 대한 문헌 권위를 생성하지는 않는다.

## BF 에너지 경계

Photon `energy_ev`는 finite/positive여야 한다. E≤0, NaN, ±Inf는 InvalidInput이다. 유효한 상태에서 0<E<chi만 PhysicalZeroBelowThreshold다. chi≤E에서 데이터가 없으면 MissingAuthority다. q의 직접 lookup은 원래 [1,1.4] 엄격 경계를 유지한다.

Material-energy 경계는 먼저 E_lo=chi+1*Ry, E_hi=chi+1.4*Ry와 비교한다. 이 encoded 에너지와 정확히 같은 node만 원래 q=1,1.2,1.4로 되돌린다. ±1ulp 밖 입력을 tolerance/clamp로 안에 넣지 않는다. Band 안이지만 q 변환이 밖으로 나가는 표현 실패는 NumericalDomainUncertain이다. 정확한 실수 energy-to-q interval 인증은 아니다.

## 단위와 측도

Lookup은 eV, proper densities는 m^-3, F는 무차원, C_P/S는 occupation/s다. `density_measure=ContinuousPerJoulePerSteradian`는 B_P와 j_P/S에만 적용한다. C_P/S 자체에 dE를 곱해 event라고 부르지 않는다. B_P와 j는 m^-3 s^-1 J^-1 sr^-1이며 caller가 dE_J dΩ를 한 번 적용한다.

`material_energy_j(E_ev)=EV_J*E_ev`, `energy_width_j(dE_ev)=EV_J*dE_ev`를 별도 함수로 둔다. Width=0은 허용한다. 양의 eV가 J 변환에서0이 되면 uncertain이며 zero rate로 바꾸지 않는다. Source kernel은 width adapter를 호출하지 않는다. 이미 적분된 rate에 이를 다시 곱하지 않는다.

기존 ledger의 HeEnergies::canonical은 여전히 eV이며 같은 단위의 moments를 받는다. 이번 단계에서 W/m³ 또는 물리 four-force 구현으로 재명명하지 않는다. Task5가 사건으로부터 SI moments를 실제로 조립해야 한다. BB sharp-line 출력의 구조 변경은 Task3, pair density/marginal/measure 구조 변경은 Task4다.

## Fixture와 local 검증

`frozen_inputs_v2.json`의 125개 case는 domain 분류의 사전등록이지 full source 정답표가 아니다. Nonfinite는 표준 JSON의 tagged object로 표현한다. `acceptance_v2.json`은 위 threshold/정규화/endpoint/error 정책과 11개 Rust 시험 이름을 고정한다. Python 표준 라이브러리의 Fraction/permutation determinant toy가 125개를 분류했으나, 실제 Rust guard나 source를 실행하지 않았다.

기존 15개 Rust 시험의 원 bytes를 prefix로 보존하고 11개를 추가했다. 소스 수정 전에 fixture와 Rust tests를 작성한 hash/timestamp를 evidence에 보존했다. Rust compiler-red/green, cargo fmt, cargo test와 실제 package parity는 NOT_RUN이다. Task8 후보 게시 후 local Codex가 실행한다. 기존 +1 floor의 parity runner 전체 개정은 Task6에 남아 있다.
