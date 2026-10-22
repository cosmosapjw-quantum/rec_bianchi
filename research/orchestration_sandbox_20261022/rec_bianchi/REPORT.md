# REC1 result: Compton exchange on eight saved thermal histories

The omitted reference-blackbody Compton term removes **2.570630–2.575791eV per baryon** along the eight stored REC thermal-moments paths from z7.9637328 to2. The associated integrated relaxation depth is1.022329–1.023559. Its largest instantaneous magnitude is46.6885% of retained primary photoheating and132.1815% of thermal adiabatic cooling. This finite budget supports including scalar Compton exchange in a new, separately identified closure calculation. It does not calculate the resulting temperature history.

Let eta be the stored total number of gas particles per baryon, including free electrons. In SI, for a nonrelativistic Maxwellian gas and the explicitly prescribed reference blackbody Tgamma=2.7255(1+z)K,

\[
Q_C=\frac{4\sigma_T a_R k_B}{m_ec}\,n_eT_\gamma^4(T_\gamma-T),\qquad
\Gamma_C=\frac{8\sigma_T a_RT_\gamma^4}{3m_ec}\frac{n_e}{n_b\eta}.
\]

The thermal energy per baryon is epsilon_th=(3/2)kB eta T. Adding Qc to its energy equation gives dT/dt|C=GammaC(Tgamma−T) at fixed composition. Chemistry retains its separate particle-number derivative. This avoids assigning the electron temperature equation to all particles without their heat capacity. The corresponding radiation energy source has the opposite sign in a closed coupled model; here the reference field is prescribed. The formula follows Ali-Haimoud & Hirata2011 Eq12, generalized from its H/He particle-count denominator to the stored21-species inventory: https://arxiv.org/abs/1011.3758 .

At frozen coefficients, Tnew=Tgamma+(T−Tgamma)exp(−GammaC dt), a positive convex combination. The implementation uses expm1 for the increment, so it is inexpensive and stable when GammaC dt is small. This exact local substep can enter a future splitting or implicit method; splitting error still requires that method's own finite validation. The current code only evaluates stored states and quadratures.

| Saved cohort case | Compton budget [eV/baryon] | Damping depth |
|---|---:|---:|
| s00_m02_r02 Mao nominal |−2.575791019|1.023558979|
| s02_m04_r01 Mao nominal |−2.575778771|1.023555811|
| s03_m03_r03 Mao nominal |−2.575513973|1.023487318|
| s03_m03_r03 Mao refined |−2.575514221|1.023487318|
| s03_m03_r03 rate derivative |−2.575106203|1.023487284|
| s04_m04_r04 Mao nominal |−2.571036971|1.022328953|
| s04_m04_r04 Mao refined |−2.571037218|1.022328953|
| s04_m04_r04 rate derivative |−2.570630086|1.022328919|

These eight histories belong to branch892aad5, each with109saved nodes, and are separate from PR120's8THERM01 histories with193nodes. Their input NPZ SHA256 values exactly match original receipts and SOURCE_INPUTS.json. Parent126,THERM01,REI129,warm729 and REI C22B were not rerun.

The budget is integral Qc/(nb H) dx, x=ln(a), and damping is integral GammaC/H dx. The difference between55-node and109-node Simpson quadrature is0.000337331–0.000340097eV/baryon. The109-node trapezoid differs from Simpson by up to0.001351865eV/baryon. These are saved-grid quadrature sensitivities. For the two existing nominal/refined pairs the budget changes about2.47e-7eV/baryon; this compares stored parent histories and is not a bound on a new Compton-coupled solution. No missing dense interpolants were reconstructed or old IVPs repeated.

C11 implementation compiled with cc -O2 -Wall -Wextra -Werror, without fast-math. One actual combined production/verification run exited0: internal wall0.278178s, processCPU0.099224s; tool elapsed2.550407s includes interpreter/import overhead. C versus separately arranged Python coefficient relative difference6.66e-16, particle heat-capacity mapping4.44e-16, exact frozen-step semigroup1.23e-16. Equilibrium, zero-electron, heating/cooling signs and invalid-input cases passed. Input routing was then made repo-portable with a pinned source manifest; only py_compile was repeated, and physical kernels/results were unchanged.

Reproduce in the published repository with `python research/orchestration_sandbox_20261022/rec_bianchi/code/run_budget.py`. The script finds the eight already published parent trajectories under research/rec_thermal_moments_20261022; no separate user download is needed. Python3,NumPy,SciPy and a C11 compiler are required. `--inputs` supports the flat staging directory used here. Outputs include RESULT.json, budgets.csv and872-row history.csv. Original sources are not modified. The first run is already complete; use its records unless input or method identity changes.

The radiation field here is an explicit isotropic blackbody reference. It does not reconstruct the donor anisotropic photon spectrum or assess full frequency-dependent Compton transport. All 872stored states have T>Tgamma and therefore cool under this reference. The actual omission budget is large enough to motivate the next model extension, while its new coupled temperature and ionization response remain a separate calculation.

DAG: current-ref/intake→fixed saved8/source contract→derived heat-capacity mapping→C implementation→872-state budget+finite checks→parent publication/backup. The science node is COMPLETE_SCOPED; publication/backup receipts are parent-owned. Future nodes: source-bound collisional excitation/ionization budget in parallel with Li exclusive-channel data resolution; then new source-consistent coupled integration using the selected thermal coordinate and frozen local substep, followed by retained-energy and finite-resolution checks. Physical HOLD, productionNOT_APPROVED, globalconvergenceNOT_RUN, historicalU5budgetCLOSED_HOLD_NOT_RESET and REI_activation=false remain.
