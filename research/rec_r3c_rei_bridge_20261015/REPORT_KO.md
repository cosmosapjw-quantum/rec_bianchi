# REC R3c-to-REI: original HyRec FULL q=0 source-matched initial-condition sensitivity

2026-10-15 KST. Starting parent REC PR93, commit 2c4627bf480a306f34bb35d0ec5a3d18182b170e. This explicitly chosen, finite R3c REI-facing subtask reproduces actual ORIGINAL HyRec2012 native H+He FULL cosmological recombination output and tests an opt-in REI initial donor. No independent Python FULL recombination trajectory or REI production run is claimed.

## Authority and physical scope

Original HyRec Oct2012 unchanged ZIP SHA256: 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27. REI scenario user-locked SHA256: 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696. Source original H+He evolves z8000->0, 8001 original stdout rows. The REI scenario physically covers zbar=20->4 and starts with declared approximate HII=0.0002, HeII=HeIII=0, gas temperature 8.098143045064857 K, and exactly zero ionizing photon stock by explicit chosen astrophysical source onset.

Original REI cosmology: h=.674, Omega_m=.315, Omega_r=.000092, Omega_Lambda=1-.315-.000092, obh²=.0224, YHe=.2454, T_CMB0=2.7255 K. To match the REI H(z) in the original HyRec massless-neutrino radiation representation, derive:

\[
\omega_{\gamma} h^2=4.48162687719\times 10^{-7} (T_0/\mathrm K)^4,\quad
N_{\rm eff}^{\rm equivalent}=\frac{\omega_r h^2/(\omega_{\gamma}h^2)-1}{0.227107317660239}
=3.03821934419124.
\]

This is an *effective background matching parameter*, NOT a measured neutrino number or a full massive-neutrino model. Source normalized hydrogen number today differs: original HyRec nH0=11.223846333047 obh²(1-Y) m^-3; REI uses (1-Y)Omega_b rho_crit/m_p. At z20 donor source nH=1756.970280931192 m^-3, REI nH=1757.9215875815148 m^-3: -0.0005411542 relative difference. Original HyRec fHe=Y/[3.97153(1-Y)] = .08188416223421702 while REI fHe=Y/[4(1-Y)]=.08130135170951498. These are retained as a declared normalization mismatch, not silently assumed equivalent. REI observables below use REI nH and fHe, whereas HyRec evolution used source values.

## Actual matched reference and observables

Original full native GCC history output z20:

- free electron fraction x_e=n_e/nH = 0.000210349192936
- Tm = 9.306042400380866 K

Original REI conditional initial is x_e=.0002, T=8.098143045064857 K. Donor-vs-baseline relative initial changes: x_e +5.174596468%, T +14.915757212%. This is not reionization scientific-result error, but difference between explicitly different initial physical models.

On the fixed recipient REI baryon density: n_e changes 0.351584317516303 -> 0.3697773871925435 m^-3. Instantaneous Thomson rate c sigma_T n_e changes 7.011846289215682e-21 -> 7.374681039639024e-21 s^-1, +5.174596468%. d tau/dln(a)=c sigma_T n_e/H changes 5.924618394385755e-5 -> 6.231193488564117e-5 (dimensionless per log scale-factor, NOT total integrated optical depth). Idealized gas internal energy u=(3/2)n_H k_B T (1+fHe+x_e) changes 3.1885009560495904e-19 -> 3.6641250800852963e-19 J/m³, +14.916856874%.

Original HyRec history.c evolves helium then assumes helium neutral in its late H-only branch once source xHeII falls below 1e-6. Native stdout only reports total x_e and Tm; candidate xHII=x_e, HeII=HeIII=0 is an *explicit conditional late-time neutral-He projection*, not an independently measured electron census by species.

## Source-run performance and science variation

The unchanged original HyRec source was compiled in an isolated temporary source directory (gcc -std=gnu99 -O3 -fno-fast-math) and executed at matched background. Original reference stdout SHA256: 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400. Raw output gzip is deterministic (mtime=0) and preservable.

Actual original-source YHe sensitivity cases at otherwise fixed matched cosmology:

| YHe | native x_e(z20) | Tm(z20), K |
|---:|---:|---:|
| .2434 | .000209769508896 | 9.29995268899975 |
| .2454 | .000210349192936 | 9.306042400380866 |
| .2474 | .000210931960942 | 9.312146756008397 |

These are conditional perturbations of source inputs, NOT a posterior interval. Three complete source histories were executed serially then in a two-worker configuration with identical source inputs. Each corresponding output SHA256 was byte-identical. Total serial source-run sum 1.3762363909 s, concurrent two-worker wall 0.9532233831 s: observed 1.44377x parallel speedup for these three independent source jobs. No REI Rust solver speedup implied.

