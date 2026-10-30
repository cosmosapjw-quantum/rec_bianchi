# REC-HD MIRI MRS six-line source shape | 2026-10-30 인계

## 원격 Git / authority (사실과 미검증 구분)

- PROJECT: `cosmosapjw-quantum/rec_bianchi`
- NEW_UNIT: `REC_HD_MIRI_MRS_SIXLINE_NUISANCE_GEOMETRY_20261030`
- NEW_DRAFT_PR: #173, https://github.com/cosmosapjw-quantum/rec_bianchi/pull/173
- NEW_BRANCH: `research/rec-hd-miri-mrs-source-shape-20261030`
- HEAD_AFTER_29_PRE_HANDOFF_COMMITS: `518940fdbcc7df0b7ed0cc1065cb3ce940d10fe9`. **최종 live head는 다시 조회**. 이번 handoff 게시로 head가 바뀔 수 있다.
- PARENT_PR: #172, **IMMUTABLE_HEAD** `331602990e014e8ff532f6cc6179d6a74a1e3296`
- GRANDPARENT_PR: #171, **IMMUTABLE_HEAD** `8e1f51397cc3019642668daf4b2f2c39ff5126d5`
- SIBLING_PR: #170, **IMMUTABLE_HEAD** `12cb56b1f3d6b145dd6d3499a6d9e6c6ab4d42c8`
- NEW_PR=Draft/Open/Unmerged, DO_NOT_MERGE=true. No owner-source switch or production change.

## 새 물리 결과와 source-lock

Four literal Neufeld (2026) v2 `.dat/.fits` unchanged. SHA256 preserved in `evidence/MIRI_SHAPE_SUMMARY.json`; all source copies checked before the run. 15-level HD CMB stationary model with original standard vs alternate H2 de-excitation collision rates, f_ortho=.75, exact original temperatures `{1000,2000,3000,4000} K`, collider densities `{1e2,1e4,1e6,1e8,1e10} cm^-3`, z `{0,.1,.25,.5,.75,1,1.25}`. New **140 physical model conditions** and CSV evidence; **120** have two or more geometrically MIRI MRS-accessible R(4)–R(9) lines. MRS bandpass 4.9–27.9 μm with real A/B/C grating subband coverage, reference STScI user docs.

Full sixline coverage at z=0 requires **3 MRS settings**. z=.25:5 lines, z=.5:4, z=.75:3, z=1:2, z=1.25:0. These are geometric constraints, not model flux detectability. No source/sensitivity covariance or telescope likelihood imported.

Constructed all-pair common-amplitude-invariant logshape `max_i ln(Palt_i/Pstd_i)-min_i ln(Palt_i/Pstd_i)` with positive net line powers, and profiled standard-source H2 density 1e2..1e10 cm^-3 and optionally T over only exact four source knots. This proves a *model shape* mismatch when positive, without assigning sigma. Selected z=0 after both nuisance variables: Talt=4000,n=1e4 => 0.16689752214 (1% model floor PASS), 3000,1e4 => 0.15197147866 (floor PASS), 2000,1e4 => 0.13202383516 (floor FAIL), 1000,1e6 => 0.07049687554 (floor PASS; direct gap 0.6980, fixed T density-only 0.2114). These are approximate numerical profiles, not rigorously certified global minima or statistical inference.

## Verification / checkpoints

- Four raw source SHA256 locks: PASS.
- 10/10 local normal unittest; 10/10 `python -O`; compileall PASS.
- Independent SciPy differential-evolution optimized one high-contrast condition, accepted absolute residual difference `<2e-5`.
- Same-context blind referee in `docs/BLIND_REFEREE_SAME_CONTEXT_KO.md`. No native distinct-author audit. `R6_DISTINCT_AUTHOR=NOT_RUN`, `C9_DISTINCT_AUTHOR=NOT_RUN`, thus scoped R/C 18/20.
- 20 individual stage JSON Git commits, direct remote blob SHA compared to local 20/20 exact; same 20 files Library uploaded 20/20, Google Drive uploaded 20/20. These are provider upload ACKs unless a later readback receipt explicitly claims more.
- Code/docs/summary/checkpoint Git blob 9/9 exact. Large source FITS, raw numeric CSV and plots are authoritative in the complete source ZIP, not Git text adapters.
- `GITHUB_CI=NOT_VERIFIED` until exact commit workflows are checked.

