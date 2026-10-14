# REC R8 → REI Codex: 실제 accepted clock 오류와 최소 safe 통합 경로

2026-10-14 KST. 먼저 **현재** `STATE.json`, `RETURN_CONTRACT.json`, 현재 Git HEAD/dirty tree, process/checkpoints, `BACKGROUND_TABLE_001` / `BACKGROUND_EXACT_CACHE_001` / 새 원자율 온도테이블의 실제 owner authority를 다시 읽는다. 2026-10-14 21:53 KST의 REI 게시 HEAD는 `45f166adee36d57cabe712ff66209926d1aa1556`이었다. 이 handoff는 기존 실행이나 권한의 자동 변경이 아니다.

이번 REC R8은 이미 종료한 `ZERO_composed_001`, `SHEAR_PLUS`, `SHEAR_MINUS`의 accepted 102개 sample만 사용했고 그 중24개의 짧은 step `dt_saved`가 독립 local H-model 적분 대비 상대 `1e-8`을 초과함을 관측했다. q=+0.01 step100에서 `a1=0.04761905043465769`, `a2=0.04761905047098814`, `dt_saved=6446090.361918509s`, reference `6446090.4791734519898...s`, relative `-1.81900864348934e-8`. `log(a2/a_ref)-log(a1/a_ref)`와 `log1p((a2-a1)/a1)`의 직접 비교가 `-1.8189893480347e-8`을 재현한다. 실제 관측된 작은 clock 오류의 원인을 `log` cancellation으로 분류할 매우 강한 근거이나 physical chemistry failure/signed detection은 아니다.

**실행 우선순위:**

1. 동시 실행 중인 original signed case/observer를 건드리지 않는다. AX07 scoped 완료, AX08 진행, AX11·AX12 PENDING을 오염시키지 않는다. 다른 팀이 이미 통합한 HE R8 reducer/source guard나 온도별 atomic rate table component를 다시 개발하지 않는다.
2. **기존 stable polynomial interval 먼저:** 이미 `BACKGROUND_TABLE_001`가 보유하고 검사를 통과한 `log1p` 폭 + factored polynomial increment를 참고한다. 현재 `Driver::tentative`의 `point_at_scale(a2).time_s - point_at_scale(a1).time_s` 등 모든 실제 누적 subtraction을 inventory한다. Baryon source, photons, ray map, ledger에 쓰는 same interval을 명시적으로 유지한다. Source/model identity와 output binary를 새로 결속한다.
3. **대안 rate-Hermite:** R7B positive integrand `F(L)=1/H`, `db/dL=sF`는 수학적 uniform ideal relative bound ε1024<3.080731e-10, ε2048<1.921401e-11. 새 production integration에는 node/slopes/libm/float evaluation과 actual step/ledger comparison이 추가로 필요하다. 단지 R7B proof가 있다는 이유로 기존 `SHORT_STEP_SUBTRACTION_HOLD`를 제거하지 않는다.
4. **시험 범위(새 owner 승인 시에만)**: (a) 동일 actual input 102 step local quadrature relative error <= 기존 frozen criterion (기존 component comparison gate 1e-9를 사용한다면 그 gate) 및 positivity, (b) 작은 first/late selected accepted step의 coupled gas/photon/ledger overlap, (c) photon energy/angle finite map·signed q parity, (d) source/clock consistency, (e) 새 executable identity와 finite resource accounting. 새 방법은 old history bitwise parity가 아니라 source-equivalent convergence/residual 검사를 사용한다. 변경점이 없을 때마다 old heavy suite를 재실행하지 않는다.
5. **Exact cache는 독립:** 기존 `BACKGROUND_EXACT_CACHE_001`의 목표는 bit-identical speedup이며, 이 clock-error 수리를 그 계약 안에 섞지 않는다. Cache를 쓴다고 잘못된 누적 차분이 고쳐지는 것은 아니다.

`theory/R8_REPORT_KO.md`의 식 `R8-E01–E03`와 `results/GLOBAL_CLOCK_CONDITIONAL.json`은 **조건부** clock upper budget이다. 노드/roundoff 실제 오차를 자동으로 채우지 않는다. 현재 R8의 실제105? 아니고 정확히 102개 selection,24 exceed는 sampled diagnostic이며 모든 accepted step의 supremum이 아니다. `code/audit_saved_steps.py --repo-root <REI_ROOT> --out <NEW_OUTPUT_DIR>`로 원본 SHA를 검증하여 재현할 수 있다. 동일 source를 그대로 사용하는 한 같은102개를 무의미하게 재실행할 필요는 없다. Source/model이나 native interval 구현이 달라진 경우에만 새 결과를 만들고 old failures를 별도 보존한다.

**Ready only as supplier:** `REC_R8_NATIVE_CLOCK_DIAGNOSTIC_INGEST`, `REC_R8_FINITE_INCREMENT_CONTRACT_INPUT`. Canonical AX11/12, current worker, accepted scientific claim, resource limit과 owner execution authority는 변경하지 않는다. 새로운 full-history, empirical upper bound, observer optical history 및 궤도/광학깊이 검출은 주장하지 않는다.
