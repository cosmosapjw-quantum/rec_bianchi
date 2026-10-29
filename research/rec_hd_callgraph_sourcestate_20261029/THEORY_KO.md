# REC_HD_CALLGRAPH_SOURCESTATE01 | 이론 연구 R1–R10

**기준:** 2026-10-29 KST; REC PR158 최종 delivery HEAD `ee78d209281c28ad7b8a9fe04a1634da80b7ad54`, tree `888368d6bda8a84c730c5bff84c0eba1e4a462ce`. PR158 science HEAD `186002d66ed10d54b798e23949750d6593a1b535`. 독립 add-only 연구 대상으로, 어느 owner·production 분기도 변경하지 않는다.

## R1–R3. 문제, 출처, 불변 조건

기존 PR157 `source_policy_firewall.py` blob `e170417a8a205e17d45ae50e5c0f14641d020387`, 원본 owner `research/program_expansion_20261025/hd_adapter/lamda_hd.py` blob `632a8a094e7eedd24a1ec3132fec20765d6e39da`를 분리한다. 원본 LAMDA HD는 2,289 bytes, SHA-256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`로 잠겨 있다. CDMS 2011 v2 `.cat/.egy/.par/.fit/.lin` 원바이트는 현재 미확보이고 2019 `c003501.cat`는 2011 `c003501i.cat`와 동일하지 않을 수 있다. 원래 35 Hz gate는 J1만 통과하고 7/8 실패. 이 서술에는 이 단계를 새 spectroscopic fit·실험·열원이라고 부를 근거가 없다.

CDMS 공식 2011 archive index는 `HD.fit`, `HD.lin`, `HD.par`, `c003501.egy`, `c003501i.cat`(2011) 및 `c003501.cat`(2019)을 구분한다. 실제 각각의 원바이트 및 QN/TAG/uncertainty는 수집되지 않았다. 이전 recoil-only PR158은 단독 free-recoil 설명을 J2–J8에 대해 조건부로 배제했으나 fitting/covariance 원인을 확정하지 않았다. 새 목표는 **source-derived 물리량을 직접 소비하는 코딩 경로 중 어느 것이 opt-in source/policy bridge를 실제로 실행하는가**를 예측 가능한 최소 상태로 분리하는 것이다.

원칙: 좌표·프레임/단위/산술 정책을 바꾸지 않는다. `source_authentication`과 `physical_source_admission`은 다른 술어이고 `production`은 HOLD다. 다른 저장소 REI/BASS의 selected-He/Grackle provider는 HD 원분자 파일을 자동으로 소비한다고 보지 않는다.

## R4–R5. 경로 차단의 필요충분조건 (derived)

유한 directed *execution-event* graph `G=(V,E)`, 진입점 집합 `R`, 민감 소비자 집합 `C`, 성공적으로 완료해야 할 정책 이벤트의 집합 `P`를 정의한다. 원래 graph에서 도달 가능한 소비자에 대한 policy dominance 정의는 모든 유향 경로가 `P`를 적어도 한 번 거치는 것이다.

> **정리 (finite guard cut)** 모든 `R→C` 경로가 `P`를 통과함은 `G\P`에서 `R`로부터 `C`가 도달 불가능한 것과 동치다.

증명: guard 없는 경로가 있으면 그 경로의 모든 꼭짓점이 `V\P`에 있으므로 guard 제거 후에도 경로가 남는다. 반대로 guard 제거 후 도달 가능하면 원래 graph에도 같은 경로가 존재하여 `P`를 우회한다. 이 명제는 노드 하나의 dominator와 복수 policy-event cut 모두에 적용된다. **적용 범위**는 선언된 G 내부다. 빠진 FFI·dynamic getattr·generated caller가 하나만 있어도 전체 저장소의 sufficient claim을 입증하지 못한다.

**주의 (call graph ≠ sequential execution CFG).** `guarded_line_coefficients`는 `strict_bridge`를 먼저 호출한 다음 `module.line_coefficients`를 호출한다. 단순 function-call graph의 두 형제 간선만으로는 순서가 사라진다. 새 코드는 실제 pinned firewall의 Python AST에 대해 straight-line 함수의 guard-before-consumer 순서만 보수적으로 인증하고, if/try/loop 또는 동일 문장의 중첩 호출에는 인증을 거부한다. 이벤트 그래프에는 이 순서만 명시적으로 승격하며 다른 호출자는 승격하지 않는다.

## R5 별도: source-state closure와 반례 (derived)

`H = SHA256(raw)`와 `data.source_sha256=H`, `data.source_roundtrip()=raw`는 `data`의 모든 소비 필드가 원래 파싱과 같음을 **보장하지 않는다**. `dataclasses.replace`로 동일 frozen dataclass의 다른 `levels`를 만들되 원본 `_original_bytes`를 보존하면 해시 검사만으로 이 변경이 탐지되지 않는다. 즉 metadata/raw 보존은 source-state semantic identity보다 약하다.

추가 충분조건은 입력 바이트를 먼저 PIN으로 인증한 다음, 변조되지 않은 결정론적 owner parser `P`로 재파싱하여 `data == P(raw)`를 확인하는 것이다. `HDDataset`의 tuple 안 원자적/불변 필드에 대한 구조적 동등성 아래 소비 상태가 원본의 정규 파싱과 일치한다. 이는 고정된 parser/동시성/임의 monkeypatch 불허라는 threat model 아래의 충분조건일 뿐, 코드 실행 권한을 가진 악의적 공격자 전체를 방어하지는 않는다. 또한 물리적 정답·원본 CDMS v2 적합성을 승인하지 않는다.

## R6–R10. 검증과 판정

- R6: 같은 모델의 별도 반례검토; native 다른 저자 review NOT_RUN. 따라서 PARTIAL.
- R7: Python 512개 finite 3-node graph cut 경우 독립 DFS oracle 대조 PASS; Wolfram `FindPath[VertexDelete[...]]` 직접 bypass 존재, guarded-only 경로 제거 확인. 실제 source의 표준 Python AST guard-before-consumer 점검 PASS.
- R8: `source-state closure`는 synthetic owner fixture에 대해 테스트했으며 실제 LAMDA 2289-byte + owner module 결합은 NOT_RUN. `G`의 실제 소스 경로는 REMOTE_STATIC_INSPECTED. 결론은 `SCOPED_CONDITIONAL`, `production HOLD`.
- R9: 구현 계약 `src/guard_graph.py`의 `read_pinned_py`, `stage_guard_evidence`, `reachable_without_cuts`, `validate_source_state`; actual native source-verified `--owner` optional이며 소스가 없으면 fail-closed/NOT_RUN으로 둔다.
- R10: `REPORT_KO.md`, `CODING_KO.md`, `evidence/CALLGRAPH_RESULT.json`, `STAGE_LEDGER.json`, `HANDOFF_NEXT_THREAD_KO.md`로 봉인.

**원본 gate** 35Hz 7/8 FAIL, `H5_epsilon=null`, H6/H7 OPEN, L4=false, REI=false, production=HOLD, central DAG **28/88 (+0)**, REC physical **0/313 (+0)**. `ν_E≠ν_P` mismatch에 임의 heat source를 추가하지 않는다. CDMS v3 자동 대체 금지.

### 우선 참조

- https://github.com/cosmosapjw-quantum/rec_bianchi/pull/158
- https://github.com/cosmosapjw-quantum/rec_bianchi/blob/ee78d209281c28ad7b8a9fe04a1634da80b7ad54/research/rec_hd_native_policy_firewall_20261029/source_policy_firewall.py
- https://github.com/cosmosapjw-quantum/rec_bianchi/blob/ee78d209281c28ad7b8a9fe04a1634da80b7ad54/research/program_expansion_20261025/hd_adapter/lamda_hd.py
- https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
- https://home.strw.leidenuniv.nl/~moldata/HD.html
