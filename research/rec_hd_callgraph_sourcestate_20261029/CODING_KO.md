# REC_HD_CALLGRAPH_SOURCESTATE01 | 코딩 연구 C1–C10

**Execution mode:** isolated and read-only towards all existing project/owner files. Parent PR158 final `ee78d209281c28ad7b8a9fe04a1634da80b7ad54`.

C1–C3: 실제 REC/BASS/REI pinned tree와 원래 firewall/owner 핵심 함수 정적 조사. `rec_bianchi` tree 8748 entries, truncated=false; Python owner/guard 원격 blob 대조. `rec rust/rec_microphysics/ledger.rs`는 He ledger, `bass _rustcore/src/microphysics/rec.rs` selected He, `rei rust/rei_rec_source_adapter/src/lib.rs` selected He projection. 이들은 HD 회전선 원본을 소비한다는 증거가 아님. 완전 native dynamic callgraph는 미확인.

C4–C5: `src/guard_graph.py`는 source Git blob 신원, pinned Python AST straight-line 순서 검사, guard-cut BFS witness, opt-in `validate_source_state` deterministic owner reparse 비교를 제공. `src/run_guard_audit.py`는 선언된 scoped event graph와 PNG를 생성하고 `--owner`가 주어지면 owner의 실제 Git blob AST도 검증한다. 이 명시적 제한은 dynamic/FFI edge가 자동으로 “없는 것”이 되지 않도록 한다.

C6: **이번 세션 Python unittest 14/14 PASS**, `python -O` 14/14 PASS, `compileall` PASS. 64개 방향 그래프 x 8개 cut=512 complete adversarial cases, known bypass witness, cyclic graph, unknown branch fail-closed, fake digest/owner code/parsed-state mutation controls. 사전에 고정된 PR157 원본 firewall Git blob `e170417a8a205e17d45ae50e5c0f14641d020387`가 제공되는 경우만 실제 file AST 검증; 이번 세션에는 PR157 검증 ZIP에서 원본 추출을 사용했음.

C7: 실제 private 2,289-byte HD와 pinned owner 507-line module이 현재 로컬 checkout에 없어 `--owner` 전체 AST 및 native invocation **NOT_RUN**. user/source-provenance gate가 미완성인데 native physics behavior/physical admission PASS로 승격하지 않는다.

C8: 9-node scoped event graph PNG 생성하고 화면에서 topology/policy branch/직접 경로를 읽어 검사함. Synthetic topology, wall performance bench 아님: `PARTIAL_SYNTHETIC_ONLY`.

C9: 독립 저자 native review NOT_RUN; Wolfram은 별도 symbolic tool이지 별개 저자 아님.

C10: 전 단계 작은 source/test/checkpoint ZIP, SHA-256 및 CRC, checkpoint ledger, post-test final SOURCE ZIP. 원격 Git/Library/Drive/Dropbox ACK는 별도로 기록하고 검증된 것만 success 표기.

## 재현

```bash
ROOT=/path/to/REC_HD_CALLGRAPH_SOURCESTATE01
FW=/path/to/exact_PR157/source_policy_firewall.py
python3 -m unittest discover -s "$ROOT/tests" -v
python3 -O -m unittest discover -s "$ROOT/tests" -v
python3 -m compileall -q "$ROOT/src" "$ROOT/tests"
python3 "$ROOT/src/run_guard_audit.py" --firewall "$FW"
# 원본 507-line owner file을 SHA로 검증할 수 있을 때만:
python3 "$ROOT/src/run_guard_audit.py" --firewall "$FW" --owner /path/to/full/owner/lamda_hd.py
```

**위 `--owner` 검사는 로컬 full checkout 전까지 NOT_RUN이며 원본 private HD file replay가 아님.**
