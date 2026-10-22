# 동시 진행 REC PR124 intake와 THERM02의 cohort 구분

확인 시점: **2026-10-23 02:47 KST**. 이번 intake는 GitHub 본문과
고정 commit의 계약·이론 문서를 읽은 문서 작업이다. 새 ODE, RHS 평가,
과거 suite 재실행은 모두 0회다.

## 실제 읽은 출처

1. [REC PR124 본문](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/124).
   GitHub API에서 실제 읽은 live HEAD는
   `e6ecef7624e39bee66b39e09d99fe355f76e2eae`, base는
   `04c0b10c1f1ec38d57c751369c553b638979e453`이며 draft 상태다.
   API의 `updated_at`은 `2026-10-22T15:48:24Z`다.
2. [PR124 FROZEN_CONTRACT.md — 위 HEAD에 고정](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e6ecef7624e39bee66b39e09d99fe355f76e2eae/research/rec_compton_coupled_20261022/FROZEN_CONTRACT.md).
   §2의 71개 UV bin, §4의 logT 방정식과 Jacobian, §5의 정확한 restart·8개
   configuration, §6의 saved/dense grid·유한 수용 기준, §7의 주장 범위를 읽었다.
3. [PR124 THEORY_KO.md — 같은 HEAD에 고정](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e6ecef7624e39bee66b39e09d99fe355f76e2eae/research/rec_compton_coupled_20261022/THEORY_KO.md).
   §2의 입자 열용량, §3의 서로 다른 photon/reference owner와 UV bin-centre
   moments, §4의 analytic Jacobian 한 행, §5의 affine 부분해, §7의 test-fluid
   에너지 owner를 확인했다.

아래는 connector가 반환한 UTF-8 문서 문자열의 byte 수와 SHA-256이다.
이는 이 intake의 읽기 identity이며 PR124 원격 전체 tree·raw·백업을 다시
검증했다는 뜻은 아니다.

| 읽은 문자열 | Bytes | SHA-256 |
|---|---:|---|
| 고정 FROZEN_CONTRACT.md | 14,924 | `5d7d27ade2c3924bc2df5b6b376a94aff3a788e36a7cab651ebcce03c55fcb92` |
| 고정 THEORY_KO.md | 22,202 | `8d4b29518a69c7d60898e90df8833d9b0409e2c61e2afef68c95545d3b304cd3` |
| live PR body 문자열 | 5,519 | `719d443e08dc95933b10b62a7f3152fa7472c5034a7dd15884ad78508aab60c0` |

PR124의 고정 계약 첫머리 `NEW_ODE_PENDING_PREFLIGHT`는 실행 전에 동결한
상태다. 현재 PR 본문은 **8개 새 IVP 완료와 보존된 결과·검토**를 보고한다.
이 서로 다른 시점의 표기를 혼동하여 PR124의 완료 계산을 다시 실행하지 않는다.
본 intake는 그 완료 보고를 관련 연구의 출처로 읽었으며 raw trajectory나
독립 검토를 재수행하지 않았다.

## 별도 연구 단위의 정확한 차이

