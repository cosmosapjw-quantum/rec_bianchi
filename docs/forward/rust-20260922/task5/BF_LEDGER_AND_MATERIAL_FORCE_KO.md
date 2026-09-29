# Task5 BF source / signed energy / material four-force 계약

## 근거와 상태

Authority: WU30 RESULT (7)-(8), T4 interface §2.2-2.3와 conservation audit §1-3. 원문 10개는 source_subset에 바이트 그대로 유지한다. 이 문서는 코드 설계와 작성 상태이며 새 물리 유도나 Rust 실행 인증이 아니다.

## 소유권과 API

기존 he_p_bf_source와 he_s_bf_source의 table handle은 정·역 과정에 동일하게 적용된다. P의 s/d partial, singlet S의 outgoing p channel, Jacobs length/velocity family는 기존 정의를 유지한다. q={1,1.2,1.4}, Mb->m²=1e-22, high-band 선형 representative에 변경이 없다. Bhatia splice, low-table 추가 또는 full-spectrum normalization은 없다.

SBoundFreeOutput에 atomic_s_density와 atomic_gross_scale을 추가한다. S source는
`c sigma a_gamma E_J² [eta_S (2+tr F) - nS tr F]`를 직접 평가한다. j=-a_gamma E_J² tr C에서 부호만 뒤집어 S source를 만들어 내지 않는다. P의 T_E, F^T, W_P^T와 eta 식은 그대로다. BF eta/C/B/j/gross의 nonfinite 산술 결과는 NumericalDomainUncertain으로 거절한다. 이 finite guard는 모든 underflow/condition-number에 대한 정밀도 증명이 아니다.

`assemble_he_bf_grid(state, &[WeightedBfMode])`의 각 node는 channel/table, energy_ev, F, V, direction, weight_energy_j, weight_omega_sr를 가진다. 원래 state의 ng/ns/WP/n+/ne/T를 복사하고 해당 mode의 F,V만 적용한다. source kernel과 measure를 분리한다. 영 가중치 node도 domain/frame/screen/source를 검사하여 missing 데이터를 0으로 숨기지 않는다. 반환은 all-or-error이며 오류 이전의 partial accumulator를 노출하지 않는다.

`assemble_selected_he_material_ledger(state, bb584, ir, bf, pairs, convention)`는 위 BF 결과와 기존 BB/pair kernel을 하나의 SI 장부에 연결한다. DirectedBbMode/DirectedPairMode는 원래 node와 명시적 진행 방향을 가진다. 같은 screen의 +/- ray를 cross product로 추정하지 않는다. Pair의 direction도 기존 exchange involution에 정확하게 결합한다.

## 측도·단위

에너지 query는 eV, BF 적분 weight는 J, 각도 weight는 sr다. proper density [m^-3]와 material proper second를 사용한다. SI 결과에는 `_j`를 붙였다. 기존 HeEnergies::canonical()과 assemble_he_event_ledger의 caller-consistent 단위는 변경하지 않았다. 새 HeEnergies::canonical_si()는 J다.

C: occupation/s. B_P와 B_S 및 j: m^-3 s^-1 J^-1 sr^-1. BF assembler는 dE_J*dOmega를 한 번 적용한다. BB는 delta_J 적분을 한 번 닫은 뒤 C_shell*a_gamma*epsilon_J²로 광자수를 누적한다. Pair는 dE_1=DeltaS_J*dy로 tag1 marginal만 전체 ordered support에 적분한다. tag1 전체와 tag2 전체를 더하지 않는다.

## 독립적인 scalar terms

`R_i = sum j_i dE_J dOmega`, `P_removed = sum E_J j_i dE_J dOmega`,
`P_int,BF = sum chi_i,J j_i dE_J dOmega`,
`H_kin = sum (E_eV-chi_i,eV)*EV_J*j_i dE_J dOmega`.

Photon number/power는 `a_gamma E_J² tr C`에서 별도 누적한다. Hkin=-Pint-Pgamma로 정의하지 않는다. 원자 P source는 B_P 행렬에서 누적하고 S source도 별도 scalar bracket을 누적하여 event-matrix 값과 비교한다. 5개 event column과 +/- event rates를 모두 테스트 대상으로 둔다.

## Four-force

metric (-,+,+,+), orthonormal material tetrad, u=(1,0,0,0)에서
`Qgamma=(Pgamma/c, integral (E/c) e tr(Sgamma) dE_J dOmega)`,
`Qmatter=-Qgamma`다. 따라서 matter energy는 `c Qmatter[0]=Pint+Hkin=-Pgamma`다. Hkin만으로 물질에너지 전체를 대체하지 않는다.

Qmatter와 Qgamma의 반대 부호는 동일 사건 장부의 정의이지 독립 검증 성과가 아니다. 코드는 photon energy와 scalar ledger의 차이, Pint+Hkin+Pgamma, matter energy/force 잔차를 따로 반환한다. spatial momentum은 원 source의 방향별 photon moment다. heavy-atom leading order에서 BB/pair recoil heat=0이어도 momentum=0으로 두지 않는다. 전자/이온/중성원자별 force partition 및 normal-frame boost는 미구현 범위다.

## 유효범위와 구현상 결정

combined assembler는 canonical HeConstants와 정확히 같은 registry만 받는다. 기존 BB kernel이 canonical line energy를 소유하는 상태에서 다른 상수 registry의 BF/pair를 섞지 않기 위한 입력 제한이다. standalone BF의 기존 일관된 custom-constant 계약은 바꾸지 않는다. 새 물리 상수·보정·rescale은 없다.

비어 있는 channel slice는 caller가 선택한 기여를 생략한 것이며 그 channel의 전체 source가 0이라는 주장이 아니다. BF empty slice는 empty sum이고, combined input이 전부 empty면 InvalidInput이다. 이 API는 finite selected support의 contribution만 반환하며 외부 band source는 UNKNOWN이다.

number_gross/energy_gross는 net-node 절댓값 합계의 진단치다. cancellation이 큰 LTE에서 독립 gain/loss reference gross를 대신하지 않는다. 원문의 exact detailed balance/보존 항등식과 f64 실행 안정성은 구별한다.

## Local 검증

새 17개 시험은 forward.rs에 있다. before/source와 테스트 사전작성 hash를 checkpoint evidence에 보존한다. Rust red/green, fmt/test/clippy, 실제 component parity와 회귀는 local Codex가 candidate exact revision에서 실행해야 한다. 여기서는 컴파일하지 않았다. Task6 전용 independent runner와 원문 T4 IDs는 그대로 미실행이다.
