# THERM02 R4–R5 / C1–C3 design intake

Date: 2026-10-22 KST. Author: `/root/thermal02_design`.
Evidence status: source/code **read**, equations below **derived**; no code
implementation, ODE, old test suite, benchmark or scientific data regeneration.
The user's supplied workflow 1.0.0 / approval 0.2 governs this task.

## 1. Source and cohort identities

The local immutable donor is THERM01, REC PR120 final commit
`7c4af579be508cccf203d3e2a3a5aa16a4b28e38`, unit
`research/rec_rei_thermal_yield_20261022`. Its eight finished histories and the
REC126 / REI129 / warm729 histories remain untouched.

New read-only upstream evidence:

- REC PR122 commit `04c0b10c1f1ec38d57c751369c553b638979e453`,
  `research/rec_thermal_omitted_budget_20261022/NEXT_UNIT_CONTRACT.md`,
  `THEORY_KO.md`, and `code/compton_budget.py`.
- PR122's future eight-IVP contract uses full63, log(T), a 5–200 eV source,
  and the saved restart at z=7.963732801243163 (109 comparison nodes).
  Its Compton branches are actual_hot and planck_reference, each paired with
  the original UV Compton source. It is marked FUTURE_ODE_NOT_RUN.
- THERM02 as proposed by root uses z20→2, 193 nodes, THERM01's 5–60 eV GL4
  continuum and w coordinate. It is a distinct new source/cohort, not an
  execution or completion claim for PR122's planned cohort.

The new source researcher owns primary-literature verification and Mao2017
coefficient intake. This design does not treat PR text alone as independent
physical validation of those coefficients.

## 2. Existing code path and exact coupling points

THERM01 `code/thermal.py` lifts compact34 to full63 before evaluating a point.
The full state is 40 geometry coordinates, 21 scaled populations, tau, and
w=epsilon_th/kB. Geometry uses 23 even coordinates; nine independent elemental
charge fractions reconstruct the 21 populations. `R_EXT` and `P_EXT` append an
identity map on w to PR220's R/P maps.

`ThermalSystem.point(x,state)` computes current Y, eta, T, UV amplitude, nb,
atomic number/thermal terms, and current geometry fields. Its `full_rhs_from_point`
uses current ne in `Geometry.rhs_from_fields`, current chemistry/H for populations,
and current ne/H for optical depth. The existing thermal equation is

\[
w'=-2w+(Q_{photo}-Q_{rec})/(n_b k_B H),\qquad
T=2w/(3\eta),\quad \eta=(1+q)\cdot Y.
\]

Add new Compton terms only to this w equation and new diagnostics/ledger sources.
No direct Compton source is added to Y, eta, or tau. Nevertheless T changes RR/DR
number rates, which change ne and opacity, the photon angular hierarchy, its
energy monopole and geometry. This feedback is retained by evaluating every
quantity from the same current state. Replaying an old Y or photon path would
solve a different problem.

The inherited geometry evaluates separate matter, photon and neutrino stresses;
their signed sum and separate diagnostics remain intact. Compton uses the photon
energy monopole, never Omega_r or photon+neutrino energy.

## 3. Units, signs and field ownership

All powers below are proper W/m^3, positive into the gas. Define

\[
K=\frac{\sigma_T c}{m_ec^2},\quad x_e=q\cdot Y,\quad n_e=n_bx_e,
\quad U_\gamma=\rho_{crit,J}\Omega_\gamma E_{\gamma,0}/a^4.
\]

Use the existing photon owner `geometry.model.omega_gamma`,
`geometry.source.rhocrit_j_m3`, and full-state index 4. Inherited `coupled.THOMSON`
is already `GAMMA_PER_NE/1e6 = sigma_T*c` in m^3/s. Multiplying that by c again is
a dimensional error. Use one explicit owner for sigma_T*c and electron rest
energy, with a cross-check against the imported source constants.

The actual_hot source is

\[
Q_C^{hot}=-4K n_e k_BT U_\gamma.
\]

It is the identifiable leading thermal term for isotropic non-tilted,
nonrelativistic electrons scattering Thomson-energy photons. It uses the actual
evolving photon monopole even for anisotropic incident radiation. It omits the
actual spectrum's recoil and induced-scattering term.

The alternative Planck reference owns its own field:

\[
T_{ref}=T_0/a,\quad U_{ref}=a_R T_{ref}^4,
\quad Q_C^{ref}=4K n_e k_B U_{ref}(T_{ref}-T).
\]

This bath is external to the grey hierarchy and Einstein density. It replaces
the actual_hot source in a case; the two are never summed. The reference bath
does not identify the actual anisotropic field's missing spectrum.

For the supplied dilute UV source,

\[
U_{UV}=c^{-1}\sum_j\Phi_j E_j,
\quad M_{UV}=c^{-1}\sum_j\Phi_j E_j^2,
\quad Q_{UV,C}=K n_e(M_{UV}-4k_BT U_{UV}).
\]

