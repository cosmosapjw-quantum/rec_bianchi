# Li core-channel wording clarification — independent review

Reviewed during the existing THERM01 scientific/code/result pass. This note does not change frozen source/config identities, code, numerical tolerances, or running IVPs.

## Observed wording defect

`FROZEN_CONTRACT.md` says, "Core excitation is zero for this support." The preceding sentence limits the admitted processes to smoothed ground-state photochannels and later sentences exclude excited-level kinetics. Nevertheless, the quoted sentence on its own is too broad as a physical statement about the entire 5–60 eV band.

The published primary article by A. Müller, A. S. Kheifets, I. Bray and D. V. Fursa, *Photoionization of the Li atom: Convergent-close-coupling calculations with a focus on two-electron removal*, Physical Review A113,033105 (published2026-03-09), explicitly discusses Li resonant single-core excitation and autoionizing states across50–70eV in its introduction. The published PDF was actually opened in this review; the author-preprint URL separately timed out and is not the evidence used here.

Primary source: https://journals.aps.org/pra/pdf/10.1103/l4xt-3sxy ; DOI https://doi.org/10.1103/l4xt-3sxy . Relevant passage: introduction, first page, discussion of Ederer and Mehlman photoabsorption measurements. The distinction between direct1s photoionization and other channels is developed in Sec.III A.

## Precise correction for the current result

Use the following statement in the final report and handoff:

> For this source support, the retained direct Li I 1s-photoionization branch and its direct-core-hole energy term vanish. Resonant core excitation and its decay are excluded model processes; some resonances lie inside50–60eV, and no zero omission error is asserted.

The thermal/yield result is therefore **a source-fit, smoothed-continuum retained-process closure** on the specified spectrum. `core_exact_zero` is a test of the retained direct-continuum branch, not a theorem that real Li has no core excitation below64.39eV.

## Classification and consequence

Classification: **source-scope wording defect; correction required for reporting**. This is not a numerical failure or a new scientific-runtime blocker. The actual code has no resolved resonant-excitation process, and the frozen physical model already excludes excited-level kinetics. Its source moments, population evolution and energy ledger are consistent for those retained processes.

No new physical term, source row, tolerance change, or IVP rerun is needed to correct the scope statement. Existing frozen contract bytes remain the run identity; this dated clarification records the correction without rewriting that identity. A future resonance-complete physical calculation needs the relevant resonance strengths/branching and energy partitions, and has a separate input obligation.
