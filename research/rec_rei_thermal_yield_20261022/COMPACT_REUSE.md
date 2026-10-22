# PR220 compact-kernel reuse assessment

Read-only R3/C1–C4 review, 2026-10-22. No old IVP, test suite, benchmark, or pipeline was executed. This note distinguishes source inspection and mathematical derivation from new numerical verification.

## Decision

**Reuse the constant reflection-even/isotope-equality maps and prepared geometry. Add one common thermal coordinate.** A local isotropic temperature equation and isotope-independent shell/final-charge transition kernel preserve the same invariant subspace. The resulting minimal state is **34 = 23 geometry + 9 element fractions + 1 optical depth + 1 thermal scalar**. Old 33-coordinate and 62-coordinate saved results remain unchanged.

The current `CompactSystem` cannot be used unchanged as the physical owner: its donor prescribes temperature, its photo generator only implements adjacent charge steps, and its diagnostics recompute the prescribed temperature. Preserve donor bytes and compose/subclass into a new scientific owner with a new schema and campaign identity.

## Inspected identities

REI PR220 head `8be7533cc97b3302bf42608699d6e8313ed6af8a`, science commit reported `a6eda7e392a493bc92ecf532b0c835cbf7f6814e`. Root directory `research/rei_hheli_compact_pilot_20261022/`.

| Object | Git blob or tree |
|---|---|
| `code/compact_system.py` | `4769767f1fb6a13856c86e0c36484a95282be570` |
| `code/compact_run.py` | `d2a9ff21be63fcf47dee9d0110a3a83d6373fd27` |
| `vendor/rec_hheli` tree | `33b218da2710e274aa79aa4239d1b949529c21c9` |
| donor `code/atomic_network.py` | `e3a0603176304f64b953c0b2faf898d6b75eceb5` |
| donor `code/coupled.py` | `7d1a346081528f7f9449fdcb1032cf84a9aabb44` |
| donor `code/geometry.py` | `a6ba35fff4f62ef795628499f108705ab6b55ac1` |
| donor `data/atomic_coefficients.json` | `2eba600a9d7a7359ca55f566f1b841a363a3e5c7` |
| donor `data/atomic_model.json` | `73285c1585f8edca92487effe95e68448f3163b8` |

These identifiers came from the actual pinned GitHub tree/contents responses. This review did not run an additional local all-byte identity test. `provenance/DONOR_IDENTITY.json` names 57 immutable donor files at REC commit `a949529872eb5ba0e20c7e206fe893e5d544e48c`; the newer REC119 closeout head `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7` is a distinct provenance role.

Primary source code URLs:

- https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8be7533cc97b3302bf42608699d6e8313ed6af8a/research/rei_hheli_compact_pilot_20261022/code/compact_system.py
- https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8be7533cc97b3302bf42608699d6e8313ed6af8a/research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/code/coupled.py
- https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8be7533cc97b3302bf42608699d6e8313ed6af8a/research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/code/atomic_network.py
- https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8be7533cc97b3302bf42608699d6e8313ed6af8a/research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/code/geometry.py
- https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8be7533cc97b3302bf42608699d6e8313ed6af8a/research/rei_hheli_compact_pilot_20261022/THEORY_KO.md

## Exact coordinate map

Full62 order is full40 geometry, 21 isotope-scaled ionic populations, tau. Full40 has indices0 elapsed-time,1 b,2 scaled shear,3 zero gas-energy placeholder; four nine-entry angular towers begin at4,13,22,31. Their order is photon energy, photon number, neutrino energy, neutrino number, each ell0..8.

The compact geometry retains `[0,1,2]` and ell`[0,2,4,6,8]` in each of those four towers. Thus23 geometry entries; all odd multipoles and placeholder index3 lift to zero.

Atomic representatives are full atomic indices `[1,2,10,11,12,17,18,19,20]`: H1 I–II, He4 I–III, Li7 I–IV. The lift copies scaled fractions into D, He3 and Li6. Nuclear neutron/tritium entries0,5,6 stay identically zero. Actual Y_Aq is isotope inventory I_A times the shared fraction f_Zq; no tiny Li population is compared against a hydrogen-sized absolute tolerance.