Here Phi_j are THERM01's actual GL4 quadrature flux weights, E_j are its node
energies in joules, U is J/m^3 and M is J^2/m^3. Both moments are linear in the
prescribed UV amplitude. Prepare their unit-amplitude values once and multiply
by that amplitude in the RHS. This reduces spectral contractions to two scalars
without changing the source quadrature, number rates or photo-heating.

**Adapter incompatibility:** PR122's `uv_reference_moments` validates one energy
per bin, `len(edges)==len(energy)+1`, and exact bin-integrated power-law flux.
THERM01 has four GL nodes per threshold-split bin. Its arrays cannot be supplied
to that bin-centre validator. A new GL-weighted adapter must preserve the actual
nodes/weights and independently compare its U/M with continuous power-law
integrals, without relabelling the old 71-bin 5–200 eV moments as current input.

## 4. Derived affine reduction and useful exact subflow

At fixed x, geometry and Y, put U_* = U_gamma for actual_hot or U_ref for the
Planck branch, and R_* = 0 or 4U_ref T_ref respectively. Then

\[
\Delta w'_C = B-Aw,
\quad A=\frac{8Kx_e(U_*+U_{UV})}{3H\eta},
\quad B=\frac{Kx_e}{H}\left(R_*+\frac{M_{UV}}{k_B}\right).
\]

A is dimensionless per x and B has units kelvin per x. With adiabatic work,
the frozen subproblem is w' = -(2+A)w+B. It has the stable solution

\[
w(x+h)=e^{-dh}w(x)+\frac{B}{d}[-\operatorname{expm1}(-dh)],
\qquad d=2+A.
\]

If adiabatic work is excluded from the test, use d=A and the continuous A→0
limit w(x+h)=w(x)+Bh. A>=0 and B>=0 make this frozen Compton/adiabatic map
positivity-preserving for h>=0 and nonnegative initial w. This is a derived
frozen-coefficient subflow, useful as an independent algebraic/numerical fixture
and possible future preconditioner. It is not the exact solution of the full
changing-Y, changing-H, changing-radiation, photo/RR/DR system. No splitting
integrator is required to obtain the constant-cost RHS reduction.

At fixed geometry and Y, the new w Jacobian entry is exactly -A. For a native
unscaled population Y_i,

\[
\partial_{Y_i}\Delta w'_C=
\frac{K}{H}\left[q_i
\left(R_*+\frac{M_{UV}}{k_B}-\frac{8U_{tot}w}{3\eta}\right)
+\frac{8x_eU_{tot}w}{3\eta^2}(1+q_i)\right],
\quad U_{tot}=U_*+U_{UV}.
\]

Multiply by the corresponding isotope scale for a derivative with respect to
the stored population coordinate. At fixed x the geometry derivative is

\[
\partial_{y_j}\Delta w'_C=-\Delta w'_C\,\partial_{y_j}\ln H
-\mathbf1_{hot}\frac{8Kx_e w}{3H\eta}\partial_{y_j}U_\gamma.
\]

The second term is directly nonzero only for full geometry coordinate 4,
where dU_gamma/dy4 = rho_crit,J Omega_gamma/a^4. The inherited geometry helper's
`hgrad` is d ln(H)/dy. Reference/UV quantities depend explicitly on x but do
not depend on geometry state at fixed x. Existing atomic/thermal Jacobian
dependence on T(Y,w) remains necessary if an analytic Jacobian is introduced.

## 5. Why compact34 remains an invariant restriction

The new temperature is a common scalar, and the new Compton term depends only on
eta, xe, the scalar photon energy monopole and prescribed scalar UV moments.
It introduces no odd angular multipoles and no isotope-specific electronic
rates. If the Mao factor is indexed by the same element/charge pair for all
isotopes, the electronic equality classes used by P remain invariant. Zero
neutron/tritium remains invariant because no new number process is introduced.
Thus, for this declared model, full RHS F obeys F(Pv) in the image of P and the
compact RHS is R F(Pv), with the w identity block unchanged. The full63 oracle
checks its finite numerical realization, while the invariant argument explains
why that comparison is meaningful.

Do not reuse an old analytic Jacobian unchanged. A numerical BDF Jacobian can
remain the baseline if measured cost is within the finite sandbox budget. The
minimal mathematical optimization is scalar moment contraction plus unchanged
projection/lift, not an unvalidated new stepping method.

## 6. Correct gas and bath ledgers

The gas store includes thermal and ionic-potential energy. It obeys

\[
\dot\epsilon_{gas}+2H\epsilon_{th}
=\frac{Q_{abs}-Q_{escape}+Q_C+Q_{UV,C}}{n_b}.
\]

At a local state, source accounting is

\[
Q_{gas}=Q_{abs}-Q_{escape}+Q_C+Q_{UV,C},
\quad Q_{C,bath}=-Q_C,
\quad Q_{UV,bath}=-Q_{abs}-Q_{UV,C},
\quad Q_{escaped}=Q_{escape},
\]

