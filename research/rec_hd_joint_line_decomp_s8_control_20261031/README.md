# REC-HD: 13-line censored likelihood decomposition and H2 S(8) control (DRAFT/HOLD)

**Scope:** add-only scientific checkpoint. Immutable base is PR #181 HEAD `c67b514152b175f964781e561c03cca8497a49f3`, which itself descends from PR #180 `ab8faf1b509899fc7b67cc15f85de2e19c211071`. **DO NOT MERGE.**

## Actual new science, not a resubmission of #181

- Reused Neufeld (2026) ApJ 1007:16, official [Zenodo v2](https://zenodo.org/records/21165907) original/alternate HD FITS, Francis et al. (2025) A&A 694 A174 [final Appendix F](https://zenodo.org/records/14592550), and Pontoppidan et al. (2024) P24 v5 KP5 opacity Git blob `96d42fe318938d42d584f96e23661abd3cce96d5`.
- Source-authentic 26 positions × H2 S(1..7) plus HD R(4..9), inherited 338 templates, 104 source-conditioned working fits, 1,352 predicted fluxes. **Those three inherited row counts are NOT new to this PR**.
- NEW: 676 individual detected/censored/excluded contribution rows exactly decompose all 104 working fit deviances; maximum relative reconstruction error **3.238875982149136e-16**.
- NEW: 52 paired *fixed-standard-parameters vs reoptimized alternate* collisional-rate-response decompositions; among 17 HD-detected apertures at epsilon=0, median reoptimization contribution to deviance 0.0004250556106626391, maximum 0.1943572194626313.
- NEW: 104 H2 S(8) transfer predictions, 26 apertures × standard/alternate × epsilon 0/0.06. In the epsilon=0 standard case, median |residual| 0.649197750827225 printed-sigma and max 5.545581647444564; **2/26** exceed 3sigma: IRAS 18089-1732 aperture 1 and Ser-emb 8 (N) aperture 1.
- HD R(9) is **10 detections and 16 limits**, not all limits. Alternate/standard intrinsic ratio median 1.3372882605539247, max 1.9626938561047558. Observed-frame line influence differs from intrinsic population shift.
- NEW scientific figures: two PNG and two SVG, linewise HD R9 deviance contrast and H2 S8 conditioned residuals.

## Mathematical and epistemic boundary

`D = Σ_detection[(y−μ)^2/v + ln(v/σ²)] − 2Σ_upper logΦ[(L−μ)/sqrt((L/3)^2+(εμ)^2)]`, where `v=σ²+(εμ)²`, `ε∈{0,0.06}`, 8 rounded-zero HD errors excluded; source Neufeld posterior bestfits fixed except 2 anchored working throughput offsets and molecular xHD scale. The original author already fitted the **same Francis data, including S(8)**, so S(8) is held out only from this working objective, **NOT an independent posterior predictive test**. The two KP5 anchors mix dust and beam throughput; no empirical cross-line MIRI covariance and no accurate censor process have been reconstructed. No true dust claim, evidence ratio, formal p-value, elemental D/H, independent posterior, or production acceptance.

## Tests, reproducibility, backups

- Scope tests `22/22 Python normal` and `22/22 Python -O` on source-inclusive clean extraction. Clean science replay `10/10 BYTE_EXACT` (six inherited forward CSV/JSON + four newly generated diagnostic CSV/JSON), no figure byte claim. ZIP manifests and CRC `51/51` full and `42/42` thin payload files verified; restored source files included in full ZIP.
- FULL_SOURCE: `REC_HD_JOINT_LINE_DECOMP_S8_CONTROL_20261031_FULL_SOURCE.zip`, 7,896,983 bytes, SHA256 `fe2a0430ea7c955d6f62379551f904e202af8831564e3d7e143c3a20b8bff85b`.
- THIN_SCIENCE: `REC_HD_JOINT_LINE_DECOMP_S8_CONTROL_20261031_THIN_SCIENCE.zip`, 520,355 bytes, SHA256 `8126024fa95ab31e9c490bdf0288980a97150f830a3d1a00f65620d6f3fb347f`.
- **Google Drive actual upload + independent raw-byte readback:** [full archive](https://drive.google.com/file/d/1-knipnocA9Y0CmTVPl-unNMott2g5PxC/view), [thin archive](https://drive.google.com/file/d/1jMPlUZnjGMTMGImhjPIHTpq9nTtHzkYP/view). Provider sizes + SHA256 and byte comparison confirmed both files.
- **ChatGPT Library independent stored-file readback:** `/BASS/rec_bianchi/REC_HD_JOINT_LINE_DECOMP_S8_CONTROL_20261031/` full and thin archive verified byte-identical against original and Drive. Dropbox upload for **this** unit NOT_VERIFIED. PR #181's previously verified Dropbox backup must not be misattributed to this new unit.
- Full executable code `src/diagnose_joint.py`, `src/joint_7h2_6hd.py`, `tests/test_diagnostics.py`, original source FITS and measured flux rows, four new scientific CSVs, summary, reports and figure files are in **the verified ZIP archive**. This Git PR is a **text checkpoint only**; not a claim that source FITS or full runnable code are Git blobs.
- Same-context adversarial science review completed; native distinct-author R6/C9 and native subagent NOT_RUN.

## Frozen central and physical DAG gates

`CANONICAL_DAG=28/88 (+0)`; `REC_PHYSICAL_DAG=0/313 (+0)`; scoped `18/20`; aux new diagnostic `1/1 EXPLORATORY`, **not counted in either upper DAG**. Original `35HZ=FAIL7/8`, `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `AUTO_NEXT_NODE=false`.

## Next public source task

Read live HEAD and restore original `posterior_isochoric.csv.gz` from the [original Neufeld Zenodo v2 record](https://zenodo.org/records/21165907), MD5 `6458f83f324a19c8e28fd656dcce2022`, to recover actual two-component emitter OPR and complete the 7H2+6HD **isochoric** joint fit rather than borrowing isobaric OPR. This public-source acquisition does not block the completed present diagnostic. Distinct-author audit and original 35 Hz gates remain separate.
