# Frozen contract: Compton coupling to the native full63 gas system

Status: **ADOPTED_FOR_IMPLEMENTATION; NEW_ODE_PENDING_PREFLIGHT**.

Activated by the user's 2026-10-22 instruction to continue physics-based simplification and coding research inside the sandbox. Parent local commit: `3a5a853abb2eb0f67650288aa1cee82c576f9ffc`; parent draft PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/122.

The prior omitted-budget unit is immutable. This is a new research unit with its own finite execution allocation and preserved failure receipts.

This document adopts the previously reviewed finite calculation as the active implementation contract. New ODE work starts only after its algebra, full analytic Jacobian and inherited admission checks are reviewed.
Its quantitative basis is [the completed fixed-path budget](../rec_thermal_omitted_budget_20261022/results/budget_v1/SUMMARY.json)
and [the independent physics review](../rec_thermal_omitted_budget_20261022/REVIEW_PHYSICS_KO.md).

## 1. Scientific question and bounded scope

On the four primary saved paths, the identifiable hot-electron Compton
component removes about 2.58 eV/baryon over the restart-to-z2 interval,
roughly 30% of the existing primary photoelectron heating. Its fixed-path
forcing is too large to interpret by substituting a temperature correction
into the old trajectory. The next question is how temperature, charge state
and opacity change when this component is inserted into the coupled gas
equations and recomputed on the resulting states.

Use the **native full63** state:

- 40 inherited geometry/radiation coordinates;
- 21 native neutron and H1/D/T, He3/He4, Li6/Li7 ion coordinates;
- one accumulated Thomson optical depth coordinate;
- one log gas temperature coordinate.

The number/photo/RR/DR operators, isotope scales, UV prescription, signed
observables, and source coefficients retain their current owners. Use the
Mao-factor hybrid for RR energy loss with the original number rates.
No new rate-derivative RR cohort is needed for this finite question.
Neutron and tritium inventories remain exactly zero at initial and checked
physical states.

H/He CI/CE, Li CI/CE, charge exchange, free-free and other missing processes
are not silently activated. Re-evaluate the supplied CI/CE diagnostics on
the new saved states afterwards, with the existing source-domain and
continuation labels. Their small old-path budget is a prioritization result,
not proof of insignificance on every future trajectory.

## 2. Two explicitly different radiation-energy owners

The implementation must freeze one of the following labels in every case
receipt. Both branches also include the same inherited dilute external-UV
Compton term. Do not add the two CMB/reference terms together.

| Branch | Gas energy source | Radiation interpretation |
|---|---|---|
| actual_hot | \(Q_C=-4\sigma_Tc\,n_e k_BT U_\gamma/(m_ec^2)\) | Leading thermal Compton component of the evolving actual Bianchi photon energy monopole; full recoil/induced closure remains absent |
| planck_reference | \(Q_C=4\sigma_Tc\,n_e k_BU_{\rm ref}(T_{\rm ref}-T)/(m_ec^2)\) | Independently specified isotropic Planck thermal bath used in place of the first branch's CMB thermal term; not a reconstruction of the actual spectrum |

In actual_hot, evaluate

\[
U_\gamma(y,x)=\rho_{\rm crit,J}\Omega_\gamma
 \frac{E_{\gamma,0}(y,x)}{a^4}
\]

from the **current integrated state**, not the old saved radiation path.
The photon hierarchy can respond to the updated electron opacity through
its inherited elastic Thomson operator. This opacity response is distinct
from an energy backreaction due to Compton scattering.

In planck_reference, \(T_{\rm ref}=2.7255\,{\rm K}/a\) and
\(U_{\rm ref}=a_R T_{\rm ref}^4\) are the explicitly selected external
reference closure. The actual grey geometry hierarchy still evolves with
its inherited operators; do not relabel it as this Planck spectrum or add
the reference bath to the Einstein energy density.

For both branches,

\[
Q_{\rm UV,C}=\frac{\sigma_Tc n_e}{m_ec^2}
 \left(M_{\rm UV}-4k_BT U_{\rm UV}\right)
\]

uses the same 71 inherited 5–200 eV photon bins and prescribed UV amplitude.
Store its recoil and thermal components separately or store sufficient
moments to reconstruct them exactly. Reuse the verified low-occupation
definition and source constants. Do not infer a general CMB occupation
from the UV calculation.

For interpretation, evaluate both candidate CMB/reference expressions on
each saved state as diagnostics, even though only the case's selected
source enters its RHS. The identity

\[
Q_{\rm Planck,ref}-Q_{\rm actual,hot}
=-\frac{4\sigma_Tc n_e k_BT}{m_ec^2}(U_{\rm ref}-U_\gamma)
 +\frac{4\sigma_Tc n_e k_B U_{\rm ref}T_{\rm ref}}{m_ec^2}
\]

separates the replacement of energy density from the reference Planck
recoil/induced correction. Neither term identifies the missing recoil of
the actual grey photon field.

