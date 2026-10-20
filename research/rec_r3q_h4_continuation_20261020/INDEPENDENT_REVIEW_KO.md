# R3Q h/4 continuation 독립 검토 — 2026-10-20

**판정: PASS_SCOPED_TWO_STEP_CONTINUATION_AND_EXECUTION_HARNESS.** 최종 `smoke_003`의 두 accepted step, original C와의 같은 h/4 비교, source/start identity 및 제한된 실행 하네스를 수용한다. 첫 물리 event와 그 뒤 두 step은 아직 실제로 실행하지 않았다. 전체 h/4 이력, h/h2/h4 수렴, 기존 U5 gate, REI 활성화는 HOLD다. 이 검토는 새 장시간 계산을 실행하지 않았으며, 원 과학 suite도 반복하지 않았다.

검토자는 구현 작성자와 다른 agent이다. 새 runner/verifier/C harness/Python continuation, 사용된 원 `history.c`, 기존 h/4 start 및 비교 함수를 읽고 최종 source closure와 기존 산출물을 읽기 전용으로 대조했다. 작성자가 수행한 focused unit tests와 실제 smoke 실행을 검토자가 다시 수행했다고 기록하지 않는다.

## 확인한 identity와 산출물

- source base commit: `888d56d72579d1e1fd30f66abe02d9f91809a767`.
- 원 HyRec2012 ZIP SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- 독립 Python h/4 시작 checkpoint SHA256: `40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef`.
- 최종 source closure SHA256: `0332531f65a2851119f50806cdf7bc384b494b09759fcf5d497d6c1a7d032bcf`; 실제100개 파일 전부 일치.
- 최종 continuation producer SHA256: `ce80868c2882797a39986173e9ee053733d5f8c5439df819cac76ef2b5f0d58b`.
- 최종 C harness SHA256: `2453d3711751bd8221b4e89fb32bca53f6dc8942c33a970f4597dc421d2b50b1`.
- `smoke_003/TERMINAL.json` SHA256: `db2ede1c12e539558465b9bd64e5a7d6b52c686638f9067bc0a1540d85b1f21b`.
- `smoke_003/worker/verification.json` SHA256: `10fbb5cc9f26c5940d3bc7e53647234d0a418896f3645c1f8fb0f4aae3fd560e`.

원 ZIP과 실제 C build 추출본을 직접 비교했다. 바뀐 원본 member는 `HyRec/hyrec_params.h` 하나이며, 정확한 변경은 `DLNA 8.49e-5`를 `(8.49e-5/4.)`로 바꾼 것이다. `history.c`, `hydrogen.c`, `helium.c` 등 원 물리 source를 수정하지 않았다. compile에는 `-fno-fast-math`가 사용됐다. 단위·원 수치 허용오차를 느슨하게 바꾸지 않았다.

checkpoint는 index72892..72900의9개 node,8개 photon column, h/4=`2.1225e-5`, 실제 마지막 두 H/He derivative와 일치하는 final predictor를 갖는다. 모든 post-Saha flag는 시작 시 True다. 최종 결과의 첫8개 virtual/average/Lyman column은 checkpoint 값과 정확히 일치한다. Python은 그 checkpoint에서72900→72901→72902를 진행했다. C는 독립적으로 원 He prehistory와 첫8개 FULL step을 재구성한 후 같은 두 step을 계산한다. C state나 C photon field는 Python evolution 입력으로 주입되지 않는다.

## 검토 중 발견하여 교정한 사항

| 문제 | 교정 확인 | 검토 판정 |
|---|---|---|
| post-Saha FD와 native predictor seed의 `/2./delta`를 `/(2*delta)`로 재결합 | Python과 C 모두 원 source의 나눗셈 순서 복구 | CLOSED |
| H+He의 post-Saha-off branch가 xHII를 갱신한 뒤 neutral 값을 재구성 | 원 `get_rec_next2_HHe`처럼 xH1s를 직접 갱신하고 `xe=(1-xH1s)+xHeII` 계산 | CLOSED; 실제 event 전환 검증과는 별개 |
| worker가 성공 label을 쓴 뒤 budget exception을 만나도 label을 유지할 수 있음 | 모든 exception에서 FAIL 지정; supervisor도 first_failure가 있으면 거부 | CLOSED |
| kill 중 잘린 verification JSON이 supervisor를 종료시켜 TERMINAL을 잃을 수 있음 | missing/malformed/non-object receipt를 명시적 read failure로 보존하고 HOLD 판정 | CLOSED |