## DAG/stop rules

- `NEW_AUXILIARY=1/1_SCOPED` conditional model physics only.
- `R_C_SCOPED=18/20`, native subagent `NOT_RUN`, same-context reviewer only.
- `CANONICAL_DAG=28/88 (+0)`; `REC_PHYSICAL_DAG=0/313 (+0)`.
- `ORIGINAL_CDMS2011_35HZ=FAIL7/8`, `H5_EPSILON=null`, `H6=OPEN`, `H7=OPEN`, `L4_READY=false`, `REI_ACTIVATION=false`.
- `PRODUCTION=HOLD`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `NO_MERGE=true`, `AUTO_NEXT_NODE=false` after this single authorized auxiliary.

## 자료 요청이 필요한 실제 blockers

1. **Sung, K. et al.** (2023), *The rotational spectrum of HD broadened by H2 at temperatures between 100–296 K*, *J. Quant. Spectrosc. Radiat. Transfer* 295, 108412; DOI https://doi.org/10.1016/j.jqsrt.2022.108412. 저자 또는 SOLEIL AILES 데이터 담당자에게 R(0)–R(3) calibrations, calibrated pixel/frequency/spectra arrays, T/P/purity metadata, LABFIT joint multispectrum parameter covariance / fit Jacobian and weights, H2O instrumental calibration nuisance covariance 요청. 표준오차만 갖고 joint covariance 합성 금지.
2. **CDMS 2011 v2 HD historical** https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/ : 원본 `HD.fit/.par/.lin` 및 `c003501i.cat/.egy` 계보 보존. CDMS 큐레이터에게 full precision original SPFIT `.var` (또는 Jacobian, weight/covariance) 요청. 2019 catalog나 v3로 대체 금지.
3. **Neufeld, D.A.** (2026), *Excitation of warm HD and H2 and implications for the interstellar deuterium abundance*, *ApJ* 1007:16, DOI https://doi.org/10.3847/1538-4357/ae851a, original four v2 files https://zenodo.org/records/21165907. 이미 ZIP에 모두 포함. 재업로드 불필요.

## 재실행

```
mkdir isolated; unzip -q REC_HD_MIRI_MRS_SIXLINE_SHAPE_20261030_SOURCE.zip -d isolated
cd isolated
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python src/miri_sixline_profile.py --root .
PYTHONPATH=src python src/plot_miri_profile.py --root .
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Re-run source ZIP manifest SHA256/CRC first and compare CSV/JSON generation to archived source before claiming byte identity. This handoff itself is not an authorization for another automatic node.

## 복사용 다음 스레드 계약

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rec_bianchi
CURRENT_PR=173
CURRENT_BRANCH=research/rec-hd-miri-mrs-source-shape-20261030
READ_LIVE_HEAD_FIRST=true
PARENT_PR=172
IMMUTABLE_PARENT_HEAD=331602990e014e8ff532f6cc6179d6a74a1e3296
GRANDPARENT_PR=171
IMMUTABLE_GRANDPARENT_HEAD=8e1f51397cc3019642668daf4b2f2c39ff5126d5
SIBLING_PR=170
CURRENT_UNIT=REC_HD_MIRI_MRS_SIXLINE_NUISANCE_GEOMETRY_20261030
SOURCE_ZIP=REC_HD_MIRI_MRS_SIXLINE_SHAPE_20261030_SOURCE.zip
SOURCE_ZIP_SHA256=READ_FINAL_BACKUP_RECEIPT
NEW_AUXILIARY=1/1_SCOPED
NEW_MODEL_CONDITIONS=140
MIRI_MRS_2PLUS_LINE_CONDITIONS=120
R_C_SCOPED=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
ORIGINAL_35HZ=FAIL7/8
H5_EPSILON=null
PRODUCTION=HOLD
GITHUB_CI=NOT_VERIFIED
NEXT_CANDIDATE_ONLY=REC_HD_EXPERIMENTAL_JOINT_COVARIANCE_SOURCED
NO_MERGE=true
NO_OWNER_SOURCE_SWITCH=true
NO_35HZ_RELAXATION=true
AUTO_NEXT_NODE=false
```