Let R select those33 entries and P lift. The implemented constant matrices satisfy RP=I by construction. For the original invariant system F, `f_c=R F(Pv)` and `J_c=R J_full P`. This is a coordinate-restricted evaluation of the original full owner, not an independently simplified physical RHS. It still evaluates many full62 operations, so coordinate reduction alone supplies no measured speedup.

For a common thermal scalar theta, use `P_ext=diag(P,1)`, `R_ext=diag(R,1)` on a conceptual63-dimensional full state. Or keep old lift strictly for the first33 and expose temperature separately. Do not relabel a34 array as compact33 or a63 array as full62.

## Why the reduction survives the selected extension

**Derived.** For elementZ with isotope inventories I_A, assume all its isotopes see one common electronic generator M_Z(T,J,n_e). This generator may include nonadjacent charge transitions. Inserting `Y_A=I_A f_Z` into `dY_A/dt=M_Z Y_A` gives `df_Z/dt=M_Z f_Z`. The common electron density

`n_e=n_b sum_Z (sum_A I_A) q_Z^T f_Z`

depends on all species but is the same for each isotope, so its nonlinearity does not break equality. A commonT equation depending on sums over isotope-weighted populations also preserves this embedding. The exact projected Jacobian must include the derivatives of n_e andT.

Parity survives if the new UV/thermal interaction is local and isotropic and no tilt or odd multipole is injected. The geometry then remains reflection-even. Baryon isotropic pressure retains pi_b=0. The existing massive anisotropic matter is a separate nonbaryonic collisionless component.

Required conditions remain zero initial n/T and no nuclear transmutation; isotope-independent rates/yields/temperature and equal initial electronic fractions; non-tilted LRS geometry; no odd angular forcing. A branching kernel may change charge by2 without invalidating the reduction, provided it is identical for Li6/Li7 and conserves nuclei.

## Smallest implementation surface

1. Keep `vendor/rec_hheli` unchanged and import its `AtomicNetwork` and `Geometry`. Reuse photo cross-section preparation, RR/DR coefficients, isotope inventory, source constants and prepared momentum geometry.
2. Build the chosen shell/final-charge photo generator and energy moments in a new module. Donor `_transition_matrix(..., upward=True)` always selects i+1, so it is not a generic ionic-yield API. For a new channel i→j, add nonnegative event rate to M[j,i] and subtract the same from M[i,i]; event multiplicity enters electron and ionization-energy changes through q_j−q_i and chi_j−chi_i.
3. Add oneT/U coordinate and a new `point()` that evaluates atomic rates at actualT. The donor `thermal_uv(x)` can still supply the chosen external UV envelope only.
4. Reuse geometry from the same common electron density and compute tau in the same properSI units. Retaining the original test-fluid Friedmann closure gives a meaningful bounded thermal extension; it does not add gas thermal energy to H or establish total Einstein/matter/radiation energy closure.
5. Rebuild diagnostics from the new state. `CoupledSystem.diagnostics` currently calls its prescribed-T `point`, uses prescribed dT/dx, and reports `bath_minus_escape` as a residual. Calling it unchanged would silently report wrong temperature, rate diagnostics and energy closure.
6. Use a fresh case directory/schema/receipt and only the new finite IVPs. Retain the existing non-clipping/non-renormalizing policy. The latest compact serializer converts NumPy scalar metadata safely and can be reused without importing the old campaign dispatcher.

## Required thermal bookkeeping

For nuclei per baryon N=sumY and free electrons e=q^TY, let g=N+e, n_g=n_b g, `u_th=(3/2)n_b g k_B T`. In this no-transmutation lane N is constant and `gdot=q^T Ydot`. The common gas temperature obeys

`Tdot = -2 H T - T gdot/g + 2 Q_th/(3 k_B n_b g)`.

The `-T gdot/g` term is required when photoionization/recombination changes particle number. If one evolves u_th, reconstruct this equivalence using `n_bdot=-3Hn_b`. Ionization potential energy is separate: `u_ion=n_b chi^TY`; its source is `n_b chi^T Ydot`. Use the same transition-energy convention in both ledger and populations. Each absorbed photon must be allocated once among change in ionic potential energy, thermal electron kinetic energy, excitation/metastable storage, and escaping radiation. Source-bound cooling must not subtract recombination binding energy a second time from the thermal reservoir.