## 3. Chosen backreaction scope and exchange ledger

For this first finite pilot, retain the inherited **test-fluid gas-energy
approximation**. Add the selected Compton source to the gas thermal
equation. Do not insert an un-derived Compton source into only the photon
monopole and then claim a closed angular/spectral collision operator.
No Compton energy correction is fed into the photon hierarchy or Einstein
equations in this branch family.

This is a conditional thermal pilot. Its receipts must say that the
opposite radiation-energy source is tracked in a transfer ledger but is
not applied dynamically. At each state record

\[
Q_{\rm gas}=Q_{\rm abs}-Q_{\rm escape}+Q_C+Q_{\rm UV,C},
\quad
Q_{\rm C,bath}=-Q_C,
\quad
Q_{\rm UV,bath}=-Q_{\rm abs}-Q_{\rm UV,C},
\quad
Q_{\rm escaped}=Q_{\rm escape}.
\]

The sum is zero at the local source level. Binding energy remains inside
the gas store; existing Li core and recombination escape keep their prior
owners. Integrated transfer ledgers are not predicted photon energy
densities: cosmological and anisotropic radiation work has not been
applied to those bookkeeping integrals.

Also report the instantaneous ratio \(|Q_C|/(HU_\gamma)\), its integral
over x, and the existing test-fluid energy ratio. These measure the
exchange scale on the actual radiation trajectory. They are not an
automatic proof or rigorous bound for the neglected backreaction.
If the measured scale calls the test-field interpretation into question,
retain that finding and formulate a radiation-coupled successor; do not
declare physical closure because an algebraic ledger balances.

A fully energy-conserving radiation/Einstein extension would be a
different source contract requiring its angular and spectral ownership.
It is not a prerequisite invented to block the explicitly limited pilot.

## 4. Gas equation and Jacobian obligations

Let \(Q_0\) and \(\dot\eta_0\) be the existing photo/RR/DR kinetic and
particle sources. The new temperature equation is

\[
(\ln T)'=-2+
\frac{2(Q_0+Q_C+Q_{\rm UV,C})/(3k_BTn_b)-\dot\eta_0}{H\eta}.
\]

Compton scattering adds no ion/electron number source. Temperature changes
nevertheless alter the existing number rates, and the resulting electron
density alters opacity. Preserve these couplings in the full63 analytic
Jacobian; do not evolve temperature against a replayed old ionic history.

A useful independent derivative check uses
\(K=\sigma_Tc/(m_ec^2)\), \(x_e=q\cdot Y\). The added contributions are

\[
g_{\rm hot}=-\frac{8K U_\gamma x_e}{3H\eta},\qquad
g_{\rm Planck}=\frac{8K U_{\rm ref}x_e}{3H\eta}
 \left(\frac{T_{\rm ref}}T-1\right),
\]

\[
g_{\rm UV}=\frac{2Kx_e}{3H\eta}
 \left(\frac{M_{\rm UV}}{k_BT}-4U_{\rm UV}\right).
\]

At fixed \(Y\) and geometry, \(\partial g_{\rm hot}/\partial\ln T=0\).
For the reference and UV terms, only the displayed inverse-temperature
parts survive this partial derivative. The actual-hot branch also has a
direct derivative with respect to \(E_{\gamma,0}\), and all terms retain
the electron/particle-abundance and Hubble-denominator derivatives.
Check these identities, the complete 63-column Jacobian and selected
directional products at physical states before new ODE work.

Physical admission and the solver's smooth signed trial extension remain
distinct. Enforce exact zero native neutron/tritium at initial and checked
physical states; do not introduce a nuclear-energy interpretation for
off-manifold Newton or finite-difference trials.

## 5. Exact initial states and eight planned configurations

Use the two already paired seeds s03_m03_r03 and s04_m04_r04. They provide
continuity with the existing independent comparison, include opposite
small deviations of the photon monopole from the isotropic normalization,
and both have existing Mao nominal/refined no-Compton baselines.

For each seed, copy the exact initial full63 vector from its completed
Mao nominal thermal trajectory. Its origin is the donor's index 84:
\(x_0=0.8513356902116996\), \(z_0=7.963732801243163\),
\(T_0=1081.319779971744\) K. Verify exact equality of the corresponding
nominal/refined initial vectors. Continue to the same \(z=2\) endpoint.
No interpolation or early-prefix ODE produces a new initial state.
Elapsed_Myr and tau remain cumulative from the donor's \(z=20\) origin.

| Seed | Compton branch | Tolerance configurations |
|---|---|---|
| s03_m03_r03 | actual_hot | nominal, refined |
| s03_m03_r03 | planck_reference | nominal, refined |
| s04_m04_r04 | actual_hot | nominal, refined |
| s04_m04_r04 | planck_reference | nominal, refined |