콜백 독립성도 확인했다. history 전달값은 detached copy이며, `dataclasses.replace(out)`는 `FullOutgoingAtomicResult.__post_init__`를 거쳐 배열을 다시 복사한다. 따라서 관측 콜백의 mutation이 다음 Python state/photon column을 바꾸지 않는다. forced non-post branch 시험은 그 산술 계약의 검사이고 실제 cosmological switch 관측으로 세지 않는다.

## 최종 실제 smoke의 의미

`smoke_003`는 `COMPLETED_SCOPED / SMOKE_ONLY`, first_failure=null이다. Python은2개 accepted step과8개 FULL source evaluation을 수행했다. event는 null이고 status는 `CAP_BEFORE_EVENT_PLUS_TWO`다. 최종 CPU는 supervisor 포함2.418778164s, wall2.522254687s이다. 기록된222298112bytes RSS는 최대 waited child의 값이며 동시 process-tree RSS 합계가 아니다.

검토자가 raw를 직접 세어 확인한 C 기록은 HE72893행, NODE1행, STEP10행, V3110행, A3110행, L30행, terminal EVENT1행이다. 이는8개 prefix+2개 새 step이다. HE72893행은 이번 comparator에서 모든 물리 field를 다시 독립 비교한 것이 아니며, 기존 독립 start 근거를 재사용한다. 현재 comparator는10개 FULL state 및 spectrum과 새 두 step의 RHS를 검사한다. 실제 native stdout/stderr, Python NPZ, 네 partial payload의 SHA와 prefix 보존을 직접 확인했다.

| 관측량 | 최종 기록 | 해석 |
|---|---:|---|
| xHII, xe, Tm 차이 | 0 | 같은 h/4의 제한된 구간 비교 |
| HeII 절대차이 | 5.421010862427522e-20 | 허용기준 이내 |
| integrated H RHS scaled차이 | 1.2790463133072194e-13 | 고정2e-7 기준 이내 |
| spectrum 최대 tolerance ratio | average7.883083461150054e-6 | 허용기준1 이내; 절대 occupation error가 아님 |
| common-input H RHS scaled차이 | 1.1258008414394283e-13 | 고정2e-10 기준 이내 |
| electron ledger residual | 2.6861108823328372e-17 | 고정5e-13 기준 이내 |

두 실제 event 선택(HeII cutoff 또는 H post-Saha off)과 `event+2`의 C/Python index 조건은 source 수준에서 일치한다. 그러나 현재 smoke에는 event가 발생하지 않았으므로 실제 event parity PASS를 부여하지 않는다. 같은 h의 C/Python 일치는 h/h2/h4 discretization 수렴이나 연속해 오차 상계가 아니다.

## 예산과 다음 실행 범위

새 smoke allocation60CPU/180wall, 새 event allocation600CPU/900wall은 기존 닫힌 U5 allocation을 재설정하지 않는다. 각 output은 create-only이고 원 실패·초기 smoke 근거를 보존한다. event mode의 제한은 추가 accepted step8192와 FULL evaluation32768이다. 어느 한도를 먼저 만나도 미완료를 완료로 승격하지 않는다.

resource 동작은 정확히 구분해야 한다. address-space limit2GiB는 **process별**이다. CPU는 parent+waited children의 측정값, 평가점/단계 경계의 cooperative guard와 최종 gate로 제한하며 child RLIMIT_CPU 자체는 process별이다. 이는 kernel 수준의 aggregate cgroup CPU hard limit이라는 뜻이 아니다. supervisor는 소유 process group의 wall timeout/실패 정리를 담당하고 malformed terminal을 과학 성공으로 받아들이지 않는다. 다음 NCP 실행 전에 실제로 배정된 단일 CPU로 affinity를 좁히고 다른 campaign을 보존해야 한다.

다음 허용 범위는 게시된 source/closure/checkpoint를 취득하고, 새 명시적 allocation에서 아직 안 된 first-event+two bounded job을 실행하는 것이다. runtime identity와 작은 환경 호환성만 재확인하고 원 start나 old science suite를 반복하지 않는다. 아직 미실행인 physical switch, full h/4 trajectory, h/h2/h4 convergence, q≠0 Bianchi extension, 최종 REI initial-condition 채택은 이 검토 후에도 각각 HOLD다.