**Derived possible rate-moment route:** For Maxwellian recombination alpha(T), if the adopted fit is interpreted as the thermal average of a fixed cross-section, its kinetic energy moment is `alpha<E> = k_B T^2 alpha'(T)+(3/2)k_BT alpha(T)`. For a DR fit `T^(-3/2)sum_i c_i exp(-E_i/T)`, this becomes `k_B T^(-3/2)sum_i c_i E_i exp(-E_i/T)`. Signed fit coefficients mean that component terms are not probabilities; check the total energy moment and total rate in the finite admitted temperature range. This is a rate-derived closure, with derivative sensitivity inherited from the fit, rather than independent cooling data.

## Finite temperature and source boundaries

The donor's runtime rate domain is100..1e6K. Its LiIII recombination row gives a lower source validity limit90K. Free adiabatic cooling from T0=100K atz20 leaves the current admitted domain immediately before the UV ramp. A dynamicT pilot must therefore explicitly select a supported startingT/interval, use different source-supported lowT rates, or model a justified physical heat term. A numerical floor or unrecorded thermostat would change the physics.

Illustration of a legitimate finite initial-condition choice: T0=1000K atz20 gives a no-source adiabatic value about184K atz8; T0=5000K gives about918K there. These algebraic estimates do not bound additional cooling, and the actual new run must retain a temperature-domain gate. They are distinct initial conditions from the REC126/REI129 prescribed-T cohorts.

The source researcher confirmed that LiI single1s ionization is not universally a double-charge Auger channel. Donor energies64.39eV and cumulative5.392+75.64=81.032eV already expose that an always-double step below81.032eV would violate energy conservation. Explicit correlated/shakeoff channels need their own source. A finite5–60eV new source avoids Li1s edge and many higher-energy channel obligations, but must be labeled as a new spectral contract, not a closure certificate for the old200eV pilot.

## Jacobian and numerical risks

- Old analytic62 Jacobian assumes prescribedT independent of state. New chemistry needs the T column `d(M(T,n_e)Y)/dT`; thermal row needs composition, geometryH andT derivatives. Old projection alone is incomplete.
- For RR beff=B+C exp(-T2/T), `beff'=C exp(-T2/T)T2/T^2`. Derivatives of the exponents multiply logarithms. Dropping this contribution changes the Badnell temperature response.
- The charge-gradient rank-one term `n_b outer(Gne Y,q)` remains necessary for electron-coupled recombination. Nonadjacent charge jumps require matching electron-source multiplicity.
- If using logT, dT/dlogT=T and the full thermal/chemical Jacobian must include that chain rule. A source-domain guard is still required; positivity ofT alone does not authorize extrapolation.
- Existing geometry rejects negative trial n_e. Chemistry tolerates signed Newton trials without clipping; retain their distinction and interpret any actual domain error as a numerical/initial-domain issue.
- Existing compact eligibility examines equality of old prepared arrays and rate blocks at100,6050,12000K. The theorem depends on the new full generator structure, not merely those three old temperatures. A structural element-level API plus finite projection checks is the small relevant replacement.
- Global module names and `sys.path` insertion can collide if two donor versions load in one process. Keep a single pinned donor import namespace/process, or load the new package with an explicit path.

## Minimal new verification

The changed dependency is the thermal/yield owner, so only it requires new tests. Useful finite checks are: positive-generator columns and nuclei/charge identities for all active new channels; per-event and bulk energy partition residuals; currentT derivative directional checks; invariant-lift residual at several permittedT/population states; and one or a few new thermally evolved trajectories with explicitT-domain and energy-ledger acceptance. A new full63 oracle may be useful only if a concrete projection risk remains; it is not necessary to rerun old full62 or REC126/REI129 cohorts.

Keep source-bound local closure validation separate from global convergence, performance/scaling, and production approval.

## Preservation and claim locks

REC125 main+1control=126 and REI127main+2oracle=129 are separate cohorts. The first REI failed raw trajectory set was local-only; successful trajectories/oracles and failed JSON/log preservation must not be represented as recovery of that absent raw set.

Existing Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL and CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false remain unchanged.

The local repository AGENTS.md was read. This task performed source/physics review only. Implementation under the frozen root contract belongs to the lower-tier executor, then a fresh read-only Astra decision. No extra governance or security machinery is proposed.
