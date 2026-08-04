# Full Bianchi–HyRec 12-PR Completion Roadmap

> **For agentic workers:** Each PR requires its own detailed implementation plan and TDD cycle. Use `superpowers:subagent-driven-development` when subagents are available; otherwise use `superpowers:executing-plans`.

**Goal:** 검증 가능한 scalar Full Bianchi–HyRec solver를 12개의 독립 리뷰 단위로 완성한다.

**Architecture:** Exact local photon–atom events, adaptive harmonic radiation transfer, primitive HYREC rates, all-Bianchi tetrad characteristics를 명시적 interface로 결합한다. Completed HYREC \(T_{vv}\)를 lift하지 않고 primitive rates에서 time-dependent residual을 재조립한다.

**Tech Stack:** Python/NumPy/SciPy, C parity harness, Wolfram Language, Precise Special Functions, pytest, NPZ/CSV/JSON ledgers.

## Global Constraints

- Metric signature \((-+++)\).
- SI units in public event APIs; eV/cgs adapters are isolated to HYREC import.
- No free global normalization.
- No posterior matrix symmetrization or angular balancing.
- Exact red/interior/blue boundary ledger.
- All PRs require unit, sign, dimensional and limiting-case tests.
- Every PR updates the equation census and supersession ledger.

---

## PR-01 — Exact recoil event and four-force

**Produces:** exact covariant photon–hydrogen event map, PT-reverse reconstruction, same-event \(Q_\gamma^\mu=-Q_{\rm H}^\mu\), small-recoil expansion bridge.

**Consumes:** v0.32 finite-volume grid, v0.33 thermodynamic completion.

**Release gates:**
\[
\epsilon_{P^\mu}<10^{-12},\quad
\epsilon_{\rm mass-shell}<10^{-12},\quad
\epsilon_{\rm reverse}<10^{-11}.
\]
PR-1B additionally requires the exact-event Kramers–Moyal drift to approach v0.33 within \(10^{-6}\).

**Plugin use:** Wolfram for covariant identities; Precise Special Functions is not on the critical path here.

---

## PR-02 — Nonlinear anisotropic Bose collision

**Produces:** \(L=12/20/24\) harmonic-exact synthesis, nonlinear stimulated edge flux, entropy and positivity monitor.

**Consumes:** PR-01 event weights, v0.32 transform registry, v0.33 Bose affinity.

**Release gates:**
\[
\epsilon_{\rm BE}<10^{-12},\quad
\epsilon_N<10^{-12},\quad
\epsilon_Q<10^{-11},\quad
\dot{\mathscr F}\le0.
\]

---

## PR-03 — Full scalar COM–KHW amplitude

**Produces:** absolutely normalized
\[
2p\ {\rm pole}+{\rm crossed}+n\ge3\ {\rm bound}
+{\rm continuum}+{\rm seagull}
\]
event amplitude.

**Consumes:** PR-01 kinematics and PR-02 nonlinear action.

**Plugin use:** `Precise Special Functions` supplies independent high-precision real-axis \(\Gamma\) and \({}_2F_1\) references; Wolfram supplies complex-parameter analytic continuation; SciSpace tracks primary analytic matrix-element sources.

**Release gates:** gauge/low-energy/TRK/static-polarizability limits, continuum quadrature convergence, bound+continuum positivity.

---

## PR-04 — HYREC common-measure moment projection

**Produces:** projection from fine harmonic event kernel to native HYREC energy bins and \(\Gamma,M_1,\ldots,M_4\) comparison without a fitted scale.

**Release gates:**
\[
\epsilon_\Gamma<10^{-4},\quad
\epsilon_{M_2}<10^{-4}
\]
for first acceptance and \(10^{-5}\) science-core moment convergence.

---

## PR-05 — Primitive HYREC operator

**Produces:** time-dependent primitive atomic/radiation block from
\[
\alpha,\beta,R_{2p2s},A_{2s},A_{3s3d},A_{4s4d}.
\]

**Removes jointly:** Sobolev escape, native \(A_{1s}\) diffusion, escape-compressed \(T_{vv}\), scalar Ly\(\alpha\) feedback closure.

**Release gates:** Saha/Planck null, M-matrix/positivity, analytic Jacobian parity.

---

## PR-06 — FLRW monolithic parity

**Produces:** implicit scalar FLRW residual and Jacobian, native-HYREC regression, timestep convergence.

**Release gates:** rate snapshot parity, \(x_e(z)\) slice agreement, source and Jacobian residuals.

---

## PR-07 — Bianchi II class-A regression

**Produces:** nonlinear shear + tilt + boundary crossings coupled to PR-06 residual.

**Release gates:** frame, branch, number, four-force, positivity and timestep refinement.

---

## PR-08 — Class-B regression

**Produces:** Bianchi V or VII\(_h\) monolithic run with \(a_\alpha\)-dependent spatial characteristic.

---

## PR-09 — Exceptional \(\mathrm{VI}_{-1/9}\) regression

**Produces:** exceptional constraint and characteristic regression, no hidden generic-\(h\) assumption.

---

## PR-10 — All-11 automated sweep

**Produces:** I, II, III, IV, V, VI\(_0\), VI\(_h\), VII\(_0\), VII\(_h\), VIII, IX invariant/limit matrix.

**Release gates:** every type passes common conservation and type-specific registry tests.

---

## PR-11 — Equation, proof and provenance census

**Produces:** one self-contained equation ledger:
definitions, frames, characteristics, collision, atomic equations, constraints, limits, type adapters, proofs and source provenance.

---

## PR-12 — Performance and release integration

**Produces:** matrix-free execution, sparse Jacobian, checkpoint/state/manifest, restart tests, production claim gates and release package.

**Final release gates:** all prior tests, runtime recovery, deterministic manifests and documented scientific scope.
