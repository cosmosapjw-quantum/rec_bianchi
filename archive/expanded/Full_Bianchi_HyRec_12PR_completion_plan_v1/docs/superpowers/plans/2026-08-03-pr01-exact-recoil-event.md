# PR-01 Exact Recoil Event Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Steps use checkbox syntax.

**Goal:** Build a covariant exact elastic photon–hydrogen recoil event map, its reverse-event reconstruction, and a same-event photon/hydrogen four-force ledger.

**Architecture:** Public APIs use SI four-momenta \(p^\mu=(E/c,\mathbf p)\) with \((-+++)\). Scattering is generated in the initial atom rest frame, transformed back to the hydrogen frame, and independently reconstructed in the final atom rest frame. Event weights and frequency-cell deposition are intentionally deferred to PR-1B.

**Tech Stack:** Python 3.12, NumPy, pytest, Wolfram Language.

## Global Constraints

- Metric signature \((-+++)\).
- Keep \(c,h,M_{\rm H}\) explicit.
- No natural-unit public API.
- Normalize every photon direction and reject \(|\beta|\ge1\).
- Use the same event transfer to define \(Q_\gamma^\mu\) and \(Q_{\rm H}^\mu\).
- Tests must fail before implementation.

---

### Task 1: Four-vector primitives and Lorentz boosts

**Files:**
- Create: `src/full_bianchi_hyrec/recoil/four_vector.py`
- Create: `tests/recoil/test_four_vector.py`

**Interfaces:**
- Produces:
  - `minkowski_dot(p: NDArray, q: NDArray) -> float`
  - `photon_four_momentum(nu_hz: float, direction: NDArray) -> NDArray`
  - `atom_four_momentum(mass_kg: float, beta: NDArray) -> NDArray`
  - `boost_four_momentum(p: NDArray, beta: NDArray) -> NDArray`
  - `inverse_boost_four_momentum(p_rest: NDArray, beta: NDArray) -> NDArray`
  - `atom_beta(P: NDArray) -> NDArray`

- [ ] Write failing tests for photon nullness, atom mass shell, boost round trip and direction normalization.
- [ ] Run `pytest tests/recoil/test_four_vector.py -v`; confirm missing-module failure.
- [ ] Implement the minimal functions.
- [ ] Re-run tests and require all PASS.
- [ ] Commit `feat(recoil): add SI Lorentz four-vector primitives`.

---

### Task 2: Exact recoil scattering event

**Files:**
- Create: `src/full_bianchi_hyrec/recoil/event.py`
- Create: `tests/recoil/test_event.py`

**Interfaces:**
- Produces:
  - `RecoilEvent` dataclass with `P_i,k_i,P_f,k_f,nu_in_rest,nu_out_rest,mu_rest`.
  - `scatter_elastic(P_i, k_i, outgoing_direction_initial_rest, mass_kg) -> RecoilEvent`.
  - `event_residuals(event, mass_kg) -> dict[str,float]`.

**Required equation:**
\[
\nu_f^*=
\frac{\nu_i^*}
{1+\frac{h\nu_i^*}{Mc^2}(1-\mu^*)}.
\]

- [ ] Write a failing rest-atom backscatter test.
- [ ] Assert exact Compton frequency, four-momentum conservation, null photons and final mass shell.
- [ ] Implement the minimal event generator.
- [ ] Add moving-atom random-event tests with deterministic seed.
- [ ] Require maximum relative invariant residual \(<10^{-12}\), allowing a separately reported cancellation floor for the raw SI mass shell.
- [ ] Commit `feat(recoil): add exact elastic photon-hydrogen event`.

---

### Task 3: Reverse-event reconstruction

**Files:**
- Modify: `src/full_bianchi_hyrec/recoil/event.py`
- Create: `tests/recoil/test_reverse_event.py`

**Interfaces:**
- Produces:
  - `reconstruct_reverse(event, mass_kg) -> RecoilEvent`
  - `reverse_residuals(forward, reverse) -> dict[str,float]`

- [ ] Write a failing test that takes the forward final atom/photon as reverse input.
- [ ] In the final-atom rest frame, use the Lorentz-transformed original incoming photon direction as the reverse outgoing direction.
- [ ] Require recovery of \(P_i,k_i\) with relative error \(<10^{-11}\).
- [ ] Commit `feat(recoil): verify exact reverse-event kinematics`.

---

### Task 4: Same-event four-force ledger

**Files:**
- Create: `src/full_bianchi_hyrec/recoil/four_force.py`
- Create: `tests/recoil/test_four_force.py`

**Interfaces:**
- Produces:
  - `event_transfer(event) -> tuple[delta_p_gamma, delta_P_atom]`
  - `four_force(event_rate_m3_s, event) -> tuple[Q_gamma,Q_atom]`

- [ ] Write a failing test for \(\Delta p_\gamma^\mu+\Delta P_{\rm H}^\mu=0\).
- [ ] Implement transfer from the stored event only.
- [ ] Test sign of atom energy gain for rest-frame backscattering.
- [ ] Commit `feat(recoil): add same-event photon-hydrogen four-force`.

---

### Task 5: Small-recoil and v0.33 bridge

**Files:**
- Create: `src/full_bianchi_hyrec/recoil/small_recoil.py`
- Create: `tests/recoil/test_small_recoil.py`
- Consume: `Full_Bianchi_HyRec_C3B2B1D0_thermodynamic_completion_v0_33/thermodynamic_completed_kernel.npz`

**Interfaces:**
- Produces:
  - `recoil_series(nu_in, mu, mass_kg, order=2)`
  - `rayleigh_phase_mean_recoil(...)`
  - `compare_to_v033(...) -> ledger`

- [ ] Test the first- and second-order series against exact scattering as \(h\nu/(Mc^2)\to0\).
- [ ] Integrate the Rayleigh phase and recover \(\langle1-\mu\rangle=1\).
- [ ] Build the thermal Hummer-event bridge and compare line-centre drift to v0.33.
- [ ] Require the exact-event small-recoil drift to approach v0.33 within \(10^{-6}\).
- [ ] Commit `test(recoil): lock v0.33 small-recoil limit`.

---

### Task 6: Durable scientific artifact

**Files:**
- Create: `artifacts/PR01_exact_recoil/PR01_ledger.json`
- Create: `artifacts/PR01_exact_recoil/EXACT_RECOIL_FORMALISM.md`
- Create: `artifacts/PR01_exact_recoil/event_regression.csv`
- Create: `artifacts/PR01_exact_recoil/MANIFEST_SHA256.txt`

- [ ] Run the complete pytest suite.
- [ ] Run Wolfram symbolic mass-shell and reverse-event identities.
- [ ] Record dimensional, sign and limiting-case checks.
- [ ] Package the artifact and verify ZIP integrity.
- [ ] Commit `docs(recoil): publish PR01 exact-recoil ledger`.
