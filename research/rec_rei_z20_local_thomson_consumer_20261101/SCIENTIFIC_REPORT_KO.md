# REC → REI: native-source-locked z=20 directional Thomson clock witness
Date: 2026-11-01. Scope: REC-owned **local, one-sided z20 interface only**. Not a high-redshift Bianchi recombination solution and NOT an REI CMB LoS receiver.

## Original data and authority
The parent REC Draft PR187 is frozen at HEAD ba283bf2262396b9a5ac14867caffd78f8469b99; immutable parent PR186 8af60c826f142f0a2e8de1b028bd72e7b5053d1b. Original HyRec2012 H+He native C output has 8001 rows, stdout SHA256 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400. Original 1581-row source blob 2b50008c744d9cb241d9985a4bf6ce8bcf83e09a, original boundary blob 89cdfc766e2e613760d84274812f2b4432373354. Original C third column is T_m/T_gamma, NOT kelvin. This unit reuses the original source-locked code, with all 8001 native C output rows rechecked.

Extra REC original source SHEAR_BACK_EXTRAPOLATION.json Git blob 7a5b76f618ae47b500f56a8084c2a15829ba184e. It explicitly admits zbar=4 to 20 ONLY; extrapolation to primordial high z is COUNTERFACTUAL_NOT_PHYSICALLY_ADMITTED. At z20 it supplies q_ref=-0.01,-0.005,0,+0.005,+0.01, with original recipient scenario SHA256 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696.

## Constructive geometry and clock derivation
Metric signature (-,+,+,+), c retained: ds²=-c²dt²+sum_i a_i²(t)(dx^i)², a_i=abar exp(beta_i), sum_i beta_i=0. Translation symmetry conserves p_i. With orthonormal photon direction n_i(t20), E(t)/E(t20)=[(1+zbar(t))/21] sqrt(sum_i n_i²(t20) exp(2[beta_i(t20)-beta_i(t)])). Hence -d ln E/dt = H_ray = sum_i n_i²(t) H_i(t).

For homogeneous comoving electrons, Gamma_T = c sigma_T ne(t). At monotone ray clock H_ray>0, d tau/d ln(1+z_ray) = Gamma_T/H_ray. Yet tau(t,t20) = integral_t^t20 Gamma_T(t') dt' is direction-INDEPENDENT at fixed cosmic time endpoints for homogeneous ne. Hbar/H_ray modifies the directional-redshift derivative, NOT physical segment optical depth at fixed t. No anisotropic tau may be manufactured by multiplying the q0 HyRec tau by this ratio.

At z20 only, source defines s=q_ref H_FLRW; Hbar=H_FLRW sqrt(1+q_ref²), Hperp=Hbar-s, Hparallel=Hbar+2s and Hray=(1-mu²)Hperp+mu² Hparallel. The source geometric identities are independently checked. A high-z beta_i history is neither supplied nor invented.

Mean clock positive lookback derivative d tau/d ln(1+zbar)=+Gamma_T/Hbar. With FORWARD ln(abar), d tau(20,z)/d ln(abar)=-Gamma_T/Hbar. The source's dtaudlna stores a positive MAGNITUDE; this is not a signed forward derivative. Both signed and positive fields are output explicitly.

## Source-conditioned local science
At z20 original REC HyRec donor normalized once to REI recipient hydrogen: ne=0.3697773871925435 m^-3, Tgas=9.306042400380866 K, xe/H=0.000210349192936. Original REI approximate IC ne=0.351584317516303 m^-3, Tgas=8.098143045064857 K, xHII=0.0002. Donor differential scattering opacity is +5.174596468% relative to published REI IC at common clock; this is not adopted.

Generate 5 actually sourced z20 shear cases x 3 directions (mu=0,0.5,1) x 2 original electron densities: 30 source-conditioned LOCAL differential-opacity rows, not 30 evolved physical states. For q=0, donor Gamma/H_FLRW must match native C-based dtaudlna. No REI IVP or original C re-execution is run in this unit.

## Native receiver search and no-overlap rule
The latest surveyed REI PR347 (HEAD 6a0f0a9e70d3f4f1dac5be00ddd1c6153f5ade85) has HI/HHe photoionization transmission and OTS kernels but no identifiable native Thomson/CMB line-of-sight receiver in tracked REI Python source. This is a source-inventory observation, NOT a no-go theorem for all archived external projects. Receiver injection is NOT_RUN.

For *future* accepted same-clock histories on strictly disjoint segments, tau_total(0,z)=tau_REI(0,20)+tau_REC(20,z). Then z>=20 visibility as seen from z0 is exp(-tau_REI(0,20)) times the REC z20-frame g_REC(z), assuming valid matched electron/clock/geometry. No accepted lower-z REI LoS opacity is supplied, so DO NOT compute or claim a full observer-z0 CMB visibility. The original donor electron-state mismatch forbids automatic owner swap.

## Hostile audit and drift watchdog
A) Original q=-0.005 high-z formal extrapolation gives Hparallel/H=-0.1559932666 at z600, nonmonotone directional redshift and explicitly outside the source domain. Reject its high-z optical interpretation without changing any tolerance.
B) Treating positive dtaudlna as signed forward derivative reverses attenuation.
C) Applying a second density-rescaling to the already REI-normalized source ne is wrong.
D) REI ionizing-photon optical-depth kernels are not automatically Thomson LoS collision/visibility receivers.
E) The 30 local operator rows cannot count as new REI DAG nodes or solve original F05 first interval.

Claim: DERIVED plus SOURCE_CONDITIONED_LOCAL_NUMERICALLY_CHECKED, depending on fresh tests/CI. Not accepted high-z Bianchi history. No new native producer evolution. STOP new local proxy atlases after this boundary question: next productive owner step is an actual source-locked LOS/Boltzmann receiver and non-overlap history, not a 31st local sample.

DAG fixed: REI canonical 28/88 (+0); REI working 33/88 (+0); REI Physical Fast 4/7 (+0); REC H5 0/313 (+0). Production HOLD, no merge/force push/owner swap/tolerance change, F05 [160,161] still blocked, AUTO_NEXT_NODE=false.

Primary literature: Ali-Haïmoud and Hirata, Phys. Rev. D 83, 043513 (2011), DOI 10.1103/PhysRevD.83.043513; Fleury, Pitrou and Uzan, Phys. Rev. D 91, 043511 (2015), DOI 10.1103/PhysRevD.91.043511.
