# REC-HD J1 CMB source-switch: bounded physical computation

2026-10-30. **Derived + numerically checked**; parent `cosmosapjw-quantum/rec_bianchi` PR169 HEAD `ca80a69908a86f659849487030c47f3bd711f311` unchanged. Inputs from archived source-matched real coefficient table of PR169, original file separately preserved in Git. No new measurements.

For two levels 0 and 1 with g1/g0=3, T_g, T_r=2.72548(1+z) K, collider q10(T,f), and Einstein A10, define nbar=[exp(h nu/(k_B T_r))-1]^-1. Collisional rates C10=n_H2 q10 and C01=3 C10 exp[-h nu/(k_B T_g)], radiative rates R10=A10(1+nbar), R01=3A10 nbar. Stationary p1=(C01+R01)/(C01+C10+R01+R10). Net energy loss per HD molecule is h nu A10[p1(1+nbar)-3(1-p1)nbar]. Physical domain: spatially homogeneous steady state, isotropic Planck CMB, optically thin, no other levels/collider, gas held at fixed T_g, no cosmological IVP. This is a two-level source-contrast diagnostic, not an owner 9- or 15-level production calculation.

Grid: T_g=100,200 K; z=0,10,30,50,80; n_H2=1,100,10000,1e6,1e8 cm^-3; ortho fraction=0,0.5,1. 150 cases. Original 2021 Flower and 2026 Neufeld/Wan J1 rates sourced from the 36-row source-matched dataset. Source 2021 A=5.442e-8/s, 2026 A=5.4420380e-8/s, same 2674.986094 GHz line. Constants SI h=6.62607015e-34 J s, k_B=1.380649e-23 J/K. No source blending.

### Derived invariants and tests
- Positive n_H2: sign of energy transfer is sign(T_g - T_r), by detailed balance. Threshold z*=T_g/2.72548-1.
- n_H2=0: blackbody-radiative equilibrium and net energy loss zero (even if T_g independently specified).
- 2021 J1 q_para=q_ortho at T_g=100,200, hence output independent of mixing fraction (only this source J1 subset).
- New results: 150 case rows with both source models, zero-density and threshold tests PASS, signs PASS, finite arithmetic PASS. Command `python generate.py` regenerates exact CSV from immutable PR169-derived local 36-row coefficient data. The source ZIP includes both data and program.

### Blind-referee-style adversarial scientific review (same author, not independent reviewer)
**Issue S1, block production:** An astrophysical signal cannot be inferred directly from per-molecule energy transfer; line optical depth, actual HD column, geometry, radiation background and velocity field are absent. Kept scoped.
**Issue S2, block 9/15 level promotion:** 2021 J1 two-level model uses 35 Hz qualified line, but 2011-v2 high-J seven of eight original 35 Hz gates fail, so no full-level promotion or statistical likelihood.
**Issue S3, source risk:** 2026 Wan et al collision coefficients and Neufeld high-J extrapolation must not be called laboratory measurements. Files of 2026 source and CDMS archived separately; this run uses matched published rate coefficients, not original FITS byte file.
**Issue S4, numerical condition:** at T_r>T_g, reported negative loss is absorption/heating; it is not negative spontaneous luminosity. Distinguish physically in tables.
**Issue S5, identity:** old FITS remote MD5-only and Git source blobs are not a local exact FITS archive. No claim of full FITS physical validation.
Native independent distinct-author referee NOT_RUN; no external reviewer receipt.

### DAG and protection
Auxiliary `REC_HD_J1_CMB_SOURCE_SWITCH_20261030=1/1_SCOPED` conditionally complete; canonical=28/88 (+0), REC physical=0/313 (+0), production=HOLD, original 35 Hz=FAIL7/8, C9/R6 distinct-author NOT_RUN, AUTO_NEXT_NODE=false. Do not merge or activate source.

### Primary bibliographic source
- D. A. Neufeld, *Excitation of Warm HD and H2 and Implications for the Interstellar Deuterium Abundance*, ApJ 1007, 16 (2026), DOI 10.3847/1538-4357/ae851a; source v2 https://zenodo.org/records/21165907.
- Y. Wan et al., *Rotational quenching of HD induced by collisions with H2 molecules*, MNRAS 488, 381-386 (2019), DOI 10.1093/mnras/stz1735.
- D. R. Flower and E. Roueff, MNRAS 309, 833-835 (1999), DOI 10.1046/j.1365-8711.1999.02888.x; HD collisions and extension documented in Leiden LAMDA https://home.strw.leidenuniv.nl/~moldata/HD.html.
