# Original-HyRec no-UV Thomson-null science and native F08 source compatibility
Date: 2026-11-01. Project: cosmosapjw-quantum/rec_bianchi. Parent immutable Draft PR188 HEAD c177bbc8a6e03b502cf910067c7cc02a2d179d89. Single bounded physical science unit.

## Result and claim type
Derived plus numerically checked on immutable original **saved C output**: native HyRec2012 H+He 8001 actual source rows at integer redshifts 8000..0, with exact SHA256 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400. The new product is the original source's no-astrophysical-reionization residual Thomson *null reference*, NOT a real ionized-IGM prediction, not actual present-day CMB tau, not an Einstein-constrained Bianchi model, and not a second native HyRec C execution.

Immutable high-z REC parent original H+He z20..1600 source 1581 rows and prior optical output SHA256 879e51d67ab9a55be81a019a6bf08487ba425ab3bf97f30bc01cdda2825555a0. Preserve exact recipient nH normalization once, original electron fraction includes any native helium contribution, original C 3rd column is dimensionless Tm/[Tgamma0(1+z)]. At z0 original native C xe/H=0.000175613025657, Tm=0.02172948677627955 K (a physically unrealistic gas endpoint after astrophysical heating, admissible only as this declared noUV null experiment). At z20 original native xe/H=0.000210349192936 and Tm=9.306042400380866 K.

## Full physical-source numerical output
- 21 native C samples at z=0..20, original 1581 previous samples z=20..1600; shared source z20 counted ONCE. 1601 distinct source-redshift ordinates total; new evolved IVPs=0. The output is 1601 **derived visibility/opacity sample rows**, not 1601 independent physical states and not canonical REI DAG nodes.
- tau_noUV(0,20)=3.871290640411524e-05 (unitless), photon transmission exp(-tau)=0.9999612878429308 and scattering probability 3.871215706918729e-05. At z1100 noUV tau0=1.124706769375157; at z1600 noUV tau0=32.558188328737074.
- Frozen-xe(z20) low-z artificial control tau=4.0831351325995635e-05. Native source x_e(z) varies; do not substitute the frozen control for genuine source C.
- Lowz source-grid Simpson vs trapezoid: absolute delta 3.411088072556069e-08; coarse Simpson step2 tau=3.8694496660808596e-05. These are quadrature witnesses, NOT valid physical model errors or an upper-bound certification.
- z20 derivative K(20)=c*sigmaT*ne/[(1+20)*H_FLRW] agrees original high-z source within 4.440892098500626e-16 relative. High-z cumulative optical-depth additivity exactly 0 difference in stored float64 source expression, and g0(z) = exp[-tau_noUV(0,20)]*g20(z) max absolute difference 1.734723475976807e-18. Visibility normalization integral minus expected = -7.41651184910097e-12. Source visibility peak zbar=1078 unchanged; this is a conditional q0 source-grid property only.
- Source-derived gzip CSV: ORIGINAL_NATIVE_C_NO_UV_THOMSON_0_TO_1600.csv.gz, SHA256 5ecdc520592f7d42cc336747d8ce9593546acc7b5d487a3a1329cdc41ec4be60. Full machine-readable state SCIENCE_STATUS.json SHA256 5426e89081e71baef7406db6056b3e9920b60b2027e09215492b7720b00909e1. Deterministic serialization checked via two independent output directories.

## Actual F08 receiver discovery: definitive current-source mismatch
REI PR349 exact HEAD 58f7ffb685c3758f1fed1113ff8134a24478c3df produced 10752 original F08 S0 optical sky rays, conditional source model. BASS PR315 exact HEAD f92dd36a060e0ac8d1c592677beb9a12cb1a111f produced source-matched Sachs distance sky to that REI S0. Contrary to the prior PR188 receiver inventory, an actual F08 source-owned observer/LoS computation now DOES EXIST.

