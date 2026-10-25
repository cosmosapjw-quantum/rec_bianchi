# 중앙 publication base 변경과 REC 의존성 — 8e → b24a

이 문서는 초기 03:06 조사 cut 이후 실제로 바뀐 중앙 source를 별도 기록한다. 과거 8e 조사 결과와 S0R 파일은 그대로 보존한다. PB01 과학 수락은 아직 **PENDING**이며, 이 문서나 local skeleton에 새 PB01 수치·판정·observation을 생성하지 않았다.

## 실제로 고정한 최신 base

| 항목 | 실제 관측 |
|---|---|
| Canonical PR | [PR222](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222), open/draft |
| Branch | `research/orchestration-sandbox-20261022` |
| HEAD | `b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4` |
| Tree | `210f15423ab8f79f691ae8a1a6cc7128b1094bff` |
| HEAD 조회 시각/횟수 | 2026-10-25T07:49:37.077Z / **1회** |
| 직전 조사 base | `8e946b46aa44581f09141184f193223277f2ec88` |
| 비교 결과 | 6 commits ahead / 반환된 changed paths 74개 |
| 최신 DAG | 428,298 bytes; Git blob `7c40670f9b407da45ebb118daf0ba8fdcbbea323` |
| 최신 DAG SHA256 | `6bd6dceea26388e19384b27fed7145f97dda5d5de76f8a83b59315fb52e6e1ce` |

실제 PR 응답, pinned commit/tree, 비교 응답 및 source 원문은 이 디렉터리의 `raw_PR222_CURRENT_ONCE.json`, `raw_COMMIT_AND_COMPARE.json`, `raw_PINNED_SOURCE_READS.json`에 보존했다. 정규화한 identity는 `CURRENT_BASE_BINDING.json`, 변경 경로와 6개 commit은 `CHANGED_PATHS_8E_TO_B24A.json`에 있다. 전체 51 repo / 2,261 branch census는 반복하지 않았다.

## 무엇이 바뀌었고 무엇을 그대로 상속하는가

현재 DAG의 원 40 contracts, 17 integration edges, 7 authorities, 40개 plan status, root non-node fields와 모든 dependency fields는 8e와 같다. 두 REC node도 observation 이월 전에는 8e와 정확히 같다. 실제 DAG 변경은 다음 두 sibling node의 부가 관측이다.

| Node | 새 실제 관측 | 원 계획 상태 |
|---|---|---|
| `CR_N5_ATOMIC_ISOTOPE_COVERAGE` | `observed_progress.additional_children`가 4개에서 5개로 증가. 기존 4개는 동일하고 H1 ground spontaneous RR finite-chain child를 추가 | `PARTIAL` 보존 |
| `HE-ANG` | `observed_completion.finitemass_cba_subunit` 추가 | `SOURCE_INPUT_PENDING` 보존 |

HH90를 포함한 `WU_NUCLEAR_PARTICLE_OWNERSHIP` 객체는 8e와 동일하다. 최신 다른 38개 node의 canonical SHA256은 `b17e3413e6f130b115d52345ab0e250e42d87354403ae67c4a909b709717f045`다. 이는 이전 8e의 다른 38개 hash와 다르므로 publication 검사에는 최신 값을 써야 한다.

`AGENTS.md`의 실제 원문은 9,351 bytes / blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`, 고정 `HANDOFF_rei_bianchi_KO.md`는 19,988 bytes / blob `b7282c1d88dbb7622853c697d5787d43b12fe8ef`로 이전과 같다. 고정 authority `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`와 원 규칙을 바꾸지 않는다.

최신 tree에는 `research/rei_source_pair_binding/hi_strain_response_20261025/` 아래 **69개의 새 path**가 있다. 나머지 변경 5개는 DAG, HE/CR handoff 두 개, HE/CR return 두 개다. 현재 tree를 parent/base tree로 사용하여 이 모든 변경을 상속해야 한다. PR228 전체 DAG를 덮어쓰는 방식은 최신 CR/HE 관측과 HH90를 보존하지 못하므로 사용하지 않는다. 69개 파일 모두의 본문을 새로 심사했다고 주장하지 않는다.

## 새 owner 성과의 source와 범위

### CR: H1 spontaneous RR finite chain

새 [CR return](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4/research/orchestration_longterm_20261023/assembly/returns/RETURN_BASS_CR_N5_RR_MILNE_20261025.json)은 `COMPLETE_SCOPED_CONDITIONAL` / `NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_H1_SPONTANEOUS_RR_FINITE_CHAIN`을 기록한다. 이는 기존 PR104의 8개 finite electron-energy chain에 native 13.6 eV Verner PI/Milne와 prescribed 10000 K 공통 bath를 결속한 spontaneous H1 ground RR 성분이다. Target은 stationary heavy target이고 recoil은 0으로 둔 해당 모델이다.

Electron/HII/HI 및 photon/internal-energy 소유권이 명시되어 있다. 그러나 `actual_photon_occupation`, `stimulated_hazard`, `total_all_level_RR_hazard`, `global_error_bound`, `global_model_error_bound`는 모두 null이다. Return은 finite-chain/grid 관측이 continuum/global physical error를 보증하지 않는다고 명시하며 parent N4/N5는 PARTIAL/OPEN으로 남긴다. 최신 중앙 계보에 실제 M2 `3ae182311e69fe2d7cb641e7bfe30c18e24dd3d0`가 존재한다. 원 return의 18/20 과학 동결과 실제 M2 게시 조건부20/20 문구는 과거 상태 그대로 보존한다.

따라서 새 RR 공급자 성분이 완성된 성과는 현재 관측에 반영한다. 이것이 REC의 원 cosmology history 또는 source-owned incident photon trace를 제공한다는 추론은 하지 않는다.

### HE: finite-mass CBA

새 [HE return](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4/research/orchestration_longterm_20261023/assembly/returns/RETURN_HEANG_FINITEMASS_CBA_20261025.json)은 finite-M labelled direct C1 Born channel, 양쪽 recoil phase, invariant/Jacobi/lab measure와 두 positive-root fold의 한정 수치 채택을 기록한다. 현재 단계는 **19/20**, C8 partial export가 열려 있다. 원 실패·비용도 보존한다.

`physical_provider_admitted=false`, `event_sigma=false`, `physical_recoil_distribution=false`이며, source-consistent joint outgoing law 또는 실제 amplitude/event payload의 count/spin/exchange/support/frame/recoil 계약이 다음 입력이다. 이 국소 모델의 성과를 최신 DAG에 보존하지만 REC history interpolation의 독립 reference나 actual incident trace로 전용하지 않는다.

### REI: native HI 순간 strain response

새 [claim gate](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4/research/rei_source_pair_binding/hi_strain_response_20261025/execution_20261025/CLAIM_GATE.json)의 root 판정은 `ADMITTED_SCOPED_NATIVE_HI_STRAIN_RESPONSE`다. Source는 **HI/z=2.479의 4,368개 radial atoms**, mass string `510998.95069 eV`이며 CSV SHA256는 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`다. CSV와 별도로 선언한 isotropic angular closure를 사용한다.