For physical recipient postprocessing on 1581 real original-C history rows, full scalar electron-density, local Thomson-depth and internal-energy calculation 2.50654 ms versus NumPy vector 0.0838970 ms, **29.876x speedup**. All three vectorized fields agree with scalar reference to maximum normalized discrepancy 3.92204e-16. These timings exclude native C integration and any REI abundance trajectory.

## Signed-q extrapolation diagnostic, NOT primordial Bianchi physics

REI adopted Bianchi LRS stress-free family is valid only between zbar20 and zbar4: ds²=-c²dt²+a²e^-2b(dx²+dy²)+a²e^4b dz², s=db/dt, H²=H_FLRW²+s², s(a)=s_ref(a_ref/a)^3 and q_ref=s_ref/H_FLRW(z20) ∈{0,±.005,±.01}. Extending this prescription mathematically to z600/1100 is outside adopted model scope.

Formal extrapolation q_ref=-.01: at z600 s/H=-.8169532458 and H_parallel/H=-.6339064917; at z1100 s/H=-.9573333862, H_parallel/H=-.9146667725. Formal qref=+.01 has s/H=+.8169532458 at z600, +.9573333862 at z1100; H_perp/H=.1830467542, .0426666138. At z600 shear²/Hflrw²=2.00672851, at z1100 10.97421411. Wolfram exact Reduce confirmed H_parallel = sqrt(Hflrw²+s²)+2s < 0 if and only if s < -Hflrw/sqrt(3), Hflrw>0. These numbers expose a blind extrapolation failure, **not** a universal no-go for Bianchi recombination.

Therefore the q0 donor may be used only as a deliberate *common initial-value counterfactual* for REI signed family. It does NOT certify primordial anisotropic recombination. The REI initial zero ionizing photons represents astrophysical source onset, not a license to relabel CMB/atomic recombination spectral photons as ionizing UV.

## Code and exact reproducibility

- src/full_bianchi_hyrec/trajectory/rei_initial_boundary.py: strict source input/schema/provenance; massless-equivalent Omega_r conversion, RI nH/fHe units; donor initial electron, Thomson and gas energy, formal shear guard. Immutable authority REI source must be supplied explicitly.
- scripts/run_rei_primordial_source_intake.py: original C source compilation, 3 true original FULL histories, serial/parallel SHA control, vector postprocess benchmark, plots and machine evidence.
- scripts/export_rei_conditional_donor.py: typed REI_DONOR_CANDIDATE_OPTIN_ONLY.json, disabled by default, source-scenario drift rejection and explicit separate sensitivity-run requirements. No rewriting original REI config.
- tests/trajectory/test_rei_initial_boundary.py: scientific dimensions, matching Omega_r and baryon source conventions, raw gzip SHA, q sign/epoch counterexample, drift negative test, source compilation/reproduction slow test.
- research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz: real raw C 8001-row output; HYREC_FLRW_Z20_TO_1600.csv is a 1581-row reference slice; diagrams are source reference plots, not REI native runs. JSON file names encode scope and source identities.

Result claims:
- VERIFIED: actual full original C FLRW H+He primordial recombination at near-matched REI expansion/background, source/run hashes, REI conditional initial delta, source-input sensitivity.
- DERIVED + COMPUTED: Thomson rate and gas u at z20 under recipient normalization; formally extrapolated signed-q kinematics outside adopted domain, and strict source-to-recipient conversion.
- NOT_RUN: independent REC Python FULL self-consistent photon-history x_e(z),T_m(z) integration and any REI native altered-IC abundance trajectory.
- NOT_ADOPTED: original REI scenario IC, astrophysical source, signed REI AX08 physics, original checkouts and checkpoints.

Relevant primary papers: Ali-Haïmoud & Hirata (2011) Phys Rev D 83 043513 doi:10.1103/PhysRevD.83.043513, Scott & Moss (2009) matter temperature doi:10.1111/j.1365-2966.2009.14939.x, Furlanetto et al (2006) cosmic dawn review astro-ph/0608032. Papers provide context; pinned original C and source scenario supply quantitative numerical authority.

Next constructive scientific result: run a **separate REI native z20→4 sensitivity study** under this donor (same MD14/BB50K source/geometry but fresh donor gas, no resumed baseline checkpoints) and compare abundance histories, clocks, tau and radiative feedback against already verified baseline with independent convergence. Separately continue REC source-owned Python R3c accepted-memory FULL history: still unresolved, no PASS.