But the original immutable F08 S0 scenario SHA256 c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1, owner source-pair ID 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8, gives x_e per H=1.0245, n_e=102.45 m^-3, H=1.0e-14 s^-1, T=50000 K, initial ionizing photons/H=0.05, prescribed time t=0..1e13 s and bookkeeping redshift reference_z0=10 (NOT today's cosmic z=0). At REC HyRec z20 donor n_e=0.3697773871925435 m^-3, H=1.1835101980340534e-16 s^-1, T=9.306042400380866 K, x_e/H=2.10349192936e-4, original target ionizing stock zero. Exact source-state contrast factors, Wolfram-checked: F08/REC n_e=277.058585917949; H=84.49441345424104; T=5372.853233287833; xe=4870.472692099705. Source photon operators and time/redshift physical interpretations also differ. The owner is not source-equivalent. Do NOT directly splice the new noUV C history into F08 S0 observer rays or claim an accurate CMB sky. This is a failure of the proposed current source binding, not a no-go theorem.

## Physics derivation
For homogeneous FLRW reference:
ne(z) = nH_REI(z20)*((1+z)/21)^3*xe_C(z);
K(z) = c sigmaT ne(z)/((1+z) H_F(z)) > 0;
tau_noUV(0,z) = int_0^z K(z') dz' (0<=z<=20);
tau_noUV(0,z)=tau_noUV(0,20)+tau_REC(20,z) (20<=z<=1600).
P(z)=exp(-tau_noUV); g(z)=K(z)P(z), per unit redshift. The exact source lower-z scaling of g relative to original REC z20 observer is exp[-tau_noUV(0,20)]. The physical content of a real reionization solution requires separately admitted proper electron histories and photon/geometry owners for the lower segment; none is produced here.

## Same-author blind-referee self-review (bounded, ONE pass)
A: False continuum accuracy. Original 1-redshift-unit source interpolants do not bound native C physical systematic error. Coarse quadrature comparison is diagnostic, NOT an epsilon certificate. PASS_SCOPED with physical uncertainty unresolved.
B: False data inflation. This is 21 reused original C low-z source rows and 1581 reused source rows, transformed into 1601 new model-derived optical witnesses. New physical evolved states = ZERO; no claim of a DAG accept.
C: False observational link. HyRec noUV extrapolation to today's epoch ignores astrophysical reionization. The implied z0 gas temperature is not the real IGM temperature. This is a null *conditional* science experiment only.
D: F08 mixing. Original F08 S0 has different H, n_e, ionized species, photon population and proper-time observer, despite sharing labels z, tau and Thomson. Verified fail-closed source SHA and quantitative mismatch. REJECT direct splice.
E: Previous result treated REI F08 receiver as absent. Now actual PR349/315 source code exists and is conditionally validated, so that historical inventory is corrected, not repeated.
F: Original F05 gate unchanged. Original 46,080-cell 26-event initial run stops at tick160 of 131072; proposed PR351 new local increment certificate not equivalent to original accepted F05 promotion. No actual owner admission.

## Drift watchdog: stop, choose real physics
This one new source-authentic global noUV optical observable + current-source non-equivalence test is a useful falsifiable REC contribution, but central DAG scientific admission has NOT moved. No new C derivative atlas or conditional photon partial PR should follow. Only future *real* source-matched late-IGM H/He accepted history plus self-consistent Bianchi geometry and polarized photon operator could make this high-z donor part of central CMB/IGM prediction. Next actual authorized REI task remains first F05 [160,161] original owner admission and thereafter truly accepted late-IGM source; REC should then perform actual native source-conditional transport on a matching clock, not splice F08 S0.

Reported counters preserved: REI canonical 28/88 (+0), working 33/88 (+0), Physical Fast 4/7 (+0), REC H5 physical 0/313 (+0), no new owner IVPs. PRODUCTION HOLD. NO_MERGE, NO_FORCE_PUSH, NO_OWNER_SWAP, NO_TOLERANCE_CHANGE, AUTO_NEXT_NODE=false. Distinct-author reviewer NOT_RUN; same-author adversarial pass only.

Literature: Ali-Haïmoud and Hirata, HyRec, Phys Rev D 83 043513 (2011), DOI 10.1103/PhysRevD.83.043513; Fleury, Pitrou and Uzan, Light propagation in a homogeneous and anisotropic universe, Phys Rev D 91 043511 (2015), DOI 10.1103/PhysRevD.91.043511.