whose sum is zero. No Compton number source belongs in eta-dot. Existing binding
energy, RR/DR escape and any explicit channel exclusions keep their owners.

The integrated gas residual on a saved x grid is

\[
R_E=\epsilon(x)-\epsilon(0)-A_{abs}+A_{escape}+A_{work}-A_C-A_{UV,C},
\]

where A_power = integral Q/(nb H) dx and A_work = integral 2 kB w dx. Preserve
signed CMB/UV transfers separately. For an absolute-throughput denominator,
integrate absolute instantaneous contributions; abs(cumulative signed transfer)
can hide cancellations. A compatible denominator is max(|epsilon0|,|epsilon|,
integral [|Qabs|+|Qescape|+|QC|+|QUV,C|]/(nb H) dx + integral 2|kB w| dx).
Declare the denominator before execution. If it differs from THERM01's
nonnegative-source expression, record the generalization and retain its old
scope; do not silently rename a changed gate.

Bath transfer integrals are bookkeeping energy/baryon, not evolved photon
energy densities; no cosmological/anisotropic radiation work is included in
those integrals. This pilot keeps the test-fluid gas approximation and the
elastic grey hierarchy. Adding an arbitrary photon-monopole source alone would
not provide the missing angular/spectral Compton operator.

Report |QC|/(H U_gamma), its x integral and the existing trace-energy ratio.
For planck_reference, additionally report |QC|/(H U_ref): the first normalizes
an external reference exchange by the actual field, while the second uses its
own declared bath. These are exchange-scale diagnostics, not rigorous neglected
backreaction error bounds.

## 7. Proposed finite scope and validation

Root's proposed new eight-IVP set has five nominal histories:
split/Mao/off, split/Mao/actual_hot, split/Mao/planck_reference,
split/derivative/planck_reference, and isotropic/Mao/planck_reference;
two tight34 histories for the split Mao hot/reference branches;
and one full63 split Mao Planck oracle. All use new identities and z20→2.

This separates RR-source sensitivity (Mao-off versus the preserved THERM01
derivative-off; Mao-reference versus derivative-reference) from Compton coupling
(Mao-off versus the two new Compton branches). It gives each Compton branch a
refinement check before interpreting their difference. No old no-Compton IVP is
rerun. The new Mao-off IVP is distinct because its energy closure changes.

Before science, freeze units/constants, UV nodes/weights, Mao row mapping,
current THERM01 source identities, ICs and all tolerances. Root proposes nominal
rtol 2e-9, inherited atols/10; tight tolerances divide this by 100, max_step
0.025 nominal and 0.0125 tight. Keep the 3e-6 integrated energy gate and existing
finite invariants; changing tolerances prospectively does not reinterpret old
3e-6 results.

Targeted new checks, with no old-suite replay:

1. Units and sigma_T*c ownership; ne=0 yields exact zero Compton terms.
2. Planck T=Tref equilibrium; hot remains negative at T=Tref, so branches are
   distinguishable. Opposite thermal sign above/below Tref is explicit.
3. UV U/M against independent continuous power-law integrals for current GL4
   nodes; source/config identity and low-occupation condition.
4. Direct source formula versus derived A/B contraction and frozen analytic map;
   semigroup and zero-rate limits. No full coupled exactness claim.
5. Local gas+bath+escape source sum and independent state-energy derivative.
6. Three nontrivial eligible states: F(Pv)=P R F(Pv), including current-T Mao
   factor mapping. An ineligible isotope/odd-mode fixture must be rejected.
7. New scalar Compton Jacobian against independently differentiated or finite
   difference expressions if an analytic path is supplied.
8. Per-case admission, retained GL8/GL16 states/integrands and integral agreement;
   finite comparison of T, fractions, tau, matter/radiation signed observables.
9. Compare hot/reference differences with refinement changes of both branches;
   differences below the observed refinement scale remain numerically unresolved.

## 8. Minimal implementation boundary and unresolved inputs

Suggested fresh unit modules: a source adapter for Mao factors and GL4 UV moments;
a Compton scalar kernel; a THERM01-derived ThermalSystem owner; a new finite
runner/plotter. Keep the immutable THERM01 vendor unchanged, importing code only,
never its run/main dispatch. Prepare U/M once and reuse current state fields once
per RHS; no expensive spectral calculation is needed inside the BDF loop.

New raw stores should include current full63 lifts, current T/ne/H/U_gamma,
U_ref/T_ref, U_UV/M_UV, selected source powers plus both alternative diagnostics,
all transfer-ledger columns, absolute-throughput columns, dense GL8/GL16 sampling,
and accepted solver nodes if the chosen solve_ivp invocation makes them available.
Do not claim internal-step nodes when only requested t_eval values were saved.

Mao source-fit accuracy, in-band Li resonances, 60–200 eV correlated ionic yield,
missing collision/secondary channels, the actual CMB spectrum and radiative
energy/Einstein backreaction remain their declared input/physical obligations.
No strong no-go result is claimed. Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL;
CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED;
REI_activation=false remain unchanged.
