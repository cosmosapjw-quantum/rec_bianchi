# REC omitted thermal processes on the saved eight trajectories

Unit: `REC_THERMAL_OMITTED_BUDGET_20261022`.
Workflow 1.0.0; approval design 0.2. The user explicitly authorized publication,
backup, and the next research loop on 2026-10-22 (UTC).

## Objective and immutable inputs

Evaluate identifiable Compton and H/He collisional source terms on the eight
completed full63 trajectories of `rec_thermal_moments_20261022`. Reuse the
original 109 stored states per trajectory, its exact physical abundances,
temperature, Hubble rate, baryon density, and radiation energy monopole.
The old source identity is
`dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e`.
The old local release is `cdf7e04518bde936206054c33413ab2b1fc300c5`, tree
`503fa14793f385a1e235763818251c5d34987842`. App publication may assign a
different commit header; exact tree equality and the local/remote mapping
must be recorded separately.

There are zero new background, chemical, thermal, or auxiliary ODE
integrations in this unit. The previous 126 and eight completed IVPs are
immutable. Existing full63 solution accuracy evidence is reused by identity;
the missing old dense diagnostic arrays are not reconstructed or claimed.

## Physics contract

Metric signature (-,+,+,+), proper SI densities and powers, x=ln(a/a_ref),
native21 isotope/ion coordinates, exact-zero neutron/tritium inventories,
common Maxwellian gas temperature, isotropic non-tilted electrons, and
test-fluid baryon energy remain as inherited.

1. Compute the leading hot-electron inverse-Compton term from the actual
   saved photon energy density. It is a separately identifiable energy
   transfer component. The full CMB recoil/stimulated term requires a
   spectral closure not supplied by the saved number and energy moments.
2. Compute an explicitly separate isotropic Planck-reference curve with
   T_gamma=T0/a and its own Planck energy density. Do not substitute it for
   the actual Bianchi photon monopole or present it as a reconstruction.
3. Compute first-order Thomson/nonrelativistic Compton exchange with the
   inherited isotropic 5–200 eV external UV bins. Verify the adopted smooth
   spectrum has small occupation and record photon/electron energy ratios.
4. Adopt Hui & Gnedin Appendix A H I, He I, He II collisional ionization
   fits and H I/He II excitation cooling fits, with explicit isotope
   electronic equality. Preserve each fit's published accuracy interval.
   Analytic continuation outside that interval is a separately labeled
   diagnostic, never a validated coefficient or a zero physical process.
5. CI moves each supplied nucleus q→q+1 and adds one electron. Its kinetic
   loss is exactly the increase in the inherited binding-energy store;
   total gas energy has no CI radiative sink. Include the new-particle term
   in the direct temperature forcing. CE uses prompt escape and unchanged
   ionic charge. He I CE/metastable closure and Li CI/CE remain unsupported
   in this finite provider; other omitted processes retain their obligations.

## Calculations and output

Save every evaluated coefficient, support mask, source term, CI abundance
source, radiation moment, and direct fixed-path dlnT/dx forcing. Report
integrals in eV/baryon and dimensionless fixed-path log-temperature forcing.
The primary integral is the positive-weight composite trapezoid on the
109 existing nodes. Also report 55-node coarsening and 109-node Simpson
diagnostics. These compare retained-grid quadrature; they are not continuous
error bounds or new trajectories. Supported-interval sums include only
intervals whose two endpoints satisfy the source's accuracy domain;
remaining intervals are reported as continuation/boundary contributions.

Compare all four primary cases; use the existing refined and alternative
RR trajectories to assess inherited-trajectory sensitivity of this budget.
Do not interpret a forcing integral as a solved deltaT, uncertainty bar,
or a rigorous omission-error bound. Physical importance follows from
actual source/work/thermal-energy ratios, without an invented promotion gate.

## Acceptance and completion

- All eight trajectory/receipt/source identities must agree before use.
- Coefficient checks use independently evaluated expressions or published
  source values; SI↔CGS, threshold mapping, and domain behavior are checked.
- CI isotope conservation, electron source, and kinetic-plus-binding
  cancellation must hold to scaled 1e-13 in targeted physical cases.
- Compton limits include vanishing electron/photon density, negative hot
  term, Planck thermal equilibrium, ultraviolet recoil sign, and a
  moment nonclosure example. Wrong c, energy-unit, density, or particle-term
  choices are checked where they would change interpretation.
- Actual plot-source arrays and figures, direct visual inspection, physics
  review and independent numerical/code review must support the report.
- Publish stages and final results to the authorized research branch/PR;
  create-only Dropbox backups must have actual acknowledgments. Preserve
  old publication failures, immutable snapshots, and identity mappings.

Completion means a reproducible fixed-path source budget and an actionable
choice of the next coupling work. Physical HOLD, production NOT_APPROVED,
global convergence NOT_RUN, U5 CLOSED_HOLD_NOT_RESET, REI_activation=false
remain inherited.