[실제 report](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4/research/rei_source_pair_binding/hi_strain_response_20261025/execution_20261025/REPORT_KO.md)는 metric signature (-,+,+,+), 물리 orthonormal frame, volume dilution을 포함한 Bianchi I 순간 strain operator와 amplitude/mass/strain JVP를 명시한다. 저장된 W/S를 재사용하고 R/R_M을 결속하여 symmetric strain B에 대해 `δP = -C[(tr B)I+2B]/15`, `C=5W-R`를 얻었다. 이 국소 응답 계수가 새로 공급된 성과다.

단위는 target당 **birth proper-second**당 source coefficient다. 같은 birth epoch/frame의 source-weighted coeval cohort에 scalar amplitude를 곱하는 범위이며, 임의 birth history에는 별도 이력 적분이 필요하다. 실제 density, initial stock, source history, Bianchi a_i/H_i·frame·volume·proper clock는 이번 결과에서 임의로 선택하지 않았다. Claim gate는 actual HI history, actual density/initial stock/geometry/clock, applicable collision/stopping/photon-feedback를 계속 OPEN으로 둔다. `physical_secondary_heat`와 `global_physical_error_bound`는 null, `L4_ready=false`다.

현재 Git 계보에는 실제 Science S `190e283357f49f287ab02442a3751959cc53b4bd`와 Documents D `b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4`가 존재한다. 최종 delivery 문서의 actual C dual ACK와 S57 readback 기록을 읽었다. S의 18/20 및 D 문서의 conditional20/20/self-SHA-external 문구는 각각 해당 동결 시점의 기록으로 보존한다. 이번 조사에서 owner의 모든 S57/D 파일이나 외부 terminal companion을 다시 검증했다고 주장하지 않는다.

## REC PB01 / H5 / H6 / H7에 대한 결론

| 의무 | 새 source가 실제로 제공한 것 | 이번 결속 판단 |
|---|---|---|
| PB01 original source endpoint/query pullback | 새 owner 결과는 다른 source/domain의 독립 성과다 | 원 z≈1100, original313 source와 prior stable K_s를 사용하는 동결 범위를 유지. 새로운 source 대체나 재계산 사유로 전용하지 않음 |
| H5 physical interpolation error | CR finite-chain RR 및 HI 순간 strain의 scoped 성분; HE conditional amplitude model | 원 history의 같은 cosmology 독립 reference·endpoint uncertainty·whole-cell curvature/defect 또는 absolute physical bound를 공급하지 않음. 기존 null을 0이나 certified로 바꾸지 않음 |
| H6 actual incident trace / geometry owner | HI는 local orthonormal frame과 coeval strain response를 명시 | 실제 REC incident photon history, 선택한 Bianchi geodesic/direction/frame, measure/volume/clock/source/query owner 연결은 제공되지 않음. 별도 HISTORY02 owner와 기존 OPEN 유지 |
| H7 history composition | 새 HI strain/JVP 성과 존재 | REC PB01의 root 수락을 대신하지 않음. 기존 same-source J_s/K_s 결과는 재사용하고, PB01 observation은 accepted JSON 뒤에만 추가 |

이는 최신 source를 읽은 뒤의 의존성 해석이다. 새 성과를 과거 8e snapshot의 미완료 상태로 덮어쓰지 않으며, 도메인이 다른 scoped 성과를 REC의 실제 입력으로 자동 연결하지 않는다.

## 로컬 publication 준비본

`DAG_DONOR18_ONLY_SKELETON.json`은 최신 b24a DAG에 PR228 donor의 REC-LINE02 8 fields와 REC-HISTORY 10 fields만 그대로 이월한 **로컬 준비본**이다. `PB01` key는 없다. `PROJECTION_SKELETON_GUARDRAIL.json`은 다른 38개 현재 node, contracts/edges/authorities/statuses/root fields 보존과 donor18 무변경을 기록한다. 이 준비본은 publication 대상 최종 candidate가 아니다.

원 donor return 6개는 `../donor_return_recovery_20261025/DONOR_RETURN6_UTF8_BUNDLE.json`에 원 blob 그대로 준비되어 있다. Root가 accepted PB01 JSON을 공급한 뒤 REC-HISTORY에 한 항목만 추가하고, 실제 candidate의 의미상 diff가 두 REC observations 추가에 한정되는지 검사한다. Remote mutation·merge·activation은 이 준비 작업에서 수행하지 않았다.
