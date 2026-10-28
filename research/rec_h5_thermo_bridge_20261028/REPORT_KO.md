# REC-H5 THERMO-BRIDGE01 | 2026-10-28 결과 보고서

**판정: PASS_SCOPED_XE_AND_COMMON_SCALING.** 132개 보존점에서 ambient `xe` 미분과 `nH,H` 동시 로그 스케일의 정확한 실수-표현 항등식을 유도·계산했다. 이전 RESPONSE01의 80자리 수반 벡터를 재사용하고, 독립 primal 블록 풀이와 3점 SciPy sparse/80–120자리 계산으로 확인했다. **전체 6축 thermodynamic Jacobian, H5 물리 오차, H6 characteristic/frame, H7 전체 결합은 완료하지 않았다.** 생산 HyRec과 중앙 DAG는 변경하지 않았다.

## 원자료, 이어받기 및 비교

- Source anchor: `REC_H5_ELECTRON_RESPONSE01_SOURCE_20261028_f94fc8df8b8c.zip`, 17,077,105 bytes, SHA256 `f94fc8df8b8c523177183a2e56c09adac2d93284f5439b9304ef4ae14229e0f6` (ZIP CRC + 84 members verified). Published predecessor draft PR #147, head `f5e049ecc20ee7b20c4fcf89003d5d12d86bdcfa`.
- Source-locked computational module from PR #147: `incoming_response.py` SHA256 `ce47a2bc204c58c29cc0962aa78c2130e7381279953a78198d6de3fb693649ac`, used unchanged. Four PRIMARY shards and seven saved adjoint shards give exactly 132 matched writer records.
- PR #135, head `52226bb8d3ac99e7de2bd7934ab30e6fb3f257fe`, has a **previously completed six-primitive derivative at one point** for the *stable-source* operator. At index131 z=1099.9986525171403 the separately reconstructed current source-prefix model produces `-49.27609212008112` vs PR135 rounded report `-49.2760921201` (absolute `1.8879891e-11`). This cross-operator agreement **does not certify all six axes or common operator identity**.
- PR #136 already constructs stable-source K_s; PR #142 QSS regularity, PR #143 background jets and PR #145 fixed-reference thermal residual are complementary and are not rerun or combined as physical certificates.
- Prior upstream census: 51 accessible repositories, 2428 branches, 1192 open PRs, Dropbox /bianchi 105261 entries. This is prior-turn survey evidence, not a repeat of all file contents in this bounded unit. Newer changes must be rechecked before the next *new* unit.

## Main derivation and computation

At each frozen point, `M X=s0+G u`, `F=d+q^T X`, `b=(nH α2s xHII,nH α2p xHII,0,...,0)^T`. See THEORY.md for all assumptions.

`Dxe F = q^T M^-1 b - (b0+b1)/H = lambda^T b - (b0+b1)/H`, with `M^T lambda=q`.

Under real-model `nH,H -> e^t(nH,H)` at fixed other inputs,

`F(t) = e^-t [F(0)+(e^t-1)xe Dxe F]`; therefore `D_(ln nH+ln H)F = xe Dxe F-F`.

Pointwise scan across the stored redshift range (not a continuous physical enclosure):
- `Dxe F`: approximately `-49.27609212 .. -47.55970120`;
- `D_(ln nH+ln H)F`: approximately `-7.44835 .. -5.63872`;
- 132/132 source-locked point checks PASS with the unchanged, *scoped* `1e-60` absolute arithmetic gate.
- Maximum 80-digit saved adjoint/primal agreement `1.65e-75` absolute.
- Maximum xe finite increment (affine exact relationship) discrepancy `1.237220e-71` absolute.
- Maximum finite common-scaling identity discrepancy `1.55e-77` absolute.
- Maximum 313-row componentwise tangent backward ratio `9.57991e-80`.

Three representative points (indices 0/65/131) were independently assembled in SciPy sparse and recomputed at Decimal120. Float64 relative error to Decimal80 was below `3.114e-13` versus fixed gate `1e-9`; Decimal80 vs Decimal120 primal absolute gap was below `8.674e-76` versus fixed gate `1e-65`. This is numerical consistency, not proof of physical coefficients outside these points.

## Preserved failure, scientific review and plots

The initial Decimal120 independent validation demanded `1e-90` agreement against an **inherited 80-digit adjoint** and exited 1. This mixes provenance precisions. Its error and resource receipt are preserved in `results/primary_001/VALIDATION_INITIAL_FAILURE.md`. A diagnosed follow-up distinguishes the inherited 80-digit adjoint gate `1e-70`, the genuinely independent 80-vs-120 primal gate `1e-65`, and SciPy gate `1e-9`. The subsequent independent numerical checks pass. No failed *source residual* was reclassified or tolerance altered after observing a physical mismatch. Tests are different-domain comparisons.

Initial plot connected sparse redshift samples by lines, implicitly suggesting unmeasured continuity. That original PNG/PDF is preserved as `THERMO_BRIDGE_INITIAL`; the corrected saved-only plot `THERMO_BRIDGE.png` displays points without intersample interpolation. The lower panel has measured numerical residuals and the `1e-60` gate, not physical error bars. Figures were visually inspected; no output-level physics validation is inferred from them. Sign reversal and incorrect pure-H interpretation are negative controls; the latter is prohibited by the theory contract.

**Review independence:** original adjoint producer vs new primal method, independent SciPy sparse implementation, and Decimal80/120 arithmetic provide algorithm/precision diversity, but there was no separate new blind native reviewer, nor external model-family independence. `native_subagent: NOT_RUN / TOOL_NOT_EXPOSED`. Thus `PASS_SCOPED` is *computational scope*, not independent publication-grade science acceptance.

## DAG and resource claims

Canonical REC 28/88 (delta0); physical 0/313, H6/H7 OPEN, L4=false, REI_activation=false. This small defined research unit gives one explicit partial H7 building block, **not a completed canonical DAG node**. Do not add local R/C stage counts to the canonical 28.

One primary, one **failed independent validation**, one repaired independent validation, one original plot and one plot-format repair were run. They are retained separately. Measurement is per child process `/usr/bin/time` CPU/wall/RSS, not parent, model, connector, or full-turn cost; all unmeasured costs are UNKNOWN_NOT_ZERO. No native C, physical IVP, historical primary, original HyRec campaign or QSS03 certificate replay.

## Remaining minimal scientific work

Bind one common source/arithmetic identity for PR135's six-axis stable J_s and incoming K_s (PR136), or derive a source-prefix consistent full six-axis JVP at 132 points. Do not substitute one-point PR135 values for the other 131, or assume native prefix rounding differentiability. Then supply independently calibrated history `delta u` including retimed queries and the actual Bianchi/thermal-ODE derivative, plus source/endpoint error enclosures. Until then leave physical epsilon, defect, e0, tube, full H7 and fit readiness null/OPEN.

**누적 측정 child CPU:** 14.66초(첫 검증 실패와 원본·수정 그림 생성 포함), child wall-sum 11.93초, 최대 RSS 197220 KiB. 병렬/모델/connector 시간은 제외하며 0으로 간주하지 않는다.
