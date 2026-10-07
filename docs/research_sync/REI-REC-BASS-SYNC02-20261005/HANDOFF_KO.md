# rec_bianchi: REI-REC-BASS-SYNC02-20261005

REC의 기존 Peebles 공용 소스를 수정 없이 REI 별도 연구 crate에서 소비했고 pointwise boundary를 독립 검증했다.

입력은 `cd68764aacfeae9fe794d7966604ac6fbb80ba7f` / 기존 PR81다. 이는 publication commit과 별도다. 공통 Loop1 판정은 `CONFIRMED / PROMOTE_SCOPED_LOOP2_INPUTS`, 동기화 기록은 `state/LOOP1_SYNC.json`이다.

실제로 받은 결과:

- REC source cd68764aacfeae9fe794d7966604ac6fbb80ba7f 고정; native10tests + Decimal2170checks PASS.
- Collapsed source와 actual retained-ground source/defect를 구분하고 SI/cgs 경계를 명시.
- Selected-He V11 fixed-input port의 scoped pass를 수신; GateI/E1C까지 확대하지 않음.

남은 경계:

- retained n=2 trajectory/independent radiation temperature extension 미실행.
- REC selected-He consumer GateI와 E1C native/COM owner overlap 미완료.
- Cargo Git dependency resolution은 이번 실행에서 하지 않음; exact-source rustc 실행이 근거.

완료된 Loop2의 pure-H one-T prescribed FLRW 반환을 해당 benchmark 범위로 수신한다. 실제 EoR모형이나 full HyRec/COM 확장 필요가 생길 때 E1C의 정확한 owner-swap 계약을 별도로 호출한다.

병렬 후보:

- REC-RETAINED-TRAJECTORY-CONTRACT: consumer 필요가 확정되면 retained excitation/ground와 source ownership 계약; 현재 collapsed benchmark를 retained solver로 재명명하지 않음.
- REC-E1C-LEGACY: 명시적 native/COM split-domain 수요가 있을 때만 원 lane 재호출; 다중 atomic owner를 새 fastest path에 중복연결하지 않음.

보존: REC source bytes unchanged; one-T/pure-H/positive-H pointwise scope; selected-He GateI deferred; E1C callable unresolved original lane.

**Loop2도 완료했다.** 실제 REC→별도 REI 소비기→native RK4 이력→BASS opacity/세 clock visibility를 연결한 pure-H, one-T, prescribed matter-only FLRW(z1200→1000, 초기 xp=0.8) benchmark다. 이력3개와 constant-x control3개, 독립91검사를 통과했고 `PROMOTE_SCOPED_EXPANDING_BENCHMARK` 판정을 받았다. Fine-grid xp 최대절대오차1.9641732684760882e-11, 추가 optical depth 상대오차3.578215511124118e-7, 세 clock 간 tau 최대차4.440892098500626e-15다. 이는 EoR scenario/F05 enclosure/general Bianchi/finite-T admission이 아니다. Actual 결과는 `loop2/evidence/INDEPENDENT_HISTORY_RESULT.json`, 독립 판정은 `review/LOOP2_REVIEW.json`에 있다.

게시 위치는 `docs/research_sync/REI-REC-BASS-SYNC02-20261005`이며 atomic repo에는 같은 task ID의 `consumer_returns/` 연결을 추가한다. 기존 CURRENT/TASKS/원문/실패 receipt는 수정하지 않는다. 기존 branch에 non-force append하며 PR의 draft 상태를 유지한다.

공통 immutable URL: `https://github.com/cosmosapjw-quantum/rei_bianchi/blob/7c10471375837b85d58ec39fe1e8242429b74700/docs/research_sync/REI-REC-BASS-SYNC02-20261005/README_KO.md` — 고정된 최종 과학·계획 commit이다. 직접 ChatGPT 스레드 메시지 전송은 사용할 수 없어 수행하지 않았다. Git/PR handoff 준비와 각 스레드의 실제 수신 ACK는 별개다.

최종 동시 결과: FLRW06 prepared native gate를 실제컴파일/18record/167scalar로 완료했다. 다시 compiler대기 또는 미실행 후보로 선택하지 않는다. 별도 late_FLRW06 반환·review를 읽고 actual accepted-stage와 독립 U/edge 소비자 계약으로 이어간다. CR은 새F04D event jets 완료를 수신했고 다음F04E는 실제F05 receiverbinding을 기다린다.

최종 owner 수신: F05 actual7000steps/MPFI200PASS 완료, F08 conditionalstage140testsPASS·전체 pairedhistory미실행. 이는 `bda0feef` owner 반환 수신이며 여기서 재실행한 결과가 아니다. F04E는 actual F05 receipt와 연결하고 F08 source 동시 수정은 피한다. FLRW06은 양쪽 동시 완료를 하나로 합친다.
