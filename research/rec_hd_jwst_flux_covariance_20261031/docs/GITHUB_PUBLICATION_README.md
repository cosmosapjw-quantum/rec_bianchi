# REC-HD: Source-locked JWST line-flux covariance sensitivity (EXPLORATORY / HOLD)

**Parent** PR #174 immutable `4a5916761c60bf68163ab1f3845db35cbb789d97`.

Only source-conditional 15-level HD non-LTE emission shape diagnostics, **not** the original observational joint likelihood. Unit: JWST_LINE_FLUX_JOINT_COVARIANCE_20261031. Full original source-inclusive archive with both Neufeld FITS files, observed transcriptions, all 54,720 conditional GLS grid scores, plots, scripts/tests and 20 R/C stage records:

- ZIP: `REC_HD_JWST_LINE_FLUX_COVARIANCE_20261031_INDEPENDENT_REPLAY_SOURCE.zip`
- SHA256: `d1ae7e29a03413b3e7f085d91b40913772de2eeff4152fbd9f944e263b66f169`, bytes 4,488,478
- Library: `/BASS/rec_bianchi/JWST_LINE_FLUX_JOINT_COVARIANCE_20261031/`
- Google Drive folder: https://drive.google.com/drive/folders/1dSrXkRyvFnsY49Mi3-jAXfq8tSwZS5WO
- Source archive Drive object: https://drive.google.com/file/d/1aI2fNsKuId3SPa7wGut8W18aityrHHkU/view
- Independent extraction/restoration from Library and Drive SHA256 match and replay output 8/8 byte exact; 12/12 current tests normal and -O; 24/24 prior implementation tests normal and -O; 18/18 parent tests normal and -O.

For derivations, numerical details, known input gaps, and exact resume contract see `docs/SCIENTIFIC_REPORT_KO.md`, `docs/HANDOFF_NEXT_THREAD_KO.md`. Original data sources: Francis 2025 arxiv:2501.02085v1 (not Zenodo final), Neufeld 2026 Zenodo 21165907 (four original bytes SHA-locked). Archive remains SSOT for full 4.4MB bulk physical data. Git contains published scripts, tests, input transcriptions, a subset of quantitative summaries, manifest and stage evidence, **not** the full bulk FITS or full 54,720-row table.

**DO NOT merge; do not switch owner model, modify historical 35Hz target, or activate production.** Original 35Hz FAIL7/8, parent CI verify_repo_quick FAIL. Canonical DAG 28/88, physical DAG 0/313, R/C scoped 18/20 unchanged. R6/C9 real distinct-author NOT_RUN. AUTO_NEXT_NODE=false.