| 항목 | REC PR124 | REC PR125의 현재 THERM02 |
|---|---|---|
| Unit | `rec_compton_coupled_20261022` | `rec_rei_thermal_compton_20261022` |
| 주된 기반 | PR122 omitted-budget 및 PR121 thermal-moments | 복구된 PR120 THERM01과 PR220 compact kernel; PR121 Mao source rows만 정확 재사용 |
| 주 상태 | native full63, 마지막 좌표 ℓ = ln T | compact34, 마지막 좌표 w = epsilon_th/k_B; 별도 full63/w oracle 1개 |
| 열변수 대응 | T = exp(ℓ), epsilon_th = (3/2)eta k_B T | w = (3/2)eta T, T = 2w/(3eta) |
| UV 지지집합·표현 | 5–200 eV, 기존 71 bin 중심 에너지·가중치 | 5–60 eV, 68 threshold-split bin 안의 GL4: 272 실제 node·가중치 |
| 초기 상태 | 저장된 Mao nominal의 exact full63 restart, donor index84 | z20에서 동결한 split 또는 isotropic 초기 상태 |
| 적분 구간 | z = 7.963732801243163 → 2; x0 = 0.8513356902116996 | z = 20 → 2; x0 = 0, x_end = ln 7 |
| 초기 온도 | 1081.319779971744 K | 1000 K |
| 비교 저장 grid | 109 nodes; 별도 513/1025 dense diagnostics와 accepted nodes | 193 nodes; 각 구간의 GL8/GL16 dense states와 별도 accepted BDF nodes |
| 정확한 cohort | 2 seeds × 2 Compton branches × nominal/refined = 8 | 5 nominal compact34 + 2 tight34 + 1 full63 oracle = 8 |
| Source 대안 | Mao hybrid만; 각 seed의 기존 no-Compton baseline 재사용 | Mao/off, Mao/hot, Mao/Planck, derivative/Planck, isotropic Mao/Planck 포함 |
| 새 nominal rtol | 2e-8 | 2e-9 |
| 정밀화 | rtol/atol을 10으로 나눔 | rtol/atol을 100으로 나눔 |
| 열항 구현 | logT RHS 및 full63 analytic Jacobian의 한 행 | 현재 상태의 w 열항 B−Aw; 기존 compact lift/restriction 유지 |
| 적분 에너지 수용치 | dense1025 absolute-throughput 기준 3e-4 | GL8/GL16 absolute-throughput 기준 3e-6 |
| 완료 근거를 읽은 범위 | live PR 본문의 8개 완료 보고 + 고정 계약·이론 | 로컬 SCIENCE_SUMMARY의 8개 PASS, 3개 refinement/oracle 비교 PASS |

각 논문의 Compton 식과 입자 열용량 원리는 재사용할 수 있다. 그러나
입력 UV 범위·quadrature·초기 상태·적분 구간·열변수·허용오차·진단 비용이
다르므로 위 두 계산을 동일 cohort, compact/full oracle 쌍 또는 공정한
속도 비교로 취급하지 않는다. UV 수치 moment나 궤적·에너지 적분값도
서로 복사하지 않는다. 두 개의 `8`을 현재 THERM02의 실행 수로 합산하지 않는다.

PR124가 새로 제안한 0-IVP diagnostics-equivalence/profiling 단위는 그
연구의 후속 계약이다. 현재 THERM02에 자동 편입하지 않는다.

## 재사용 가능한 물리 구조와 남은 의무

두 단위는 현재 기체 온도 → 재결합 수율 → 전자수 → 기존 elastic Thomson
opacity → 현재 photon moments의 결합을 유지한다. `actual_hot`은 현재
실제 photon 에너지의 leading thermal Compton 성분이고,
`planck_reference`는 독립적으로 지정한 등방 Planck bath다. 두 소스는
대안이며 동시에 더하지 않는다.

두 단위 모두 반대 부호 bath source를 transfer ledger에 기록하지만
Compton 에너지 source를 실제 photon hierarchy나 Einstein 방정식에
동적으로 넣지는 않는다. 국소 gas/bath 합의 영점, 또는 작은
|Q_C|/(H U_gamma)는 spectral/Einstein closure 완료나 그 오차 상한을
보장하지 않는다. matter와 radiation stress는 각각의 부호를 보존한다.

현재 THERM02의 다음 의무는 다음 두 source 계약이다.

- **N1 — Li final charge/state/energy partition:**
  에너지별 최종 전하·준위 단면적과 electron kinetic / residual level /
  escaping photon 에너지 배분의 정확한 수치 입력은 `MISSING_EXACT_INPUT`이다.
  5–60 eV의 실제 공명을 직접 1s-hole 문턱 폐쇄로 제거하지 않는다.
- **N2 — 실제 spectral recoil/induced 및 radiation-energy/Einstein backreaction:**
  기존 grey angular number/energy moments가 정하지 못하는 spectral 입력과
  충돌 source의 angular/energy ownership이 열린 상태다. 외부 Planck bath의
  recoil를 실제 photon field의 recoil 입력으로 대체하지 않는다.

다음 행동은 **새 ODE 0회인 source-bound provider contract 작성**이다.
이는 후속 실행의 승인이나 production 승격이 아니다. `NEXT_DAG.json`은
현재 local science 완료와 최종 게시·백업 미완료를 별도로 기록한다.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
REI 첫 실패 raw의 과거 local-only 보존 범위도 유지한다.
