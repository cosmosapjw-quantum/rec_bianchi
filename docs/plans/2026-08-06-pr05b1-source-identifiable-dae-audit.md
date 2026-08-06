# PR-05B1 Source-Identifiable DAE and Native-Radiation Time-Measure Audit

> **Execution rule:** follow test-driven development. Do not promote a local time derivative for an original-HyRec virtual spike unless its mass/time measure is source-identifiable.

**Goal:** Determine the source-identifiable differential/algebraic/memory roles of the October-2012 original-HyRec hydrogen variables, implement the resulting bounded DAE reference, and either close or rigorously block the requested time-dependent native-radiation replacement.

**Architecture:** Preserve the v0.58 `BackgroundSnapshot` and primitive-rate lock. Represent the original-HyRec local solve as a semi-explicit DAE in independent variable `eta=ln a`: free-electron fraction differential, 2s/2p and 311 virtual departures algebraic, and `Dfminus`/Lyman/average-radiation arrays as causal accepted-step memory. The local virtual-spike time derivative remains forbidden unless finite spike support or an equivalent photon mass measure is supplied by canonical evidence.

**Conventions:** metric `(-,+,+,+)`; ordinary frequency in Hz; `c,h,k_B` explicit; source temperatures in eV only inside the source adapter; no native-to-COM state remap; no fitted time scale.

## Task 1 — Source-role and provenance census

1. Lock source lines for `populateTS_2photon`, `solve_real_virt`, `fplus_from_fminus`, `Dfminus_hist`, `Dfnu_hist`, and `dxHIIdlna`.
2. Record the paper/supplement equations showing:
   - excited states are solved in steady state;
   - the delta-spike transfer equation neglects the local time derivative in the zero-width limit;
   - radiation time dependence is carried by causal redshift history.
3. Produce a typed row-role registry and a replacement ownership matrix.

## Task 2 — RED tests

1. Require exactly one local differential row (`x_e`) and 313 algebraic rows (`2s`, `2p`, 311 virtual states).
2. Require causal-history blocks to be outside the local mass matrix.
3. Require source `dxHIIdlna` parity at `z≈1300,1100,900`.
4. Require source residual and PETSc-shifted analytic IJacobian parity.
5. Require a fail-closed native-radiation mass audit and constructive non-uniqueness witness.
6. Require no compressed term to be removed and no future history endpoint to be accepted.

## Task 3 — Minimal implementation

1. Add `trajectory/time_dependent_native.py` with immutable schemas, source DAE residual, IJacobian, frozen-coefficient backward-Euler reference, restart and no-go audit.
2. Keep virtual rows algebraic and history state causal.
3. Implement no new normalization, cell edge, support width, or physical time scale.

## Task 4 — Independent validation

1. Wolfram: symbolic source residual, shifted Jacobian and finite-width mass dependence.
2. High precision: independently re-evaluate `dxHIIdlna` and the shifted solve with `mpmath`.
3. Verify dimension/sign/steady-limit checks.
4. Run Bianchi II, class-B `VI_h`, exceptional `VI_-1/9` fixed-local-state firewall.

## Task 5 — Decision and durable release

1. If finite native-radiation mass is not source-identifiable, issue `PASS_BOUNDED_NO_GO`, keep all four compressed terms active, and redirect PR-05B2 to the causal characteristic-history state.
2. Generate implementation, tests, formalism, source-line ledger, adversarial review, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, feature Git bundle, full recovery bundle and receipts.
3. Do not call PR-05B complete unless all requested compressed replacements are present in the same residual/Jacobian/conservation ledger.