This is **eight distinct new IVPs**, with no new no-Compton baseline run.
All completed REC126 and thermal8 trajectories are reused by identity.
The saved s00_m02_r02 case has zero initial shear and zero matter/radiation
stress targets, with matter_A = radiation_A = 0 in its
[donor receipt](../rec_rei_hheli_sandbox_20261021/results/pilot_v2/cases/s00_m02_r02/RESULT.json).
It can supply additional saved-state algebraic checks without another ODE.
An analytic FLRW-limit check should explicitly set shear and all higher
angular multipoles to zero and the normalized photon number/energy
monopoles to unity. Neither this limit nor numerical isotropy determines
the missing photon spectrum.

Nominal settings inherit rtol 2e−8, max_step 0.025 and the previous full63
atol vector: 40 geometry entries at 2e−11, 21 scaled species entries at
2e−10, tau at 2e−11, and logT at 2e−10. Refined settings divide rtol and
every atol by 10 and use max_step 0.0125. Both Compton branches receive
their own refinement pair.
No RR-alternative, parameter scan, opacity-off or nuclear cohort is
automatically appended.

## 6. Reuse, evidence and finite stopping rules

Freeze runtime modules, atomic/thermal/Compton source hashes, configuration,
initial vector hash, input NPZ/RESULT hashes and environment before running.
Only a completed result with an exact matching identity is reusable as that
configuration. Preserve partial/failure receipts; never overwrite an old
trajectory to make a comparison uniform.

The existing finite criteria come from the thermal-moments
[contract](../rec_thermal_moments_20261022/FROZEN_CONTRACT.md) and its runtime.
Carry them forward as numerical/admissibility checks, not new physical
promotion criteria:

- shared coefficient domain 100–1e6 K, no temperature floor or clipping;
  finite state, nonnegative electron density, exact-zero neutron/tritium;
- scaled populations at least −2e−8, isotope residual below 2e−7 and
  baryon residual below 2e−8;
- source-energy residual below 5e−12 relative to absolute source terms,
  now including the selected Compton/UV terms and their ledger;
- inherited tau, number-monopole, Einstein, tensor-sum, sampled angular
  positivity and trace-energy checks;
- same-branch nominal/refined maxima below 3e−5 in lnT and conditional
  ionic fractions, and below 3e−7 in tau and the existing signed six-vector.
  Report the stress-only subset separately from its shear coordinate;
- integrated gas-energy residual below 3e−4 of the absolute throughput on
  a 1025-node dense diagnostic grid; report the 513→1025 difference separately.

The new gas integral must include
\(Q_{\rm abs}-Q_{\rm escape}+Q_C+Q_{\rm UV,C}\) and the existing
\(3k_BT\eta\) work per baryon per x. Do not reuse the old no-Compton
integrand under a new label.

Persist the 109 comparison states and the actual 513/1025 diagnostic arrays,
source integrands, cumulative integrals and endpoint energies. Preserve
accepted BDF time/state nodes if available from the selected solver API,
and state exactly which sets receive admission checks. Do not claim
positivity for every internal trial or the entire continuum from a sampled
check. Do not rerun the old eight to recover their absent dense arrays.

Run serially with one numerical thread. Adopt the prior finite allocation:
240 s cooperative per-case wall cap and 1200 s total campaign wall cap,
including diagnostic processing. Record actual CPU/wall use. Failed,
resumed or retried work consumes the same allocation; do not reset the
budget, silently add configurations, or discard failure evidence.
Historical U5 budgets remain CLOSED_HOLD_NOT_RESET.

Stop the affected case on source/configuration mismatch, unsupported
temperature, integration failure, nonfinite state, failed inherited
admission, or exhausted budget. Stop completion/promotion of the cohort
when its required source, energy or refinement evidence fails. Diagnose
the concrete failure with retained evidence before any revised finite
contract; a large physical temperature change is not itself a failure.
No arbitrary small-effect threshold is introduced.

## 7. Required comparisons and completion meaning

Compare each new branch to the matching existing Mao no-Compton result,
and compare the two branches using both nominal/refined pairs. Report
temperature endpoint and sampled peak, ion fractions, electron density,
tau, signed stress/shear, Compton/UV transfer and total gas-energy residual.
Do not label a branch difference resolved unless it is distinguishable
from the observed refinement changes in both branches. Those changes
are finite numerical evidence, not global error bounds.

Re-evaluate the current source-bound omitted-process budget on the new
states with an explicit new-input adapter and identity. Do not mislabel
the old fixed-path integrals as energy actually exchanged on the new path.
Retain all unsupported-channel and empirical low-temperature obligations.

Completion means an implemented, source-frozen full63 Compton pilot with
its limited bath ownership, finite comparisons, saved diagnostic arrays,
visual review and independent implementation/results review. It does not
mean a fully closed CMB spectrum, radiation-energy/Einstein backreaction,
global convergence or a production model. Physical HOLD,
production NOT_APPROVED, global convergence NOT_RUN and
REI_activation=false remain.
