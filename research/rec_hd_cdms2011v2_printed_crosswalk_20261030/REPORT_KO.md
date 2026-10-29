# REC HD | Historical CDMS v2 × LAMDA photon global-level compatibility atlas
2026-10-30 · scoped physical-data advancement · Draft/HOLD

## Scientific result

New official historical **2011 CDMS v2 `.egy` rendered-text** input, J=0..8 of v=0 HD, has been integrated with the frozen 2021 LAMDA 8 printed photon frequencies and the two measured 2022 rotational spacings. **All 8 photon frequencies are simultaneously representable by a single 9-level wavenumber vector that would round to every printed six-decimal 2011 `.egy` energy.** This is stronger than merely checking each adjacent transition separately. Exact global maximum offset **14,604.021 Hz** against a 14,989.6229Hz half-cell and minimum slack **385.6019Hz**. Largest standalone gap-vs-photon difference **24,917.6546Hz** (J=2). This result does not require fitting parameters or a guessed covariance.

Crucially, this does *not* cure the pre-existing original **35Hz FAIL7/8** between **2021 LAMDA term energies and photon fields**: they are different source representations. CDMS's displayed 2011 term wavenumbers are consistent with photon frequencies only at the source's much coarser 6-decimal display precision. Do not widen the original 35Hz gate or substitute CDMS v3.

| Measured 2022 v=0 spacing | Lab Hz | Lab minus 2011 printed `.egy` gap Hz | Lab minus inherited photon sum Hz |
|---|---:|---:|---:|
| J2−J0 | 8006533168000 | -14864136.031 | -14877400 |
| J3−J1 | 13283245098000 | -45021603.217 | -45034200 |

These nominal differences exceed decimal display offsets but **cannot** be expressed as catalog-model sigma significance without genuine old fit covariance/systematics and laboratory cross-correlations. Neither the historical v2 catalog original bytes nor the original fit covariance were retrieved. Exa-accessible normalized text is not the original raw `.egy` binary/source bytes.

## Actual work performed

- Read 2026-10-30 relevant REC PR161 and immutable PR160 source archives from Library, verified SHA256 and all ZIP CRC; reconstructed source-dependent physical data from the inherited PR161 LAMDA transcription and the CDMS 2011 archive text.
- New 2011 `.egy` physical input rows: 9; new eight-line crosswalk rows: 8; new 2022 measured pair crosswalk rows: 2. New model IVPs: 0.
- New Python physical artifact outputs: `CROSSWALK.json`, 2 CSVs and data figures, exact units and source roles.
- New Wolfram independent **method** check (exact rational arithmetic): global 8/8, J=4 boundary, per-line max, two lab residuals, integrability true.
- New tests after diagnostic repair: 8/8 normal, 8/8 `-O`, compileall PASS; initial failures retained.

## Full-science gate status

| Contract | State |
|---|---|
| New auxiliary: printed historical source crosswalk | 1/2 (one scoped complete; raw/covariance OPEN) |
| Parent PR161 J1 auxiliary | 1/2 (unchanged) |
| Canonical central DAG | 28/88 (+0) |
| REC Physical DAG | 0/313 (+0) |
| Original 35Hz | FAIL7/8, unchanged |
| CDMS 2011 raw full `.cat/.egy/.par/.fit/.lin` | NOT_ACQUIRED |
| Full fit covariance | null |
| Different-author R6/C9 | NOT_RUN |
| H5 epsilon / H6 / H7 | null / OPEN / OPEN |
| L4 / REI activation / production | false / false / HOLD |

The parent physical model remains unmodified. No synthetic source replacements, deuterium reaction enthalpies or unrelated REI/BASS/WU process contributions were folded into this HD radiation source.

## External sources

- Official archival CDMS v2 directory: https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
- Historical `.egy` original file (rendered text read; original raw byte unverified): https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/c003501.egy
- HD source version description: https://home.strw.leidenuniv.nl/~moldata/HD.html
- Cozijn et al. 2022 EPJD, DOI:10.1140/epjd/s10053-022-00552-x
- Cozijn et al. 2022 PRA, DOI:10.1103/PhysRevA.105.062823
- PR161: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/161
- Parent PR160: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/160

## Next constructive scientific node

Acquire authenticated CDMS December 2011 v2 original *bytes*, full SPFIT `.fit` fit-parameter covariance and catalog `.cat` with line QN/tag/frequency/errors. Reconstruct source fit frequency uncertainty jointly and compare against two measured constraints, preserving native 35Hz policy. The next node is NOT automatically admitted as physical DAG completion.
