# REC-HD-MULTICHANNEL-AFFINITY01

Source-locked conditional HD two-bath 26-channel Markov diagnostic for 2026-10-29. This does **not** replace the original HD data, rates, accepted 35 Hz spectroscopy gate, entire H5/REI physical source, or cosmological transport.

Read THEORY.md, REPORT_KO.md, FROZEN_CONTRACT.json, SURVEY.json, SCIENTIFIC_ADMISSION.json, RESOURCE_LEDGER.json, STAGES.json and HANDOFF_NEXT_THREAD_KO.md.

Run from this capsule root after unpacking: `python code/multichannel.py --source inputs/lamda_hd_pinned_20261025.dat --prior /path/to/REC_PR150_saved_RESULT.json --out /new/attempt`; requires mpmath. Independent verification: `python code/independent_validate.py --source inputs/lamda_hd_pinned_20261025.dat --primary results/RESULT.json --out /tmp/independent.json`, then `python code/test_multichannel.py`. Note: the latter script expects source at this exact capsule path.

The immutable full SOURCE ZIP includes the byte-pinned LAMDA source privately, but public Git deliberately excludes that data due to unresolved redistribution permission. The original LAMDA raw 2289 bytes SHA256 is 0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb. Previous stored 24 Kirchhoff values and scientific stage provenance are included in published REPORT and source comparison results, but for replay use original PR150 source ZIP, not source substitution.

Canonical DAG 28/88 +0; physical 0/313, source-choice HOLD; R6/C9 native blind independent review NOT_RUN.
